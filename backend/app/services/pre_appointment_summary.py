"""
Pre-Appointment Summary Service — PraxisMed Sprint 17 / Module 122

Builds a structured, safe pre-appointment brief from linked
appointment_request and patient data.

Safety guarantees (enforced by construction — no AI, no inference):
  - No diagnosis, prognosis, or medical recommendation generated.
  - No patient history hallucinated — only fields explicitly captured at intake.
  - Urgency level is surfaced as-is from intake metadata, not escalated.
  - Doctor/staff approval is always required before any action is taken.
  - Output is a plain dict of factual fields only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _suggested_next_action(status: str, action_required: bool) -> str:
    """Map appointment request status to a plain-language staff action prompt."""
    if status == "new" and action_required:
        return "Review and confirm"
    if status == "callback_needed":
        return "Call patient"
    if status == "confirmed":
        return "Appointment confirmed — no further action needed"
    if status in ("rejected", "cancelled", "archived"):
        return "No action required"
    return "Review appointment request"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_pre_appointment_summary(
    appointment_request: Dict[str, Any],
    patient: Optional[Dict[str, Any]] = None,
    previous_request_count: int = 0,
) -> Dict[str, Any]:
    """
    Return a structured pre-appointment brief as a plain dict.

    Parameters
    ----------
    appointment_request:
        Row dict from appointment_requests table (must include at minimum:
        id, clinic_id, patient_name, status, action_required, source).
    patient:
        Row dict from patients table for the linked patient_id, or None
        if no patient is linked.
    previous_request_count:
        Number of prior appointment_requests for the same patient in this
        clinic, excluding the current request.

    Returns
    -------
    A dict containing only safe factual fields.  The dict never contains
    keys named "diagnosis", "medical_recommendation", "treatment",
    "prognosis", or any derivative of these terms.
    """
    patient_id = appointment_request.get("patient_id")
    patient_type = "returning" if patient_id is not None else "new"

    # Phone preference: linked patient row (more authoritative) → intake field
    if patient is not None:
        patient_phone = patient.get("phone") or appointment_request.get("patient_phone")
    else:
        patient_phone = appointment_request.get("patient_phone")

    status = str(appointment_request.get("status") or "")
    action_required = bool(appointment_request.get("action_required", False))

    preferred_starts_at = appointment_request.get("preferred_starts_at")
    preferred_ends_at = appointment_request.get("preferred_ends_at")

    return {
        "request_id":             str(appointment_request.get("id") or ""),
        "clinic_id":              str(appointment_request.get("clinic_id") or ""),
        "patient_name":           appointment_request.get("patient_name") or "",
        "patient_phone":          patient_phone,
        "patient_type":           patient_type,
        "previous_request_count": max(0, int(previous_request_count)),
        "reason":                 appointment_request.get("reason"),
        "preferred_starts_at":    str(preferred_starts_at) if preferred_starts_at is not None else None,
        "preferred_ends_at":      str(preferred_ends_at) if preferred_ends_at is not None else None,
        "source":                 str(appointment_request.get("source") or ""),
        "status":                 status,
        "action_required":        action_required,
        "urgency_level":          str(appointment_request.get("urgency_level") or "normal"),
        "suggested_next_action":  _suggested_next_action(status, action_required),
        "generated_at":           datetime.now(timezone.utc).isoformat(),
        "safety_note": (
            "This summary contains no medical advice or diagnosis. "
            "All actions require doctor or staff review and confirmation."
        ),
    }
