"""
Tests for Sprint 20 / Module 149 — Patient History Data Model Foundation.

Covers: migration contract (7 FHIR tables), schema SQL, Pydantic schemas,
repository layer, service layer, API routes (auth guards, no-DELETE),
FHIR alignment checks, vocabulary guards, safety invariants.

No real patient PHI. No diagnosis generated. No medical advice. No triage scoring.
Synthetic/fake staging only. production_phi_enabled always False.
Production PHI remains NO-GO.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app
from backend.app.schemas.patient_history import (
    AllergyHistoryCreate,
    MedicationHistoryCreate,
    ConditionHistoryCreate,
    ProcedureHistoryCreate,
    ImmunizationHistoryCreate,
    FamilyHistoryCreate,
    SocialHistoryCreate,
    HistoryStatusUpdate,
)
from backend.app.db.repositories.patient_history_repo import (
    HISTORY_TYPE_TABLE,
    UnsupportedHistoryTypeError,
    InvalidPatientHistoryEntryError,
)

_REPO_ROOT = Path(__file__).parent.parent.parent
_MIGRATION = _REPO_ROOT / "backend/migrations/versions/0007_patient_history_data_model.py"
_SCHEMA_SQL = _REPO_ROOT / "backend/app/db/schema.sql"
_SCHEMA_SRC = _REPO_ROOT / "backend/app/schemas/patient_history.py"
_REPO_SRC = _REPO_ROOT / "backend/app/db/repositories/patient_history_repo.py"
_SERVICE_SRC = _REPO_ROOT / "backend/app/services/patient_history.py"
_ROUTES_SRC = _REPO_ROOT / "backend/app/api/routes/patient_history.py"
_ROUTER_SRC = _REPO_ROOT / "backend/app/api/router.py"
_ARCH_DOC = _REPO_ROOT / "docs/architecture/PATIENT_HISTORY_DATA_MODEL_FOUNDATION.md"

_FAKE_CLINIC_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
_FAKE_PATIENT_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
_FAKE_CONSENT_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
_FAKE_ENTRY_ID = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
_FAKE_VERSION_GROUP = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"

_ALL_TABLES = [
    "patient_history_allergies",
    "patient_history_medications",
    "patient_history_conditions",
    "patient_history_procedures",
    "patient_history_immunizations",
    "patient_history_family_history",
    "patient_history_social_history",
]

_FAKE_ALLERGY_ROW: Dict[str, Any] = {
    "id": _FAKE_ENTRY_ID,
    "clinic_id": _FAKE_CLINIC_ID,
    "patient_id": _FAKE_PATIENT_ID,
    "consent_event_id": _FAKE_CONSENT_ID,
    "appointment_request_id": None,
    "version_group_id": _FAKE_VERSION_GROUP,
    "version_number": 1,
    "supersedes_entry_id": None,
    "correction_reason": None,
    "status": "unverified",
    "source_type": "staff_console",
    "source_ref": None,
    "entered_by_user_id": None,
    "reviewed_by_user_id": None,
    "reviewed_at": None,
    "review_note": None,
    "effective_start_date": None,
    "effective_end_date": None,
    "notes": None,
    "fhir_resource_type": "AllergyIntolerance",
    "fhir_payload": {},
    "metadata": {},
    "production_phi_enabled": False,
    "created_at": "2026-07-08T10:00:00+00:00",
    "updated_at": "2026-07-08T10:00:00+00:00",
    "substance_text": "Penicillin",
    "reaction_text": "Rash",
    "severity": "moderate",
    "clinical_status": None,
    "verification_status": None,
    "category": None,
    "criticality": None,
    "onset_text": None,
}

_FAKE_POOL = MagicMock()


def _admin_auth() -> AuthContext:
    return AuthContext(
        user_id="admin-user-1",
        clinic_id=_FAKE_CLINIC_ID,
        role="admin",
    )


@pytest.fixture()
def client_auth():
    app.dependency_overrides[get_db_pool] = lambda: _FAKE_POOL
    app.dependency_overrides[get_current_user] = _admin_auth
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def client_no_auth():
    app.dependency_overrides[get_db_pool] = lambda: _FAKE_POOL
    app.dependency_overrides.pop(get_current_user, None)
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── Migration contract ───────────────────────────────────────────────────────


def test_migration_file_exists():
    assert _MIGRATION.exists()


def test_migration_revision_id():
    src = _MIGRATION.read_text()
    assert 'revision = "0007_patient_history_data_model"' in src


def test_migration_down_revision():
    src = _MIGRATION.read_text()
    assert 'down_revision = "0006_consent_events"' in src


def test_migration_has_all_seven_tables():
    src = _MIGRATION.read_text()
    for table in _ALL_TABLES:
        assert table in src, f"Table {table!r} missing from migration"


def test_migration_tables_include_clinic_id():
    src = _MIGRATION.read_text()
    assert "clinic_id" in src


def test_migration_tables_include_patient_id():
    src = _MIGRATION.read_text()
    assert "patient_id" in src


def test_migration_tables_include_consent_event_id():
    src = _MIGRATION.read_text()
    assert "consent_event_id" in src


def test_migration_tables_include_appointment_request_id():
    src = _MIGRATION.read_text()
    assert "appointment_request_id" in src


def test_migration_tables_include_version_group_id():
    src = _MIGRATION.read_text()
    assert "version_group_id" in src


def test_migration_tables_include_version_number():
    src = _MIGRATION.read_text()
    assert "version_number" in src


def test_migration_tables_include_supersedes_entry_id():
    src = _MIGRATION.read_text()
    assert "supersedes_entry_id" in src


def test_migration_tables_include_status():
    src = _MIGRATION.read_text()
    assert "status" in src


def test_migration_tables_include_source_type():
    src = _MIGRATION.read_text()
    assert "source_type" in src


def test_migration_tables_include_reviewed_by_user_id():
    src = _MIGRATION.read_text()
    assert "reviewed_by_user_id" in src


def test_migration_tables_include_reviewed_at():
    src = _MIGRATION.read_text()
    assert "reviewed_at" in src


def test_migration_tables_include_fhir_resource_type():
    src = _MIGRATION.read_text()
    assert "fhir_resource_type" in src


def test_migration_tables_include_fhir_payload():
    src = _MIGRATION.read_text()
    assert "fhir_payload" in src


def test_migration_tables_include_metadata():
    src = _MIGRATION.read_text()
    assert "metadata" in src


def test_migration_tables_production_phi_enabled_false():
    src = _MIGRATION.read_text()
    assert "production_phi_enabled" in src
    assert "false" in src.lower()


def test_migration_references_consent_events():
    src = _MIGRATION.read_text()
    assert "consent_events" in src


def test_migration_phi_check_constraint():
    src = _MIGRATION.read_text()
    assert "phi_check" in src


def test_migration_status_check_constraint():
    src = _MIGRATION.read_text()
    assert "status_check" in src


def test_migration_source_type_check_constraint():
    src = _MIGRATION.read_text()
    assert "source_type_check" in src


def test_migration_version_check_constraint():
    src = _MIGRATION.read_text()
    assert "version_check" in src


def test_migration_has_downgrade():
    src = _MIGRATION.read_text()
    assert "def downgrade" in src


# ── FHIR alignment ───────────────────────────────────────────────────────────


def test_fhir_allergies_table_has_substance_text():
    src = _MIGRATION.read_text()
    assert "substance_text" in src


def test_fhir_allergies_resource_type():
    src = _MIGRATION.read_text()
    assert "AllergyIntolerance" in src


def test_fhir_medications_table_has_medication_text():
    src = _MIGRATION.read_text()
    assert "medication_text" in src


def test_fhir_medications_resource_type():
    src = _MIGRATION.read_text()
    assert "MedicationStatement" in src


def test_fhir_conditions_table_has_condition_text():
    src = _MIGRATION.read_text()
    assert "condition_text" in src


def test_fhir_conditions_table_has_patient_reported():
    src = _MIGRATION.read_text()
    assert "patient_reported" in src


def test_fhir_conditions_resource_type():
    src = _MIGRATION.read_text()
    assert "Condition" in src


def test_fhir_procedures_table_has_procedure_text():
    src = _MIGRATION.read_text()
    assert "procedure_text" in src


def test_fhir_procedures_resource_type():
    src = _MIGRATION.read_text()
    assert "Procedure" in src


def test_fhir_immunizations_table_has_vaccine_text():
    src = _MIGRATION.read_text()
    assert "vaccine_text" in src


def test_fhir_immunizations_resource_type():
    src = _MIGRATION.read_text()
    assert "Immunization" in src


def test_fhir_family_history_table_has_relationship_text():
    src = _MIGRATION.read_text()
    assert "relationship_text" in src


def test_fhir_family_history_resource_type():
    src = _MIGRATION.read_text()
    assert "FamilyMemberHistory" in src


def test_fhir_social_history_table_has_observation_category():
    src = _MIGRATION.read_text()
    assert "observation_category" in src


def test_fhir_social_history_resource_type():
    src = _MIGRATION.read_text()
    assert "Observation" in src


# ── schema.sql ───────────────────────────────────────────────────────────────


def test_schema_sql_has_all_seven_tables():
    src = _SCHEMA_SQL.read_text()
    for table in _ALL_TABLES:
        assert table in src, f"Table {table!r} missing from schema.sql"


# ── Pydantic schema validation ───────────────────────────────────────────────


def test_allergy_schema_accepts_valid_entry():
    obj = AllergyHistoryCreate(
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        substance_text="Penicillin",
    )
    assert obj.substance_text == "Penicillin"
    assert obj.status == "unverified"
    assert obj.source_type == "staff_console"


def test_allergy_schema_rejects_empty_substance():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        AllergyHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            substance_text="   ",
        )


def test_allergy_schema_requires_consent_event_id():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        AllergyHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id="  ",
            substance_text="Penicillin",
        )


def test_allergy_schema_requires_patient_id():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        AllergyHistoryCreate(
            patient_id="",
            consent_event_id=_FAKE_CONSENT_ID,
            substance_text="Penicillin",
        )


def test_allergy_schema_rejects_invalid_status():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        AllergyHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            substance_text="Penicillin",
            status="active",
        )


def test_allergy_schema_rejects_invalid_source_type():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        AllergyHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            substance_text="Penicillin",
            source_type="unknown_source",
        )


def test_allergy_schema_rejects_forbidden_metadata():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        AllergyHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            substance_text="Penicillin",
            metadata={"diagnosis_code": "X99"},
        )


def test_allergy_schema_rejects_triage_metadata():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        AllergyHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            substance_text="Penicillin",
            metadata={"triage_score": 3},
        )


def test_allergy_schema_accepts_safe_metadata():
    obj = AllergyHistoryCreate(
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        substance_text="Penicillin",
        metadata={"source_form": "intake_v1"},
    )
    assert obj.metadata["source_form"] == "intake_v1"


def test_allergy_schema_rejects_version_number_zero():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        AllergyHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            substance_text="Penicillin",
            version_number=0,
        )


def test_medication_schema_accepts_valid_entry():
    obj = MedicationHistoryCreate(
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        medication_text="Ibuprofen 400mg",
    )
    assert obj.medication_text == "Ibuprofen 400mg"


def test_medication_schema_rejects_empty_medication_text():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        MedicationHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            medication_text="",
        )


def test_condition_schema_accepts_valid_entry():
    obj = ConditionHistoryCreate(
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        condition_text="Seasonal rhinitis",
        patient_reported=True,
    )
    assert obj.patient_reported is True


def test_condition_schema_rejects_empty_condition_text():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        ConditionHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            condition_text="",
        )


def test_procedure_schema_accepts_valid_entry():
    obj = ProcedureHistoryCreate(
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        procedure_text="Appendectomy 2020",
    )
    assert obj.procedure_text == "Appendectomy 2020"


def test_immunization_schema_accepts_valid_entry():
    obj = ImmunizationHistoryCreate(
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        vaccine_text="Influenza",
    )
    assert obj.vaccine_text == "Influenza"


def test_family_history_schema_accepts_valid_entry():
    obj = FamilyHistoryCreate(
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        relationship_text="Mother",
    )
    assert obj.relationship_text == "Mother"


def test_social_history_schema_accepts_valid_entry():
    obj = SocialHistoryCreate(
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        observation_category="smoking",
        observation_text="Non-smoker",
    )
    assert obj.observation_category == "smoking"


def test_social_history_rejects_empty_category():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        SocialHistoryCreate(
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            observation_category="",
            observation_text="Non-smoker",
        )


def test_status_update_accepts_approved():
    obj = HistoryStatusUpdate(status="approved")
    assert obj.status == "approved"


def test_status_update_accepts_rejected():
    obj = HistoryStatusUpdate(status="rejected")
    assert obj.status == "rejected"


def test_status_update_rejects_unverified():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        HistoryStatusUpdate(status="unverified")


def test_status_update_rejects_unknown():
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        HistoryStatusUpdate(status="active")


# ── Repository layer (unit, mock pool) ──────────────────────────────────────


@pytest.mark.asyncio
async def test_repo_create_allergy_calls_fetchrow():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=dict(_FAKE_ALLERGY_ROW))
    from backend.app.db.repositories.patient_history_repo import create_allergy_history
    result = await create_allergy_history(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        substance_text="Penicillin",
    )
    pool.fetchrow.assert_called_once()
    assert result["substance_text"] == "Penicillin"


@pytest.mark.asyncio
async def test_repo_create_allergy_rejects_empty_substance():
    pool = MagicMock()
    from backend.app.db.repositories.patient_history_repo import create_allergy_history
    with pytest.raises(InvalidPatientHistoryEntryError):
        await create_allergy_history(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            patient_id=_FAKE_PATIENT_ID,
            consent_event_id=_FAKE_CONSENT_ID,
            substance_text="",
        )


@pytest.mark.asyncio
async def test_repo_create_medication_calls_fetchrow():
    pool = MagicMock()
    row = dict(_FAKE_ALLERGY_ROW)
    row["medication_text"] = "Ibuprofen"
    row["fhir_resource_type"] = "MedicationStatement"
    pool.fetchrow = AsyncMock(return_value=row)
    from backend.app.db.repositories.patient_history_repo import create_medication_history
    result = await create_medication_history(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        patient_id=_FAKE_PATIENT_ID,
        consent_event_id=_FAKE_CONSENT_ID,
        medication_text="Ibuprofen",
    )
    pool.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_repo_list_by_type_allergies():
    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=[dict(_FAKE_ALLERGY_ROW)])
    from backend.app.db.repositories.patient_history_repo import list_patient_history_by_type
    rows = await list_patient_history_by_type(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        patient_id=_FAKE_PATIENT_ID,
        history_type="allergies",
    )
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_repo_list_by_type_rejects_invalid():
    pool = MagicMock()
    from backend.app.db.repositories.patient_history_repo import list_patient_history_by_type
    with pytest.raises(UnsupportedHistoryTypeError):
        await list_patient_history_by_type(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            patient_id=_FAKE_PATIENT_ID,
            history_type="unknown_type",
        )


@pytest.mark.asyncio
async def test_repo_get_history_entry_by_id():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=dict(_FAKE_ALLERGY_ROW))
    from backend.app.db.repositories.patient_history_repo import get_history_entry_by_id
    result = await get_history_entry_by_id(pool=pool, history_type="allergies", entry_id=_FAKE_ENTRY_ID)
    assert result["id"] == _FAKE_ENTRY_ID


@pytest.mark.asyncio
async def test_repo_get_history_entry_returns_none_if_missing():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    from backend.app.db.repositories.patient_history_repo import get_history_entry_by_id
    result = await get_history_entry_by_id(pool=pool, history_type="allergies", entry_id=_FAKE_ENTRY_ID)
    assert result is None


@pytest.mark.asyncio
async def test_repo_update_status_to_approved():
    row = dict(_FAKE_ALLERGY_ROW)
    row["status"] = "approved"
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row)
    from backend.app.db.repositories.patient_history_repo import update_history_entry_status
    result = await update_history_entry_status(
        pool=pool,
        history_type="allergies",
        entry_id=_FAKE_ENTRY_ID,
        status="approved",
    )
    assert result["status"] == "approved"


@pytest.mark.asyncio
async def test_repo_update_status_rejects_invalid():
    pool = MagicMock()
    from backend.app.db.repositories.patient_history_repo import update_history_entry_status
    with pytest.raises(InvalidPatientHistoryEntryError):
        await update_history_entry_status(
            pool=pool,
            history_type="allergies",
            entry_id=_FAKE_ENTRY_ID,
            status="invalid_status",
        )


@pytest.mark.asyncio
async def test_repo_timeline_fetches_all_types():
    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=[])
    from backend.app.db.repositories.patient_history_repo import list_patient_history_timeline
    rows = await list_patient_history_timeline(
        pool=pool, clinic_id=_FAKE_CLINIC_ID, patient_id=_FAKE_PATIENT_ID
    )
    assert pool.fetch.call_count == 7  # one call per table


# ── Service layer — consent gate ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_service_create_blocked_when_consent_missing():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value={"id": _FAKE_CLINIC_ID})
    from backend.app.services.patient_history import create_patient_history_entry
    from backend.app.services.consent_ledger import ConsentValidationError

    async def mock_fetchrow(sql, *args):
        if "clinics" in sql:
            return {"id": _FAKE_CLINIC_ID}
        if "patients" in sql:
            return {"id": _FAKE_PATIENT_ID}
        if "consent_events" in sql:
            return None
        return None

    pool.fetchrow = AsyncMock(side_effect=mock_fetchrow)
    with pytest.raises(ConsentValidationError):
        await create_patient_history_entry(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            history_type="allergies",
            payload={
                "patient_id": _FAKE_PATIENT_ID,
                "consent_event_id": _FAKE_CONSENT_ID,
                "substance_text": "Penicillin",
            },
        )


@pytest.mark.asyncio
async def test_service_list_history_verifies_clinic():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    from backend.app.services.patient_history import list_patient_history
    from backend.app.services.consent_ledger import ClinicNotFoundError
    with pytest.raises(ClinicNotFoundError):
        await list_patient_history(
            pool=pool,
            clinic_id=_FAKE_CLINIC_ID,
            patient_id=_FAKE_PATIENT_ID,
            history_type="allergies",
        )


# ── API routes — auth guards ─────────────────────────────────────────────────


def test_post_history_requires_auth(client_no_auth):
    resp = client_no_auth.post(
        f"/clinics/{_FAKE_CLINIC_ID}/patients/{_FAKE_PATIENT_ID}/history/allergies",
        json={"consent_event_id": _FAKE_CONSENT_ID, "substance_text": "Penicillin"},
    )
    assert resp.status_code in (401, 403)


def test_get_timeline_requires_auth(client_no_auth):
    resp = client_no_auth.get(
        f"/clinics/{_FAKE_CLINIC_ID}/patients/{_FAKE_PATIENT_ID}/history"
    )
    assert resp.status_code in (401, 403)


def test_get_history_by_type_requires_auth(client_no_auth):
    resp = client_no_auth.get(
        f"/clinics/{_FAKE_CLINIC_ID}/patients/{_FAKE_PATIENT_ID}/history/allergies"
    )
    assert resp.status_code in (401, 403)


def test_get_history_entry_requires_auth(client_no_auth):
    resp = client_no_auth.get(f"/patient-history/allergies/{_FAKE_ENTRY_ID}")
    assert resp.status_code in (401, 403)


def test_patch_status_requires_auth(client_no_auth):
    resp = client_no_auth.patch(
        f"/patient-history/allergies/{_FAKE_ENTRY_ID}/status",
        json={"status": "approved"},
    )
    assert resp.status_code in (401, 403)


# ── No DELETE route ──────────────────────────────────────────────────────────


def test_no_delete_for_history_entry(client_auth):
    resp = client_auth.delete(f"/patient-history/allergies/{_FAKE_ENTRY_ID}")
    assert resp.status_code == 405


def test_no_delete_for_patient_history_list(client_auth):
    resp = client_auth.delete(
        f"/clinics/{_FAKE_CLINIC_ID}/patients/{_FAKE_PATIENT_ID}/history"
    )
    assert resp.status_code == 405


# ── Invalid history_type rejects cleanly ────────────────────────────────────


def test_invalid_history_type_returns_400(client_auth):
    resp = client_auth.get(
        f"/clinics/{_FAKE_CLINIC_ID}/patients/{_FAKE_PATIENT_ID}/history/diagnoses"
    )
    assert resp.status_code == 400


# ── production_phi_enabled always False ─────────────────────────────────────


def test_routes_always_return_phi_false_on_get_entry(client_auth):
    _FAKE_POOL.fetchrow = AsyncMock(return_value=dict(_FAKE_ALLERGY_ROW))
    resp = client_auth.get(f"/patient-history/allergies/{_FAKE_ENTRY_ID}")
    assert resp.status_code == 200
    assert resp.json().get("production_phi_enabled") is False


def test_routes_always_return_phi_false_on_timeline(client_auth):
    _FAKE_POOL.fetchrow = AsyncMock(return_value={"id": _FAKE_CLINIC_ID})
    _FAKE_POOL.fetch = AsyncMock(return_value=[])
    resp = client_auth.get(
        f"/clinics/{_FAKE_CLINIC_ID}/patients/{_FAKE_PATIENT_ID}/history"
    )
    assert resp.status_code == 200
    assert resp.json().get("production_phi_enabled") is False


# ── Router registration ──────────────────────────────────────────────────────


def test_router_imports_patient_history():
    src = _ROUTER_SRC.read_text()
    assert "patient_history" in src


def test_router_includes_patient_history_router():
    src = _ROUTER_SRC.read_text()
    assert "patient_history.router" in src


# ── HISTORY_TYPE_TABLE mapping ───────────────────────────────────────────────


def test_history_type_table_has_seven_entries():
    assert len(HISTORY_TYPE_TABLE) == 7


def test_history_type_table_maps_allergies():
    assert HISTORY_TYPE_TABLE["allergies"] == "patient_history_allergies"


def test_history_type_table_maps_family_history():
    assert HISTORY_TYPE_TABLE["family-history"] == "patient_history_family_history"


def test_history_type_table_maps_social_history():
    assert HISTORY_TYPE_TABLE["social-history"] == "patient_history_social_history"


# ── Vocabulary guards ────────────────────────────────────────────────────────


def _all_sources() -> str:
    return "\n".join([
        _SCHEMA_SRC.read_text(),
        _REPO_SRC.read_text(),
        _SERVICE_SRC.read_text(),
        _ROUTES_SRC.read_text(),
    ])


def _diagnos_lines_outside_prohibition(src: str) -> list:
    lines = [l for l in src.splitlines() if re.search(r"diagnos", l, re.IGNORECASE)]
    return [l for l in lines if not re.search(r"\bno\s+diagnos", l, re.IGNORECASE)]


def test_no_actual_sk_key_in_source_files():
    src = _all_sources()
    assert not re.search(r"sk-[A-Za-z0-9]{10,}", src)


def test_no_vapi_live_credential_in_source_files():
    src = _all_sources()
    assert not re.search(r"vapi_live_[A-Za-z0-9]{6,}", src)


def test_no_database_url_in_source_files():
    src = _all_sources()
    assert "DATABASE_URL" not in src


def test_no_jwt_secret_in_source_files():
    src = _all_sources()
    assert "JWT_SECRET" not in src


def test_no_automatic_diagnosis_generation_in_service():
    src = _SERVICE_SRC.read_text()
    bad = _diagnos_lines_outside_prohibition(src)
    assert not bad, f"Unexpected diagnosis vocabulary in service: {bad}"


def test_no_medical_advice_in_routes():
    src = _ROUTES_SRC.read_text()
    lines = [l for l in src.splitlines() if "medical advice" in l.lower()]
    bad = [l for l in lines if "no medical advice" not in l.lower()]
    assert not bad


def test_no_treatment_recommendation_in_service():
    src = _SERVICE_SRC.read_text().lower()
    assert "treatment_recommendation" not in src


def test_no_triage_scoring_in_service():
    src = _SERVICE_SRC.read_text().lower()
    assert "triage_score" not in src


def test_routes_no_delete_endpoint():
    src = _ROUTES_SRC.read_text()
    assert not re.search(r"@router\.delete", src)


def test_service_calls_assert_valid_consent():
    src = _SERVICE_SRC.read_text()
    assert "assert_valid_consent_for_history_write" in src


def test_service_production_phi_false_enforced():
    src = _SERVICE_SRC.read_text()
    assert "production_phi_enabled" in src
    assert "False" in src


def test_routes_production_phi_false_enforced():
    src = _ROUTES_SRC.read_text()
    assert "production_phi_enabled=False" in src


# ── Arch doc ─────────────────────────────────────────────────────────────────


def test_arch_doc_exists():
    assert _ARCH_DOC.exists(), f"Architecture doc missing: {_ARCH_DOC}"


def test_arch_doc_mentions_consent_event_id_required():
    src = _ARCH_DOC.read_text()
    assert "consent_event_id" in src


def test_arch_doc_mentions_fhir():
    src = _ARCH_DOC.read_text()
    assert "FHIR" in src


def test_arch_doc_mentions_synthetic_staging():
    src = _ARCH_DOC.read_text().lower()
    assert "synthetic" in src


def test_arch_doc_mentions_no_go():
    src = _ARCH_DOC.read_text()
    assert "NO-GO" in src


def test_arch_doc_mentions_append_only():
    src = _ARCH_DOC.read_text().lower()
    assert "append-only" in src or "append only" in src


def test_arch_doc_mentions_staff_review():
    src = _ARCH_DOC.read_text().lower()
    assert "review" in src


def test_arch_doc_mentions_no_deletion():
    src = _ARCH_DOC.read_text().lower()
    assert "no delete" in src or "no deletion" in src or "no del" in src


def test_arch_doc_mentions_all_seven_fhir_types():
    src = _ARCH_DOC.read_text()
    for fhir_type in ["AllergyIntolerance", "MedicationStatement", "Condition",
                       "Procedure", "Immunization", "FamilyMemberHistory", "Observation"]:
        assert fhir_type in src, f"FHIR type {fhir_type!r} missing from arch doc"
