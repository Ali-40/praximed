"""
Vapi call event handler — PraxisMed Sprint 1 / Module 14

Normalises inbound Vapi webhook payloads and persists them via the call
log repository.  No direct SQL here; no external Vapi API calls made.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class VapiEventError(RuntimeError):
    """Base class for Vapi event handling errors."""


class InvalidVapiEventPayloadError(VapiEventError):
    """Raised when a required field is missing from the event payload."""


class UnsupportedVapiEventTypeError(VapiEventError):
    """Raised when the event_type is not handled by this service."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_EVENT_TYPES = frozenset({
    "call.started",
    "call.ended",
    "transcript.ready",
    "summary.ready",
    "human_handoff.required",
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_dt(value: Any) -> Optional[datetime]:
    """Coerce an ISO string or naïve datetime to a UTC-aware datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# 1. normalize_vapi_call_event
# ---------------------------------------------------------------------------


def normalize_vapi_call_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalise a raw Vapi webhook payload.

    Required fields: ``clinic_id``, ``event_type``, ``call_id``.
    Raises ``InvalidVapiEventPayloadError`` for missing required fields and
    ``UnsupportedVapiEventTypeError`` for unknown event types.
    """
    for field in ("clinic_id", "event_type", "call_id"):
        if not payload.get(field):
            raise InvalidVapiEventPayloadError(
                f"Missing required field: {field!r}"
            )

    event_type = str(payload["event_type"])
    if event_type not in SUPPORTED_EVENT_TYPES:
        raise UnsupportedVapiEventTypeError(
            f"Unsupported Vapi event type: {event_type!r}. "
            f"Supported: {sorted(SUPPORTED_EVENT_TYPES)}"
        )

    action_required = bool(payload.get("action_required", False))
    if event_type == "human_handoff.required":
        action_required = True

    return {
        "clinic_id":        str(payload["clinic_id"]),
        "event_type":       event_type,
        "call_id":          str(payload["call_id"]),
        "caller_phone":     payload.get("caller_phone"),
        "started_at":       _parse_dt(payload.get("started_at")),
        "ended_at":         _parse_dt(payload.get("ended_at")),
        "duration_seconds": payload.get("duration_seconds"),
        "transcript_text":  payload.get("transcript_text"),
        "summary":          payload.get("summary"),
        "urgency_level":    str(payload.get("urgency_level", "normal")),
        "action_required":  action_required,
    }


# ---------------------------------------------------------------------------
# 2. process_vapi_call_event
# ---------------------------------------------------------------------------


async def process_vapi_call_event(pool: Any, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalise *payload* and persist the call event via the repository.

    For ``human_handoff.required`` events ``action_required`` is forced to
    True before upserting so the row is always flagged regardless of the
    caller's payload.

    Returns a summary dict suitable for returning as an HTTP response body.
    """
    from backend.app.db.repositories import call_repo  # local import avoids circulars
    from backend.app.modules.notifications import notification_router  # local import avoids circulars

    normalised = normalize_vapi_call_event(payload)

    call_status = _event_type_to_status(normalised["event_type"])

    await call_repo.upsert_call_log(
        pool=pool,
        clinic_id=normalised["clinic_id"],
        external_call_id=normalised["call_id"],
        call_status=call_status,
        caller_phone=normalised.get("caller_phone"),
        started_at=normalised.get("started_at"),
        ended_at=normalised.get("ended_at"),
        duration_seconds=normalised.get("duration_seconds"),
        transcript_text=normalised.get("transcript_text"),
        summary=normalised.get("summary"),
        action_required=normalised["action_required"],
        urgency_level=normalised["urgency_level"],
        raw_payload=payload,
    )

    notification_created = False
    should_notify = normalised["event_type"] == "human_handoff.required" or (
        normalised["event_type"] == "call.ended"
        and (
            normalised["urgency_level"] in ("urgent", "emergency")
            or normalised["action_required"]
        )
    )

    if should_notify:
        try:
            await notification_router.create_urgent_call_notification(
                pool=pool,
                clinic_id=normalised["clinic_id"],
                call_id=normalised["call_id"],
                caller_phone=normalised.get("caller_phone"),
                urgency_level=normalised["urgency_level"],
                raw_payload=payload,
            )
            notification_created = True
        except Exception:
            notification_created = False

    return {
        "ok":                  True,
        "clinic_id":           normalised["clinic_id"],
        "event_type":          normalised["event_type"],
        "call_id":             normalised["call_id"],
        "message":             f"Event {normalised['event_type']!r} processed successfully.",
        "notification_created": notification_created,
    }


def _event_type_to_status(event_type: str) -> str:
    mapping = {
        "call.started":           "in_progress",
        "call.ended":             "ended",
        "transcript.ready":       "ended",
        "summary.ready":          "ended",
        "human_handoff.required": "handoff",
    }
    return mapping.get(event_type, "unknown")
