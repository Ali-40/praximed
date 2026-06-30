"""
Pydantic schemas for notification endpoints — PraxisMed Sprint 1 / Module 23
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator

_VALID_CHANNELS = frozenset({"internal", "sms", "push", "email", "webhook"})
_VALID_TYPES = frozenset({
    "urgent_call", "human_handoff", "callback_needed", "appointment_request",
    "cancellation", "calendar_sync_failure", "summary_ready", "system",
})
_VALID_PRIORITIES = frozenset({"low", "normal", "high", "urgent", "emergency"})


class NotificationCreate(BaseModel):
    clinic_id: str
    channel: str = "internal"
    notification_type: str
    title: str
    message: str
    priority: str = "normal"
    recipient_user_id: Optional[str] = None
    related_resource_type: Optional[str] = None
    related_resource_id: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("clinic_id")
    @classmethod
    def clinic_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("clinic_id must not be empty")
        return v

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("message must not be empty")
        return v

    @field_validator("channel")
    @classmethod
    def channel_valid(cls, v: str) -> str:
        if v not in _VALID_CHANNELS:
            raise ValueError(f"channel must be one of {sorted(_VALID_CHANNELS)!r}")
        return v

    @field_validator("notification_type")
    @classmethod
    def notification_type_valid(cls, v: str) -> str:
        if v not in _VALID_TYPES:
            raise ValueError(f"notification_type must be one of {sorted(_VALID_TYPES)!r}")
        return v

    @field_validator("priority")
    @classmethod
    def priority_valid(cls, v: str) -> str:
        if v not in _VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(_VALID_PRIORITIES)!r}")
        return v


class NotificationResponse(BaseModel):
    ok: bool
    notification: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class NotificationListResponse(BaseModel):
    ok: bool
    notifications: List[Dict[str, Any]]
    message: Optional[str] = None
