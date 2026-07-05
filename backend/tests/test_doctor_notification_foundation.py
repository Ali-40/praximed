"""
Tests for Module 123 — Doctor Notification System Foundation.

Verifies that:
- create_appointment_request_notification produces a clinic-scoped internal
  notification with correct type, resource link, and safe factual content.
- capture_vapi_appointment_request creates the notification as part of the
  capture flow and surfaces notification_created in the return dict.
- Notification list endpoint enforces authentication and clinic isolation.
- No external delivery channel (SMS/push/email/webhook) is used.
- No diagnosis or medical advice appears in notification content.

No real database, no real network, no secrets, no real patient data.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app
from backend.app.modules.notifications.notification_router import (
    create_appointment_request_notification,
)
from backend.app.modules.vapi.vapi_appointment_capture import (
    capture_vapi_appointment_request,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLINIC_ID       = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
OTHER_CLINIC_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
REQUEST_ID      = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
PATIENT_ID      = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
NOTIFICATION_ID = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"
PATIENT_NAME    = "Fake Notification Patient"
REASON          = "routine check"

FAKE_NOTIFICATION = {
    "id":                    NOTIFICATION_ID,
    "clinic_id":             CLINIC_ID,
    "channel":               "internal",
    "notification_type":     "appointment_request",
    "priority":              "normal",
    "title":                 "New appointment request",
    "message":               f"New appointment request from {PATIENT_NAME}. Reason: {REASON}. Action: Review and confirm.",
    "status":                "pending",
    "related_resource_type": "appointment_requests",
    "related_resource_id":   REQUEST_ID,
    "recipient_user_id":     None,
    "raw_payload":           None,
    "scheduled_for":         None,
    "sent_at":               None,
    "read_at":               None,
    "error_message":         None,
    "created_at":            "2026-07-05T09:00:00+00:00",
    "updated_at":            "2026-07-05T09:00:00+00:00",
}

FAKE_APPT_ROW = {
    "id":              REQUEST_ID,
    "clinic_id":       CLINIC_ID,
    "source":          "vapi",
    "source_ref":      "call-fake-001",
    "patient_name":    PATIENT_NAME,
    "patient_id":      PATIENT_ID,
    "status":          "new",
    "urgency_level":   "normal",
    "action_required": True,
}

FAKE_PATIENT = {
    "id":        PATIENT_ID,
    "clinic_id": CLINIC_ID,
    "full_name": PATIENT_NAME,
    "phone":     None,
    "status":    "active",
}

_REPO_PATH  = "backend.app.modules.notifications.notification_router.notification_repo"
_APPT_REPO  = "backend.app.modules.vapi.vapi_appointment_capture.appointment_request_repo"
_PAT_REPO   = "backend.app.modules.vapi.vapi_appointment_capture.patient_repo"
# notification_router is imported locally inside capture_vapi_appointment_request;
# patch it at its definition site so all callers see the mock.
_NOTIF_CREATE = "backend.app.modules.notifications.notification_router.create_appointment_request_notification"
_NOTIF_REPO_ROUTE = "backend.app.api.routes.notifications.notification_repo"
_AUDIT = "backend.app.modules.audit.audit_logger.safe_record_audit_event"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pool() -> MagicMock:
    return MagicMock()


def _staff_auth(clinic_id: str = CLINIC_ID) -> AuthContext:
    return AuthContext(user_id="staff-1", clinic_id=clinic_id, role="staff", auth_scheme="jwt_bearer")


def _doctor_auth(clinic_id: str = CLINIC_ID) -> AuthContext:
    return AuthContext(user_id="doctor-1", clinic_id=clinic_id, role="doctor", auth_scheme="jwt_bearer")


# ---------------------------------------------------------------------------
# 1. notification_type is appointment_request
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_notification_type_is_appointment_request():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
        )
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["notification_type"] == "appointment_request"


# ---------------------------------------------------------------------------
# 2. related_resource_type is appointment_requests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_related_resource_type_is_appointment_requests():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
        )
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["related_resource_type"] == "appointment_requests"


# ---------------------------------------------------------------------------
# 3. related_resource_id equals the appointment request id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_related_resource_id_equals_request_id():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
        )
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["related_resource_id"] == REQUEST_ID


# ---------------------------------------------------------------------------
# 4. clinic_id is passed through (tenant isolation)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_clinic_id_passed_through():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
        )
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["clinic_id"] == CLINIC_ID


# ---------------------------------------------------------------------------
# 5. channel is internal (no external delivery)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_channel_is_internal():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
        )
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["channel"] == "internal"
        assert call_kwargs["channel"] not in {"sms", "push", "email", "webhook"}


# ---------------------------------------------------------------------------
# 6. message includes patient_name
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_message_includes_patient_name():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
        )
        call_kwargs = mock_create.call_args.kwargs
        assert PATIENT_NAME in call_kwargs["message"]


# ---------------------------------------------------------------------------
# 7. message includes reason when provided
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_message_includes_reason():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
            reason=REASON,
        )
        call_kwargs = mock_create.call_args.kwargs
        assert REASON in call_kwargs["message"]


# ---------------------------------------------------------------------------
# 8. message includes suggested_next_action when provided
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_message_includes_suggested_next_action():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
            suggested_next_action="Review and confirm",
        )
        call_kwargs = mock_create.call_args.kwargs
        assert "Review and confirm" in call_kwargs["message"]


# ---------------------------------------------------------------------------
# 9. message does not contain diagnosis
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_message_does_not_contain_diagnosis():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
            reason="routine check",
            suggested_next_action="Review and confirm",
        )
        call_kwargs = mock_create.call_args.kwargs
        assert "diagnosis" not in call_kwargs["message"].lower()


# ---------------------------------------------------------------------------
# 10. message does not contain medical advice
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_message_does_not_contain_medical_advice():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
            reason="routine check",
            suggested_next_action="Review and confirm",
        )
        call_kwargs = mock_create.call_args.kwargs
        assert "medical advice" not in call_kwargs["message"].lower()


# ---------------------------------------------------------------------------
# 11. message gracefully omits reason when not provided
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_message_omits_reason_when_not_provided():
    pool = _make_pool()
    with patch(f"{_REPO_PATH}.create_notification", new=AsyncMock(return_value=FAKE_NOTIFICATION)) as mock_create:
        await create_appointment_request_notification(
            pool=pool,
            clinic_id=CLINIC_ID,
            request_id=REQUEST_ID,
            patient_name=PATIENT_NAME,
        )
        call_kwargs = mock_create.call_args.kwargs
        assert "Reason:" not in call_kwargs["message"]


# ---------------------------------------------------------------------------
# 12. Vapi capture sets notification_created=True on success
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_vapi_capture_notification_created_true_on_success():
    pool = _make_pool()

    cfg = MagicMock()
    cfg.tenant_id = CLINIC_ID
    loader = MagicMock()
    loader.load = AsyncMock(return_value=cfg)

    with (
        patch(f"{_PAT_REPO}.find_or_create_patient_from_vapi", new=AsyncMock(return_value=FAKE_PATIENT)),
        patch(f"{_APPT_REPO}.create_appointment_request", new=AsyncMock(return_value=FAKE_APPT_ROW)),
        patch(f"{_NOTIF_CREATE}", new=AsyncMock(return_value={"ok": True})),
    ):
        result = await capture_vapi_appointment_request(
            pool=pool,
            config_loader=loader,
            clinic_ref="fake-clinic",
            call_id="call-fake-001",
            patient_name=PATIENT_NAME,
            reason=REASON,
        )

    assert result["notification_created"] is True


# ---------------------------------------------------------------------------
# 13. Vapi capture sets notification_created=False when notification fails
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_vapi_capture_notification_created_false_on_failure():
    pool = _make_pool()

    cfg = MagicMock()
    cfg.tenant_id = CLINIC_ID
    loader = MagicMock()
    loader.load = AsyncMock(return_value=cfg)

    with (
        patch(f"{_PAT_REPO}.find_or_create_patient_from_vapi", new=AsyncMock(return_value=FAKE_PATIENT)),
        patch(f"{_APPT_REPO}.create_appointment_request", new=AsyncMock(return_value=FAKE_APPT_ROW)),
        patch(f"{_NOTIF_CREATE}", new=AsyncMock(side_effect=RuntimeError("db error"))),
    ):
        result = await capture_vapi_appointment_request(
            pool=pool,
            config_loader=loader,
            clinic_ref="fake-clinic",
            call_id="call-fake-001",
            patient_name=PATIENT_NAME,
            reason=REASON,
        )

    # Appointment is still created; notification failure is non-fatal
    assert result["ok"] is True
    assert result["notification_created"] is False


# ---------------------------------------------------------------------------
# 14. Notification list route: 401 without authentication
# ---------------------------------------------------------------------------


def test_list_notifications_401_without_auth():
    fake_pool = MagicMock()
    app.dependency_overrides[get_db_pool] = lambda: fake_pool
    try:
        with patch(f"{_NOTIF_REPO_ROUTE}.list_notifications", new=AsyncMock(return_value=[])):
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get(f"/notifications?clinic_id={CLINIC_ID}")
        assert response.status_code == 401
    finally:
        app.dependency_overrides.pop(get_db_pool, None)


# ---------------------------------------------------------------------------
# 15. Notification list route: 403 for wrong clinic
# ---------------------------------------------------------------------------


def test_list_notifications_403_wrong_clinic():
    fake_pool = MagicMock()

    def _override_pool():
        return fake_pool

    def _override_auth():
        return _staff_auth(clinic_id=OTHER_CLINIC_ID)

    app.dependency_overrides[get_db_pool] = _override_pool
    app.dependency_overrides[get_current_user] = _override_auth
    try:
        with patch(f"{_NOTIF_REPO_ROUTE}.list_notifications", new=AsyncMock(return_value=[])):
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get(f"/notifications?clinic_id={CLINIC_ID}")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_db_pool, None)
        app.dependency_overrides.pop(get_current_user, None)
