"""
Vapi appointment capture service — PraxisMed Sprint 1 / Module 18

Translates a completed Vapi phone session into a structured appointment
request for clinic staff review.

Business rule: this module NEVER confirms or books an appointment
automatically.  It only creates a request with status='new' and
action_required=True so clinic staff can review before confirming.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from backend.app.db.repositories import appointment_request_repo


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
        raw_payload=raw_payload,
    )

    message = (
        "The appointment request has been captured and forwarded to the clinic. "
        "Staff must review and confirm the appointment before it is booked. "
        "The patient will be contacted once staff confirm the appointment."
    )

    notification_created = False
    try:
        from backend.app.modules.notifications import notification_router  # local import avoids circulars
        request_id = row.get("id") if isinstance(row, dict) else None
        await notification_router.create_appointment_request_notification(
            pool=pool,
            clinic_id=clinic_id,
            request_id=request_id,
            patient_name=patient_name,
            urgency_level=urgency_level,
            raw_payload=raw_payload,
        )
        notification_created = True
    except Exception:
        notification_created = False

    return {
        "ok":                  True,
        "clinic_id":           clinic_id,
        "request":             row,
        "message":             message,
        "notification_created": notification_created,
    }
