"""
Machine/internal auth FastAPI dependencies — PraxisMed Sprint 3 / Module 39

Provides get_machine_auth_context and require_* helpers for machine-to-machine
route protection. Not yet applied to existing routes (Module 40).
"""

from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException

from backend.app.core.machine_auth import (
    InvalidMachineAuthHeaderError,
    MachineAccessDeniedError,
    MachineAuthContext,
    MachineAuthError,
    authorize_machine_access,
    build_machine_auth_context_from_headers,
)


def get_machine_auth_context(
    x_service_name: Optional[str] = Header(default=None, alias="X-Service-Name"),
    x_service_clinic_id: Optional[str] = Header(default=None, alias="X-Service-Clinic-Id"),
    x_service_scopes: Optional[str] = Header(default=None, alias="X-Service-Scopes"),
) -> MachineAuthContext:
    try:
        return build_machine_auth_context_from_headers(
            service_name=x_service_name,
            clinic_id=x_service_clinic_id,
            scopes=x_service_scopes,
        )
    except (InvalidMachineAuthHeaderError, MachineAuthError) as exc:
        raise HTTPException(status_code=401, detail=str(exc))


def require_machine_access(
    machine_context: MachineAuthContext,
    allowed_services: set,
    required_scope: Optional[str] = None,
    requested_clinic_id: Optional[str] = None,
) -> MachineAuthContext:
    try:
        return authorize_machine_access(
            machine_context=machine_context,
            allowed_services=allowed_services,
            required_scope=required_scope,
            requested_clinic_id=requested_clinic_id,
        )
    except MachineAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


def require_vapi_tool_access(
    requested_clinic_id: str,
    machine_context: MachineAuthContext,
) -> MachineAuthContext:
    return require_machine_access(
        machine_context=machine_context,
        allowed_services={"vapi", "internal", "system"},
        required_scope="vapi:tool",
        requested_clinic_id=requested_clinic_id,
    )


def require_vapi_webhook_access(
    requested_clinic_id: Optional[str],
    machine_context: MachineAuthContext,
) -> MachineAuthContext:
    return require_machine_access(
        machine_context=machine_context,
        allowed_services={"vapi", "internal", "system"},
        required_scope="vapi:webhook",
        requested_clinic_id=requested_clinic_id,
    )


def require_n8n_calendar_sync_access(
    requested_clinic_id: str,
    machine_context: MachineAuthContext,
) -> MachineAuthContext:
    return require_machine_access(
        machine_context=machine_context,
        allowed_services={"n8n", "internal", "system"},
        required_scope="calendar:sync",
        requested_clinic_id=requested_clinic_id,
    )


def require_availability_read_access(
    requested_clinic_id: str,
    machine_context: MachineAuthContext,
) -> MachineAuthContext:
    return require_machine_access(
        machine_context=machine_context,
        allowed_services={"vapi", "internal", "system", "dashboard"},
        required_scope="availability:read",
        requested_clinic_id=requested_clinic_id,
    )
