"""
Calendar Repository — PraxisMed Sprint 1 / Module 4

Database access layer for:
  • clinic_calendar_connections  — OAuth/API links to external calendars
  • clinic_calendar_blocks       — busy periods the booking layer must respect
  • clinic_calendar_sync_events  — append-only sync operation log

All functions accept an asyncpg Pool (or any object that exposes the same
.fetchrow() / .fetch() / .execute() coroutine interface) so they can be called
from FastAPI lifespan handlers, n8n webhook processors, Vapi handlers, or tests.

Rules:
  • Parameterised SQL only — no string interpolation of user-supplied values.
  • Python-level validation for invariants that the DB also enforces (e.g.
    ends_at > starts_at) so callers get a clear error before the round-trip.
  • No FastAPI, no config_loader, no Vapi, no WhatsApp imports.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class CalendarRepoError(RuntimeError):
    """Base exception for all calendar repository errors."""


class InvalidCalendarRangeError(CalendarRepoError):
    """Raised when ends_at is not strictly greater than starts_at."""


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _assert_valid_range(starts_at: datetime, ends_at: datetime) -> None:
    """Raise InvalidCalendarRangeError if the time range is not strictly positive."""
    if ends_at <= starts_at:
        raise InvalidCalendarRangeError(
            f"ends_at must be strictly after starts_at; "
            f"got starts_at={starts_at.isoformat()!r}, ends_at={ends_at.isoformat()!r}"
        )


# ---------------------------------------------------------------------------
# 1. upsert_calendar_connection
# ---------------------------------------------------------------------------


async def upsert_calendar_connection(
    pool: Any,
    clinic_id: str,
    provider: str,
    external_calendar_id: str,
    sync_status: str = "active",
) -> Dict[str, Any]:
    """
    Insert or update a calendar connection row.

    Uses ON CONFLICT on the (clinic_id, provider, external_calendar_id) unique
    index so repeated calls from a webhook are idempotent.

    Returns the created or updated row as a dict.
    """
    sql = """
        INSERT INTO clinic_calendar_connections
            (clinic_id, provider, external_calendar_id, sync_status)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (clinic_id, provider, external_calendar_id)
        DO UPDATE SET
            sync_status = EXCLUDED.sync_status,
            updated_at  = now()
        RETURNING *
    """
    row = await pool.fetchrow(sql, clinic_id, provider, external_calendar_id, sync_status)
    return dict(row)


# ---------------------------------------------------------------------------
# 2. upsert_calendar_block
# ---------------------------------------------------------------------------


async def upsert_calendar_block(
    pool: Any,
    clinic_id: str,
    connection_id: Optional[str],
    external_event_id: Optional[str],
    title: Optional[str],
    block_type: str,
    starts_at: datetime,
    ends_at: datetime,
    is_all_day: bool = False,
    source: str = "calendar_sync",
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Insert or update a calendar block.

    When external_event_id is provided the row is upserted on the
    (clinic_id, connection_id, external_event_id) composite to avoid
    duplicates from repeated sync runs.  When external_event_id is None
    an unconditional INSERT is performed (manual blocks).

    Raises InvalidCalendarRangeError before touching the database if
    ends_at <= starts_at.
    """
    _assert_valid_range(starts_at, ends_at)

    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    if external_event_id is not None:
        sql = """
            INSERT INTO clinic_calendar_blocks
                (clinic_id, connection_id, external_event_id, title,
                 block_type, starts_at, ends_at, is_all_day, source, raw_payload)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb)
            ON CONFLICT (clinic_id, connection_id, external_event_id)
            DO UPDATE SET
                title       = EXCLUDED.title,
                block_type  = EXCLUDED.block_type,
                starts_at   = EXCLUDED.starts_at,
                ends_at     = EXCLUDED.ends_at,
                is_all_day  = EXCLUDED.is_all_day,
                source      = EXCLUDED.source,
                raw_payload = EXCLUDED.raw_payload,
                updated_at  = now()
            RETURNING *
        """
        row = await pool.fetchrow(
            sql,
            clinic_id, connection_id, external_event_id, title,
            block_type, starts_at, ends_at, is_all_day, source, raw_payload_json,
        )
    else:
        sql = """
            INSERT INTO clinic_calendar_blocks
                (clinic_id, connection_id, title,
                 block_type, starts_at, ends_at, is_all_day, source, raw_payload)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
            RETURNING *
        """
        row = await pool.fetchrow(
            sql,
            clinic_id, connection_id, title,
            block_type, starts_at, ends_at, is_all_day, source, raw_payload_json,
        )

    return dict(row)


# ---------------------------------------------------------------------------
# 3. delete_calendar_block_by_external_id
# ---------------------------------------------------------------------------


async def delete_calendar_block_by_external_id(
    pool: Any,
    clinic_id: str,
    connection_id: str,
    external_event_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Delete the calendar block identified by its external event id.

    Returns the deleted row as a dict, or None if no row was found.
    """
    sql = """
        DELETE FROM clinic_calendar_blocks
        WHERE  clinic_id         = $1
          AND  connection_id     = $2
          AND  external_event_id = $3
        RETURNING *
    """
    row = await pool.fetchrow(sql, clinic_id, connection_id, external_event_id)
    return dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 4. get_overlapping_blocks
# ---------------------------------------------------------------------------


async def get_overlapping_blocks(
    pool: Any,
    clinic_id: str,
    starts_at: datetime,
    ends_at: datetime,
) -> List[Dict[str, Any]]:
    """
    Return all blocks for *clinic_id* that overlap the requested time range.

    Standard half-open interval overlap condition:
        block.starts_at < requested ends_at
        AND block.ends_at  > requested starts_at

    Ordered by starts_at ascending so callers can iterate chronologically.
    """
    sql = """
        SELECT *
        FROM   clinic_calendar_blocks
        WHERE  clinic_id  = $1
          AND  starts_at  < $3
          AND  ends_at    > $2
        ORDER BY starts_at ASC
    """
    rows = await pool.fetch(sql, clinic_id, starts_at, ends_at)
    return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# 5. is_time_available
# ---------------------------------------------------------------------------


async def is_time_available(
    pool: Any,
    clinic_id: str,
    starts_at: datetime,
    ends_at: datetime,
) -> bool:
    """
    Return True when no calendar blocks overlap the requested slot.

    Raises InvalidCalendarRangeError before querying if ends_at <= starts_at.
    """
    _assert_valid_range(starts_at, ends_at)
    blocks = await get_overlapping_blocks(pool, clinic_id, starts_at, ends_at)
    return len(blocks) == 0


# ---------------------------------------------------------------------------
# 6. log_calendar_sync_event
# ---------------------------------------------------------------------------


async def log_calendar_sync_event(
    pool: Any,
    clinic_id: str,
    connection_id: Optional[str],
    event_type: str,
    status: str,
    message: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Append a row to clinic_calendar_sync_events.

    This table is append-only (no UPDATE).  Every sync operation — whether
    triggered by n8n, a webhook, or a manual retry — should produce a row here
    so the dashboard and alerting pipelines have a full history.

    Returns the inserted row.
    """
    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    sql = """
        INSERT INTO clinic_calendar_sync_events
            (clinic_id, connection_id, event_type, status, message, raw_payload)
        VALUES ($1, $2, $3, $4, $5, $6::jsonb)
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id, connection_id, event_type, status, message, raw_payload_json,
    )
    return dict(row)
