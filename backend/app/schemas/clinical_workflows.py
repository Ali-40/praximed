"""
Clinical workflow Pydantic schemas — PraxisMed Sprint 3 / Module 35
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, field_validator, model_validator


class AudioReferenceAttachRequest(BaseModel):
    clinic_id: str
    file_name: str
    content_type: str
    file_size_bytes: int
    uploaded_by_user_id: Optional[str] = None
    source: str = "doctor_mobile"
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("file_name")
    @classmethod
    def file_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("file_name must not be empty")
        return v

    @field_validator("content_type")
    @classmethod
    def content_type_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content_type must not be empty")
        return v

    @field_validator("file_size_bytes")
    @classmethod
    def file_size_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("file_size_bytes must be greater than 0")
        return v


class ManualTranscriptRequest(BaseModel):
    clinic_id: str
    audio_file_path: str
    transcript_text: str
    language: str = "de-AT"
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("audio_file_path")
    @classmethod
    def audio_file_path_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("audio_file_path must not be empty")
        return v

    @field_validator("transcript_text")
    @classmethod
    def transcript_text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("transcript_text must not be empty")
        return v

    @field_validator("language")
    @classmethod
    def language_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("language must not be empty")
        return v


class ClinicalSummaryDraftRequest(BaseModel):
    clinic_id: str
    transcript_text: str
    language: str = "de-AT"
    patient_context: Optional[Dict[str, Any]] = None
    consultation_context: Optional[Dict[str, Any]] = None
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("transcript_text")
    @classmethod
    def transcript_text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("transcript_text must not be empty")
        return v

    @field_validator("language")
    @classmethod
    def language_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("language must not be empty")
        return v

    @field_validator("patient_context")
    @classmethod
    def patient_context_is_dict(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, dict):
            raise ValueError("patient_context must be a dict if provided")
        return v

    @field_validator("consultation_context")
    @classmethod
    def consultation_context_is_dict(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, dict):
            raise ValueError("consultation_context must be a dict if provided")
        return v


class ReviewPackageRequest(BaseModel):
    clinic_id: str
    draft_summary: Dict[str, Any]
    transcript_text: Optional[str] = None
    patient_context: Optional[Dict[str, Any]] = None
    consultation_context: Optional[Dict[str, Any]] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("draft_summary")
    @classmethod
    def draft_summary_not_empty(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError("draft_summary must be a non-empty dict")
        return v

    @field_validator("patient_context")
    @classmethod
    def patient_context_is_dict(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, dict):
            raise ValueError("patient_context must be a dict if provided")
        return v

    @field_validator("consultation_context")
    @classmethod
    def consultation_context_is_dict(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, dict):
            raise ValueError("consultation_context must be a dict if provided")
        return v


class ApproveSummaryRequest(BaseModel):
    clinic_id: str
    approved_summary: Dict[str, Any]
    approved_by_user_id: str

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

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


class RejectSummaryRequest(BaseModel):
    clinic_id: str
    rejected_reason: str
    rejected_by_user_id: Optional[str] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("rejected_reason")
    @classmethod
    def rejected_reason_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("rejected_reason must not be empty")
        return v

    @field_validator("rejected_by_user_id")
    @classmethod
    def rejected_by_user_id_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("rejected_by_user_id must not be empty if provided")
        return v


class WorkflowResponse(BaseModel):
    ok: bool
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class TimelineReportResponse(BaseModel):
    ok: bool
    report: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
