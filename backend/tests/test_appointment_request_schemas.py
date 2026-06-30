"""
Unit tests for appointment request Pydantic schemas — PraxisMed Sprint 1 / Module 17
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.app.schemas.appointment_requests import (
    AppointmentRequestAssign,
    AppointmentRequestCreate,
    AppointmentRequestUpdateStatus,
)

_NOW   = datetime(2024, 6, 3,  9, 0, tzinfo=timezone.utc)
_LATER = datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc)

_VALID = dict(
    clinic_id="11111111-1111-4111-8111-111111111111",
    source="vapi",
    patient_name="Maria Muster",
)


# ---------------------------------------------------------------------------
# 1. Valid create schema passes
# ---------------------------------------------------------------------------

def test_valid_create_schema():
    schema = AppointmentRequestCreate(**_VALID)
    assert schema.clinic_id == _VALID["clinic_id"]
    assert schema.source == "vapi"
    assert schema.urgency_level == "normal"
    assert schema.preferred_starts_at is None


# ---------------------------------------------------------------------------
# 2. Empty clinic_id fails
# ---------------------------------------------------------------------------

def test_empty_clinic_id_fails():
    with pytest.raises(ValidationError):
        AppointmentRequestCreate(**{**_VALID, "clinic_id": ""})


# ---------------------------------------------------------------------------
# 3. Empty patient_name fails
# ---------------------------------------------------------------------------

def test_empty_patient_name_fails():
    with pytest.raises(ValidationError):
        AppointmentRequestCreate(**{**_VALID, "patient_name": ""})


# ---------------------------------------------------------------------------
# 4. Invalid source fails
# ---------------------------------------------------------------------------

def test_invalid_source_fails():
    with pytest.raises(ValidationError):
        AppointmentRequestCreate(**{**_VALID, "source": "fax"})


# ---------------------------------------------------------------------------
# 5. Invalid urgency_level fails
# ---------------------------------------------------------------------------

def test_invalid_urgency_fails():
    with pytest.raises(ValidationError):
        AppointmentRequestCreate(**{**_VALID, "urgency_level": "critical"})


# ---------------------------------------------------------------------------
# 6. Invalid preferred time range fails (preferred_ends_at <= preferred_starts_at)
# ---------------------------------------------------------------------------

def test_invalid_time_range_fails():
    with pytest.raises(ValidationError):
        AppointmentRequestCreate(
            **_VALID,
            preferred_starts_at=_LATER,
            preferred_ends_at=_NOW,
        )


def test_equal_preferred_times_fail():
    with pytest.raises(ValidationError):
        AppointmentRequestCreate(
            **_VALID,
            preferred_starts_at=_NOW,
            preferred_ends_at=_NOW,
        )


# ---------------------------------------------------------------------------
# 7. Valid status update passes
# ---------------------------------------------------------------------------

def test_valid_status_update():
    schema = AppointmentRequestUpdateStatus(status="confirmed")
    assert schema.status == "confirmed"
    assert schema.action_required is None


def test_valid_status_update_with_action_required():
    schema = AppointmentRequestUpdateStatus(status="callback_needed", action_required=True)
    assert schema.action_required is True


# ---------------------------------------------------------------------------
# 8. Invalid status update fails
# ---------------------------------------------------------------------------

def test_invalid_status_update_fails():
    with pytest.raises(ValidationError):
        AppointmentRequestUpdateStatus(status="pending")


# ---------------------------------------------------------------------------
# 9. Empty assigned_user_id fails
# ---------------------------------------------------------------------------

def test_empty_assigned_user_id_fails():
    with pytest.raises(ValidationError):
        AppointmentRequestAssign(assigned_user_id="")


def test_valid_assigned_user_id():
    schema = AppointmentRequestAssign(assigned_user_id="33333333-3333-4333-8333-333333333333")
    assert schema.assigned_user_id == "33333333-3333-4333-8333-333333333333"
