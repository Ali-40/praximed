"""
Patient History Review Service — PraxisMed Sprint 20 / Module 154.

Staff/doctor review workflow for unverified patient history proposals.
Approve/merge creates ONE approved patient_history_* row. No auto-approval.
Reject sets proposal_status=rejected with reason. No history row created.

No auto-approval. No diagnosis generation. No medical advice. No triage scoring.
No treatment recommendations. No external LLM. No API keys.
production_phi_enabled always False. synthetic_demo always True.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.app.core.auth_context import AuthContext
from backend.app.db.repositories import patient_history_repo, patient_history_structuring_repo as struct_repo
from backend.app.db.repositories.patient_history_repo import (
    HISTORY_TYPE_TABLE,
    UnsupportedHistoryTypeError,
)
from backend.app.services.consent_ledger import (
    assert_valid_consent_for_history_write,
    ConsentValidationError,
)
from backend.app.schemas.patient_history_review import _FORBIDDEN_MERGE_KEYS

logger = logging.getLogger(__name__)

_HISTORY_WRITE_PURPOSE = "patient_history_collection"

_PRIMARY_TEXT_FIELD = {
    "allergies":      "substance_text",
    "medications":    "medication_text",
    "conditions":     "condition_text",
    "procedures":     "procedure_text",
    "immunizations":  "vaccine_text",
    "family-history": "relationship_text",
    "social-history": "observation_category",
}

_CREATE_FN = {
    "allergies":      patient_history_repo.create_allergy_history,
    "medications":    patient_history_repo.create_medication_history,
    "conditions":     patient_history_repo.create_condition_history,
    "procedures":     patient_history_repo.create_procedure_history,
    "immunizations":  patient_history_repo.create_immunization_history,
    "family-history": patient_history_repo.create_family_history,
    "social-history": patient_history_repo.create_social_history,
}


class ReviewServiceError(RuntimeError):
    """Base error for review service."""


class ProposalNotFoundError(ReviewServiceError):
    """Raised when the proposal does not exist for this clinic."""


class ProposalNotEligibleError(ReviewServiceError):
    """Raised when the proposal is not in unverified status."""


class StaffReviewRequiredError(ReviewServiceError):
    """Raised when staff_review_required flag is not true."""


class PhiGuardError(ReviewServiceError):
    """Raised when production_phi_enabled would be set true."""


class PatientRequiredError(ReviewServiceError):
    """Raised when patient_id is missing and is required for merge."""


class ForbiddenMergeFieldError(ReviewServiceError):
    """Raised when edited_fields contain forbidden keys."""


async def _load_proposal(pool: Any, proposal_id: str, clinic_id: str) -> Dict[str, Any]:
    proposal = await struct_repo.get_history_proposal_by_id(
        pool=pool, proposal_id=proposal_id, clinic_id=clinic_id
    )
    if proposal is None:
        raise ProposalNotFoundError(
            f"Proposal {proposal_id!r} not found for clinic {clinic_id!r}."
        )
    return proposal


def _assert_proposal_unverified(proposal: Dict[str, Any]) -> None:
    if proposal.get("proposal_status") != "unverified":
        raise ProposalNotEligibleError(
            f"Proposal {proposal.get('id')!r} is not eligible for merge "
            f"(current status: {proposal.get('proposal_status')!r}). "
            "Only unverified proposals can be merged."
        )


def _assert_staff_review_required(proposal: Dict[str, Any]) -> None:
    if not proposal.get("staff_review_required"):
        raise StaffReviewRequiredError(
            "staff_review_required is not true on this proposal. Cannot merge."
        )


def _assert_phi_disabled(proposal: Dict[str, Any]) -> None:
    if proposal.get("production_phi_enabled"):
        raise PhiGuardError("production_phi_enabled is true on proposal. Cannot merge. Production PHI remains NO-GO.")


def _assert_patient_present(proposal: Dict[str, Any]) -> None:
    if not proposal.get("patient_id"):
        raise PatientRequiredError(
            "patient_id is required on proposal before merging into patient_history_*."
        )


def _assert_no_forbidden_merge_keys(edited_fields: Dict[str, Any]) -> None:
    for k in edited_fields:
        if k.lower() in _FORBIDDEN_MERGE_KEYS:
            raise ForbiddenMergeFieldError(
                f"Field key {k!r} is forbidden in edited_fields. "
                "No scoring, diagnosis, advice, or auto-approval fields allowed."
            )


def _extract_primary_text(history_type: str, edited_fields: Dict[str, Any], proposed_fields: Dict[str, Any]) -> str:
    primary_key = _PRIMARY_TEXT_FIELD.get(history_type, "")
    value = edited_fields.get(primary_key) or proposed_fields.get(primary_key) or proposed_fields.get("raw_answer", "")
    return str(value).strip() if value else "unspecified"


async def approve_and_merge_history_proposal(
    pool: Any,
    proposal_id: str,
    clinic_id: str,
    edited_fields: Dict[str, Any],
    edited_fhir_payload: Optional[Dict[str, Any]] = None,
    review_note: Optional[str] = None,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    proposal = await _load_proposal(pool, proposal_id, clinic_id)

    _assert_proposal_unverified(proposal)
    _assert_staff_review_required(proposal)
    _assert_phi_disabled(proposal)
    _assert_patient_present(proposal)
    _assert_no_forbidden_merge_keys(edited_fields)

    history_type = proposal["history_type"]
    if history_type not in HISTORY_TYPE_TABLE:
        raise UnsupportedHistoryTypeError(f"Unsupported history_type {history_type!r} on proposal.")

    consent_event_id = str(proposal["consent_event_id"])
    patient_id = str(proposal["patient_id"])
    appointment_request_id = (
        str(proposal["appointment_request_id"]) if proposal.get("appointment_request_id") else None
    )
    fhir_resource_type = proposal["fhir_resource_type"]
    proposed_fields: Dict[str, Any] = proposal.get("proposed_fields") or {}

    await assert_valid_consent_for_history_write(
        pool=pool,
        clinic_id=clinic_id,
        consent_event_id=consent_event_id,
        purpose=_HISTORY_WRITE_PURPOSE,
    )

    primary_key = _PRIMARY_TEXT_FIELD[history_type]
    primary_text = _extract_primary_text(history_type, edited_fields, proposed_fields)

    create_fn = _CREATE_FN[history_type]
    actor_id = str(actor_user.user_id) if actor_user else None

    merged_fields = {k: v for k, v in edited_fields.items() if k != primary_key}
    merged_fields["appointment_request_id"] = appointment_request_id
    merged_fields["status"] = "approved"
    merged_fields["source_type"] = "ai_proposal"
    merged_fields["source_ref"] = f"proposal:{proposal_id}"
    merged_fields["fhir_resource_type"] = fhir_resource_type
    merged_fields["fhir_payload"] = edited_fhir_payload or proposal.get("proposed_fhir_payload") or {}
    merged_fields["reviewed_by_user_id"] = actor_id
    merged_fields["review_note"] = review_note
    merged_fields["production_phi_enabled"] = False
    merged_fields.pop("clinic_id", None)
    merged_fields.pop("patient_id", None)
    merged_fields.pop("consent_event_id", None)

    if history_type == "social-history":
        observation_text = (
            edited_fields.get("observation_text")
            or proposed_fields.get("observation_text")
            or proposed_fields.get("raw_answer", "unspecified")
        )
        merged_fields.pop("observation_text", None)
        history_row = await create_fn(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            consent_event_id=consent_event_id,
            observation_category=primary_text,
            observation_text=observation_text,
            **{k: v for k, v in merged_fields.items()},
        )
    else:
        history_row = await create_fn(
            pool=pool,
            clinic_id=clinic_id,
            patient_id=patient_id,
            consent_event_id=consent_event_id,
            **{primary_key: primary_text},
            **{k: v for k, v in merged_fields.items()},
        )

    merged_entry_id = str(history_row["id"])

    updated_proposal = await struct_repo.update_proposal_status(
        pool=pool,
        proposal_id=proposal_id,
        clinic_id=clinic_id,
        proposal_status="merged",
        rejected_reason=None,
        reviewed_by_user_id=actor_id,
        review_note=review_note,
    )

    if updated_proposal is not None:
        await pool.execute(
            """UPDATE patient_history_proposals
               SET merged_history_entry_id = $1::uuid, updated_at = now()
               WHERE id = $2::uuid AND clinic_id = $3::uuid""",
            merged_entry_id, proposal_id, clinic_id,
        )

    logger.info(
        "proposal_merged proposal_id=%s history_type=%s entry_id=%s clinic=%s actor=%s",
        proposal_id,
        history_type,
        merged_entry_id,
        clinic_id,
        actor_id or "anonymous",
    )

    return {
        "ok": True,
        "proposal_id": proposal_id,
        "merged_history_entry_id": merged_entry_id,
        "history_type": history_type,
        "fhir_resource_type": fhir_resource_type,
        "proposal_status": "merged",
        "production_phi_enabled": False,
        "review_note": review_note,
        "message": "Proposal merged into patient history after staff review.",
    }


async def reject_history_proposal_with_review(
    pool: Any,
    proposal_id: str,
    clinic_id: str,
    rejected_reason: Optional[str] = None,
    review_note: Optional[str] = None,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    proposal = await _load_proposal(pool, proposal_id, clinic_id)
    _assert_proposal_unverified(proposal)

    actor_id = str(actor_user.user_id) if actor_user else None

    await struct_repo.update_proposal_status(
        pool=pool,
        proposal_id=proposal_id,
        clinic_id=clinic_id,
        proposal_status="rejected",
        rejected_reason=rejected_reason,
        reviewed_by_user_id=actor_id,
        review_note=review_note,
    )

    logger.info(
        "proposal_rejected_review proposal_id=%s clinic=%s actor=%s",
        proposal_id,
        clinic_id,
        actor_id or "anonymous",
    )

    return {
        "ok": True,
        "proposal_id": proposal_id,
        "proposal_status": "rejected",
        "rejected_reason": rejected_reason,
        "production_phi_enabled": False,
        "message": "Proposal rejected.",
    }


async def list_review_queue(
    pool: Any,
    clinic_id: str,
    patient_id: Optional[str] = None,
    history_type: Optional[str] = None,
    status: str = "unverified",
    limit: int = 50,
    actor_user: Optional[AuthContext] = None,
) -> List[Dict[str, Any]]:
    return await struct_repo.list_history_proposals(
        pool=pool,
        clinic_id=clinic_id,
        patient_id=patient_id,
        proposal_status=status,
        history_type=history_type,
        limit=limit,
    )


async def get_proposal_review_detail(
    pool: Any,
    proposal_id: str,
    clinic_id: str,
    actor_user: Optional[AuthContext] = None,
) -> Dict[str, Any]:
    return await _load_proposal(pool, proposal_id, clinic_id)
