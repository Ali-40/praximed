"""
Unit tests for vapi_appointment_capture service — PraxisMed Sprint 1 / Module 18

All tests use AsyncMock objects; no real database or config loader is used.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.modules.vapi.vapi_appointment_capture import (
    InvalidVapiAppointmentCaptureError,
    VapiAppointmentCaptureError,
    capture_vapi_appointment_request,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLINIC_ID  = "11111111-1111-4111-8111-111111111111"
CLINIC_REF = "test-clinic"
CALL_ID    = "vapi-call-abc123"
PATIENT    = "Maria Muster"

_NOW   = datetime(2024, 6, 3,  9, 0, tzinfo=timezone.utc)
_LATER = datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc)

FAKE_ROW = {
    "id":              "22222222-2222-4222-8222-222222222222",
    "clinic_id":       CLINIC_ID,
    "source":          "vapi",
    "source_ref":      CALL_ID,
    "patient_name":    PATIENT,
    "status":          "new",
    "urgency_level":   "normal",
    "action_required": True,
    "created_at":      "2024-06-03T09:00:00+00:00",
    "updated_at":      "2024-06-03T09:00:00+00:00",
}

REPO_PATH = "backend.app.modules.vapi.vapi_appointment_capture.appointment_request_repo"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(clinic_id: str = CLINIC_ID) -> MagicMock:
    cfg = MagicMock()
    cfg.clinic_id = clinic_id
    return cfg


def _make_loader(config=None) -> MagicMock:
    loader = MagicMock()
    loader.get = AsyncMock(return_value=config or _make_config())
    return loader


def _make_pool() -> MagicMock:
    return MagicMock()


# ---------------------------------------------------------------------------
# 1. Loads clinic config via config_loader.get
# ---------------------------------------------------------------------------

async def test_loads_clinic_config():
    loader = _make_loader()
    with patch(f"{REPO_PATH}.create_appointment_request", new=AsyncMock(return_value=FAKE_ROW)):
        await capture_vapi_appointment_request(_make_pool(), loader, CLINIC_REF, CALL_ID, PATIENT)
    loader.get.assert_awaited_once_with(CLINIC_REF)


# ---------------------------------------------------------------------------
# 2. Calls create_appointment_request
# ---------------------------------------------------------------------------

async def test_calls_create_appointment_request():
    mock_create = AsyncMock(return_value=FAKE_ROW)
    with patch(f"{REPO_PATH}.create_appointment_request", new=mock_create):
        await capture_vapi_appointment_request(_make_pool(), _make_loader(), CLINIC_REF, CALL_ID, PATIENT)
    mock_create.assert_awaited_once()


# ---------------------------------------------------------------------------
# 3. Passes source="vapi"
# ---------------------------------------------------------------------------

async def test_passes_source_vapi():
    mock_create = AsyncMock(return_value=FAKE_ROW)
    with patch(f"{REPO_PATH}.create_appointment_request", new=mock_create):
        await capture_vapi_appointment_request(_make_pool(), _make_loader(), CLINIC_REF, CALL_ID, PATIENT)
    assert mock_create.call_args.kwargs["source"] == "vapi"


# ---------------------------------------------------------------------------
# 4. Passes source_ref=call_id
# ---------------------------------------------------------------------------

async def test_passes_source_ref_call_id():
    mock_create = AsyncMock(return_value=FAKE_ROW)
    with patch(f"{REPO_PATH}.create_appointment_request", new=mock_create):
        await capture_vapi_appointment_request(_make_pool(), _make_loader(), CLINIC_REF, CALL_ID, PATIENT)
    assert mock_create.call_args.kwargs["source_ref"] == CALL_ID


# ---------------------------------------------------------------------------
# 5. Sets status="new"
# ---------------------------------------------------------------------------

async def test_sets_status_new():
    mock_create = AsyncMock(return_value=FAKE_ROW)
    with patch(f"{REPO_PATH}.create_appointment_request", new=mock_create):
        await capture_vapi_appointment_request(_make_pool(), _make_loader(), CLINIC_REF, CALL_ID, PATIENT)
    assert mock_create.call_args.kwargs["status"] == "new"


# ---------------------------------------------------------------------------
# 6. Sets action_required=True
# ---------------------------------------------------------------------------

async def test_sets_action_required_true():
    mock_create = AsyncMock(return_value=FAKE_ROW)
    with patch(f"{REPO_PATH}.create_appointment_request", new=mock_create):
        await capture_vapi_appointment_request(_make_pool(), _make_loader(), CLINIC_REF, CALL_ID, PATIENT)
    assert mock_create.call_args.kwargs["action_required"] is True


# ---------------------------------------------------------------------------
# 7. Returns message stating staff confirmation is required
# ---------------------------------------------------------------------------

async def test_returns_staff_confirmation_message():
    with patch(f"{REPO_PATH}.create_appointment_request", new=AsyncMock(return_value=FAKE_ROW)):
        result = await capture_vapi_appointment_request(
            _make_pool(), _make_loader(), CLINIC_REF, CALL_ID, PATIENT
        )
    assert result["ok"] is True
    assert "confirm" in result["message"].lower()
    assert result["request"] == FAKE_ROW
    assert result["clinic_id"] == CLINIC_ID


# ---------------------------------------------------------------------------
# 8. Empty clinic_ref raises InvalidVapiAppointmentCaptureError
# ---------------------------------------------------------------------------

async def test_empty_clinic_ref_raises():
    with pytest.raises(InvalidVapiAppointmentCaptureError):
        await capture_vapi_appointment_request(_make_pool(), _make_loader(), "", CALL_ID, PATIENT)


# ---------------------------------------------------------------------------
# 9. Empty call_id raises InvalidVapiAppointmentCaptureError
# ---------------------------------------------------------------------------

async def test_empty_call_id_raises():
    with pytest.raises(InvalidVapiAppointmentCaptureError):
        await capture_vapi_appointment_request(_make_pool(), _make_loader(), CLINIC_REF, "", PATIENT)


# ---------------------------------------------------------------------------
# 10. Empty patient_name raises InvalidVapiAppointmentCaptureError
# ---------------------------------------------------------------------------

async def test_empty_patient_name_raises():
    with pytest.raises(InvalidVapiAppointmentCaptureError):
        await capture_vapi_appointment_request(_make_pool(), _make_loader(), CLINIC_REF, CALL_ID, "")


# ---------------------------------------------------------------------------
# 11. Invalid preferred time range raises InvalidVapiAppointmentCaptureError
# ---------------------------------------------------------------------------

async def test_invalid_time_range_raises():
    with pytest.raises(InvalidVapiAppointmentCaptureError):
        await capture_vapi_appointment_request(
            _make_pool(), _make_loader(), CLINIC_REF, CALL_ID, PATIENT,
            preferred_starts_at=_LATER,
            preferred_ends_at=_NOW,
        )


async def test_equal_preferred_times_raise():
    with pytest.raises(InvalidVapiAppointmentCaptureError):
        await capture_vapi_appointment_request(
            _make_pool(), _make_loader(), CLINIC_REF, CALL_ID, PATIENT,
            preferred_starts_at=_NOW,
            preferred_ends_at=_NOW,
        )


# ---------------------------------------------------------------------------
# 12. Repository error propagates cleanly
# ---------------------------------------------------------------------------

async def test_repo_error_propagates():
    from backend.app.db.repositories.appointment_request_repo import InvalidAppointmentRequestError
    with patch(
        f"{REPO_PATH}.create_appointment_request",
        new=AsyncMock(side_effect=InvalidAppointmentRequestError("repo bad input")),
    ):
        with pytest.raises(InvalidAppointmentRequestError):
            await capture_vapi_appointment_request(
                _make_pool(), _make_loader(), CLINIC_REF, CALL_ID, PATIENT
            )
