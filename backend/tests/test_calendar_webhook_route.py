"""
Tests for POST /webhooks/n8n/calendar-sync — PraxisMed Sprint 1 / Module 8

Strategy
--------
• All tests use FastAPI's synchronous TestClient.
• ``get_db_pool`` is overridden via ``app.dependency_overrides`` so no real
  asyncpg pool is ever created.
• ``process_calendar_sync_payload`` is patched at the route's import site so
  no real repository calls are made.
• Module 47: ``verify_n8n_webhook_signature_dependency`` is overridden in most
  fixtures so non-sig tests remain focused on their own concern.  A dedicated
  ``client_sig_tests`` fixture lets the real HMAC dep run for sig-specific tests.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.dependencies.machine_auth import get_machine_auth_context
from backend.app.api.dependencies.webhook_signature import (
    verify_n8n_webhook_signature_dependency,
)
from backend.app.api.deps import get_db_pool
from backend.app.core.machine_auth import MachineAuthContext
from backend.app.core.webhook_signature import compute_hmac_sha256_signature

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

URL = "/webhooks/n8n/calendar-sync"

CLINIC_ID       = "11111111-1111-4111-8111-111111111111"
OTHER_CLINIC_ID = "99999999-9999-4999-8999-999999999999"

VALID_PAYLOAD = {
    "clinic_id":             CLINIC_ID,
    "provider":              "google",
    "external_calendar_id":  "cal@group.calendar.google.com",
    "event_type":            "connection_upsert",
}

SUCCESS_RESULT = {
    "ok":         True,
    "event_type": "connection_upsert",
    "clinic_id":  CLINIC_ID,
    "action":     "connection_upserted",
    "message":    "ok",
}

FAKE_POOL = object()

# Module 47 — webhook signature constants
N8N_SIG_ENV    = "N8N_WEBHOOK_SECRET"
N8N_SIG_SECRET = "test-n8n-secret"
N8N_SIG_HEADER = "X-N8N-Signature"

# Pre-serialised payload bytes for deterministic HMAC computation
_VALID_PAYLOAD_BYTES = json.dumps(VALID_PAYLOAD).encode()

SYNC_SERVICE = (
    "backend.app.api.routes.calendar_webhooks.process_calendar_sync_payload"
)
AUDIT_SAFE = "backend.app.modules.audit.audit_logger.safe_record_audit_event"


def _machine_auth() -> MachineAuthContext:
    return MachineAuthContext(
        service_name="n8n", clinic_id=CLINIC_ID, scopes={"calendar:sync"}
    )


def _n8n_sig(payload_bytes: bytes = _VALID_PAYLOAD_BYTES) -> str:
    return compute_hmac_sha256_signature(payload_bytes, N8N_SIG_SECRET)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client_with_pool():
    """Pool + machine auth + sig dep all overridden — tests focus on route behaviour."""
    app.dependency_overrides[get_db_pool]                              = lambda: FAKE_POOL
    app.dependency_overrides[get_machine_auth_context]                 = _machine_auth
    app.dependency_overrides[verify_n8n_webhook_signature_dependency]  = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,                             None)
    app.dependency_overrides.pop(get_machine_auth_context,                None)
    app.dependency_overrides.pop(verify_n8n_webhook_signature_dependency, None)


@pytest.fixture()
def client_no_pool():
    """Machine auth + sig dep overridden — no pool — for 503 pool tests."""
    app.dependency_overrides.pop(get_db_pool, None)
    try:
        del app.state.db_pool
    except (AttributeError, KeyError):
        pass
    app.dependency_overrides[get_machine_auth_context]                = _machine_auth
    app.dependency_overrides[verify_n8n_webhook_signature_dependency] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,                             None)
    app.dependency_overrides.pop(get_machine_auth_context,                None)
    app.dependency_overrides.pop(verify_n8n_webhook_signature_dependency, None)


@pytest.fixture()
def client_no_auth():
    """Pool + sig dep overridden — no machine auth override — for machine auth tests."""
    app.dependency_overrides[get_db_pool]                             = lambda: FAKE_POOL
    app.dependency_overrides.pop(get_machine_auth_context, None)
    app.dependency_overrides[verify_n8n_webhook_signature_dependency] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,                             None)
    app.dependency_overrides.pop(verify_n8n_webhook_signature_dependency, None)


@pytest.fixture()
def client_sig_tests():
    """Pool + machine auth overridden — real HMAC sig dep runs — for sig-specific tests."""
    app.dependency_overrides[get_db_pool]              = lambda: FAKE_POOL
    app.dependency_overrides[get_machine_auth_context] = _machine_auth
    app.dependency_overrides.pop(verify_n8n_webhook_signature_dependency, None)
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,              None)
    app.dependency_overrides.pop(get_machine_auth_context, None)


# ===========================================================================
# Route behaviour tests (1–3)
# ===========================================================================


def test_valid_payload_returns_200(client_with_pool):
    """Test 1 — Valid payload returns 200 and ok=True."""
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_route_calls_process_calendar_sync_payload(client_with_pool):
    """Test 2 — Route delegates to process_calendar_sync_payload."""
    mock_service = AsyncMock(return_value=SUCCESS_RESULT)
    with patch(SYNC_SERVICE, new=mock_service):
        client_with_pool.post(URL, json=VALID_PAYLOAD)
    mock_service.assert_awaited_once()


def test_route_passes_pool_to_service(client_with_pool):
    """Test 3 — Route passes the app DB pool to the service."""
    captured: list[Any] = []

    async def capture_args(pool, payload):
        captured.append(pool)
        return SUCCESS_RESULT

    with patch(SYNC_SERVICE, new=capture_args):
        client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert len(captured) == 1
    assert captured[0] is FAKE_POOL


# ===========================================================================
# Pool / handler error tests (4–8)
# ===========================================================================


def test_no_db_pool_returns_503(client_no_pool):
    """Test 4 — Missing DB pool returns 503."""
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 503


def test_invalid_payload_error_returns_400(client_with_pool):
    """Test 5 — InvalidCalendarPayloadError → 400."""
    from backend.app.modules.calendar_sync.calendar_sync import InvalidCalendarPayloadError
    with patch(
        SYNC_SERVICE,
        new=AsyncMock(side_effect=InvalidCalendarPayloadError("missing clinic_id")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 400
    assert "clinic_id" in response.json()["detail"]


def test_unsupported_event_type_returns_400(client_with_pool):
    """Test 6 — UnsupportedCalendarEventTypeError → 400."""
    from backend.app.modules.calendar_sync.calendar_sync import UnsupportedCalendarEventTypeError
    with patch(
        SYNC_SERVICE,
        new=AsyncMock(side_effect=UnsupportedCalendarEventTypeError("bad_type")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 400


def test_unexpected_exception_returns_500(client_with_pool):
    """Test 7 — Unhandled exception in service → 500."""
    with patch(
        SYNC_SERVICE,
        new=AsyncMock(side_effect=RuntimeError("something exploded")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 500
    assert "Internal error" in response.json()["detail"]


def test_no_real_db_connection_needed(client_with_pool):
    """Test 8 — Sanity: FAKE_POOL sentinel is sufficient to pass the route."""
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 200


# ===========================================================================
# Machine auth guard tests (9–13)
# ===========================================================================


def test_missing_machine_auth_headers_returns_401(client_no_auth):
    """Test 9 — Missing X-Service-Name → 401."""
    response = client_no_auth.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_invalid_service_name_returns_401(client_no_auth):
    """Test 10 — Unknown service name → 401."""
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


def test_wrong_clinic_returns_403(client_no_auth):
    """Test 11 — Correct service, wrong clinic → 403."""
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


def test_missing_scope_returns_403(client_no_auth):
    """Test 12 — Missing required scope → 403."""
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


def test_valid_machine_auth_returns_200(client_no_auth):
    """Test 13 — Valid machine auth (sig overridden) → 200."""
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


# ===========================================================================
# Audit logging tests (14–18)
# ===========================================================================


def test_calendar_sync_records_audit_event(client_with_pool):
    """Test 14 — Successful route records an audit event."""
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "n8n.calendar_sync"
    assert event["resource_type"] == "calendar_sync"


def test_calendar_sync_audit_actor_type_is_machine(client_with_pool):
    """Test 15 — Audit actor_type is 'machine'."""
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["actor_type"] == "machine"


def test_calendar_sync_audit_metadata_includes_event_type(client_with_pool):
    """Test 16 — Audit metadata contains event_type from the payload."""
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["metadata"]["event_type"] == "connection_upsert"


def test_calendar_sync_audit_clinic_id_from_payload(client_with_pool):
    """Test 17 — Audit clinic_id matches the payload clinic_id."""
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["clinic_id"] == CLINIC_ID


def test_calendar_sync_audit_failure_does_not_break_route(client_with_pool):
    """Test 18 — Audit failure does not affect the 200 response."""
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": False, "audit_log": None, "message": "failed", "error": "db"})):
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200


# ===========================================================================
# Module 47 — Webhook signature enforcement tests (19–24)
# ===========================================================================


def test_valid_machine_auth_and_valid_sig_returns_200(client_sig_tests, monkeypatch):
    """M47-1 — Valid HMAC signature + valid machine auth → 200."""
    monkeypatch.setenv(N8N_SIG_ENV, N8N_SIG_SECRET)
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(
            URL,
            content=_VALID_PAYLOAD_BYTES,
            headers={
                "Content-Type": "application/json",
                N8N_SIG_HEADER: _n8n_sig(),
            },
        )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_missing_n8n_sig_header_returns_401(client_sig_tests, monkeypatch):
    """M47-2 — Missing X-N8N-Signature header → 401."""
    monkeypatch.setenv(N8N_SIG_ENV, N8N_SIG_SECRET)
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_invalid_n8n_sig_returns_401(client_sig_tests, monkeypatch):
    """M47-3 — Wrong HMAC digest value → 401."""
    monkeypatch.setenv(N8N_SIG_ENV, N8N_SIG_SECRET)
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(
            URL,
            content=_VALID_PAYLOAD_BYTES,
            headers={
                "Content-Type": "application/json",
                N8N_SIG_HEADER: "sha256=deadbeefdeadbeef",
            },
        )
    assert response.status_code == 401


def test_missing_n8n_secret_env_returns_503(client_sig_tests, monkeypatch):
    """M47-4 — N8N_WEBHOOK_SECRET not set → 503."""
    monkeypatch.delenv(N8N_SIG_ENV, raising=False)
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(
            URL,
            content=_VALID_PAYLOAD_BYTES,
            headers={
                "Content-Type": "application/json",
                N8N_SIG_HEADER: "sha256=anysig",
            },
        )
    assert response.status_code == 503


def test_n8n_sig_uses_raw_request_body(client_sig_tests, monkeypatch):
    """M47-8 — Signature computed over different bytes → 401 (raw body check)."""
    monkeypatch.setenv(N8N_SIG_ENV, N8N_SIG_SECRET)
    tampered_body = json.dumps({**VALID_PAYLOAD, "extra": "tampered"}).encode()
    sig_over_original = _n8n_sig(_VALID_PAYLOAD_BYTES)
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(
            URL,
            content=tampered_body,
            headers={
                "Content-Type": "application/json",
                N8N_SIG_HEADER: sig_over_original,
            },
        )
    assert response.status_code == 401


def test_audit_records_after_valid_sig_and_processing(client_sig_tests, monkeypatch):
    """M47-7 — Audit event recorded after valid sig + successful processing."""
    monkeypatch.setenv(N8N_SIG_ENV, N8N_SIG_SECRET)
    with patch(SYNC_SERVICE, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        response = client_sig_tests.post(
            URL,
            content=_VALID_PAYLOAD_BYTES,
            headers={
                "Content-Type": "application/json",
                N8N_SIG_HEADER: _n8n_sig(),
            },
        )
    assert response.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "n8n.calendar_sync"
    assert event["actor_type"] == "machine"
