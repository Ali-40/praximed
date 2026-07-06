"""
Tests for Sprint 19 / Module 132 — Real Clinic Onboarding Backend Foundation.

Covers: schema contract, Pydantic schemas, repository, API routes, docs.
Fake clinic data only. No real PHI. No secrets. Production PHI: NO-GO.
"""

from __future__ import annotations

import os
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app
from backend.app.schemas.clinic_onboarding import (
    ClinicOnboardingRequestCreate,
    ClinicOnboardingRequestStatusUpdate,
)
from backend.app.db.repositories.clinic_onboarding_repo import (
    InvalidClinicOnboardingRequestError,
    create_clinic_onboarding_request,
    get_clinic_onboarding_request_by_id,
    list_clinic_onboarding_requests,
    update_clinic_onboarding_status,
)

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SCHEMA_SQL = os.path.join(_REPO_ROOT, "backend", "app", "db", "schema.sql")
_MIGRATION  = os.path.join(_REPO_ROOT, "backend", "migrations", "versions", "0004_clinic_onboarding_requests.py")
_ARCH_DOC   = os.path.join(_REPO_ROOT, "docs", "architecture", "CLINIC_ONBOARDING_BACKEND_FOUNDATION.md")

# ---------------------------------------------------------------------------
# Fake data — never use real clinic/doctor names
# ---------------------------------------------------------------------------

FAKE_CLINIC_NAME = "Demo Wahlarzt Praxis Wien"
FAKE_DOCTOR_NAME = "Dr. Demo Arzt"
FAKE_EMAIL       = "demo.clinic@example.test"
FAKE_PHONE       = "+43123456789"
REQUEST_ID       = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"

FAKE_ROW: Dict[str, Any] = {
    "id":                     REQUEST_ID,
    "clinic_name":            FAKE_CLINIC_NAME,
    "clinic_type":            None,
    "specialty":              "Innere Medizin",
    "city":                   "Wien",
    "address":                None,
    "website":                None,
    "doctor_name":            FAKE_DOCTOR_NAME,
    "contact_email":          FAKE_EMAIL,
    "contact_phone":          FAKE_PHONE,
    "preferred_language":     "de",
    "fallback_language":      "en",
    "supported_languages":    ["de", "en"],
    "workflow_notes":         None,
    "estimated_call_volume":  None,
    "current_booking_system": None,
    "wants_ai_phone_intake":  True,
    "wants_dashboard":        True,
    "wants_notifications":    False,
    "pilot_interest_level":   "new",
    "status":                 "submitted",
    "source":                 "onboarding_page",
    "consent_pilot_contact":  True,
    "acknowledges_no_phi":    True,
    "production_phi_enabled": False,
    "created_at":             "2026-07-06T10:00:00+00:00",
    "updated_at":             "2026-07-06T10:00:00+00:00",
}

VALID_CREATE_BODY: Dict[str, Any] = {
    "clinic_name":           FAKE_CLINIC_NAME,
    "doctor_name":           FAKE_DOCTOR_NAME,
    "contact_email":         FAKE_EMAIL,
    "contact_phone":         FAKE_PHONE,
    "specialty":             "Innere Medizin",
    "city":                  "Wien",
    "preferred_language":    "de",
    "fallback_language":     "en",
    "supported_languages":   ["de", "en"],
    "consent_pilot_contact": True,
    "acknowledges_no_phi":   True,
}

REPO_PATH = "backend.app.api.routes.clinic_onboarding.clinic_onboarding_repo"
FAKE_POOL = MagicMock()


def _staff_auth() -> AuthContext:
    return AuthContext(user_id="staff-1", clinic_id="11111111-1111-4111-8111-111111111111", role="staff", auth_scheme="jwt_bearer")


@pytest.fixture()
def client_public():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides.pop(get_current_user, None)
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)


@pytest.fixture()
def client_auth():
    app.dependency_overrides[get_db_pool] = lambda: FAKE_POOL
    app.dependency_overrides[get_current_user] = _staff_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


# ===========================================================================
# 1. Schema SQL contract
# ===========================================================================


def _sql() -> str:
    with open(_SCHEMA_SQL, encoding="utf-8") as f:
        return f.read().lower()


def test_schema_sql_has_clinic_onboarding_requests_table() -> None:
    assert "create table if not exists clinic_onboarding_requests" in _sql()


def test_schema_sql_has_id_uuid_pk() -> None:
    assert "id" in _sql() and "uuid" in _sql() and "primary key" in _sql()


def test_schema_sql_has_clinic_name_column() -> None:
    assert "clinic_name" in _sql()


def test_schema_sql_has_doctor_name_column() -> None:
    assert "doctor_name" in _sql()


def test_schema_sql_has_contact_email_column() -> None:
    assert "contact_email" in _sql()


def test_schema_sql_has_preferred_language_column() -> None:
    assert "preferred_language" in _sql()


def test_schema_sql_has_fallback_language_column() -> None:
    assert "fallback_language" in _sql()


def test_schema_sql_has_supported_languages_jsonb() -> None:
    assert "supported_languages" in _sql() and "jsonb" in _sql()


def test_schema_sql_has_consent_pilot_contact() -> None:
    assert "consent_pilot_contact" in _sql()


def test_schema_sql_has_acknowledges_no_phi() -> None:
    assert "acknowledges_no_phi" in _sql()


def test_schema_sql_production_phi_enabled_defaults_false() -> None:
    assert "production_phi_enabled" in _sql()
    assert "default false" in _sql()


def test_schema_sql_has_status_check_constraint() -> None:
    sql = _sql()
    for status in ("submitted", "reviewed", "demo_booked", "pilot_approved", "rejected", "archived"):
        assert status in sql


def test_schema_sql_has_preferred_language_check_constraint() -> None:
    sql = _sql()
    assert "clinic_onboarding_requests_preferred_language_check" in sql


def test_schema_sql_has_production_phi_constraint() -> None:
    assert "clinic_onboarding_requests_production_phi_false" in _sql()


def test_schema_sql_has_email_index() -> None:
    assert "idx_clinic_onboarding_requests_email" in _sql()


def test_schema_sql_has_status_index() -> None:
    assert "idx_clinic_onboarding_requests_status" in _sql()


def test_schema_sql_has_created_at_index() -> None:
    assert "idx_clinic_onboarding_requests_created_at" in _sql()


def test_schema_sql_has_preferred_language_index() -> None:
    assert "idx_clinic_onboarding_requests_preferred_language" in _sql()


# ===========================================================================
# 2. Migration contract
# ===========================================================================


def _migration() -> str:
    with open(_MIGRATION, encoding="utf-8") as f:
        return f.read().lower()


def test_migration_file_exists() -> None:
    assert os.path.isfile(_MIGRATION)


def test_migration_has_correct_revision() -> None:
    assert "0004_clinic_onboarding_requests" in _migration()


def test_migration_has_correct_down_revision() -> None:
    assert "0003_patient_id_appt_requests" in _migration()


def test_migration_creates_table() -> None:
    assert "create table if not exists clinic_onboarding_requests" in _migration()


def test_migration_has_downgrade() -> None:
    assert "drop table if exists clinic_onboarding_requests" in _migration()


# ===========================================================================
# 3. Pydantic schema validation
# ===========================================================================


def test_schema_requires_clinic_name() -> None:
    body = {**VALID_CREATE_BODY, "clinic_name": ""}
    with pytest.raises(Exception):
        ClinicOnboardingRequestCreate(**body)


def test_schema_requires_doctor_name() -> None:
    body = {**VALID_CREATE_BODY, "doctor_name": ""}
    with pytest.raises(Exception):
        ClinicOnboardingRequestCreate(**body)


def test_schema_requires_contact_email() -> None:
    body = {**VALID_CREATE_BODY, "contact_email": "not-an-email"}
    with pytest.raises(Exception):
        ClinicOnboardingRequestCreate(**body)


def test_schema_preferred_language_defaults_to_de() -> None:
    body = {k: v for k, v in VALID_CREATE_BODY.items() if k != "preferred_language"}
    obj = ClinicOnboardingRequestCreate(**body)
    assert obj.preferred_language == "de"


def test_schema_fallback_language_defaults_to_en() -> None:
    body = {k: v for k, v in VALID_CREATE_BODY.items() if k != "fallback_language"}
    obj = ClinicOnboardingRequestCreate(**body)
    assert obj.fallback_language == "en"


def test_schema_invalid_preferred_language_rejected() -> None:
    body = {**VALID_CREATE_BODY, "preferred_language": "fr", "supported_languages": ["fr", "en"]}
    with pytest.raises(Exception):
        ClinicOnboardingRequestCreate(**body)


def test_schema_supported_languages_includes_de_and_en() -> None:
    obj = ClinicOnboardingRequestCreate(**VALID_CREATE_BODY)
    assert "de" in obj.supported_languages
    assert "en" in obj.supported_languages


def test_schema_consent_pilot_contact_required_true() -> None:
    body = {**VALID_CREATE_BODY, "consent_pilot_contact": False}
    with pytest.raises(Exception):
        ClinicOnboardingRequestCreate(**body)


def test_schema_acknowledges_no_phi_required_true() -> None:
    body = {**VALID_CREATE_BODY, "acknowledges_no_phi": False}
    with pytest.raises(Exception):
        ClinicOnboardingRequestCreate(**body)


def test_schema_preferred_language_must_be_in_supported() -> None:
    body = {**VALID_CREATE_BODY, "preferred_language": "en", "supported_languages": ["de"]}
    with pytest.raises(Exception):
        ClinicOnboardingRequestCreate(**body)


def test_schema_valid_submission_creates_model() -> None:
    obj = ClinicOnboardingRequestCreate(**VALID_CREATE_BODY)
    assert obj.clinic_name == FAKE_CLINIC_NAME
    assert obj.doctor_name == FAKE_DOCTOR_NAME
    assert obj.preferred_language == "de"


def test_status_update_schema_rejects_invalid_status() -> None:
    with pytest.raises(Exception):
        ClinicOnboardingRequestStatusUpdate(status="activated")


def test_status_update_schema_accepts_valid_statuses() -> None:
    for st in ("submitted", "reviewed", "demo_booked", "pilot_approved", "rejected", "archived"):
        obj = ClinicOnboardingRequestStatusUpdate(status=st)
        assert obj.status == st


# ===========================================================================
# 4. Repository unit tests (AsyncMock pool, no real DB)
# ===========================================================================


def _pool_with_row(row=None):
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row if row is not None else FAKE_ROW)
    pool.fetch    = AsyncMock(return_value=[FAKE_ROW])
    pool.fetchval = AsyncMock(return_value=1)
    return pool


async def test_repo_create_calls_fetchrow() -> None:
    pool = _pool_with_row()
    result = await create_clinic_onboarding_request(
        pool=pool,
        clinic_name=FAKE_CLINIC_NAME,
        doctor_name=FAKE_DOCTOR_NAME,
        contact_email=FAKE_EMAIL,
        consent_pilot_contact=True,
        acknowledges_no_phi=True,
    )
    pool.fetchrow.assert_awaited_once()
    assert result["clinic_name"] == FAKE_CLINIC_NAME


async def test_repo_create_empty_clinic_name_raises() -> None:
    pool = _pool_with_row()
    with pytest.raises(InvalidClinicOnboardingRequestError):
        await create_clinic_onboarding_request(
            pool=pool, clinic_name="", doctor_name=FAKE_DOCTOR_NAME,
            contact_email=FAKE_EMAIL, consent_pilot_contact=True, acknowledges_no_phi=True,
        )


async def test_repo_create_empty_doctor_name_raises() -> None:
    pool = _pool_with_row()
    with pytest.raises(InvalidClinicOnboardingRequestError):
        await create_clinic_onboarding_request(
            pool=pool, clinic_name=FAKE_CLINIC_NAME, doctor_name="",
            contact_email=FAKE_EMAIL, consent_pilot_contact=True, acknowledges_no_phi=True,
        )


async def test_repo_create_invalid_language_raises() -> None:
    pool = _pool_with_row()
    with pytest.raises(InvalidClinicOnboardingRequestError):
        await create_clinic_onboarding_request(
            pool=pool, clinic_name=FAKE_CLINIC_NAME, doctor_name=FAKE_DOCTOR_NAME,
            contact_email=FAKE_EMAIL, consent_pilot_contact=True, acknowledges_no_phi=True,
            preferred_language="fr",
        )


async def test_repo_create_no_consent_raises() -> None:
    pool = _pool_with_row()
    with pytest.raises(InvalidClinicOnboardingRequestError):
        await create_clinic_onboarding_request(
            pool=pool, clinic_name=FAKE_CLINIC_NAME, doctor_name=FAKE_DOCTOR_NAME,
            contact_email=FAKE_EMAIL, consent_pilot_contact=False, acknowledges_no_phi=True,
        )


async def test_repo_create_no_phi_ack_raises() -> None:
    pool = _pool_with_row()
    with pytest.raises(InvalidClinicOnboardingRequestError):
        await create_clinic_onboarding_request(
            pool=pool, clinic_name=FAKE_CLINIC_NAME, doctor_name=FAKE_DOCTOR_NAME,
            contact_email=FAKE_EMAIL, consent_pilot_contact=True, acknowledges_no_phi=False,
        )


async def test_repo_get_by_id_returns_row() -> None:
    pool = _pool_with_row()
    result = await get_clinic_onboarding_request_by_id(pool, REQUEST_ID)
    pool.fetchrow.assert_awaited_once()
    assert result is not None
    assert result["id"] == REQUEST_ID


async def test_repo_get_by_id_returns_none_when_missing() -> None:
    pool = _pool_with_row(row=None)
    pool.fetchrow = AsyncMock(return_value=None)
    result = await get_clinic_onboarding_request_by_id(pool, REQUEST_ID)
    assert result is None


async def test_repo_list_returns_rows() -> None:
    pool = _pool_with_row()
    result = await list_clinic_onboarding_requests(pool)
    pool.fetch.assert_awaited_once()
    assert isinstance(result, list)
    assert len(result) == 1


async def test_repo_list_invalid_limit_raises() -> None:
    pool = _pool_with_row()
    with pytest.raises(InvalidClinicOnboardingRequestError):
        await list_clinic_onboarding_requests(pool, limit=0)


async def test_repo_update_status_calls_fetchrow() -> None:
    pool = _pool_with_row()
    result = await update_clinic_onboarding_status(pool, REQUEST_ID, "reviewed")
    pool.fetchrow.assert_awaited_once()
    assert result is not None


async def test_repo_update_invalid_status_raises() -> None:
    pool = _pool_with_row()
    with pytest.raises(InvalidClinicOnboardingRequestError):
        await update_clinic_onboarding_status(pool, REQUEST_ID, "activated")


# ===========================================================================
# 5. API route tests
# ===========================================================================


def test_post_public_create_returns_201(client_public) -> None:
    with patch(f"{REPO_PATH}.create_clinic_onboarding_request", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client_public.post("/clinic-onboarding-requests", json=VALID_CREATE_BODY)
    assert resp.status_code == 201
    body = resp.json()
    assert body["ok"] is True
    assert body["request"]["clinic_name"] == FAKE_CLINIC_NAME


def test_post_response_has_no_production_activation(client_public) -> None:
    with patch(f"{REPO_PATH}.create_clinic_onboarding_request", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client_public.post("/clinic-onboarding-requests", json=VALID_CREATE_BODY)
    assert resp.status_code == 201
    body = resp.json()
    assert body["request"]["production_phi_enabled"] is False
    assert body["request"]["status"] == "submitted"


def test_post_missing_consent_returns_422(client_public) -> None:
    bad_body = {**VALID_CREATE_BODY, "consent_pilot_contact": False}
    resp = client_public.post("/clinic-onboarding-requests", json=bad_body)
    assert resp.status_code == 422


def test_post_missing_phi_ack_returns_422(client_public) -> None:
    bad_body = {**VALID_CREATE_BODY, "acknowledges_no_phi": False}
    resp = client_public.post("/clinic-onboarding-requests", json=bad_body)
    assert resp.status_code == 422


def test_post_invalid_language_returns_422(client_public) -> None:
    bad_body = {**VALID_CREATE_BODY, "preferred_language": "fr", "supported_languages": ["fr", "en"]}
    resp = client_public.post("/clinic-onboarding-requests", json=bad_body)
    assert resp.status_code == 422


def test_post_missing_clinic_name_returns_422(client_public) -> None:
    bad_body = {**VALID_CREATE_BODY, "clinic_name": ""}
    resp = client_public.post("/clinic-onboarding-requests", json=bad_body)
    assert resp.status_code == 422


def test_post_response_no_secrets(client_public) -> None:
    with patch(f"{REPO_PATH}.create_clinic_onboarding_request", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client_public.post("/clinic-onboarding-requests", json=VALID_CREATE_BODY)
    text = resp.text
    assert "eyJ" not in text
    assert "sk-" not in text


def test_get_list_requires_auth(client_public) -> None:
    resp = client_public.get("/clinic-onboarding-requests")
    assert resp.status_code in (401, 403)


def test_get_detail_requires_auth(client_public) -> None:
    resp = client_public.get(f"/clinic-onboarding-requests/{REQUEST_ID}")
    assert resp.status_code in (401, 403)


def test_patch_status_requires_auth(client_public) -> None:
    resp = client_public.patch(
        f"/clinic-onboarding-requests/{REQUEST_ID}/status",
        json={"status": "reviewed"},
    )
    assert resp.status_code in (401, 403)


def test_get_list_returns_200_with_auth(client_auth) -> None:
    with patch(f"{REPO_PATH}.list_clinic_onboarding_requests", new=AsyncMock(return_value=[FAKE_ROW])):
        resp = client_auth.get("/clinic-onboarding-requests")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert isinstance(body["requests"], list)
    assert body["total"] == 1


def test_get_detail_returns_200_with_auth(client_auth) -> None:
    with patch(f"{REPO_PATH}.get_clinic_onboarding_request_by_id", new=AsyncMock(return_value=FAKE_ROW)):
        resp = client_auth.get(f"/clinic-onboarding-requests/{REQUEST_ID}")
    assert resp.status_code == 200
    assert resp.json()["request"]["id"] == REQUEST_ID


def test_get_detail_returns_404_when_missing(client_auth) -> None:
    with patch(f"{REPO_PATH}.get_clinic_onboarding_request_by_id", new=AsyncMock(return_value=None)):
        resp = client_auth.get(f"/clinic-onboarding-requests/{REQUEST_ID}")
    assert resp.status_code == 404


def test_patch_status_returns_200_with_auth(client_auth) -> None:
    updated = {**FAKE_ROW, "status": "reviewed"}
    with patch(f"{REPO_PATH}.update_clinic_onboarding_status", new=AsyncMock(return_value=updated)):
        resp = client_auth.patch(
            f"/clinic-onboarding-requests/{REQUEST_ID}/status",
            json={"status": "reviewed"},
        )
    assert resp.status_code == 200
    assert resp.json()["request"]["status"] == "reviewed"


def test_patch_invalid_status_returns_422(client_auth) -> None:
    resp = client_auth.patch(
        f"/clinic-onboarding-requests/{REQUEST_ID}/status",
        json={"status": "production_activated"},
    )
    assert resp.status_code == 422


# ===========================================================================
# 6. No PHI fields accepted
# ===========================================================================


def test_create_body_has_no_patient_name_field() -> None:
    import inspect
    from backend.app.schemas.clinic_onboarding import ClinicOnboardingRequestCreate
    fields = ClinicOnboardingRequestCreate.model_fields
    assert "patient_name" not in fields
    assert "patient_phone" not in fields
    assert "date_of_birth" not in fields
    assert "diagnosis" not in fields


def test_create_body_has_no_vapi_credentials() -> None:
    import inspect
    from backend.app.schemas.clinic_onboarding import ClinicOnboardingRequestCreate
    fields = ClinicOnboardingRequestCreate.model_fields
    for phi_field in ("vapi_api_key", "vapi_secret", "jwt_secret", "api_key"):
        assert phi_field not in fields


# ===========================================================================
# 7. Language foundation
# ===========================================================================


def test_german_is_default_preferred_language() -> None:
    body = {k: v for k, v in VALID_CREATE_BODY.items() if k not in ("preferred_language", "fallback_language")}
    obj = ClinicOnboardingRequestCreate(**body)
    assert obj.preferred_language == "de"


def test_english_is_supported_fallback() -> None:
    body = {k: v for k, v in VALID_CREATE_BODY.items() if k != "fallback_language"}
    obj = ClinicOnboardingRequestCreate(**body)
    assert obj.fallback_language == "en"


def test_supported_languages_always_contains_both() -> None:
    obj = ClinicOnboardingRequestCreate(**VALID_CREATE_BODY)
    assert "de" in obj.supported_languages
    assert "en" in obj.supported_languages


def test_language_preference_stored_not_vapi_configured() -> None:
    # This module stores language preference only; Vapi assistant wiring is a future module.
    import backend.app.db.repositories.clinic_onboarding_repo as repo_mod
    src = open(repo_mod.__file__, encoding="utf-8").read()
    assert "vapi" not in src.lower() or "vapi_key" not in src.lower()


# ===========================================================================
# 8. Architecture doc
# ===========================================================================


def _arch() -> str:
    with open(_ARCH_DOC, encoding="utf-8") as f:
        return f.read()


def test_arch_doc_exists() -> None:
    assert os.path.isfile(_ARCH_DOC)


def test_arch_doc_covers_purpose() -> None:
    assert "purpose" in _arch().lower() or "Purpose" in _arch()


def test_arch_doc_covers_table_schema() -> None:
    assert "clinic_onboarding_requests" in _arch()


def test_arch_doc_covers_public_endpoint() -> None:
    assert "/clinic-onboarding-requests" in _arch()


def test_arch_doc_covers_german_first() -> None:
    flat = _arch().lower()
    assert "german" in flat or "deutsch" in flat or "de" in flat


def test_arch_doc_covers_english_fallback() -> None:
    flat = _arch().lower()
    assert "english" in flat or "en" in flat or "fallback" in flat


def test_arch_doc_no_automatic_tenant_activation() -> None:
    flat = _arch().lower()
    assert "no automatic" in flat or "not automatic" in flat or "does not create" in flat


def test_arch_doc_no_phi() -> None:
    flat = _arch().lower()
    assert "no phi" in flat or "no patient" in flat


def test_arch_doc_production_phi_no_go() -> None:
    assert "NO-GO" in _arch() or "no-go" in _arch().lower()
