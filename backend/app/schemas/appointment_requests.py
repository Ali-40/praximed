"""
Pydantic request/response schemas for appointment request endpoints — PraxisMed Sprint 1 / Module 17
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_VALID_SOURCES = frozenset({"vapi", "whatsapp", "web", "staff", "system"})
_VALID_STATUSES = frozenset({"new", "confirmed", "rejected", "callback_needed", "cancelled", "archived"})
_VALID_URGENCY_LEVELS = frozenset({"low", "normal", "urgent", "emergency"})


class AppointmentRequestCreate(BaseModel):
    clinic_id: str
    source: str
    patient_name: str
    source_ref: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    date_of_birth: Optional[date] = None
    reason: Optional[str] = None
    preferred_starts_at: Optional[datetime] = None
    preferred_ends_at: Optional[datetime] = None
    urgency_level: str = "normal"
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("patient_name")
    @classmethod
    def patient_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("patient_name must not be empty")
        return v

    @field_validator("source")
    @classmethod
    def source_valid(cls, v: str) -> str:
        if v not in _VALID_SOURCES:
            raise ValueError(f"source must be one of {sorted(_VALID_SOURCES)!r}")
        return v

    @field_validator("urgency_level")
    @classmethod
    def urgency_valid(cls, v: str) -> str:
        if v not in _VALID_URGENCY_LEVELS:
            raise ValueError(f"urgency_level must be one of {sorted(_VALID_URGENCY_LEVELS)!r}")
        return v

    @model_validator(mode="after")
    def preferred_time_range_valid(self) -> "AppointmentRequestCreate":
        if self.preferred_starts_at is not None and self.preferred_ends_at is not None:
            if self.preferred_ends_at <= self.preferred_starts_at:
                raise ValueError("preferred_ends_at must be after preferred_starts_at")
        return self


class AppointmentRequestUpdateStatus(BaseModel):
    status: str
    action_required: Optional[bool] = None

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(_VALID_STATUSES)!r}")
        return v


class AppointmentRequestAssign(BaseModel):
    assigned_user_id: str

    @field_validator("assigned_user_id")
    @classmethod
    def assigned_user_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("assigned_user_id must not be empty")
        return v


class AppointmentRequestResponse(BaseModel):
    ok: bool
    request: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class AppointmentRequestListResponse(BaseModel):
    ok: bool
    requests: List[Dict[str, Any]]
    message: Optional[str] = None
