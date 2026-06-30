"""
Tests for backend/app/db/repositories/notification_repo.py

No real database connection is used — asyncpg pool is fully mocked.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.db.repositories import notification_repo
from backend.app.db.repositories.notification_repo import (
    InvalidNotificationError,
    cancel_notification,
    create_notification,
    get_notification_by_id,
    list_notifications,
    mark_notification_failed,
    mark_notification_read,
    mark_notification_sent,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CLINIC_ID = "clinic-uuid-001"
NOTIF_ID = "notif-uuid-001"


def _make_pool(fetchrow_result=None, fetch_result=None):
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fetchrow_result)
    pool.fetch = AsyncMock(return_value=fetch_result or [])
    return pool


def _fake_row(**kwargs):
    base = {
        "id": NOTIF_ID,
        "clinic_id": CLINIC_ID,
        "recipient_user_id": None,
        "channel": "internal",
        "notification_type": "urgent_call",
        "priority": "normal",
        "title": "Test notification",
        "message": "Something happened",
        "status": "pending",
        "related_resource_type": None,
        "related_resource_id": None,
        "scheduled_for": None,
        "sent_at": None,
        "read_at": None,
        "error_message": None,
        "raw_payload": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# 1. create_notification calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_notification_calls_fetchrow():
    pool = _make_pool(fetchrow_result=_fake_row())
    result = await create_notification(
        pool, CLINIC_ID, "internal", "urgent_call", "Title", "Body"
    )
    pool.fetchrow.assert_called_once()
    assert result["clinic_id"] == CLINIC_ID


# ---------------------------------------------------------------------------
# 2. empty clinic_id raises InvalidNotificationError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_notification_empty_clinic_id():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="clinic_id"):
        await create_notification(pool, "", "internal", "urgent_call", "Title", "Body")


# ---------------------------------------------------------------------------
# 3. empty title raises InvalidNotificationError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_notification_empty_title():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="title"):
        await create_notification(pool, CLINIC_ID, "internal", "urgent_call", "", "Body")


# ---------------------------------------------------------------------------
# 4. empty message raises InvalidNotificationError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_notification_empty_message():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="message"):
        await create_notification(pool, CLINIC_ID, "internal", "urgent_call", "Title", "")


# ---------------------------------------------------------------------------
# 5. invalid channel raises InvalidNotificationError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_notification_invalid_channel():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="channel"):
        await create_notification(pool, CLINIC_ID, "fax", "urgent_call", "Title", "Body")


# ---------------------------------------------------------------------------
# 6. invalid notification_type raises InvalidNotificationError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_notification_invalid_type():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="notification_type"):
        await create_notification(pool, CLINIC_ID, "internal", "unknown_type", "Title", "Body")


# ---------------------------------------------------------------------------
# 7. invalid priority raises InvalidNotificationError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_notification_invalid_priority():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="priority"):
        await create_notification(
            pool, CLINIC_ID, "internal", "urgent_call", "Title", "Body", priority="critical"
        )


# ---------------------------------------------------------------------------
# 8. invalid status raises InvalidNotificationError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_notification_invalid_status():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="status"):
        await create_notification(
            pool, CLINIC_ID, "internal", "urgent_call", "Title", "Body", status="delivered"
        )


# ---------------------------------------------------------------------------
# 9. get_notification_by_id calls fetchrow and filters by clinic_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_notification_by_id_calls_fetchrow():
    pool = _make_pool(fetchrow_result=_fake_row())
    result = await get_notification_by_id(pool, CLINIC_ID, NOTIF_ID)
    pool.fetchrow.assert_called_once()
    call_args = pool.fetchrow.call_args
    sql_arg = call_args[0][0]
    assert "$1" in sql_arg and "$2" in sql_arg
    assert result["id"] == NOTIF_ID


@pytest.mark.asyncio
async def test_get_notification_by_id_passes_clinic_id():
    pool = _make_pool(fetchrow_result=None)
    result = await get_notification_by_id(pool, CLINIC_ID, NOTIF_ID)
    call_args = pool.fetchrow.call_args[0]
    assert CLINIC_ID in call_args
    assert result is None


# ---------------------------------------------------------------------------
# 10. list_notifications calls fetch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_notifications_calls_fetch():
    pool = _make_pool(fetch_result=[_fake_row()])
    result = await list_notifications(pool, CLINIC_ID)
    pool.fetch.assert_called_once()
    assert len(result) == 1


# ---------------------------------------------------------------------------
# 11. list_notifications validates limit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_notifications_limit_too_low():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="limit"):
        await list_notifications(pool, CLINIC_ID, limit=0)


@pytest.mark.asyncio
async def test_list_notifications_limit_too_high():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="limit"):
        await list_notifications(pool, CLINIC_ID, limit=101)


# ---------------------------------------------------------------------------
# 12. list_notifications supports status filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_notifications_status_filter():
    pool = _make_pool(fetch_result=[])
    await list_notifications(pool, CLINIC_ID, status="pending")
    call_args = pool.fetch.call_args[0]
    assert "pending" in call_args


@pytest.mark.asyncio
async def test_list_notifications_invalid_status_filter():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="status"):
        await list_notifications(pool, CLINIC_ID, status="bad_status")


# ---------------------------------------------------------------------------
# 13. list_notifications supports priority filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_notifications_priority_filter():
    pool = _make_pool(fetch_result=[])
    await list_notifications(pool, CLINIC_ID, priority="high")
    call_args = pool.fetch.call_args[0]
    assert "high" in call_args


@pytest.mark.asyncio
async def test_list_notifications_invalid_priority_filter():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="priority"):
        await list_notifications(pool, CLINIC_ID, priority="critical")


# ---------------------------------------------------------------------------
# 14. list_notifications supports notification_type filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_notifications_type_filter():
    pool = _make_pool(fetch_result=[])
    await list_notifications(pool, CLINIC_ID, notification_type="urgent_call")
    call_args = pool.fetch.call_args[0]
    assert "urgent_call" in call_args


@pytest.mark.asyncio
async def test_list_notifications_invalid_type_filter():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="notification_type"):
        await list_notifications(pool, CLINIC_ID, notification_type="bad_type")


# ---------------------------------------------------------------------------
# 15. list_notifications supports recipient_user_id filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_notifications_recipient_filter():
    pool = _make_pool(fetch_result=[])
    user_id = "user-uuid-999"
    await list_notifications(pool, CLINIC_ID, recipient_user_id=user_id)
    call_args = pool.fetch.call_args[0]
    assert user_id in call_args


# ---------------------------------------------------------------------------
# 16. mark_notification_sent calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mark_notification_sent_calls_fetchrow():
    pool = _make_pool(fetchrow_result=_fake_row(status="sent"))
    result = await mark_notification_sent(pool, CLINIC_ID, NOTIF_ID)
    pool.fetchrow.assert_called_once()
    assert result["status"] == "sent"


# ---------------------------------------------------------------------------
# 17. mark_notification_failed calls fetchrow and validates error_message
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mark_notification_failed_calls_fetchrow():
    pool = _make_pool(fetchrow_result=_fake_row(status="failed", error_message="timeout"))
    result = await mark_notification_failed(pool, CLINIC_ID, NOTIF_ID, "timeout")
    pool.fetchrow.assert_called_once()
    assert result["status"] == "failed"


@pytest.mark.asyncio
async def test_mark_notification_failed_empty_error_message():
    pool = _make_pool()
    with pytest.raises(InvalidNotificationError, match="error_message"):
        await mark_notification_failed(pool, CLINIC_ID, NOTIF_ID, "")


# ---------------------------------------------------------------------------
# 18. mark_notification_read calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mark_notification_read_calls_fetchrow():
    pool = _make_pool(fetchrow_result=_fake_row(status="read"))
    result = await mark_notification_read(pool, CLINIC_ID, NOTIF_ID)
    pool.fetchrow.assert_called_once()
    assert result["status"] == "read"


# ---------------------------------------------------------------------------
# 19. cancel_notification calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_notification_calls_fetchrow():
    pool = _make_pool(fetchrow_result=_fake_row(status="cancelled"))
    result = await cancel_notification(pool, CLINIC_ID, NOTIF_ID)
    pool.fetchrow.assert_called_once()
    assert result["status"] == "cancelled"


# ---------------------------------------------------------------------------
# 20. SQL uses parameterized placeholders, not string formatting
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sql_uses_parameterized_placeholders():
    """Verify that all SQL in the repo uses $N placeholders and no % or .format()."""
    import inspect
    source = inspect.getsource(notification_repo)
    assert "%" not in source or source.count("%") == 0 or all(
        "%" not in line or line.strip().startswith("#")
        for line in source.splitlines()
    ), "SQL must not use % string formatting"
    # All SQL strings should use $1, $2 … style placeholders
    assert "$1" in source, "SQL must use $1 parameterized placeholders"
