"""
Tests for backend/app/schemas/notifications.py — PraxisMed Sprint 1 / Module 23
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.schemas.notifications import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
)

CLINIC_ID = "clinic-uuid-001"


def _valid_body(**overrides) -> dict:
    base = {
        "clinic_id":        CLINIC_ID,
        "notification_type": "urgent_call",
        "title":            "Test title",
        "message":          "Test message",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. Valid NotificationCreate passes
# ---------------------------------------------------------------------------


def test_valid_notification_create_passes():
    model = NotificationCreate(**_valid_body())
    assert model.clinic_id == CLINIC_ID
    assert model.channel == "internal"
    assert model.priority == "normal"


# ---------------------------------------------------------------------------
# 2. Empty clinic_id fails
# ---------------------------------------------------------------------------


def test_empty_clinic_id_fails():
    with pytest.raises(ValidationError, match="clinic_id"):
        NotificationCreate(**_valid_body(clinic_id=""))


# ---------------------------------------------------------------------------
# 3. Empty title fails
# ---------------------------------------------------------------------------


def test_empty_title_fails():
    with pytest.raises(ValidationError, match="title"):
        NotificationCreate(**_valid_body(title=""))


# ---------------------------------------------------------------------------
# 4. Empty message fails
# ---------------------------------------------------------------------------


def test_empty_message_fails():
    with pytest.raises(ValidationError, match="message"):
        NotificationCreate(**_valid_body(message=""))


# ---------------------------------------------------------------------------
# 5. Invalid channel fails
# ---------------------------------------------------------------------------


def test_invalid_channel_fails():
    with pytest.raises(ValidationError, match="channel"):
        NotificationCreate(**_valid_body(channel="telegram"))


# ---------------------------------------------------------------------------
# 6. Invalid notification_type fails
# ---------------------------------------------------------------------------


def test_invalid_notification_type_fails():
    with pytest.raises(ValidationError, match="notification_type"):
        NotificationCreate(**_valid_body(notification_type="bad_type"))


# ---------------------------------------------------------------------------
# 7. Invalid priority fails
# ---------------------------------------------------------------------------


def test_invalid_priority_fails():
    with pytest.raises(ValidationError, match="priority"):
        NotificationCreate(**_valid_body(priority="critical"))


# ---------------------------------------------------------------------------
# 8. NotificationResponse accepts notification dict
# ---------------------------------------------------------------------------


def test_notification_response_accepts_dict():
    resp = NotificationResponse(ok=True, notification={"id": "abc", "status": "pending"})
    assert resp.ok is True
    assert resp.notification["id"] == "abc"


# ---------------------------------------------------------------------------
# 9. NotificationListResponse accepts list of dicts
# ---------------------------------------------------------------------------


def test_notification_list_response_accepts_list():
    resp = NotificationListResponse(
        ok=True,
        notifications=[{"id": "a"}, {"id": "b"}],
    )
    assert resp.ok is True
    assert len(resp.notifications) == 2
