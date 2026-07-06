"""
Clinic Onboarding Request Repository — PraxisMed Sprint 19 / Module 132.

Async CRUD for clinic_onboarding_requests. All SQL is parameterised.
No real tenant is created. No patient PHI. production_phi_enabled always false.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


_VALID_LANGUAGES = frozenset({"de", "en"})
_VALID_STATUSES = frozenset({"submitted", "reviewed", "demo_booked", "pilot_approved", "rejected", "archived"})


class ClinicOnboardingRepoError(RuntimeError):
    """Base class for clinic onboarding repository errors."""


class InvalidClinicOnboardingRequestError(ClinicOnboardingRepoError):
    """Raised when required fields are missing or values are invalid."""


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _assert_nonempty(value: str, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidClinicOnboardingRequestError(f"{name!r} must not be empty")


def _assert_valid_enum(value: str, name: str, valid: frozenset) -> None:
    if value not in valid:
        raise InvalidClinicOnboardingRequestError(
            f"{name!r} must be one of {sorted(valid)!r}; got {value!r}"
        )


async def create_clinic_onboarding_request(
    pool: Any,
    clinic_name: str,
    doctor_name: str,
    contact_email: str,
    consent_pilot_contact: bool,
    acknowledges_no_phi: bool,
    clinic_type: Optional[str] = None,
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    address: Optional[str] = None,
    website: Optional[str] = None,
    contact_phone: Optional[str] = None,
    preferred_language: str = "de",
    fallback_language: str = "en",
    supported_languages: Optional[List[str]] = None,
    workflow_notes: Optional[str] = None,
    estimated_call_volume: Optional[str] = None,
    current_booking_system: Optional[str] = None,
    wants_ai_phone_intake: bool = True,
    wants_dashboard: bool = True,
    wants_notifications: bool = False,
    pilot_interest_level: str = "new",
    source: str = "onboarding_page",
) -> Dict[str, Any]:
    _assert_nonempty(clinic_name, "clinic_name")
    _assert_nonempty(doctor_name, "doctor_name")
    _assert_nonempty(contact_email, "contact_email")
    _assert_valid_enum(preferred_language, "preferred_language", _VALID_LANGUAGES)
    _assert_valid_enum(fallback_language, "fallback_language", _VALID_LANGUAGES)

    if not consent_pilot_contact:
        raise InvalidClinicOnboardingRequestError("consent_pilot_contact must be true")
    if not acknowledges_no_phi:
        raise InvalidClinicOnboardingRequestError("acknowledges_no_phi must be true")

    langs = supported_languages if supported_languages is not None else ["de", "en"]
    supported_languages_json = json.dumps(langs)

    sql = """
        INSERT INTO clinic_onboarding_requests (
            clinic_name, clinic_type, specialty, city, address, website,
            doctor_name, contact_email, contact_phone,
            preferred_language, fallback_language, supported_languages,
            workflow_notes, estimated_call_volume, current_booking_system,
            wants_ai_phone_intake, wants_dashboard, wants_notifications,
            pilot_interest_level, status, source,
            consent_pilot_contact, acknowledges_no_phi,
            production_phi_enabled
        ) VALUES (
            $1,  $2,  $3,  $4,  $5,  $6,
            $7,  $8,  $9,
            $10, $11, $12::jsonb,
            $13, $14, $15,
            $16, $17, $18,
            $19, 'submitted', $20,
            $21, $22,
            false
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_name, clinic_type, specialty, city, address, website,
        doctor_name, contact_email, contact_phone,
        preferred_language, fallback_language, supported_languages_json,
        workflow_notes, estimated_call_volume, current_booking_system,
        wants_ai_phone_intake, wants_dashboard, wants_notifications,
        pilot_interest_level, source,
        consent_pilot_contact, acknowledges_no_phi,
    )
    return _row_to_dict(row)


async def get_clinic_onboarding_request_by_id(
    pool: Any,
    request_id: str,
) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM clinic_onboarding_requests WHERE id = $1"
    row = await pool.fetchrow(sql, request_id)
    return _row_to_dict(row) if row is not None else None


async def list_clinic_onboarding_requests(
    pool: Any,
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if limit < 1 or limit > 200:
        raise InvalidClinicOnboardingRequestError("limit must be between 1 and 200")

    sql = """
        SELECT * FROM clinic_onboarding_requests
        WHERE ($1::text IS NULL OR status = $1)
        ORDER BY created_at DESC
        LIMIT $2
    """
    rows = await pool.fetch(sql, status, limit)
    return [_row_to_dict(r) for r in rows]


async def update_clinic_onboarding_status(
    pool: Any,
    request_id: str,
    status: str,
    reviewer_notes: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    _assert_valid_enum(status, "status", _VALID_STATUSES)

    sql = """
        UPDATE clinic_onboarding_requests
        SET status     = $1,
            updated_at = now()
        WHERE id = $2
        RETURNING *
    """
    row = await pool.fetchrow(sql, status, request_id)
    return _row_to_dict(row) if row is not None else None
