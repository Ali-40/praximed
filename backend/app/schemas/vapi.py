"""
Pydantic request/response schemas for Vapi tool endpoints — PraxisMed Sprint 1 / Modules 12, 18
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_VALID_URGENCY_LEVELS = frozenset({"low", "normal", "urgent", "emergency"})


class VapiAvailabilityCheckRequest(BaseModel):
    clinic_ref: str
    starts_at: datetime
    ends_at: datetime
    caller_phone: Optional[str] = None
    reason: Optional[str] = None

    @field_validator("clinic_ref")
    @classmethod
    def clinic_ref_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_ref must not be empty")
        return v

    @model_validator(mode="after")
    def ends_after_starts(self) -> "VapiAvailabilityCheckRequest":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class VapiAvailabilityCheckResponse(BaseModel):
    ok: bool
    available: bool
    message: str
    starts_at: datetime
    ends_at: datetime


class VapiSlotSuggestionRequest(BaseModel):
    clinic_ref: str
    date: date
    limit: int = 3
    caller_phone: Optional[str] = None
    reason: Optional[str] = None

    @field_validator("clinic_ref")
    @classmethod
    def clinic_ref_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_ref must not be empty")
        return v

    @field_validator("limit")
    @classmethod
    def limit_in_range(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError("limit must be between 1 and 10")
        return v


class VapiSuggestedSlot(BaseModel):
    starts_at: datetime
    ends_at: datetime


class VapiSlotSuggestionResponse(BaseModel):
    ok: bool
    message: str
    slots: List[VapiSuggestedSlot]


# ---------------------------------------------------------------------------
# Module 18 — Appointment capture schemas
# ---------------------------------------------------------------------------


class VapiAppointmentCaptureRequest(BaseModel):
    clinic_ref: str
    call_id: str
    patient_name: str
    caller_phone: Optional[str] = None
    patient_email: Optional[str] = None
    date_of_birth: Optional[date] = None
    reason: Optional[str] = None
    preferred_starts_at: Optional[datetime] = None
    preferred_ends_at: Optional[datetime] = None
    urgency_level: str = "normal"
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("clinic_ref")
    @classmethod
    def clinic_ref_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_ref must not be empty")
        return v

    @field_validator("call_id")
    @classmethod
    def call_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("call_id must not be empty")
        return v

    @field_validator("patient_name")
    @classmethod
    def patient_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("patient_name must not be empty")
        return v

    @field_validator("urgency_level")
    @classmethod
    def urgency_valid(cls, v: str) -> str:
        if v not in _VALID_URGENCY_LEVELS:
            raise ValueError(
                f"urgency_level must be one of {sorted(_VALID_URGENCY_LEVELS)!r}"
            )
        return v

    @model_validator(mode="after")
    def preferred_time_range_valid(self) -> "VapiAppointmentCaptureRequest":
        if self.preferred_starts_at is not None and self.preferred_ends_at is not None:
            if self.preferred_ends_at <= self.preferred_starts_at:
                raise ValueError("preferred_ends_at must be after preferred_starts_at")
        return self


class VapiAppointmentCaptureResponse(BaseModel):
    ok: bool
    message: str
    request: Optional[Dict[str, Any]] = None
