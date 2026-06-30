"""
Notification Repository — PraxisMed Sprint 1 / Module 20

Provides async CRUD operations for the ``clinic_notifications`` table.
All SQL is parameterised ($1, $2, …) — no string interpolation.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class NotificationRepoError(RuntimeError):
    """Base class for notification repository errors."""


class InvalidNotificationError(NotificationRepoError):
    """Raised when required fields are missing or values are invalid."""


# ---------------------------------------------------------------------------
# Allowed enum values
# ---------------------------------------------------------------------------

_VALID_CHANNELS = frozenset({"internal", "sms", "push", "email", "webhook"})
_VALID_TYPES = frozenset({
    "urgent_call", "human_handoff", "callback_needed", "appointment_request",
    "cancellation", "calendar_sync_failure", "summary_ready", "system",
})
_VALID_PRIORITIES = frozenset({"low", "normal", "high", "urgent", "emergency"})
_VALID_STATUSES = frozenset({"pending", "sent", "failed", "read", "cancelled"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _assert_nonempty(value: Any, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidNotificationError(f"{name!r} must not be empty")


def _assert_valid_enum(value: str, name: str, valid: frozenset) -> None:
    if value not in valid:
        raise InvalidNotificationError(
            f"{name!r} must be one of {sorted(valid)!r}; got {value!r}"
        )


# ---------------------------------------------------------------------------
# 1. create_notification
# ---------------------------------------------------------------------------


async def create_notification(
    pool: Any,
    clinic_id: str,
    channel: str,
    notification_type: str,
    title: str,
    message: str,
    priority: str = "normal",
    recipient_user_id: Optional[str] = None,
    status: str = "pending",
    related_resource_type: Optional[str] = None,
    related_resource_id: Optional[str] = None,
    scheduled_for: Optional[datetime] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(title, "title")
    _assert_nonempty(message, "message")
    _assert_valid_enum(channel, "channel", _VALID_CHANNELS)
    _assert_valid_enum(notification_type, "notification_type", _VALID_TYPES)
    _assert_valid_enum(priority, "priority", _VALID_PRIORITIES)
    _assert_valid_enum(status, "status", _VALID_STATUSES)

    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    sql = """
        INSERT INTO clinic_notifications (
            clinic_id, recipient_user_id, channel, notification_type,
            priority, title, message, status,
            related_resource_type, related_resource_id,
            scheduled_for, raw_payload
        ) VALUES (
            $1, $2, $3, $4,
            $5, $6, $7, $8,
            $9, $10,
            $11, $12::jsonb
        )
        RETURNING *
    """
    row = await pool.fetchrow(
        sql,
        clinic_id, recipient_user_id, channel, notification_type,
        priority, title, message, status,
        related_resource_type, related_resource_id,
        scheduled_for, raw_payload_json,
    )
    return _row_to_dict(row)


# ---------------------------------------------------------------------------
# 2. get_notification_by_id
# ---------------------------------------------------------------------------


async def get_notification_by_id(
    pool: Any,
    clinic_id: str,
    notification_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT *
        FROM clinic_notifications
        WHERE clinic_id = $1
          AND id        = $2
    """
    row = await pool.fetchrow(sql, clinic_id, notification_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 3. list_notifications
# ---------------------------------------------------------------------------


async def list_notifications(
    pool: Any,
    clinic_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    notification_type: Optional[str] = None,
    recipient_user_id: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if limit < 1 or limit > 100:
        raise InvalidNotificationError("limit must be between 1 and 100")
    if status is not None:
        _assert_valid_enum(status, "status", _VALID_STATUSES)
    if priority is not None:
        _assert_valid_enum(priority, "priority", _VALID_PRIORITIES)
    if notification_type is not None:
        _assert_valid_enum(notification_type, "notification_type", _VALID_TYPES)

    sql = """
        SELECT *
        FROM clinic_notifications
        WHERE clinic_id = $1
          AND ($2::text IS NULL OR status            = $2)
          AND ($3::text IS NULL OR priority           = $3)
          AND ($4::text IS NULL OR notification_type  = $4)
          AND ($5::text IS NULL OR recipient_user_id::text = $5)
        ORDER BY created_at DESC
        LIMIT $6
    """
    rows = await pool.fetch(sql, clinic_id, status, priority, notification_type, recipient_user_id, limit)
    return [_row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# 4. mark_notification_sent
# ---------------------------------------------------------------------------


async def mark_notification_sent(
    pool: Any,
    clinic_id: str,
    notification_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE clinic_notifications
        SET status     = 'sent',
            sent_at    = now(),
            updated_at = now()
        WHERE clinic_id = $1
          AND id        = $2
        RETURNING *
    """
    row = await pool.fetchrow(sql, clinic_id, notification_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 5. mark_notification_failed
# ---------------------------------------------------------------------------


async def mark_notification_failed(
    pool: Any,
    clinic_id: str,
    notification_id: str,
    error_message: str,
) -> Optional[Dict[str, Any]]:
    _assert_nonempty(error_message, "error_message")
    sql = """
        UPDATE clinic_notifications
        SET status        = 'failed',
            error_message = $1,
            updated_at    = now()
        WHERE clinic_id = $2
          AND id        = $3
        RETURNING *
    """
    row = await pool.fetchrow(sql, error_message, clinic_id, notification_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 6. mark_notification_read
# ---------------------------------------------------------------------------


async def mark_notification_read(
    pool: Any,
    clinic_id: str,
    notification_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE clinic_notifications
        SET status     = 'read',
            read_at    = now(),
            updated_at = now()
        WHERE clinic_id = $1
          AND id        = $2
        RETURNING *
    """
    row = await pool.fetchrow(sql, clinic_id, notification_id)
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 7. cancel_notification
# ---------------------------------------------------------------------------


async def cancel_notification(
    pool: Any,
    clinic_id: str,
    notification_id: str,
) -> Optional[Dict[str, Any]]:
    sql = """
        UPDATE clinic_notifications
        SET status     = 'cancelled',
            updated_at = now()
        WHERE clinic_id = $1
          AND id        = $2
        RETURNING *
    """
    row = await pool.fetchrow(sql, clinic_id, notification_id)
    return _row_to_dict(row) if row is not None else None
