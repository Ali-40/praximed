"""
Consent Ledger Service — PraxisMed Sprint 20 / Module 148.

Orchestrates consent event creation, retrieval, revocation, and the
assert_valid_consent_for_history_write gate.

No real patient PHI stored beyond what is in patients table.
No diagnosis. No medical advice. No triage scoring. No live external calls.
production_phi_enabled always False. Synthetic/fake staging only.
Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import consent_event_repo
from backend.app.db.repositories.consent_event_repo import (
    ConsentEventNotFoundError,
    InvalidConsentEventError,
)
from backend.app.schemas.consent_event import ConsentEventCreate, ConsentEventRevoke

logger = logging.getLogger(__name__)

_HISTORY_WRITE_PURPOSES = frozenset({
    "patient_history_collection",
    "phone_history_questions",
})


class ConsentLedgerError(RuntimeError):
    """Base error for consent ledger service."""


class ClinicNotFoundError(ConsentLedgerError):
    """Raised when the target clinic does not exist."""


class PatientNotFoundError(ConsentLedgerError):
    """Raised when the target patient does not exist or does not belong to the clinic."""


class AppointmentRequestNotFoundError(ConsentLedgerError):
    """Raised when the target appointment request does not exist or does not belong to the clinic."""


class ConsentValidationError(ConsentLedgerError):
    """Raised when a history write consent gate check fails."""


async def _verify_clinic_exists(pool: Any, clinic_id: str) -> None:
    row = await pool.fetchrow(
        "SELECT id FROM clinics WHERE id = $1::uuid", clinic_id
    )
    if row is None:
        raise ClinicNotFoundError(f"Clinic not found: {clinic_id!r}")


async def _verify_patient_belongs_to_clinic(
    pool: Any, clinic_id: str, patient_id: str
) -> None:
    row = await pool.fetchrow(
        "SELECT id FROM patients WHERE id = $1::uuid AND clinic_id = $2::uuid",
        patient_id,
        clinic_id,
    )
    if row is None:
        raise PatientNotFoundError(
            f"Patient {patient_id!r} not found or does not belong to clinic {clinic_id!r}"
        )


async def _verify_appointment_request_belongs_to_clinic(
    pool: Any, clinic_id: str, appointment_request_id: str
) -> None:
    row = await pool.fetchrow(
        "SELECT id FROM appointment_requests WHERE id = $1::uuid AND clinic_id = $2::uuid",
        appointment_request_id,
        clinic_id,
    )
    if row is None:
        raise AppointmentRequestNotFoundError(
            f"Appointment request {appointment_request_id!r} not found or does not belong to clinic {clinic_id!r}"
        )


async def create_consent_event(
    pool: Any,
    payload: ConsentEventCreate,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    await _verify_clinic_exists(pool, payload.clinic_id)

    if payload.patient_id:
        await _verify_patient_belongs_to_clinic(pool, payload.clinic_id, payload.patient_id)

    if payload.appointment_request_id:
        await _verify_appointment_request_belongs_to_clinic(
            pool, payload.clinic_id, payload.appointment_request_id
        )

    row = await consent_event_repo.create_consent_event(
        pool=pool,
        clinic_id=payload.clinic_id,
        patient_id=payload.patient_id,
        appointment_request_id=payload.appointment_request_id,
        consent_subject_type=payload.consent_subject_type,
        consent_subject_ref=payload.consent_subject_ref,
        purpose=payload.purpose,
        scope=payload.scope,
        channel=payload.channel,
        language=payload.language,
        consent_text_version=payload.consent_text_version,
        consent_text_snapshot=payload.consent_text_snapshot,
        granted=payload.granted,
        captured_by_user_id=actor_user.user_id if actor_user else None,
        captured_by_system=payload.captured_by_system,
        metadata=payload.metadata,
    )

    logger.info(
        "consent_event_created event_id=%s clinic_id=%s purpose=%s channel=%s language=%s actor=%s",
        row.get("id"),
        payload.clinic_id,
        payload.purpose,
        payload.channel,
        payload.language,
        actor_user.user_id if actor_user else "anonymous",
    )

    row["production_phi_enabled"] = False
    return row


async def get_consent_event(
    pool: Any,
    event_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Optional[Dict[str, Any]]:
    row = await consent_event_repo.get_consent_event_by_id(pool=pool, event_id=event_id)
    if row is not None:
        row["production_phi_enabled"] = False
    return row


async def list_clinic_consent_events(
    pool: Any,
    clinic_id: str,
    actor_user: Optional[AuthContext] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    await _verify_clinic_exists(pool, clinic_id)
    rows = await consent_event_repo.list_consent_events_for_clinic(
        pool=pool, clinic_id=clinic_id, limit=limit
    )
    for row in rows:
        row["production_phi_enabled"] = False
    return rows


async def revoke_consent_event(
    pool: Any,
    event_id: str,
    payload: ConsentEventRevoke,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    row = await consent_event_repo.revoke_consent_event(
        pool=pool,
        event_id=event_id,
        revoked_by_user_id=actor_user.user_id if actor_user else None,
        revocation_reason=payload.revocation_reason,
        revoked_at=payload.revoked_at,
    )
    if row is None:
        raise ConsentEventNotFoundError(f"Consent event not found: {event_id!r}")

    logger.info(
        "consent_event_revoked event_id=%s actor=%s reason=%s",
        event_id,
        actor_user.user_id if actor_user else "anonymous",
        payload.revocation_reason,
    )

    row["production_phi_enabled"] = False
    return row


async def assert_valid_consent_for_history_write(
    pool: Any,
    clinic_id: str,
    consent_event_id: str,
    purpose: str,
) -> None:
    """Gate check: raise ConsentValidationError if the consent is not valid for a history write.

    Requirements:
    - consent event exists
    - same clinic_id
    - granted is True
    - revoked_at is None
    - purpose is patient_history_collection or phone_history_questions
    - production_phi_enabled is False
    """
    if purpose not in _HISTORY_WRITE_PURPOSES:
        raise ConsentValidationError(
            f"purpose {purpose!r} is not valid for a history write. "
            f"Must be one of {sorted(_HISTORY_WRITE_PURPOSES)!r}."
        )

    row = await consent_event_repo.get_consent_event_by_id(pool=pool, event_id=consent_event_id)
    if row is None:
        raise ConsentValidationError(
            f"Consent event not found: {consent_event_id!r}"
        )

    if str(row.get("clinic_id", "")) != str(clinic_id):
        raise ConsentValidationError(
            f"Consent event {consent_event_id!r} does not belong to clinic {clinic_id!r}"
        )

    if not row.get("granted"):
        raise ConsentValidationError(
            f"Consent event {consent_event_id!r} is not granted"
        )

    if row.get("revoked_at") is not None:
        raise ConsentValidationError(
            f"Consent event {consent_event_id!r} has been revoked"
        )

    if row.get("production_phi_enabled"):
        raise ConsentValidationError(
            "production_phi_enabled must be False — production PHI is NO-GO"
        )
