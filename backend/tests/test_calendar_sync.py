"""
Unit tests for backend/app/modules/calendar_sync/calendar_sync.py

All repository functions are patched via AsyncMock — no real database
connection is used at any point.

Patch targets (calendar_repo functions as imported by calendar_sync):
  backend.app.modules.calendar_sync.calendar_sync.upsert_calendar_connection
  backend.app.modules.calendar_sync.calendar_sync.upsert_calendar_block
  backend.app.modules.calendar_sync.calendar_sync.delete_calendar_block_by_external_id
  backend.app.modules.calendar_sync.calendar_sync.log_calendar_sync_event
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

# ---------------------------------------------------------------------------
# Patch targets
# ---------------------------------------------------------------------------

MOD = "backend.app.modules.calendar_sync.calendar_sync"

P_UPSERT_CONN   = f"{MOD}.upsert_calendar_connection"
P_UPSERT_BLOCK  = f"{MOD}.upsert_calendar_block"
P_DELETE_BLOCK  = f"{MOD}.delete_calendar_block_by_external_id"
P_LOG           = f"{MOD}.log_calendar_sync_event"

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

CLINIC_ID      = "11111111-1111-4111-8111-111111111111"
CONNECTION_ID  = "22222222-2222-4222-a222-222222222222"
EXT_CAL_ID     = "cal@group.calendar.google.com"
EXT_EVENT_ID   = "google-evt-abc123"

START_ISO = "2025-06-02T09:00:00+00:00"
END_ISO   = "2025-06-02T10:00:00+00:00"
START_DT  = datetime(2025, 6, 2, 9,  0, tzinfo=timezone.utc)
END_DT    = datetime(2025, 6, 2, 10, 0, tzinfo=timezone.utc)

FAKE_CONN_ROW = {
    "id":                   CONNECTION_ID,
    "clinic_id":            CLINIC_ID,
    "provider":             "google",
    "external_calendar_id": EXT_CAL_ID,
    "sync_status":          "active",
}

FAKE_BLOCK_ROW = {
    "id":                "block-id-1",
    "clinic_id":         CLINIC_ID,
    "connection_id":     CONNECTION_ID,
    "external_event_id": EXT_EVENT_ID,
    "block_type":        "busy",
    "starts_at":         START_DT,
    "ends_at":           END_DT,
}

FAKE_LOG_ROW = {
    "id":         "log-id-1",
    "clinic_id":  CLINIC_ID,
    "event_type": "block_upsert",
    "status":     "success",
}

BASE_PAYLOAD = {
    "clinic_id":             CLINIC_ID,
    "provider":              "google",
    "external_calendar_id":  EXT_CAL_ID,
}

CONNECTION_UPSERT_PAYLOAD = {**BASE_PAYLOAD, "event_type": "connection_upsert"}

BLOCK_UPSERT_PAYLOAD = {
    **BASE_PAYLOAD,
    "event_type":        "block_upsert",
    "external_event_id": EXT_EVENT_ID,
    "starts_at":         START_ISO,
    "ends_at":           END_ISO,
    "block_type":        "busy",
}

BLOCK_DELETE_PAYLOAD = {
    **BASE_PAYLOAD,
    "event_type":        "block_delete",
    "external_event_id": EXT_EVENT_ID,
}

# ---------------------------------------------------------------------------
# normalize_calendar_payload — pure function tests (no DB, no patching)
# ---------------------------------------------------------------------------


def test_normalize_accepts_connection_upsert():
    from backend.app.modules.calendar_sync.calendar_sync import normalize_calendar_payload

    result = normalize_calendar_payload(CONNECTION_UPSERT_PAYLOAD)

    assert result["clinic_id"]            == CLINIC_ID
    assert result["provider"]             == "google"
    assert result["external_calendar_id"] == EXT_CAL_ID
    assert result["event_type"]           == "connection_upsert"
    assert result["sync_status"]          == "active"


def test_normalize_accepts_block_upsert_converts_datetimes():
    from backend.app.modules.calendar_sync.calendar_sync import normalize_calendar_payload

    result = normalize_calendar_payload(BLOCK_UPSERT_PAYLOAD)

    assert result["event_type"]        == "block_upsert"
    assert result["external_event_id"] == EXT_EVENT_ID
    assert result["block_type"]        == "busy"

    # ISO strings must be coerced to aware datetime objects
    assert isinstance(result["starts_at"], datetime)
    assert isinstance(result["ends_at"],   datetime)
    assert result["starts_at"].tzinfo is not None
    assert result["ends_at"].tzinfo   is not None
    assert result["starts_at"] == START_DT
    assert result["ends_at"]   == END_DT


def test_normalize_accepts_block_upsert_with_datetime_objects():
    """Already-datetime values must pass through without error."""
    from backend.app.modules.calendar_sync.calendar_sync import normalize_calendar_payload

    payload = {**BLOCK_UPSERT_PAYLOAD, "starts_at": START_DT, "ends_at": END_DT}
    result  = normalize_calendar_payload(payload)

    assert result["starts_at"] == START_DT
    assert result["ends_at"]   == END_DT


def test_normalize_accepts_block_delete():
    from backend.app.modules.calendar_sync.calendar_sync import normalize_calendar_payload

    result = normalize_calendar_payload(BLOCK_DELETE_PAYLOAD)

    assert result["event_type"]        == "block_delete"
    assert result["external_event_id"] == EXT_EVENT_ID


def test_normalize_naive_datetime_becomes_utc_aware():
    """Naive datetimes must be treated as UTC and made tz-aware."""
    from backend.app.modules.calendar_sync.calendar_sync import normalize_calendar_payload

    naive_start = "2025-06-02T09:00:00"   # no tz suffix
    naive_end   = "2025-06-02T10:00:00"
    payload = {**BLOCK_UPSERT_PAYLOAD, "starts_at": naive_start, "ends_at": naive_end}
    result  = normalize_calendar_payload(payload)

    assert result["starts_at"].tzinfo is not None
    assert result["ends_at"].tzinfo   is not None


# ---------------------------------------------------------------------------
# normalize_calendar_payload — validation errors
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("missing_field", ["clinic_id", "provider",
                                           "external_calendar_id", "event_type"])
def test_normalize_raises_for_missing_base_field(missing_field: str):
    from backend.app.modules.calendar_sync.calendar_sync import (
        normalize_calendar_payload,
        InvalidCalendarPayloadError,
    )

    payload = {k: v for k, v in CONNECTION_UPSERT_PAYLOAD.items() if k != missing_field}
    with pytest.raises(InvalidCalendarPayloadError, match=missing_field):
        normalize_calendar_payload(payload)


@pytest.mark.parametrize("missing_field", ["external_event_id", "starts_at",
                                           "ends_at", "block_type"])
def test_normalize_raises_for_missing_block_upsert_field(missing_field: str):
    from backend.app.modules.calendar_sync.calendar_sync import (
        normalize_calendar_payload,
        InvalidCalendarPayloadError,
    )

    payload = {k: v for k, v in BLOCK_UPSERT_PAYLOAD.items() if k != missing_field}
    with pytest.raises(InvalidCalendarPayloadError):
        normalize_calendar_payload(payload)


def test_normalize_raises_for_missing_block_delete_field():
    from backend.app.modules.calendar_sync.calendar_sync import (
        normalize_calendar_payload,
        InvalidCalendarPayloadError,
    )

    payload = {k: v for k, v in BLOCK_DELETE_PAYLOAD.items()
               if k != "external_event_id"}
    with pytest.raises(InvalidCalendarPayloadError, match="external_event_id"):
        normalize_calendar_payload(payload)


def test_normalize_raises_for_unsupported_event_type():
    from backend.app.modules.calendar_sync.calendar_sync import (
        normalize_calendar_payload,
        UnsupportedCalendarEventTypeError,
    )

    payload = {**BASE_PAYLOAD, "event_type": "totally_unknown"}
    with pytest.raises(UnsupportedCalendarEventTypeError, match="totally_unknown"):
        normalize_calendar_payload(payload)


def test_normalize_raises_for_bad_datetime_string():
    from backend.app.modules.calendar_sync.calendar_sync import (
        normalize_calendar_payload,
        InvalidCalendarPayloadError,
    )

    payload = {**BLOCK_UPSERT_PAYLOAD, "starts_at": "not-a-date"}
    with pytest.raises(InvalidCalendarPayloadError, match="starts_at"):
        normalize_calendar_payload(payload)


# ---------------------------------------------------------------------------
# process_calendar_sync_payload — integration (repo calls mocked)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_process_connection_upsert_calls_upsert_connection():
    """connection_upsert must call upsert_calendar_connection and log success."""
    from backend.app.modules.calendar_sync.calendar_sync import process_calendar_sync_payload

    with (
        patch(P_UPSERT_CONN,  new=AsyncMock(return_value=FAKE_CONN_ROW)),
        patch(P_UPSERT_BLOCK, new=AsyncMock()) as mock_block,
        patch(P_DELETE_BLOCK, new=AsyncMock()) as mock_delete,
        patch(P_LOG,          new=AsyncMock(return_value=FAKE_LOG_ROW)) as mock_log,
    ):
        result = await process_calendar_sync_payload(None, CONNECTION_UPSERT_PAYLOAD)

    assert result["ok"]         is True
    assert result["event_type"] == "connection_upsert"
    assert result["action"]     == "connection_upserted"
    mock_block.assert_not_awaited()
    mock_delete.assert_not_awaited()
    mock_log.assert_awaited_once()   # success log


@pytest.mark.asyncio
async def test_process_block_upsert_calls_upsert_block():
    """block_upsert must call both upsert_calendar_connection and upsert_calendar_block."""
    from backend.app.modules.calendar_sync.calendar_sync import process_calendar_sync_payload

    with (
        patch(P_UPSERT_CONN,  new=AsyncMock(return_value=FAKE_CONN_ROW)),
        patch(P_UPSERT_BLOCK, new=AsyncMock(return_value=FAKE_BLOCK_ROW)) as mock_block,
        patch(P_DELETE_BLOCK, new=AsyncMock()) as mock_delete,
        patch(P_LOG,          new=AsyncMock(return_value=FAKE_LOG_ROW)),
    ):
        result = await process_calendar_sync_payload(None, BLOCK_UPSERT_PAYLOAD)

    assert result["ok"]     is True
    assert result["action"] == "block_upserted"
    mock_block.assert_awaited_once()
    mock_delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_block_delete_calls_delete_block():
    """block_delete must call delete_calendar_block_by_external_id."""
    from backend.app.modules.calendar_sync.calendar_sync import process_calendar_sync_payload

    with (
        patch(P_UPSERT_CONN,  new=AsyncMock(return_value=FAKE_CONN_ROW)),
        patch(P_UPSERT_BLOCK, new=AsyncMock()) as mock_block,
        patch(P_DELETE_BLOCK, new=AsyncMock(return_value=FAKE_BLOCK_ROW)) as mock_delete,
        patch(P_LOG,          new=AsyncMock(return_value=FAKE_LOG_ROW)),
    ):
        result = await process_calendar_sync_payload(None, BLOCK_DELETE_PAYLOAD)

    assert result["ok"]     is True
    assert result["action"] == "block_deleted"
    mock_delete.assert_awaited_once()
    mock_block.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_logs_success_event():
    """log_calendar_sync_event must be called with status='success' on the happy path."""
    from backend.app.modules.calendar_sync.calendar_sync import process_calendar_sync_payload

    with (
        patch(P_UPSERT_CONN,  new=AsyncMock(return_value=FAKE_CONN_ROW)),
        patch(P_UPSERT_BLOCK, new=AsyncMock(return_value=FAKE_BLOCK_ROW)),
        patch(P_DELETE_BLOCK, new=AsyncMock()),
        patch(P_LOG,          new=AsyncMock(return_value=FAKE_LOG_ROW)) as mock_log,
    ):
        await process_calendar_sync_payload(None, BLOCK_UPSERT_PAYLOAD)

    mock_log.assert_awaited_once()
    _, kwargs = mock_log.call_args
    assert kwargs.get("status") == "success"


@pytest.mark.asyncio
async def test_process_logs_failure_when_repo_call_fails():
    """
    When upsert_calendar_block raises, log_calendar_sync_event must be called
    with status='error' and the function must re-raise a CalendarSyncError.
    """
    from backend.app.modules.calendar_sync.calendar_sync import (
        process_calendar_sync_payload,
        CalendarSyncError,
    )

    with (
        patch(P_UPSERT_CONN,  new=AsyncMock(return_value=FAKE_CONN_ROW)),
        patch(P_UPSERT_BLOCK, new=AsyncMock(side_effect=RuntimeError("DB down"))),
        patch(P_DELETE_BLOCK, new=AsyncMock()),
        patch(P_LOG,          new=AsyncMock(return_value=FAKE_LOG_ROW)) as mock_log,
    ):
        with pytest.raises(CalendarSyncError):
            await process_calendar_sync_payload(None, BLOCK_UPSERT_PAYLOAD)

    mock_log.assert_awaited_once()
    _, kwargs = mock_log.call_args
    assert kwargs.get("status") == "error"


@pytest.mark.asyncio
async def test_process_logs_failure_for_invalid_payload():
    """
    InvalidCalendarPayloadError during normalisation must trigger an error log
    and then re-raise.
    """
    from backend.app.modules.calendar_sync.calendar_sync import (
        process_calendar_sync_payload,
        InvalidCalendarPayloadError,
    )

    bad_payload = {"event_type": "block_upsert"}   # missing clinic_id etc.

    with (
        patch(P_UPSERT_CONN,  new=AsyncMock()),
        patch(P_UPSERT_BLOCK, new=AsyncMock()),
        patch(P_DELETE_BLOCK, new=AsyncMock()),
        patch(P_LOG,          new=AsyncMock(return_value=FAKE_LOG_ROW)) as mock_log,
    ):
        with pytest.raises(InvalidCalendarPayloadError):
            await process_calendar_sync_payload(None, bad_payload)

    mock_log.assert_awaited_once()
    _, kwargs = mock_log.call_args
    assert kwargs.get("status") == "error"


@pytest.mark.asyncio
async def test_process_no_real_db_used():
    """Confirm no real asyncpg Pool object is ever needed — pool=None is fine."""
    from backend.app.modules.calendar_sync.calendar_sync import process_calendar_sync_payload

    with (
        patch(P_UPSERT_CONN,  new=AsyncMock(return_value=FAKE_CONN_ROW)),
        patch(P_UPSERT_BLOCK, new=AsyncMock(return_value=FAKE_BLOCK_ROW)),
        patch(P_DELETE_BLOCK, new=AsyncMock()),
        patch(P_LOG,          new=AsyncMock(return_value=FAKE_LOG_ROW)),
    ):
        result = await process_calendar_sync_payload(None, BLOCK_UPSERT_PAYLOAD)

    assert result["ok"] is True
