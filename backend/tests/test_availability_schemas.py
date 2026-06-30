"""
Unit tests for availability Pydantic schemas — PraxisMed Sprint 1 / Module 9
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from backend.app.schemas.availability import (
    AvailabilityCheckRequest,
    SuggestedSlotsRequest,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_T0 = datetime(2024, 6, 1, 9, 0, tzinfo=timezone.utc)
_T1 = datetime(2024, 6, 1, 9, 30, tzinfo=timezone.utc)
_DATE = date(2024, 6, 1)
_REF = "11111111-1111-4111-8111-111111111111"


# ---------------------------------------------------------------------------
# AvailabilityCheckRequest
# ---------------------------------------------------------------------------


def test_availability_check_request_valid():
    req = AvailabilityCheckRequest(clinic_ref=_REF, starts_at=_T0, ends_at=_T1)
    assert req.clinic_ref == _REF
    assert req.starts_at == _T0
    assert req.ends_at == _T1


def test_availability_check_request_empty_clinic_ref():
    with pytest.raises(ValidationError):
        AvailabilityCheckRequest(clinic_ref="", starts_at=_T0, ends_at=_T1)


def test_availability_check_request_whitespace_clinic_ref():
    with pytest.raises(ValidationError):
        AvailabilityCheckRequest(clinic_ref="   ", starts_at=_T0, ends_at=_T1)


def test_availability_check_request_ends_equal_starts():
    with pytest.raises(ValidationError):
        AvailabilityCheckRequest(clinic_ref=_REF, starts_at=_T0, ends_at=_T0)


def test_availability_check_request_ends_before_starts():
    with pytest.raises(ValidationError):
        AvailabilityCheckRequest(clinic_ref=_REF, starts_at=_T1, ends_at=_T0)


# ---------------------------------------------------------------------------
# SuggestedSlotsRequest
# ---------------------------------------------------------------------------


def test_suggested_slots_request_valid():
    req = SuggestedSlotsRequest(clinic_ref=_REF, date=_DATE)
    assert req.clinic_ref == _REF
    assert req.date == _DATE
    assert req.limit == 5  # default


def test_suggested_slots_request_custom_limit():
    req = SuggestedSlotsRequest(clinic_ref=_REF, date=_DATE, limit=10)
    assert req.limit == 10


def test_suggested_slots_request_empty_clinic_ref():
    with pytest.raises(ValidationError):
        SuggestedSlotsRequest(clinic_ref="", date=_DATE)


def test_suggested_slots_request_limit_zero():
    with pytest.raises(ValidationError):
        SuggestedSlotsRequest(clinic_ref=_REF, date=_DATE, limit=0)


def test_suggested_slots_request_limit_too_high():
    with pytest.raises(ValidationError):
        SuggestedSlotsRequest(clinic_ref=_REF, date=_DATE, limit=21)


def test_suggested_slots_request_limit_boundary_low():
    req = SuggestedSlotsRequest(clinic_ref=_REF, date=_DATE, limit=1)
    assert req.limit == 1


def test_suggested_slots_request_limit_boundary_high():
    req = SuggestedSlotsRequest(clinic_ref=_REF, date=_DATE, limit=20)
    assert req.limit == 20
