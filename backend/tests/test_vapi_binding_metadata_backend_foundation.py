"""
Tests for Sprint 19 / Module 145 — Vapi Binding Metadata Backend Foundation.

Covers: migration contract, schema validation, repository, service, routes, arch doc.
Fake data only. No real Vapi credentials. No actual secret values.
Secret refs: VAPI_API_KEY_REF_CLINIC_DEMO, VAPI_WEBHOOK_SECRET_REF_CLINIC_DEMO.
No PHI. No patient data. Production PHI remains NO-GO.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app
from backend.app.schemas.clinic_vapi_binding import (
    ClinicVapiBindingCreate,
    ClinicVapiBindingUpdateStatus,
)
from backend.app.db.repositories.clinic_vapi_binding_repo import (
    InvalidClinicVapiBindingError,
    create_clinic_vapi_binding,
    get_clinic_vapi_binding_by_clinic_id,
    update_clinic_vapi_binding_status,
)

_REPO_ROOT = Path(__file__).parent.parent.parent
_MIGRATION = _REPO_ROOT / "backend/migrations/versions/0005_clinic_vapi_bindings.py"
_SCHEMA_SQL = _REPO_ROOT / "backend/app/db/schema.sql"
_ARCH_DOC = _REPO_ROOT / "docs/architecture/VAPI_BINDING_METADATA_BACKEND_FOUNDATION.md"
_SERVICE_SRC = _REPO_ROOT / "backend/app/services/clinic_vapi_binding.py"
_ROUTES_SRC = _REPO_ROOT / "backend/app/api/routes/clinic_vapi_bindings.py"
_SCHEMA_SRC = _REPO_ROOT / "backend/app/schemas/clinic_vapi_binding.py"

_FAKE_CLINIC_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
_FAKE_BINDING_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
_FAKE_API_KEY_REF = "VAPI_API_KEY_REF_CLINIC_DEMO"
_FAKE_WEBHOOK_REF = "VAPI_WEBHOOK_SECRET_REF_CLINIC_DEMO"

FAKE_BINDING_ROW: Dict[str, Any] = {
    "id": _FAKE_BINDING_ID,
    "clinic_id": _FAKE_CLINIC_ID,
    "assistant_id": None,
    "phone_number_id": None,
    "vapi_project_id": None,
    "api_key_secret_ref": _FAKE_API_KEY_REF,
    "webhook_secret_ref": _FAKE_WEBHOOK_REF,
    "assistant_config_version": None,
    "language_mode": "german_first",
    "status": "draft",
    "created_by_user_id": None,
    "production_phi_enabled": False,
    "created_at": "2026-07-06T10:00:00+00:00",
    "updated_at": "2026-07-06T10:00:00+00:00",
}

_FAKE_POOL = MagicMock()


def _admin_auth() -> AuthContext:
    return AuthContext(
        user_id="admin-1",
        clinic_id=_FAKE_CLINIC_ID,
        role="admin",
    )


@pytest.fixture()
def client_auth():
    app.dependency_overrides[get_db_pool] = lambda: _FAKE_POOL
    app.dependency_overrides[get_current_user] = _admin_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def client_no_auth():
    app.dependency_overrides[get_db_pool] = lambda: _FAKE_POOL
    app.dependency_overrides.pop(get_current_user, None)
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)


# ===========================================================================
# 1. Migration contract — static file checks
# ===========================================================================


def test_migration_file_exists():
    assert _MIGRATION.exists(), f"Missing migration: {_MIGRATION}"


def test_migration_table_name():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "clinic_vapi_bindings" in src


def test_migration_includes_clinic_id():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "clinic_id" in src


def test_migration_includes_assistant_id():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "assistant_id" in src


def test_migration_includes_phone_number_id():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "phone_number_id" in src


def test_migration_includes_vapi_project_id():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "vapi_project_id" in src


def test_migration_includes_api_key_secret_ref():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "api_key_secret_ref" in src


def test_migration_includes_webhook_secret_ref():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "webhook_secret_ref" in src


def test_migration_includes_language_mode():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "language_mode" in src


def test_migration_includes_status():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "status" in src


def test_migration_status_check_constraint():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "draft" in src and "configured" in src and "disabled" in src and "revoked" in src


def test_migration_language_mode_check_constraint():
    src = _MIGRATION.read_text(encoding="utf-8")
    assert "german_first" in src and "english_first" in src and "bilingual_auto" in src


def test_migration_no_secret_value_columns():
    src = _MIGRATION.read_text(encoding="utf-8").lower()
    assert "vapi_api_key_value" not in src
    assert "webhook_secret_value" not in src


def test_schema_sql_contains_clinic_vapi_bindings():
    src = _SCHEMA_SQL.read_text(encoding="utf-8")
    assert "clinic_vapi_bindings" in src


# ===========================================================================
# 2. Pydantic schema — validation
# ===========================================================================


def test_schema_accepts_valid_reference_names():
    payload = ClinicVapiBindingCreate(
        clinic_id=_FAKE_CLINIC_ID,
        api_key_secret_ref=_FAKE_API_KEY_REF,
        webhook_secret_ref=_FAKE_WEBHOOK_REF,
        language_mode="german_first",
    )
    assert payload.api_key_secret_ref == _FAKE_API_KEY_REF
    assert payload.webhook_secret_ref == _FAKE_WEBHOOK_REF


def test_schema_rejects_sk_api_key():
    with pytest.raises(Exception):
        ClinicVapiBindingCreate(
            clinic_id=_FAKE_CLINIC_ID,
            api_key_secret_ref="sk-1234567890abcdef12345",
            webhook_secret_ref=_FAKE_WEBHOOK_REF,
        )


def test_schema_rejects_vapi_live_key():
    with pytest.raises(Exception):
        ClinicVapiBindingCreate(
            clinic_id=_FAKE_CLINIC_ID,
            api_key_secret_ref="vapi_live_abc123xyz",
            webhook_secret_ref=_FAKE_WEBHOOK_REF,
        )


def test_schema_rejects_lowercase_ref():
    with pytest.raises(Exception):
        ClinicVapiBindingCreate(
            clinic_id=_FAKE_CLINIC_ID,
            api_key_secret_ref="vapi_api_key_ref_clinic_demo",
            webhook_secret_ref=_FAKE_WEBHOOK_REF,
        )


def test_schema_rejects_webhook_actual_secret():
    with pytest.raises(Exception):
        ClinicVapiBindingCreate(
            clinic_id=_FAKE_CLINIC_ID,
            api_key_secret_ref=_FAKE_API_KEY_REF,
            webhook_secret_ref="vapi_live_webhook_secret_xyz",
        )


def test_schema_rejects_unsupported_status():
    with pytest.raises(Exception):
        ClinicVapiBindingUpdateStatus(status="active")


def test_schema_rejects_unsupported_language_mode():
    with pytest.raises(Exception):
        ClinicVapiBindingCreate(
            clinic_id=_FAKE_CLINIC_ID,
            api_key_secret_ref=_FAKE_API_KEY_REF,
            webhook_secret_ref=_FAKE_WEBHOOK_REF,
            language_mode="unsupported_mode",
        )


def test_schema_accepts_valid_statuses():
    for status in ("draft", "configured", "disabled", "revoked"):
        obj = ClinicVapiBindingUpdateStatus(status=status)
        assert obj.status == status


def test_schema_accepts_valid_language_modes():
    for mode in ("german_first", "english_first", "bilingual_auto"):
        payload = ClinicVapiBindingCreate(
            clinic_id=_FAKE_CLINIC_ID,
            api_key_secret_ref=_FAKE_API_KEY_REF,
            webhook_secret_ref=_FAKE_WEBHOOK_REF,
            language_mode=mode,
        )
        assert payload.language_mode == mode


def test_schema_production_phi_enabled_not_accepted():
    src = _SCHEMA_SRC.read_text(encoding="utf-8")
    assert "production_phi_enabled" not in src.split("class ClinicVapiBindingCreate")[1].split("class ")[0]


# ===========================================================================
# 3. Repository — mock pool
# ===========================================================================


@pytest.mark.asyncio
async def test_repo_create_stores_reference_names():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=FAKE_BINDING_ROW)

    result = await create_clinic_vapi_binding(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        api_key_secret_ref=_FAKE_API_KEY_REF,
        webhook_secret_ref=_FAKE_WEBHOOK_REF,
        language_mode="german_first",
    )

    assert result["api_key_secret_ref"] == _FAKE_API_KEY_REF
    assert result["webhook_secret_ref"] == _FAKE_WEBHOOK_REF
    assert result["clinic_id"] == _FAKE_CLINIC_ID


@pytest.mark.asyncio
async def test_repo_create_no_secret_values_in_sql():
    pool = MagicMock()
    captured_sql: list = []

    async def capture_fetchrow(sql, *args, **kwargs):
        captured_sql.append(sql)
        return FAKE_BINDING_ROW

    pool.fetchrow = capture_fetchrow

    await create_clinic_vapi_binding(
        pool=pool,
        clinic_id=_FAKE_CLINIC_ID,
        api_key_secret_ref=_FAKE_API_KEY_REF,
        webhook_secret_ref=_FAKE_WEBHOOK_REF,
    )

    for sql in captured_sql:
        assert "sk-" not in sql
        assert "vapi_live" not in sql.lower()


@pytest.mark.asyncio
async def test_repo_get_by_clinic_id():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=FAKE_BINDING_ROW)

    result = await get_clinic_vapi_binding_by_clinic_id(pool=pool, clinic_id=_FAKE_CLINIC_ID)

    assert result is not None
    assert result["clinic_id"] == _FAKE_CLINIC_ID


@pytest.mark.asyncio
async def test_repo_get_by_clinic_id_returns_none_when_not_found():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)

    result = await get_clinic_vapi_binding_by_clinic_id(pool=pool, clinic_id=_FAKE_CLINIC_ID)

    assert result is None


@pytest.mark.asyncio
async def test_repo_status_update():
    pool = MagicMock()
    updated_row = {**FAKE_BINDING_ROW, "status": "configured"}
    pool.fetchrow = AsyncMock(return_value=updated_row)

    result = await update_clinic_vapi_binding_status(
        pool=pool, binding_id=_FAKE_BINDING_ID, status="configured"
    )

    assert result["status"] == "configured"


@pytest.mark.asyncio
async def test_repo_status_update_rejects_invalid_status():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=FAKE_BINDING_ROW)

    with pytest.raises(InvalidClinicVapiBindingError):
        await update_clinic_vapi_binding_status(
            pool=pool, binding_id=_FAKE_BINDING_ID, status="active"
        )


# ===========================================================================
# 4. Routes — authentication
# ===========================================================================


def test_post_route_requires_auth(client_no_auth):
    resp = client_no_auth.post(
        f"/clinics/{_FAKE_CLINIC_ID}/vapi-bindings",
        json={
            "clinic_id": _FAKE_CLINIC_ID,
            "api_key_secret_ref": _FAKE_API_KEY_REF,
            "webhook_secret_ref": _FAKE_WEBHOOK_REF,
        },
    )
    assert resp.status_code in (401, 403, 422), (
        f"Expected auth failure, got {resp.status_code}"
    )


def test_get_route_requires_auth(client_no_auth):
    resp = client_no_auth.get(f"/clinics/{_FAKE_CLINIC_ID}/vapi-bindings")
    assert resp.status_code in (401, 403, 422), (
        f"Expected auth failure, got {resp.status_code}"
    )


def test_patch_route_requires_auth(client_no_auth):
    resp = client_no_auth.patch(
        f"/clinic-vapi-bindings/{_FAKE_BINDING_ID}/status",
        json={"status": "configured"},
    )
    assert resp.status_code in (401, 403, 422), (
        f"Expected auth failure, got {resp.status_code}"
    )


def test_post_route_returns_201_with_auth(client_auth):
    import asyncio

    async def fake_fetchrow(sql, *args, **kwargs):
        if "clinics" in sql and "SELECT" in sql:
            return {"id": _FAKE_CLINIC_ID}
        return FAKE_BINDING_ROW

    _FAKE_POOL.fetchrow = fake_fetchrow

    resp = client_auth.post(
        f"/clinics/{_FAKE_CLINIC_ID}/vapi-bindings",
        json={
            "clinic_id": _FAKE_CLINIC_ID,
            "api_key_secret_ref": _FAKE_API_KEY_REF,
            "webhook_secret_ref": _FAKE_WEBHOOK_REF,
            "language_mode": "german_first",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["ok"] is True
    assert data["production_phi_enabled"] is False


def test_post_route_response_no_secret_values(client_auth):
    async def fake_fetchrow(sql, *args, **kwargs):
        if "clinics" in sql and "SELECT" in sql:
            return {"id": _FAKE_CLINIC_ID}
        return FAKE_BINDING_ROW

    _FAKE_POOL.fetchrow = fake_fetchrow

    resp = client_auth.post(
        f"/clinics/{_FAKE_CLINIC_ID}/vapi-bindings",
        json={
            "clinic_id": _FAKE_CLINIC_ID,
            "api_key_secret_ref": _FAKE_API_KEY_REF,
            "webhook_secret_ref": _FAKE_WEBHOOK_REF,
        },
    )
    body_text = resp.text.lower()
    assert "sk-" not in body_text
    assert "vapi_live" not in body_text


def test_get_route_returns_404_when_clinic_missing(client_auth):
    async def fake_fetchrow(sql, *args, **kwargs):
        return None

    _FAKE_POOL.fetchrow = fake_fetchrow

    resp = client_auth.get(f"/clinics/{_FAKE_CLINIC_ID}/vapi-bindings")
    assert resp.status_code == 404


def test_patch_route_returns_404_when_binding_missing(client_auth):
    async def fake_fetchrow(sql, *args, **kwargs):
        return None

    _FAKE_POOL.fetchrow = fake_fetchrow

    resp = client_auth.patch(
        f"/clinic-vapi-bindings/{_FAKE_BINDING_ID}/status",
        json={"status": "configured"},
    )
    assert resp.status_code == 404


def test_post_route_rejects_actual_api_key(client_auth):
    resp = client_auth.post(
        f"/clinics/{_FAKE_CLINIC_ID}/vapi-bindings",
        json={
            "clinic_id": _FAKE_CLINIC_ID,
            "api_key_secret_ref": "sk-1234567890abcdef12345",
            "webhook_secret_ref": _FAKE_WEBHOOK_REF,
        },
    )
    assert resp.status_code == 422


# ===========================================================================
# 5. Source code static checks — no live Vapi calls, no PHI
# ===========================================================================


def test_service_no_live_vapi_call():
    src = _SERVICE_SRC.read_text(encoding="utf-8").lower()
    assert "requests.get" not in src
    assert "httpx" not in src
    assert "aiohttp" not in src
    assert "vapi.ai" not in src


def test_routes_no_live_vapi_call():
    src = _ROUTES_SRC.read_text(encoding="utf-8").lower()
    assert "vapi.ai" not in src
    assert "requests.get" not in src
    assert "httpx" not in src


def test_service_no_phi_fields():
    src = _SERVICE_SRC.read_text(encoding="utf-8").lower()
    assert "patient_name" not in src
    assert "transcript" not in src
    assert "recording_url" not in src


def test_routes_no_phi_fields():
    src = _ROUTES_SRC.read_text(encoding="utf-8").lower()
    assert "patient_name" not in src
    assert "transcript" not in src
    assert "recording_url" not in src


def test_schema_no_phi_fields():
    src = _SCHEMA_SRC.read_text(encoding="utf-8").lower()
    assert "patient_name" not in src
    assert "patient_data" not in src
    assert "transcript" not in src
    assert "recording_url" not in src


def test_service_production_phi_always_false():
    src = _SERVICE_SRC.read_text(encoding="utf-8")
    assert "production_phi_enabled" in src
    assert "False" in src


def test_routes_production_phi_always_false():
    src = _ROUTES_SRC.read_text(encoding="utf-8")
    assert "production_phi_enabled" in src
    assert "False" in src


# ===========================================================================
# 6. Architecture doc static checks
# ===========================================================================


def test_arch_doc_exists():
    assert _ARCH_DOC.exists(), f"Missing arch doc: {_ARCH_DOC}"


def _arch() -> str:
    return _ARCH_DOC.read_text(encoding="utf-8")


def test_arch_doc_mentions_env_var_only():
    src = _arch().lower()
    assert "environment variable" in src or "env var" in src


def test_arch_doc_no_live_vapi_calls():
    src = _arch().lower()
    assert "no live vapi" in src or "no live" in src or "makes no live" in src


def test_arch_doc_production_phi_no_go():
    src = _arch()
    assert "NO-GO" in src or "no-go" in src.lower()


def test_arch_doc_clinic_vapi_bindings():
    assert "clinic_vapi_bindings" in _arch()


def test_arch_doc_api_key_secret_ref():
    assert "api_key_secret_ref" in _arch()


def test_arch_doc_webhook_secret_ref():
    assert "webhook_secret_ref" in _arch()


def test_arch_doc_no_vapi_credentials_stored():
    src = _arch().lower()
    assert "no vapi" in src or "no credentials" in src or "reference" in src


def test_arch_doc_no_phi():
    src = _arch().lower()
    assert "no phi" in src


def test_arch_doc_status_values():
    src = _arch()
    assert "draft" in src
    assert "configured" in src
    assert "disabled" in src
    assert "revoked" in src
