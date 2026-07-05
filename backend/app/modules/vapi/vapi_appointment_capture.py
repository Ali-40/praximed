"""
Vapi appointment capture service — PraxisMed Sprint 1 / Module 18
Updated: Sprint 11 / Module 88 — adapt_vapi_tool_call_body for nested tool-call shape

Translates a completed Vapi phone session into a structured appointment
request for clinic staff review.

Business rule: this module NEVER confirms or books an appointment
automatically.  It only creates a request with status='new' and
action_required=True so clinic staff can review before confirming.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

from backend.app.db.repositories import appointment_request_repo
from backend.app.db.repositories import patient_repo

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class VapiAppointmentCaptureError(RuntimeError):
    """Base exception for Vapi appointment capture errors."""


class InvalidVapiAppointmentCaptureError(VapiAppointmentCaptureError):
    """Raised when required fields are missing or values are invalid."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _assert_nonempty(value: str, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidVapiAppointmentCaptureError(f"{name!r} must not be empty")


# ---------------------------------------------------------------------------
# Adapter — nested Vapi tool-call body → flat VapiAppointmentCaptureRequest
# ---------------------------------------------------------------------------


def adapt_vapi_tool_call_body(
    raw_body: Dict[str, Any],
    machine_clinic_id: str,
) -> Dict[str, Any]:
    """
    Normalize a Vapi tool-call body into VapiAppointmentCaptureRequest fields.

    Supports two shapes:
    - Nested (real Vapi server-URL): {"message": {"toolCallList": [...], "call": {...}}}
    - Flat (local harness): {"clinic_ref": "...", "call_id": "...", "patient_name": "..."}

    Security: for nested payloads, clinic_ref is ALWAYS taken from machine_clinic_id.
    Any clinic_ref embedded in function.arguments is silently ignored.
    Raw payload is stored for audit trail but never logged.
    """
    message = raw_body.get("message")
    if not isinstance(message, dict):
        return raw_body

    tool_call_list = message.get("toolCallList")
    if not isinstance(tool_call_list, list) or not tool_call_list:
        return raw_body

    first_call = tool_call_list[0] if isinstance(tool_call_list[0], dict) else {}
    func = first_call.get("function", {}) if isinstance(first_call, dict) else {}
    arguments = func.get("arguments", {})

    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except (json.JSONDecodeError, TypeError):
            arguments = {}
    if not isinstance(arguments, dict):
        arguments = {}

    call_obj = message.get("call")
    call_id: Optional[str] = None
    caller_phone: Optional[str] = None

    if isinstance(call_obj, dict):
        call_id = call_obj.get("id")
        customer = call_obj.get("customer")
        if isinstance(customer, dict):
            caller_phone = customer.get("number")

    if not call_id and isinstance(first_call, dict):
        call_id = first_call.get("id") or ""

    adapted: Dict[str, Any] = {
        "clinic_ref":   machine_clinic_id,
        "call_id":      call_id or "",
        "patient_name": arguments.get("patient_name", ""),
        "raw_payload":  raw_body,
    }

    for field in ("patient_email", "date_of_birth", "reason",
                  "preferred_starts_at", "preferred_ends_at", "urgency_level"):
        if field in arguments:
            adapted[field] = arguments[field]

    if caller_phone is not None:
        adapted["caller_phone"] = caller_phone
    elif "caller_phone" in arguments:
        adapted["caller_phone"] = arguments["caller_phone"]

    return adapted


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def capture_vapi_appointment_request(
    pool: Any,
    config_loader: Any,
    clinic_ref: str,
    call_id: str,
    patient_name: str,
    caller_phone: Optional[str] = None,
    patient_email: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    reason: Optional[str] = None,
    preferred_starts_at: Optional[datetime] = None,
    preferred_ends_at: Optional[datetime] = None,
    urgency_level: str = "normal",
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Record a Vapi phone call as a structured appointment request.

    Validates inputs, resolves clinic_id from the config loader, then
    inserts an appointment_requests row with source='vapi',
    status='new', and action_required=True.

    Returns a plain dict the route layer passes back to Vapi.
    The response message explicitly states that staff confirmation is
    required — the appointment is NOT booked automatically.
    """
    _assert_nonempty(clinic_ref, "clinic_ref")
    _assert_nonempty(call_id, "call_id")
    _assert_nonempty(patient_name, "patient_name")

    if preferred_starts_at is not None and preferred_ends_at is not None:
        if preferred_ends_at <= preferred_starts_at:
            raise InvalidVapiAppointmentCaptureError(
                "preferred_ends_at must be strictly after preferred_starts_at"
            )

    config = await config_loader.load(clinic_ref)
    clinic_id = config.tenant_id

    # Find or create the patient record, scoped strictly to this clinic.
    # Matching is done by phone when available; a new row is created otherwise.
    # This links the appointment request to a durable patient identity so that
    # notifications, pre-appointment summaries, consultation drafts, and patient
    # timelines can all reference the same patient record.
    patient = await patient_repo.find_or_create_patient_from_vapi(
        pool=pool,
        clinic_id=clinic_id,
        full_name=patient_name,
        phone=caller_phone,
        email=patient_email,
        date_of_birth=date_of_birth,
    )
    patient_id = patient["id"]

    row = await appointment_request_repo.create_appointment_request(
        pool=pool,
        clinic_id=clinic_id,
        source="vapi",
        source_ref=call_id,
        patient_name=patient_name,
        patient_phone=caller_phone,
        patient_email=patient_email,
        date_of_birth=date_of_birth,
        reason=reason,
        preferred_starts_at=preferred_starts_at,
        preferred_ends_at=preferred_ends_at,
        status="new",
        urgency_level=urgency_level,
        action_required=True,
        patient_id=patient_id,
        raw_payload=raw_payload,
    )

    message = (
        "The appointment request has been captured and forwarded to the clinic. "
        "Staff must review and confirm the appointment before it is booked. "
        "The patient will be contacted once staff confirm the appointment."
    )

    notification_created = False
    notification_error: Optional[str] = None
    # str() converts asyncpg uuid.UUID objects to plain strings before passing
    # to notification_repo which stores related_resource_id as TEXT.
    notification_request_id: Optional[str] = (
        str(row["id"]) if isinstance(row, dict) and row.get("id") is not None else None
    )
    try:
        from backend.app.modules.notifications import notification_router  # local import avoids circulars
        await notification_router.create_appointment_request_notification(
            pool=pool,
            clinic_id=clinic_id,
            request_id=notification_request_id,
            patient_name=patient_name,
            urgency_level=urgency_level,
            reason=reason,
            suggested_next_action="Review and confirm",
            raw_payload=raw_payload,
        )
        notification_created = True
    except Exception as exc:
        notification_error = f"{type(exc).__name__}: {exc}"
        logger.error(
            "Notification creation failed for clinic_id=%s request_id=%s: %s",
            clinic_id,
            notification_request_id,
            notification_error,
        )
        notification_created = False

    return {
        "ok":                   True,
        "clinic_id":            clinic_id,
        "patient_id":           patient_id,
        "request":              row,
        "message":              message,
        "notification_created": notification_created,
        "notification_error":   notification_error,
    }
