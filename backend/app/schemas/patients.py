"""
Pydantic schemas for patient endpoints — PraxisMed Sprint 2 / Module 26
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_VALID_STATUSES = frozenset({"active", "inactive", "archived"})


class PatientCreate(BaseModel):
    clinic_id: str
    full_name: str
    external_patient_id: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_language: str = "de-AT"
    status: str = "active"
    notes: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("full_name must not be empty")
        return v

    @field_validator("preferred_language")
    @classmethod
    def preferred_language_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("preferred_language must not be empty")
        return v

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(_VALID_STATUSES)!r}")
        return v


class PatientUpsertByExternalId(BaseModel):
    clinic_id: str
    external_patient_id: str
    full_name: str
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_language: str = "de-AT"
    status: str = "active"
    notes: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("external_patient_id")
    @classmethod
    def external_patient_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("external_patient_id must not be empty")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("full_name must not be empty")
        return v

    @field_validator("preferred_language")
    @classmethod
    def preferred_language_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("preferred_language must not be empty")
        return v

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(_VALID_STATUSES)!r}")
        return v


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_language: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PatientUpdate":
        fields = (
            self.full_name, self.date_of_birth, self.phone, self.email,
            self.preferred_language, self.status, self.notes, self.raw_payload,
        )
        if all(v is None for v in fields):
            raise ValueError("At least one update field must be provided")
        return self

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("full_name must not be empty")
        return v

    @field_validator("preferred_language")
    @classmethod
    def preferred_language_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("preferred_language must not be empty")
        return v

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(_VALID_STATUSES)!r}")
        return v


class PatientResponse(BaseModel):
    ok: bool
    patient: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class PatientListResponse(BaseModel):
    ok: bool
    patients: List[Dict[str, Any]]
    message: Optional[str] = None
