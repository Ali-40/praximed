"""
Patient and Appointment Data Linking Foundation — Sprint 17 / Module 121

Tests for:
  - patient_repo.find_or_create_patient_from_vapi (find, create, tenant isolation)
  - appointment_request_repo.create_appointment_request patient_id parameter
  - vapi_appointment_capture integration: patient created, linked, phone reuse,
    cross-clinic isolation

All tests use AsyncMock; no real database or PHI.
No real patient data. No secrets. Fake data only.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from backend.app.db.repositories.patient_repo import find_or_create_patient_from_vapi
from backend.app.db.repositories.appointment_request_repo import create_appointment_request
from backend.app.modules.vapi.vapi_appointment_capture import capture_vapi_appointment_request

# ---------------------------------------------------------------------------
# Constants — fake data only, no real patients
# ---------------------------------------------------------------------------

CLINIC_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
CLINIC_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
CLINIC_REF = "test-clinic"
CALL_ID = "call-test-001"
PATIENT_NAME = "Test Patient"
PATIENT_PHONE = "+43000000099"

EXISTING_PATIENT = {
    "id":        "11111111-1111-4111-8111-111111111111",
    "clinic_id": CLINIC_A,
    "full_name": PATIENT_NAME,
    "phone":     PATIENT_PHONE,
    "status":    "active",
}

NEW_PATIENT = {
    "id":        "22222222-2222-4222-8222-222222222222",
    "clinic_id": CLINIC_A,
    "full_name": PATIENT_NAME,
    "phone":     PATIENT_PHONE,
    "status":    "active",
}

NEW_PATIENT_NO_PHONE = {
    "id":        "33333333-3333-4333-8333-333333333333",
    "clinic_id": CLINIC_A,
    "full_name": PATIENT_NAME,
    "phone":     None,
    "status":    "active",
}

FAKE_APPT_ROW = {
    "id":              "55555555-5555-4555-8555-555555555555",
    "clinic_id":       CLINIC_A,
    "source":          "vapi",
    "patient_name":    PATIENT_NAME,
    "patient_id":      EXISTING_PATIENT["id"],
    "status":          "new",
    "action_required": True,
}

REPO_PATH = "backend.app.modules.vapi.vapi_appointment_capture.appointment_request_repo"
PATIENT_REPO_PATH = "backend.app.modules.vapi.vapi_appointment_capture.patient_repo"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(clinic_id: str = CLINIC_A) -> MagicMock:
    cfg = MagicMock()
    cfg.tenant_id = clinic_id
    return cfg


def _make_loader(clinic_id: str = CLINIC_A) -> MagicMock:
    loader = MagicMock()
    loader.load = AsyncMock(return_value=_make_config(clinic_id))
    return loader


# ===========================================================================
# 1. find_or_create_patient_from_vapi — returns existing patient on phone match
# ===========================================================================

async def test_find_or_create_returns_existing_when_phone_matches():
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(return_value=EXISTING_PATIENT)

    result = await find_or_create_patient_from_vapi(
        pool=pool,
        clinic_id=CLINIC_A,
        full_name=PATIENT_NAME,
        phone=PATIENT_PHONE,
    )

    assert result["id"] == EXISTING_PATIENT["id"]
    pool.fetchrow.assert_awaited_once()


# ===========================================================================
# 2. find_or_create_patient_from_vapi — creates new patient when no match
# ===========================================================================

async def test_find_or_create_creates_new_patient_when_no_match():
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(side_effect=[None, NEW_PATIENT])

    result = await find_or_create_patient_from_vapi(
        pool=pool,
        clinic_id=CLINIC_A,
        full_name=PATIENT_NAME,
        phone=PATIENT_PHONE,
    )

    assert result["id"] == NEW_PATIENT["id"]
    assert pool.fetchrow.await_count == 2


# ===========================================================================
# 3. find_or_create_patient_from_vapi — creates new patient when no phone
# ===========================================================================

async def test_find_or_create_creates_new_patient_when_no_phone():
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(return_value=NEW_PATIENT_NO_PHONE)

    result = await find_or_create_patient_from_vapi(
        pool=pool,
        clinic_id=CLINIC_A,
        full_name=PATIENT_NAME,
        phone=None,
    )

    assert result["id"] == NEW_PATIENT_NO_PHONE["id"]
    pool.fetchrow.assert_awaited_once()


# ===========================================================================
# 4. find_or_create_patient_from_vapi — skips SELECT when phone is whitespace-only
# ===========================================================================

async def test_find_or_create_whitespace_phone_treated_as_no_phone():
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(return_value=NEW_PATIENT_NO_PHONE)

    result = await find_or_create_patient_from_vapi(
        pool=pool,
        clinic_id=CLINIC_A,
        full_name=PATIENT_NAME,
        phone="   ",
    )

    assert result["id"] == NEW_PATIENT_NO_PHONE["id"]
    pool.fetchrow.assert_awaited_once()


# ===========================================================================
# 5. find_or_create_patient_from_vapi — phone is stripped before lookup
# ===========================================================================

async def test_find_or_create_strips_phone_whitespace():
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(return_value=EXISTING_PATIENT)

    await find_or_create_patient_from_vapi(
        pool=pool,
        clinic_id=CLINIC_A,
        full_name=PATIENT_NAME,
        phone=f"  {PATIENT_PHONE}  ",
    )

    _, args, _ = pool.fetchrow.mock_calls[0]
    assert PATIENT_PHONE in args, "normalized (stripped) phone must be passed to SELECT"


# ===========================================================================
# 6. find_or_create_patient_from_vapi — SELECT is scoped to clinic_id
# ===========================================================================

async def test_find_or_create_select_scoped_to_clinic_id():
    """clinic_id must be passed as first parameter to the SELECT query."""
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(return_value=EXISTING_PATIENT)

    await find_or_create_patient_from_vapi(
        pool=pool,
        clinic_id=CLINIC_A,
        full_name=PATIENT_NAME,
        phone=PATIENT_PHONE,
    )

    _, args, _ = pool.fetchrow.mock_calls[0]
    # args[0] is the SQL string; args[1] is clinic_id (first positional parameter)
    assert args[1] == CLINIC_A, "SELECT must pass clinic_id as first parameter"


# ===========================================================================
# 7. find_or_create_patient_from_vapi — tenant isolation: same phone, diff clinic
# ===========================================================================

async def test_find_or_create_tenant_isolation_different_clinics():
    """Same phone in different clinics resolves via separate SELECT queries
    scoped by their respective clinic_id — cross-linking is impossible."""
    patient_b = {**EXISTING_PATIENT, "id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc", "clinic_id": CLINIC_B}

    pool_a = AsyncMock()
    pool_a.fetchrow = AsyncMock(return_value=EXISTING_PATIENT)

    pool_b = AsyncMock()
    pool_b.fetchrow = AsyncMock(return_value=patient_b)

    result_a = await find_or_create_patient_from_vapi(
        pool=pool_a, clinic_id=CLINIC_A, full_name=PATIENT_NAME, phone=PATIENT_PHONE
    )
    result_b = await find_or_create_patient_from_vapi(
        pool=pool_b, clinic_id=CLINIC_B, full_name=PATIENT_NAME, phone=PATIENT_PHONE
    )

    assert result_a["id"] != result_b["id"]
    assert result_a["clinic_id"] == CLINIC_A
    assert result_b["clinic_id"] == CLINIC_B

    _, args_a, _ = pool_a.fetchrow.mock_calls[0]
    _, args_b, _ = pool_b.fetchrow.mock_calls[0]
    # args[0] is SQL string; args[1] is clinic_id
    assert args_a[1] == CLINIC_A
    assert args_b[1] == CLINIC_B


# ===========================================================================
# 8. create_appointment_request — accepts patient_id parameter
# ===========================================================================

async def test_create_appointment_request_accepts_patient_id():
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(return_value=FAKE_APPT_ROW)

    row = await create_appointment_request(
        pool=pool,
        clinic_id=CLINIC_A,
        source="vapi",
        patient_name=PATIENT_NAME,
        patient_id=EXISTING_PATIENT["id"],
    )

    assert row["patient_id"] == EXISTING_PATIENT["id"]


# ===========================================================================
# 9. create_appointment_request — patient_id defaults to None (backward compat)
# ===========================================================================

async def test_create_appointment_request_patient_id_defaults_to_none():
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(return_value={**FAKE_APPT_ROW, "patient_id": None})

    row = await create_appointment_request(
        pool=pool,
        clinic_id=CLINIC_A,
        source="staff",
        patient_name=PATIENT_NAME,
    )

    assert row["patient_id"] is None


# ===========================================================================
# 10. create_appointment_request — patient_id is included in SQL INSERT
# ===========================================================================

async def test_create_appointment_request_passes_patient_id_to_sql():
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(return_value=FAKE_APPT_ROW)

    await create_appointment_request(
        pool=pool,
        clinic_id=CLINIC_A,
        source="vapi",
        patient_name=PATIENT_NAME,
        patient_id=EXISTING_PATIENT["id"],
    )

    call_args = pool.fetchrow.call_args
    all_args = list(call_args.args) + list(call_args.kwargs.values())
    assert EXISTING_PATIENT["id"] in all_args, (
        "patient_id must be passed to pool.fetchrow in the INSERT"
    )


# ===========================================================================
# 11. Vapi capture — calls find_or_create_patient_from_vapi
# ===========================================================================

async def test_vapi_capture_calls_patient_linking():
    with patch(f"{PATIENT_REPO_PATH}.find_or_create_patient_from_vapi", new=AsyncMock(return_value=EXISTING_PATIENT)) as mock_patient:
        with patch(f"{REPO_PATH}.create_appointment_request", new=AsyncMock(return_value=FAKE_APPT_ROW)):
            await capture_vapi_appointment_request(
                MagicMock(),
                _make_loader(),
                CLINIC_REF,
                CALL_ID,
                PATIENT_NAME,
                caller_phone=PATIENT_PHONE,
            )
    mock_patient.assert_awaited_once()


# ===========================================================================
# 12. Vapi capture — passes patient_id to create_appointment_request
# ===========================================================================

async def test_vapi_capture_passes_patient_id_to_repo():
    with patch(f"{PATIENT_REPO_PATH}.find_or_create_patient_from_vapi", new=AsyncMock(return_value=EXISTING_PATIENT)):
        with patch(f"{REPO_PATH}.create_appointment_request", new=AsyncMock(return_value=FAKE_APPT_ROW)) as mock_create:
            await capture_vapi_appointment_request(
                MagicMock(),
                _make_loader(),
                CLINIC_REF,
                CALL_ID,
                PATIENT_NAME,
                caller_phone=PATIENT_PHONE,
            )
    assert mock_create.call_args.kwargs["patient_id"] == EXISTING_PATIENT["id"]


# ===========================================================================
# 13. Vapi capture — response includes patient_id
# ===========================================================================

async def test_vapi_capture_response_includes_patient_id():
    with patch(f"{PATIENT_REPO_PATH}.find_or_create_patient_from_vapi", new=AsyncMock(return_value=EXISTING_PATIENT)):
        with patch(f"{REPO_PATH}.create_appointment_request", new=AsyncMock(return_value=FAKE_APPT_ROW)):
            result = await capture_vapi_appointment_request(
                MagicMock(),
                _make_loader(),
                CLINIC_REF,
                CALL_ID,
                PATIENT_NAME,
                caller_phone=PATIENT_PHONE,
            )
    assert result["patient_id"] == EXISTING_PATIENT["id"]


# ===========================================================================
# 14. Vapi capture — patient matching scoped to clinic_id (not caller phone alone)
# ===========================================================================

async def test_vapi_capture_patient_matching_passes_clinic_id():
    with patch(
        f"{PATIENT_REPO_PATH}.find_or_create_patient_from_vapi",
        new=AsyncMock(return_value=EXISTING_PATIENT),
    ) as mock_patient:
        with patch(f"{REPO_PATH}.create_appointment_request", new=AsyncMock(return_value=FAKE_APPT_ROW)):
            await capture_vapi_appointment_request(
                MagicMock(),
                _make_loader(CLINIC_A),
                CLINIC_REF,
                CALL_ID,
                PATIENT_NAME,
                caller_phone=PATIENT_PHONE,
            )
    assert mock_patient.call_args.kwargs["clinic_id"] == CLINIC_A


# ===========================================================================
# 15. Vapi capture — second call with same phone reuses existing patient
# ===========================================================================

async def test_vapi_capture_reuses_patient_for_second_call_same_phone():
    """find_or_create is called once per capture call; returning the same patient
    (simulated by mock) means the second request links to the same patient_id."""
    with patch(
        f"{PATIENT_REPO_PATH}.find_or_create_patient_from_vapi",
        new=AsyncMock(return_value=EXISTING_PATIENT),
    ) as mock_patient:
        with patch(f"{REPO_PATH}.create_appointment_request", new=AsyncMock(return_value=FAKE_APPT_ROW)) as mock_create:
            pool = MagicMock()
            loader = _make_loader()

            await capture_vapi_appointment_request(pool, loader, CLINIC_REF, "call-1", PATIENT_NAME, caller_phone=PATIENT_PHONE)
            await capture_vapi_appointment_request(pool, loader, CLINIC_REF, "call-2", PATIENT_NAME, caller_phone=PATIENT_PHONE)

    assert mock_patient.await_count == 2
    for c in mock_create.call_args_list:
        assert c.kwargs["patient_id"] == EXISTING_PATIENT["id"]


# ===========================================================================
# 16. Vapi capture — patient_repo failure does NOT silently swallow the error
# ===========================================================================

async def test_vapi_capture_propagates_patient_repo_error():
    with patch(
        f"{PATIENT_REPO_PATH}.find_or_create_patient_from_vapi",
        new=AsyncMock(side_effect=RuntimeError("patient repo unavailable")),
    ):
        with pytest.raises(RuntimeError, match="patient repo unavailable"):
            await capture_vapi_appointment_request(
                MagicMock(),
                _make_loader(),
                CLINIC_REF,
                CALL_ID,
                PATIENT_NAME,
            )


# ===========================================================================
# 17. No real patient data — verify fake constants
# ===========================================================================

def test_no_real_patient_data_in_fixtures():
    """Safety check: fake constants must not contain real clinic UUIDs or PII."""
    real_staging_clinic = "1a5bbc75-c1b0-4488-94aa-64b3f1c50056"
    assert CLINIC_A != real_staging_clinic
    assert CLINIC_B != real_staging_clinic
    assert "staging" not in PATIENT_NAME.lower()
    assert "praximed.test" not in PATIENT_PHONE
