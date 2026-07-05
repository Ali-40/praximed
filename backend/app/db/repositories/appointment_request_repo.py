"""
Appointment Request Repository — PraxisMed Sprint 1 / Module 16

Provides async CRUD operations for the ``appointment_requests`` table.
All SQL is parameterised ($1, $2, …) — no string interpolation.
Direct SQL lives only in this module; callers receive plain dicts.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class AppointmentRequestRepoError(RuntimeError):
    """Base class for appointment request repository errors."""


class InvalidAppointmentRequestError(AppointmentRequestRepoError):
    """Raised when required fields are missing or values are invalid."""


# ---------------------------------------------------------------------------
# Allowed enum values
# ---------------------------------------------------------------------------

_VALID_SOURCES = frozenset({"vapi", "whatsapp", "web", "staff", "system"})
_VALID_STATUSES = frozenset({"new", "confirmed", "rejected", "callback_needed", "cancelled", "archived"})
_VALID_URGENCY_LEVELS = frozenset({"low", "normal", "urgent", "emergency"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _assert_nonempty(value: str, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidAppointmentRequestError(f"{name!r} must not be empty")


def _assert_valid_enum(value: str, name: str, valid: frozenset) -> None:
    if value not in valid:
        raise InvalidAppointmentRequestError(
            f"{name!r} must be one of {sorted(valid)!r}; got {value!r}"
        )


# ---------------------------------------------------------------------------
# 1. create_appointment_request
# ---------------------------------------------------------------------------


async def create_appointment_request(
    pool: Any,
    clinic_id: str,
    source: str,
    patient_name: str,
    source_ref: Optional[str] = None,
    patient_phone: Optional[str] = None,
    patient_email: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    reason: Optional[str] = None,
    preferred_starts_at: Optional[datetime] = None,
    preferred_ends_at: Optional[datetime] = None,
    status: str = "new",
    urgency_level: str = "normal",
    action_required: bool = True,
    assigned_user_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Insert a new appointment request row.

    Validates all enum fields and the preferred time range before
    touching the database.  Returns the inserted row as a dict.
    """
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(source, "source")
    _assert_nonempty(patient_name, "patient_name")
    _assert_valid_enum(source, "source", _VALID_SOURCES)
    _assert_valid_enum(status, "status", _VALID_STATUSES)
    _assert_valid_enum(urgency_level, "urgency_level", _VALID_URGENCY_LEVELS)

    if preferred_starts_at is not None and preferred_ends_at is not None:
        if preferred_ends_at <= preferred_starts_at:
            raise InvalidAppointmentRequestError(
                "preferred_ends_at must be strictly after preferred_starts_at"
            )

    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    sql = """
        INSERT INTO appointment_requests (
            clinic_id, source, source_ref, patient_name, patient_phone,
            patient_email, date_of_birth, reason,
            preferred_starts_at, preferred_ends_at,
            status, urgency_level, action_required,
            assigned_user_id, patient_id, raw_payload
        ) VALUES (
            $1, $2, $3, $4, $5,
            $6, $7, $8,
            $9, $10,
            $11, $12, $13,
            $14, $15, $16::jsonb
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id, source, source_ref, patient_name, patient_phone,
        patient_email, date_of_birth, reason,
        preferred_starts_at, preferred_ends_at,
        status, urgency_level, action_required,
        assigned_user_id, patient_id, raw_payload_json,
    )
    return _row_to_dict(row)


# ---------------------------------------------------------------------------
# 2. get_appointment_request_by_id
# ---------------------------------------------------------------------------


async def get_appointment_request_by_id(
    pool: Any,
    clinic_id: str,
    request_id: str,
) -> Optional[Dict[str, Any]]:
    """Return a single appointment request by its UUID, scoped to clinic_id."""
    sql = """
        SELECT *
        FROM appointment_requests
        WHERE clinic_id = $1
          AND id        = $2
    """
    row = await pool.fetchrow(sql, clinic_id, request_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 3. list_appointment_requests
# ---------------------------------------------------------------------------


async def list_appointment_requests(
    pool: Any,
    clinic_id: str,
    status: Optional[str] = None,
    action_required: Optional[bool] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Return recent appointment requests for a clinic, newest first.

    ``limit`` must be 1–100.  ``status`` and ``action_required`` are
    optional filters; omitting them returns all rows up to the limit.
    """
    if limit < 1 or limit > 100:
        raise InvalidAppointmentRequestError("limit must be between 1 and 100")

    sql = """
        SELECT *
        FROM appointment_requests
        WHERE clinic_id = $1
          AND ($2::text    IS NULL OR status          = $2)
          AND ($3::boolean IS NULL OR action_required = $3)
        ORDER BY created_at DESC
        LIMIT $4
    """
    rows = await pool.fetch(sql, clinic_id, status, action_required, limit)
    return [_row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# 4. update_appointment_request_status
# ---------------------------------------------------------------------------


async def update_appointment_request_status(
    pool: Any,
    clinic_id: str,
    request_id: str,
    status: str,
    action_required: Optional[bool] = None,
) -> Optional[Dict[str, Any]]:
    """Update the status (and optionally action_required) of an appointment request."""
    _assert_valid_enum(status, "status", _VALID_STATUSES)

    if action_required is None:
        sql = """
            UPDATE appointment_requests
            SET status     = $1,
                updated_at = now()
            WHERE clinic_id = $2
              AND id         = $3
            RETURNING *
        """
        row = await pool.fetchrow(sql, status, clinic_id, request_id)
    else:
        sql = """
            UPDATE appointment_requests
            SET status          = $1,
                action_required = $2,
                updated_at      = now()
            WHERE clinic_id = $3
              AND id         = $4
            RETURNING *
        """
        row = await pool.fetchrow(sql, status, action_required, clinic_id, request_id)

    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 5. assign_appointment_request
# ---------------------------------------------------------------------------


async def assign_appointment_request(
    pool: Any,
    clinic_id: str,
    request_id: str,
    assigned_user_id: str,
) -> Optional[Dict[str, Any]]:
    """Assign an appointment request to a clinic user."""
    sql = """
        UPDATE appointment_requests
        SET assigned_user_id = $1,
            updated_at       = now()
        WHERE clinic_id = $2
          AND id         = $3
        RETURNING *
    """
    row = await pool.fetchrow(sql, assigned_user_id, clinic_id, request_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 6. mark_callback_needed
# ---------------------------------------------------------------------------


async def mark_callback_needed(
    pool: Any,
    clinic_id: str,
    request_id: str,
) -> Optional[Dict[str, Any]]:
    """Set status to callback_needed and action_required to true."""
    sql = """
        UPDATE appointment_requests
        SET status          = 'callback_needed',
            action_required = true,
            updated_at      = now()
        WHERE clinic_id = $1
          AND id         = $2
        RETURNING *
    """
    row = await pool.fetchrow(sql, clinic_id, request_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 7. archive_appointment_request
# ---------------------------------------------------------------------------


async def archive_appointment_request(
    pool: Any,
    clinic_id: str,
    request_id: str,
) -> Optional[Dict[str, Any]]:
    """Set status to archived and action_required to false."""
    sql = """
        UPDATE appointment_requests
        SET status          = 'archived',
            action_required = false,
            updated_at      = now()
        WHERE clinic_id = $1
          AND id         = $2
        RETURNING *
    """
    row = await pool.fetchrow(sql, clinic_id, request_id)
    return _row_to_dict(row) if row is not None else None
