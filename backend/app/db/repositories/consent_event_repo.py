"""
Consent Event Repository — PraxisMed Sprint 20 / Module 148.

Async CRUD for consent_events. All SQL is parameterised.
Tenant-scoped: all queries include clinic_id.
Append-only: revocation uses revoked_at marker; no DELETE.
No real patient PHI stored. No diagnosis. No medical advice.
production_phi_enabled always false. Production PHI remains NO-GO.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

_VALID_CHANNELS = frozenset({
    "onboarding_form",
    "intake_link",
    "phone_call",
    "staff_console",
    "developer_console",
    "import_demo",
})
_VALID_LANGUAGES = frozenset({"de", "en", "ar"})
_VALID_PURPOSES = frozenset({
    "appointment_intake",
    "patient_history_collection",
    "phone_history_questions",
    "demo_seed",
    "data_processing_acknowledgement",
})


class ConsentEventRepoError(RuntimeError):
    """Base class for consent event repository errors."""


class InvalidConsentEventError(ConsentEventRepoError):
    """Raised when required fields are missing or values are invalid."""


class ConsentEventNotFoundError(ConsentEventRepoError):
    """Raised when a requested consent event does not exist."""


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _assert_nonempty(value: str, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidConsentEventError(f"{name!r} must not be empty")


def _assert_valid_enum(value: str, name: str, valid: frozenset) -> None:
    if value not in valid:
        raise InvalidConsentEventError(
            f"{name!r} must be one of {sorted(valid)!r}; got {value!r}"
        )


async def create_consent_event(
    pool: Any,
    clinic_id: str,
    purpose: str,
    scope: str,
    channel: str,
    consent_text_version: str,
    consent_text_snapshot: str,
    language: str = "de",
    patient_id: Optional[str] = None,
    appointment_request_id: Optional[str] = None,
    consent_subject_type: str = "patient",
    consent_subject_ref: Optional[str] = None,
    granted: bool = True,
    captured_by_user_id: Optional[str] = None,
    captured_by_system: Optional[str] = None,
    source_ip_hash: Optional[str] = None,
    user_agent_hash: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(purpose, "purpose")
    _assert_nonempty(scope, "scope")
    _assert_nonempty(consent_text_version, "consent_text_version")
    _assert_nonempty(consent_text_snapshot, "consent_text_snapshot")
    _assert_valid_enum(channel, "channel", _VALID_CHANNELS)
    _assert_valid_enum(language, "language", _VALID_LANGUAGES)
    _assert_valid_enum(purpose, "purpose", _VALID_PURPOSES)

    import json
    metadata_json = json.dumps(metadata or {})

    sql = """
        INSERT INTO consent_events (
            clinic_id, patient_id, appointment_request_id,
            consent_subject_type, consent_subject_ref,
            purpose, scope, channel, language,
            consent_text_version, consent_text_snapshot,
            granted,
            captured_by_user_id, captured_by_system,
            source_ip_hash, user_agent_hash,
            metadata, production_phi_enabled
        ) VALUES (
            $1::uuid, $2::uuid, $3::uuid,
            $4, $5,
            $6, $7, $8, $9,
            $10, $11,
            $12,
            $13::uuid, $14,
            $15, $16,
            $17::jsonb, false
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id,
        patient_id,
        appointment_request_id,
        consent_subject_type,
        consent_subject_ref,
        purpose,
        scope,
        channel,
        language,
        consent_text_version,
        consent_text_snapshot,
        granted,
        captured_by_user_id,
        captured_by_system,
        source_ip_hash,
        user_agent_hash,
        metadata_json,
    )
    return _row_to_dict(row)


async def get_consent_event_by_id(
    pool: Any,
    event_id: str,
) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM consent_events WHERE id = $1::uuid"
    row = await pool.fetchrow(sql, event_id)
    return _row_to_dict(row) if row is not None else None


async def list_consent_events_for_clinic(
    pool: Any,
    clinic_id: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if limit < 1 or limit > 200:
        raise InvalidConsentEventError("limit must be between 1 and 200")
    sql = """
        SELECT * FROM consent_events
        WHERE clinic_id = $1::uuid
        ORDER BY created_at DESC
        LIMIT $2
    """
    rows = await pool.fetch(sql, clinic_id, limit)
    return [_row_to_dict(r) for r in rows]


async def list_consent_events_for_patient(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if limit < 1 or limit > 200:
        raise InvalidConsentEventError("limit must be between 1 and 200")
    sql = """
        SELECT * FROM consent_events
        WHERE clinic_id = $1::uuid
          AND patient_id = $2::uuid
        ORDER BY created_at DESC
        LIMIT $3
    """
    rows = await pool.fetch(sql, clinic_id, patient_id, limit)
    return [_row_to_dict(r) for r in rows]


async def revoke_consent_event(
    pool: Any,
    event_id: str,
    revoked_by_user_id: Optional[str] = None,
    revocation_reason: Optional[str] = None,
    revoked_at: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE consent_events
        SET revoked_at          = COALESCE($2::timestamptz, now()),
            revoked_by_user_id  = $3::uuid,
            revocation_reason   = $4,
            updated_at          = now()
        WHERE id = $1::uuid
        RETURNING *
    """
    row = await pool.fetchrow(sql, event_id, revoked_at, revoked_by_user_id, revocation_reason)
    return _row_to_dict(row) if row is not None else None


async def has_valid_consent_for_purpose(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    purpose: str,
) -> bool:
    """Return True if a granted, non-revoked consent event exists for this patient+purpose+clinic."""
    sql = """
        SELECT EXISTS (
            SELECT 1 FROM consent_events
            WHERE clinic_id  = $1::uuid
              AND patient_id = $2::uuid
              AND purpose    = $3
              AND granted    = true
              AND revoked_at IS NULL
        )
    """
    result = await pool.fetchval(sql, clinic_id, patient_id, purpose)
    return bool(result)
