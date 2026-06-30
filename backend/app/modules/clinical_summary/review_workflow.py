"""
Doctor Review and Approval Workflow — PraxisMed Sprint 2 / Module 33

Service for validating, packaging, approving, and rejecting AI-generated
clinical summary drafts. Human doctor review is mandatory before any
summary is treated as final medical documentation.

Safety guarantees:
  - Never auto-approves AI output.
  - Never generates diagnosis or treatment advice.
  - Never modifies clinical content during approval.
  - Doctor review is always required before finalisation.
  - AI/LLM calls: NONE.
  - External service calls: NONE.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.db.repositories import consultation_repo
from backend.app.modules.clinical_summary.summary_builder import (
    InvalidClinicalSummaryInputError,
    validate_clinical_summary_draft,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ReviewWorkflowError(RuntimeError):
    """Base class for review workflow errors."""


class InvalidReviewInputError(ReviewWorkflowError):
    """Raised when review input is missing or invalid."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REVIEW_SCHEMA_VERSION = "doctor_review_workflow.v1"

_REVIEW_INSTRUCTIONS = [
    "Doctor must review and edit before approval.",
    "Draft must not be treated as final medical documentation.",
    "AI-generated draft does not replace clinical judgment.",
]


# ---------------------------------------------------------------------------
# 1. validate_review_context
# ---------------------------------------------------------------------------


def validate_review_context(clinic_id: str, session_id: str) -> Dict[str, Any]:
    if not clinic_id or not str(clinic_id).strip():
        raise InvalidReviewInputError("'clinic_id' must not be empty")
    if not session_id or not str(session_id).strip():
        raise InvalidReviewInputError("'session_id' must not be empty")
    return {"clinic_id": clinic_id, "session_id": session_id}


# ---------------------------------------------------------------------------
# 2. validate_reviewer_user_id
# ---------------------------------------------------------------------------


def validate_reviewer_user_id(reviewer_user_id: str) -> str:
    if not reviewer_user_id or not str(reviewer_user_id).strip():
        raise InvalidReviewInputError("'reviewer_user_id' must not be empty")
    return reviewer_user_id


# ---------------------------------------------------------------------------
# 3. validate_draft_ready_for_review
# ---------------------------------------------------------------------------


def validate_draft_ready_for_review(draft_summary: Any) -> Dict[str, Any]:
    if not isinstance(draft_summary, dict):
        raise InvalidReviewInputError("'draft_summary' must be a dict")

    try:
        validate_clinical_summary_draft(draft_summary)
    except InvalidClinicalSummaryInputError as exc:
        raise InvalidReviewInputError(str(exc)) from exc

    if not draft_summary.get("doctor_review_required"):
        raise InvalidReviewInputError(
            "'doctor_review_required' must be True in draft_summary"
        )
    if not draft_summary.get("no_diagnosis_generated"):
        raise InvalidReviewInputError(
            "'no_diagnosis_generated' must be True in draft_summary"
        )
    if not draft_summary.get("no_treatment_advice_generated"):
        raise InvalidReviewInputError(
            "'no_treatment_advice_generated' must be True in draft_summary"
        )
    if "diagnosis" in draft_summary:
        raise InvalidReviewInputError(
            "draft_summary must not contain a top-level 'diagnosis' key"
        )

    return draft_summary


# ---------------------------------------------------------------------------
# 4. build_review_package
# ---------------------------------------------------------------------------


def build_review_package(
    clinic_id: str,
    session_id: str,
    draft_summary: Dict[str, Any],
    transcript_text: Optional[str] = None,
    patient_context: Optional[Dict[str, Any]] = None,
    consultation_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    validate_review_context(clinic_id, session_id)
    validate_draft_ready_for_review(draft_summary)

    if patient_context is not None and not isinstance(patient_context, dict):
        raise InvalidReviewInputError("'patient_context' must be a dict if provided")
    if consultation_context is not None and not isinstance(consultation_context, dict):
        raise InvalidReviewInputError(
            "'consultation_context' must be a dict if provided"
        )

    return {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "clinic_id": clinic_id,
        "session_id": session_id,
        "status": "pending_doctor_review",
        "doctor_review_required": True,
        "draft_summary": draft_summary,
        "transcript_text": transcript_text,
        "patient_context": patient_context,
        "consultation_context": consultation_context,
        "review_instructions": list(_REVIEW_INSTRUCTIONS),
    }


# ---------------------------------------------------------------------------
# 5. validate_approved_summary
# ---------------------------------------------------------------------------


def validate_approved_summary(
    approved_summary: Any,
    approved_by_user_id: str,
) -> Dict[str, Any]:
    if not isinstance(approved_summary, dict) or not approved_summary:
        raise InvalidReviewInputError(
            "'approved_summary' must be a non-empty dict"
        )
    if not approved_by_user_id or not str(approved_by_user_id).strip():
        raise InvalidReviewInputError("'approved_by_user_id' must not be empty")

    approved_summary["doctor_approved"] = True
    approved_summary["approved_by_user_id"] = approved_by_user_id
    approved_summary["source"] = "doctor_review"

    return approved_summary


# ---------------------------------------------------------------------------
# 6. approve_summary_after_review
# ---------------------------------------------------------------------------


async def approve_summary_after_review(
    pool: Any,
    clinic_id: str,
    session_id: str,
    approved_summary: Dict[str, Any],
    approved_by_user_id: str,
) -> Dict[str, Any]:
    validate_review_context(clinic_id, session_id)
    approved_summary = validate_approved_summary(approved_summary, approved_by_user_id)

    try:
        consultation = await consultation_repo.approve_consultation_summary(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            approved_summary=approved_summary,
            approved_by_user_id=approved_by_user_id,
        )
    except InvalidReviewInputError:
        raise
    except Exception as exc:
        raise ReviewWorkflowError(
            f"Failed to approve clinical summary: {exc}"
        ) from exc

    return {
        "ok": True,
        "consultation": consultation,
        "approved_summary": approved_summary,
        "message": "Clinical summary approved by doctor.",
    }


# ---------------------------------------------------------------------------
# 7. validate_rejection_reason
# ---------------------------------------------------------------------------


def validate_rejection_reason(rejected_reason: str) -> str:
    if not rejected_reason or not str(rejected_reason).strip():
        raise InvalidReviewInputError("'rejected_reason' must not be empty")
    return rejected_reason


# ---------------------------------------------------------------------------
# 8. reject_summary_after_review
# ---------------------------------------------------------------------------


async def reject_summary_after_review(
    pool: Any,
    clinic_id: str,
    session_id: str,
    rejected_reason: str,
    rejected_by_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    validate_review_context(clinic_id, session_id)
    validate_rejection_reason(rejected_reason)

    if rejected_by_user_id is not None and not str(rejected_by_user_id).strip():
        raise InvalidReviewInputError(
            "'rejected_by_user_id' must not be empty if provided"
        )

    try:
        consultation = await consultation_repo.reject_consultation_summary(
            pool=pool,
            clinic_id=clinic_id,
            session_id=session_id,
            rejected_reason=rejected_reason,
            rejected_by_user_id=rejected_by_user_id,
        )
    except InvalidReviewInputError:
        raise
    except Exception as exc:
        raise ReviewWorkflowError(
            f"Failed to reject clinical summary: {exc}"
        ) from exc

    return {
        "ok": True,
        "consultation": consultation,
        "rejected_reason": rejected_reason,
        "message": "Clinical summary rejected. Revision is required.",
    }
