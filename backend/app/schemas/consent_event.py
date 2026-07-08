"""
Pydantic schemas for consent_events — PraxisMed Sprint 20 / Module 148.

Consent ledger schemas: who consented, when, for what purpose, via what channel,
in which language. No real patient PHI. No diagnosis. No medical advice.
production_phi_enabled always False. Synthetic/fake staging only.
Production PHI remains NO-GO.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_VALID_CHANNELS = frozenset({
    "onboarding_form",
    "intake_link",
    "phone_call",
    "staff_console",
    "developer_console",
    "import_demo",
})
_VALID_LANGUAGES = frozenset({"de", "en", "ar"})
_VALID_PURPOSES = frozenset({
    "appointment_intake",
    "patient_history_collection",
    "phone_history_questions",
    "demo_seed",
    "data_processing_acknowledgement",
})

# Reject metadata keys that look like diagnosis, medical advice, or secrets.
_FORBIDDEN_METADATA_PATTERNS = [
    "diagnosis",
    "medical_advice",
    "triage",
    "prescription",
    "sk-",
    "vapi_live",
    "jwt",
    "password",
    "secret",
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


class ConsentEventCreate(BaseModel):
    clinic_id: str
    patient_id: Optional[str] = None
    appointment_request_id: Optional[str] = None
    consent_subject_type: str = "patient"
    consent_subject_ref: Optional[str] = None
    purpose: str
    scope: str
    channel: str
    language: str = "de"
    consent_text_version: str
    consent_text_snapshot: str
    granted: bool = True
    captured_by_system: Optional[str] = None
    metadata: Dict[str, Any] = {}

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v.strip()

    @field_validator("purpose")
    @classmethod
    def purpose_valid(cls, v: str) -> str:
        if v not in _VALID_PURPOSES:
            raise ValueError(
                f"purpose must be one of {sorted(_VALID_PURPOSES)!r}; got {v!r}"
            )
        return v

    @field_validator("channel")
    @classmethod
    def channel_valid(cls, v: str) -> str:
        if v not in _VALID_CHANNELS:
            raise ValueError(
                f"channel must be one of {sorted(_VALID_CHANNELS)!r}; got {v!r}"
            )
        return v

    @field_validator("language")
    @classmethod
    def language_valid(cls, v: str) -> str:
        if v not in _VALID_LANGUAGES:
            raise ValueError(
                f"language must be one of {sorted(_VALID_LANGUAGES)!r}; got {v!r}"
            )
        return v

    @field_validator("consent_text_version")
    @classmethod
    def consent_text_version_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("consent_text_version must not be empty")
        return v.strip()

    @field_validator("consent_text_snapshot")
    @classmethod
    def consent_text_snapshot_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("consent_text_snapshot must not be empty")
        return v.strip()

    @field_validator("scope")
    @classmethod
    def scope_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("scope must not be empty")
        return v.strip()

    @field_validator("metadata")
    @classmethod
    def metadata_no_forbidden(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        _reject_forbidden_metadata(v)
        return v


class ConsentEventRead(BaseModel):
    id: str
    clinic_id: str
    patient_id: Optional[str] = None
    appointment_request_id: Optional[str] = None
    consent_subject_type: str
    consent_subject_ref: Optional[str] = None
    purpose: str
    scope: str
    channel: str
    language: str
    consent_text_version: str
    granted: bool
    revoked_at: Any = None
    revoked_by_user_id: Optional[str] = None
    revocation_reason: Optional[str] = None
    captured_by_user_id: Optional[str] = None
    captured_by_system: Optional[str] = None
    metadata: Dict[str, Any] = {}
    production_phi_enabled: bool = False
    created_at: Any
    updated_at: Any


class ConsentEventRevoke(BaseModel):
    revocation_reason: Optional[str] = None
    revoked_at: Optional[str] = None


class ConsentEventResponse(BaseModel):
    ok: bool
    event: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    production_phi_enabled: bool = False


class ConsentEventListResponse(BaseModel):
    ok: bool
    events: List[Dict[str, Any]]
    total: int
    production_phi_enabled: bool = False
