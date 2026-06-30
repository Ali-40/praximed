"""
Integration tests for appointment request routes — PraxisMed Sprint 1 / Module 17

Strategy:
- Use FastAPI TestClient; no real event loop or database.
- Override get_db_pool via app.dependency_overrides.
- Patch appointment_request_repo functions at their usage site in the route module.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import get_db_pool

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLINIC_ID  = "11111111-1111-4111-8111-111111111111"
REQUEST_ID = "22222222-2222-4222-8222-222222222222"
USER_ID    = "33333333-3333-4333-8333-333333333333"

BASE_URL     = "/appointment-requests"
GET_ONE_URL  = f"/appointment-requests/{REQUEST_ID}"
STATUS_URL   = f"/appointment-requests/{REQUEST_ID}/status"
ASSIGN_URL   = f"/appointment-requests/{REQUEST_ID}/assign"
CALLBACK_URL = f"/appointment-requests/{REQUEST_ID}/callback-needed"
ARCHIVE_URL  = f"/appointment-requests/{REQUEST_ID}/archive"

CREATE_BODY = {
    "clinic_id":    CLINIC_ID,
    "source":       "vapi",
    "patient_name": "Maria Muster",
}

FAKE_ROW = {
    "id":                  REQUEST_ID,
    "clinic_id":           CLINIC_ID,
    "source":              "vapi",
    "source_ref":          None,
    "patient_name":        "Maria Muster",
    "patient_phone":       None,
    "patient_email":       None,
    "date_of_birth":       None,
    "reason":              None,
    "preferred_starts_at": None,
    "preferred_ends_at":   None,
    "status":              "new",
    "urgency_level":       "normal",
    "action_required":     True,
    "assigned_user_id":    None,
    "raw_payload":         None,
    "created_at":          "2024-06-03T09:00:00+00:00",
    "updated_at":          "2024-06-03T09:00:00+00:00",
}

REPO = "backend.app.api.routes.appointment_requests.appointment_request_repo"

FAKE_POOL = MagicMock()

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)


@pytest.fixture()
def client_no_pool():
    app.dependency_overrides.pop(get_db_pool, None)
    try:
        del app.state.db_pool
    except (AttributeError, KeyError):
        pass
    yield TestClient(app)


# ---------------------------------------------------------------------------
# 1. POST /appointment-requests returns 200
# ---------------------------------------------------------------------------

def test_post_create_returns_200(client):
    with patch(f"{REPO}.create_appointment_request", new=AsyncMock(return_value=FAKE_ROW)):
        response = client.post(BASE_URL, json=CREATE_BODY)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["request"]["id"] == REQUEST_ID


# ---------------------------------------------------------------------------
# 2. POST route calls create_appointment_request with correct args
# ---------------------------------------------------------------------------

def test_post_create_calls_repo(client):
    mock_fn = AsyncMock(return_value=FAKE_ROW)
    with patch(f"{REPO}.create_appointment_request", new=mock_fn):
        client.post(BASE_URL, json=CREATE_BODY)
    mock_fn.assert_awaited_once()
    kw = mock_fn.call_args.kwargs
    assert kw["clinic_id"] == CLINIC_ID
    assert kw["source"] == "vapi"
    assert kw["patient_name"] == "Maria Muster"


# ---------------------------------------------------------------------------
# 3. GET /appointment-requests returns 200 with a list
# ---------------------------------------------------------------------------

def test_get_list_returns_200(client):
    with patch(f"{REPO}.list_appointment_requests", new=AsyncMock(return_value=[FAKE_ROW])):
        response = client.get(BASE_URL, params={"clinic_id": CLINIC_ID})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert isinstance(body["requests"], list)
    assert len(body["requests"]) == 1
    assert body["requests"][0]["id"] == REQUEST_ID


# ---------------------------------------------------------------------------
# 4. GET list passes status/action_required/limit filters
# ---------------------------------------------------------------------------

def test_get_list_passes_filters(client):
    mock_fn = AsyncMock(return_value=[FAKE_ROW])
    with patch(f"{REPO}.list_appointment_requests", new=mock_fn):
        client.get(BASE_URL, params={
            "clinic_id":       CLINIC_ID,
            "status":          "new",
            "action_required": True,
            "limit":           10,
        })
    mock_fn.assert_awaited_once()
    kw = mock_fn.call_args.kwargs
    assert kw["status"] == "new"
    assert kw["action_required"] is True
    assert kw["limit"] == 10


# ---------------------------------------------------------------------------
# 5. GET /appointment-requests/{id} returns 200 when found
# ---------------------------------------------------------------------------

def test_get_by_id_returns_200(client):
    with patch(f"{REPO}.get_appointment_request_by_id", new=AsyncMock(return_value=FAKE_ROW)):
        response = client.get(GET_ONE_URL, params={"clinic_id": CLINIC_ID})
    assert response.status_code == 200
    assert response.json()["request"]["id"] == REQUEST_ID


# ---------------------------------------------------------------------------
# 6. GET /appointment-requests/{id} returns 404 when repo returns None
# ---------------------------------------------------------------------------

def test_get_by_id_returns_404(client):
    with patch(f"{REPO}.get_appointment_request_by_id", new=AsyncMock(return_value=None)):
        response = client.get(GET_ONE_URL, params={"clinic_id": CLINIC_ID})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 7. PATCH status route returns 200
# ---------------------------------------------------------------------------

def test_patch_status_returns_200(client):
    with patch(f"{REPO}.update_appointment_request_status", new=AsyncMock(return_value=FAKE_ROW)):
        response = client.patch(
            STATUS_URL,
            json={"status": "confirmed"},
            params={"clinic_id": CLINIC_ID},
        )
    assert response.status_code == 200
    assert response.json()["ok"] is True


# ---------------------------------------------------------------------------
# 8. PATCH assign route returns 200
# ---------------------------------------------------------------------------

def test_patch_assign_returns_200(client):
    with patch(f"{REPO}.assign_appointment_request", new=AsyncMock(return_value=FAKE_ROW)):
        response = client.patch(
            ASSIGN_URL,
            json={"assigned_user_id": USER_ID},
            params={"clinic_id": CLINIC_ID},
        )
    assert response.status_code == 200
    assert response.json()["ok"] is True


# ---------------------------------------------------------------------------
# 9. POST callback-needed route returns 200
# ---------------------------------------------------------------------------

def test_post_callback_needed_returns_200(client):
    with patch(f"{REPO}.mark_callback_needed", new=AsyncMock(return_value=FAKE_ROW)):
        response = client.post(CALLBACK_URL, params={"clinic_id": CLINIC_ID})
    assert response.status_code == 200
    assert response.json()["ok"] is True


# ---------------------------------------------------------------------------
# 10. POST archive route returns 200
# ---------------------------------------------------------------------------

def test_post_archive_returns_200(client):
    with patch(f"{REPO}.archive_appointment_request", new=AsyncMock(return_value=FAKE_ROW)):
        response = client.post(ARCHIVE_URL, params={"clinic_id": CLINIC_ID})
    assert response.status_code == 200
    assert response.json()["ok"] is True


# ---------------------------------------------------------------------------
# 11. Missing db_pool returns 503
# ---------------------------------------------------------------------------

def test_missing_pool_returns_503(client_no_pool):
    response = client_no_pool.post(BASE_URL, json=CREATE_BODY)
    assert response.status_code == 503


# ---------------------------------------------------------------------------
# 12. Invalid request body returns 422
# ---------------------------------------------------------------------------

def test_invalid_body_returns_422(client):
    response = client.post(BASE_URL, json={
        "clinic_id":    CLINIC_ID,
        "source":       "invalid_source",
        "patient_name": "Maria Muster",
    })
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 13. Repository validation error maps to 400
# ---------------------------------------------------------------------------

def test_repo_validation_error_returns_400(client):
    from backend.app.db.repositories.appointment_request_repo import InvalidAppointmentRequestError
    with patch(
        f"{REPO}.create_appointment_request",
        new=AsyncMock(side_effect=InvalidAppointmentRequestError("bad input")),
    ):
        response = client.post(BASE_URL, json=CREATE_BODY)
    assert response.status_code == 400
    assert "bad input" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 14. Unexpected repository error maps to 500
# ---------------------------------------------------------------------------

def test_unexpected_error_returns_500(client):
    with patch(
        f"{REPO}.create_appointment_request",
        new=AsyncMock(side_effect=RuntimeError("db exploded")),
    ):
        response = client.post(BASE_URL, json=CREATE_BODY)
    assert response.status_code == 500
    assert "Internal error" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 15. Existing health route still works
# ---------------------------------------------------------------------------

def test_health_route_still_works(client):
    response = client.get("/health")
    assert response.status_code == 200
