"""
Pydantic schemas for the doctor/staff review workflow — PraxisMed Sprint 20 / Module 154.

Review unverified patient history proposals and merge into patient_history_* tables
only after explicit staff/doctor action.

No auto-approval. No diagnosis generation. No medical advice. No triage scoring.
No treatment recommendations. Staff/doctor must confirm review before merge.
production_phi_enabled always False. synthetic_demo always True.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_FORBIDDEN_MERGE_KEYS = frozenset({
    "clinical_confidence",
    "diagnosis_score",
    "risk_score",
    "triage_score",
    "medical_advice",
    "treatment_recommendation",
    "diagnosis_generated",
    "auto_approved",
    "auto_confirmed",
})

_SECRET_PATTERNS = frozenset({"sk-", "vapi_live", "jwt", "DATABASE_URL", "password", "secret"})


def _reject_forbidden_merge_field_keys(fields: Dict[str, Any]) -> None:
    for k in fields:
        if k.lower() in _FORBIDDEN_MERGE_KEYS:
            raise ValueError(
                f"Field key {k!r} is forbidden. No scoring, diagnosis, advice, auto-approval, or triage fields allowed."
            )
        for pat in _SECRET_PATTERNS:
            if pat.lower() in k.lower():
                raise ValueError(f"Field key {k!r} appears to contain a secret pattern {pat!r}. Not allowed.")


# ── Merge request ─────────────────────────────────────────────────────────────


class PatientHistoryMergeRequest(BaseModel):
    edited_fields: Dict[str, Any]
    edited_fhir_payload: Optional[Dict[str, Any]] = None
    review_note: Optional[str] = None
    confirm_staff_review: bool

    @field_validator("confirm_staff_review")
    @classmethod
    def staff_review_must_be_confirmed(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "confirm_staff_review must be True. Staff/doctor review is required before merging a proposal."
            )
        return True

    @field_validator("edited_fields")
    @classmethod
    def edited_fields_no_forbidden_keys(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        _reject_forbidden_merge_field_keys(v)
        return v

    @model_validator(mode="after")
    def no_phi_unlock(self) -> "PatientHistoryMergeRequest":
        if self.edited_fields.get("production_phi_enabled") is True:
            raise ValueError("production_phi_enabled cannot be True in edited_fields.")
        return self


# ── Merge result ──────────────────────────────────────────────────────────────


class PatientHistoryMergeResult(BaseModel):
    ok: bool
    proposal_id: str
    merged_history_entry_id: str
    history_type: str
    fhir_resource_type: str
    proposal_status: str = "merged"
    production_phi_enabled: bool = False
    review_note: Optional[str] = None
    message: str = "Proposal merged into patient history after staff review."


# ── Reject request ────────────────────────────────────────────────────────────


class PatientHistoryRejectRequest(BaseModel):
    rejected_reason: Optional[str] = None
    review_note: Optional[str] = None


# ── Reject result ─────────────────────────────────────────────────────────────


class PatientHistoryRejectResult(BaseModel):
    ok: bool
    proposal_id: str
    proposal_status: str = "rejected"
    rejected_reason: Optional[str] = None
    production_phi_enabled: bool = False
    message: str = "Proposal rejected."


# ── Review queue item ─────────────────────────────────────────────────────────


class PatientHistoryReviewQueueItem(BaseModel):
    id: str
    clinic_id: str
    structuring_run_id: str
    intake_submission_id: str
    consent_event_id: str
    patient_id: Optional[str] = None
    appointment_request_id: Optional[str] = None
    proposal_status: str
    history_type: str
    fhir_resource_type: str
    source_question_key: Optional[str] = None
    extraction_confidence: Optional[float] = None
    staff_review_required: bool
    synthetic_demo: bool
    production_phi_enabled: bool = False
    created_at: Any
    extraction_note: str = "Extraction confidence only — not a medical judgment."


# ── Review detail ─────────────────────────────────────────────────────────────


class PatientHistoryProposalReviewDetail(BaseModel):
    id: str
    clinic_id: str
    structuring_run_id: str
    intake_submission_id: str
    consent_event_id: str
    patient_id: Optional[str] = None
    appointment_request_id: Optional[str] = None
    proposal_status: str
    history_type: str
    fhir_resource_type: str
    source_question_key: Optional[str] = None
    source_answer_ref: Optional[str] = None
    proposed_fields: Dict[str, Any]
    proposed_fhir_payload: Dict[str, Any]
    extraction_confidence: Optional[float] = None
    confidence_explanation: Optional[str] = None
    staff_review_required: bool
    reviewed_by_user_id: Optional[str] = None
    reviewed_at: Optional[Any] = None
    review_note: Optional[str] = None
    merged_history_entry_id: Optional[str] = None
    rejected_reason: Optional[str] = None
    synthetic_demo: bool
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any
    extraction_note: str = "Extraction confidence only — not a medical judgment."


# ── Review queue list response ────────────────────────────────────────────────


class PatientHistoryReviewQueueResponse(BaseModel):
    ok: bool
    proposals: List[Dict[str, Any]]
    total: int
    production_phi_enabled: bool = False
    extraction_note: str = "Extraction confidence only — not a medical judgment."
