"""
Pydantic schemas for clinic Vapi binding endpoints — PraxisMed Sprint 19 / Module 145.

Secret reference names only — never actual secret values.
No VAPI_API_KEY value accepted or returned.
No VAPI_WEBHOOK_SECRET value accepted or returned.
No PHI. No patient data. production_phi_enabled always False.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator

_VALID_STATUSES = frozenset({"draft", "configured", "disabled", "revoked"})
_VALID_LANGUAGE_MODES = frozenset({"german_first", "english_first", "bilingual_auto"})

# Reference names must be uppercase alphanumeric + underscores, 3–100 chars.
# This format accepts VAPI_API_KEY_REF_CLINIC_DEMO and rejects sk-..., vapi_live_..., JWTs.
_REF_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,99}$")

# Belt-and-suspenders: also reject values containing these literal patterns
# even if they somehow pass the regex (defence in depth).
_FORBIDDEN_VALUE_PATTERNS = [
    "sk-",       # OpenAI-style key prefix
    "vapi_live", # Vapi live credential prefix
]


def _validate_secret_ref(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    v = value.strip()
    for bad in _FORBIDDEN_VALUE_PATTERNS:
        if bad in v.lower():
            raise ValueError(
                f"{field_name} appears to contain an actual secret value "
                f"(matched forbidden pattern '{bad}'). "
                f"Supply a reference name only, e.g. VAPI_API_KEY_REF_CLINIC_DEMO."
            )
    if not _REF_NAME_RE.match(v):
        raise ValueError(
            f"{field_name} must be an uppercase reference name "
            f"(e.g. VAPI_API_KEY_REF_CLINIC_DEMO). "
            f"Only uppercase letters, digits, and underscores are allowed."
        )
    return v


class ClinicVapiBindingCreate(BaseModel):
    clinic_id: str
    api_key_secret_ref: str
    webhook_secret_ref: str
    language_mode: str = "german_first"

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v.strip()

    @field_validator("api_key_secret_ref")
    @classmethod
    def api_key_ref_valid(cls, v: str) -> str:
        return _validate_secret_ref(v, "api_key_secret_ref")

    @field_validator("webhook_secret_ref")
    @classmethod
    def webhook_ref_valid(cls, v: str) -> str:
        return _validate_secret_ref(v, "webhook_secret_ref")

    @field_validator("language_mode")
    @classmethod
    def language_mode_valid(cls, v: str) -> str:
        if v not in _VALID_LANGUAGE_MODES:
            raise ValueError(
                f"language_mode must be one of {sorted(_VALID_LANGUAGE_MODES)!r}; got {v!r}"
            )
        return v


class ClinicVapiBindingRead(BaseModel):
    id: str
    clinic_id: str
    assistant_id: Optional[str] = None
    phone_number_id: Optional[str] = None
    vapi_project_id: Optional[str] = None
    api_key_secret_ref: str
    webhook_secret_ref: str
    assistant_config_version: Optional[str] = None
    language_mode: str
    status: str
    created_by_user_id: Optional[str] = None
    created_at: Any
    updated_at: Any
    production_phi_enabled: bool = False


class ClinicVapiBindingUpdateStatus(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in _VALID_STATUSES:
            raise ValueError(
                f"status must be one of {sorted(_VALID_STATUSES)!r}; got {v!r}"
            )
        return v


class ClinicVapiBindingResponse(BaseModel):
    ok: bool
    binding: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    production_phi_enabled: bool = False


class ClinicVapiBindingListResponse(BaseModel):
    ok: bool
    bindings: List[Dict[str, Any]]
    total: int
    production_phi_enabled: bool = False
