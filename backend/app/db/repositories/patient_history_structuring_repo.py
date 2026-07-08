"""
Patient History Structuring Repository — PraxisMed Sprint 20 / Module 153.

Async CRUD for patient_history_structuring_runs and patient_history_proposals.
All SQL is parameterised. Tenant-scoped. No cross-clinic leakage.

No patient_history_* writes. No approval/merge. No delete.
No external LLM calls. No API keys. No raw prompts stored. No raw model response stored.
synthetic_demo always true. production_phi_enabled always false.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


class StructuringRepoError(RuntimeError):
    """Base error for structuring repo."""


class StructuringRunNotFoundError(StructuringRepoError):
    """Raised when a structuring run does not exist."""


class ProposalNotFoundError(StructuringRepoError):
    """Raised when a proposal does not exist."""


def _row_to_dict(row: Any) -> Dict[str, Any]:
    d = dict(row)
    for key in ("proposed_fields", "proposed_fhir_payload"):
        if isinstance(d.get(key), str):
            try:
                d[key] = json.loads(d[key])
            except (ValueError, TypeError):
                pass
    return d


async def create_structuring_run(
    pool: Any,
    clinic_id: str,
    intake_submission_id: str,
    consent_event_id: str,
    provider: str = "local_demo_extractor",
    language: str = "de",
    extraction_mode: str = "synthetic_demo",
    proposals_count: int = 0,
    intake_link_id: Optional[str] = None,
    template_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    appointment_request_id: Optional[str] = None,
    provider_model: Optional[str] = None,
    status: str = "completed",
    error_message: Optional[str] = None,
    pseudonymized_log_ref: Optional[str] = None,
    created_by_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    sql = """
        INSERT INTO patient_history_structuring_runs (
            clinic_id, intake_submission_id, intake_link_id, template_id,
            patient_id, appointment_request_id, consent_event_id,
            provider, provider_model, status, language, extraction_mode,
            proposals_count, error_message, pseudonymized_log_ref,
            synthetic_demo, production_phi_enabled, created_by_user_id
        ) VALUES (
            $1::uuid, $2::uuid, $3::uuid, $4::uuid,
            $5::uuid, $6::uuid, $7::uuid,
            $8, $9, $10, $11, $12,
            $13, $14, $15,
            true, false, $16::uuid
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id, intake_submission_id, intake_link_id, template_id,
        patient_id, appointment_request_id, consent_event_id,
        provider, provider_model, status, language, extraction_mode,
        proposals_count, error_message, pseudonymized_log_ref,
        created_by_user_id,
    )
    return dict(row)


async def create_history_proposal(
    pool: Any,
    clinic_id: str,
    structuring_run_id: str,
    intake_submission_id: str,
    consent_event_id: str,
    history_type: str,
    fhir_resource_type: str,
    proposed_fields: Dict[str, Any],
    proposed_fhir_payload: Dict[str, Any],
    source_question_key: Optional[str] = None,
    source_answer_ref: Optional[str] = None,
    extraction_confidence: Optional[float] = None,
    confidence_explanation: Optional[str] = None,
    patient_id: Optional[str] = None,
    appointment_request_id: Optional[str] = None,
) -> Dict[str, Any]:
    sql = """
        INSERT INTO patient_history_proposals (
            clinic_id, structuring_run_id, intake_submission_id, consent_event_id,
            patient_id, appointment_request_id,
            proposal_status, history_type, fhir_resource_type,
            source_question_key, source_answer_ref,
            proposed_fields, proposed_fhir_payload,
            extraction_confidence, confidence_explanation,
            staff_review_required, synthetic_demo, production_phi_enabled
        ) VALUES (
            $1::uuid, $2::uuid, $3::uuid, $4::uuid,
            $5::uuid, $6::uuid,
            'unverified', $7, $8,
            $9, $10,
            $11::jsonb, $12::jsonb,
            $13, $14,
            true, true, false
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id, structuring_run_id, intake_submission_id, consent_event_id,
        patient_id, appointment_request_id,
        history_type, fhir_resource_type,
        source_question_key, source_answer_ref,
        json.dumps(proposed_fields), json.dumps(proposed_fhir_payload),
        extraction_confidence, confidence_explanation,
    )
    return _row_to_dict(row)


async def list_history_proposals(
    pool: Any,
    clinic_id: str,
    patient_id: Optional[str] = None,
    proposal_status: Optional[str] = None,
    history_type: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    filters = ["clinic_id = $1::uuid"]
    params: List[Any] = [clinic_id]
    idx = 2

    if patient_id is not None:
        filters.append(f"patient_id = ${idx}::uuid")
        params.append(patient_id)
        idx += 1

    if proposal_status is not None:
        filters.append(f"proposal_status = ${idx}")
        params.append(proposal_status)
        idx += 1

    if history_type is not None:
        filters.append(f"history_type = ${idx}")
        params.append(history_type)
        idx += 1

    params.append(limit)
    where = " AND ".join(filters)
    sql = f"""
        SELECT * FROM patient_history_proposals
        WHERE {where}
        ORDER BY created_at DESC LIMIT ${idx}
    """
    rows = await pool.fetch(sql, *params)
    return [_row_to_dict(r) for r in rows]


async def get_history_proposal_by_id(
    pool: Any,
    proposal_id: str,
    clinic_id: str,
) -> Optional[Dict[str, Any]]:
    row = await pool.fetchrow(
        "SELECT * FROM patient_history_proposals WHERE id = $1::uuid AND clinic_id = $2::uuid",
        proposal_id, clinic_id,
    )
    return _row_to_dict(row) if row is not None else None


async def get_structuring_run_by_id(
    pool: Any,
    run_id: str,
    clinic_id: str,
) -> Optional[Dict[str, Any]]:
    row = await pool.fetchrow(
        "SELECT * FROM patient_history_structuring_runs WHERE id = $1::uuid AND clinic_id = $2::uuid",
        run_id, clinic_id,
    )
    return dict(row) if row is not None else None


async def list_proposals_for_run(
    pool: Any,
    run_id: str,
    clinic_id: str,
) -> List[Dict[str, Any]]:
    rows = await pool.fetch(
        """SELECT * FROM patient_history_proposals
           WHERE structuring_run_id = $1::uuid AND clinic_id = $2::uuid
           ORDER BY created_at""",
        run_id, clinic_id,
    )
    return [_row_to_dict(r) for r in rows]


async def update_proposal_status(
    pool: Any,
    proposal_id: str,
    clinic_id: str,
    proposal_status: str,
    rejected_reason: Optional[str] = None,
    reviewed_by_user_id: Optional[str] = None,
    review_note: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE patient_history_proposals
        SET proposal_status     = $3,
            rejected_reason     = $4,
            reviewed_by_user_id = $5::uuid,
            review_note         = $6,
            reviewed_at         = now(),
            updated_at          = now()
        WHERE id = $1::uuid AND clinic_id = $2::uuid
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        proposal_id, clinic_id,
        proposal_status, rejected_reason, reviewed_by_user_id, review_note,
    )
    return _row_to_dict(row) if row is not None else None
