"""
Consultation Session Repository — PraxisMed Sprint 2 / Module 28

Provides async CRUD operations for the ``consultation_sessions`` table.
All SQL is parameterised ($1, $2, …) — no string interpolation.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ConsultationRepoError(RuntimeError):
    """Base class for consultation repository errors."""


class InvalidConsultationSessionError(ConsultationRepoError):
    """Raised when required fields are missing or values are invalid."""


# ---------------------------------------------------------------------------
# Allowed enum values
# ---------------------------------------------------------------------------

_VALID_SOURCES = frozenset({"manual", "vapi", "web", "doctor_mobile", "system"})

_VALID_STATUSES = frozenset({
    "created", "recording", "audio_uploaded", "transcribing",
    "transcribed", "draft_ready", "approved", "rejected", "archived",
})

_VALID_APPROVAL_STATUSES = frozenset({
    "not_ready", "pending_review", "approved", "rejected",
})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _assert_nonempty(value: Any, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidConsultationSessionError(f"{name!r} must not be empty")


def _assert_valid_source(value: str) -> None:
    if value not in _VALID_SOURCES:
        raise InvalidConsultationSessionError(
            f"'source' must be one of {sorted(_VALID_SOURCES)!r}; got {value!r}"
        )


def _assert_valid_status(value: str) -> None:
    if value not in _VALID_STATUSES:
        raise InvalidConsultationSessionError(
            f"'status' must be one of {sorted(_VALID_STATUSES)!r}; got {value!r}"
        )


def _assert_valid_approval_status(value: str) -> None:
    if value not in _VALID_APPROVAL_STATUSES:
        raise InvalidConsultationSessionError(
            f"'approval_status' must be one of {sorted(_VALID_APPROVAL_STATUSES)!r}; got {value!r}"
        )


# ---------------------------------------------------------------------------
# 1. create_consultation_session
# ---------------------------------------------------------------------------


async def create_consultation_session(
    pool: Any,
    clinic_id: str,
    patient_id: str,
    doctor_user_id: Optional[str] = None,
    source: str = "manual",
    status: str = "created",
    title: Optional[str] = None,
    reason_for_visit: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(patient_id, "patient_id")
    _assert_valid_source(source)
    _assert_valid_status(status)

    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    sql = """
        INSERT INTO consultation_sessions (
            clinic_id, patient_id, doctor_user_id,
            source, status, title, reason_for_visit, raw_payload
        ) VALUES (
            $1, $2, $3,
            $4, $5, $6, $7, $8::jsonb
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id, patient_id, doctor_user_id,
        source, status, title, reason_for_visit, raw_payload_json,
    )
    return _row_to_dict(row)


# ---------------------------------------------------------------------------
# 2. get_consultation_session_by_id
# ---------------------------------------------------------------------------


async def get_consultation_session_by_id(
    pool: Any,
    clinic_id: str,
    session_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT *
        FROM consultation_sessions
        WHERE clinic_id = $1
          AND id        = $2
    """
    row = await pool.fetchrow(sql, clinic_id, session_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 3. list_consultation_sessions
# ---------------------------------------------------------------------------


async def list_consultation_sessions(
    pool: Any,
    clinic_id: str,
    patient_id: Optional[str] = None,
    doctor_user_id: Optional[str] = None,
    status: Optional[str] = None,
    approval_status: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if limit < 1 or limit > 100:
        raise InvalidConsultationSessionError("limit must be between 1 and 100")
    if status is not None:
        _assert_valid_status(status)
    if approval_status is not None:
        _assert_valid_approval_status(approval_status)
    if source is not None:
        _assert_valid_source(source)

    sql = """
        SELECT *
        FROM consultation_sessions
        WHERE clinic_id = $1
          AND ($2::text IS NULL OR patient_id      = $2::uuid)
          AND ($3::text IS NULL OR doctor_user_id  = $3::uuid)
          AND ($4::text IS NULL OR status          = $4)
          AND ($5::text IS NULL OR approval_status = $5)
          AND ($6::text IS NULL OR source          = $6)
        ORDER BY created_at DESC
        LIMIT $7
    """
    rows = await pool.fetch(
        sql,
        clinic_id, patient_id, doctor_user_id,
        status, approval_status, source, limit,
    )
    return [_row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# 4. update_consultation_status
# ---------------------------------------------------------------------------


async def update_consultation_status(
    pool: Any,
    clinic_id: str,
    session_id: str,
    status: str,
    approval_status: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    _assert_valid_status(status)
    if approval_status is not None:
        _assert_valid_approval_status(approval_status)

    sql = """
        UPDATE consultation_sessions
        SET status          = $1,
            approval_status = COALESCE($2, approval_status),
            updated_at      = now()
        WHERE clinic_id = $3
          AND id        = $4
        RETURNING *
    """
    row = await pool.fetchrow(sql, status, approval_status, clinic_id, session_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 5. attach_audio_to_session
# ---------------------------------------------------------------------------


async def attach_audio_to_session(
    pool: Any,
    clinic_id: str,
    session_id: str,
    audio_file_path: str,
) -> Optional[Dict[str, Any]]:
    _assert_nonempty(audio_file_path, "audio_file_path")

    sql = """
        UPDATE consultation_sessions
        SET audio_file_path = $1,
            status          = 'audio_uploaded',
            updated_at      = now()
        WHERE clinic_id = $2
          AND id        = $3
        RETURNING *
    """
    row = await pool.fetchrow(sql, audio_file_path, clinic_id, session_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 6. save_transcript
# ---------------------------------------------------------------------------


async def save_transcript(
    pool: Any,
    clinic_id: str,
    session_id: str,
    transcript_text: str,
) -> Optional[Dict[str, Any]]:
    _assert_nonempty(transcript_text, "transcript_text")

    sql = """
        UPDATE consultation_sessions
        SET transcript_text = $1,
            status          = 'transcribed',
            updated_at      = now()
        WHERE clinic_id = $2
          AND id        = $3
        RETURNING *
    """
    row = await pool.fetchrow(sql, transcript_text, clinic_id, session_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 7. save_draft_summary
# ---------------------------------------------------------------------------


async def save_draft_summary(
    pool: Any,
    clinic_id: str,
    session_id: str,
    draft_summary: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    if not draft_summary or not isinstance(draft_summary, dict):
        raise InvalidConsultationSessionError("'draft_summary' must be a non-empty dict")

    draft_summary_json = json.dumps(draft_summary)

    sql = """
        UPDATE consultation_sessions
        SET draft_summary   = $1::jsonb,
            status          = 'draft_ready',
            approval_status = 'pending_review',
            updated_at      = now()
        WHERE clinic_id = $2
          AND id        = $3
        RETURNING *
    """
    row = await pool.fetchrow(sql, draft_summary_json, clinic_id, session_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 8. approve_consultation_summary
# ---------------------------------------------------------------------------


async def approve_consultation_summary(
    pool: Any,
    clinic_id: str,
    session_id: str,
    approved_summary: Dict[str, Any],
    approved_by_user_id: str,
) -> Optional[Dict[str, Any]]:
    if not approved_summary or not isinstance(approved_summary, dict):
        raise InvalidConsultationSessionError("'approved_summary' must be a non-empty dict")
    _assert_nonempty(approved_by_user_id, "approved_by_user_id")

    approved_summary_json = json.dumps(approved_summary)

    sql = """
        UPDATE consultation_sessions
        SET approved_summary    = $1::jsonb,
            approved_by_user_id = $2,
            approved_at         = now(),
            status              = 'approved',
            approval_status     = 'approved',
            updated_at          = now()
        WHERE clinic_id = $3
          AND id        = $4
        RETURNING *
    """
    row = await pool.fetchrow(
        sql, approved_summary_json, approved_by_user_id, clinic_id, session_id
    )
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 9. reject_consultation_summary
# ---------------------------------------------------------------------------


async def reject_consultation_summary(
    pool: Any,
    clinic_id: str,
    session_id: str,
    rejected_reason: str,
    rejected_by_user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    _assert_nonempty(rejected_reason, "rejected_reason")

    sql = """
        UPDATE consultation_sessions
        SET rejected_reason     = $1,
            approved_by_user_id = COALESCE($2, approved_by_user_id),
            status              = 'rejected',
            approval_status     = 'rejected',
            updated_at          = now()
        WHERE clinic_id = $3
          AND id        = $4
        RETURNING *
    """
    row = await pool.fetchrow(
        sql, rejected_reason, rejected_by_user_id, clinic_id, session_id
    )
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 10. archive_consultation_session
# ---------------------------------------------------------------------------


async def archive_consultation_session(
    pool: Any,
    clinic_id: str,
    session_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE consultation_sessions
        SET status     = 'archived',
            updated_at = now()
        WHERE clinic_id = $1
          AND id        = $2
        RETURNING *
    """
    row = await pool.fetchrow(sql, clinic_id, session_id)
    return _row_to_dict(row) if row is not None else None
