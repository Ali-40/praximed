"""
Unit tests for call_repo — PraxisMed Sprint 1 / Module 13

All tests use AsyncMock pool objects; no real database connection is made.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.db.repositories.call_repo import (
    CallRepoError,
    InvalidCallLogError,
    get_call_log_by_external_id,
    list_recent_call_logs,
    mark_call_action_required,
    upsert_call_log,
)

CLINIC_ID    = "11111111-1111-4111-8111-111111111111"
CALL_ID      = "vapi-call-abc123"
CALL_STATUS  = "in_progress"

_NOW = datetime(2024, 6, 3, 9, 0, tzinfo=timezone.utc)

FAKE_ROW = {
    "id":               "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "clinic_id":        CLINIC_ID,
    "provider":         "vapi",
    "external_call_id": CALL_ID,
    "call_status":      CALL_STATUS,
    "action_required":  False,
    "urgency_level":    "normal",
    "created_at":       _NOW,
    "updated_at":       _NOW,
}


def _pool_with_row(row=None):
    """Return a fake pool whose fetchrow always returns *row*."""
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row or FAKE_ROW)
    pool.fetch    = AsyncMock(return_value=[FAKE_ROW])
    return pool


# ---------------------------------------------------------------------------
# 1. upsert_call_log calls fetchrow
# ---------------------------------------------------------------------------

async def test_upsert_call_log_calls_fetchrow():
    pool = _pool_with_row()
    result = await upsert_call_log(pool, CLINIC_ID, CALL_ID, CALL_STATUS)
    pool.fetchrow.assert_awaited_once()
    assert result["external_call_id"] == CALL_ID


# ---------------------------------------------------------------------------
# 2. upsert_call_log raises InvalidCallLogError for empty required fields
# ---------------------------------------------------------------------------

async def test_upsert_empty_clinic_id_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidCallLogError):
        await upsert_call_log(pool, "", CALL_ID, CALL_STATUS)


async def test_upsert_empty_external_call_id_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidCallLogError):
        await upsert_call_log(pool, CLINIC_ID, "", CALL_STATUS)


async def test_upsert_empty_call_status_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidCallLogError):
        await upsert_call_log(pool, CLINIC_ID, CALL_ID, "")


# ---------------------------------------------------------------------------
# 3. get_call_log_by_external_id calls fetchrow
# ---------------------------------------------------------------------------

async def test_get_call_log_calls_fetchrow():
    pool = _pool_with_row()
    result = await get_call_log_by_external_id(pool, CLINIC_ID, CALL_ID)
    pool.fetchrow.assert_awaited_once()
    assert result["external_call_id"] == CALL_ID


async def test_get_call_log_returns_none_when_not_found():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    result = await get_call_log_by_external_id(pool, CLINIC_ID, "nonexistent")
    assert result is None


# ---------------------------------------------------------------------------
# 4. list_recent_call_logs calls fetch
# ---------------------------------------------------------------------------

async def test_list_recent_call_logs_calls_fetch():
    pool = _pool_with_row()
    results = await list_recent_call_logs(pool, CLINIC_ID)
    pool.fetch.assert_awaited_once()
    assert isinstance(results, list)
    assert len(results) == 1


async def test_list_recent_call_logs_with_action_filter():
    pool = _pool_with_row()
    await list_recent_call_logs(pool, CLINIC_ID, action_required=True)
    pool.fetch.assert_awaited_once()
    # Verify the SQL call included the boolean filter argument
    args = pool.fetch.call_args[0]
    assert True in args


# ---------------------------------------------------------------------------
# 5. list_recent_call_logs validates limit
# ---------------------------------------------------------------------------

async def test_list_recent_call_logs_limit_zero_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidCallLogError):
        await list_recent_call_logs(pool, CLINIC_ID, limit=0)


async def test_list_recent_call_logs_limit_too_high_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidCallLogError):
        await list_recent_call_logs(pool, CLINIC_ID, limit=101)


async def test_list_recent_call_logs_limit_boundary_valid():
    pool = _pool_with_row()
    await list_recent_call_logs(pool, CLINIC_ID, limit=1)
    await list_recent_call_logs(pool, CLINIC_ID, limit=100)
    assert pool.fetch.await_count == 2


# ---------------------------------------------------------------------------
# 6. mark_call_action_required calls fetchrow
# ---------------------------------------------------------------------------

async def test_mark_call_action_required_calls_fetchrow():
    pool = _pool_with_row()
    await mark_call_action_required(pool, CLINIC_ID, CALL_ID)
    pool.fetchrow.assert_awaited_once()


async def test_mark_call_action_required_passes_true():
    pool = _pool_with_row()
    await mark_call_action_required(pool, CLINIC_ID, CALL_ID, action_required=True, urgency_level="high")
    args = pool.fetchrow.call_args[0]
    assert True in args
    assert "high" in args


# ---------------------------------------------------------------------------
# 7. SQL uses ON CONFLICT
# ---------------------------------------------------------------------------

async def test_upsert_sql_uses_on_conflict():
    """Verify the upsert SQL contains ON CONFLICT … DO UPDATE."""
    captured_sql: list[str] = []

    async def capturing_fetchrow(sql, *args):
        captured_sql.append(sql)
        return FAKE_ROW

    pool = MagicMock()
    pool.fetchrow = capturing_fetchrow

    await upsert_call_log(pool, CLINIC_ID, CALL_ID, CALL_STATUS)

    assert captured_sql, "fetchrow was never called"
    sql_lower = captured_sql[0].lower()
    assert "on conflict" in sql_lower, "SQL must contain ON CONFLICT"
    assert "do update" in sql_lower, "SQL must contain DO UPDATE"
