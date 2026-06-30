"""
Unit tests for backend/app/db/repositories/calendar_repo.py

All tests use FakePool / FakeConn — no real PostgreSQL connection is made.
The fakes implement exactly the asyncpg surface used by calendar_repo:
  pool.fetchrow(sql, *args)  → single row dict or None
  pool.fetch(sql, *args)     → list of row dicts
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, call

import pytest

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

CLINIC_ID      = "11111111-1111-4111-8111-111111111111"
CONNECTION_ID  = "22222222-2222-4222-a222-222222222222"
EXT_EVENT_ID   = "google-evt-abc123"

NOW   = datetime(2025, 6, 1, 9, 0, 0, tzinfo=timezone.utc)
LATER = datetime(2025, 6, 1, 10, 0, 0, tzinfo=timezone.utc)

FAKE_CONNECTION_ROW: Dict[str, Any] = {
    "id":                   CONNECTION_ID,
    "clinic_id":            CLINIC_ID,
    "provider":             "google",
    "external_calendar_id": "cal@group.calendar.google.com",
    "sync_status":          "active",
}

FAKE_BLOCK_ROW: Dict[str, Any] = {
    "id":                CONNECTION_ID,
    "clinic_id":         CLINIC_ID,
    "connection_id":     CONNECTION_ID,
    "external_event_id": EXT_EVENT_ID,
    "title":             "Lunch break",
    "block_type":        "busy",
    "starts_at":         NOW,
    "ends_at":           LATER,
    "is_all_day":        False,
    "source":            "calendar_sync",
    "raw_payload":       None,
}

FAKE_SYNC_EVENT_ROW: Dict[str, Any] = {
    "id":            "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
    "clinic_id":     CLINIC_ID,
    "connection_id": CONNECTION_ID,
    "event_type":    "sync_complete",
    "status":        "success",
    "message":       None,
    "raw_payload":   None,
}


# ---------------------------------------------------------------------------
# Fake async pool
# ---------------------------------------------------------------------------


class FakePool:
    """
    Minimal asyncpg Pool stand-in.

    Initialise with explicit return values for fetchrow and fetch so each
    test can control what the "database" returns without any real connection.
    """

    def __init__(
        self,
        fetchrow_return: Any = None,
        fetch_return: Optional[List[Any]] = None,
    ) -> None:
        self.fetchrow = AsyncMock(return_value=fetchrow_return)
        self.fetch    = AsyncMock(return_value=fetch_return or [])


# ---------------------------------------------------------------------------
# 1. upsert_calendar_connection calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_calendar_connection_calls_fetchrow():
    from backend.app.db.repositories.calendar_repo import upsert_calendar_connection

    pool = FakePool(fetchrow_return=FAKE_CONNECTION_ROW)
    result = await upsert_calendar_connection(
        pool,
        clinic_id=CLINIC_ID,
        provider="google",
        external_calendar_id="cal@group.calendar.google.com",
    )

    pool.fetchrow.assert_awaited_once()
    sql_called = pool.fetchrow.call_args.args[0]
    assert "clinic_calendar_connections" in sql_called
    assert "on conflict" in sql_called.lower()
    assert result == FAKE_CONNECTION_ROW


# ---------------------------------------------------------------------------
# 2. upsert_calendar_block calls fetchrow for a valid range
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_calendar_block_calls_fetchrow_valid_range():
    from backend.app.db.repositories.calendar_repo import upsert_calendar_block

    pool = FakePool(fetchrow_return=FAKE_BLOCK_ROW)
    result = await upsert_calendar_block(
        pool,
        clinic_id=CLINIC_ID,
        connection_id=CONNECTION_ID,
        external_event_id=EXT_EVENT_ID,
        title="Lunch break",
        block_type="busy",
        starts_at=NOW,
        ends_at=LATER,
    )

    pool.fetchrow.assert_awaited_once()
    sql_called = pool.fetchrow.call_args.args[0]
    assert "clinic_calendar_blocks" in sql_called
    assert result == FAKE_BLOCK_ROW


# ---------------------------------------------------------------------------
# 3. upsert_calendar_block raises InvalidCalendarRangeError for bad range
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_calendar_block_raises_for_ends_before_starts():
    from backend.app.db.repositories.calendar_repo import (
        upsert_calendar_block,
        InvalidCalendarRangeError,
    )

    pool = FakePool()
    with pytest.raises(InvalidCalendarRangeError):
        await upsert_calendar_block(
            pool,
            clinic_id=CLINIC_ID,
            connection_id=CONNECTION_ID,
            external_event_id=EXT_EVENT_ID,
            title="Bad block",
            block_type="busy",
            starts_at=LATER,   # reversed — starts after it ends
            ends_at=NOW,
        )

    pool.fetchrow.assert_not_awaited()


@pytest.mark.asyncio
async def test_upsert_calendar_block_raises_for_equal_times():
    from backend.app.db.repositories.calendar_repo import (
        upsert_calendar_block,
        InvalidCalendarRangeError,
    )

    pool = FakePool()
    with pytest.raises(InvalidCalendarRangeError):
        await upsert_calendar_block(
            pool,
            clinic_id=CLINIC_ID,
            connection_id=CONNECTION_ID,
            external_event_id=EXT_EVENT_ID,
            title="Zero-length block",
            block_type="busy",
            starts_at=NOW,
            ends_at=NOW,   # equal — zero duration
        )

    pool.fetchrow.assert_not_awaited()


# ---------------------------------------------------------------------------
# 4. delete_calendar_block_by_external_id calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_calendar_block_calls_fetchrow():
    from backend.app.db.repositories.calendar_repo import delete_calendar_block_by_external_id

    pool = FakePool(fetchrow_return=FAKE_BLOCK_ROW)
    result = await delete_calendar_block_by_external_id(
        pool,
        clinic_id=CLINIC_ID,
        connection_id=CONNECTION_ID,
        external_event_id=EXT_EVENT_ID,
    )

    pool.fetchrow.assert_awaited_once()
    sql_called = pool.fetchrow.call_args.args[0]
    assert "delete from" in sql_called.lower()
    assert "clinic_calendar_blocks" in sql_called
    assert result == FAKE_BLOCK_ROW


@pytest.mark.asyncio
async def test_delete_calendar_block_returns_none_when_not_found():
    from backend.app.db.repositories.calendar_repo import delete_calendar_block_by_external_id

    pool = FakePool(fetchrow_return=None)
    result = await delete_calendar_block_by_external_id(
        pool,
        clinic_id=CLINIC_ID,
        connection_id=CONNECTION_ID,
        external_event_id="nonexistent",
    )
    assert result is None


# ---------------------------------------------------------------------------
# 5. get_overlapping_blocks calls fetch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_overlapping_blocks_calls_fetch():
    from backend.app.db.repositories.calendar_repo import get_overlapping_blocks

    pool = FakePool(fetch_return=[FAKE_BLOCK_ROW])
    results = await get_overlapping_blocks(pool, CLINIC_ID, NOW, LATER)

    pool.fetch.assert_awaited_once()
    sql_called = pool.fetch.call_args.args[0]
    assert "clinic_calendar_blocks" in sql_called
    assert len(results) == 1
    assert results[0] == FAKE_BLOCK_ROW


# ---------------------------------------------------------------------------
# 6. is_time_available returns True when no overlapping blocks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_time_available_returns_true_when_no_blocks():
    from backend.app.db.repositories.calendar_repo import is_time_available

    pool = FakePool(fetch_return=[])   # empty → no conflicts
    result = await is_time_available(pool, CLINIC_ID, NOW, LATER)
    assert result is True


# ---------------------------------------------------------------------------
# 7. is_time_available returns False when overlapping blocks exist
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_time_available_returns_false_when_blocks_exist():
    from backend.app.db.repositories.calendar_repo import is_time_available

    pool = FakePool(fetch_return=[FAKE_BLOCK_ROW])
    result = await is_time_available(pool, CLINIC_ID, NOW, LATER)
    assert result is False


# ---------------------------------------------------------------------------
# 8. is_time_available raises InvalidCalendarRangeError for invalid range
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_time_available_raises_for_invalid_range():
    from backend.app.db.repositories.calendar_repo import (
        is_time_available,
        InvalidCalendarRangeError,
    )

    pool = FakePool()
    with pytest.raises(InvalidCalendarRangeError):
        await is_time_available(pool, CLINIC_ID, LATER, NOW)   # inverted range

    pool.fetch.assert_not_awaited()


# ---------------------------------------------------------------------------
# 9. log_calendar_sync_event calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_calendar_sync_event_calls_fetchrow():
    from backend.app.db.repositories.calendar_repo import log_calendar_sync_event

    pool = FakePool(fetchrow_return=FAKE_SYNC_EVENT_ROW)
    result = await log_calendar_sync_event(
        pool,
        clinic_id=CLINIC_ID,
        connection_id=CONNECTION_ID,
        event_type="sync_complete",
        status="success",
    )

    pool.fetchrow.assert_awaited_once()
    sql_called = pool.fetchrow.call_args.args[0]
    assert "clinic_calendar_sync_events" in sql_called
    assert result == FAKE_SYNC_EVENT_ROW


@pytest.mark.asyncio
async def test_log_calendar_sync_event_accepts_optional_fields():
    from backend.app.db.repositories.calendar_repo import log_calendar_sync_event

    pool = FakePool(fetchrow_return=FAKE_SYNC_EVENT_ROW)
    # connection_id=None and raw_payload provided — must not raise
    await log_calendar_sync_event(
        pool,
        clinic_id=CLINIC_ID,
        connection_id=None,
        event_type="webhook_received",
        status="pending",
        message="processing",
        raw_payload={"key": "value"},
    )

    pool.fetchrow.assert_awaited_once()


# ---------------------------------------------------------------------------
# 10. Overlap SQL contains the correct condition tokens
# ---------------------------------------------------------------------------


def test_overlap_sql_contains_correct_condition():
    """
    Verify the overlap condition in get_overlapping_blocks contains:
      starts_at <   (block starts before requested end)
      ends_at >     (block ends after requested start)

    We extract the SQL string directly from the source rather than
    running it against a database.
    """
    import inspect
    from backend.app.db.repositories import calendar_repo

    source = inspect.getsource(calendar_repo.get_overlapping_blocks)

    # The SQL must contain both halves of the overlap predicate.
    assert re.search(r"starts_at\s*<", source), (
        "get_overlapping_blocks SQL must include 'starts_at <'"
    )
    assert re.search(r"ends_at\s*>", source), (
        "get_overlapping_blocks SQL must include 'ends_at >'"
    )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_calendar_block_without_external_event_id():
    """Blocks without an external_event_id use a plain INSERT (no ON CONFLICT)."""
    from backend.app.db.repositories.calendar_repo import upsert_calendar_block

    manual_block = {**FAKE_BLOCK_ROW, "external_event_id": None}
    pool = FakePool(fetchrow_return=manual_block)

    result = await upsert_calendar_block(
        pool,
        clinic_id=CLINIC_ID,
        connection_id=CONNECTION_ID,
        external_event_id=None,   # manual block
        title="Doctor away",
        block_type="vacation",
        starts_at=NOW,
        ends_at=LATER,
    )

    pool.fetchrow.assert_awaited_once()
    # Plain INSERT must NOT contain ON CONFLICT
    sql_called = pool.fetchrow.call_args.args[0]
    assert "on conflict" not in sql_called.lower()
    assert result == manual_block


@pytest.mark.asyncio
async def test_upsert_calendar_connection_default_sync_status():
    """sync_status defaults to 'active' when not supplied."""
    from backend.app.db.repositories.calendar_repo import upsert_calendar_connection

    pool = FakePool(fetchrow_return=FAKE_CONNECTION_ROW)
    await upsert_calendar_connection(
        pool,
        clinic_id=CLINIC_ID,
        provider="microsoft",
        external_calendar_id="cal-id-xyz",
        # sync_status omitted — should default to 'active'
    )

    args = pool.fetchrow.call_args.args
    # 4th positional arg after the SQL string is sync_status
    assert args[4] == "active"
