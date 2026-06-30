"""
Availability Engine — PraxisMed Sprint 1 / Module 5

Decides whether a requested appointment slot is bookable by combining two
independent checks:

  1. Opening-hours check  (pure Python, no I/O)
     Is the slot within the clinic's configured weekday hours?

  2. Calendar-block check  (async database read via calendar_repo)
     Does any existing block overlap the slot?

Only when both checks pass does a slot qualify as bookable.

Opening-hours format (stored in ClinicConfig.opening_hours):
  {
    "monday":    {"open": "08:00", "close": "18:00"},
    "tuesday":   {"open": "08:00", "close": "18:00"},
    ...
    "saturday":  null,    # null or absent key → closed
    "sunday":    null
  }

If opening_hours is absent from the config the engine falls back to
DEFAULT_OPENING_HOURS (Mon–Fri 08:00–18:00, weekends closed).

Calendar-rules format (stored in ClinicConfig.calendar_rules):
  {"slot_minutes": 30}
"""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from backend.app.core.config_loader import ClinicConfig
from backend.app.db.repositories.calendar_repo import get_overlapping_blocks

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class AvailabilityEngineError(RuntimeError):
    """Base exception for availability engine failures."""


class InvalidAvailabilityRangeError(AvailabilityEngineError):
    """Raised when ends_at is not strictly greater than starts_at."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Ordered to match Python's datetime.weekday() (0 = Monday … 6 = Sunday)
_WEEKDAY_NAMES = [
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday",
]

DEFAULT_OPENING_HOURS: Dict[str, Optional[Dict[str, str]]] = {
    "monday":    {"open": "08:00", "close": "18:00"},
    "tuesday":   {"open": "08:00", "close": "18:00"},
    "wednesday": {"open": "08:00", "close": "18:00"},
    "thursday":  {"open": "08:00", "close": "18:00"},
    "friday":    {"open": "08:00", "close": "18:00"},
    "saturday":  None,
    "sunday":    None,
}

_TIME_RE = re.compile(r"^(\d{2}):(\d{2})$")

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _assert_valid_range(starts_at: datetime, ends_at: datetime) -> None:
    if ends_at <= starts_at:
        raise InvalidAvailabilityRangeError(
            f"ends_at must be strictly after starts_at; "
            f"got starts_at={starts_at.isoformat()!r}, ends_at={ends_at.isoformat()!r}"
        )


def _get_timezone(config: ClinicConfig) -> ZoneInfo:
    tz_name = config.timezone or "Europe/Vienna"
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError):
        return ZoneInfo("Europe/Vienna")


def _parse_hhmm(value: str) -> time:
    """Parse 'HH:MM' into a :class:`datetime.time` object."""
    m = _TIME_RE.match(value)
    if not m:
        raise AvailabilityEngineError(f"Invalid time string {value!r}; expected HH:MM")
    return time(int(m.group(1)), int(m.group(2)))


def _get_opening_hours(config: ClinicConfig) -> Dict[str, Optional[Dict[str, str]]]:
    return config.opening_hours if config.opening_hours is not None else DEFAULT_OPENING_HOURS


def _localize(dt: datetime, tz: ZoneInfo) -> datetime:
    """Return *dt* converted to *tz*.  If *dt* is naive, assume UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)


# ---------------------------------------------------------------------------
# 1. is_within_opening_hours
# ---------------------------------------------------------------------------


def is_within_opening_hours(
    config: ClinicConfig,
    starts_at: datetime,
    ends_at: datetime,
) -> bool:
    """
    Return True only when the *entire* slot is within the clinic's opening hours.

    The check is performed in the clinic's local timezone.  Both endpoints are
    tested against the weekday hours for the *start* day.  A slot that straddles
    midnight is therefore always rejected (medical appointments should not do so).

    Returns False for closed days, out-of-hours slots, and invalid ranges.
    """
    if ends_at <= starts_at:
        raise InvalidAvailabilityRangeError(
            f"ends_at must be strictly after starts_at; "
            f"got starts_at={starts_at.isoformat()!r}, ends_at={ends_at.isoformat()!r}"
        )

    tz = _get_timezone(config)
    local_start = _localize(starts_at, tz)
    local_end   = _localize(ends_at,   tz)

    weekday_name = _WEEKDAY_NAMES[local_start.weekday()]
    hours = _get_opening_hours(config).get(weekday_name)

    if not hours:
        return False  # closed day

    open_time  = _parse_hhmm(hours["open"])
    close_time = _parse_hhmm(hours["close"])

    slot_start = local_start.time().replace(tzinfo=None)
    slot_end   = local_end.time().replace(tzinfo=None)

    # Slot must not straddle midnight (ends on the same calendar day)
    if local_end.date() > local_start.date():
        return False

    return slot_start >= open_time and slot_end <= close_time


# ---------------------------------------------------------------------------
# 2. get_slot_duration_minutes
# ---------------------------------------------------------------------------


def get_slot_duration_minutes(config: ClinicConfig, default_minutes: int = 30) -> int:
    """
    Return the slot duration in minutes from *config.calendar_rules*.

    Falls back to *default_minutes* (30) when the key is absent.
    """
    if config.calendar_rules and "slot_minutes" in config.calendar_rules:
        return int(config.calendar_rules["slot_minutes"])
    return default_minutes


# ---------------------------------------------------------------------------
# 3. is_slot_bookable
# ---------------------------------------------------------------------------


async def is_slot_bookable(
    pool: Any,
    config: ClinicConfig,
    starts_at: datetime,
    ends_at: datetime,
) -> bool:
    """
    Return True when both checks pass:

      1. The slot is within the clinic's opening hours.
      2. No existing calendar block overlaps the slot.

    The database is only queried when the opening-hours check passes.
    """
    if not is_within_opening_hours(config, starts_at, ends_at):
        return False

    blocks = await get_overlapping_blocks(pool, config.tenant_id, starts_at, ends_at)
    return len(blocks) == 0


# ---------------------------------------------------------------------------
# 4. suggest_available_slots
# ---------------------------------------------------------------------------


async def suggest_available_slots(
    pool: Any,
    config: ClinicConfig,
    target_date: date,
    limit: int = 5,
) -> List[Dict[str, datetime]]:
    """
    Return up to *limit* bookable slots on *target_date*.

    Algorithm:
      1. Determine opening hours for the weekday of *target_date*.
      2. Build candidate slots of *slot_duration_minutes* from open to close.
      3. Fetch all calendar blocks that overlap the full day in one DB call.
      4. Keep only candidates with no overlapping block.
      5. Return the first *limit* passing candidates.

    Each returned dict has ``starts_at`` and ``ends_at`` as timezone-aware
    datetimes in the clinic's local timezone.
    """
    tz = _get_timezone(config)
    weekday_name = _WEEKDAY_NAMES[target_date.weekday()]
    hours = _get_opening_hours(config).get(weekday_name)

    if not hours:
        return []  # clinic is closed that day

    open_time  = _parse_hhmm(hours["open"])
    close_time = _parse_hhmm(hours["close"])
    slot_delta = timedelta(minutes=get_slot_duration_minutes(config))

    # Build aware datetimes for the full business day
    day_open  = datetime(target_date.year, target_date.month, target_date.day,
                         open_time.hour, open_time.minute, tzinfo=tz)
    day_close = datetime(target_date.year, target_date.month, target_date.day,
                         close_time.hour, close_time.minute, tzinfo=tz)

    # Single DB round-trip: fetch every block that touches this day
    day_start = datetime(target_date.year, target_date.month, target_date.day,
                         0, 0, 0, tzinfo=tz)
    day_end   = datetime(target_date.year, target_date.month, target_date.day,
                         23, 59, 59, tzinfo=tz)
    day_blocks = await get_overlapping_blocks(pool, config.tenant_id, day_start, day_end)

    available: List[Dict[str, datetime]] = []
    cursor = day_open

    while cursor + slot_delta <= day_close:
        slot_end = cursor + slot_delta

        # Check against in-memory blocks (no extra DB calls)
        blocked = any(
            b["starts_at"] < slot_end and b["ends_at"] > cursor
            for b in day_blocks
        )

        if not blocked:
            available.append({"starts_at": cursor, "ends_at": slot_end})
            if len(available) >= limit:
                break

        cursor += slot_delta

    return available
