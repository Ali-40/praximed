"""
Audit Logger Service — PraxisMed Sprint 4 / Module 42

Thin service layer that builds and records structured audit events.
Wraps audit_repo.create_audit_log with higher-level helpers for
human (AuthContext) and machine (MachineAuthContext) actors.

No FastAPI imports. No external service calls. No schema changes.
Route integration is Module 43.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.db.repositories import audit_repo
from backend.app.db.repositories.audit_repo import (
    AuditRepoError,
    InvalidAuditEventError as _RepoValidationError,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class AuditLoggerError(RuntimeError):
    """Raised when the audit logger encounters an unexpected failure."""


class InvalidAuditLogInputError(ValueError):
    """Raised when audit event input fails validation."""


# ---------------------------------------------------------------------------
# Allowed values (mirrors audit_repo — kept here for standalone validation)
# ---------------------------------------------------------------------------

_VALID_ACTOR_TYPES = frozenset({"user", "machine", "system"})
_VALID_RESULTS = frozenset({"success", "failure", "denied"})
_VALID_SEVERITIES = frozenset({"info", "warning", "critical"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _assert_nonempty(value: Any, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidAuditLogInputError(f"{name!r} must not be empty")


def _assert_valid_enum(value: str, name: str, valid: frozenset) -> None:
    if value not in valid:
        raise InvalidAuditLogInputError(
            f"{name!r} must be one of {sorted(valid)!r}; got {value!r}"
        )


# ---------------------------------------------------------------------------
# 1. build_audit_event
# ---------------------------------------------------------------------------


def build_audit_event(
    clinic_id: str,
    action: str,
    resource_type: str,
    actor_type: str = "system",
    actor_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    result: str = "success",
    severity: str = "info",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(action, "action")
    _assert_nonempty(resource_type, "resource_type")
    _assert_valid_enum(actor_type, "actor_type", _VALID_ACTOR_TYPES)
    _assert_valid_enum(result, "result", _VALID_RESULTS)
    _assert_valid_enum(severity, "severity", _VALID_SEVERITIES)

    return {
        "clinic_id": clinic_id,
        "action": action,
        "resource_type": resource_type,
        "actor_type": actor_type,
        "actor_id": actor_id,
        "resource_id": resource_id,
        "result": result,
        "severity": severity,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "request_id": request_id,
        "metadata": metadata,
    }


# ---------------------------------------------------------------------------
# 2. build_user_audit_event
# ---------------------------------------------------------------------------


def build_user_audit_event(
    auth_context: Any,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    result: str = "success",
    severity: str = "info",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    combined_meta: Dict[str, Any] = {"role": auth_context.role}
    if metadata:
        combined_meta.update(metadata)

    return build_audit_event(
        clinic_id=auth_context.clinic_id,
        action=action,
        resource_type=resource_type,
        actor_type="user",
        actor_id=auth_context.user_id,
        resource_id=resource_id,
        result=result,
        severity=severity,
        metadata=combined_meta,
    )


# ---------------------------------------------------------------------------
# 3. build_machine_audit_event
# ---------------------------------------------------------------------------


def build_machine_audit_event(
    machine_context: Any,
    action: str,
    resource_type: str,
    clinic_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    result: str = "success",
    severity: str = "info",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    resolved_clinic_id = clinic_id if clinic_id is not None else machine_context.clinic_id

    if not resolved_clinic_id or not str(resolved_clinic_id).strip():
        raise InvalidAuditLogInputError(
            "No clinic_id could be determined for machine audit event. "
            "Provide an explicit clinic_id or ensure machine_context.clinic_id is set."
        )

    scopes = machine_context.scopes
    combined_meta: Dict[str, Any] = {
        "scopes": sorted(scopes) if scopes else [],
    }
    if metadata:
        combined_meta.update(metadata)

    return build_audit_event(
        clinic_id=resolved_clinic_id,
        action=action,
        resource_type=resource_type,
        actor_type="machine",
        actor_id=machine_context.service_name,
        resource_id=resource_id,
        result=result,
        severity=severity,
        metadata=combined_meta,
    )


# ---------------------------------------------------------------------------
# 4. record_audit_event
# ---------------------------------------------------------------------------


async def record_audit_event(pool: Any, event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        audit_log = await audit_repo.create_audit_log(
            pool=pool,
            clinic_id=event.get("clinic_id"),
            action=event.get("action", ""),
            resource_type=event.get("resource_type", ""),
            actor_type=event.get("actor_type", "system"),
            actor_id=event.get("actor_id"),
            resource_id=event.get("resource_id"),
            result=event.get("result", "success"),
            severity=event.get("severity", "info"),
            ip_address=event.get("ip_address"),
            user_agent=event.get("user_agent"),
            request_id=event.get("request_id"),
            metadata=event.get("metadata"),
        )
    except _RepoValidationError as exc:
        raise InvalidAuditLogInputError(str(exc)) from exc
    except AuditRepoError as exc:
        raise AuditLoggerError(str(exc)) from exc
    except Exception as exc:
        raise AuditLoggerError(f"Unexpected error recording audit event: {exc}") from exc

    return {
        "ok": True,
        "audit_log": audit_log,
        "message": "Audit event recorded.",
    }


# ---------------------------------------------------------------------------
# 5. safe_record_audit_event
# ---------------------------------------------------------------------------


async def safe_record_audit_event(pool: Any, event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return await record_audit_event(pool, event)
    except Exception as exc:
        return {
            "ok": False,
            "audit_log": None,
            "message": "Audit event could not be recorded.",
            "error": str(exc),
        }
