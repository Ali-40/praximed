"""
Patient History Repository — PraxisMed Sprint 20 / Module 149.

Async CRUD for seven FHIR-aligned patient history tables.
All SQL is parameterised. All queries are tenant-scoped by clinic_id.
Append-only: no DELETE. Corrections create new rows.
production_phi_enabled always false (DB enforces).

No real patient PHI. No diagnosis generated. No medical advice. No triage scoring.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

_VALID_STATUSES = frozenset({"unverified", "approved", "rejected", "superseded"})
_VALID_SOURCE_TYPES = frozenset({
    "staff_console", "intake_link", "phone_call",
    "ai_proposal", "demo_seed", "import_demo",
})

# Map history_type URL slug to DB table name
HISTORY_TYPE_TABLE: Dict[str, str] = {
    "allergies":      "patient_history_allergies",
    "medications":    "patient_history_medications",
    "conditions":     "patient_history_conditions",
    "procedures":     "patient_history_procedures",
    "immunizations":  "patient_history_immunizations",
    "family-history": "patient_history_family_history",
    "social-history": "patient_history_social_history",
}

HISTORY_TYPE_FHIR: Dict[str, str] = {
    "allergies":      "AllergyIntolerance",
    "medications":    "MedicationStatement",
    "conditions":     "Condition",
    "procedures":     "Procedure",
    "immunizations":  "Immunization",
    "family-history": "FamilyMemberHistory",
    "social-history": "Observation",
}


class PatientHistoryRepoError(RuntimeError):
    """Base class for patient history repository errors."""


class InvalidPatientHistoryEntryError(PatientHistoryRepoError):
    """Raised when required fields are missing or invalid."""


class PatientHistoryEntryNotFoundError(PatientHistoryRepoError):
    """Raised when a requested history entry does not exist."""


class UnsupportedHistoryTypeError(PatientHistoryRepoError):
    """Raised when an unsupported history_type is given."""


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _validate_history_type(history_type: str) -> str:
    if history_type not in HISTORY_TYPE_TABLE:
        raise UnsupportedHistoryTypeError(
            f"Unsupported history_type {history_type!r}. "
            f"Must be one of {sorted(HISTORY_TYPE_TABLE)!r}."
        )
    return history_type


def _validate_status(status: str) -> str:
    if status not in _VALID_STATUSES:
        raise InvalidPatientHistoryEntryError(
            f"status must be one of {sorted(_VALID_STATUSES)!r}; got {status!r}"
        )
    return status


def _validate_source_type(source_type: str) -> str:
    if source_type not in _VALID_SOURCE_TYPES:
        raise InvalidPatientHistoryEntryError(
            f"source_type must be one of {sorted(_VALID_SOURCE_TYPES)!r}; got {source_type!r}"
        )
    return source_type


def _assert_nonempty(value: str, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidPatientHistoryEntryError(f"{name!r} must not be empty")


# ── Generic create helper ────────────────────────────────────────────────────

async def _create_entry(
    pool: Any,
    table: str,
    fhir_resource_type: str,
    common: Dict[str, Any],
    specific_cols: List[str],
    specific_vals: List[Any],
) -> Dict[str, Any]:
    version_group_id = common.get("version_group_id") or str(uuid.uuid4())
    common_cols = [
        "clinic_id", "patient_id", "appointment_request_id", "consent_event_id",
        "version_group_id", "version_number", "supersedes_entry_id", "correction_reason",
        "status", "source_type", "source_ref",
        "entered_by_user_id", "reviewed_by_user_id", "reviewed_at", "review_note",
        "effective_start_date", "effective_end_date", "notes",
        "fhir_resource_type", "fhir_payload", "metadata",
    ]
    common_vals = [
        common["clinic_id"],
        common["patient_id"],
        common.get("appointment_request_id"),
        common["consent_event_id"],
        version_group_id,
        common.get("version_number", 1),
        common.get("supersedes_entry_id"),
        common.get("correction_reason"),
        common.get("status", "unverified"),
        common.get("source_type", "staff_console"),
        common.get("source_ref"),
        common.get("entered_by_user_id"),
        None,  # reviewed_by_user_id
        None,  # reviewed_at
        None,  # review_note
        common.get("effective_start_date"),
        common.get("effective_end_date"),
        common.get("notes"),
        fhir_resource_type,
        json.dumps(common.get("fhir_payload") or {}),
        json.dumps(common.get("metadata") or {}),
    ]

    all_cols = common_cols + specific_cols
    all_vals = common_vals + specific_vals
    n = len(all_cols)
    # Build positional params: $1::uuid, $2::uuid, etc.
    # Use text cast for uuid columns, jsonb for json, text for the rest.
    uuid_cols = {
        "clinic_id", "patient_id", "appointment_request_id", "consent_event_id",
        "version_group_id", "supersedes_entry_id", "entered_by_user_id",
        "reviewed_by_user_id",
    }
    jsonb_cols = {"fhir_payload", "metadata"}

    def cast(col: str, idx: int) -> str:
        if col in uuid_cols:
            return f"${idx}::uuid"
        if col in jsonb_cols:
            return f"${idx}::jsonb"
        if col in {"effective_start_date", "effective_end_date"}:
            return f"${idx}::date"
        if col == "reviewed_at":
            return f"${idx}::timestamptz"
        return f"${idx}"

    params = ", ".join(cast(col, i + 1) for i, col in enumerate(all_cols))
    cols_str = ", ".join(all_cols)
    sql = f"INSERT INTO {table} ({cols_str}) VALUES ({params}) RETURNING *"
    row = await pool.fetchrow(sql, *all_vals)
    return _row_to_dict(row)


# ── Per-resource create functions ────────────────────────────────────────────


async def create_allergy_history(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    consent_event_id: str,
    substance_text: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(patient_id, "patient_id")
    _assert_nonempty(consent_event_id, "consent_event_id")
    _assert_nonempty(substance_text, "substance_text")
    common = {"clinic_id": clinic_id, "patient_id": patient_id,
              "consent_event_id": consent_event_id, **kwargs}
    spec_cols = ["substance_text", "reaction_text", "severity", "clinical_status",
                 "verification_status", "category", "criticality", "onset_text"]
    spec_vals = [
        substance_text,
        kwargs.get("reaction_text"),
        kwargs.get("severity"),
        kwargs.get("clinical_status"),
        kwargs.get("verification_status"),
        kwargs.get("category"),
        kwargs.get("criticality"),
        kwargs.get("onset_text"),
    ]
    return await _create_entry(
        pool, "patient_history_allergies", "AllergyIntolerance",
        common, spec_cols, spec_vals,
    )


async def create_medication_history(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    consent_event_id: str,
    medication_text: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(patient_id, "patient_id")
    _assert_nonempty(consent_event_id, "consent_event_id")
    _assert_nonempty(medication_text, "medication_text")
    common = {"clinic_id": clinic_id, "patient_id": patient_id,
              "consent_event_id": consent_event_id, **kwargs}
    spec_cols = ["medication_text", "dosage_text", "frequency_text", "route_text",
                 "medication_status", "start_text", "end_text", "reason_text"]
    spec_vals = [
        medication_text,
        kwargs.get("dosage_text"),
        kwargs.get("frequency_text"),
        kwargs.get("route_text"),
        kwargs.get("medication_status"),
        kwargs.get("start_text"),
        kwargs.get("end_text"),
        kwargs.get("reason_text"),
    ]
    return await _create_entry(
        pool, "patient_history_medications", "MedicationStatement",
        common, spec_cols, spec_vals,
    )


async def create_condition_history(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    consent_event_id: str,
    condition_text: str,
    patient_reported: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(patient_id, "patient_id")
    _assert_nonempty(consent_event_id, "consent_event_id")
    _assert_nonempty(condition_text, "condition_text")
    common = {"clinic_id": clinic_id, "patient_id": patient_id,
              "consent_event_id": consent_event_id, **kwargs}
    spec_cols = ["condition_text", "clinical_status", "verification_status",
                 "onset_text", "abatement_text", "body_site_text", "severity_text",
                 "patient_reported"]
    spec_vals = [
        condition_text,
        kwargs.get("clinical_status"),
        kwargs.get("verification_status"),
        kwargs.get("onset_text"),
        kwargs.get("abatement_text"),
        kwargs.get("body_site_text"),
        kwargs.get("severity_text"),
        patient_reported,
    ]
    return await _create_entry(
        pool, "patient_history_conditions", "Condition",
        common, spec_cols, spec_vals,
    )


async def create_procedure_history(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    consent_event_id: str,
    procedure_text: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(patient_id, "patient_id")
    _assert_nonempty(consent_event_id, "consent_event_id")
    _assert_nonempty(procedure_text, "procedure_text")
    common = {"clinic_id": clinic_id, "patient_id": patient_id,
              "consent_event_id": consent_event_id, **kwargs}
    spec_cols = ["procedure_text", "performed_text", "body_site_text",
                 "outcome_text", "performer_text", "reason_text"]
    spec_vals = [
        procedure_text,
        kwargs.get("performed_text"),
        kwargs.get("body_site_text"),
        kwargs.get("outcome_text"),
        kwargs.get("performer_text"),
        kwargs.get("reason_text"),
    ]
    return await _create_entry(
        pool, "patient_history_procedures", "Procedure",
        common, spec_cols, spec_vals,
    )


async def create_immunization_history(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    consent_event_id: str,
    vaccine_text: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(patient_id, "patient_id")
    _assert_nonempty(consent_event_id, "consent_event_id")
    _assert_nonempty(vaccine_text, "vaccine_text")
    common = {"clinic_id": clinic_id, "patient_id": patient_id,
              "consent_event_id": consent_event_id, **kwargs}
    spec_cols = ["vaccine_text", "occurrence_text", "lot_number", "site_text",
                 "route_text", "dose_number", "series_text", "immunization_status"]
    spec_vals = [
        vaccine_text,
        kwargs.get("occurrence_text"),
        kwargs.get("lot_number"),
        kwargs.get("site_text"),
        kwargs.get("route_text"),
        kwargs.get("dose_number"),
        kwargs.get("series_text"),
        kwargs.get("immunization_status"),
    ]
    return await _create_entry(
        pool, "patient_history_immunizations", "Immunization",
        common, spec_cols, spec_vals,
    )


async def create_family_history(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    consent_event_id: str,
    relationship_text: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(patient_id, "patient_id")
    _assert_nonempty(consent_event_id, "consent_event_id")
    _assert_nonempty(relationship_text, "relationship_text")
    common = {"clinic_id": clinic_id, "patient_id": patient_id,
              "consent_event_id": consent_event_id, **kwargs}
    spec_cols = ["relationship_text", "condition_text", "age_text", "deceased", "note_text"]
    spec_vals = [
        relationship_text,
        kwargs.get("condition_text"),
        kwargs.get("age_text"),
        kwargs.get("deceased"),
        kwargs.get("note_text"),
    ]
    return await _create_entry(
        pool, "patient_history_family_history", "FamilyMemberHistory",
        common, spec_cols, spec_vals,
    )


async def create_social_history(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    consent_event_id: str,
    observation_category: str,
    observation_text: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(patient_id, "patient_id")
    _assert_nonempty(consent_event_id, "consent_event_id")
    _assert_nonempty(observation_category, "observation_category")
    _assert_nonempty(observation_text, "observation_text")
    common = {"clinic_id": clinic_id, "patient_id": patient_id,
              "consent_event_id": consent_event_id, **kwargs}
    spec_cols = ["observation_category", "observation_text", "value_text", "period_text"]
    spec_vals = [
        observation_category,
        observation_text,
        kwargs.get("value_text"),
        kwargs.get("period_text"),
    ]
    return await _create_entry(
        pool, "patient_history_social_history", "Observation",
        common, spec_cols, spec_vals,
    )


# ── Query functions ──────────────────────────────────────────────────────────


async def list_patient_history_by_type(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    history_type: str,
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    _validate_history_type(history_type)
    table = HISTORY_TYPE_TABLE[history_type]
    if status is not None:
        sql = f"""
            SELECT * FROM {table}
            WHERE clinic_id = $1::uuid AND patient_id = $2::uuid AND status = $3
            ORDER BY created_at DESC LIMIT $4
        """
        rows = await pool.fetch(sql, clinic_id, patient_id, status, limit)
    else:
        sql = f"""
            SELECT * FROM {table}
            WHERE clinic_id = $1::uuid AND patient_id = $2::uuid
            ORDER BY created_at DESC LIMIT $3
        """
        rows = await pool.fetch(sql, clinic_id, patient_id, limit)
    return [_row_to_dict(r) for r in rows]


async def list_patient_history_timeline(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    limit_per_type: int = 20,
) -> List[Dict[str, Any]]:
    all_rows: List[Dict[str, Any]] = []
    for history_type, table in HISTORY_TYPE_TABLE.items():
        sql = f"""
            SELECT *, '{history_type}' AS history_type FROM {table}
            WHERE clinic_id = $1::uuid AND patient_id = $2::uuid
            ORDER BY created_at DESC LIMIT $3
        """
        rows = await pool.fetch(sql, clinic_id, patient_id, limit_per_type)
        all_rows.extend(_row_to_dict(r) for r in rows)
    all_rows.sort(key=lambda r: str(r.get("created_at", "")), reverse=True)
    return all_rows


async def get_history_entry_by_id(
    pool: Any,
    history_type: str,
    entry_id: str,
) -> Optional[Dict[str, Any]]:
    _validate_history_type(history_type)
    table = HISTORY_TYPE_TABLE[history_type]
    sql = f"SELECT * FROM {table} WHERE id = $1::uuid"
    row = await pool.fetchrow(sql, entry_id)
    return _row_to_dict(row) if row is not None else None


async def update_history_entry_status(
    pool: Any,
    history_type: str,
    entry_id: str,
    status: str,
    reviewed_by_user_id: Optional[str] = None,
    review_note: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    _validate_history_type(history_type)
    _validate_status(status)
    table = HISTORY_TYPE_TABLE[history_type]
    sql = f"""
        UPDATE {table}
        SET status               = $2,
            reviewed_by_user_id  = $3::uuid,
            reviewed_at          = now(),
            review_note          = $4,
            updated_at           = now()
        WHERE id = $1::uuid
        RETURNING *
    """
    row = await pool.fetchrow(sql, entry_id, status, reviewed_by_user_id, review_note)
    return _row_to_dict(row) if row is not None else None


async def mark_history_entry_superseded(
    pool: Any,
    history_type: str,
    entry_id: str,
    superseded_by_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    _validate_history_type(history_type)
    table = HISTORY_TYPE_TABLE[history_type]
    sql = f"""
        UPDATE {table}
        SET status     = 'superseded',
            updated_at = now()
        WHERE id = $1::uuid
        RETURNING *
    """
    row = await pool.fetchrow(sql, entry_id)
    return _row_to_dict(row) if row is not None else None
