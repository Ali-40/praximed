"""
Tests for Sprint 17 / Module 122 — Pre-Appointment Summary Foundation.

Covers:
  - build_pre_appointment_summary (pure service, unit tests)
  - GET /appointment-requests/{id}/pre-appointment-summary (route integration tests)

No real patient data. No secrets. Fake data only.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.services.pre_appointment_summary import (
    build_pre_appointment_summary,
    _suggested_next_action,
)
from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app

# ---------------------------------------------------------------------------
# Fake data constants — no real patients, no real clinics
# ---------------------------------------------------------------------------

CLINIC_ID       = "11111111-1111-4111-8111-111111111111"
OTHER_CLINIC_ID = "99999999-9999-4999-8999-999999999999"
REQUEST_ID      = "22222222-2222-4222-8222-222222222222"
PATIENT_ID      = "33333333-3333-4333-8333-333333333333"

FAKE_REQUEST = {
    "id":                  REQUEST_ID,
    "clinic_id":           CLINIC_ID,
    "source":              "vapi",
    "source_ref":          "call-fake-001",
    "patient_name":        "Fake Patient",
    "patient_phone":       "+43000000099",
    "patient_email":       None,
    "date_of_birth":       None,
    "reason":              "Routine checkup",
    "preferred_starts_at": None,
    "preferred_ends_at":   None,
    "status":              "new",
    "urgency_level":       "normal",
    "action_required":     True,
    "assigned_user_id":    None,
    "patient_id":          PATIENT_ID,
    "raw_payload":         None,
    "created_at":          "2026-07-05T09:00:00+00:00",
    "updated_at":          "2026-07-05T09:00:00+00:00",
}

FAKE_PATIENT = {
    "id":        PATIENT_ID,
    "clinic_id": CLINIC_ID,
    "full_name": "Fake Patient",
    "phone":     "+43000000099",
    "email":     None,
    "status":    "active",
}

REPO    = "backend.app.api.routes.appointment_requests.appointment_request_repo"
PAT     = "backend.app.api.routes.appointment_requests.patient_repo"
FAKE_POOL = MagicMock()

SUMMARY_URL = f"/appointment-requests/{REQUEST_ID}/pre-appointment-summary"

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


def _staff_auth() -> AuthContext:
    return AuthContext(user_id="u1", clinic_id=CLINIC_ID, role="staff", auth_scheme="jwt_bearer")


def _wrong_clinic_auth() -> AuthContext:
    return AuthContext(user_id="u1", clinic_id=OTHER_CLINIC_ID, role="staff", auth_scheme="jwt_bearer")


# ---------------------------------------------------------------------------
# Route client fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_current_user] = _staff_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def wrong_clinic_client():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_current_user] = _wrong_clinic_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def unauth_client():
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)


# ===========================================================================
# Service unit tests — build_pre_appointment_summary
# ===========================================================================

# 1. patient_name comes from appointment_request
def test_summary_includes_patient_name():
    s = build_pre_appointment_summary(FAKE_REQUEST)
    assert s["patient_name"] == "Fake Patient"


# 2. patient_phone from linked patient row (preferred over intake phone)
def test_summary_uses_patient_phone_from_linked_patient():
    patient = {**FAKE_PATIENT, "phone": "+43111111111"}
    req = {**FAKE_REQUEST, "patient_phone": "+43000000099"}
    s = build_pre_appointment_summary(req, patient=patient)
    assert s["patient_phone"] == "+43111111111"


# 3. Falls back to appointment_request.patient_phone when no patient
def test_summary_falls_back_to_request_phone_when_no_patient():
    req = {**FAKE_REQUEST, "patient_id": None}
    s = build_pre_appointment_summary(req, patient=None)
    assert s["patient_phone"] == "+43000000099"


# 4. patient_type = "returning" when patient_id is set
def test_summary_patient_type_returning_when_linked():
    s = build_pre_appointment_summary(FAKE_REQUEST, patient=FAKE_PATIENT)
    assert s["patient_type"] == "returning"


# 5. patient_type = "new" when patient_id is None
def test_summary_patient_type_new_when_not_linked():
    req = {**FAKE_REQUEST, "patient_id": None}
    s = build_pre_appointment_summary(req)
    assert s["patient_type"] == "new"


# 6. reason included
def test_summary_includes_reason():
    s = build_pre_appointment_summary(FAKE_REQUEST)
    assert s["reason"] == "Routine checkup"


# 7. preferred_starts_at included (None when not set)
def test_summary_includes_preferred_starts_at_none():
    s = build_pre_appointment_summary(FAKE_REQUEST)
    assert s["preferred_starts_at"] is None


# 8. source, status, action_required, urgency_level included
def test_summary_includes_appointment_metadata():
    s = build_pre_appointment_summary(FAKE_REQUEST)
    assert s["source"] == "vapi"
    assert s["status"] == "new"
    assert s["action_required"] is True
    assert s["urgency_level"] == "normal"


# 9. previous_request_count included
def test_summary_includes_previous_request_count():
    s = build_pre_appointment_summary(FAKE_REQUEST, previous_request_count=3)
    assert s["previous_request_count"] == 3


# 10. suggested_next_action = "Review and confirm" for new + action_required
def test_suggested_next_action_review_and_confirm():
    assert _suggested_next_action("new", True) == "Review and confirm"


# 11. suggested_next_action = "Call patient" for callback_needed
def test_suggested_next_action_call_patient():
    assert _suggested_next_action("callback_needed", True) == "Call patient"


# 12. suggested_next_action for confirmed
def test_suggested_next_action_confirmed():
    assert _suggested_next_action("confirmed", False) == "Appointment confirmed — no further action needed"


# 13. suggested_next_action for archived/rejected/cancelled
def test_suggested_next_action_no_action_required():
    for status in ("archived", "rejected", "cancelled"):
        assert _suggested_next_action(status, False) == "No action required"


# 14. No "diagnosis" key in output
def test_summary_has_no_diagnosis_key():
    s = build_pre_appointment_summary(FAKE_REQUEST, patient=FAKE_PATIENT)
    assert "diagnosis" not in s


# 15. No "medical_recommendation" key in output
def test_summary_has_no_medical_recommendation_key():
    s = build_pre_appointment_summary(FAKE_REQUEST, patient=FAKE_PATIENT)
    assert "medical_recommendation" not in s


# 16. No "treatment" key in output
def test_summary_has_no_treatment_key():
    s = build_pre_appointment_summary(FAKE_REQUEST, patient=FAKE_PATIENT)
    assert "treatment" not in s


# 17. safety_note present
def test_summary_includes_safety_note():
    s = build_pre_appointment_summary(FAKE_REQUEST)
    assert "safety_note" in s
    assert "no medical advice" in s["safety_note"].lower()


# 18. Handles missing patient_id gracefully (no exception)
def test_summary_handles_no_patient_id():
    req = {**FAKE_REQUEST, "patient_id": None}
    s = build_pre_appointment_summary(req, patient=None)
    assert s["patient_type"] == "new"
    assert "safety_note" in s


# ===========================================================================
# Route integration tests — GET /appointment-requests/{id}/pre-appointment-summary
# ===========================================================================

# 19. Route returns 200 with summary when request exists
def test_route_returns_summary(client):
    with patch(f"{REPO}.get_appointment_request_by_id", new=AsyncMock(return_value=FAKE_REQUEST)), \
         patch(f"{PAT}.get_patient_by_id", new=AsyncMock(return_value=FAKE_PATIENT)), \
         patch(f"{REPO}.count_requests_for_patient", new=AsyncMock(return_value=0)):
        resp = client.get(SUMMARY_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert "summary" in body
    assert body["summary"]["patient_name"] == "Fake Patient"


# 20. Route returns 404 when appointment request not found
def test_route_returns_404_when_not_found(client):
    with patch(f"{REPO}.get_appointment_request_by_id", new=AsyncMock(return_value=None)):
        resp = client.get(SUMMARY_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 404


# 21. Route enforces auth — 401 without token
def test_route_requires_auth(unauth_client):
    resp = unauth_client.get(SUMMARY_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 401


# 22. Wrong clinic_id returns 403
def test_route_rejects_wrong_clinic(wrong_clinic_client):
    resp = wrong_clinic_client.get(SUMMARY_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 403


# 23. Summary from route includes required fields
def test_route_summary_includes_all_required_fields(client):
    with patch(f"{REPO}.get_appointment_request_by_id", new=AsyncMock(return_value=FAKE_REQUEST)), \
         patch(f"{PAT}.get_patient_by_id", new=AsyncMock(return_value=FAKE_PATIENT)), \
         patch(f"{REPO}.count_requests_for_patient", new=AsyncMock(return_value=1)):
        resp = client.get(SUMMARY_URL, params={"clinic_id": CLINIC_ID})
    summary = resp.json()["summary"]
    for field in ("request_id", "clinic_id", "patient_name", "patient_type",
                  "source", "status", "action_required", "suggested_next_action",
                  "safety_note", "generated_at"):
        assert field in summary, f"Missing field: {field}"


# 24. Route skips patient lookup when patient_id is None
def test_route_handles_no_patient_id(client):
    req_no_patient = {**FAKE_REQUEST, "patient_id": None}
    with patch(f"{REPO}.get_appointment_request_by_id", new=AsyncMock(return_value=req_no_patient)):
        resp = client.get(SUMMARY_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["summary"]["patient_type"] == "new"


# 25. Summary does not contain diagnosis key (route level)
def test_route_summary_has_no_diagnosis(client):
    with patch(f"{REPO}.get_appointment_request_by_id", new=AsyncMock(return_value=FAKE_REQUEST)), \
         patch(f"{PAT}.get_patient_by_id", new=AsyncMock(return_value=FAKE_PATIENT)), \
         patch(f"{REPO}.count_requests_for_patient", new=AsyncMock(return_value=0)):
        resp = client.get(SUMMARY_URL, params={"clinic_id": CLINIC_ID})
    assert "diagnosis" not in resp.json()["summary"]
