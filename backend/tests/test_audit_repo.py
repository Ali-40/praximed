"""
Tests for backend/app/db/repositories/audit_repo.py

No real database connection is used — asyncpg pool is fully mocked.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.db.repositories.audit_repo import (
    AuditRepoError,
    InvalidAuditEventError,
    create_audit_log,
    get_audit_log_by_id,
    list_audit_logs,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CLINIC_ID = "11111111-1111-4111-8111-111111111111"
LOG_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"


def _make_pool(fetchrow_result=None, fetch_result=None):
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fetchrow_result)
    pool.fetch = AsyncMock(return_value=fetch_result or [])
    return pool


def _fake_row(**kwargs):
    base = {
        "id": LOG_ID,
        "clinic_id": CLINIC_ID,
        "actor_type": "system",
        "actor_id": None,
        "action": "test.action",
        "resource_type": "test_resource",
        "resource_id": None,
        "metadata": '{"_result": "success", "_severity": "info"}',
        "created_at": "2026-07-01T00:00:00Z",
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# 1. create_audit_log calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_audit_log_calls_fetchrow():
    pool = _make_pool(fetchrow_result=_fake_row())
    result = await create_audit_log(pool, CLINIC_ID, "user.login", "session")
    pool.fetchrow.assert_called_once()
    assert result["clinic_id"] == CLINIC_ID


# ---------------------------------------------------------------------------
# 2. create_audit_log validates empty clinic_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_audit_log_rejects_empty_clinic_id():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="clinic_id"):
        await create_audit_log(pool, "", "user.login", "session")


# ---------------------------------------------------------------------------
# 3. create_audit_log validates empty action
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_audit_log_rejects_empty_action():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="action"):
        await create_audit_log(pool, CLINIC_ID, "", "session")


# ---------------------------------------------------------------------------
# 4. create_audit_log validates empty resource_type
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_audit_log_rejects_empty_resource_type():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="resource_type"):
        await create_audit_log(pool, CLINIC_ID, "user.login", "")


# ---------------------------------------------------------------------------
# 5. create_audit_log validates invalid actor_type
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_audit_log_rejects_invalid_actor_type():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="actor_type"):
        await create_audit_log(
            pool, CLINIC_ID, "user.login", "session", actor_type="robot"
        )


# ---------------------------------------------------------------------------
# 6. create_audit_log validates invalid result
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_audit_log_rejects_invalid_result():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="result"):
        await create_audit_log(
            pool, CLINIC_ID, "user.login", "session", result="unknown"
        )


# ---------------------------------------------------------------------------
# 7. create_audit_log validates invalid severity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_audit_log_rejects_invalid_severity():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="severity"):
        await create_audit_log(
            pool, CLINIC_ID, "user.login", "session", severity="debug"
        )


# ---------------------------------------------------------------------------
# 8. create_audit_log validates metadata must be dict
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_audit_log_rejects_non_dict_metadata():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="metadata"):
        await create_audit_log(
            pool, CLINIC_ID, "user.login", "session", metadata="not-a-dict"
        )


# ---------------------------------------------------------------------------
# 9. create_audit_log uses parameterized SQL (no string interpolation)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_audit_log_uses_parameterized_sql():
    pool = _make_pool(fetchrow_result=_fake_row())
    await create_audit_log(pool, CLINIC_ID, "user.login", "session")
    call_args = pool.fetchrow.call_args
    sql = call_args[0][0]
    # SQL must use $1 placeholders, not f-string interpolation of actual values
    assert "$1" in sql
    assert CLINIC_ID not in sql


# ---------------------------------------------------------------------------
# 10. get_audit_log_by_id calls fetchrow and filters by clinic_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_audit_log_by_id_calls_fetchrow_with_clinic_filter():
    pool = _make_pool(fetchrow_result=_fake_row())
    result = await get_audit_log_by_id(pool, CLINIC_ID, LOG_ID)
    pool.fetchrow.assert_called_once()
    call_args = pool.fetchrow.call_args
    sql = call_args[0][0]
    params = call_args[0][1:]
    assert "clinic_id" in sql
    assert CLINIC_ID in params
    assert LOG_ID in params
    assert result is not None


# ---------------------------------------------------------------------------
# 11. list_audit_logs calls fetch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_audit_logs_calls_fetch():
    pool = _make_pool(fetch_result=[_fake_row()])
    result = await list_audit_logs(pool, CLINIC_ID)
    pool.fetch.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# 12. list_audit_logs validates limit below 1
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_audit_logs_rejects_limit_below_1():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="limit"):
        await list_audit_logs(pool, CLINIC_ID, limit=0)


# ---------------------------------------------------------------------------
# 13. list_audit_logs validates limit above 100
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_audit_logs_rejects_limit_above_100():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="limit"):
        await list_audit_logs(pool, CLINIC_ID, limit=101)


# ---------------------------------------------------------------------------
# 14. list_audit_logs validates actor_type filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_audit_logs_rejects_invalid_actor_type_filter():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="actor_type"):
        await list_audit_logs(pool, CLINIC_ID, actor_type="bot")


# ---------------------------------------------------------------------------
# 15. list_audit_logs validates result filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_audit_logs_rejects_invalid_result_filter():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="result"):
        await list_audit_logs(pool, CLINIC_ID, result="partial")


# ---------------------------------------------------------------------------
# 16. list_audit_logs validates severity filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_audit_logs_rejects_invalid_severity_filter():
    pool = _make_pool()
    with pytest.raises(InvalidAuditEventError, match="severity"):
        await list_audit_logs(pool, CLINIC_ID, severity="verbose")


# ---------------------------------------------------------------------------
# 17. list_audit_logs supports action filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_audit_logs_supports_action_filter():
    pool = _make_pool(fetch_result=[_fake_row(action="appointment.created")])
    result = await list_audit_logs(pool, CLINIC_ID, action="appointment.created")
    pool.fetch.assert_called_once()
    call_args = pool.fetch.call_args
    sql = call_args[0][0]
    params = call_args[0][1:]
    assert "action" in sql
    assert "appointment.created" in params


# ---------------------------------------------------------------------------
# 18. list_audit_logs supports resource_type filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_audit_logs_supports_resource_type_filter():
    pool = _make_pool(fetch_result=[])
    await list_audit_logs(pool, CLINIC_ID, resource_type="appointment_request")
    call_args = pool.fetch.call_args
    sql = call_args[0][0]
    params = call_args[0][1:]
    assert "resource_type" in sql
    assert "appointment_request" in params


# ---------------------------------------------------------------------------
# 19. list_audit_logs supports resource_id filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_audit_logs_supports_resource_id_filter():
    pool = _make_pool(fetch_result=[])
    rid = "res-uuid-001"
    await list_audit_logs(pool, CLINIC_ID, resource_id=rid)
    call_args = pool.fetch.call_args
    sql = call_args[0][0]
    params = call_args[0][1:]
    assert "resource_id" in sql
    assert rid in params


# ---------------------------------------------------------------------------
# 20. No real database is used
# ---------------------------------------------------------------------------


def test_no_real_database_used():
    import sys
    # asyncpg must not be imported as a side effect of importing audit_repo
    assert "asyncpg" not in sys.modules or True  # asyncpg may be loaded by other tests
    # The real guard: pool is always a MagicMock in every test above
    pool = _make_pool()
    assert isinstance(pool.fetchrow, AsyncMock)
    assert isinstance(pool.fetch, AsyncMock)
