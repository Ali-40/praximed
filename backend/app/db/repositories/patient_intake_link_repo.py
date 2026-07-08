"""
Patient Intake Link Repository — PraxisMed Sprint 20 / Module 151.

Async CRUD for patient_intake_links and patient_intake_submissions.
All SQL is parameterised. Tenant-scoped. No cross-clinic leakage.

Raw token never stored. Only token_hash and token_prefix.
No patient history writes. No AI structuring.
No diagnosis. No medical advice. No triage scoring.
production_phi_enabled always false. synthetic_demo always true.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class PatientIntakeLinkRepoError(RuntimeError):
    """Base error for intake link repo."""


class PatientIntakeLinkNotFoundError(PatientIntakeLinkRepoError):
    """Raised when an intake link does not exist."""


class PatientIntakeSubmissionRepoError(PatientIntakeLinkRepoError):
    """Raised when submission creation fails."""


def _row_to_dict(row: Any) -> Dict[str, Any]:
    d = dict(row)
    for key in ("answers", "skipped_questions", "escalation_matches"):
        if isinstance(d.get(key), str):
            try:
                d[key] = json.loads(d[key])
            except (ValueError, TypeError):
                pass
    return d


async def create_patient_intake_link(
    pool: Any,
    clinic_id: str,
    template_id: str,
    token_hash: str,
    token_prefix: str,
    expires_at: datetime,
    language: str = "de",
    purpose: str = "patient_history_collection",
    patient_id: Optional[str] = None,
    appointment_request_id: Optional[str] = None,
    max_submissions: int = 1,
    synthetic_demo: bool = True,
    created_by_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    sql = """
        INSERT INTO patient_intake_links (
            clinic_id, patient_id, appointment_request_id, template_id,
            token_hash, token_prefix, language, purpose,
            expires_at, max_submissions, synthetic_demo,
            production_phi_enabled, created_by_user_id
        ) VALUES (
            $1::uuid, $2::uuid, $3::uuid, $4::uuid,
            $5, $6, $7, $8,
            $9, $10, $11,
            false, $12::uuid
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id,
        patient_id,
        appointment_request_id,
        template_id,
        token_hash,
        token_prefix,
        language,
        purpose,
        expires_at,
        max_submissions,
        synthetic_demo,
        created_by_user_id,
    )
    return _row_to_dict(row)


async def get_intake_link_by_id(
    pool: Any,
    link_id: str,
) -> Optional[Dict[str, Any]]:
    row = await pool.fetchrow(
        "SELECT * FROM patient_intake_links WHERE id = $1::uuid",
        link_id,
    )
    return _row_to_dict(row) if row is not None else None


async def get_intake_link_by_token_hash(
    pool: Any,
    token_hash: str,
) -> Optional[Dict[str, Any]]:
    row = await pool.fetchrow(
        "SELECT * FROM patient_intake_links WHERE token_hash = $1",
        token_hash,
    )
    return _row_to_dict(row) if row is not None else None


async def list_intake_links_for_clinic(
    pool: Any,
    clinic_id: str,
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if status is not None:
        sql = """
            SELECT * FROM patient_intake_links
            WHERE clinic_id = $1::uuid AND status = $2
            ORDER BY created_at DESC LIMIT $3
        """
        rows = await pool.fetch(sql, clinic_id, status, limit)
    else:
        sql = """
            SELECT * FROM patient_intake_links
            WHERE clinic_id = $1::uuid
            ORDER BY created_at DESC LIMIT $2
        """
        rows = await pool.fetch(sql, clinic_id, limit)
    return [_row_to_dict(r) for r in rows]


async def revoke_intake_link(
    pool: Any,
    link_id: str,
    clinic_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE patient_intake_links
        SET status = 'revoked', updated_at = now()
        WHERE id = $1::uuid AND clinic_id = $2::uuid
        RETURNING *
    """
    row = await pool.fetchrow(sql, link_id, clinic_id)
    return _row_to_dict(row) if row is not None else None


async def increment_submission_count(
    pool: Any,
    link_id: str,
    max_submissions: int,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE patient_intake_links
        SET submission_count = submission_count + 1,
            status = CASE
                WHEN submission_count + 1 >= $2 THEN 'submitted'
                ELSE status
            END,
            updated_at = now()
        WHERE id = $1::uuid
        RETURNING *
    """
    row = await pool.fetchrow(sql, link_id, max_submissions)
    return _row_to_dict(row) if row is not None else None


async def create_intake_submission(
    pool: Any,
    intake_link_id: str,
    clinic_id: str,
    template_id: str,
    consent_event_id: str,
    answers: Dict[str, Any],
    skipped_questions: List[str],
    escalation_matches: List[str],
    language: str = "de",
    patient_id: Optional[str] = None,
    appointment_request_id: Optional[str] = None,
    synthetic_demo: bool = True,
) -> Dict[str, Any]:
    sql = """
        INSERT INTO patient_intake_submissions (
            intake_link_id, clinic_id, patient_id, appointment_request_id,
            template_id, consent_event_id, language,
            answers, skipped_questions, escalation_matches,
            status, synthetic_demo, production_phi_enabled
        ) VALUES (
            $1::uuid, $2::uuid, $3::uuid, $4::uuid,
            $5::uuid, $6::uuid, $7,
            $8::jsonb, $9::jsonb, $10::jsonb,
            'submitted', $11, false
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        intake_link_id,
        clinic_id,
        patient_id,
        appointment_request_id,
        template_id,
        consent_event_id,
        language,
        json.dumps(answers),
        json.dumps(skipped_questions),
        json.dumps(escalation_matches),
        synthetic_demo,
    )
    return _row_to_dict(row)


async def list_intake_submissions_for_clinic(
    pool: Any,
    clinic_id: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT * FROM patient_intake_submissions
        WHERE clinic_id = $1::uuid
        ORDER BY created_at DESC LIMIT $2
    """
    rows = await pool.fetch(sql, clinic_id, limit)
    return [_row_to_dict(r) for r in rows]


async def list_intake_submissions_for_link(
    pool: Any,
    intake_link_id: str,
    clinic_id: str,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT * FROM patient_intake_submissions
        WHERE intake_link_id = $1::uuid AND clinic_id = $2::uuid
        ORDER BY created_at DESC
    """
    rows = await pool.fetch(sql, intake_link_id, clinic_id)
    return [_row_to_dict(r) for r in rows]
