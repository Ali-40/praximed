"""
Pydantic schemas for patient intake link flow — PraxisMed Sprint 20 / Module 151.

Demo-only intake token links. Raw token not stored.
Consent step required on submission.
No patient history writes. No AI structuring.
No diagnosis. No medical advice. No triage scoring.
Synthetic/fake staging only. production_phi_enabled always False.
Production PHI remains NO-GO.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_VALID_LANGUAGES = frozenset({"de", "en", "ar"})
_VALID_PURPOSES = frozenset({
    "patient_history_collection",
    "phone_history_questions",
    "demo_seed",
})
_VALID_LINK_STATUSES = frozenset({"active", "submitted", "expired", "revoked"})
_VALID_SUBMISSION_STATUSES = frozenset({"submitted", "review_pending", "archived_demo"})

_FORBIDDEN_ANSWER_PATTERNS = [
    "diagnosis_score", "risk_score", "triage_score", "medical_advice",
    "treatment_recommendation", "sk-", "jwt", "password", "secret", "DATABASE_URL",
]


def _reject_forbidden_answer_keys(obj: Any, path: str = "") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            k_lower = k.lower()
            for pattern in _FORBIDDEN_ANSWER_PATTERNS:
                if pattern in k_lower:
                    raise ValueError(
                        f"Answer key {k!r} at {path!r} contains forbidden pattern {pattern!r}. "
                        "No scoring, diagnosis, secrets, or advice fields allowed."
                    )
            _reject_forbidden_answer_keys(v, path=f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _reject_forbidden_answer_keys(item, path=f"{path}[{i}]")


# ── Admin / protected create ───────────────────────────────────────────────────


class PatientIntakeLinkCreate(BaseModel):
    template_id: str
    language: str = "de"
    purpose: str = "patient_history_collection"
    expires_at: datetime
    patient_id: Optional[str] = None
    appointment_request_id: Optional[str] = None
    max_submissions: int = 1
    synthetic_demo: bool = True
    production_phi_enabled: bool = False

    @field_validator("template_id")
    @classmethod
    def template_id_nonempty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("template_id must not be empty")
        return v.strip()

    @field_validator("language")
    @classmethod
    def language_valid(cls, v: str) -> str:
        if v not in _VALID_LANGUAGES:
            raise ValueError(f"language must be one of {sorted(_VALID_LANGUAGES)!r}; got {v!r}")
        return v

    @field_validator("purpose")
    @classmethod
    def purpose_valid(cls, v: str) -> str:
        if v not in _VALID_PURPOSES:
            raise ValueError(f"purpose must be one of {sorted(_VALID_PURPOSES)!r}; got {v!r}")
        return v

    @field_validator("max_submissions")
    @classmethod
    def max_submissions_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_submissions must be >= 1")
        return v

    @field_validator("expires_at")
    @classmethod
    def expires_at_future(cls, v: datetime) -> datetime:
        now = datetime.now(tz=timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= now:
            raise ValueError("expires_at must be in the future")
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


# ── Admin / protected read ─────────────────────────────────────────────────────


class PatientIntakeLinkRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: Optional[str] = None
    appointment_request_id: Optional[str] = None
    template_id: str
    token_prefix: str
    status: str
    purpose: str
    language: str
    expires_at: Any
    max_submissions: int
    submission_count: int
    synthetic_demo: bool
    production_phi_enabled: bool = False
    created_by_user_id: Optional[str] = None
    created_at: Any
    updated_at: Any


# ── Public template payload ────────────────────────────────────────────────────


class PatientIntakePublicTemplateRead(BaseModel):
    link_id: str
    clinic_id: str
    language: str
    purpose: str
    template_key: str
    display_name: str
    specialty: str
    primary_language: str
    template_schema: Dict[str, Any]
    escalation_keywords: List[str]
    synthetic_demo: bool = True
    production_phi_enabled: bool = False
    demo_notice: str = (
        "Demo staging intake only. Do not enter real medical information."
    )


# ── Public submission ──────────────────────────────────────────────────────────


class PatientIntakeSubmissionCreate(BaseModel):
    language: str = "de"
    answers: Dict[str, Any] = {}
    skipped_questions: List[str] = []
    consent_granted: bool = True
    consent_text_version: str = "v1"
    consent_text_snapshot: str = (
        "I understand this is a demo intake and consent to submit synthetic information for testing."
    )
    synthetic_demo: bool = True
    production_phi_enabled: bool = False

    @field_validator("language")
    @classmethod
    def language_valid(cls, v: str) -> str:
        if v not in _VALID_LANGUAGES:
            raise ValueError(f"language must be one of {sorted(_VALID_LANGUAGES)!r}; got {v!r}")
        return v

    @field_validator("answers")
    @classmethod
    def answers_no_forbidden_keys(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        _reject_forbidden_answer_keys(v, path="answers")
        return v

    @field_validator("consent_granted")
    @classmethod
    def consent_must_be_granted(cls, v: bool) -> bool:
        if not v:
            raise ValueError("consent_granted must be True to submit intake")
        return v

    @field_validator("production_phi_enabled")
    @classmethod
    def phi_always_false(cls, v: bool) -> bool:
        if v:
            raise ValueError("production_phi_enabled must always be False")
        return False


# ── Submission read ────────────────────────────────────────────────────────────


class PatientIntakeSubmissionRead(BaseModel):
    id: str
    intake_link_id: str
    clinic_id: str
    patient_id: Optional[str] = None
    appointment_request_id: Optional[str] = None
    template_id: str
    consent_event_id: str
    language: str
    answers: Dict[str, Any]
    skipped_questions: List[str]
    escalation_matches: List[str]
    status: str
    synthetic_demo: bool
    production_phi_enabled: bool = False
    submitted_at: Any
    created_at: Any


# ── Revoke ─────────────────────────────────────────────────────────────────────


class PatientIntakeLinkRevoke(BaseModel):
    reason: Optional[str] = None


# ── Responses ─────────────────────────────────────────────────────────────────


class PatientIntakeLinkCreateResponse(BaseModel):
    ok: bool
    link: Optional[PatientIntakeLinkRead] = None
    intake_url: Optional[str] = None
    raw_token_shown_once: bool = True
    production_phi_enabled: bool = False
    message: Optional[str] = None


class PatientIntakeLinkResponse(BaseModel):
    ok: bool
    link: Optional[Dict[str, Any]] = None
    production_phi_enabled: bool = False
    message: Optional[str] = None


class PatientIntakeLinkListResponse(BaseModel):
    ok: bool
    links: List[Dict[str, Any]]
    total: int
    production_phi_enabled: bool = False


class PatientIntakePublicResponse(BaseModel):
    ok: bool
    template: Optional[PatientIntakePublicTemplateRead] = None
    demo_notice: str = "Demo staging intake only. Do not enter real medical information."
    production_phi_enabled: bool = False
    message: Optional[str] = None


class PatientIntakeSubmitResponse(BaseModel):
    ok: bool
    submission_id: Optional[str] = None
    consent_event_id: Optional[str] = None
    escalation_matches: List[str] = []
    status: str = "submitted"
    production_phi_enabled: bool = False
    message: Optional[str] = None


class PatientIntakeSubmissionListResponse(BaseModel):
    ok: bool
    submissions: List[Dict[str, Any]]
    total: int
    production_phi_enabled: bool = False
