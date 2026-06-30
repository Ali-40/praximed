"""
Tests for patient_repo — Sprint 2 / Module 25.

All tests use a MagicMock pool with AsyncMock fetchrow/fetch.
No real database connection is used.
"""

from __future__ import annotations

import json
from datetime import date
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from backend.app.db.repositories.patient_repo import (
    InvalidPatientError,
    archive_patient,
    create_patient,
    get_patient_by_external_id,
    get_patient_by_id,
    list_patients,
    update_patient,
    upsert_patient_by_external_id,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pool(row=None, rows=None):
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row)
    pool.fetch = AsyncMock(return_value=rows or [])
    return pool


def _fake_row(**kwargs):
    defaults = {
        "id": "pat-1",
        "clinic_id": "clinic-1",
        "external_patient_id": None,
        "full_name": "Ada Lovelace",
        "date_of_birth": date(1815, 12, 10),
        "phone": "+43123456789",
        "email": "ada@example.com",
        "preferred_language": "de-AT",
        "status": "active",
        "notes": None,
        "raw_payload": None,
        "created_at": "2024-01-01T00:00:00+00:00",
        "updated_at": "2024-01-01T00:00:00+00:00",
    }
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# 1. create_patient calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_patient_calls_fetchrow():
    pool = _make_pool(row=_fake_row())
    result = await create_patient(pool, clinic_id="clinic-1", full_name="Ada Lovelace")
    pool.fetchrow.assert_awaited_once()
    assert result["full_name"] == "Ada Lovelace"


# ---------------------------------------------------------------------------
# 2. create_patient raises InvalidPatientError for empty clinic_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_patient_empty_clinic_id():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="clinic_id"):
        await create_patient(pool, clinic_id="", full_name="Ada Lovelace")


# ---------------------------------------------------------------------------
# 3. create_patient raises InvalidPatientError for empty full_name
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_patient_empty_full_name():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="full_name"):
        await create_patient(pool, clinic_id="clinic-1", full_name="")


# ---------------------------------------------------------------------------
# 4. create_patient raises InvalidPatientError for empty preferred_language
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_patient_empty_preferred_language():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="preferred_language"):
        await create_patient(
            pool, clinic_id="clinic-1", full_name="Ada Lovelace", preferred_language=""
        )


# ---------------------------------------------------------------------------
# 5. create_patient validates invalid status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_patient_invalid_status():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="status"):
        await create_patient(
            pool, clinic_id="clinic-1", full_name="Ada Lovelace", status="deleted"
        )


# ---------------------------------------------------------------------------
# 6. upsert_patient_by_external_id calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_patient_calls_fetchrow():
    pool = _make_pool(row=_fake_row(external_patient_id="ext-99"))
    result = await upsert_patient_by_external_id(
        pool,
        clinic_id="clinic-1",
        external_patient_id="ext-99",
        full_name="Ada Lovelace",
    )
    pool.fetchrow.assert_awaited_once()
    assert result["external_patient_id"] == "ext-99"


# ---------------------------------------------------------------------------
# 7. upsert_patient_by_external_id requires external_patient_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_patient_empty_external_patient_id():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="external_patient_id"):
        await upsert_patient_by_external_id(
            pool, clinic_id="clinic-1", external_patient_id="", full_name="Ada Lovelace"
        )


# ---------------------------------------------------------------------------
# 8. upsert SQL uses ON CONFLICT
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_sql_uses_on_conflict():
    pool = _make_pool(row=_fake_row())
    await upsert_patient_by_external_id(
        pool,
        clinic_id="clinic-1",
        external_patient_id="ext-1",
        full_name="Ada Lovelace",
    )
    sql_arg = pool.fetchrow.call_args[0][0]
    assert "ON CONFLICT" in sql_arg.upper()
    assert "DO UPDATE" in sql_arg.upper()


# ---------------------------------------------------------------------------
# 9. get_patient_by_id calls fetchrow and filters by clinic_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_patient_by_id_calls_fetchrow_and_filters_clinic():
    pool = _make_pool(row=_fake_row())
    result = await get_patient_by_id(pool, clinic_id="clinic-1", patient_id="pat-1")
    pool.fetchrow.assert_awaited_once()
    sql_arg, *bind_args = pool.fetchrow.call_args[0]
    assert "clinic_id" in sql_arg.lower()
    assert "clinic-1" in bind_args


# ---------------------------------------------------------------------------
# 10. get_patient_by_external_id calls fetchrow and filters by clinic_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_patient_by_external_id_calls_fetchrow_and_filters_clinic():
    pool = _make_pool(row=_fake_row(external_patient_id="ext-1"))
    result = await get_patient_by_external_id(
        pool, clinic_id="clinic-1", external_patient_id="ext-1"
    )
    pool.fetchrow.assert_awaited_once()
    sql_arg, *bind_args = pool.fetchrow.call_args[0]
    assert "clinic_id" in sql_arg.lower()
    assert "clinic-1" in bind_args


# ---------------------------------------------------------------------------
# 11. list_patients calls fetch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_patients_calls_fetch():
    pool = _make_pool(rows=[_fake_row()])
    result = await list_patients(pool, clinic_id="clinic-1")
    pool.fetch.assert_awaited_once()
    assert len(result) == 1


# ---------------------------------------------------------------------------
# 12. list_patients validates limit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_patients_invalid_limit_zero():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="limit"):
        await list_patients(pool, clinic_id="clinic-1", limit=0)


@pytest.mark.asyncio
async def test_list_patients_invalid_limit_over_100():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="limit"):
        await list_patients(pool, clinic_id="clinic-1", limit=101)


# ---------------------------------------------------------------------------
# 13. list_patients validates status filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_patients_invalid_status_filter():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="status"):
        await list_patients(pool, clinic_id="clinic-1", status="deleted")


# ---------------------------------------------------------------------------
# 14. list_patients supports search filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_patients_search_filter_passed_to_query():
    pool = _make_pool(rows=[])
    await list_patients(pool, clinic_id="clinic-1", search="Ada")
    sql_arg, *bind_args = pool.fetch.call_args[0]
    assert "ILIKE" in sql_arg.upper()
    assert "Ada" in bind_args


# ---------------------------------------------------------------------------
# 15. update_patient calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_patient_calls_fetchrow():
    pool = _make_pool(row=_fake_row(full_name="Ada B. Lovelace"))
    result = await update_patient(
        pool, clinic_id="clinic-1", patient_id="pat-1", full_name="Ada B. Lovelace"
    )
    pool.fetchrow.assert_awaited_once()
    assert result["full_name"] == "Ada B. Lovelace"


# ---------------------------------------------------------------------------
# 16. update_patient validates at least one update field
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_patient_no_fields_raises():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="[Aa]t least one"):
        await update_patient(pool, clinic_id="clinic-1", patient_id="pat-1")


# ---------------------------------------------------------------------------
# 17. update_patient validates invalid status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_patient_invalid_status():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="status"):
        await update_patient(
            pool, clinic_id="clinic-1", patient_id="pat-1", status="removed"
        )


# ---------------------------------------------------------------------------
# 18. update_patient validates empty full_name if provided
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_patient_empty_full_name():
    pool = _make_pool()
    with pytest.raises(InvalidPatientError, match="full_name"):
        await update_patient(
            pool, clinic_id="clinic-1", patient_id="pat-1", full_name=""
        )


# ---------------------------------------------------------------------------
# 19. archive_patient calls fetchrow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_archive_patient_calls_fetchrow():
    pool = _make_pool(row=_fake_row(status="archived"))
    result = await archive_patient(pool, clinic_id="clinic-1", patient_id="pat-1")
    pool.fetchrow.assert_awaited_once()
    assert result["status"] == "archived"


# ---------------------------------------------------------------------------
# 20. SQL uses parameterised placeholders, not string formatting
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sql_uses_parameterised_placeholders():
    """Verify $1 placeholders appear and no f-string / %-format markers."""
    pool = _make_pool(row=_fake_row())

    await create_patient(pool, clinic_id="clinic-1", full_name="Ada Lovelace")
    sql = pool.fetchrow.call_args[0][0]
    assert "$1" in sql
    assert "%" not in sql
    assert "{" not in sql
