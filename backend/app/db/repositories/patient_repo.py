"""
Patient Repository — PraxisMed Sprint 2 / Module 25

Provides async CRUD operations for the ``patients`` table.
All SQL is parameterised ($1, $2, …) — no string interpolation.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PatientRepoError(RuntimeError):
    """Base class for patient repository errors."""


class InvalidPatientError(PatientRepoError):
    """Raised when required fields are missing or values are invalid."""


# ---------------------------------------------------------------------------
# Allowed enum values
# ---------------------------------------------------------------------------

_VALID_STATUSES = frozenset({"active", "inactive", "archived"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _assert_nonempty(value: Any, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidPatientError(f"{name!r} must not be empty")


def _assert_valid_status(value: str) -> None:
    if value not in _VALID_STATUSES:
        raise InvalidPatientError(
            f"'status' must be one of {sorted(_VALID_STATUSES)!r}; got {value!r}"
        )


# ---------------------------------------------------------------------------
# 1. create_patient
# ---------------------------------------------------------------------------


async def create_patient(
    pool: Any,
    clinic_id: str,
    full_name: str,
    external_patient_id: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    preferred_language: str = "de-AT",
    status: str = "active",
    notes: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(full_name, "full_name")
    _assert_nonempty(preferred_language, "preferred_language")
    _assert_valid_status(status)

    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    sql = """
        INSERT INTO patients (
            clinic_id, external_patient_id, full_name,
            date_of_birth, phone, email,
            preferred_language, status, notes, raw_payload
        ) VALUES (
            $1, $2, $3,
            $4, $5, $6,
            $7, $8, $9, $10::jsonb
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id, external_patient_id, full_name,
        date_of_birth, phone, email,
        preferred_language, status, notes, raw_payload_json,
    )
    return _row_to_dict(row)


# ---------------------------------------------------------------------------
# 2. upsert_patient_by_external_id
# ---------------------------------------------------------------------------


async def upsert_patient_by_external_id(
    pool: Any,
    clinic_id: str,
    external_patient_id: str,
    full_name: str,
    date_of_birth: Optional[date] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    preferred_language: str = "de-AT",
    status: str = "active",
    notes: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(external_patient_id, "external_patient_id")
    _assert_nonempty(full_name, "full_name")
    _assert_nonempty(preferred_language, "preferred_language")
    _assert_valid_status(status)

    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    sql = """
        INSERT INTO patients (
            clinic_id, external_patient_id, full_name,
            date_of_birth, phone, email,
            preferred_language, status, notes, raw_payload
        ) VALUES (
            $1, $2, $3,
            $4, $5, $6,
            $7, $8, $9, $10::jsonb
        )
        ON CONFLICT (clinic_id, external_patient_id) DO UPDATE
            SET full_name          = EXCLUDED.full_name,
                date_of_birth      = EXCLUDED.date_of_birth,
                phone              = EXCLUDED.phone,
                email              = EXCLUDED.email,
                preferred_language = EXCLUDED.preferred_language,
                status             = EXCLUDED.status,
                notes              = EXCLUDED.notes,
                raw_payload        = EXCLUDED.raw_payload,
                updated_at         = now()
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id, external_patient_id, full_name,
        date_of_birth, phone, email,
        preferred_language, status, notes, raw_payload_json,
    )
    return _row_to_dict(row)


# ---------------------------------------------------------------------------
# 3. get_patient_by_id
# ---------------------------------------------------------------------------


async def get_patient_by_id(
    pool: Any,
    clinic_id: str,
    patient_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT *
        FROM patients
        WHERE clinic_id = $1
          AND id        = $2
    """
    row = await pool.fetchrow(sql, clinic_id, patient_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 4. get_patient_by_external_id
# ---------------------------------------------------------------------------


async def get_patient_by_external_id(
    pool: Any,
    clinic_id: str,
    external_patient_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT *
        FROM patients
        WHERE clinic_id            = $1
          AND external_patient_id  = $2
    """
    row = await pool.fetchrow(sql, clinic_id, external_patient_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 5. list_patients
# ---------------------------------------------------------------------------


async def list_patients(
    pool: Any,
    clinic_id: str,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if limit < 1 or limit > 100:
        raise InvalidPatientError("limit must be between 1 and 100")
    if status is not None:
        _assert_valid_status(status)

    sql = """
        SELECT *
        FROM patients
        WHERE clinic_id = $1
          AND ($2::text IS NULL OR status = $2)
          AND (
              $3::text IS NULL
              OR full_name            ILIKE '%' || $3 || '%'
              OR phone                ILIKE '%' || $3 || '%'
              OR email                ILIKE '%' || $3 || '%'
              OR external_patient_id  ILIKE '%' || $3 || '%'
          )
        ORDER BY created_at DESC
        LIMIT $4
    """
    rows = await pool.fetch(sql, clinic_id, status, search, limit)
    return [_row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# 6. update_patient
# ---------------------------------------------------------------------------


async def update_patient(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    full_name: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    preferred_language: Optional[str] = None,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    # Require at least one field to update (date_of_birth, phone, email, notes,
    # raw_payload are nullable so any explicit pass counts as an update intent)
    update_fields = {
        "full_name": full_name,
        "date_of_birth": date_of_birth,
        "phone": phone,
        "email": email,
        "preferred_language": preferred_language,
        "status": status,
        "notes": notes,
        "raw_payload": raw_payload,
    }
    if all(v is None for v in update_fields.values()):
        raise InvalidPatientError("At least one update field must be provided")

    if full_name is not None:
        _assert_nonempty(full_name, "full_name")
    if preferred_language is not None:
        _assert_nonempty(preferred_language, "preferred_language")
    if status is not None:
        _assert_valid_status(status)

    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    sql = """
        UPDATE patients
        SET full_name          = COALESCE($1, full_name),
            date_of_birth      = COALESCE($2, date_of_birth),
            phone              = COALESCE($3, phone),
            email              = COALESCE($4, email),
            preferred_language = COALESCE($5, preferred_language),
            status             = COALESCE($6, status),
            notes              = COALESCE($7, notes),
            raw_payload        = COALESCE($8::jsonb, raw_payload),
            updated_at         = now()
        WHERE clinic_id = $9
          AND id         = $10
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        full_name, date_of_birth, phone, email,
        preferred_language, status, notes, raw_payload_json,
        clinic_id, patient_id,
    )
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 7. archive_patient
# ---------------------------------------------------------------------------


async def find_or_create_patient_from_vapi(
    pool: Any,
    clinic_id: str,
    full_name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    date_of_birth: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Return an existing patient matched by phone within this clinic, or create one.

    Matching strategy (in order):
    1. If phone is provided: match on (clinic_id, normalized_phone). Returns the
       earliest-created matching patient. Tenant isolation is enforced — matching
       is always scoped by clinic_id so the same phone number in two different
       clinics resolves to two separate patient records.
    2. If no phone, or no match found: create a new patient row.

    Phone normalization: leading/trailing whitespace is stripped; E.164 format
    (e.g. "+43123456789") is preserved as-is.

    Callers should not rely on name deduplication — if two Vapi calls provide
    the same name but different (or no) phone numbers, two patient rows are
    created. Name-based deduplication requires human review.
    """
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(full_name, "full_name")

    normalized_phone: Optional[str] = phone.strip() if phone and phone.strip() else None

    if normalized_phone:
        sql = """
            SELECT *
            FROM patients
            WHERE clinic_id = $1
              AND phone     = $2
            ORDER BY created_at ASC
            LIMIT 1
        """
        row = await pool.fetchrow(sql, clinic_id, normalized_phone)
        if row is not None:
            return _row_to_dict(row)

    return await create_patient(
        pool=pool,
        clinic_id=clinic_id,
        full_name=full_name,
        phone=normalized_phone,
        email=email,
        date_of_birth=date_of_birth,
    )


async def archive_patient(
    pool: Any,
    clinic_id: str,
    patient_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE patients
        SET status     = 'archived',
            updated_at = now()
        WHERE clinic_id = $1
          AND id        = $2
        RETURNING *
    """
    row = await pool.fetchrow(sql, clinic_id, patient_id)
    return _row_to_dict(row) if row is not None else None
