"""
Call log repository — PraxisMed Sprint 1 / Module 13

Provides async CRUD operations for the ``clinic_call_logs`` table.
All SQL is parameterised ($1, $2, …) — no string interpolation.
Direct SQL lives only in this module; callers receive plain dicts.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class CallRepoError(RuntimeError):
    """Base class for call repository errors."""


class InvalidCallLogError(CallRepoError):
    """Raised when required call log fields are missing or invalid."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _assert_nonempty(value: str, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidCallLogError(f"{name!r} must not be empty")


# ---------------------------------------------------------------------------
# 1. upsert_call_log
# ---------------------------------------------------------------------------


async def upsert_call_log(
    pool: Any,
    clinic_id: str,
    external_call_id: str,
    call_status: str,
    provider: str = "vapi",
    caller_phone: Optional[str] = None,
    direction: str = "inbound",
    started_at: Optional[datetime] = None,
    ended_at: Optional[datetime] = None,
    duration_seconds: Optional[int] = None,
    transcript_text: Optional[str] = None,
    summary: Optional[str] = None,
    action_required: bool = False,
    urgency_level: str = "normal",
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Insert or update a call log row keyed on (clinic_id, provider, external_call_id).

    Returns the full row as a dict.
    """
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(external_call_id, "external_call_id")
    _assert_nonempty(call_status, "call_status")

    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    sql = """
        INSERT INTO clinic_call_logs (
            clinic_id, provider, external_call_id, caller_phone, direction,
            call_status, started_at, ended_at, duration_seconds,
            transcript_text, summary, action_required, urgency_level,
            raw_payload, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5,
            $6, $7, $8, $9,
            $10, $11, $12, $13,
            $14::jsonb, now()
        )
        ON CONFLICT (clinic_id, provider, external_call_id)
        DO UPDATE SET
            caller_phone     = EXCLUDED.caller_phone,
            direction        = EXCLUDED.direction,
            call_status      = EXCLUDED.call_status,
            started_at       = COALESCE(EXCLUDED.started_at,    clinic_call_logs.started_at),
            ended_at         = COALESCE(EXCLUDED.ended_at,      clinic_call_logs.ended_at),
            duration_seconds = COALESCE(EXCLUDED.duration_seconds, clinic_call_logs.duration_seconds),
            transcript_text  = COALESCE(EXCLUDED.transcript_text,  clinic_call_logs.transcript_text),
            summary          = COALESCE(EXCLUDED.summary,           clinic_call_logs.summary),
            action_required  = EXCLUDED.action_required,
            urgency_level    = EXCLUDED.urgency_level,
            raw_payload      = COALESCE(EXCLUDED.raw_payload,       clinic_call_logs.raw_payload),
            updated_at       = now()
        RETURNING *
    """

    row = await pool.fetchrow(
        sql,
        clinic_id,
        provider,
        external_call_id,
        caller_phone,
        direction,
        call_status,
        started_at,
        ended_at,
        duration_seconds,
        transcript_text,
        summary,
        action_required,
        urgency_level,
        raw_payload_json,
    )
    return _row_to_dict(row)


# ---------------------------------------------------------------------------
# 2. get_call_log_by_external_id
# ---------------------------------------------------------------------------


async def get_call_log_by_external_id(
    pool: Any,
    clinic_id: str,
    external_call_id: str,
    provider: str = "vapi",
) -> Optional[Dict[str, Any]]:
    """Return a single call log row matching the external ID, or None."""
    sql = """
        SELECT *
        FROM clinic_call_logs
        WHERE clinic_id = $1
          AND provider  = $2
          AND external_call_id = $3
    """
    row = await pool.fetchrow(sql, clinic_id, provider, external_call_id)
    return _row_to_dict(row) if row else None


# ---------------------------------------------------------------------------
# 3. list_recent_call_logs
# ---------------------------------------------------------------------------


async def list_recent_call_logs(
    pool: Any,
    clinic_id: str,
    limit: int = 20,
    action_required: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """
    Return recent call logs for a clinic, newest first.

    ``limit`` must be 1–100.  Pass ``action_required=True/False`` to filter.
    """
    if limit < 1 or limit > 100:
        raise InvalidCallLogError("limit must be between 1 and 100")

    if action_required is None:
        sql = """
            SELECT *
            FROM clinic_call_logs
            WHERE clinic_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """
        rows = await pool.fetch(sql, clinic_id, limit)
    else:
        sql = """
            SELECT *
            FROM clinic_call_logs
            WHERE clinic_id       = $1
              AND action_required = $2
            ORDER BY created_at DESC
            LIMIT $3
        """
        rows = await pool.fetch(sql, clinic_id, action_required, limit)

    return [_row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# 4. mark_call_action_required
# ---------------------------------------------------------------------------


async def mark_call_action_required(
    pool: Any,
    clinic_id: str,
    external_call_id: str,
    action_required: bool = True,
    urgency_level: str = "normal",
    provider: str = "vapi",
) -> Dict[str, Any]:
    """Update the action_required and urgency_level fields for a call log row."""
    sql = """
        UPDATE clinic_call_logs
        SET action_required = $1,
            urgency_level   = $2,
            updated_at      = now()
        WHERE clinic_id        = $3
          AND provider         = $4
          AND external_call_id = $5
        RETURNING *
    """
    row = await pool.fetchrow(
        sql, action_required, urgency_level, clinic_id, provider, external_call_id
    )
    return _row_to_dict(row) if row else {}
