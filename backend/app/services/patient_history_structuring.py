"""
Patient History Structuring Service — PraxisMed Sprint 20 / Module 153.

Local deterministic demo extraction only. No external LLM. No API keys.
Reads patient_intake_submissions, maps answers to history proposals via
template question history_target. All proposals remain status=unverified.

No automatic approval. No diagnosis. No medical advice. No triage scoring.
No treatment recommendations. No patient_history_* writes.
extraction_confidence is extraction confidence only — not a medical judgment.
production_phi_enabled always False. synthetic_demo always True.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import patient_history_structuring_repo as repo

logger = logging.getLogger(__name__)


_HISTORY_TYPE_TO_FHIR: Dict[str, str] = {
    "allergies": "AllergyIntolerance",
    "medications": "MedicationStatement",
    "conditions": "Condition",
    "procedures": "Procedure",
    "immunizations": "Immunization",
    "family-history": "FamilyMemberHistory",
    "social-history": "Observation",
}

_SKIPPED_HISTORY_TARGETS = frozenset({"none", "appointment-context"})


class StructuringServiceError(RuntimeError):
    """Base error for structuring service."""


class SubmissionNotFoundError(StructuringServiceError):
    """Raised when intake submission does not exist for this clinic."""


class AlreadyStructuredError(StructuringServiceError):
    """Raised when the submission already has a completed structuring run."""


class ProposalNotFoundError(StructuringServiceError):
    """Raised when a proposal does not exist for this clinic."""


class StructuringRunNotFoundError(StructuringServiceError):
    """Raised when a structuring run does not exist for this clinic."""


async def _load_submission(pool: Any, submission_id: str, clinic_id: str) -> Dict[str, Any]:
    row = await pool.fetchrow(
        "SELECT * FROM patient_intake_submissions WHERE id = $1::uuid AND clinic_id = $2::uuid",
        submission_id, clinic_id,
    )
    if row is None:
        raise SubmissionNotFoundError(
            f"Intake submission {submission_id!r} not found for clinic {clinic_id!r}."
        )
    d = dict(row)
    for key in ("answers", "skipped_questions", "escalation_matches"):
        if isinstance(d.get(key), str):
            try:
                d[key] = json.loads(d[key])
            except (ValueError, TypeError):
                pass
    return d


async def _load_template_questions(pool: Any, template_id: str) -> List[Dict[str, Any]]:
    row = await pool.fetchrow(
        "SELECT template_schema FROM anamnesis_templates WHERE id = $1::uuid", template_id
    )
    if row is None:
        return []
    schema = row["template_schema"]
    if isinstance(schema, str):
        try:
            schema = json.loads(schema)
        except (ValueError, TypeError):
            return []
    questions: List[Dict[str, Any]] = []
    for section in schema.get("sections", []):
        for q in section.get("questions", []):
            questions.append(q)
    return questions


def _build_demo_proposal(
    answer_text: str,
    history_type: str,
    fhir_resource_type: str,
    question_key: str,
    label: str,
) -> Dict[str, Any]:
    proposed_fields: Dict[str, Any] = {
        "raw_answer": answer_text,
        "extraction_source": "local_demo_extractor",
        "question_label": label,
    }
    proposed_fhir_payload: Dict[str, Any] = {
        "resourceType": fhir_resource_type,
        "text": {"status": "generated", "div": f"<div>{answer_text}</div>"},
        "note": [{"text": answer_text}],
    }
    return {
        "proposed_fields": proposed_fields,
        "proposed_fhir_payload": proposed_fhir_payload,
        "extraction_confidence": 0.70,
        "confidence_explanation": (
            "Extraction confidence only — not a medical judgment. "
            "Local demo extractor: direct answer text mapped to FHIR field."
        ),
    }


async def _check_not_already_structured(pool: Any, submission_id: str, clinic_id: str) -> None:
    row = await pool.fetchrow(
        """SELECT id FROM patient_history_structuring_runs
           WHERE intake_submission_id = $1::uuid AND clinic_id = $2::uuid AND status = 'completed'
           LIMIT 1""",
        submission_id, clinic_id,
    )
    if row is not None:
        raise AlreadyStructuredError(
            f"Submission {submission_id!r} has already been structured (run {row['id']!r})."
        )


async def structure_intake_submission(
    pool: Any,
    submission_id: str,
    clinic_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    await _check_not_already_structured(pool, submission_id, clinic_id)

    submission = await _load_submission(pool, submission_id, clinic_id)
    answers: Dict[str, Any] = submission.get("answers") or {}
    template_id: Optional[str] = (
        str(submission["template_id"]) if submission.get("template_id") else None
    )
    consent_event_id = str(submission["consent_event_id"])
    patient_id: Optional[str] = (
        str(submission["patient_id"]) if submission.get("patient_id") else None
    )
    appointment_request_id: Optional[str] = (
        str(submission["appointment_request_id"])
        if submission.get("appointment_request_id")
        else None
    )
    language: str = str(submission.get("language") or "de")

    questions = await _load_template_questions(pool, template_id) if template_id else []

    extraction_pairs: List[Dict[str, Any]] = []
    for q in questions:
        history_target = q.get("history_target", "none")
        if history_target in _SKIPPED_HISTORY_TARGETS:
            continue
        if history_target not in _HISTORY_TYPE_TO_FHIR:
            continue
        question_key = q.get("question_key", "")
        answer_text = answers.get(question_key)
        if not answer_text or not str(answer_text).strip():
            continue
        label_dict = q.get("label") or {}
        label = label_dict.get("en") or label_dict.get("de") or question_key
        extraction_pairs.append({
            "question_key": question_key,
            "history_type": history_target,
            "fhir_resource_type": _HISTORY_TYPE_TO_FHIR[history_target],
            "answer_text": str(answer_text).strip(),
            "label": label,
        })

    run = await repo.create_structuring_run(
        pool=pool,
        clinic_id=clinic_id,
        intake_submission_id=submission_id,
        consent_event_id=consent_event_id,
        provider="local_demo_extractor",
        language=language,
        extraction_mode="synthetic_demo",
        proposals_count=len(extraction_pairs),
        intake_link_id=(
            str(submission["intake_link_id"]) if submission.get("intake_link_id") else None
        ),
        template_id=template_id,
        patient_id=patient_id,
        appointment_request_id=appointment_request_id,
        provider_model=None,
        status="completed",
        created_by_user_id=str(actor_user.user_id) if actor_user else None,
    )
    run_id = str(run["id"])

    proposal_ids: List[str] = []
    for pair in extraction_pairs:
        demo = _build_demo_proposal(
            answer_text=pair["answer_text"],
            history_type=pair["history_type"],
            fhir_resource_type=pair["fhir_resource_type"],
            question_key=pair["question_key"],
            label=pair["label"],
        )
        proposal = await repo.create_history_proposal(
            pool=pool,
            clinic_id=clinic_id,
            structuring_run_id=run_id,
            intake_submission_id=submission_id,
            consent_event_id=consent_event_id,
            history_type=pair["history_type"],
            fhir_resource_type=pair["fhir_resource_type"],
            proposed_fields=demo["proposed_fields"],
            proposed_fhir_payload=demo["proposed_fhir_payload"],
            source_question_key=pair["question_key"],
            source_answer_ref=None,
            extraction_confidence=demo["extraction_confidence"],
            confidence_explanation=demo["confidence_explanation"],
            patient_id=patient_id,
            appointment_request_id=appointment_request_id,
        )
        proposal_ids.append(str(proposal["id"]))

    logger.info(
        "structuring_run_completed run_id=%s clinic=%s proposals=%d actor=%s",
        run_id,
        clinic_id,
        len(proposal_ids),
        actor_user.user_id if actor_user else "anonymous",
    )

    return {
        "ok": True,
        "run_id": run_id,
        "proposals_created": len(proposal_ids),
        "proposal_ids": proposal_ids,
        "provider": "local_demo_extractor",
        "extraction_mode": "synthetic_demo",
        "production_phi_enabled": False,
        "extraction_note": "Extraction confidence only — not a medical judgment.",
    }


async def list_patient_history_proposals(
    pool: Any,
    clinic_id: str,
    patient_id: Optional[str] = None,
    proposal_status: Optional[str] = None,
    history_type: Optional[str] = None,
    limit: int = 50,
    actor_user: Optional[AuthContext] = None,
) -> List[Dict[str, Any]]:
    return await repo.list_history_proposals(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
        proposal_status=proposal_status,
        history_type=history_type,
        limit=limit,
    )


async def get_structuring_run(
    pool: Any,
    run_id: str,
    clinic_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    run = await repo.get_structuring_run_by_id(pool=pool, run_id=run_id, clinic_id=clinic_id)
    if run is None:
        raise StructuringRunNotFoundError(
            f"Structuring run {run_id!r} not found for clinic {clinic_id!r}."
        )
    proposals = await repo.list_proposals_for_run(pool=pool, run_id=run_id, clinic_id=clinic_id)
    return {"run": run, "proposals": proposals}


async def reject_history_proposal(
    pool: Any,
    proposal_id: str,
    clinic_id: str,
    reason: Optional[str] = None,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    updated = await repo.update_proposal_status(
        pool=pool,
        proposal_id=proposal_id,
        clinic_id=clinic_id,
        proposal_status="rejected",
        rejected_reason=reason,
        reviewed_by_user_id=str(actor_user.user_id) if actor_user else None,
        review_note=None,
    )
    if updated is None:
        raise ProposalNotFoundError(
            f"Proposal {proposal_id!r} not found for clinic {clinic_id!r}."
        )
    logger.info(
        "proposal_rejected proposal_id=%s clinic=%s actor=%s",
        proposal_id,
        clinic_id,
        actor_user.user_id if actor_user else "anonymous",
    )
    return updated


async def archive_demo_history_proposal(
    pool: Any,
    proposal_id: str,
    clinic_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    updated = await repo.update_proposal_status(
        pool=pool,
        proposal_id=proposal_id,
        clinic_id=clinic_id,
        proposal_status="archived_demo",
        rejected_reason=None,
        reviewed_by_user_id=str(actor_user.user_id) if actor_user else None,
        review_note="archived_demo",
    )
    if updated is None:
        raise ProposalNotFoundError(
            f"Proposal {proposal_id!r} not found for clinic {clinic_id!r}."
        )
    logger.info(
        "proposal_archived_demo proposal_id=%s clinic=%s actor=%s",
        proposal_id,
        clinic_id,
        actor_user.user_id if actor_user else "anonymous",
    )
    return updated
