"""
Tests for POST /webhooks/n8n/calendar-sync — PraxisMed Sprint 1 / Module 8

Strategy
--------
• All tests use FastAPI's synchronous TestClient.
• ``get_db_pool`` is overridden via ``app.dependency_overrides`` so no real
  asyncpg pool is ever created.
• ``process_calendar_sync_payload`` is patched at the route's import site so
  no real repository calls are made.
• Each test fixture tears down overrides after itself to keep tests isolated.
"""

from __future__ import annotations

import os
from typing import Any
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

URL = "/webhooks/n8n/calendar-sync"

SECRET_ENV   = "PRAXIMED_N8N_WEBHOOK_SECRET"
SECRET_VALUE = "super-secret-token-123"
SECRET_HEADER = "X-PraxisMed-Webhook-Secret"

# Minimal valid payload accepted by process_calendar_sync_payload
VALID_PAYLOAD = {
    "clinic_id":             "11111111-1111-4111-8111-111111111111",
    "provider":              "google",
    "external_calendar_id":  "cal@group.calendar.google.com",
    "event_type":            "connection_upsert",
}

CLINIC_ID = "11111111-1111-4111-8111-111111111111"
OTHER_CLINIC_ID = "99999999-9999-4999-8999-999999999999"

FAKE_POOL = object()   # sentinel — identity tested in test 3


def _machine_auth() -> MachineAuthContext:
    return MachineAuthContext(
        service_name="n8n", clinic_id=CLINIC_ID, scopes={"calendar:sync"}
    )


SYNC_SERVICE = (
    "backend.app.api.routes.calendar_webhooks.process_calendar_sync_payload"
)

SUCCESS_RESULT = {
    "ok":         True,
    "event_type": "connection_upsert",
    "clinic_id":  "11111111-1111-4111-8111-111111111111",
    "action":     "connection_upserted",
    "message":    "ok",
}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client_with_pool():
    """TestClient with pool and machine auth overrides."""
    app.dependency_overrides[get_db_pool]              = lambda: FAKE_POOL
    app.dependency_overrides[get_machine_auth_context] = _machine_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,              None)
    app.dependency_overrides.pop(get_machine_auth_context, None)


@pytest.fixture()
def client_no_pool():
    """TestClient with machine auth override — no pool."""
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


def test_valid_payload_returns_200_when_no_secret_set(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)

    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["ok"] is True


# ---------------------------------------------------------------------------
# 2. Route calls process_calendar_sync_payload
# ---------------------------------------------------------------------------


def test_route_calls_process_calendar_sync_payload(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)

    mock_service = AsyncMock(return_value=SUCCESS_RESULT)
    with patch(SYNC_SERVICE, new=mock_service):
        client_with_pool.post(URL, json=VALID_PAYLOAD)

    mock_service.assert_awaited_once()


# ---------------------------------------------------------------------------
# 3. Route passes the app DB pool to the service
# ---------------------------------------------------------------------------


def test_route_passes_pool_to_service(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)

    captured: list[Any] = []

    async def capture_args(pool, payload):
        captured.append(pool)
        return SUCCESS_RESULT

    with patch(SYNC_SERVICE, new=capture_args):
        client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert len(captured) == 1
    assert captured[0] is FAKE_POOL


# ---------------------------------------------------------------------------
# 4. Correct secret header → 200
# ---------------------------------------------------------------------------


def test_correct_secret_header_returns_200(client_with_pool, monkeypatch):
    monkeypatch.setenv(SECRET_ENV, SECRET_VALUE)

    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(
            URL,
            json=VALID_PAYLOAD,
            headers={SECRET_HEADER: SECRET_VALUE},
        )

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 5. Missing secret header → 401
# ---------------------------------------------------------------------------


def test_missing_secret_header_returns_401(client_with_pool, monkeypatch):
    monkeypatch.setenv(SECRET_ENV, SECRET_VALUE)

    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 6. Wrong secret header → 401
# ---------------------------------------------------------------------------


def test_wrong_secret_header_returns_401(client_with_pool, monkeypatch):
    monkeypatch.setenv(SECRET_ENV, SECRET_VALUE)

    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(
            URL,
            json=VALID_PAYLOAD,
            headers={SECRET_HEADER: "wrong-secret"},
        )

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 7. No DB pool on app.state → 503
# ---------------------------------------------------------------------------


def test_no_db_pool_returns_503(client_no_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)

    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_pool.post(URL, json=VALID_PAYLOAD)

    assert response.status_code == 503


# ---------------------------------------------------------------------------
# 8. InvalidCalendarPayloadError → 400
# ---------------------------------------------------------------------------


def test_invalid_payload_error_returns_400(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)

    from backend.app.modules.calendar_sync.calendar_sync import InvalidCalendarPayloadError

    with patch(
        SYNC_SERVICE,
        new=AsyncMock(side_effect=InvalidCalendarPayloadError("missing clinic_id")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert response.status_code == 400
    assert "clinic_id" in response.json()["detail"]


def test_unsupported_event_type_returns_400(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)

    from backend.app.modules.calendar_sync.calendar_sync import UnsupportedCalendarEventTypeError

    with patch(
        SYNC_SERVICE,
        new=AsyncMock(side_effect=UnsupportedCalendarEventTypeError("bad_type")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# 9. Unexpected exception → 500
# ---------------------------------------------------------------------------


def test_unexpected_exception_returns_500(client_with_pool, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)

    with patch(
        SYNC_SERVICE,
        new=AsyncMock(side_effect=RuntimeError("something exploded")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert response.status_code == 500
    assert "Internal error" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 11. No real DB connection used anywhere in the test suite
# ---------------------------------------------------------------------------


def test_no_real_db_connection_needed(client_with_pool, monkeypatch):
    """Sanity check: pool=FAKE_POOL (a plain object) is enough to pass."""
    monkeypatch.delenv(SECRET_ENV, raising=False)

    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert response.status_code == 200


# ===========================================================================
# Module 40 — Machine auth guard tests
# ===========================================================================


# ---------------------------------------------------------------------------
# 12. Missing X-Service-Name header → 401
# ---------------------------------------------------------------------------

def test_missing_machine_auth_headers_returns_401(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    response = client_no_auth.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 13. Invalid service name → 401
# ---------------------------------------------------------------------------

def test_invalid_service_name_returns_401(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    response = client_no_auth.post(
        URL,
        json=VALID_PAYLOAD,
        headers={
            "X-Service-Name": "rogue-bot",
            "X-Service-Clinic-Id": CLINIC_ID,
            "X-Service-Scopes": "calendar:sync",
        },
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 14. Wrong clinic → 403
# ---------------------------------------------------------------------------

def test_wrong_clinic_returns_403(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_auth.post(
            URL,
            json=VALID_PAYLOAD,
            headers={
                "X-Service-Name": "n8n",
                "X-Service-Clinic-Id": OTHER_CLINIC_ID,
                "X-Service-Scopes": "calendar:sync",
            },
        )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 15. Missing required scope → 403
# ---------------------------------------------------------------------------

def test_missing_scope_returns_403(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_auth.post(
            URL,
            json=VALID_PAYLOAD,
            headers={
                "X-Service-Name": "n8n",
                "X-Service-Clinic-Id": CLINIC_ID,
                "X-Service-Scopes": "vapi:tool",
            },
        )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 16. Valid machine auth → 200
# ---------------------------------------------------------------------------

def test_valid_machine_auth_returns_200(client_no_auth, monkeypatch):
    monkeypatch.delenv(SECRET_ENV, raising=False)
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_auth.post(
            URL,
            json=VALID_PAYLOAD,
            headers={
                "X-Service-Name": "n8n",
                "X-Service-Clinic-Id": CLINIC_ID,
                "X-Service-Scopes": "calendar:sync",
            },
        )
    assert response.status_code == 200
