"""
Integration tests for Vapi tool routes — PraxisMed Sprint 1 / Module 12

Strategy
--------
• All tests use FastAPI's synchronous TestClient.
• ``get_db_pool`` and ``get_config_loader`` are overridden via
  ``app.dependency_overrides`` so no real DB or filesystem access occurs.
• Availability engine functions are patched at their import site in the
  route module so no real availability logic runs.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.dependencies.machine_auth import get_machine_auth_context
from backend.app.api.deps import get_db_pool, get_config_loader
from backend.app.core.machine_auth import MachineAuthContext

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CHECK_URL   = "/vapi/tools/check-availability"
SUGGEST_URL = "/vapi/tools/suggest-slots"

TENANT_ID  = "11111111-1111-4111-8111-111111111111"
CLINIC_REF = TENANT_ID

T0 = datetime(2024, 6, 3, 9, 0, tzinfo=timezone.utc)
T1 = datetime(2024, 6, 3, 9, 30, tzinfo=timezone.utc)

CHECK_PAYLOAD = {
    "clinic_ref": CLINIC_REF,
    "starts_at":  T0.isoformat(),
    "ends_at":    T1.isoformat(),
}

SUGGEST_PAYLOAD = {
    "clinic_ref": CLINIC_REF,
    "date":       "2024-06-03",
    "limit":      3,
}

IS_SLOT_BOOKABLE = (
    "backend.app.api.routes.vapi_tools.availability_engine.is_slot_bookable"
)
SUGGEST_SLOTS = (
    "backend.app.api.routes.vapi_tools.availability_engine.suggest_available_slots"
)

OTHER_CLINIC_ID = "99999999-9999-4999-8999-999999999999"

FAKE_POOL = object()


def _machine_auth() -> MachineAuthContext:
    return MachineAuthContext(
        service_name="vapi", clinic_id=CLINIC_REF, scopes={"vapi:tool"}
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_config(tenant_id: str = TENANT_ID) -> MagicMock:
    cfg = MagicMock()
    cfg.tenant_id = tenant_id
    return cfg


def _make_fake_loader(config: Any = None) -> MagicMock:
    cfg = config or _make_fake_config()
    loader = MagicMock()
    loader.load = AsyncMock(return_value=cfg)
    return loader


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client_full():
    fake_config = _make_fake_config()
    fake_loader = _make_fake_loader(fake_config)
    app.dependency_overrides[get_db_pool]              = lambda: FAKE_POOL
    app.dependency_overrides[get_config_loader]        = lambda: fake_loader
    app.dependency_overrides[get_machine_auth_context] = _machine_auth
    yield TestClient(app), fake_loader, fake_config
    app.dependency_overrides.pop(get_db_pool,              None)
    app.dependency_overrides.pop(get_config_loader,        None)
    app.dependency_overrides.pop(get_machine_auth_context, None)


@pytest.fixture()
def client_no_pool():
    app.dependency_overrides.pop(get_db_pool, None)
    try:
        del app.state.db_pool
    except (AttributeError, KeyError):
        pass
    fake_loader = _make_fake_loader()
    app.dependency_overrides[get_config_loader]        = lambda: fake_loader
    app.dependency_overrides[get_machine_auth_context] = _machine_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,              None)
    app.dependency_overrides.pop(get_config_loader,        None)
    app.dependency_overrides.pop(get_machine_auth_context, None)


@pytest.fixture()
def client_no_loader():
    app.dependency_overrides[get_db_pool]              = lambda: FAKE_POOL
    app.dependency_overrides[get_machine_auth_context] = _machine_auth
    app.dependency_overrides.pop(get_config_loader, None)
    try:
        del app.state.config_loader
    except (AttributeError, KeyError):
        pass
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,              None)
    app.dependency_overrides.pop(get_config_loader,        None)
    app.dependency_overrides.pop(get_machine_auth_context, None)


@pytest.fixture()
def client_no_auth():
    """TestClient with pool + loader overrides — no machine auth override."""
    fake_config = _make_fake_config()
    fake_loader = _make_fake_loader(fake_config)
    app.dependency_overrides[get_db_pool]       = lambda: FAKE_POOL
    app.dependency_overrides[get_config_loader] = lambda: fake_loader
    app.dependency_overrides.pop(get_machine_auth_context, None)
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool,              None)
    app.dependency_overrides.pop(get_config_loader,        None)


# ---------------------------------------------------------------------------
# 1. Check returns 200 and available=True
# ---------------------------------------------------------------------------

def test_vapi_check_returns_200_available_true(client_full):
    client, _loader, _cfg = client_full
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)):
        response = client.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["available"] is True
    assert "verfügbar" in body["message"].lower() or "available" in body["message"].lower()


# ---------------------------------------------------------------------------
# 2. Check route calls config_loader.load
# ---------------------------------------------------------------------------

def test_vapi_check_calls_config_loader(client_full):
    client, fake_loader, _cfg = client_full
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)):
        client.post(CHECK_URL, json=CHECK_PAYLOAD)

    fake_loader.load.assert_awaited_once_with(CLINIC_REF)


# ---------------------------------------------------------------------------
# 3. Check route passes pool to is_slot_bookable
# ---------------------------------------------------------------------------

def test_vapi_check_passes_pool_to_engine(client_full):
    client, _loader, _cfg = client_full
    captured: list[Any] = []

    async def capture(pool, config, starts_at, ends_at):
        captured.append(pool)
        return True

    with patch(IS_SLOT_BOOKABLE, new=capture):
        client.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert len(captured) == 1
    assert captured[0] is FAKE_POOL


# ---------------------------------------------------------------------------
# 4. Check returns available=False when engine returns False
# ---------------------------------------------------------------------------

def test_vapi_check_returns_available_false(client_full):
    client, _loader, _cfg = client_full
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=False)):
        response = client.post(CHECK_URL, json=CHECK_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is False
    # Message should guide agent to offer alternatives
    assert "alternative" in body["message"].lower() or "nicht verfügbar" in body["message"].lower()


# ---------------------------------------------------------------------------
# 5. Suggest returns 200 and slots
# ---------------------------------------------------------------------------

def test_vapi_suggest_returns_200_with_slots(client_full):
    client, _loader, _cfg = client_full
    fake_slots = [{"starts_at": T0, "ends_at": T1}]
    with patch(SUGGEST_SLOTS, new=AsyncMock(return_value=fake_slots)):
        response = client.post(SUGGEST_URL, json=SUGGEST_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert len(body["slots"]) == 1


# ---------------------------------------------------------------------------
# 6. Suggest returns callback message when no slots
# ---------------------------------------------------------------------------

def test_vapi_suggest_callback_message_when_no_slots(client_full):
    client, _loader, _cfg = client_full
    with patch(SUGGEST_SLOTS, new=AsyncMock(return_value=[])):
        response = client.post(SUGGEST_URL, json=SUGGEST_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["slots"] == []
    assert "rückruf" in body["message"].lower() or "callback" in body["message"].lower()


# ---------------------------------------------------------------------------
# 7. Missing db_pool → 503
# ---------------------------------------------------------------------------

def test_vapi_check_missing_pool_returns_503(client_no_pool):
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)):
        response = client_no_pool.post(CHECK_URL, json=CHECK_PAYLOAD)
    assert response.status_code == 503


# ---------------------------------------------------------------------------
# 8. Missing config_loader → 503
# ---------------------------------------------------------------------------

def test_vapi_check_missing_config_loader_returns_503(client_no_loader):
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)):
        response = client_no_loader.post(CHECK_URL, json=CHECK_PAYLOAD)
    assert response.status_code == 503


# ---------------------------------------------------------------------------
# 9. Invalid request body → 422
# ---------------------------------------------------------------------------

def test_vapi_check_invalid_body_returns_422(client_full):
    client, _loader, _cfg = client_full
    response = client.post(CHECK_URL, json={"clinic_ref": ""})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 10. InvalidAvailabilityRangeError → 400
# ---------------------------------------------------------------------------

def test_vapi_check_range_error_returns_400(client_full):
    from backend.app.modules.calendar_sync.availability_engine import (
        InvalidAvailabilityRangeError,
    )
    client, _loader, _cfg = client_full
    with patch(
        IS_SLOT_BOOKABLE,
        new=AsyncMock(side_effect=InvalidAvailabilityRangeError("bad range")),
    ):
        response = client.post(CHECK_URL, json=CHECK_PAYLOAD)
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# 11. Unexpected engine error → 500
# ---------------------------------------------------------------------------

def test_vapi_check_unexpected_error_returns_500(client_full):
    client, _loader, _cfg = client_full
    with patch(
        IS_SLOT_BOOKABLE,
        new=AsyncMock(side_effect=RuntimeError("boom")),
    ):
        response = client.post(CHECK_URL, json=CHECK_PAYLOAD)
    assert response.status_code == 500
    assert "Internal error" in response.json()["detail"]


# ===========================================================================
# Module 18 — Capture appointment request route tests
# ===========================================================================

CAPTURE_URL = "/vapi/tools/capture-appointment-request"

CAPTURE_PAYLOAD = {
    "clinic_ref":   CLINIC_REF,
    "call_id":      "vapi-call-abc123",
    "patient_name": "Maria Muster",
}

FAKE_CAPTURE_RESULT = {
    "ok":        True,
    "clinic_id": TENANT_ID,
    "request": {
        "id":              "22222222-2222-4222-8222-222222222222",
        "clinic_id":       TENANT_ID,
        "source":          "vapi",
        "source_ref":      "vapi-call-abc123",
        "patient_name":    "Maria Muster",
        "status":          "new",
        "action_required": True,
        "created_at":      "2024-06-03T09:00:00+00:00",
        "updated_at":      "2024-06-03T09:00:00+00:00",
    },
    "message": (
        "The appointment request has been captured and forwarded to the clinic. "
        "Staff must review and confirm the appointment before it is booked."
    ),
}

CAPTURE_FUNC = (
    "backend.app.modules.vapi.vapi_appointment_capture.capture_vapi_appointment_request"
)
AUDIT_SAFE = "backend.app.modules.audit.audit_logger.safe_record_audit_event"


# ---------------------------------------------------------------------------
# 1. POST /vapi/tools/capture-appointment-request returns 200
# ---------------------------------------------------------------------------

def test_capture_returns_200(client_full):
    client, _loader, _cfg = client_full
    with patch(CAPTURE_FUNC, new=AsyncMock(return_value=FAKE_CAPTURE_RESULT)):
        response = client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert "request" in body


# ---------------------------------------------------------------------------
# 2. Route calls capture_vapi_appointment_request with correct args
# ---------------------------------------------------------------------------

def test_capture_route_calls_capture_service(client_full):
    client, _loader, _cfg = client_full
    mock_fn = AsyncMock(return_value=FAKE_CAPTURE_RESULT)
    with patch(CAPTURE_FUNC, new=mock_fn):
        client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    mock_fn.assert_awaited_once()
    kw = mock_fn.call_args.kwargs
    assert kw["clinic_ref"]   == CLINIC_REF
    assert kw["call_id"]      == "vapi-call-abc123"
    assert kw["patient_name"] == "Maria Muster"


# ---------------------------------------------------------------------------
# 3. Route passes app DB pool to capture service
# ---------------------------------------------------------------------------

def test_capture_route_passes_pool(client_full):
    client, _loader, _cfg = client_full
    captured: list[Any] = []

    async def capturing(*args, **kwargs):
        captured.append(kwargs.get("pool"))
        return FAKE_CAPTURE_RESULT

    with patch(CAPTURE_FUNC, new=capturing):
        client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)

    assert len(captured) == 1
    assert captured[0] is FAKE_POOL


# ---------------------------------------------------------------------------
# 4. Route passes app config_loader to capture service
# ---------------------------------------------------------------------------

def test_capture_route_passes_config_loader(client_full):
    client, fake_loader, _cfg = client_full
    captured: list[Any] = []

    async def capturing(*args, **kwargs):
        captured.append(kwargs.get("config_loader"))
        return FAKE_CAPTURE_RESULT

    with patch(CAPTURE_FUNC, new=capturing):
        client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)

    assert len(captured) == 1
    assert captured[0] is fake_loader


# ---------------------------------------------------------------------------
# 5. Response message does not claim appointment is already confirmed
# ---------------------------------------------------------------------------

def test_capture_message_not_auto_confirmed(client_full):
    client, _loader, _cfg = client_full
    with patch(CAPTURE_FUNC, new=AsyncMock(return_value=FAKE_CAPTURE_RESULT)):
        response = client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    msg = response.json()["message"].lower()
    assert "captured" in msg or "staff" in msg
    assert "appointment is confirmed" not in msg
    assert "automatically confirmed" not in msg
    assert "booking confirmed" not in msg


# ---------------------------------------------------------------------------
# 6. Missing db_pool returns 503
# ---------------------------------------------------------------------------

def test_capture_missing_pool_returns_503(client_no_pool):
    response = client_no_pool.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert response.status_code == 503


# ---------------------------------------------------------------------------
# 7. Missing config_loader returns 503
# ---------------------------------------------------------------------------

def test_capture_missing_config_loader_returns_503(client_no_loader):
    response = client_no_loader.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert response.status_code == 503


# ---------------------------------------------------------------------------
# 8. Invalid request body returns 422
# ---------------------------------------------------------------------------

def test_capture_invalid_body_returns_422(client_full):
    client, _loader, _cfg = client_full
    # Missing required patient_name; invalid urgency_level
    response = client.post(CAPTURE_URL, json={
        "clinic_ref": CLINIC_REF,
        "call_id":    "vapi-call-abc123",
        "patient_name": "",
    })
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 9. Invalid capture input maps to 400
# ---------------------------------------------------------------------------

def test_capture_invalid_input_returns_400(client_full):
    from backend.app.modules.vapi.vapi_appointment_capture import (
        InvalidVapiAppointmentCaptureError,
    )
    client, _loader, _cfg = client_full
    with patch(
        CAPTURE_FUNC,
        new=AsyncMock(side_effect=InvalidVapiAppointmentCaptureError("bad input")),
    ):
        response = client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert response.status_code == 400
    assert "bad input" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 10. Unexpected capture error maps to 500
# ---------------------------------------------------------------------------

def test_capture_unexpected_error_returns_500(client_full):
    client, _loader, _cfg = client_full
    with patch(
        CAPTURE_FUNC,
        new=AsyncMock(side_effect=RuntimeError("db exploded")),
    ):
        response = client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert response.status_code == 500
    assert "Internal error" in response.json()["detail"]


# ===========================================================================
# Module 40 — Machine auth guard tests
# ===========================================================================


# ---------------------------------------------------------------------------
# 11. Missing X-Service-Name header → 401
# ---------------------------------------------------------------------------

def test_missing_machine_auth_headers_returns_401(client_no_auth):
    response = client_no_auth.post(CHECK_URL, json=CHECK_PAYLOAD)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 12. Invalid service name → 401
# ---------------------------------------------------------------------------

def test_invalid_service_name_returns_401(client_no_auth):
    response = client_no_auth.post(
        CHECK_URL,
        json=CHECK_PAYLOAD,
        headers={
            "X-Service-Name": "rogue-bot",
            "X-Service-Clinic-Id": CLINIC_REF,
            "X-Service-Scopes": "vapi:tool",
        },
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 13. Wrong clinic → 403
# ---------------------------------------------------------------------------

def test_wrong_clinic_returns_403(client_no_auth):
    response = client_no_auth.post(
        CHECK_URL,
        json=CHECK_PAYLOAD,
        headers={
            "X-Service-Name": "vapi",
            "X-Service-Clinic-Id": OTHER_CLINIC_ID,
            "X-Service-Scopes": "vapi:tool",
        },
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 14. Missing required scope → 403
# ---------------------------------------------------------------------------

def test_missing_scope_returns_403(client_no_auth):
    response = client_no_auth.post(
        CHECK_URL,
        json=CHECK_PAYLOAD,
        headers={
            "X-Service-Name": "vapi",
            "X-Service-Clinic-Id": CLINIC_REF,
            "X-Service-Scopes": "availability:read",
        },
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 15. Valid machine auth → 200
# ---------------------------------------------------------------------------

def test_valid_machine_auth_returns_200(client_no_auth):
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)):
        response = client_no_auth.post(
            CHECK_URL,
            json=CHECK_PAYLOAD,
            headers={
                "X-Service-Name": "vapi",
                "X-Service-Clinic-Id": CLINIC_REF,
                "X-Service-Scopes": "vapi:tool",
            },
        )
    assert response.status_code == 200


# ===========================================================================
# Module 44 — Audit logging tests
# ===========================================================================


def test_capture_records_audit_event(client_full):
    client, _loader, _cfg = client_full
    with patch(CAPTURE_FUNC, new=AsyncMock(return_value=FAKE_CAPTURE_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert resp.status_code == 200
    mock_audit.assert_awaited_once()
    event = mock_audit.call_args[0][1]
    assert event["action"] == "vapi.appointment_capture"
    assert event["resource_type"] == "appointment_requests"
    assert event["actor_type"] == "machine"


def test_capture_audit_severity_is_warning(client_full):
    client, _loader, _cfg = client_full
    with patch(CAPTURE_FUNC, new=AsyncMock(return_value=FAKE_CAPTURE_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["severity"] == "warning"


def test_capture_audit_metadata_includes_call_id(client_full):
    client, _loader, _cfg = client_full
    with patch(CAPTURE_FUNC, new=AsyncMock(return_value=FAKE_CAPTURE_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["metadata"]["call_id"] == "vapi-call-abc123"


def test_capture_audit_resource_id_from_request(client_full):
    client, _loader, _cfg = client_full
    with patch(CAPTURE_FUNC, new=AsyncMock(return_value=FAKE_CAPTURE_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert resp.status_code == 200
    event = mock_audit.call_args[0][1]
    assert event["resource_id"] == FAKE_CAPTURE_RESULT["request"]["id"]


def test_capture_audit_failure_does_not_break_route(client_full):
    client, _loader, _cfg = client_full
    with patch(CAPTURE_FUNC, new=AsyncMock(return_value=FAKE_CAPTURE_RESULT)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": False, "audit_log": None, "message": "failed", "error": "db"})):
        resp = client.post(CAPTURE_URL, json=CAPTURE_PAYLOAD)
    assert resp.status_code == 200


def test_check_availability_does_not_record_audit(client_full):
    client, _loader, _cfg = client_full
    with patch(IS_SLOT_BOOKABLE, new=AsyncMock(return_value=True)), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(CHECK_URL, json=CHECK_PAYLOAD)
    assert resp.status_code == 200
    mock_audit.assert_not_awaited()


def test_suggest_slots_does_not_record_audit(client_full):
    client, _loader, _cfg = client_full
    with patch(SUGGEST_SLOTS, new=AsyncMock(return_value=[])), \
         patch(AUDIT_SAFE, new=AsyncMock(return_value={"ok": True})) as mock_audit:
        resp = client.post(SUGGEST_URL, json=SUGGEST_PAYLOAD)
    assert resp.status_code == 200
    mock_audit.assert_not_awaited()
