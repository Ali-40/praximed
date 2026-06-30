"""
Tests for backend/app/modules/notifications/notification_router.py

No real database connection — notification_repo.create_notification is mocked.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.modules.notifications.notification_router import (
    InvalidNotificationEventError,
    build_notification_event,
    create_appointment_request_notification,
    create_calendar_sync_failure_notification,
    create_urgent_call_notification,
    infer_priority,
    route_notification_event,
)

CLINIC_ID = "clinic-uuid-001"
CALL_ID = "call-uuid-001"
REQUEST_ID = "req-uuid-001"

_REPO_PATH = "backend.app.modules.notifications.notification_router.notification_repo"


def _make_pool():
    return MagicMock()


def _fake_notification(**kwargs):
    base = {
        "id": "notif-uuid-001",
        "clinic_id": CLINIC_ID,
        "channel": "internal",
        "notification_type": "urgent_call",
        "priority": "urgent",
        "title": "Urgent call requires attention",
        "message": "An urgent call requires immediate staff attention.",
        "status": "pending",
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# 1. infer_priority returns urgent for urgent_call
# ---------------------------------------------------------------------------


def test_infer_priority_urgent_call():
    assert infer_priority("urgent_call") == "urgent"


# ---------------------------------------------------------------------------
# 2. infer_priority returns high for callback_needed
# ---------------------------------------------------------------------------


def test_infer_priority_callback_needed():
    assert infer_priority("callback_needed") == "high"


# ---------------------------------------------------------------------------
# 3. infer_priority uses urgency_level override
# ---------------------------------------------------------------------------


def test_infer_priority_urgency_level_override():
    assert infer_priority("urgent_call", urgency_level="low") == "low"
    assert infer_priority("system", urgency_level="emergency") == "emergency"


# ---------------------------------------------------------------------------
# 4. infer_priority raises for invalid notification_type
# ---------------------------------------------------------------------------


def test_infer_priority_invalid_type():
    with pytest.raises(InvalidNotificationEventError, match="notification_type"):
        infer_priority("not_a_real_type")


# ---------------------------------------------------------------------------
# 5. infer_priority raises for invalid urgency_level
# ---------------------------------------------------------------------------


def test_infer_priority_invalid_urgency_level():
    with pytest.raises(InvalidNotificationEventError, match="urgency_level"):
        infer_priority("urgent_call", urgency_level="critical")


# ---------------------------------------------------------------------------
# 6. build_notification_event returns normalized event
# ---------------------------------------------------------------------------


def test_build_notification_event_returns_normalized():
    event = build_notification_event(
        clinic_id=CLINIC_ID,
        notification_type="urgent_call",
        title="Test title",
        message="Test message",
    )
    assert event["clinic_id"] == CLINIC_ID
    assert event["notification_type"] == "urgent_call"
    assert event["title"] == "Test title"
    assert event["message"] == "Test message"
    assert "priority" in event
    assert "channel" in event


# ---------------------------------------------------------------------------
# 7. build_notification_event defaults channel to internal
# ---------------------------------------------------------------------------


def test_build_notification_event_default_channel():
    event = build_notification_event(
        CLINIC_ID, "system", "Title", "Message"
    )
    assert event["channel"] == "internal"


# ---------------------------------------------------------------------------
# 8. build_notification_event infers priority when priority is None
# ---------------------------------------------------------------------------


def test_build_notification_event_infers_priority():
    event = build_notification_event(CLINIC_ID, "human_handoff", "Title", "Message")
    assert event["priority"] == "urgent"

    event2 = build_notification_event(CLINIC_ID, "summary_ready", "Title", "Message")
    assert event2["priority"] == "normal"


# ---------------------------------------------------------------------------
# 9. build_notification_event validates empty clinic_id
# ---------------------------------------------------------------------------


def test_build_notification_event_empty_clinic_id():
    with pytest.raises(InvalidNotificationEventError, match="clinic_id"):
        build_notification_event("", "urgent_call", "Title", "Message")


# ---------------------------------------------------------------------------
# 10. build_notification_event validates empty title
# ---------------------------------------------------------------------------


def test_build_notification_event_empty_title():
    with pytest.raises(InvalidNotificationEventError, match="title"):
        build_notification_event(CLINIC_ID, "urgent_call", "", "Message")


# ---------------------------------------------------------------------------
# 11. build_notification_event validates empty message
# ---------------------------------------------------------------------------


def test_build_notification_event_empty_message():
    with pytest.raises(InvalidNotificationEventError, match="message"):
        build_notification_event(CLINIC_ID, "urgent_call", "Title", "")


# ---------------------------------------------------------------------------
# 12. build_notification_event validates invalid channel
# ---------------------------------------------------------------------------


def test_build_notification_event_invalid_channel():
    with pytest.raises(InvalidNotificationEventError, match="channel"):
        build_notification_event(
            CLINIC_ID, "urgent_call", "Title", "Message", channel="telegram"
        )


# ---------------------------------------------------------------------------
# 13. build_notification_event validates invalid priority
# ---------------------------------------------------------------------------


def test_build_notification_event_invalid_priority():
    with pytest.raises(InvalidNotificationEventError, match="priority"):
        build_notification_event(
            CLINIC_ID, "urgent_call", "Title", "Message", priority="critical"
        )


# ---------------------------------------------------------------------------
# 14. route_notification_event calls notification_repo.create_notification
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_route_notification_event_calls_create_notification():
    pool = _make_pool()
    fake = _fake_notification()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=fake)) as mock_create:
        result = await route_notification_event(pool, {
            "clinic_id": CLINIC_ID,
            "notification_type": "urgent_call",
            "title": "Title",
            "message": "Message",
        })
    mock_create.assert_called_once()
    assert result["ok"] is True


# ---------------------------------------------------------------------------
# 15. route_notification_event passes normalized values to create_notification
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_route_notification_event_passes_normalized_values():
    pool = _make_pool()
    fake = _fake_notification()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=fake)) as mock_create:
        await route_notification_event(pool, {
            "clinic_id": CLINIC_ID,
            "notification_type": "appointment_request",
            "title": "New request",
            "message": "Patient X",
            "channel": "internal",
        })
    call_kwargs = mock_create.call_args[1]
    assert call_kwargs["clinic_id"] == CLINIC_ID
    assert call_kwargs["notification_type"] == "appointment_request"
    assert call_kwargs["channel"] == "internal"


# ---------------------------------------------------------------------------
# 16. create_urgent_call_notification — related_resource_type = clinic_call_logs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_urgent_call_notification_resource_type():
    pool = _make_pool()
    fake = _fake_notification(related_resource_type="clinic_call_logs", related_resource_id=CALL_ID)
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=fake)) as mock_create:
        result = await create_urgent_call_notification(pool, CLINIC_ID, CALL_ID)
    call_kwargs = mock_create.call_args[1]
    assert call_kwargs["related_resource_type"] == "clinic_call_logs"
    assert call_kwargs["related_resource_id"] == CALL_ID
    assert result["ok"] is True


# ---------------------------------------------------------------------------
# 17. create_urgent_call_notification includes caller_phone in message
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_urgent_call_notification_includes_caller_phone():
    pool = _make_pool()
    fake = _fake_notification()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=fake)) as mock_create:
        await create_urgent_call_notification(
            pool, CLINIC_ID, CALL_ID, caller_phone="+43123456789"
        )
    call_kwargs = mock_create.call_args[1]
    assert "+43123456789" in call_kwargs["message"]


# ---------------------------------------------------------------------------
# 18. create_appointment_request_notification — related_resource_type = appointment_requests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_appointment_request_notification_resource_type():
    pool = _make_pool()
    fake = _fake_notification(
        notification_type="appointment_request",
        related_resource_type="appointment_requests",
        related_resource_id=REQUEST_ID,
    )
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=fake)) as mock_create:
        result = await create_appointment_request_notification(
            pool, CLINIC_ID, REQUEST_ID, "Maria Muster"
        )
    call_kwargs = mock_create.call_args[1]
    assert call_kwargs["related_resource_type"] == "appointment_requests"
    assert call_kwargs["related_resource_id"] == REQUEST_ID
    assert result["ok"] is True


# ---------------------------------------------------------------------------
# 19. create_appointment_request_notification includes patient_name in message
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_appointment_request_notification_includes_patient_name():
    pool = _make_pool()
    fake = _fake_notification(notification_type="appointment_request")
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=fake)) as mock_create:
        await create_appointment_request_notification(
            pool, CLINIC_ID, REQUEST_ID, "Maria Muster"
        )
    call_kwargs = mock_create.call_args[1]
    assert "Maria Muster" in call_kwargs["message"]


# ---------------------------------------------------------------------------
# 20. create_calendar_sync_failure_notification — high priority
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_calendar_sync_failure_notification_high_priority():
    pool = _make_pool()
    fake = _fake_notification(
        notification_type="calendar_sync_failure",
        priority="high",
        related_resource_type="calendar_sync",
    )
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=fake)) as mock_create:
        result = await create_calendar_sync_failure_notification(
            pool, CLINIC_ID, "Google Calendar sync failed"
        )
    call_kwargs = mock_create.call_args[1]
    assert call_kwargs["priority"] == "high"
    assert call_kwargs["notification_type"] == "calendar_sync_failure"
    assert call_kwargs["related_resource_type"] == "calendar_sync"
    assert result["ok"] is True


# ---------------------------------------------------------------------------
# 21. Repository error propagates cleanly
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_route_notification_event_repo_error_propagates():
    pool = _make_pool()
    with patch(
        f"{_REPO_PATH}.create_notification",
        new=AsyncMock(side_effect=RuntimeError("DB connection lost")),
    ):
        with pytest.raises(RuntimeError, match="DB connection lost"):
            await route_notification_event(pool, {
                "clinic_id": CLINIC_ID,
                "notification_type": "system",
                "title": "Title",
                "message": "Message",
            })
