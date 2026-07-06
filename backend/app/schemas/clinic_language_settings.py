"""
Clinic Language Settings schemas — PraxisMed Sprint 19 / Module 138.

German-first defaults for Austrian clinics. English fallback supported.
No PHI. No secrets. No Vapi credentials.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, field_validator, model_validator

ALLOWED_LANGUAGES: frozenset[str] = frozenset({"de", "en"})
ALLOWED_VAPI_MODES: frozenset[str] = frozenset(
    {"german_first", "english_first", "bilingual_auto"}
)
ALLOWED_UI_LANGUAGES: frozenset[str] = frozenset({"de", "en"})

# ---------------------------------------------------------------------------
# Read (response)
# ---------------------------------------------------------------------------


class ClinicLanguageSettingsRead(BaseModel):
    ok: bool = True
    clinic_id: str
    primary_language: str = "de"
    fallback_language: str = "en"
    supported_languages: List[str] = ["de", "en"]
    default_patient_language: str = "de"
    vapi_assistant_language_mode: str = "german_first"
    clinic_ui_language: str = "de"
    updated_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Update (request body)
# ---------------------------------------------------------------------------


class ClinicLanguageSettingsUpdate(BaseModel):
    primary_language: Optional[str] = None
    fallback_language: Optional[str] = None
    supported_languages: Optional[List[str]] = None
    default_patient_language: Optional[str] = None
    vapi_assistant_language_mode: Optional[str] = None
    clinic_ui_language: Optional[str] = None

    @field_validator("primary_language")
    @classmethod
    def _validate_primary_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_LANGUAGES:
            raise ValueError(
                f"primary_language must be one of {sorted(ALLOWED_LANGUAGES)}; got {v!r}"
            )
        return v

    @field_validator("fallback_language")
    @classmethod
    def _validate_fallback_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_LANGUAGES:
            raise ValueError(
                f"fallback_language must be one of {sorted(ALLOWED_LANGUAGES)}; got {v!r}"
            )
        return v

    @field_validator("supported_languages")
    @classmethod
    def _validate_supported_languages(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            if len(v) == 0:
                raise ValueError("supported_languages cannot be empty")
            invalid = [lang for lang in v if lang not in ALLOWED_LANGUAGES]
            if invalid:
                raise ValueError(
                    f"supported_languages contains unsupported values: {invalid}. "
                    f"Allowed: {sorted(ALLOWED_LANGUAGES)}"
                )
        return v

    @field_validator("default_patient_language")
    @classmethod
    def _validate_default_patient_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_LANGUAGES:
            raise ValueError(
                f"default_patient_language must be one of {sorted(ALLOWED_LANGUAGES)}; got {v!r}"
            )
        return v

    @field_validator("vapi_assistant_language_mode")
    @classmethod
    def _validate_vapi_mode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_VAPI_MODES:
            raise ValueError(
                f"vapi_assistant_language_mode must be one of "
                f"{sorted(ALLOWED_VAPI_MODES)}; got {v!r}"
            )
        return v

    @field_validator("clinic_ui_language")
    @classmethod
    def _validate_clinic_ui_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_UI_LANGUAGES:
            raise ValueError(
                f"clinic_ui_language must be one of {sorted(ALLOWED_UI_LANGUAGES)}; got {v!r}"
            )
        return v

    @model_validator(mode="after")
    def _validate_primary_in_supported(self) -> "ClinicLanguageSettingsUpdate":
        primary = self.primary_language
        supported = self.supported_languages
        if primary is not None and supported is not None:
            if primary not in supported:
                raise ValueError(
                    f"primary_language {primary!r} must be in supported_languages {supported}"
                )
        return self
