"""
Pydantic request/response schemas for Vapi tool endpoints — PraxisMed Sprint 1 / Module 12
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator, model_validator


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
