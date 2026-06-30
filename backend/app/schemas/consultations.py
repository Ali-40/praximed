"""
Pydantic schemas for consultation session endpoints — PraxisMed Sprint 2 / Module 29
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator

_VALID_SOURCES = frozenset({"manual", "vapi", "web", "doctor_mobile", "system"})

_VALID_STATUSES = frozenset({
    "created", "recording", "audio_uploaded", "transcribing",
    "transcribed", "draft_ready", "approved", "rejected", "archived",
})

_VALID_APPROVAL_STATUSES = frozenset({
    "not_ready", "pending_review", "approved", "rejected",
})


class ConsultationSessionCreate(BaseModel):
    clinic_id: str
    patient_id: str
    doctor_user_id: Optional[str] = None
    source: str = "manual"
    status: str = "created"
    title: Optional[str] = None
    reason_for_visit: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("patient_id")
    @classmethod
    def patient_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("patient_id must not be empty")
        return v

    @field_validator("source")
    @classmethod
    def source_valid(cls, v: str) -> str:
        if v not in _VALID_SOURCES:
            raise ValueError(f"source must be one of {sorted(_VALID_SOURCES)!r}")
        return v

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(_VALID_STATUSES)!r}")
        return v


class ConsultationStatusUpdate(BaseModel):
    status: str
    approval_status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(_VALID_STATUSES)!r}")
        return v

    @field_validator("approval_status")
    @classmethod
    def approval_status_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in _VALID_APPROVAL_STATUSES:
            raise ValueError(
                f"approval_status must be one of {sorted(_VALID_APPROVAL_STATUSES)!r}"
            )
        return v


class ConsultationAudioAttach(BaseModel):
    audio_file_path: str

    @field_validator("audio_file_path")
    @classmethod
    def audio_file_path_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("audio_file_path must not be empty")
        return v


class ConsultationTranscriptSave(BaseModel):
    transcript_text: str

    @field_validator("transcript_text")
    @classmethod
    def transcript_text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("transcript_text must not be empty")
        return v


class ConsultationDraftSummarySave(BaseModel):
    draft_summary: Dict[str, Any]

    @field_validator("draft_summary")
    @classmethod
    def draft_summary_not_empty(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError("draft_summary must be a non-empty dict")
        return v


class ConsultationApprove(BaseModel):
    approved_summary: Dict[str, Any]
    approved_by_user_id: str

    @field_validator("approved_summary")
    @classmethod
    def approved_summary_not_empty(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError("approved_summary must be a non-empty dict")
        return v

    @field_validator("approved_by_user_id")
    @classmethod
    def approved_by_user_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("approved_by_user_id must not be empty")
        return v


class ConsultationReject(BaseModel):
    rejected_reason: str
    rejected_by_user_id: Optional[str] = None

    @field_validator("rejected_reason")
    @classmethod
    def rejected_reason_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("rejected_reason must not be empty")
        return v


class ConsultationResponse(BaseModel):
    ok: bool
    consultation: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class ConsultationListResponse(BaseModel):
    ok: bool
    consultations: List[Dict[str, Any]]
    message: Optional[str] = None
