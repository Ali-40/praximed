"""
Machine/internal authentication context — PraxisMed Sprint 3 / Module 39

Provides MachineAuthContext and authorization helpers for machine-to-machine
API access (Vapi webhooks, n8n calendar sync, availability tools).

Header-based trust only — no real signature verification in this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set


class MachineAuthError(RuntimeError):
    ...


class InvalidMachineAuthHeaderError(MachineAuthError):
    ...


class MachineAccessDeniedError(MachineAuthError):
    ...


DEFAULT_MACHINE_AUTH_SCHEME = "internal_service_header"

ALLOWED_SERVICE_NAMES: Set[str] = {"vapi", "n8n", "internal", "system", "dashboard"}

ALLOWED_SERVICE_SCOPES: Set[str] = {
    "availability:read",
    "calendar:sync",
    "vapi:webhook",
    "vapi:tool",
    "clinical:workflow",
    "internal:admin",
}


@dataclass
class MachineAuthContext:
    service_name: str
    clinic_id: Optional[str] = None
    scopes: Set[str] = field(default_factory=set)
    auth_scheme: str = DEFAULT_MACHINE_AUTH_SCHEME
    raw_claims: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self) -> None:
        if not self.service_name or not str(self.service_name).strip():
            raise InvalidMachineAuthHeaderError("service_name must not be empty")
        if self.service_name not in ALLOWED_SERVICE_NAMES:
            raise InvalidMachineAuthHeaderError(
                f"Unknown service: {self.service_name!r}. "
                f"Allowed: {sorted(ALLOWED_SERVICE_NAMES)}"
            )
        if self.clinic_id is not None and not str(self.clinic_id).strip():
            raise InvalidMachineAuthHeaderError("clinic_id must not be empty when provided")
        if not isinstance(self.scopes, set):
            raise InvalidMachineAuthHeaderError("scopes must be a set")
        unknown = self.scopes - ALLOWED_SERVICE_SCOPES
        if unknown:
            raise InvalidMachineAuthHeaderError(
                f"Unknown scopes: {sorted(unknown)!r}"
            )


def normalize_machine_header_value(value: Optional[str], header_name: str) -> str:
    if value is None:
        raise InvalidMachineAuthHeaderError(f"Missing required header: {header_name!r}")
    stripped = value.strip()
    if not stripped:
        raise InvalidMachineAuthHeaderError(f"Header {header_name!r} must not be empty")
    return stripped


def parse_scope_header(value: Optional[str]) -> Set[str]:
    if not value or not value.strip():
        return set()
    scopes = {s.strip() for s in value.split(",") if s.strip()}
    unknown = scopes - ALLOWED_SERVICE_SCOPES
    if unknown:
        raise InvalidMachineAuthHeaderError(f"Unknown scopes: {sorted(unknown)!r}")
    return scopes


def build_machine_auth_context_from_headers(
    service_name: Optional[str],
    clinic_id: Optional[str] = None,
    scopes: Optional[str] = None,
    auth_scheme: str = DEFAULT_MACHINE_AUTH_SCHEME,
    raw_claims: Optional[Dict[str, Any]] = None,
) -> MachineAuthContext:
    normalized_service = normalize_machine_header_value(service_name, "X-Service-Name")
    normalized_clinic_id: Optional[str] = None
    if clinic_id is not None:
        normalized_clinic_id = normalize_machine_header_value(clinic_id, "X-Service-Clinic-Id")
    parsed_scopes = parse_scope_header(scopes)
    if raw_claims is not None and not isinstance(raw_claims, dict):
        raise InvalidMachineAuthHeaderError("raw_claims must be a dict when provided")
    return MachineAuthContext(
        service_name=normalized_service,
        clinic_id=normalized_clinic_id,
        scopes=parsed_scopes,
        auth_scheme=auth_scheme,
        raw_claims=raw_claims,
    )


def ensure_machine_service_allowed(
    machine_context: MachineAuthContext,
    allowed_services: Set[str],
) -> None:
    if not allowed_services:
        raise MachineAuthError("allowed_services must not be empty")
    unknown = allowed_services - ALLOWED_SERVICE_NAMES
    if unknown:
        raise MachineAuthError(
            f"Unknown services in allowed_services: {sorted(unknown)!r}"
        )
    if machine_context.service_name not in allowed_services:
        raise MachineAccessDeniedError(
            f"Service {machine_context.service_name!r} is not in allowed services"
        )


def ensure_machine_scope(
    machine_context: MachineAuthContext,
    required_scope: str,
) -> None:
    if required_scope not in ALLOWED_SERVICE_SCOPES:
        raise MachineAuthError(f"Unknown required scope: {required_scope!r}")
    if required_scope not in machine_context.scopes:
        raise MachineAccessDeniedError(
            f"Service {machine_context.service_name!r} does not have required scope "
            f"{required_scope!r}"
        )


def ensure_machine_clinic_access(
    machine_context: MachineAuthContext,
    requested_clinic_id: str,
) -> None:
    if not requested_clinic_id or not str(requested_clinic_id).strip():
        raise MachineAuthError("requested_clinic_id must not be empty")
    if machine_context.clinic_id is None:
        if "internal:admin" not in machine_context.scopes:
            raise MachineAccessDeniedError(
                "Service has no clinic_id and does not have internal:admin scope"
            )
        return
    if machine_context.clinic_id != requested_clinic_id:
        raise MachineAccessDeniedError(
            f"Service clinic_id {machine_context.clinic_id!r} does not match "
            f"requested {requested_clinic_id!r}"
        )


def authorize_machine_access(
    machine_context: MachineAuthContext,
    allowed_services: Set[str],
    required_scope: Optional[str] = None,
    requested_clinic_id: Optional[str] = None,
) -> MachineAuthContext:
    ensure_machine_service_allowed(machine_context, allowed_services)
    if required_scope is not None:
        ensure_machine_scope(machine_context, required_scope)
    if requested_clinic_id is not None:
        ensure_machine_clinic_access(machine_context, requested_clinic_id)
    return machine_context
