"""
Integration tests for notification routes — PraxisMed Sprint 1 / Module 23
Updated: Sprint 3 / Module 38 — auth fixture overrides and tenant guard tests added.

Strategy:
- Use FastAPI TestClient; no real event loop or database.
- Override get_db_pool and get_auth_context via app.dependency_overrides.
- Patch notification_repo functions at their usage site in the route module.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.api.dependencies.auth import get_auth_context
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLINIC_ID       = "11111111-1111-4111-8111-111111111111"
OTHER_CLINIC_ID = "99999999-9999-4999-8999-999999999999"
NOTIFICATION_ID = "22222222-2222-4222-8222-222222222222"

BASE_URL   = "/notifications"
GET_ONE    = f"/notifications/{NOTIFICATION_ID}"
READ_URL   = f"/notifications/{NOTIFICATION_ID}/read"
CANCEL_URL = f"/notifications/{NOTIFICATION_ID}/cancel"

CREATE_BODY = {
    "clinic_id":        CLINIC_ID,
    "notification_type": "urgent_call",
    "title":            "Urgent call",
    "message":          "A call requires attention",
}

FAKE_ROW = {
    "id":                  NOTIFICATION_ID,
    "clinic_id":           CLINIC_ID,
    "channel":             "internal",
    "notification_type":   "urgent_call",
    "priority":            "urgent",
    "title":               "Urgent call",
    "message":             "A call requires attention",
    "status":              "pending",
    "recipient_user_id":   None,
    "related_resource_type": None,
    "related_resource_id": None,
    "scheduled_for":       None,
    "sent_at":             None,
    "read_at":             None,
    "error_message":       None,
    "raw_payload":         None,
    "created_at":          "2024-06-03T09:00:00+00:00",
    "updated_at":          "2024-06-03T09:00:00+00:00",
}

REPO = "backend.app.api.routes.notifications.notification_repo"
AUDIT_SAFE = "backend.app.modules.audit.audit_logger.safe_record_audit_event"

FAKE_POOL = MagicMock()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _staff_auth() -> AuthContext:
    return AuthContext(user_id="staff-1", clinic_id=CLINIC_ID, role="staff")


@pytest.fixture()
def client():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_auth_context] = _staff_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_auth_context, None)


@pytest.fixture()
def client_no_pool():
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides[get_auth_context] = _staff_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_auth_context, None)


@pytest.fixture()
def client_no_auth():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides.pop(get_auth_context, None)
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)


# ---------------------------------------------------------------------------
# 1. POST /notifications returns 200
# ---------------------------------------------------------------------------


def test_create_notification_returns_200(client):
    with patch(f"{REPO}.create_notification", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 2. POST route calls create_notification
# ---------------------------------------------------------------------------


def test_create_notification_calls_repo(client):
    with patch(f"{REPO}.create_notification", new=AsyncMock(return_value=FAKE_ROW)) as mock:
        client.post(BASE_URL, json=CREATE_BODY)
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 3. GET /notifications returns 200 list
# ---------------------------------------------------------------------------


def test_list_notifications_returns_200(client):
    with patch(f"{REPO}.list_notifications", new=AsyncMock(return_value=[FAKE_ROW])):
        resp = client.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert isinstance(data["notifications"], list)
    assert len(data["notifications"]) == 1


# ---------------------------------------------------------------------------
# 4. GET list passes filters
# ---------------------------------------------------------------------------


def test_list_notifications_passes_filters(client):
    with patch(f"{REPO}.list_notifications", new=AsyncMock(return_value=[])) as mock:
        client.get(BASE_URL, params={
            "clinic_id":        CLINIC_ID,
            "status":           "pending",
            "priority":         "high",
            "notification_type": "urgent_call",
            "recipient_user_id": "user-001",
            "limit":            "10",
        })
    call_kwargs = mock.call_args.kwargs
    assert call_kwargs["status"] == "pending"
    assert call_kwargs["priority"] == "high"
    assert call_kwargs["notification_type"] == "urgent_call"
    assert call_kwargs["recipient_user_id"] == "user-001"
    assert call_kwargs["limit"] == 10


# ---------------------------------------------------------------------------
# 5. GET /notifications/{id} returns 200 when found
# ---------------------------------------------------------------------------


def test_get_notification_returns_200(client):
    with patch(f"{REPO}.get_notification_by_id", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client.get(GET_ONE, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["notification"]["id"] == NOTIFICATION_ID


# ---------------------------------------------------------------------------
# 6. GET /notifications/{id} returns 404 when repo returns None
# ---------------------------------------------------------------------------


def test_get_notification_returns_404(client):
    with patch(f"{REPO}.get_notification_by_id", new=AsyncMock(return_value=None)):
        resp = client.get(GET_ONE, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 7. POST /notifications/{id}/read returns 200
# ---------------------------------------------------------------------------


def test_mark_read_returns_200(client):
    with patch(f"{REPO}.mark_notification_read", new=AsyncMock(return_value={**FAKE_ROW, "status": "read"})):
        resp = client.post(READ_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["notification"]["status"] == "read"


# ---------------------------------------------------------------------------
# 8. POST /notifications/{id}/read returns 404 when repo returns None
# ---------------------------------------------------------------------------


def test_mark_read_returns_404(client):
    with patch(f"{REPO}.mark_notification_read", new=AsyncMock(return_value=None)):
        resp = client.post(READ_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 9. POST /notifications/{id}/cancel returns 200
# ---------------------------------------------------------------------------


def test_cancel_notification_returns_200(client):
    with patch(f"{REPO}.cancel_notification", new=AsyncMock(return_value={**FAKE_ROW, "status": "cancelled"})):
        resp = client.post(CANCEL_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["notification"]["status"] == "cancelled"


# ---------------------------------------------------------------------------
# 10. POST /notifications/{id}/cancel returns 404 when repo returns None
# ---------------------------------------------------------------------------


def test_cancel_notification_returns_404(client):
    with patch(f"{REPO}.cancel_notification", new=AsyncMock(return_value=None)):
        resp = client.post(CANCEL_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 11. Missing db_pool returns HTTP 503
# ---------------------------------------------------------------------------


def test_missing_pool_returns_503(client_no_pool):
    resp = client_no_pool.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 503


# ---------------------------------------------------------------------------
# 12. Invalid request body returns HTTP 422
# ---------------------------------------------------------------------------


def test_invalid_body_returns_422(client):
    resp = client.post(BASE_URL, json={"clinic_id": CLINIC_ID})  # missing required fields
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 13. Repository validation error maps to HTTP 400
# ---------------------------------------------------------------------------


def test_repo_validation_error_returns_400(client):
    from backend.app.db.repositories.notification_repo import InvalidNotificationError
    with patch(
        f"{REPO}.create_notification",
        new=AsyncMock(side_effect=InvalidNotificationError("bad channel")),
    ):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 400
    assert "bad channel" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 14. Unexpected repository error maps to HTTP 500
# ---------------------------------------------------------------------------


def test_unexpected_repo_error_returns_500(client):
    with patch(
        f"{REPO}.create_notification",
        new=AsyncMock(side_effect=RuntimeError("db exploded")),
    ):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 500


# ---------------------------------------------------------------------------
# 15. Existing routes still work
# ---------------------------------------------------------------------------


def test_health_route_still_works(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_appointment_requests_route_still_works(client):
    resp = client.get("/appointment-requests", params={"clinic_id": CLINIC_ID})
    # Will fail at DB level (MagicMock pool), but route must be registered (not 404)
    assert resp.status_code != 404


def test_vapi_tools_route_still_registered(client):
    resp = client.post("/vapi/tools/check-availability", json={})
    assert resp.status_code != 404


# ---------------------------------------------------------------------------
# Auth enforcement tests (Module 38)
# ---------------------------------------------------------------------------


def test_missing_user_id_header_returns_401(client_no_auth):
    resp = client_no_auth.get(
        BASE_URL,
        params={"clinic_id": CLINIC_ID},
        headers={"X-Clinic-Id": CLINIC_ID, "X-User-Role": "staff"},
    )
    assert resp.status_code == 401


def test_missing_clinic_id_header_returns_401(client_no_auth):
    resp = client_no_auth.get(
        BASE_URL,
        params={"clinic_id": CLINIC_ID},
        headers={"X-User-Id": "staff-1", "X-User-Role": "staff"},
    )
    assert resp.status_code == 401


def test_wrong_clinic_returns_403(client_no_auth):
    with patch(f"{REPO}.list_notifications", new=AsyncMock(return_value=[])):
        resp = client_no_auth.get(
            BASE_URL,
            params={"clinic_id": CLINIC_ID},
            headers={
                "X-User-Id": "staff-1",
                "X-Clinic-Id": OTHER_CLINIC_ID,
                "X-User-Role": "staff",
            },
        )
    assert resp.status_code == 403


def test_viewer_role_denied_returns_403(client_no_auth):
    resp = client_no_auth.get(
        BASE_URL,
        params={"clinic_id": CLINIC_ID},
        headers={
            "X-User-Id": "user-1",
            "X-Clinic-Id": CLINIC_ID,
            "X-User-Role": "viewer",
        },
    )
    assert resp.status_code == 403


def test_staff_role_allowed(client_no_auth):
    with patch(f"{REPO}.list_notifications", new=AsyncMock(return_value=[])):
        resp = client_no_auth.get(
            BASE_URL,
            params={"clinic_id": CLINIC_ID},
            headers={
                "X-User-Id": "staff-1",
                "X-Clinic-Id": CLINIC_ID,
                "X-User-Role": "staff",
            },
        )
    assert resp.status_code == 200


def test_doctor_role_allowed(client_no_auth):
    with patch(f"{REPO}.list_notifications", new=AsyncMock(return_value=[])):
        resp = client_no_auth.get(
            BASE_URL,
            params={"clinic_id": CLINIC_ID},
            headers={
                "X-User-Id": "doctor-1",
                "X-Clinic-Id": CLINIC_ID,
                "X-User-Role": "doctor",
            },
        )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Audit logging tests (Module 43)
# ---------------------------------------------------------------------------


def test_create_notification_records_audit_event(client):
    with patch(f"{REPO}.create_notification", new=AsyncMock(return_value=FAKE_ROW)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "notification.create"
    assert event["resource_type"] == "clinic_notifications"
    assert event["actor_type"] == "user"


def test_mark_read_records_audit_event(client):
    with patch(f"{REPO}.mark_notification_read", new=AsyncMock(return_value={**FAKE_ROW, "status": "read"})), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(READ_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "notification.mark_read"


def test_cancel_notification_records_audit_event(client):
    with patch(f"{REPO}.cancel_notification", new=AsyncMock(return_value={**FAKE_ROW, "status": "cancelled"})), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(CANCEL_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "notification.cancel"


def test_audit_metadata_excludes_message_and_raw_payload(client):
    with patch(f"{REPO}.create_notification", new=AsyncMock(return_value=FAKE_ROW)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        client.post(BASE_URL, json=CREATE_BODY)
    event = mock_audit.call_args[0][1]
    meta = event.get("metadata", {})
    assert "message" not in meta
    assert "raw_payload" not in meta


def test_audit_failure_does_not_break_notification_route(client):
    with patch(f"{REPO}.create_notification", new=AsyncMock(return_value=FAKE_ROW)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": False, "audit_log": None, "message": "failed", "error": "db"})):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 200
