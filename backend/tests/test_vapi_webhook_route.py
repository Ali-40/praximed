"""
Integration tests for POST /webhooks/vapi/call-event — PraxisMed Sprint 1 / Module 14

Strategy
--------
• Synchronous TestClient; no real event loop needed in test code.
• ``get_db_pool`` is overridden via ``app.dependency_overrides``.
• ``process_vapi_call_event`` is patched at its import site in the route module.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.dependencies.machine_auth import get_machine_auth_context
from backend.app.api.deps import get_db_pool
from backend.app.core.machine_auth import MachineAuthContext

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

URL = "/webhooks/vapi/call-event"

CLINIC_ID = "11111111-1111-4111-8111-111111111111"
CALL_ID   = "vapi-call-abc123"

VALID_PAYLOAD = {
    "clinic_id":  CLINIC_ID,
    "event_type": "call.started",
    "call_id":    CALL_ID,
}

SUCCESS_RESULT = {
    "ok":         True,
    "clinic_id":  CLINIC_ID,
    "event_type": "call.started",
    "call_id":    CALL_ID,
    "message":    "Event 'call.started' processed successfully.",
}

OTHER_CLINIC_ID = "99999999-9999-4999-8999-999999999999"

FAKE_POOL = object()


def _machine_auth() -> MachineAuthContext:
    return MachineAuthContext(
        service_name="vapi", clinic_id=CLINIC_ID, scopes={"vapi:webhook"}
    )


SECRET_ENV   = "PRAXIMED_VAPI_WEBHOOK_SECRET"
SECRET_VALUE = "vapi-super-secret-999"
SECRET_HEADER = "X-PraxisMed-Vapi-Secret"

PROCESS_EVENT = "backend.app.api.routes.vapi_webhooks.process_vapi_call_event"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client_with_pool():
    app.dependency_overrides[get_db_pool]              = lambda: FAKE_POOL
    app.dependency_overrides[get_machine_auth_context] = _machine_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,              None)
    app.dependency_overrides.pop(get_machine_auth_context, None)


@pytest.fixture()
def client_no_pool():
    app.dependency_overrides.pop(get_db_pool, None)
    try:
        del app.state.db_pool
    except (AttributeError, KeyError):
        pass
    app.dependency_overrides[get_machine_auth_context] = _machine_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,              None)
    app.dependency_overrides.pop(get_machine_auth_context, None)


@pytest.fixture()
def client_no_auth():
    """TestClient with pool override — no machine auth override."""
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides.pop(get_machine_auth_context, None)
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)


# ---------------------------------------------------------------------------
# 1. Valid payload with no env secret → 200
# ---------------------------------------------------------------------------

def test_valid_payload_no_secret_returns_200(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["ok"] is True


# ---------------------------------------------------------------------------
# 2. Route calls process_vapi_call_event
# ---------------------------------------------------------------------------

def test_route_calls_process_vapi_call_event(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    mock_handler = AsyncMock(return_value=SUCCESS_RESULT)
    with patch(PROCESS_EVENT, new=mock_handler):
        client_with_pool.post(URL, json=VALID_PAYLOAD)
    mock_handler.assert_awaited_once()


# ---------------------------------------------------------------------------
# 3. Route passes app DB pool to handler
# ---------------------------------------------------------------------------

def test_route_passes_pool_to_handler(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    captured: list = []

    async def capture(pool, payload):
        captured.append(pool)
        return SUCCESS_RESULT

    with patch(PROCESS_EVENT, new=capture):
        client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert len(captured) == 1
    assert captured[0] is FAKE_POOL


# ---------------------------------------------------------------------------
# 4. Correct secret succeeds when env var is set
# ---------------------------------------------------------------------------

def test_correct_secret_returns_200(client_with_pool, monkeypatch):
    monkeypatch.setenv(SECRET_ENV, SECRET_VALUE)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(
            URL,
            json=VALID_PAYLOAD,
            headers={SECRET_HEADER: SECRET_VALUE},
        )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 5. Missing secret returns 401 when env var is set
# ---------------------------------------------------------------------------

def test_missing_secret_returns_401(client_with_pool, monkeypatch):
    monkeypatch.setenv(SECRET_ENV, SECRET_VALUE)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 6. Wrong secret returns 401 when env var is set
# ---------------------------------------------------------------------------

def test_wrong_secret_returns_401(client_with_pool, monkeypatch):
    monkeypatch.setenv(SECRET_ENV, SECRET_VALUE)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(
            URL,
            json=VALID_PAYLOAD,
            headers={SECRET_HEADER: "not-the-right-secret"},
        )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 7. Missing db_pool → 503
# ---------------------------------------------------------------------------

def test_missing_pool_returns_503(client_no_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 503


# ---------------------------------------------------------------------------
# 8. InvalidVapiEventPayloadError → 400
# ---------------------------------------------------------------------------

def test_invalid_payload_returns_400(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    from backend.app.modules.vapi.vapi_event_handler import InvalidVapiEventPayloadError
    with patch(
        PROCESS_EVENT,
        new=AsyncMock(side_effect=InvalidVapiEventPayloadError("missing clinic_id")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# 9. UnsupportedVapiEventTypeError → 400
# ---------------------------------------------------------------------------

def test_unsupported_event_type_returns_400(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    from backend.app.modules.vapi.vapi_event_handler import UnsupportedVapiEventTypeError
    with patch(
        PROCESS_EVENT,
        new=AsyncMock(side_effect=UnsupportedVapiEventTypeError("unknown.event")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# 10. Unexpected handler error → 500
# ---------------------------------------------------------------------------

def test_unexpected_error_returns_500(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    with patch(
        PROCESS_EVENT,
        new=AsyncMock(side_effect=RuntimeError("something exploded")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 500
    assert "Internal error" in response.json()["detail"]


# ===========================================================================
# Module 40 — Machine auth guard tests
# ===========================================================================


# ---------------------------------------------------------------------------
# 11. Missing X-Service-Name header → 401
# ---------------------------------------------------------------------------

def test_missing_machine_auth_headers_returns_401(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    response = client_no_auth.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 12. Invalid service name → 401
# ---------------------------------------------------------------------------

def test_invalid_service_name_returns_401(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    response = client_no_auth.post(
        URL,
        json=VALID_PAYLOAD,
        headers={
            "X-Service-Name": "rogue-bot",
            "X-Service-Clinic-Id": CLINIC_ID,
            "X-Service-Scopes": "vapi:webhook",
        },
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 13. Wrong clinic → 403
# ---------------------------------------------------------------------------

def test_wrong_clinic_returns_403(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_auth.post(
            URL,
            json=VALID_PAYLOAD,
            headers={
                "X-Service-Name": "vapi",
                "X-Service-Clinic-Id": OTHER_CLINIC_ID,
                "X-Service-Scopes": "vapi:webhook",
            },
        )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 14. Missing required scope → 403
# ---------------------------------------------------------------------------

def test_missing_scope_returns_403(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_auth.post(
            URL,
            json=VALID_PAYLOAD,
            headers={
                "X-Service-Name": "vapi",
                "X-Service-Clinic-Id": CLINIC_ID,
                "X-Service-Scopes": "availability:read",
            },
        )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 15. Valid machine auth → 200
# ---------------------------------------------------------------------------

def test_valid_machine_auth_returns_200(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_auth.post(
            URL,
            json=VALID_PAYLOAD,
            headers={
                "X-Service-Name": "vapi",
                "X-Service-Clinic-Id": CLINIC_ID,
                "X-Service-Scopes": "vapi:webhook",
            },
        )
    assert response.status_code == 200
