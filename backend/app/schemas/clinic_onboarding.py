"""
Pydantic schemas for clinic onboarding request endpoints — PraxisMed Sprint 19 / Module 132.

Public pilot/onboarding intake form. No patient PHI. No automatic tenant creation.
production_phi_enabled is always forced to false — it cannot be accepted from public input.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_VALID_LANGUAGES = frozenset({"de", "en"})
_VALID_STATUSES = frozenset({"submitted", "reviewed", "demo_booked", "pilot_approved", "rejected", "archived"})

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ClinicOnboardingRequestCreate(BaseModel):
    clinic_name: str
    clinic_type: Optional[str] = None
    specialty: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    doctor_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    preferred_language: str = "de"
    fallback_language: str = "en"
    supported_languages: List[str] = ["de", "en"]
    workflow_notes: Optional[str] = None
    estimated_call_volume: Optional[str] = None
    current_booking_system: Optional[str] = None
    wants_ai_phone_intake: bool = True
    wants_dashboard: bool = True
    wants_notifications: bool = False
    pilot_interest_level: str = "new"
    source: str = "onboarding_page"
    consent_pilot_contact: bool
    acknowledges_no_phi: bool

    @field_validator("clinic_name")
    @classmethod
    def clinic_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_name must not be empty")
        return v.strip()

    @field_validator("doctor_name")
    @classmethod
    def doctor_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("doctor_name must not be empty")
        return v.strip()

    @field_validator("contact_email")
    @classmethod
    def contact_email_valid(cls, v: str) -> str:
        if not v or not _EMAIL_RE.match(v.strip()):
            raise ValueError("contact_email must be a valid email address")
        return v.strip().lower()

    @field_validator("preferred_language")
    @classmethod
    def preferred_language_valid(cls, v: str) -> str:
        norm = v.strip().lower()
        if norm not in _VALID_LANGUAGES:
            raise ValueError(f"preferred_language must be one of {sorted(_VALID_LANGUAGES)!r}")
        return norm

    @field_validator("fallback_language")
    @classmethod
    def fallback_language_valid(cls, v: str) -> str:
        norm = v.strip().lower()
        if norm not in _VALID_LANGUAGES:
            raise ValueError(f"fallback_language must be one of {sorted(_VALID_LANGUAGES)!r}")
        return norm

    @field_validator("supported_languages")
    @classmethod
    def supported_languages_valid(cls, v: List[str]) -> List[str]:
        normed = [lang.strip().lower() for lang in v]
        invalid = [lang for lang in normed if lang not in _VALID_LANGUAGES]
        if invalid:
            raise ValueError(f"supported_languages contains invalid values: {invalid!r}")
        return normed

    @model_validator(mode="after")
    def consent_required(self) -> "ClinicOnboardingRequestCreate":
        if not self.consent_pilot_contact:
            raise ValueError("consent_pilot_contact must be true to submit an onboarding request")
        if not self.acknowledges_no_phi:
            raise ValueError("acknowledges_no_phi must be true to submit an onboarding request")
        return self

    @model_validator(mode="after")
    def preferred_language_in_supported(self) -> "ClinicOnboardingRequestCreate":
        if self.preferred_language not in self.supported_languages:
            raise ValueError("preferred_language must be included in supported_languages")
        return self


class ClinicOnboardingRequestRead(BaseModel):
    id: str
    clinic_name: str
    clinic_type: Optional[str] = None
    specialty: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    doctor_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    preferred_language: str
    fallback_language: str
    supported_languages: Any
    workflow_notes: Optional[str] = None
    estimated_call_volume: Optional[str] = None
    current_booking_system: Optional[str] = None
    wants_ai_phone_intake: bool
    wants_dashboard: bool
    wants_notifications: bool
    pilot_interest_level: str
    status: str
    source: str
    consent_pilot_contact: bool
    acknowledges_no_phi: bool
    production_phi_enabled: bool
    created_at: Any
    updated_at: Any


class ClinicOnboardingRequestStatusUpdate(BaseModel):
    status: str
    reviewer_notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(_VALID_STATUSES)!r}")
        return v


class ClinicOnboardingRequestResponse(BaseModel):
    ok: bool
    request: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class ClinicOnboardingRequestListResponse(BaseModel):
    ok: bool
    requests: List[Dict[str, Any]]
    total: int
