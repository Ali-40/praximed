"""
Integration tests for POST /webhooks/vapi/call-event — PraxisMed Sprint 1 / Module 14

Strategy
--------
• Synchronous TestClient; no real event loop needed in test code.
• ``get_db_pool`` is overridden via ``app.dependency_overrides``.
• ``process_vapi_call_event`` is patched at its import site in the route module.
• Module 47: ``verify_vapi_webhook_signature_dependency`` is overridden in most
  fixtures so non-sig tests remain focused on their own concern.  A dedicated
  ``client_sig_tests`` fixture lets the real HMAC dep run for sig-specific tests.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.dependencies.machine_auth import get_machine_auth_context
from backend.app.api.dependencies.webhook_signature import (
    verify_vapi_webhook_signature_dependency,
)
from backend.app.api.deps import get_db_pool
from backend.app.core.machine_auth import MachineAuthContext
from backend.app.core.webhook_signature import compute_hmac_sha256_signature

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

# Module 47 — webhook signature constants
VAPI_SIG_ENV    = "VAPI_WEBHOOK_SECRET"
VAPI_SIG_SECRET = "test-vapi-secret"
VAPI_SIG_HEADER = "X-Vapi-Signature"

# Pre-serialised payload bytes for deterministic HMAC computation
_VALID_PAYLOAD_BYTES = json.dumps(VALID_PAYLOAD).encode()

PROCESS_EVENT = "backend.app.api.routes.vapi_webhooks.process_vapi_call_event"
AUDIT_SAFE    = "backend.app.modules.audit.audit_logger.safe_record_audit_event"


def _machine_auth() -> MachineAuthContext:
    return MachineAuthContext(
        service_name="vapi", clinic_id=CLINIC_ID, scopes={"vapi:webhook"}
    )


def _vapi_sig(payload_bytes: bytes = _VALID_PAYLOAD_BYTES) -> str:
    return compute_hmac_sha256_signature(payload_bytes, VAPI_SIG_SECRET)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client_with_pool():
    """Pool + machine auth + sig dep all overridden — tests focus on route behaviour."""
    app.dependency_overrides[get_db_pool]                                = lambda: FAKE_POOL
    app.dependency_overrides[get_machine_auth_context]                   = _machine_auth
    app.dependency_overrides[verify_vapi_webhook_signature_dependency]   = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,                              None)
    app.dependency_overrides.pop(get_machine_auth_context,                 None)
    app.dependency_overrides.pop(verify_vapi_webhook_signature_dependency, None)


@pytest.fixture()
def client_no_pool():
    """Machine auth + sig dep overridden — no pool — for 503 pool tests."""
    app.dependency_overrides.pop(get_db_pool, None)
    try:
        del app.state.db_pool
    except (AttributeError, KeyError):
        pass
    app.dependency_overrides[get_machine_auth_context]                 = _machine_auth
    app.dependency_overrides[verify_vapi_webhook_signature_dependency] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,                              None)
    app.dependency_overrides.pop(get_machine_auth_context,                 None)
    app.dependency_overrides.pop(verify_vapi_webhook_signature_dependency, None)


@pytest.fixture()
def client_no_auth():
    """Pool + sig dep overridden — no machine auth override — for machine auth tests."""
    app.dependency_overrides[get_db_pool]                              = lambda: FAKE_POOL
    app.dependency_overrides.pop(get_machine_auth_context, None)
    app.dependency_overrides[verify_vapi_webhook_signature_dependency] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,                              None)
    app.dependency_overrides.pop(verify_vapi_webhook_signature_dependency, None)


@pytest.fixture()
def client_sig_tests():
    """Pool + machine auth overridden — real HMAC sig dep runs — for sig-specific tests."""
    app.dependency_overrides[get_db_pool]              = lambda: FAKE_POOL
    app.dependency_overrides[get_machine_auth_context] = _machine_auth
    app.dependency_overrides.pop(verify_vapi_webhook_signature_dependency, None)
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,              None)
    app.dependency_overrides.pop(get_machine_auth_context, None)


# ===========================================================================
# Route behaviour tests (1–3)
# ===========================================================================


def test_valid_payload_returns_200(client_with_pool):
    """Test 1 — Valid payload returns 200 and ok=True."""
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_route_calls_process_vapi_call_event(client_with_pool):
    """Test 2 — Route delegates to process_vapi_call_event."""
    mock_handler = AsyncMock(return_value=SUCCESS_RESULT)
    with patch(PROCESS_EVENT, new=mock_handler):
        client_with_pool.post(URL, json=VALID_PAYLOAD)
    mock_handler.assert_awaited_once()


def test_route_passes_pool_to_handler(client_with_pool):
    """Test 3 — Route passes the app DB pool to the handler."""
    captured: list = []

    async def capture(pool, payload):
        captured.append(pool)
        return SUCCESS_RESULT

    with patch(PROCESS_EVENT, new=capture):
        client_with_pool.post(URL, json=VALID_PAYLOAD)

    assert len(captured) == 1
    assert captured[0] is FAKE_POOL


# ===========================================================================
# Pool / handler error tests (4–7)
# ===========================================================================


def test_missing_pool_returns_503(client_no_pool):
    """Test 4 — Missing DB pool returns 503."""
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_no_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 503


def test_invalid_payload_returns_400(client_with_pool):
    """Test 5 — InvalidVapiEventPayloadError → 400."""
    from backend.app.modules.vapi.vapi_event_handler import InvalidVapiEventPayloadError
    with patch(
        PROCESS_EVENT,
        new=AsyncMock(side_effect=InvalidVapiEventPayloadError("missing clinic_id")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 400


def test_unsupported_event_type_returns_400(client_with_pool):
    """Test 6 — UnsupportedVapiEventTypeError → 400."""
    from backend.app.modules.vapi.vapi_event_handler import UnsupportedVapiEventTypeError
    with patch(
        PROCESS_EVENT,
        new=AsyncMock(side_effect=UnsupportedVapiEventTypeError("unknown.event")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 400


def test_unexpected_error_returns_500(client_with_pool):
    """Test 7 — Unhandled exception in handler → 500."""
    with patch(
        PROCESS_EVENT,
        new=AsyncMock(side_effect=RuntimeError("something exploded")),
    ):
        response = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 500
    assert "Internal error" in response.json()["detail"]


# ===========================================================================
# Machine auth guard tests (8–12)
# ===========================================================================


def test_missing_machine_auth_headers_returns_401(client_no_auth):
    """Test 8 — Missing X-Service-Name → 401."""
    response = client_no_auth.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_invalid_service_name_returns_401(client_no_auth):
    """Test 9 — Unknown service name → 401."""
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


def test_wrong_clinic_returns_403(client_no_auth):
    """Test 10 — Correct service, wrong clinic → 403."""
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


def test_missing_scope_returns_403(client_no_auth):
    """Test 11 — Missing required scope → 403."""
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


def test_valid_machine_auth_returns_200(client_no_auth):
    """Test 12 — Valid machine auth (sig overridden) → 200."""
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


# ===========================================================================
# Audit logging tests (13–18)
# ===========================================================================


def test_call_event_records_audit_event(client_with_pool):
    """Test 13 — Successful route records an audit event."""
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "vapi.call_event"
    assert event["resource_type"] == "clinic_call_logs"
    assert event["actor_type"] == "machine"


def test_call_event_audit_severity_warning_when_action_required(client_with_pool):
    """Test 14 — Audit severity is 'warning' when result has action_required=True."""
    result_with_action = {**SUCCESS_RESULT, "action_required": True}
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=result_with_action)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["severity"] == "warning"


def test_call_event_audit_severity_info_when_not_action_required(client_with_pool):
    """Test 15 — Audit severity is 'info' when action_required is falsy."""
    result_no_action = {**SUCCESS_RESULT, "action_required": False}
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=result_no_action)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["severity"] == "info"


def test_call_event_audit_metadata_includes_event_type(client_with_pool):
    """Test 16 — Audit metadata contains the event_type from the payload."""
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["metadata"]["event_type"] == "call.started"


def test_call_event_audit_resource_id_from_call_id(client_with_pool):
    """Test 17 — Audit resource_id is the call_id returned by the handler."""
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["resource_id"] == CALL_ID


def test_call_event_audit_failure_does_not_break_route(client_with_pool):
    """Test 18 — Audit failure does not affect the 200 response."""
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": False, "audit_log": None, "message": "failed", "error": "db"})):
        resp = client_with_pool.post(URL, json=VALID_PAYLOAD)
    assert resp.status_code == 200


# ===========================================================================
# Module 47 — Webhook signature enforcement tests (19–24)
# ===========================================================================


def test_valid_machine_auth_and_valid_sig_returns_200(client_sig_tests, monkeypatch):
    """M47-1 — Valid HMAC signature + valid machine auth → 200."""
    monkeypatch.setenv(VAPI_SIG_ENV, VAPI_SIG_SECRET)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(
            URL,
            content=_VALID_PAYLOAD_BYTES,
            headers={
                "Content-Type": "application/json",
                VAPI_SIG_HEADER: _vapi_sig(),
            },
        )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_missing_vapi_sig_header_returns_401(client_sig_tests, monkeypatch):
    """M47-2 — Missing X-Vapi-Signature header → 401."""
    monkeypatch.setenv(VAPI_SIG_ENV, VAPI_SIG_SECRET)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_invalid_vapi_sig_returns_401(client_sig_tests, monkeypatch):
    """M47-3 — Wrong HMAC digest value → 401."""
    monkeypatch.setenv(VAPI_SIG_ENV, VAPI_SIG_SECRET)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(
            URL,
            content=_VALID_PAYLOAD_BYTES,
            headers={
                "Content-Type": "application/json",
                VAPI_SIG_HEADER: "sha256=deadbeefdeadbeef",
            },
        )
    assert response.status_code == 401


def test_missing_vapi_secret_env_returns_503(client_sig_tests, monkeypatch):
    """M47-4 — VAPI_WEBHOOK_SECRET not set → 503."""
    monkeypatch.delenv(VAPI_SIG_ENV, raising=False)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(
            URL,
            content=_VALID_PAYLOAD_BYTES,
            headers={
                "Content-Type": "application/json",
                VAPI_SIG_HEADER: "sha256=anysig",
            },
        )
    assert response.status_code == 503


def test_vapi_sig_uses_raw_request_body(client_sig_tests, monkeypatch):
    """M47-8 — Signature computed over different bytes → 401 (raw body check)."""
    monkeypatch.setenv(VAPI_SIG_ENV, VAPI_SIG_SECRET)
    tampered_body = json.dumps({**VALID_PAYLOAD, "extra": "tampered"}).encode()
    sig_over_original = _vapi_sig(_VALID_PAYLOAD_BYTES)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)):
        response = client_sig_tests.post(
            URL,
            content=tampered_body,
            headers={
                "Content-Type": "application/json",
                VAPI_SIG_HEADER: sig_over_original,
            },
        )
    assert response.status_code == 401


def test_audit_records_after_valid_sig_and_processing(client_sig_tests, monkeypatch):
    """M47-7 — Audit event recorded after valid sig + successful processing."""
    monkeypatch.setenv(VAPI_SIG_ENV, VAPI_SIG_SECRET)
    with patch(PROCESS_EVENT, new=AsyncMock(return_value=SUCCESS_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        response = client_sig_tests.post(
            URL,
            content=_VALID_PAYLOAD_BYTES,
            headers={
                "Content-Type": "application/json",
                VAPI_SIG_HEADER: _vapi_sig(),
            },
        )
    assert response.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "vapi.call_event"
    assert event["actor_type"] == "machine"
