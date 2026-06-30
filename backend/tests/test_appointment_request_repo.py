"""
Unit tests for appointment_request_repo — PraxisMed Sprint 1 / Module 16

All tests use AsyncMock pool objects; no real database connection is made.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.db.repositories.appointment_request_repo import (
    AppointmentRequestRepoError,
    InvalidAppointmentRequestError,
    archive_appointment_request,
    assign_appointment_request,
    create_appointment_request,
    get_appointment_request_by_id,
    list_appointment_requests,
    mark_callback_needed,
    update_appointment_request_status,
)

CLINIC_ID  = "11111111-1111-4111-8111-111111111111"
REQUEST_ID = "22222222-2222-4222-8222-222222222222"
USER_ID    = "33333333-3333-4333-8333-333333333333"

_NOW = datetime(2024, 6, 3, 9, 0, tzinfo=timezone.utc)

FAKE_ROW = {
    "id":                  REQUEST_ID,
    "clinic_id":           CLINIC_ID,
    "source":              "vapi",
    "source_ref":          None,
    "patient_name":        "Maria Muster",
    "patient_phone":       "+43 123 456789",
    "patient_email":       None,
    "date_of_birth":       None,
    "reason":              None,
    "preferred_starts_at": None,
    "preferred_ends_at":   None,
    "status":              "new",
    "urgency_level":       "normal",
    "action_required":     True,
    "assigned_user_id":    None,
    "raw_payload":         None,
    "created_at":          _NOW,
    "updated_at":          _NOW,
}


def _pool_with_row(row=None):
    """Return a fake pool whose fetchrow/fetch always returns *row*."""
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row if row is not None else FAKE_ROW)
    pool.fetch    = AsyncMock(return_value=[FAKE_ROW])
    return pool


# ---------------------------------------------------------------------------
# 1. create_appointment_request calls fetchrow
# ---------------------------------------------------------------------------

async def test_create_calls_fetchrow():
    pool = _pool_with_row()
    result = await create_appointment_request(pool, CLINIC_ID, "vapi", "Maria Muster")
    pool.fetchrow.assert_awaited_once()
    assert result["patient_name"] == "Maria Muster"


# ---------------------------------------------------------------------------
# 2–3. create_appointment_request raises for empty required fields
# ---------------------------------------------------------------------------

async def test_create_empty_clinic_id_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidAppointmentRequestError):
        await create_appointment_request(pool, "", "vapi", "Maria Muster")


async def test_create_empty_patient_name_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidAppointmentRequestError):
        await create_appointment_request(pool, CLINIC_ID, "vapi", "")


# ---------------------------------------------------------------------------
# 4. create_appointment_request validates invalid source
# ---------------------------------------------------------------------------

async def test_create_invalid_source_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidAppointmentRequestError):
        await create_appointment_request(pool, CLINIC_ID, "fax", "Maria Muster")


# ---------------------------------------------------------------------------
# 5. create_appointment_request validates invalid status
# ---------------------------------------------------------------------------

async def test_create_invalid_status_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidAppointmentRequestError):
        await create_appointment_request(
            pool, CLINIC_ID, "vapi", "Maria Muster", status="unknown"
        )


# ---------------------------------------------------------------------------
# 6. create_appointment_request validates invalid urgency_level
# ---------------------------------------------------------------------------

async def test_create_invalid_urgency_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidAppointmentRequestError):
        await create_appointment_request(
            pool, CLINIC_ID, "vapi", "Maria Muster", urgency_level="critical"
        )


# ---------------------------------------------------------------------------
# 7. create_appointment_request validates invalid preferred time range
# ---------------------------------------------------------------------------

async def test_create_invalid_time_range_raises():
    pool = _pool_with_row()
    starts = datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc)
    ends   = datetime(2024, 6, 3,  9, 0, tzinfo=timezone.utc)  # before starts
    with pytest.raises(InvalidAppointmentRequestError):
        await create_appointment_request(
            pool, CLINIC_ID, "vapi", "Maria Muster",
            preferred_starts_at=starts,
            preferred_ends_at=ends,
        )


# ---------------------------------------------------------------------------
# 8. get_appointment_request_by_id calls fetchrow and filters by clinic_id
# ---------------------------------------------------------------------------

async def test_get_by_id_calls_fetchrow_and_filters_clinic():
    pool = _pool_with_row()
    result = await get_appointment_request_by_id(pool, CLINIC_ID, REQUEST_ID)
    pool.fetchrow.assert_awaited_once()
    args = pool.fetchrow.call_args[0]
    assert CLINIC_ID in args, "clinic_id must be passed as a SQL parameter"
    assert result["id"] == REQUEST_ID


# ---------------------------------------------------------------------------
# 9. list_appointment_requests calls fetch
# ---------------------------------------------------------------------------

async def test_list_calls_fetch():
    pool = _pool_with_row()
    results = await list_appointment_requests(pool, CLINIC_ID)
    pool.fetch.assert_awaited_once()
    assert isinstance(results, list)
    assert len(results) == 1


# ---------------------------------------------------------------------------
# 10. list_appointment_requests validates limit
# ---------------------------------------------------------------------------

async def test_list_limit_zero_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidAppointmentRequestError):
        await list_appointment_requests(pool, CLINIC_ID, limit=0)


async def test_list_limit_too_high_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidAppointmentRequestError):
        await list_appointment_requests(pool, CLINIC_ID, limit=101)


async def test_list_limit_boundary_valid():
    pool = _pool_with_row()
    await list_appointment_requests(pool, CLINIC_ID, limit=1)
    await list_appointment_requests(pool, CLINIC_ID, limit=100)
    assert pool.fetch.await_count == 2


# ---------------------------------------------------------------------------
# 11. list_appointment_requests supports status filter
# ---------------------------------------------------------------------------

async def test_list_status_filter():
    pool = _pool_with_row()
    await list_appointment_requests(pool, CLINIC_ID, status="new")
    pool.fetch.assert_awaited_once()
    args = pool.fetch.call_args[0]
    assert "new" in args, "status value must be passed as a SQL parameter"


# ---------------------------------------------------------------------------
# 12. list_appointment_requests supports action_required filter
# ---------------------------------------------------------------------------

async def test_list_action_required_filter():
    pool = _pool_with_row()
    await list_appointment_requests(pool, CLINIC_ID, action_required=True)
    pool.fetch.assert_awaited_once()
    args = pool.fetch.call_args[0]
    assert True in args, "action_required value must be passed as a SQL parameter"


# ---------------------------------------------------------------------------
# 13. update_appointment_request_status calls fetchrow
# ---------------------------------------------------------------------------

async def test_update_status_calls_fetchrow():
    pool = _pool_with_row()
    result = await update_appointment_request_status(pool, CLINIC_ID, REQUEST_ID, "confirmed")
    pool.fetchrow.assert_awaited_once()
    assert result is not None


# ---------------------------------------------------------------------------
# 14. update_appointment_request_status validates invalid status
# ---------------------------------------------------------------------------

async def test_update_status_invalid_raises():
    pool = _pool_with_row()
    with pytest.raises(InvalidAppointmentRequestError):
        await update_appointment_request_status(pool, CLINIC_ID, REQUEST_ID, "pending")


# ---------------------------------------------------------------------------
# 15. assign_appointment_request calls fetchrow
# ---------------------------------------------------------------------------

async def test_assign_calls_fetchrow():
    pool = _pool_with_row()
    result = await assign_appointment_request(pool, CLINIC_ID, REQUEST_ID, USER_ID)
    pool.fetchrow.assert_awaited_once()
    args = pool.fetchrow.call_args[0]
    assert USER_ID in args, "assigned_user_id must be passed as a SQL parameter"


# ---------------------------------------------------------------------------
# 16. mark_callback_needed calls fetchrow
# ---------------------------------------------------------------------------

async def test_mark_callback_needed_calls_fetchrow():
    pool = _pool_with_row()
    await mark_callback_needed(pool, CLINIC_ID, REQUEST_ID)
    pool.fetchrow.assert_awaited_once()
    args = pool.fetchrow.call_args[0]
    assert CLINIC_ID in args


# ---------------------------------------------------------------------------
# 17. archive_appointment_request calls fetchrow
# ---------------------------------------------------------------------------

async def test_archive_calls_fetchrow():
    pool = _pool_with_row()
    await archive_appointment_request(pool, CLINIC_ID, REQUEST_ID)
    pool.fetchrow.assert_awaited_once()
    args = pool.fetchrow.call_args[0]
    assert CLINIC_ID in args


# ---------------------------------------------------------------------------
# 18. SQL uses parameterized placeholders, not string formatting
# ---------------------------------------------------------------------------

async def test_sql_uses_parameterized_placeholders():
    captured_sql: list[str] = []

    async def capturing_fetchrow(sql, *args):
        captured_sql.append(sql)
        return FAKE_ROW

    pool = MagicMock()
    pool.fetchrow = capturing_fetchrow

    await create_appointment_request(pool, CLINIC_ID, "vapi", "Maria Muster")

    assert captured_sql, "fetchrow was never called"
    assert "$1" in captured_sql[0], "SQL must use $1 parameterized placeholders"
    assert "%" not in captured_sql[0], "SQL must not use %-style string formatting"
    assert "{" not in captured_sql[0], "SQL must not use {}-style string formatting"
