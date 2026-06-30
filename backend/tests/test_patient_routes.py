"""
Integration tests for patient routes — PraxisMed Sprint 2 / Module 26
Updated: Sprint 3 / Module 37 — auth fixture overrides and tenant guard tests added.

Strategy:
- Use FastAPI TestClient; no real event loop or database.
- Override get_db_pool and get_auth_context via app.dependency_overrides.
- Patch patient_repo functions at their usage site in the route module.
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
PATIENT_ID      = "22222222-2222-4222-8222-222222222222"
EXT_ID          = "EXT-001"

BASE_URL      = "/patients"
UPSERT_URL    = "/patients/upsert-by-external-id"
GET_ONE_URL   = f"/patients/{PATIENT_ID}"
BY_EXT_URL    = f"/patients/by-external-id/{EXT_ID}"
PATCH_URL     = f"/patients/{PATIENT_ID}"
ARCHIVE_URL   = f"/patients/{PATIENT_ID}/archive"

CREATE_BODY = {
    "clinic_id": CLINIC_ID,
    "full_name": "Ada Lovelace",
}

UPSERT_BODY = {
    "clinic_id":            CLINIC_ID,
    "external_patient_id":  EXT_ID,
    "full_name":            "Ada Lovelace",
}

FAKE_ROW = {
    "id":                  PATIENT_ID,
    "clinic_id":           CLINIC_ID,
    "external_patient_id": None,
    "full_name":           "Ada Lovelace",
    "date_of_birth":       None,
    "phone":               None,
    "email":               None,
    "preferred_language":  "de-AT",
    "status":              "active",
    "notes":               None,
    "raw_payload":         None,
    "created_at":          "2024-06-03T09:00:00+00:00",
    "updated_at":          "2024-06-03T09:00:00+00:00",
}

REPO = "backend.app.api.routes.patients.patient_repo"

FAKE_POOL = MagicMock()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _staff_auth() -> AuthContext:
    return AuthContext(user_id="user-1", clinic_id=CLINIC_ID, role="staff")


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
# 1. POST /patients returns 200
# ---------------------------------------------------------------------------


def test_create_patient_returns_200(client):
    with patch(f"{REPO}.create_patient", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 2. POST route calls create_patient
# ---------------------------------------------------------------------------


def test_create_patient_calls_repo(client):
    with patch(f"{REPO}.create_patient", new=AsyncMock(return_value=FAKE_ROW)) as mock:
        client.post(BASE_URL, json=CREATE_BODY)
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 3. POST /patients/upsert-by-external-id returns 200
# ---------------------------------------------------------------------------


def test_upsert_patient_returns_200(client):
    with patch(
        f"{REPO}.upsert_patient_by_external_id", new=AsyncMock(return_value=FAKE_ROW)
    ):
        resp = client.post(UPSERT_URL, json=UPSERT_BODY)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 4. Upsert route calls upsert_patient_by_external_id
# ---------------------------------------------------------------------------


def test_upsert_patient_calls_repo(client):
    with patch(
        f"{REPO}.upsert_patient_by_external_id", new=AsyncMock(return_value=FAKE_ROW)
    ) as mock:
        client.post(UPSERT_URL, json=UPSERT_BODY)
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# 5. GET /patients returns 200 list
# ---------------------------------------------------------------------------


def test_list_patients_returns_200(client):
    with patch(f"{REPO}.list_patients", new=AsyncMock(return_value=[FAKE_ROW])):
        resp = client.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert len(data["patients"]) == 1


# ---------------------------------------------------------------------------
# 6. GET list passes status/search/limit filters
# ---------------------------------------------------------------------------


def test_list_patients_passes_filters(client):
    with patch(f"{REPO}.list_patients", new=AsyncMock(return_value=[])) as mock:
        client.get(BASE_URL, params={
            "clinic_id": CLINIC_ID,
            "status":    "active",
            "search":    "Ada",
            "limit":     "10",
        })
    kwargs = mock.call_args.kwargs
    assert kwargs["status"] == "active"
    assert kwargs["search"] == "Ada"
    assert kwargs["limit"] == 10


# ---------------------------------------------------------------------------
# 7. GET /patients/{patient_id} returns 200 when found
# ---------------------------------------------------------------------------


def test_get_patient_by_id_returns_200(client):
    with patch(f"{REPO}.get_patient_by_id", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client.get(GET_ONE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["patient"]["id"] == PATIENT_ID


# ---------------------------------------------------------------------------
# 8. GET /patients/{patient_id} returns 404 when repo returns None
# ---------------------------------------------------------------------------


def test_get_patient_by_id_returns_404(client):
    with patch(f"{REPO}.get_patient_by_id", new=AsyncMock(return_value=None)):
        resp = client.get(GET_ONE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 9. GET /patients/by-external-id/{external_patient_id} returns 200 when found
# ---------------------------------------------------------------------------


def test_get_patient_by_external_id_returns_200(client):
    with patch(
        f"{REPO}.get_patient_by_external_id",
        new=AsyncMock(return_value={**FAKE_ROW, "external_patient_id": EXT_ID}),
    ):
        resp = client.get(BY_EXT_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["patient"]["external_patient_id"] == EXT_ID


# ---------------------------------------------------------------------------
# 10. GET /patients/by-external-id/{external_patient_id} returns 404 when not found
# ---------------------------------------------------------------------------


def test_get_patient_by_external_id_returns_404(client):
    with patch(
        f"{REPO}.get_patient_by_external_id", new=AsyncMock(return_value=None)
    ):
        resp = client.get(BY_EXT_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 11. PATCH /patients/{patient_id} returns 200
# ---------------------------------------------------------------------------


def test_update_patient_returns_200(client):
    updated = {**FAKE_ROW, "full_name": "Ada B. Lovelace"}
    with patch(f"{REPO}.update_patient", new=AsyncMock(return_value=updated)):
        resp = client.patch(
            PATCH_URL,
            params={"clinic_id": CLINIC_ID},
            json={"full_name": "Ada B. Lovelace"},
        )
    assert resp.status_code == 200
    assert resp.json()["patient"]["full_name"] == "Ada B. Lovelace"


# ---------------------------------------------------------------------------
# 12. PATCH /patients/{patient_id} returns 404 when repo returns None
# ---------------------------------------------------------------------------


def test_update_patient_returns_404(client):
    with patch(f"{REPO}.update_patient", new=AsyncMock(return_value=None)):
        resp = client.patch(
            PATCH_URL,
            params={"clinic_id": CLINIC_ID},
            json={"full_name": "Ada B. Lovelace"},
        )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 13. POST /patients/{patient_id}/archive returns 200
# ---------------------------------------------------------------------------


def test_archive_patient_returns_200(client):
    archived = {**FAKE_ROW, "status": "archived"}
    with patch(f"{REPO}.archive_patient", new=AsyncMock(return_value=archived)):
        resp = client.post(ARCHIVE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 200
    assert resp.json()["patient"]["status"] == "archived"


# ---------------------------------------------------------------------------
# 14. POST /patients/{patient_id}/archive returns 404 when repo returns None
# ---------------------------------------------------------------------------


def test_archive_patient_returns_404(client):
    with patch(f"{REPO}.archive_patient", new=AsyncMock(return_value=None)):
        resp = client.post(ARCHIVE_URL, params={"clinic_id": CLINIC_ID})
    assert resp.status_code == 404


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
    resp = client.post(BASE_URL, json={"clinic_id": CLINIC_ID})  # missing full_name
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 17. Repository validation error maps to HTTP 400
# ---------------------------------------------------------------------------


def test_repo_validation_error_returns_400(client):
    from backend.app.db.repositories.patient_repo import InvalidPatientError
    with patch(
        f"{REPO}.create_patient",
        new=AsyncMock(side_effect=InvalidPatientError("bad status")),
    ):
        resp = client.post(BASE_URL, json=CREATE_BODY)
    assert resp.status_code == 400
    assert "bad status" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 18. Unexpected repository error maps to HTTP 500
# ---------------------------------------------------------------------------


def test_unexpected_repo_error_returns_500(client):
    with patch(
        f"{REPO}.create_patient",
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
# Auth enforcement tests (Module 37)
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
        headers={"X-User-Id": "user-1", "X-User-Role": "staff"},
    )
    assert resp.status_code == 401


def test_wrong_clinic_returns_403(client_no_auth):
    with patch(f"{REPO}.list_patients", new=AsyncMock(return_value=[])):
        resp = client_no_auth.get(
            BASE_URL,
            params={"clinic_id": CLINIC_ID},
            headers={
                "X-User-Id": "user-1",
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


def test_doctor_role_allowed_for_patient_routes(client_no_auth):
    with patch(f"{REPO}.list_patients", new=AsyncMock(return_value=[])):
        resp = client_no_auth.get(
            BASE_URL,
            params={"clinic_id": CLINIC_ID},
            headers={
                "X-User-Id": "doc-1",
                "X-Clinic-Id": CLINIC_ID,
                "X-User-Role": "doctor",
            },
        )
    assert resp.status_code == 200
