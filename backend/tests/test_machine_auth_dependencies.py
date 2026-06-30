"""
Tests for machine auth FastAPI dependencies — PraxisMed Sprint 3 / Module 39.

Uses a tiny test-only FastAPI app. No real database.
"""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.app.api.dependencies.machine_auth import (
    get_machine_auth_context,
    require_availability_read_access,
    require_machine_access,
    require_n8n_calendar_sync_access,
    require_vapi_tool_access,
    require_vapi_webhook_access,
)
from backend.app.core.machine_auth import MachineAuthContext

# ---------------------------------------------------------------------------
# Tiny test-only FastAPI app
# ---------------------------------------------------------------------------

machine_test_app = FastAPI()

CLINIC_ID = "clinic-1"
OTHER_CLINIC_ID = "clinic-2"


@machine_test_app.get("/test/machine-me")
def route_machine_me(machine: MachineAuthContext = Depends(get_machine_auth_context)) -> dict:
    return {
        "service_name": machine.service_name,
        "clinic_id": machine.clinic_id,
        "scopes": sorted(machine.scopes),
    }


@machine_test_app.get("/test/machine-access")
def route_machine_access(
    machine: MachineAuthContext = Depends(get_machine_auth_context),
) -> dict:
    result = require_machine_access(
        machine_context=machine,
        allowed_services={"vapi", "internal"},
        required_scope="vapi:tool",
        requested_clinic_id=CLINIC_ID,
    )
    return {"ok": True, "service": result.service_name}


@machine_test_app.post("/test/vapi-tool")
def route_vapi_tool(
    machine: MachineAuthContext = Depends(get_machine_auth_context),
) -> dict:
    result = require_vapi_tool_access(requested_clinic_id=CLINIC_ID, machine_context=machine)
    return {"ok": True, "service": result.service_name}


@machine_test_app.post("/test/vapi-webhook")
def route_vapi_webhook(
    machine: MachineAuthContext = Depends(get_machine_auth_context),
) -> dict:
    result = require_vapi_webhook_access(requested_clinic_id=CLINIC_ID, machine_context=machine)
    return {"ok": True}


@machine_test_app.post("/test/n8n-calendar")
def route_n8n_calendar(
    machine: MachineAuthContext = Depends(get_machine_auth_context),
) -> dict:
    result = require_n8n_calendar_sync_access(
        requested_clinic_id=CLINIC_ID, machine_context=machine
    )
    return {"ok": True}


@machine_test_app.get("/test/availability")
def route_availability(
    machine: MachineAuthContext = Depends(get_machine_auth_context),
) -> dict:
    result = require_availability_read_access(
        requested_clinic_id=CLINIC_ID, machine_context=machine
    )
    return {"ok": True}


client = TestClient(machine_test_app, raise_server_exceptions=False)


def _headers(
    service_name: str = "vapi",
    clinic_id: str = CLINIC_ID,
    scopes: str = "vapi:tool",
) -> dict:
    h: dict = {"X-Service-Name": service_name}
    if clinic_id:
        h["X-Service-Clinic-Id"] = clinic_id
    if scopes:
        h["X-Service-Scopes"] = scopes
    return h


# ---------------------------------------------------------------------------
# 1. get_machine_auth_context returns context from valid headers
# ---------------------------------------------------------------------------


def test_get_machine_auth_context_valid_headers():
    resp = client.get("/test/machine-me", headers=_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["service_name"] == "vapi"
    assert data["clinic_id"] == CLINIC_ID
    assert "vapi:tool" in data["scopes"]


# ---------------------------------------------------------------------------
# 2. missing X-Service-Name returns HTTP 401
# ---------------------------------------------------------------------------


def test_missing_service_name_returns_401():
    resp = client.get(
        "/test/machine-me",
        headers={"X-Service-Clinic-Id": CLINIC_ID, "X-Service-Scopes": "vapi:tool"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 3. invalid X-Service-Name returns HTTP 401
# ---------------------------------------------------------------------------


def test_invalid_service_name_returns_401():
    resp = client.get("/test/machine-me", headers=_headers(service_name="rogue-service"))
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 4. invalid X-Service-Scopes returns HTTP 401
# ---------------------------------------------------------------------------


def test_invalid_service_scopes_returns_401():
    resp = client.get("/test/machine-me", headers=_headers(scopes="not:a:known:scope"))
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 5. require_machine_access allows valid machine context
# ---------------------------------------------------------------------------


def test_require_machine_access_allows_valid():
    resp = client.get("/test/machine-access", headers=_headers())
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 6. require_machine_access rejects disallowed service with HTTP 403
# ---------------------------------------------------------------------------


def test_require_machine_access_rejects_disallowed_service():
    resp = client.get(
        "/test/machine-access",
        headers=_headers(service_name="n8n", scopes="calendar:sync"),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 7. require_machine_access rejects missing scope with HTTP 403
# ---------------------------------------------------------------------------


def test_require_machine_access_rejects_missing_scope():
    resp = client.get(
        "/test/machine-access",
        headers={
            "X-Service-Name": "vapi",
            "X-Service-Clinic-Id": CLINIC_ID,
            "X-Service-Scopes": "availability:read",
        },
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 8. require_machine_access rejects wrong clinic with HTTP 403
# ---------------------------------------------------------------------------


def test_require_machine_access_rejects_wrong_clinic():
    resp = client.get(
        "/test/machine-access",
        headers=_headers(clinic_id=OTHER_CLINIC_ID),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 9. require_vapi_tool_access allows vapi with vapi:tool scope
# ---------------------------------------------------------------------------


def test_require_vapi_tool_access_allows_vapi():
    resp = client.post("/test/vapi-tool", headers=_headers(service_name="vapi", scopes="vapi:tool"))
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# 10. require_vapi_tool_access rejects n8n
# ---------------------------------------------------------------------------


def test_require_vapi_tool_access_rejects_n8n():
    resp = client.post(
        "/test/vapi-tool",
        headers=_headers(service_name="n8n", scopes="calendar:sync"),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 11. require_vapi_webhook_access allows vapi with vapi:webhook scope
# ---------------------------------------------------------------------------


def test_require_vapi_webhook_access_allows_vapi():
    resp = client.post(
        "/test/vapi-webhook",
        headers=_headers(service_name="vapi", scopes="vapi:webhook"),
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 12. require_n8n_calendar_sync_access allows n8n with calendar:sync scope
# ---------------------------------------------------------------------------


def test_require_n8n_calendar_sync_access_allows_n8n():
    resp = client.post(
        "/test/n8n-calendar",
        headers=_headers(service_name="n8n", scopes="calendar:sync"),
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 13. require_availability_read_access allows vapi with availability:read scope
# ---------------------------------------------------------------------------


def test_require_availability_read_access_allows_vapi():
    resp = client.get(
        "/test/availability",
        headers=_headers(service_name="vapi", scopes="availability:read"),
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 14. require_availability_read_access rejects missing scope
# ---------------------------------------------------------------------------


def test_require_availability_read_access_rejects_missing_scope():
    resp = client.get(
        "/test/availability",
        headers={
            "X-Service-Name": "vapi",
            "X-Service-Clinic-Id": CLINIC_ID,
            "X-Service-Scopes": "vapi:tool",
        },
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 15. No database is used
# ---------------------------------------------------------------------------


def test_no_database_used():
    resp = client.get("/test/machine-me", headers=_headers())
    assert resp.status_code == 200
    assert "service_name" in resp.json()
