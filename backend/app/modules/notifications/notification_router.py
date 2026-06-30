"""
Notification Router Service — PraxisMed Sprint 1 / Module 21

Converts system events into clinic_notifications records via notification_repo.
Does not send SMS, push, email, or webhooks — only creates DB records.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from backend.app.db.repositories import notification_repo


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class NotificationRouterError(RuntimeError):
    """Base class for notification router errors."""


class InvalidNotificationEventError(NotificationRouterError):
    """Raised when an event field is missing or invalid."""


# ---------------------------------------------------------------------------
# Allowed values
# ---------------------------------------------------------------------------

_VALID_TYPES = frozenset({
    "urgent_call", "human_handoff", "callback_needed", "appointment_request",
    "cancellation", "calendar_sync_failure", "summary_ready", "system",
})

_VALID_CHANNELS = frozenset({"internal", "sms", "push", "email", "webhook"})

_VALID_PRIORITIES = frozenset({"low", "normal", "high", "urgent", "emergency"})

_VALID_URGENCY_LEVELS = frozenset({"low", "normal", "urgent", "emergency"})

_TYPE_DEFAULT_PRIORITY: Dict[str, str] = {
    "urgent_call":           "urgent",
    "human_handoff":         "urgent",
    "callback_needed":       "high",
    "appointment_request":   "normal",
    "cancellation":          "high",
    "calendar_sync_failure": "high",
    "summary_ready":         "normal",
    "system":                "normal",
}

_URGENCY_TO_PRIORITY: Dict[str, str] = {
    "low":       "low",
    "normal":    "normal",
    "urgent":    "urgent",
    "emergency": "emergency",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _assert_nonempty(value: Any, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidNotificationEventError(f"{name!r} must not be empty")


def _assert_valid(value: str, name: str, valid: frozenset) -> None:
    if value not in valid:
        raise InvalidNotificationEventError(
            f"{name!r} must be one of {sorted(valid)!r}; got {value!r}"
        )


# ---------------------------------------------------------------------------
# 1. infer_priority
# ---------------------------------------------------------------------------


def infer_priority(
    notification_type: str,
    urgency_level: Optional[str] = None,
) -> str:
    _assert_valid(notification_type, "notification_type", _VALID_TYPES)
    if urgency_level is not None:
        _assert_valid(urgency_level, "urgency_level", _VALID_URGENCY_LEVELS)
        return _URGENCY_TO_PRIORITY[urgency_level]
    return _TYPE_DEFAULT_PRIORITY[notification_type]


# ---------------------------------------------------------------------------
# 2. build_notification_event
# ---------------------------------------------------------------------------


def build_notification_event(
    clinic_id: str,
    notification_type: str,
    title: str,
    message: str,
    channel: str = "internal",
    priority: Optional[str] = None,
    urgency_level: Optional[str] = None,
    recipient_user_id: Optional[str] = None,
    related_resource_type: Optional[str] = None,
    related_resource_id: Optional[str] = None,
    scheduled_for: Optional[datetime] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(title, "title")
    _assert_nonempty(message, "message")
    _assert_valid(notification_type, "notification_type", _VALID_TYPES)
    _assert_valid(channel, "channel", _VALID_CHANNELS)

    if priority is None:
        resolved_priority = infer_priority(notification_type, urgency_level)
    else:
        _assert_valid(priority, "priority", _VALID_PRIORITIES)
        resolved_priority = priority

    return {
        "clinic_id":             clinic_id,
        "channel":               channel,
        "notification_type":     notification_type,
        "priority":              resolved_priority,
        "title":                 title,
        "message":               message,
        "recipient_user_id":     recipient_user_id,
        "related_resource_type": related_resource_type,
        "related_resource_id":   related_resource_id,
        "scheduled_for":         scheduled_for,
        "raw_payload":           raw_payload,
    }


# ---------------------------------------------------------------------------
# 3. route_notification_event
# ---------------------------------------------------------------------------


async def route_notification_event(
    pool: Any,
    event: Dict[str, Any],
) -> Dict[str, Any]:
    normalized = build_notification_event(
        clinic_id=event["clinic_id"],
        notification_type=event["notification_type"],
        title=event["title"],
        message=event["message"],
        channel=event.get("channel", "internal"),
        priority=event.get("priority"),
        urgency_level=event.get("urgency_level"),
        recipient_user_id=event.get("recipient_user_id"),
        related_resource_type=event.get("related_resource_type"),
        related_resource_id=event.get("related_resource_id"),
        scheduled_for=event.get("scheduled_for"),
        raw_payload=event.get("raw_payload"),
    )
    created = await notification_repo.create_notification(pool, **normalized)
    return {
        "ok": True,
        "notification": created,
        "message": "Notification record created successfully.",
    }


# ---------------------------------------------------------------------------
# 4. create_urgent_call_notification
# ---------------------------------------------------------------------------


async def create_urgent_call_notification(
    pool: Any,
    clinic_id: str,
    call_id: str,
    caller_phone: Optional[str] = None,
    urgency_level: str = "urgent",
    recipient_user_id: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    phone_part = f" from {caller_phone}" if caller_phone else ""
    return await route_notification_event(pool, {
        "clinic_id":             clinic_id,
        "notification_type":     "urgent_call",
        "title":                 "Urgent call requires attention",
        "message":               f"An urgent call{phone_part} requires immediate staff attention.",
        "channel":               "internal",
        "urgency_level":         urgency_level,
        "recipient_user_id":     recipient_user_id,
        "related_resource_type": "clinic_call_logs",
        "related_resource_id":   call_id,
        "raw_payload":           raw_payload,
    })


# ---------------------------------------------------------------------------
# 5. create_appointment_request_notification
# ---------------------------------------------------------------------------


async def create_appointment_request_notification(
    pool: Any,
    clinic_id: str,
    request_id: str,
    patient_name: str,
    urgency_level: str = "normal",
    recipient_user_id: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return await route_notification_event(pool, {
        "clinic_id":             clinic_id,
        "notification_type":     "appointment_request",
        "title":                 "New appointment request",
        "message":               f"A new appointment request has been received from {patient_name}.",
        "channel":               "internal",
        "urgency_level":         urgency_level,
        "recipient_user_id":     recipient_user_id,
        "related_resource_type": "appointment_requests",
        "related_resource_id":   request_id,
        "raw_payload":           raw_payload,
    })


# ---------------------------------------------------------------------------
# 6. create_calendar_sync_failure_notification
# ---------------------------------------------------------------------------


async def create_calendar_sync_failure_notification(
    pool: Any,
    clinic_id: str,
    message: str,
    recipient_user_id: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return await route_notification_event(pool, {
        "clinic_id":             clinic_id,
        "notification_type":     "calendar_sync_failure",
        "title":                 "Calendar sync failure",
        "message":               message,
        "channel":               "internal",
        "priority":              "high",
        "recipient_user_id":     recipient_user_id,
        "related_resource_type": "calendar_sync",
        "raw_payload":           raw_payload,
    })
