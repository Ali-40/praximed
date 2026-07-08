"""
Pydantic schemas for anamnesis_templates — PraxisMed Sprint 20 / Module 150.

Clinic-configurable questionnaire templates for consent-first patient intake.
German-first, English fallback, Arabic-ready.

No patient answers stored in this schema. No history writes. No AI structuring.
No diagnosis. No medical advice. No triage scoring. No treatment recommendations.
Synthetic/fake staging only. production_phi_enabled always False.
Production PHI remains NO-GO.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_VALID_STATUSES = frozenset({"draft", "active", "archived"})
_VALID_LANGUAGES = frozenset({"de", "en", "ar"})
_VALID_CONSENT_PURPOSES = frozenset({
    "patient_history_collection",
    "phone_history_questions",
    "demo_seed",
})
_VALID_QUESTION_TYPES = frozenset({
    "text", "textarea", "single_select", "multi_select",
    "yes_no", "date", "number",
})
_VALID_HISTORY_TARGETS = frozenset({
    "allergies", "medications", "conditions", "procedures",
    "immunizations", "family-history", "social-history",
    "appointment-context", "none",
})

_FORBIDDEN_SCHEMA_PATTERNS = [
    "score", "risk_score", "triage_score", "diagnosis_score",
    "medical_advice", "treatment_recommendation",
    "sk-", "vapi_live", "jwt", "password", "secret", "DATABASE_URL",
]


def _reject_forbidden_schema_content(obj: Any, path: str = "") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            k_lower = k.lower()
            for pattern in _FORBIDDEN_SCHEMA_PATTERNS:
                if pattern in k_lower:
                    raise ValueError(
                        f"Template schema key {k!r} (at {path!r}) contains "
                        f"forbidden pattern {pattern!r}. "
                        "No scoring, secrets, diagnosis, or advice fields allowed."
                    )
            _reject_forbidden_schema_content(v, path=f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _reject_forbidden_schema_content(item, path=f"{path}[{i}]")


# ── Question ─────────────────────────────────────────────────────────────────


class AnamnesisTemplateQuestion(BaseModel):
    question_key: str
    history_target: str = "none"
    type: str
    label: Dict[str, str]
    help_text: Optional[Dict[str, str]] = None
    required: bool = False
    skip_allowed: bool = True
    maps_to_fhir: Optional[str] = None
    options: Optional[List[Dict[str, str]]] = None

    @field_validator("question_key")
    @classmethod
    def question_key_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("question_key must not be empty")
        return v.strip()

    @field_validator("type")
    @classmethod
    def type_valid(cls, v: str) -> str:
        if v not in _VALID_QUESTION_TYPES:
            raise ValueError(
                f"question type must be one of {sorted(_VALID_QUESTION_TYPES)!r}; got {v!r}"
            )
        return v

    @field_validator("history_target")
    @classmethod
    def history_target_valid(cls, v: str) -> str:
        if v not in _VALID_HISTORY_TARGETS:
            raise ValueError(
                f"history_target must be one of {sorted(_VALID_HISTORY_TARGETS)!r}; got {v!r}"
            )
        return v

    @field_validator("label")
    @classmethod
    def label_not_empty(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not v:
            raise ValueError("label must not be empty — at least one language required")
        return v


# ── Section ──────────────────────────────────────────────────────────────────


class AnamnesisTemplateSection(BaseModel):
    section_key: str
    title: Dict[str, str]
    description: Optional[Dict[str, str]] = None
    questions: List[AnamnesisTemplateQuestion]

    @field_validator("section_key")
    @classmethod
    def section_key_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("section_key must not be empty")
        return v.strip()

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not v:
            raise ValueError("section title must not be empty")
        return v

    @field_validator("questions")
    @classmethod
    def questions_not_empty(cls, v: List[AnamnesisTemplateQuestion]) -> List[AnamnesisTemplateQuestion]:
        if not v:
            raise ValueError("section must have at least one question")
        return v


# ── Template Schema ───────────────────────────────────────────────────────────


class AnamnesisTemplateSchemaPayload(BaseModel):
    sections: List[AnamnesisTemplateSection]

    @field_validator("sections")
    @classmethod
    def sections_not_empty(cls, v: List[AnamnesisTemplateSection]) -> List[AnamnesisTemplateSection]:
        if not v:
            raise ValueError("template_schema must have at least one section")
        return v


# ── Create ────────────────────────────────────────────────────────────────────


class AnamnesisTemplateCreate(BaseModel):
    template_key: str
    display_name: str
    specialty: str
    primary_language: str = "de"
    supported_languages: List[str] = ["de", "en"]
    template_schema: Dict[str, Any]
    escalation_keywords: List[str] = []
    consent_purpose: str = "patient_history_collection"
    synthetic_demo: bool = True
    clinic_id: Optional[str] = None
    version: int = 1

    @field_validator("template_key")
    @classmethod
    def template_key_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("template_key must not be empty")
        return v.strip()

    @field_validator("display_name")
    @classmethod
    def display_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("display_name must not be empty")
        return v.strip()

    @field_validator("specialty")
    @classmethod
    def specialty_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("specialty must not be empty")
        return v.strip()

    @field_validator("primary_language")
    @classmethod
    def primary_language_valid(cls, v: str) -> str:
        if v not in _VALID_LANGUAGES:
            raise ValueError(
                f"primary_language must be one of {sorted(_VALID_LANGUAGES)!r}; got {v!r}"
            )
        return v

    @field_validator("supported_languages")
    @classmethod
    def supported_languages_valid(cls, v: List[str]) -> List[str]:
        for lang in v:
            if lang not in _VALID_LANGUAGES:
                raise ValueError(
                    f"supported_languages may only contain {sorted(_VALID_LANGUAGES)!r}; got {lang!r}"
                )
        return v

    @field_validator("consent_purpose")
    @classmethod
    def consent_purpose_valid(cls, v: str) -> str:
        if v not in _VALID_CONSENT_PURPOSES:
            raise ValueError(
                f"consent_purpose must be one of {sorted(_VALID_CONSENT_PURPOSES)!r}; got {v!r}"
            )
        return v

    @field_validator("version")
    @classmethod
    def version_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("version must be >= 1")
        return v

    @field_validator("template_schema")
    @classmethod
    def template_schema_valid(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if "sections" not in v:
            raise ValueError("template_schema must contain 'sections'")
        if not v["sections"]:
            raise ValueError("template_schema sections must not be empty")
        _reject_forbidden_schema_content(v, path="template_schema")
        return v

    @model_validator(mode="after")
    def primary_language_in_supported(self) -> "AnamnesisTemplateCreate":
        if self.primary_language not in self.supported_languages:
            raise ValueError(
                f"primary_language {self.primary_language!r} must be in supported_languages {self.supported_languages!r}"
            )
        return self


# ── Update ────────────────────────────────────────────────────────────────────


class AnamnesisTemplateUpdate(BaseModel):
    display_name: Optional[str] = None
    template_schema: Optional[Dict[str, Any]] = None
    escalation_keywords: Optional[List[str]] = None

    @field_validator("template_schema")
    @classmethod
    def template_schema_valid(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is not None:
            if "sections" not in v or not v["sections"]:
                raise ValueError("template_schema must contain non-empty sections")
            _reject_forbidden_schema_content(v, path="template_schema")
        return v


class AnamnesisTemplateStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        allowed = {"active", "archived"}
        if v not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)!r}; got {v!r}")
        return v


# ── Read + Response ──────────────────────────────────────────────────────────


class AnamnesisTemplateRead(BaseModel):
    id: str
    clinic_id: Optional[str] = None
    template_key: str
    display_name: str
    specialty: str
    version: int
    status: str
    primary_language: str
    supported_languages: List[str]
    template_schema: Dict[str, Any]
    escalation_keywords: List[str]
    consent_purpose: str
    synthetic_demo: bool
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


class AnamnesisTemplateResponse(BaseModel):
    ok: bool
    template: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    production_phi_enabled: bool = False


class AnamnesisTemplateListResponse(BaseModel):
    ok: bool
    templates: List[Dict[str, Any]]
    total: int
    production_phi_enabled: bool = False
