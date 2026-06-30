"""
Calendar Sync Service — PraxisMed Sprint 1 / Module 6

Processes normalised calendar sync payloads received from n8n webhooks.
This module sits between the webhook handler (not yet built) and the
database repository layer (Module 4).  It contains no SQL and no FastAPI
imports.

Payload flow
------------
n8n webhook → (future route) → process_calendar_sync_payload()
                                    │
                                    ├─ normalize_calendar_payload()   [validate + coerce]
                                    │
                                    ├─ calendar_repo.upsert_calendar_connection()
                                    │
                                    ├─ (event-specific)
                                    │     block_upsert  → calendar_repo.upsert_calendar_block()
                                    │     block_delete  → calendar_repo.delete_calendar_block_by_external_id()
                                    │
                                    └─ calendar_repo.log_calendar_sync_event()   [always]

Supported event_type values
----------------------------
  connection_upsert  — register or refresh a calendar connection
  block_upsert       — create/update a busy block from a calendar event
  block_delete       — remove a busy block when a calendar event is deleted
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.app.db.repositories.calendar_repo import (
    delete_calendar_block_by_external_id,
    log_calendar_sync_event,
    upsert_calendar_block,
    upsert_calendar_connection,
)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class CalendarSyncError(RuntimeError):
    """Base exception for calendar sync failures."""


class InvalidCalendarPayloadError(CalendarSyncError):
    """Raised when a required field is missing or has an invalid value."""


class UnsupportedCalendarEventTypeError(CalendarSyncError):
    """Raised when event_type is not one of the recognised values."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_EVENT_TYPES = frozenset(
    {"connection_upsert", "block_upsert", "block_delete"}
)

# Fields required in every payload regardless of event_type
_BASE_REQUIRED = ("clinic_id", "provider", "external_calendar_id", "event_type")

# Additional fields required per event_type
_EVENT_REQUIRED: Dict[str, tuple[str, ...]] = {
    "connection_upsert": (),
    "block_upsert": ("external_event_id", "starts_at", "ends_at", "block_type"),
    "block_delete": ("external_event_id",),
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _require(payload: Dict[str, Any], *fields: str) -> None:
    """Raise InvalidCalendarPayloadError for the first missing or empty field."""
    for field in fields:
        if not payload.get(field):
            raise InvalidCalendarPayloadError(
                f"Required field {field!r} is missing or empty in the sync payload."
            )


def _parse_dt(value: Any, field_name: str) -> datetime:
    """
    Coerce *value* to a timezone-aware datetime.

    Accepts:
      • an already-aware datetime (passed through unchanged)
      • an ISO 8601 string (with or without timezone suffix)

    Naive datetimes are assumed to be UTC and made aware.
    """
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError as exc:
            raise InvalidCalendarPayloadError(
                f"Field {field_name!r} is not a valid ISO 8601 datetime string: {value!r}"
            ) from exc
    else:
        raise InvalidCalendarPayloadError(
            f"Field {field_name!r} must be a datetime or ISO string; got {type(value).__name__}"
        )

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


# ---------------------------------------------------------------------------
# 1. normalize_calendar_payload
# ---------------------------------------------------------------------------


def normalize_calendar_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalise a raw n8n calendar sync payload.

    Returns a new dict with:
      • all base fields present and non-empty
      • event_type validated against the supported set
      • starts_at / ends_at converted to timezone-aware datetimes (block_upsert)
      • event-specific required fields confirmed present

    Raises
    ------
    InvalidCalendarPayloadError
        When a required field is absent or has an invalid value.
    UnsupportedCalendarEventTypeError
        When event_type is not in SUPPORTED_EVENT_TYPES.
    """
    # --- base fields --------------------------------------------------------
    _require(payload, *_BASE_REQUIRED)

    event_type: str = payload["event_type"]
    if event_type not in SUPPORTED_EVENT_TYPES:
        raise UnsupportedCalendarEventTypeError(
            f"event_type {event_type!r} is not supported. "
            f"Supported values: {sorted(SUPPORTED_EVENT_TYPES)}"
        )

    # --- event-specific fields ----------------------------------------------
    _require(payload, *_EVENT_REQUIRED[event_type])

    # Build a normalised copy so we do not mutate the caller's dict
    normalised: Dict[str, Any] = {
        "clinic_id":             payload["clinic_id"],
        "provider":              payload["provider"],
        "external_calendar_id":  payload["external_calendar_id"],
        "event_type":            event_type,
        "sync_status":           payload.get("sync_status", "active"),
        "connection_id":         payload.get("connection_id"),
    }

    if event_type == "block_upsert":
        normalised["external_event_id"] = payload["external_event_id"]
        normalised["starts_at"]         = _parse_dt(payload["starts_at"], "starts_at")
        normalised["ends_at"]           = _parse_dt(payload["ends_at"],   "ends_at")
        normalised["block_type"]        = payload["block_type"]
        normalised["title"]             = payload.get("title")
        normalised["is_all_day"]        = bool(payload.get("is_all_day", False))
        normalised["source"]            = payload.get("source", "calendar_sync")
        normalised["raw_payload"]       = payload.get("raw_payload")

    elif event_type == "block_delete":
        normalised["external_event_id"] = payload["external_event_id"]

    return normalised


# ---------------------------------------------------------------------------
# 2. process_calendar_sync_payload
# ---------------------------------------------------------------------------


async def process_calendar_sync_payload(
    pool: Any,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Orchestrate a complete calendar sync operation for a single n8n payload.

    Steps
    -----
    1. Normalise and validate the payload.
    2. Upsert the calendar connection (always).
    3. Perform the event-specific repository operation.
    4. Log the outcome to clinic_calendar_sync_events (always, even on error).

    Returns a result dict:
        {
            "ok":         bool,
            "event_type": str,
            "clinic_id":  str,
            "action":     str,   # human-readable description of what ran
            "message":    str,   # success detail or error message
        }
    """
    # --- step 1: normalise --------------------------------------------------
    try:
        norm = normalize_calendar_payload(payload)
    except (InvalidCalendarPayloadError, UnsupportedCalendarEventTypeError) as exc:
        # Log without a connection_id because we may not have one yet
        clinic_id = payload.get("clinic_id", "unknown")
        await _safe_log(
            pool,
            clinic_id=clinic_id,
            connection_id=None,
            event_type=payload.get("event_type", "unknown"),
            status="error",
            message=str(exc),
            raw_payload=payload,
        )
        raise

    clinic_id    = norm["clinic_id"]
    event_type   = norm["event_type"]
    connection_id: Optional[str] = norm.get("connection_id")

    # --- step 2: upsert connection ------------------------------------------
    try:
        conn_row = await upsert_calendar_connection(
            pool,
            clinic_id=clinic_id,
            provider=norm["provider"],
            external_calendar_id=norm["external_calendar_id"],
            sync_status=norm["sync_status"],
        )
        # Use the DB-assigned connection id for subsequent operations
        connection_id = str(conn_row.get("id", connection_id or ""))
    except Exception as exc:
        await _safe_log(
            pool,
            clinic_id=clinic_id,
            connection_id=connection_id,
            event_type=event_type,
            status="error",
            message=f"upsert_calendar_connection failed: {exc}",
            raw_payload=payload,
        )
        raise CalendarSyncError(
            f"Failed to upsert calendar connection for clinic {clinic_id!r}: {exc}"
        ) from exc

    # --- step 3: event-specific operation -----------------------------------
    action: str
    message: str

    try:
        if event_type == "connection_upsert":
            action  = "connection_upserted"
            message = (
                f"Calendar connection upserted for provider {norm['provider']!r}, "
                f"calendar {norm['external_calendar_id']!r}."
            )

        elif event_type == "block_upsert":
            await upsert_calendar_block(
                pool,
                clinic_id=clinic_id,
                connection_id=connection_id,
                external_event_id=norm["external_event_id"],
                title=norm.get("title"),
                block_type=norm["block_type"],
                starts_at=norm["starts_at"],
                ends_at=norm["ends_at"],
                is_all_day=norm["is_all_day"],
                source=norm["source"],
                raw_payload=norm.get("raw_payload"),
            )
            action  = "block_upserted"
            message = (
                f"Calendar block upserted: event {norm['external_event_id']!r} "
                f"({norm['block_type']}) "
                f"{norm['starts_at'].isoformat()} → {norm['ends_at'].isoformat()}."
            )

        elif event_type == "block_delete":
            deleted = await delete_calendar_block_by_external_id(
                pool,
                clinic_id=clinic_id,
                connection_id=connection_id,
                external_event_id=norm["external_event_id"],
            )
            action  = "block_deleted"
            message = (
                f"Calendar block deleted: event {norm['external_event_id']!r}. "
                f"Row {'removed' if deleted else 'not found (already absent)'}."
            )

        else:
            # Defensive — normalize_calendar_payload already guards this
            raise UnsupportedCalendarEventTypeError(event_type)

    except (CalendarSyncError, UnsupportedCalendarEventTypeError):
        raise
    except Exception as exc:
        await _safe_log(
            pool,
            clinic_id=clinic_id,
            connection_id=connection_id,
            event_type=event_type,
            status="error",
            message=str(exc),
            raw_payload=payload,
        )
        raise CalendarSyncError(
            f"Calendar sync operation {event_type!r} failed for clinic {clinic_id!r}: {exc}"
        ) from exc

    # --- step 4: log success ------------------------------------------------
    await _safe_log(
        pool,
        clinic_id=clinic_id,
        connection_id=connection_id,
        event_type=event_type,
        status="success",
        message=message,
        raw_payload=payload,
    )

    return {
        "ok":         True,
        "event_type": event_type,
        "clinic_id":  clinic_id,
        "action":     action,
        "message":    message,
    }


# ---------------------------------------------------------------------------
# Internal: fire-and-forget sync event logger
# ---------------------------------------------------------------------------


async def _safe_log(
    pool: Any,
    *,
    clinic_id: str,
    connection_id: Optional[str],
    event_type: str,
    status: str,
    message: Optional[str] = None,
    raw_payload: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a sync event; silently swallow any error so that a logging failure
    never masks the original exception or prevents a success response.
    """
    try:
        await log_calendar_sync_event(
            pool,
            clinic_id=clinic_id,
            connection_id=connection_id,
            event_type=event_type,
            status=status,
            message=message,
            raw_payload=raw_payload,
        )
    except Exception:  # noqa: BLE001
        pass
