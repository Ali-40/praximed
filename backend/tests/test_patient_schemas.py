"""
Tests for backend/app/schemas/patients.py — PraxisMed Sprint 2 / Module 26
"""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from backend.app.schemas.patients import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
    PatientUpsertByExternalId,
)

CLINIC_ID = "clinic-uuid-001"


def _create_body(**overrides) -> dict:
    base = {"clinic_id": CLINIC_ID, "full_name": "Ada Lovelace"}
    base.update(overrides)
    return base


def _upsert_body(**overrides) -> dict:
    base = {
        "clinic_id": CLINIC_ID,
        "external_patient_id": "ext-001",
        "full_name": "Ada Lovelace",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. Valid PatientCreate passes
# ---------------------------------------------------------------------------


def test_valid_patient_create_passes():
    model = PatientCreate(**_create_body())
    assert model.clinic_id == CLINIC_ID
    assert model.full_name == "Ada Lovelace"
    assert model.preferred_language == "de-AT"
    assert model.status == "active"


# ---------------------------------------------------------------------------
# 2. Empty clinic_id fails
# ---------------------------------------------------------------------------


def test_empty_clinic_id_fails():
    with pytest.raises(ValidationError, match="clinic_id"):
        PatientCreate(**_create_body(clinic_id=""))


# ---------------------------------------------------------------------------
# 3. Empty full_name fails
# ---------------------------------------------------------------------------


def test_empty_full_name_fails():
    with pytest.raises(ValidationError, match="full_name"):
        PatientCreate(**_create_body(full_name=""))


# ---------------------------------------------------------------------------
# 4. Empty preferred_language fails
# ---------------------------------------------------------------------------


def test_empty_preferred_language_fails():
    with pytest.raises(ValidationError, match="preferred_language"):
        PatientCreate(**_create_body(preferred_language=""))


# ---------------------------------------------------------------------------
# 5. Invalid status fails
# ---------------------------------------------------------------------------


def test_invalid_status_fails():
    with pytest.raises(ValidationError, match="status"):
        PatientCreate(**_create_body(status="deleted"))


# ---------------------------------------------------------------------------
# 6. Valid PatientUpsertByExternalId passes
# ---------------------------------------------------------------------------


def test_valid_patient_upsert_passes():
    model = PatientUpsertByExternalId(**_upsert_body())
    assert model.external_patient_id == "ext-001"
    assert model.status == "active"


# ---------------------------------------------------------------------------
# 7. Empty external_patient_id fails
# ---------------------------------------------------------------------------


def test_empty_external_patient_id_fails():
    with pytest.raises(ValidationError, match="external_patient_id"):
        PatientUpsertByExternalId(**_upsert_body(external_patient_id=""))


# ---------------------------------------------------------------------------
# 8. Valid PatientUpdate passes
# ---------------------------------------------------------------------------


def test_valid_patient_update_passes():
    model = PatientUpdate(full_name="Ada B. Lovelace")
    assert model.full_name == "Ada B. Lovelace"


# ---------------------------------------------------------------------------
# 9. Empty PatientUpdate fails
# ---------------------------------------------------------------------------


def test_empty_patient_update_fails():
    with pytest.raises(ValidationError, match="[Aa]t least one"):
        PatientUpdate()


# ---------------------------------------------------------------------------
# 10. PatientUpdate invalid status fails
# ---------------------------------------------------------------------------


def test_patient_update_invalid_status_fails():
    with pytest.raises(ValidationError, match="status"):
        PatientUpdate(status="removed")


# ---------------------------------------------------------------------------
# 11. PatientResponse accepts patient dict
# ---------------------------------------------------------------------------


def test_patient_response_accepts_dict():
    resp = PatientResponse(ok=True, patient={"id": "pat-1", "status": "active"})
    assert resp.ok is True
    assert resp.patient["id"] == "pat-1"


# ---------------------------------------------------------------------------
# 12. PatientListResponse accepts list of dicts
# ---------------------------------------------------------------------------


def test_patient_list_response_accepts_list():
    resp = PatientListResponse(
        ok=True,
        patients=[{"id": "a"}, {"id": "b"}],
    )
    assert resp.ok is True
    assert len(resp.patients) == 2
