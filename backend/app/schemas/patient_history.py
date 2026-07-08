"""
Pydantic schemas for FHIR-aligned patient history — PraxisMed Sprint 20 / Module 149.

Seven FHIR R4 resource types:
  AllergyIntolerance, MedicationStatement, Condition (patient-reported),
  Procedure, Immunization, FamilyMemberHistory, Observation (social history).

No real patient PHI. No diagnosis generated. No medical advice. No triage scoring.
Synthetic/fake staging only. production_phi_enabled always False.
Production PHI remains NO-GO.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator

_VALID_STATUSES = frozenset({"unverified", "approved", "rejected", "superseded"})
_VALID_SOURCE_TYPES = frozenset({
    "staff_console", "intake_link", "phone_call",
    "ai_proposal", "demo_seed", "import_demo",
})
_VALID_HISTORY_TYPES = frozenset({
    "allergies", "medications", "conditions", "procedures",
    "immunizations", "family-history", "social-history",
})
_HISTORY_TYPE_TO_TABLE = {
    "allergies":      "patient_history_allergies",
    "medications":    "patient_history_medications",
    "conditions":     "patient_history_conditions",
    "procedures":     "patient_history_procedures",
    "immunizations":  "patient_history_immunizations",
    "family-history": "patient_history_family_history",
    "social-history": "patient_history_social_history",
}
_HISTORY_TYPE_TO_FHIR = {
    "allergies":      "AllergyIntolerance",
    "medications":    "MedicationStatement",
    "conditions":     "Condition",
    "procedures":     "Procedure",
    "immunizations":  "Immunization",
    "family-history": "FamilyMemberHistory",
    "social-history": "Observation",
}

_FORBIDDEN_METADATA_PATTERNS = [
    "diagnosis", "medical_advice", "triage", "prescription",
    "sk-", "vapi_live", "jwt", "password", "secret",
    "treatment_recommendation",
]


def _reject_forbidden_metadata(metadata: Dict[str, Any]) -> None:
    for key in metadata:
        key_lower = key.lower()
        for pattern in _FORBIDDEN_METADATA_PATTERNS:
            if pattern in key_lower:
                raise ValueError(
                    f"metadata key {key!r} contains a forbidden pattern ({pattern!r}). "
                    "No diagnosis, medical advice, triage, or secret fields allowed."
                )


def _validate_not_empty(v: str, field: str) -> str:
    if not v or not str(v).strip():
        raise ValueError(f"{field} must not be empty")
    return v.strip()


# ── Common base for Create payloads ─────────────────────────────────────────


class HistoryEntryCommonCreate(BaseModel):
    patient_id: str
    consent_event_id: str
    appointment_request_id: Optional[str] = None
    version_group_id: Optional[str] = None
    version_number: int = 1
    supersedes_entry_id: Optional[str] = None
    correction_reason: Optional[str] = None
    status: str = "unverified"
    source_type: str = "staff_console"
    source_ref: Optional[str] = None
    effective_start_date: Optional[str] = None
    effective_end_date: Optional[str] = None
    notes: Optional[str] = None
    fhir_payload: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

    @field_validator("patient_id")
    @classmethod
    def patient_id_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "patient_id")

    @field_validator("consent_event_id")
    @classmethod
    def consent_event_id_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "consent_event_id")

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(_VALID_STATUSES)!r}; got {v!r}")
        return v

    @field_validator("source_type")
    @classmethod
    def source_type_valid(cls, v: str) -> str:
        if v not in _VALID_SOURCE_TYPES:
            raise ValueError(f"source_type must be one of {sorted(_VALID_SOURCE_TYPES)!r}; got {v!r}")
        return v

    @field_validator("version_number")
    @classmethod
    def version_number_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("version_number must be >= 1")
        return v

    @field_validator("metadata")
    @classmethod
    def metadata_no_forbidden(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        _reject_forbidden_metadata(v)
        return v


# ── AllergyIntolerance ───────────────────────────────────────────────────────


class AllergyHistoryCreate(HistoryEntryCommonCreate):
    substance_text: str
    reaction_text: Optional[str] = None
    severity: Optional[str] = None
    clinical_status: Optional[str] = None
    verification_status: Optional[str] = None
    category: Optional[str] = None
    criticality: Optional[str] = None
    onset_text: Optional[str] = None

    @field_validator("substance_text")
    @classmethod
    def substance_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "substance_text")


class AllergyHistoryRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    consent_event_id: str
    appointment_request_id: Optional[str] = None
    version_group_id: str
    version_number: int
    status: str
    source_type: str
    fhir_resource_type: str
    substance_text: str
    reaction_text: Optional[str] = None
    severity: Optional[str] = None
    clinical_status: Optional[str] = None
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


# ── MedicationStatement ──────────────────────────────────────────────────────


class MedicationHistoryCreate(HistoryEntryCommonCreate):
    medication_text: str
    dosage_text: Optional[str] = None
    frequency_text: Optional[str] = None
    route_text: Optional[str] = None
    medication_status: Optional[str] = None
    start_text: Optional[str] = None
    end_text: Optional[str] = None
    reason_text: Optional[str] = None

    @field_validator("medication_text")
    @classmethod
    def medication_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "medication_text")


class MedicationHistoryRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    consent_event_id: str
    version_group_id: str
    version_number: int
    status: str
    source_type: str
    fhir_resource_type: str
    medication_text: str
    dosage_text: Optional[str] = None
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


# ── Condition (patient-reported, no diagnosis generated) ─────────────────────


class ConditionHistoryCreate(HistoryEntryCommonCreate):
    condition_text: str
    clinical_status: Optional[str] = None
    verification_status: Optional[str] = None
    onset_text: Optional[str] = None
    abatement_text: Optional[str] = None
    body_site_text: Optional[str] = None
    severity_text: Optional[str] = None
    patient_reported: bool = True

    @field_validator("condition_text")
    @classmethod
    def condition_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "condition_text")


class ConditionHistoryRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    consent_event_id: str
    version_group_id: str
    version_number: int
    status: str
    source_type: str
    fhir_resource_type: str
    condition_text: str
    patient_reported: bool
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


# ── Procedure ────────────────────────────────────────────────────────────────


class ProcedureHistoryCreate(HistoryEntryCommonCreate):
    procedure_text: str
    performed_text: Optional[str] = None
    body_site_text: Optional[str] = None
    outcome_text: Optional[str] = None
    performer_text: Optional[str] = None
    reason_text: Optional[str] = None

    @field_validator("procedure_text")
    @classmethod
    def procedure_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "procedure_text")


class ProcedureHistoryRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    consent_event_id: str
    version_group_id: str
    version_number: int
    status: str
    source_type: str
    fhir_resource_type: str
    procedure_text: str
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


# ── Immunization ─────────────────────────────────────────────────────────────


class ImmunizationHistoryCreate(HistoryEntryCommonCreate):
    vaccine_text: str
    occurrence_text: Optional[str] = None
    lot_number: Optional[str] = None
    site_text: Optional[str] = None
    route_text: Optional[str] = None
    dose_number: Optional[str] = None
    series_text: Optional[str] = None
    immunization_status: Optional[str] = None

    @field_validator("vaccine_text")
    @classmethod
    def vaccine_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "vaccine_text")


class ImmunizationHistoryRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    consent_event_id: str
    version_group_id: str
    version_number: int
    status: str
    source_type: str
    fhir_resource_type: str
    vaccine_text: str
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


# ── FamilyMemberHistory ──────────────────────────────────────────────────────


class FamilyHistoryCreate(HistoryEntryCommonCreate):
    relationship_text: str
    condition_text: Optional[str] = None
    age_text: Optional[str] = None
    deceased: Optional[bool] = None
    note_text: Optional[str] = None

    @field_validator("relationship_text")
    @classmethod
    def relationship_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "relationship_text")


class FamilyHistoryRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    consent_event_id: str
    version_group_id: str
    version_number: int
    status: str
    source_type: str
    fhir_resource_type: str
    relationship_text: str
    condition_text: Optional[str] = None
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


# ── Observation / Social History (non-diagnostic) ────────────────────────────


class SocialHistoryCreate(HistoryEntryCommonCreate):
    observation_category: str
    observation_text: str
    value_text: Optional[str] = None
    period_text: Optional[str] = None

    @field_validator("observation_category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "observation_category")

    @field_validator("observation_text")
    @classmethod
    def observation_not_empty(cls, v: str) -> str:
        return _validate_not_empty(v, "observation_text")


class SocialHistoryRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    consent_event_id: str
    version_group_id: str
    version_number: int
    status: str
    source_type: str
    fhir_resource_type: str
    observation_category: str
    observation_text: str
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


# ── Status update ─────────────────────────────────────────────────────────────


class HistoryStatusUpdate(BaseModel):
    status: str
    review_note: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        allowed = {"approved", "rejected", "superseded"}
        if v not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)!r}; got {v!r}")
        return v


# ── Response wrappers ─────────────────────────────────────────────────────────


class HistoryEntryResponse(BaseModel):
    ok: bool
    entry: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    production_phi_enabled: bool = False


class HistoryEntryListResponse(BaseModel):
    ok: bool
    entries: List[Dict[str, Any]]
    total: int
    history_type: Optional[str] = None
    production_phi_enabled: bool = False


class PatientHistoryTimelineResponse(BaseModel):
    ok: bool
    patient_id: str
    clinic_id: str
    timeline: List[Dict[str, Any]]
    total: int
    production_phi_enabled: bool = False
