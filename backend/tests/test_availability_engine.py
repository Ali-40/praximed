"""
Unit tests for backend/app/modules/calendar_sync/availability_engine.py

No real database connection is used.  calendar_repo.get_overlapping_blocks is
patched at the engine's import site so each test controls exactly what the
"database" returns.

All datetimes are timezone-aware (UTC or Europe/Vienna).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, patch
from zoneinfo import ZoneInfo

import pytest

from backend.app.core.config_loader import ClinicConfig

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

CLINIC_UUID = "11111111-1111-4111-8111-111111111111"
VIENNA_TZ   = ZoneInfo("Europe/Vienna")

WEEKDAY_OPENING_HOURS = {
    "monday":    {"open": "08:00", "close": "18:00"},
    "tuesday":   {"open": "08:00", "close": "18:00"},
    "wednesday": {"open": "08:00", "close": "18:00"},
    "thursday":  {"open": "08:00", "close": "18:00"},
    "friday":    {"open": "08:00", "close": "18:00"},
    "saturday":  None,
    "sunday":    None,
}


def _make_config(
    opening_hours: dict | None = None,
    calendar_rules: dict | None = None,
    timezone_str: str = "Europe/Vienna",
) -> ClinicConfig:
    return ClinicConfig(
        tenant_id=CLINIC_UUID,
        clinic_name="Praxis Dr. Muster",
        timezone=timezone_str,
        opening_hours=opening_hours if opening_hours is not None else WEEKDAY_OPENING_HOURS,
        calendar_rules=calendar_rules,
    )


def _vienna(year: int, month: int, day: int, hour: int, minute: int = 0) -> datetime:
    """Return an aware datetime in Europe/Vienna."""
    return datetime(year, month, day, hour, minute, tzinfo=VIENNA_TZ)


# Monday 2025-06-02 in Vienna
MONDAY     = date(2025, 6, 2)
MON_OPEN   = _vienna(2025, 6, 2,  8,  0)   # 08:00 — opening time
MON_MID    = _vienna(2025, 6, 2,  9,  0)   # 09:00 — inside hours
MON_MID2   = _vienna(2025, 6, 2, 10,  0)   # 10:00 — inside hours
MON_CLOSE  = _vienna(2025, 6, 2, 18,  0)   # 18:00 — closing time

# Saturday 2025-06-07 (closed)
SATURDAY   = date(2025, 6, 7)
SAT_MID    = _vienna(2025, 6, 7, 10,  0)
SAT_MID2   = _vienna(2025, 6, 7, 11,  0)

PATCH_TARGET = (
    "backend.app.modules.calendar_sync.availability_engine.get_overlapping_blocks"
)

# ---------------------------------------------------------------------------
# 1. Slot inside opening hours → True
# ---------------------------------------------------------------------------


def test_within_opening_hours_inside():
    from backend.app.modules.calendar_sync.availability_engine import is_within_opening_hours

    config = _make_config()
    assert is_within_opening_hours(config, MON_MID, MON_MID2) is True


# ---------------------------------------------------------------------------
# 2. Slot before opening time → False
# ---------------------------------------------------------------------------


def test_within_opening_hours_before_open():
    from backend.app.modules.calendar_sync.availability_engine import is_within_opening_hours

    config = _make_config()
    too_early_start = _vienna(2025, 6, 2, 7, 0)
    too_early_end   = _vienna(2025, 6, 2, 7, 30)
    assert is_within_opening_hours(config, too_early_start, too_early_end) is False


# ---------------------------------------------------------------------------
# 3. Slot after closing time → False
# ---------------------------------------------------------------------------


def test_within_opening_hours_after_close():
    from backend.app.modules.calendar_sync.availability_engine import is_within_opening_hours

    config = _make_config()
    late_start = _vienna(2025, 6, 2, 18,  0)
    late_end   = _vienna(2025, 6, 2, 18, 30)
    assert is_within_opening_hours(config, late_start, late_end) is False


# ---------------------------------------------------------------------------
# 4. Closed day → False
# ---------------------------------------------------------------------------


def test_within_opening_hours_closed_day():
    from backend.app.modules.calendar_sync.availability_engine import is_within_opening_hours

    config = _make_config()
    assert is_within_opening_hours(config, SAT_MID, SAT_MID2) is False


# ---------------------------------------------------------------------------
# 5. Invalid range raises InvalidAvailabilityRangeError
# ---------------------------------------------------------------------------


def test_within_opening_hours_invalid_range_raises():
    from backend.app.modules.calendar_sync.availability_engine import (
        is_within_opening_hours,
        InvalidAvailabilityRangeError,
    )

    config = _make_config()
    with pytest.raises(InvalidAvailabilityRangeError):
        is_within_opening_hours(config, MON_MID2, MON_MID)  # ends before starts


def test_within_opening_hours_equal_times_raises():
    from backend.app.modules.calendar_sync.availability_engine import (
        is_within_opening_hours,
        InvalidAvailabilityRangeError,
    )

    config = _make_config()
    with pytest.raises(InvalidAvailabilityRangeError):
        is_within_opening_hours(config, MON_MID, MON_MID)   # zero duration


# ---------------------------------------------------------------------------
# 6. get_slot_duration_minutes returns configured value
# ---------------------------------------------------------------------------


def test_get_slot_duration_returns_config_value():
    from backend.app.modules.calendar_sync.availability_engine import get_slot_duration_minutes

    config = _make_config(calendar_rules={"slot_minutes": 20})
    assert get_slot_duration_minutes(config) == 20


# ---------------------------------------------------------------------------
# 7. get_slot_duration_minutes falls back to default
# ---------------------------------------------------------------------------


def test_get_slot_duration_falls_back_to_default():
    from backend.app.modules.calendar_sync.availability_engine import get_slot_duration_minutes

    config_no_rules = _make_config(calendar_rules=None)
    assert get_slot_duration_minutes(config_no_rules) == 30

    config_empty_rules = _make_config(calendar_rules={})
    assert get_slot_duration_minutes(config_empty_rules) == 30

    assert get_slot_duration_minutes(config_no_rules, default_minutes=15) == 15


# ---------------------------------------------------------------------------
# 8. is_slot_bookable returns False outside opening hours without calling DB
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_slot_bookable_false_outside_hours_no_db_call():
    from backend.app.modules.calendar_sync.availability_engine import is_slot_bookable

    config = _make_config()
    with patch(PATCH_TARGET, new=AsyncMock()) as mock_get:
        result = await is_slot_bookable(None, config, SAT_MID, SAT_MID2)

    assert result is False
    mock_get.assert_not_awaited()   # DB must NOT be called for out-of-hours slots


# ---------------------------------------------------------------------------
# 9. is_slot_bookable returns False when overlapping blocks exist
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_slot_bookable_false_when_overlapping_blocks():
    from backend.app.modules.calendar_sync.availability_engine import is_slot_bookable

    config = _make_config()
    fake_block = {
        "id": "block-id", "clinic_id": CLINIC_UUID,
        "starts_at": MON_MID, "ends_at": MON_MID2,
        "block_type": "busy",
    }
    with patch(PATCH_TARGET, new=AsyncMock(return_value=[fake_block])):
        result = await is_slot_bookable(None, config, MON_MID, MON_MID2)

    assert result is False


# ---------------------------------------------------------------------------
# 10. is_slot_bookable returns True when no overlaps
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_slot_bookable_true_when_no_overlaps():
    from backend.app.modules.calendar_sync.availability_engine import is_slot_bookable

    config = _make_config()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=[])):
        result = await is_slot_bookable(None, config, MON_MID, MON_MID2)

    assert result is True


# ---------------------------------------------------------------------------
# 11. suggest_available_slots returns slots for an open day
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggest_available_slots_returns_slots_open_day():
    from backend.app.modules.calendar_sync.availability_engine import suggest_available_slots

    config = _make_config(calendar_rules={"slot_minutes": 60})

    with patch(PATCH_TARGET, new=AsyncMock(return_value=[])):
        slots = await suggest_available_slots(None, config, MONDAY, limit=3)

    assert len(slots) == 3
    for slot in slots:
        assert "starts_at" in slot
        assert "ends_at" in slot
        assert slot["ends_at"] > slot["starts_at"]
        assert slot["ends_at"] - slot["starts_at"] == timedelta(hours=1)


@pytest.mark.asyncio
async def test_suggest_available_slots_returns_empty_on_closed_day():
    from backend.app.modules.calendar_sync.availability_engine import suggest_available_slots

    config = _make_config()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=[])):
        slots = await suggest_available_slots(None, config, SATURDAY, limit=5)

    assert slots == []


# ---------------------------------------------------------------------------
# 12. suggest_available_slots excludes blocked slots
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggest_available_slots_excludes_blocked_slots():
    from backend.app.modules.calendar_sync.availability_engine import suggest_available_slots

    config = _make_config(calendar_rules={"slot_minutes": 60})

    # Block the first two hours (08:00–10:00) on Monday
    block_1 = {
        "id": "blk-1", "clinic_id": CLINIC_UUID,
        "starts_at": _vienna(2025, 6, 2,  8, 0),
        "ends_at":   _vienna(2025, 6, 2,  9, 0),
        "block_type": "busy",
    }
    block_2 = {
        "id": "blk-2", "clinic_id": CLINIC_UUID,
        "starts_at": _vienna(2025, 6, 2,  9, 0),
        "ends_at":   _vienna(2025, 6, 2, 10, 0),
        "block_type": "busy",
    }

    with patch(PATCH_TARGET, new=AsyncMock(return_value=[block_1, block_2])):
        slots = await suggest_available_slots(None, config, MONDAY, limit=3)

    assert len(slots) == 3
    # Every returned slot must start at or after 10:00 (first free hour)
    for slot in slots:
        assert slot["starts_at"] >= _vienna(2025, 6, 2, 10, 0), (
            f"Expected slot after blocked period but got {slot['starts_at']}"
        )


@pytest.mark.asyncio
async def test_suggest_available_slots_respects_limit():
    from backend.app.modules.calendar_sync.availability_engine import suggest_available_slots

    config = _make_config(calendar_rules={"slot_minutes": 30})

    with patch(PATCH_TARGET, new=AsyncMock(return_value=[])):
        slots = await suggest_available_slots(None, config, MONDAY, limit=2)

    assert len(slots) == 2


@pytest.mark.asyncio
async def test_suggest_available_slots_single_db_call():
    """suggest_available_slots must batch-fetch blocks in a single DB call."""
    from backend.app.modules.calendar_sync.availability_engine import suggest_available_slots

    config = _make_config(calendar_rules={"slot_minutes": 60})
    mock_get = AsyncMock(return_value=[])

    with patch(PATCH_TARGET, new=mock_get):
        await suggest_available_slots(None, config, MONDAY, limit=5)

    assert mock_get.await_count == 1, (
        f"Expected exactly 1 DB call, got {mock_get.await_count}"
    )
