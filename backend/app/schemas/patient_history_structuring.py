"""
Pydantic schemas for AI structuring service — PraxisMed Sprint 20 / Module 153.

Intermediate proposal layer between intake submissions and approved history.
Local deterministic demo extraction only in this module — no external LLM.

extraction_confidence is extraction confidence only — NOT a medical judgment.
All proposals remain unverified until staff/doctor explicit approval (future module).

No diagnosis. No medical advice. No treatment recommendations. No triage scoring.
No clinical_confidence field. No diagnosis_score. No risk_score. No triage_score.
synthetic_demo always True. production_phi_enabled always False.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_VALID_PROVIDERS = frozenset({
    "local_demo_extractor",
    "claude_haiku_planned",
    "disabled_external_llm",
})
_VALID_RUN_STATUSES = frozenset({"completed", "failed", "skipped"})
_VALID_LANGUAGES = frozenset({"de", "en", "ar"})
_VALID_EXTRACTION_MODES = frozenset({
    "synthetic_demo",
    "rule_based",
    "external_llm_disabled",
})
_VALID_PROPOSAL_STATUSES = frozenset({
    "unverified",
    "rejected",
    "merged",
    "archived_demo",
})
_VALID_HISTORY_TYPES = frozenset({
    "allergies",
    "medications",
    "conditions",
    "procedures",
    "immunizations",
    "family-history",
    "social-history",
})
_VALID_FHIR_TYPES = frozenset({
    "AllergyIntolerance",
    "MedicationStatement",
    "Condition",
    "Procedure",
    "Immunization",
    "FamilyMemberHistory",
    "Observation",
})

_FORBIDDEN_FIELD_KEYS = frozenset({
    "clinical_confidence",
    "diagnosis_score",
    "risk_score",
    "triage_score",
    "medical_advice",
    "treatment_recommendation",
    "diagnosis_generated",
})


def _reject_forbidden_proposed_fields(fields: Dict[str, Any]) -> None:
    for k in fields:
        if k.lower() in _FORBIDDEN_FIELD_KEYS:
            raise ValueError(
                f"Proposed field key {k!r} is forbidden. "
                "No scoring, diagnosis, advice, or triage fields allowed."
            )


# ── Structuring run ───────────────────────────────────────────────────────────


class PatientHistoryStructuringRunRead(BaseModel):
    id: str
    clinic_id: str
    intake_submission_id: str
    intake_link_id: Optional[str] = None
    template_id: Optional[str] = None
    patient_id: Optional[str] = None
    appointment_request_id: Optional[str] = None
    consent_event_id: str
    provider: str
    provider_model: Optional[str] = None
    status: str
    language: str
    extraction_mode: str
    proposals_count: int
    error_message: Optional[str] = None
    pseudonymized_log_ref: Optional[str] = None
    synthetic_demo: bool
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


# ── Proposal read ─────────────────────────────────────────────────────────────


class PatientHistoryProposalRead(BaseModel):
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


# ── Structuring request ───────────────────────────────────────────────────────


class StructuringRequest(BaseModel):
    provider: str = "local_demo_extractor"
    extraction_mode: str = "synthetic_demo"
    synthetic_demo: bool = True
    production_phi_enabled: bool = False

    @field_validator("provider")
    @classmethod
    def provider_valid(cls, v: str) -> str:
        if v not in _VALID_PROVIDERS:
            raise ValueError(f"provider must be one of {sorted(_VALID_PROVIDERS)!r}; got {v!r}")
        return v

    @field_validator("extraction_mode")
    @classmethod
    def extraction_mode_valid(cls, v: str) -> str:
        if v not in _VALID_EXTRACTION_MODES:
            raise ValueError(f"extraction_mode must be one of {sorted(_VALID_EXTRACTION_MODES)!r}; got {v!r}")
        return v

    @field_validator("production_phi_enabled")
    @classmethod
    def phi_always_false(cls, v: bool) -> bool:
        if v:
            raise ValueError("production_phi_enabled must always be False")
        return False

    @field_validator("synthetic_demo")
    @classmethod
    def demo_always_true(cls, v: bool) -> bool:
        if not v:
            raise ValueError("synthetic_demo must always be True")
        return True


# ── Structuring result ────────────────────────────────────────────────────────


class StructuringResult(BaseModel):
    ok: bool
    run_id: Optional[str] = None
    proposals_created: int = 0
    proposal_ids: List[str] = []
    provider: str = "local_demo_extractor"
    extraction_mode: str = "synthetic_demo"
    production_phi_enabled: bool = False
    message: Optional[str] = None
    extraction_note: str = "Extraction confidence only — not a medical judgment."


# ── Proposal status update (reject / archive only) ────────────────────────────


class ProposalStatusUpdate(BaseModel):
    proposal_status: str
    reason: Optional[str] = None

    @field_validator("proposal_status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        allowed = {"rejected", "archived_demo"}
        if v not in allowed:
            raise ValueError(
                f"Only 'rejected' and 'archived_demo' are allowed in this module; got {v!r}"
            )
        return v


# ── List responses ────────────────────────────────────────────────────────────


class PatientHistoryProposalListResponse(BaseModel):
    ok: bool
    proposals: List[Dict[str, Any]]
    total: int
    production_phi_enabled: bool = False
    extraction_note: str = "Extraction confidence only — not a medical judgment."


class PatientHistoryStructuringRunResponse(BaseModel):
    ok: bool
    run: Optional[Dict[str, Any]] = None
    proposals: List[Dict[str, Any]] = []
    production_phi_enabled: bool = False
    extraction_note: str = "Extraction confidence only — not a medical judgment."
    message: Optional[str] = None
