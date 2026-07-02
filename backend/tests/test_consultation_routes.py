"""
Integration tests for consultation session routes — PraxisMed Sprint 2 / Module 29
Updated: Sprint 3 / Module 37 — auth fixture overrides and tenant guard tests added.
Updated: Sprint 7 / Module 62 — JWT current_user auth wired; auth tests use Bearer tokens.

Strategy:
- Use FastAPI TestClient; no real event loop or database.
- Override get_db_pool and get_current_user via app.dependency_overrides.
- Patch consultation_repo functions at their usage site in the route module.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLINIC_ID       = "11111111-1111-4111-8111-111111111111"
OTHER_CLINIC_ID = "99999999-9999-4999-8999-999999999999"
PATIENT_ID      = "33333333-3333-4333-8333-333333333333"
SESSION_ID      = "22222222-2222-4222-8222-222222222222"
JWT_SECRET      = "test-secret-consultation-routes-m62"

BASE_URL       = "/consultations"
GET_ONE_URL    = f"/consultations/{SESSION_ID}"
STATUS_URL     = f"/consultations/{SESSION_ID}/status"
AUDIO_URL      = f"/consultations/{SESSION_ID}/audio"
TRANSCRIPT_URL = f"/consultations/{SESSION_ID}/transcript"
DRAFT_URL      = f"/consultations/{SESSION_ID}/draft-summary"
APPROVE_URL    = f"/consultations/{SESSION_ID}/approve"
REJECT_URL     = f"/consultations/{SESSION_ID}/reject"
ARCHIVE_URL    = f"/consultations/{SESSION_ID}/archive"

CREATE_BODY = {
    "clinic_id":  CLINIC_ID,
    "patient_id": PATIENT_ID,
}

FAKE_ROW = {
    "id":                  SESSION_ID,
    "clinic_id":           CLINIC_ID,
    "patient_id":          PATIENT_ID,
    "doctor_user_id":      None,
    "source":              "manual",
    "status":              "created",
    "title":               None,
    "reason_for_visit":    None,
    "audio_file_path":     None,
    "transcript_text":     None,
    "draft_summary":       None,
    "approved_summary":    None,
    "approval_status":     "not_ready",
    "approved_by_user_id": None,
    "approved_at":         None,
    "rejected_reason":     None,
    "raw_payload":         None,
    "created_at":          "2024-06-01T10:00:00+00:00",
    "updated_at":          "2024-06-01T10:00:00+00:00",
}

REPO = "backend.app.api.routes.consultations.consultation_repo"
AUDIT_SAFE = "backend.app.modules.audit.audit_logger.safe_record_audit_event"

FAKE_POOL = MagicMock()


# ---------------------------------------------------------------------------
# Auth context factories
# ---------------------------------------------------------------------------


def _doctor_auth() -> AuthContext:
    return AuthContext(user_id="doctor-1", clinic_id=CLINIC_ID, role="doctor",
                       auth_scheme="jwt_bearer")


def _owner_auth() -> AuthContext:
    return AuthContext(user_id="owner-1", clinic_id=CLINIC_ID, role="owner",
                       auth_scheme="jwt_bearer")


def _staff_auth() -> AuthContext:
    return AuthContext(user_id="staff-1", clinic_id=CLINIC_ID, role="staff",
                       auth_scheme="jwt_bearer")


def _viewer_auth() -> AuthContext:
    return AuthContext(user_id="viewer-1", clinic_id=CLINIC_ID, role="viewer",
                       auth_scheme="jwt_bearer")


def _wrong_clinic_auth() -> AuthContext:
    return AuthContext(user_id="doctor-1", clinic_id=OTHER_CLINIC_ID, role="doctor",
                       auth_scheme="jwt_bearer")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_current_user] = _doctor_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def client_no_pool():
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides[get_current_user] = _doctor_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def client_no_auth():
    """No get_current_user override — real JWT dependency runs."""
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides.pop(get_current_user, None)
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.pop(get_db_pool, None)


@pytest.fixture()
def client_wrong_clinic():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_current_user] = _wrong_clinic_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def client_staff():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_current_user] = _staff_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def client_viewer():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_current_user] = _viewer_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def client_owner():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_current_user] = _owner_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# 1. POST /consultations returns 200
# ---------------------------------------------------------------------------


def test_create_consultation_returns_200(client):
    with patch(f"{REPO}.create_consultation_session", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 2. POST route calls create_consultation_session
# ---------------------------------------------------------------------------


def test_create_consultation_calls_repo(client):
    with patch(
        f"{REPO}.create_consultation_session", new=AsyncMock(return_value=FAKE_ROW)
    ) as mock:
        client.post(BASE_URL, json=CREATE_BODY)
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 3. GET /consultations returns 200 list
# ---------------------------------------------------------------------------


def test_list_consultations_returns_200(client):
    with patch(f"{REPO}.list_consultation_sessions", new=AsyncMock(return_value=[FAKE_ROW])):
        resp = client.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert len(data["consultations"]) == 1


# ---------------------------------------------------------------------------
# 4. GET list passes all filters
# ---------------------------------------------------------------------------


def test_list_passes_filters(client):
    with patch(
        f"{REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])
    ) as mock:
        client.get(BASE_URL, params={
            "clinic_id":       CLINIC_ID,
            "patient_id":      PATIENT_ID,
            "doctor_user_id":  "doc-1",
            "status":          "draft_ready",
            "approval_status": "pending_review",
            "source":          "vapi",
            "limit":           "10",
        })
    kwargs = mock.call_args.kwargs
    assert kwargs["patient_id"] == PATIENT_ID
    assert kwargs["doctor_user_id"] == "doc-1"
    assert kwargs["status"] == "draft_ready"
    assert kwargs["approval_status"] == "pending_review"
    assert kwargs["source"] == "vapi"
    assert kwargs["limit"] == 10


# ---------------------------------------------------------------------------
# 5. GET /consultations/{session_id} returns 200 when found
# ---------------------------------------------------------------------------


def test_get_consultation_returns_200(client):
    with patch(
        f"{REPO}.get_consultation_session_by_id", new=AsyncMock(return_value=FAKE_ROW)
    ):
        resp = client.get(GET_ONE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["consultation"]["id"] == SESSION_ID


# ---------------------------------------------------------------------------
# 6. GET /consultations/{session_id} returns 404 when repo returns None
# ---------------------------------------------------------------------------


def test_get_consultation_returns_404(client):
    with patch(
        f"{REPO}.get_consultation_session_by_id", new=AsyncMock(return_value=None)
    ):
        resp = client.get(GET_ONE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 7. PATCH /consultations/{session_id}/status returns 200
# ---------------------------------------------------------------------------


def test_update_status_returns_200(client):
    updated = {**FAKE_ROW, "status": "transcribing"}
    with patch(f"{REPO}.update_consultation_status", new=AsyncMock(return_value=updated)):
        resp = client.patch(
            STATUS_URL,
            params={"clinic_id": CLINIC_ID},
            json={"status": "transcribing"},
        )
    assert resp.status_code == 200
    assert resp.json()["consultation"]["status"] == "transcribing"


# ---------------------------------------------------------------------------
# 8. PATCH status returns 404 when repo returns None
# ---------------------------------------------------------------------------


def test_update_status_returns_404(client):
    with patch(f"{REPO}.update_consultation_status", new=AsyncMock(return_value=None)):
        resp = client.patch(
            STATUS_URL,
            params={"clinic_id": CLINIC_ID},
            json={"status": "transcribing"},
        )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 9. POST /consultations/{session_id}/audio returns 200
# ---------------------------------------------------------------------------


def test_attach_audio_returns_200(client):
    updated = {**FAKE_ROW, "audio_file_path": "/audio/rec.mp3", "status": "audio_uploaded"}
    with patch(f"{REPO}.attach_audio_to_session", new=AsyncMock(return_value=updated)):
        resp = client.post(
            AUDIO_URL,
            params={"clinic_id": CLINIC_ID},
            json={"audio_file_path": "/audio/rec.mp3"},
        )
    assert resp.status_code == 200
    assert resp.json()["consultation"]["audio_file_path"] == "/audio/rec.mp3"


# ---------------------------------------------------------------------------
# 10. POST /consultations/{session_id}/transcript returns 200
# ---------------------------------------------------------------------------


def test_save_transcript_returns_200(client):
    updated = {**FAKE_ROW, "transcript_text": "Patient coughs.", "status": "transcribed"}
    with patch(f"{REPO}.save_transcript", new=AsyncMock(return_value=updated)):
        resp = client.post(
            TRANSCRIPT_URL,
            params={"clinic_id": CLINIC_ID},
            json={"transcript_text": "Patient coughs."},
        )
    assert resp.status_code == 200
    assert resp.json()["consultation"]["transcript_text"] == "Patient coughs."


# ---------------------------------------------------------------------------
# 11. POST /consultations/{session_id}/draft-summary returns 200
# ---------------------------------------------------------------------------


def test_save_draft_summary_returns_200(client):
    updated = {**FAKE_ROW, "status": "draft_ready", "approval_status": "pending_review"}
    with patch(f"{REPO}.save_draft_summary", new=AsyncMock(return_value=updated)):
        resp = client.post(
            DRAFT_URL,
            params={"clinic_id": CLINIC_ID},
            json={"draft_summary": {"diagnosis": "Flu"}},
        )
    assert resp.status_code == 200
    assert resp.json()["consultation"]["status"] == "draft_ready"


# ---------------------------------------------------------------------------
# 12. POST /consultations/{session_id}/approve returns 200
# ---------------------------------------------------------------------------


def test_approve_consultation_returns_200(client):
    updated = {**FAKE_ROW, "status": "approved", "approval_status": "approved"}
    with patch(f"{REPO}.approve_consultation_summary", new=AsyncMock(return_value=updated)):
        resp = client.post(
            APPROVE_URL,
            params={"clinic_id": CLINIC_ID},
            json={
                "approved_summary": {"final": "All clear"},
                "approved_by_user_id": "doc-1",
            },
        )
    assert resp.status_code == 200
    assert resp.json()["consultation"]["approval_status"] == "approved"


# ---------------------------------------------------------------------------
# 13. POST /consultations/{session_id}/reject returns 200
# ---------------------------------------------------------------------------


def test_reject_consultation_returns_200(client):
    updated = {**FAKE_ROW, "status": "rejected", "approval_status": "rejected"}
    with patch(f"{REPO}.reject_consultation_summary", new=AsyncMock(return_value=updated)):
        resp = client.post(
            REJECT_URL,
            params={"clinic_id": CLINIC_ID},
            json={"rejected_reason": "Incomplete notes"},
        )
    assert resp.status_code == 200
    assert resp.json()["consultation"]["status"] == "rejected"


# ---------------------------------------------------------------------------
# 14. POST /consultations/{session_id}/archive returns 200
# ---------------------------------------------------------------------------


def test_archive_consultation_returns_200(client):
    archived = {**FAKE_ROW, "status": "archived"}
    with patch(f"{REPO}.archive_consultation_session", new=AsyncMock(return_value=archived)):
        resp = client.post(ARCHIVE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["consultation"]["status"] == "archived"


# ---------------------------------------------------------------------------
# 15. Missing db_pool returns HTTP 503
# ---------------------------------------------------------------------------


def test_missing_pool_returns_503(client_no_pool):
    resp = client_no_pool.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 503


# ---------------------------------------------------------------------------
# 16. Invalid request body returns HTTP 422
# ---------------------------------------------------------------------------


def test_invalid_body_returns_422(client):
    resp = client.post(BASE_URL, json={"clinic_id": CLINIC_ID})  # missing patient_id
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 17. Repository validation error maps to HTTP 400
# ---------------------------------------------------------------------------


def test_repo_validation_error_returns_400(client):
    from backend.app.db.repositories.consultation_repo import InvalidConsultationSessionError
    with patch(
        f"{REPO}.create_consultation_session",
        new=AsyncMock(side_effect=InvalidConsultationSessionError("bad source")),
    ):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 400
    assert "bad source" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 18. Unexpected repository error maps to HTTP 500
# ---------------------------------------------------------------------------


def test_unexpected_repo_error_returns_500(client):
    with patch(
        f"{REPO}.create_consultation_session",
        new=AsyncMock(side_effect=RuntimeError("db exploded")),
    ):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 500


# ---------------------------------------------------------------------------
# 19. Existing routes still work
# ---------------------------------------------------------------------------


def test_health_route_still_works(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_patients_route_still_registered(client):
    # Patients uses get_current_user, which is overridden in this fixture.
    resp = client.get("/patients", params={"clinic_id": CLINIC_ID})
    assert resp.status_code != 404


def test_notifications_route_still_registered(client):
    resp = client.get("/notifications", params={"clinic_id": CLINIC_ID})
    assert resp.status_code != 404


def test_appointment_requests_route_still_registered(client):
    resp = client.get("/appointment-requests", params={"clinic_id": CLINIC_ID})
    assert resp.status_code != 404


def test_vapi_tools_route_still_registered(client):
    resp = client.post("/vapi/tools/check-availability", json={})
    assert resp.status_code != 404


# ---------------------------------------------------------------------------
# JWT auth enforcement tests (Module 62)
# ---------------------------------------------------------------------------


def test_missing_authorization_header_returns_401(client_no_auth):
    """No Authorization header → 401 from get_current_user."""
    resp = client_no_auth.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 401


def test_invalid_bearer_token_returns_401(client_no_auth, monkeypatch):
    """Malformed Bearer token → 401 from get_current_user."""
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    resp = client_no_auth.get(
        BASE_URL,
        params={"clinic_id": CLINIC_ID},
        headers={"Authorization": "Bearer not.a.real.jwt"},
    )
    assert resp.status_code == 401


def test_wrong_clinic_returns_403(client_wrong_clinic):
    """Valid JWT for a different clinic → 403 from require_clinical_clinic_access."""
    with patch(f"{REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])):
        resp = client_wrong_clinic.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 403


def test_staff_role_denied_returns_403(client_staff):
    """Staff role is not in CLINICAL_ROLES → 403."""
    with patch(f"{REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])):
        resp = client_staff.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 403


def test_viewer_role_denied_returns_403(client_viewer):
    """Viewer role is not in CLINICAL_ROLES → 403."""
    with patch(f"{REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])):
        resp = client_viewer.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 403


def test_doctor_role_allowed(client):
    """Doctor is in CLINICAL_ROLES → 200."""
    with patch(f"{REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])):
        resp = client.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200


def test_owner_role_allowed(client_owner):
    """Owner is in CLINICAL_ROLES → 200."""
    with patch(f"{REPO}.list_consultation_sessions", new=AsyncMock(return_value=[])):
        resp = client_owner.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200


def test_valid_jwt_can_create_consultation(client):
    """Authenticated doctor can create a consultation."""
    with patch(f"{REPO}.create_consultation_session", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 200
    assert resp.json()["consultation"]["clinic_id"] == CLINIC_ID


def test_valid_jwt_can_approve_consultation(client):
    """Authenticated doctor can approve a consultation."""
    updated = {**FAKE_ROW, "approval_status": "approved"}
    with patch(f"{REPO}.approve_consultation_summary", new=AsyncMock(return_value=updated)):
        resp = client.post(
            APPROVE_URL,
            params={"clinic_id": CLINIC_ID},
            json={"approved_summary": {"diagnosis": "ok"}, "approved_by_user_id": "doc-1"},
        )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Audit logging tests (Module 43)
# ---------------------------------------------------------------------------


def test_create_consultation_records_audit_event(client):
    with patch(f"{REPO}.create_consultation_session", new=AsyncMock(return_value=FAKE_ROW)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "consultation.create"
    assert event["resource_type"] == "consultation_sessions"


def test_save_transcript_records_audit_event(client):
    updated = {**FAKE_ROW, "transcript_text": "..."}
    with patch(f"{REPO}.save_transcript", new=AsyncMock(return_value=updated)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(TRANSCRIPT_URL, params={"clinic_id": CLINIC_ID}, json={"transcript_text": "..."})
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "consultation.transcript_save"


def test_approve_consultation_records_critical_audit_event(client):
    updated = {**FAKE_ROW, "approval_status": "approved"}
    with patch(f"{REPO}.approve_consultation_summary", new=AsyncMock(return_value=updated)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(APPROVE_URL, params={"clinic_id": CLINIC_ID},
                           json={"approved_summary": {"diagnosis": "ok"}, "approved_by_user_id": "doc-1"})
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "consultation.approve"
    assert event["severity"] == "critical"


def test_reject_consultation_records_critical_audit_event(client):
    updated = {**FAKE_ROW, "approval_status": "rejected"}
    with patch(f"{REPO}.reject_consultation_summary", new=AsyncMock(return_value=updated)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(REJECT_URL, params={"clinic_id": CLINIC_ID},
                           json={"rejected_reason": "incomplete", "rejected_by_user_id": "doc-1"})
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "consultation.reject"
    assert event["severity"] == "critical"


def test_audit_metadata_excludes_phi_fields(client):
    sensitive = {**FAKE_ROW, "transcript_text": "Patient says X", "draft_summary": {"key": "val"},
                 "approved_summary": {"key": "val"}, "rejected_reason": "private"}
    with patch(f"{REPO}.create_consultation_session", new=AsyncMock(return_value=sensitive)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        client.post(BASE_URL, json=CREATE_BODY)
    event = mock_audit.call_args[0][1]
    meta = event.get("metadata", {})
    assert "transcript_text" not in meta
    assert "draft_summary" not in meta
    assert "approved_summary" not in meta
    assert "rejected_reason" not in meta


def test_audit_failure_does_not_break_consultation_route(client):
    with patch(f"{REPO}.create_consultation_session", new=AsyncMock(return_value=FAKE_ROW)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": False, "audit_log": None, "message": "failed", "error": "db"})):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 200
