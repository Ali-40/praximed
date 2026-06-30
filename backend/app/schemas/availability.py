"""
Pydantic request/response schemas for availability endpoints — PraxisMed Sprint 1 / Module 9
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator, model_validator


class AvailabilityCheckRequest(BaseModel):
    clinic_ref: str
    starts_at: datetime
    ends_at: datetime

    @field_validator("clinic_ref")
    @classmethod
    def clinic_ref_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_ref must not be empty")
        return v

    @model_validator(mode="after")
    def ends_after_starts(self) -> "AvailabilityCheckRequest":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class AvailabilityCheckResponse(BaseModel):
    ok: bool
    clinic_id: Optional[str]
    available: bool
    starts_at: datetime
    ends_at: datetime
    reason: Optional[str] = None


class SuggestedSlotsRequest(BaseModel):
    clinic_ref: str
    date: date
    limit: int = 5

    @field_validator("clinic_ref")
    @classmethod
    def clinic_ref_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_ref must not be empty")
        return v

    @field_validator("limit")
    @classmethod
    def limit_in_range(cls, v: int) -> int:
        if v < 1 or v > 20:
            raise ValueError("limit must be between 1 and 20")
        return v


class SuggestedSlot(BaseModel):
    starts_at: datetime
    ends_at: datetime


class SuggestedSlotsResponse(BaseModel):
    ok: bool
    clinic_id: Optional[str]
    slots: List[SuggestedSlot]
    reason: Optional[str] = None
