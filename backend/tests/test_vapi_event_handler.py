"""
Unit tests for vapi_event_handler — PraxisMed Sprint 1 / Module 14

All DB calls are mocked; no real database or Vapi API is used.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.modules.vapi.vapi_event_handler import (
    InvalidVapiEventPayloadError,
    UnsupportedVapiEventTypeError,
    normalize_vapi_call_event,
    process_vapi_call_event,
)

CLINIC_ID = "11111111-1111-4111-8111-111111111111"
CALL_ID   = "vapi-call-abc123"

UPSERT_PATH = "backend.app.db.repositories.call_repo.upsert_call_log"


def _base_payload(**overrides) -> dict:
    base = {
        "clinic_id":  CLINIC_ID,
        "event_type": "call.started",
        "call_id":    CALL_ID,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1–4. normalize_vapi_call_event — happy paths
# ---------------------------------------------------------------------------

def test_normalize_call_started():
    p = _base_payload(event_type="call.started", started_at="2024-06-03T09:00:00Z")
    result = normalize_vapi_call_event(p)
    assert result["event_type"] == "call.started"
    assert isinstance(result["started_at"], datetime)
    assert result["started_at"].tzinfo is not None


def test_normalize_call_ended():
    p = _base_payload(
        event_type="call.ended",
        started_at="2024-06-03T09:00:00Z",
        ended_at="2024-06-03T09:15:00Z",
        duration_seconds=900,
    )
    result = normalize_vapi_call_event(p)
    assert result["event_type"] == "call.ended"
    assert result["duration_seconds"] == 900
    assert isinstance(result["ended_at"], datetime)


def test_normalize_transcript_ready():
    p = _base_payload(event_type="transcript.ready", transcript_text="Hallo, ich möchte einen Termin.")
    result = normalize_vapi_call_event(p)
    assert result["event_type"] == "transcript.ready"
    assert "Hallo" in result["transcript_text"]


def test_normalize_summary_ready():
    p = _base_payload(event_type="summary.ready", summary="Patient möchte einen Termin für Montag.")
    result = normalize_vapi_call_event(p)
    assert result["event_type"] == "summary.ready"
    assert result["summary"] is not None


# ---------------------------------------------------------------------------
# 5. human_handoff.required forces action_required=True
# ---------------------------------------------------------------------------

def test_normalize_human_handoff_forces_action_required():
    p = _base_payload(event_type="human_handoff.required", action_required=False)
    result = normalize_vapi_call_event(p)
    assert result["event_type"] == "human_handoff.required"
    assert result["action_required"] is True


def test_normalize_human_handoff_without_flag_also_forces_true():
    p = _base_payload(event_type="human_handoff.required")
    result = normalize_vapi_call_event(p)
    assert result["action_required"] is True


# ---------------------------------------------------------------------------
# 6. Missing required fields raise InvalidVapiEventPayloadError
# ---------------------------------------------------------------------------

def test_missing_clinic_id_raises():
    p = {"event_type": "call.started", "call_id": CALL_ID}
    with pytest.raises(InvalidVapiEventPayloadError):
        normalize_vapi_call_event(p)


def test_missing_event_type_raises():
    p = {"clinic_id": CLINIC_ID, "call_id": CALL_ID}
    with pytest.raises(InvalidVapiEventPayloadError):
        normalize_vapi_call_event(p)


def test_missing_call_id_raises():
    p = {"clinic_id": CLINIC_ID, "event_type": "call.started"}
    with pytest.raises(InvalidVapiEventPayloadError):
        normalize_vapi_call_event(p)


# ---------------------------------------------------------------------------
# 7. Unsupported event type raises UnsupportedVapiEventTypeError
# ---------------------------------------------------------------------------

def test_unsupported_event_type_raises():
    p = _base_payload(event_type="unknown.event")
    with pytest.raises(UnsupportedVapiEventTypeError):
        normalize_vapi_call_event(p)


# ---------------------------------------------------------------------------
# 8. process_vapi_call_event calls upsert_call_log
# ---------------------------------------------------------------------------

async def test_process_event_calls_upsert_call_log():
    pool = MagicMock()
    fake_row = {"id": "abc", "external_call_id": CALL_ID}

    with patch(
        "backend.app.db.repositories.call_repo.upsert_call_log",
        new=AsyncMock(return_value=fake_row),
    ) as mock_upsert:
        result = await process_vapi_call_event(pool, _base_payload())

    mock_upsert.assert_awaited_once()
    assert result["ok"] is True
    assert result["clinic_id"] == CLINIC_ID
    assert result["call_id"] == CALL_ID


# ---------------------------------------------------------------------------
# 9. Repository failure propagates cleanly
# ---------------------------------------------------------------------------

async def test_process_event_propagates_repo_error():
    from backend.app.db.repositories.call_repo import CallRepoError

    pool = MagicMock()
    with patch(
        "backend.app.db.repositories.call_repo.upsert_call_log",
        new=AsyncMock(side_effect=CallRepoError("db error")),
    ):
        with pytest.raises(CallRepoError):
            await process_vapi_call_event(pool, _base_payload())


# ---------------------------------------------------------------------------
# Module 22 — Notification integration tests
# ---------------------------------------------------------------------------

NOTIF_PATH = "backend.app.modules.notifications.notification_router.create_urgent_call_notification"
FAKE_UPSERT = {"id": "abc", "external_call_id": CALL_ID}
FAKE_NOTIF  = {"ok": True, "notification": {"id": "notif-001"}, "message": "created"}


# 10. human_handoff.required creates urgent call notification

@pytest.mark.asyncio
async def test_human_handoff_creates_urgent_call_notification():
    pool = MagicMock()
    with patch(UPSERT_PATH, new=AsyncMock(return_value=FAKE_UPSERT)):
        with patch(NOTIF_PATH, new=AsyncMock(return_value=FAKE_NOTIF)) as mock_notif:
            result = await process_vapi_call_event(
                pool, _base_payload(event_type="human_handoff.required")
            )
    mock_notif.assert_awaited_once()
    assert result["notification_created"] is True


# 11. urgent call.ended creates urgent call notification

@pytest.mark.asyncio
async def test_urgent_call_ended_creates_notification():
    pool = MagicMock()
    with patch(UPSERT_PATH, new=AsyncMock(return_value=FAKE_UPSERT)):
        with patch(NOTIF_PATH, new=AsyncMock(return_value=FAKE_NOTIF)) as mock_notif:
            result = await process_vapi_call_event(
                pool, _base_payload(event_type="call.ended", urgency_level="urgent")
            )
    mock_notif.assert_awaited_once()
    assert result["notification_created"] is True


# 12. action_required call.ended creates urgent call notification

@pytest.mark.asyncio
async def test_action_required_call_ended_creates_notification():
    pool = MagicMock()
    with patch(UPSERT_PATH, new=AsyncMock(return_value=FAKE_UPSERT)):
        with patch(NOTIF_PATH, new=AsyncMock(return_value=FAKE_NOTIF)) as mock_notif:
            result = await process_vapi_call_event(
                pool, _base_payload(event_type="call.ended", action_required=True)
            )
    mock_notif.assert_awaited_once()
    assert result["notification_created"] is True


# 13. normal call.ended does not create notification

@pytest.mark.asyncio
async def test_normal_call_ended_no_notification():
    pool = MagicMock()
    with patch(UPSERT_PATH, new=AsyncMock(return_value=FAKE_UPSERT)):
        with patch(NOTIF_PATH, new=AsyncMock(return_value=FAKE_NOTIF)) as mock_notif:
            result = await process_vapi_call_event(
                pool,
                _base_payload(event_type="call.ended", urgency_level="normal", action_required=False),
            )
    mock_notif.assert_not_called()
    assert result["notification_created"] is False


# 14. notification failure does not break successful call event processing

@pytest.mark.asyncio
async def test_notification_failure_does_not_break_call_event():
    pool = MagicMock()
    with patch(UPSERT_PATH, new=AsyncMock(return_value=FAKE_UPSERT)):
        with patch(NOTIF_PATH, new=AsyncMock(side_effect=RuntimeError("notif down"))):
            result = await process_vapi_call_event(
                pool, _base_payload(event_type="human_handoff.required")
            )
    assert result["ok"] is True
    assert result["notification_created"] is False


# 15. process result includes notification_created=True when created

@pytest.mark.asyncio
async def test_result_includes_notification_created_true():
    pool = MagicMock()
    with patch(UPSERT_PATH, new=AsyncMock(return_value=FAKE_UPSERT)):
        with patch(NOTIF_PATH, new=AsyncMock(return_value=FAKE_NOTIF)):
            result = await process_vapi_call_event(
                pool, _base_payload(event_type="human_handoff.required")
            )
    assert result["notification_created"] is True


# 16. process result includes notification_created=False when skipped

@pytest.mark.asyncio
async def test_result_includes_notification_created_false_when_skipped():
    pool = MagicMock()
    with patch(UPSERT_PATH, new=AsyncMock(return_value=FAKE_UPSERT)):
        with patch(NOTIF_PATH, new=AsyncMock(return_value=FAKE_NOTIF)):
            result = await process_vapi_call_event(
                pool, _base_payload(event_type="call.started")
            )
    assert result["notification_created"] is False
