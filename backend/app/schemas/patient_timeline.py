"""
Patient Timeline schemas — PraxisMed Sprint 20 / Module 156.

Longitudinal patient timeline aggregates approved history entries, unverified proposals,
structuring runs, consent events, and intake submissions into a chronological view.

No diagnosis. No medical advice. No triage scoring. No treatment recommendations.
No external LLM. No PHI unlock. production_phi_enabled always False.
Approved history vs unverified proposals are clearly separated.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, field_validator

_ALLOWED_ITEM_TYPES = frozenset({
    "appointment_request",
    "intake_submission",
    "consent_event",
    "structuring_run",
    "history_proposal",
    "approved_history",
})

_ALLOWED_ITEM_SOURCES = frozenset({
    "appointment_requests",
    "patient_intake_submissions",
    "consent_events",
    "patient_history_structuring_runs",
    "patient_history_proposals",
    "patient_history_allergies",
    "patient_history_medications",
    "patient_history_conditions",
    "patient_history_procedures",
    "patient_history_immunizations",
    "patient_history_family_history",
    "patient_history_social_history",
})

_FORBIDDEN_METADATA_KEYS = frozenset({
    "diagnosis",
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

_EXTRACTION_NOTE = "Extraction confidence only — not a medical judgment."


class PatientTimelineItem(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    item_type: str
    item_source: str
    title: str
    summary: Optional[str] = None
    occurred_at: Any
    status: Optional[str] = None
    history_type: Optional[str] = None
    fhir_resource_type: Optional[str] = None
    source_ref_id: Optional[str] = None
    source_route_hint: Optional[str] = None
    consent_event_id: Optional[str] = None
    production_phi_enabled: bool = False
    synthetic_demo: Optional[bool] = True
    staff_review_required: Optional[bool] = None
    is_approved_history: bool = False
    is_unverified_proposal: bool = False
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("item_type")
    @classmethod
    def item_type_must_be_allowed(cls, v: str) -> str:
        if v not in _ALLOWED_ITEM_TYPES:
            raise ValueError(
                f"item_type {v!r} is not allowed. Must be one of {sorted(_ALLOWED_ITEM_TYPES)!r}."
            )
        return v

    @field_validator("item_source")
    @classmethod
    def item_source_must_be_allowed(cls, v: str) -> str:
        if v not in _ALLOWED_ITEM_SOURCES:
            raise ValueError(
                f"item_source {v!r} is not allowed. Must be one of {sorted(_ALLOWED_ITEM_SOURCES)!r}."
            )
        return v

    @field_validator("production_phi_enabled")
    @classmethod
    def phi_must_be_false(cls, v: bool) -> bool:
        if v:
            raise ValueError(
                "production_phi_enabled must be False. Production PHI remains NO-GO."
            )
        return False

    @field_validator("metadata")
    @classmethod
    def metadata_no_forbidden_keys(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is None:
            return v
        for k in v:
            if k.lower() in _FORBIDDEN_METADATA_KEYS:
                raise ValueError(
                    f"Metadata key {k!r} is forbidden. No diagnosis, advice, scoring, or auto-approval fields."
                )
        return v


class PatientTimelineFilters(BaseModel):
    include_unverified: bool = True
    limit: int = 100


class PatientTimelineResponse(BaseModel):
    ok: bool
    clinic_id: str
    patient_id: str
    items: List[Dict[str, Any]]
    total: int
    approved_history_count: int = 0
    unverified_proposal_count: int = 0
    consent_event_count: int = 0
    intake_submission_count: int = 0
    appointment_count: int = 0
    structuring_run_count: int = 0
    include_unverified: bool = True
    production_phi_enabled: bool = False
    extraction_note: str = _EXTRACTION_NOTE


class PatientTimelineDeltaItem(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    item_type: str
    item_source: str
    title: str
    summary: Optional[str] = None
    occurred_at: Any
    status: Optional[str] = None
    history_type: Optional[str] = None
    is_approved_history: bool = False
    is_unverified_proposal: bool = False
    production_phi_enabled: bool = False

    @field_validator("production_phi_enabled")
    @classmethod
    def phi_must_be_false(cls, v: bool) -> bool:
        if v:
            raise ValueError("production_phi_enabled must be False.")
        return False


class PatientTimelineDeltaResponse(BaseModel):
    ok: bool
    clinic_id: str
    patient_id: str
    delta_anchor_status: str
    delta_anchor_at: Optional[Any] = None
    items: List[Dict[str, Any]]
    total: int
    approved_history_count: int = 0
    unverified_proposal_count: int = 0
    includes_unverified_proposals: bool = True
    since: Optional[str] = None
    production_phi_enabled: bool = False
    extraction_note: str = _EXTRACTION_NOTE
