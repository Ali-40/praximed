"""
Patient History Service — PraxisMed Sprint 20 / Module 149.

Orchestrates FHIR-aligned patient history creation, retrieval, status updates,
and timeline assembly. Requires valid consent before any write.

No real patient PHI. No diagnosis generated. No medical advice. No triage scoring.
No deletion. Append-only/versioned. production_phi_enabled always False.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import patient_history_repo
from backend.app.db.repositories.patient_history_repo import (
    HISTORY_TYPE_TABLE,
    UnsupportedHistoryTypeError,
    InvalidPatientHistoryEntryError,
    PatientHistoryEntryNotFoundError,
)
from backend.app.services.consent_ledger import (
    assert_valid_consent_for_history_write,
    ConsentValidationError,
    ClinicNotFoundError,
)

logger = logging.getLogger(__name__)

_HISTORY_WRITE_PURPOSE = "patient_history_collection"


class PatientHistoryServiceError(RuntimeError):
    """Base error for patient history service."""


class PatientNotFoundError(PatientHistoryServiceError):
    """Raised when the patient does not exist or does not belong to the clinic."""


class AppointmentRequestNotFoundError(PatientHistoryServiceError):
    """Raised when the appointment request does not belong to the clinic."""


class HistoryEntryNotFoundError(PatientHistoryServiceError):
    """Raised when a requested history entry does not exist."""


async def _verify_clinic_exists(pool: Any, clinic_id: str) -> None:
    row = await pool.fetchrow("SELECT id FROM clinics WHERE id = $1::uuid", clinic_id)
    if row is None:
        raise ClinicNotFoundError(f"Clinic not found: {clinic_id!r}")


async def _verify_patient_belongs_to_clinic(
    pool: Any, clinic_id: str, patient_id: str
) -> None:
    row = await pool.fetchrow(
        "SELECT id FROM patients WHERE id = $1::uuid AND clinic_id = $2::uuid",
        patient_id, clinic_id,
    )
    if row is None:
        raise PatientNotFoundError(
            f"Patient {patient_id!r} not found or does not belong to clinic {clinic_id!r}"
        )


async def _verify_appt_request_belongs_to_clinic(
    pool: Any, clinic_id: str, appointment_request_id: str
) -> None:
    row = await pool.fetchrow(
        "SELECT id FROM appointment_requests WHERE id = $1::uuid AND clinic_id = $2::uuid",
        appointment_request_id, clinic_id,
    )
    if row is None:
        raise AppointmentRequestNotFoundError(
            f"Appointment request {appointment_request_id!r} not found or does not belong to clinic {clinic_id!r}"
        )


def _build_create_kwargs(payload: Dict[str, Any], actor_user: Optional[AuthContext]) -> Dict[str, Any]:
    kwargs = dict(payload)
    kwargs.pop("clinic_id", None)
    kwargs.pop("patient_id", None)
    kwargs.pop("consent_event_id", None)
    kwargs["entered_by_user_id"] = actor_user.user_id if actor_user else None
    return kwargs


_CREATE_FN = {
    "allergies":      patient_history_repo.create_allergy_history,
    "medications":    patient_history_repo.create_medication_history,
    "conditions":     patient_history_repo.create_condition_history,
    "procedures":     patient_history_repo.create_procedure_history,
    "immunizations":  patient_history_repo.create_immunization_history,
    "family-history": patient_history_repo.create_family_history,
    "social-history": patient_history_repo.create_social_history,
}

_PRIMARY_TEXT_FIELD = {
    "allergies":      "substance_text",
    "medications":    "medication_text",
    "conditions":     "condition_text",
    "procedures":     "procedure_text",
    "immunizations":  "vaccine_text",
    "family-history": "relationship_text",
    "social-history": "observation_category",
}


async def create_patient_history_entry(
    pool: Any,
    clinic_id: str,
    history_type: str,
    payload: Dict[str, Any],
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    if history_type not in HISTORY_TYPE_TABLE:
        raise UnsupportedHistoryTypeError(
            f"Unsupported history_type {history_type!r}."
        )

    await _verify_clinic_exists(pool, clinic_id)
    patient_id = payload["patient_id"]
    consent_event_id = payload["consent_event_id"]
    await _verify_patient_belongs_to_clinic(pool, clinic_id, patient_id)

    appt_req_id = payload.get("appointment_request_id")
    if appt_req_id:
        await _verify_appt_request_belongs_to_clinic(pool, clinic_id, appt_req_id)

    await assert_valid_consent_for_history_write(
        pool=pool,
        clinic_id=clinic_id,
        consent_event_id=consent_event_id,
        purpose=_HISTORY_WRITE_PURPOSE,
    )

    create_fn = _CREATE_FN[history_type]
    primary_field = _PRIMARY_TEXT_FIELD[history_type]
    primary_value = payload[primary_field]

    kwargs = _build_create_kwargs(payload, actor_user)
    kwargs.pop(primary_field, None)

    if history_type == "social-history":
        row = await create_fn(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            consent_event_id=consent_event_id,
            observation_category=primary_value,
            observation_text=payload["observation_text"],
            **{k: v for k, v in kwargs.items() if k not in ("observation_text",)},
        )
    else:
        row = await create_fn(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            consent_event_id=consent_event_id,
            **{primary_field: primary_value},
            **kwargs,
        )

    row["production_phi_enabled"] = False

    logger.info(
        "patient_history_created type=%s id=%s clinic_id=%s patient_id=%s actor=%s",
        history_type,
        row.get("id"),
        clinic_id,
        patient_id,
        actor_user.user_id if actor_user else "anonymous",
    )
    return row


async def list_patient_history(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    history_type: Optional[str] = None,
    status: Optional[str] = None,
    actor_user: Optional[AuthContext] = None,
) -> List[Dict[str, Any]]:
    await _verify_clinic_exists(pool, clinic_id)
    await _verify_patient_belongs_to_clinic(pool, clinic_id, patient_id)

    if history_type is not None:
        rows = await patient_history_repo.list_patient_history_by_type(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            history_type=history_type,
            status=status,
        )
    else:
        rows = await patient_history_repo.list_patient_history_timeline(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
        )

    for row in rows:
        row["production_phi_enabled"] = False
    return rows


async def get_patient_history_entry(
    pool: Any,
    clinic_id: str,
    history_type: str,
    entry_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Optional[Dict[str, Any]]:
    row = await patient_history_repo.get_history_entry_by_id(
        pool=pool,
        history_type=history_type,
        entry_id=entry_id,
    )
    if row is None:
        return None
    if str(row.get("clinic_id", "")) != str(clinic_id):
        return None
    row["production_phi_enabled"] = False
    return row


async def update_patient_history_status(
    pool: Any,
    clinic_id: str,
    history_type: str,
    entry_id: str,
    status: str,
    review_note: Optional[str] = None,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    existing = await patient_history_repo.get_history_entry_by_id(
        pool=pool,
        history_type=history_type,
        entry_id=entry_id,
    )
    if existing is None or str(existing.get("clinic_id", "")) != str(clinic_id):
        raise HistoryEntryNotFoundError(
            f"History entry {entry_id!r} not found for clinic {clinic_id!r}"
        )

    reviewed_by_user_id = actor_user.user_id if actor_user else None
    row = await patient_history_repo.update_history_entry_status(
        pool=pool,
        history_type=history_type,
        entry_id=entry_id,
        status=status,
        reviewed_by_user_id=reviewed_by_user_id,
        review_note=review_note,
    )
    if row is None:
        raise HistoryEntryNotFoundError(f"History entry {entry_id!r} not found")

    row["production_phi_enabled"] = False

    logger.info(
        "patient_history_status_updated type=%s id=%s status=%s actor=%s",
        history_type,
        entry_id,
        status,
        actor_user.user_id if actor_user else "anonymous",
    )
    return row


async def list_patient_history_timeline(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    actor_user: Optional[AuthContext] = None,
) -> List[Dict[str, Any]]:
    await _verify_clinic_exists(pool, clinic_id)
    await _verify_patient_belongs_to_clinic(pool, clinic_id, patient_id)
    rows = await patient_history_repo.list_patient_history_timeline(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
    )
    for row in rows:
        row["production_phi_enabled"] = False
    return rows
