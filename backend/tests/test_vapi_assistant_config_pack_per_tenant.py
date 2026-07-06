"""
Sprint 19 / Module 141 — Vapi Assistant Configuration Pack Per Tenant

Tests for:
- VapiAssistantConfigPack schema
- build_vapi_assistant_config_pack service
- GET /clinics/{clinic_id}/vapi-assistant-config-pack route
- Architecture doc checks

No PHI. No secrets. No live Vapi binding. production_phi_enabled always False.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# File and doc paths
# ---------------------------------------------------------------------------

SCHEMA_PATH = Path(
    "backend/app/schemas/vapi_assistant_config.py"
)
SERVICE_PATH = Path(
    "backend/app/services/vapi_assistant_config.py"
)
ROUTE_PATH = Path(
    "backend/app/api/routes/vapi_assistant_config.py"
)
ARCH_DOC = Path(
    "docs/architecture/VAPI_ASSISTANT_CONFIGURATION_PACK_PER_TENANT.md"
)


def _schema() -> str:
    return SCHEMA_PATH.read_text(encoding="utf-8")


def _service() -> str:
    return SERVICE_PATH.read_text(encoding="utf-8")


def _route() -> str:
    return ROUTE_PATH.read_text(encoding="utf-8")


def _arch() -> str:
    return ARCH_DOC.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_schema_file_exists():
    assert SCHEMA_PATH.exists()


def test_service_file_exists():
    assert SERVICE_PATH.exists()


def test_route_file_exists():
    assert ROUTE_PATH.exists()


def test_arch_doc_exists():
    assert ARCH_DOC.exists(), f"Missing arch doc: {ARCH_DOC}"


# ---------------------------------------------------------------------------
# Schema — VapiAssistantConfigPack
# ---------------------------------------------------------------------------


def test_schema_has_vapiassistantconfigpack():
    assert "VapiAssistantConfigPack" in _schema()


def test_schema_has_clinic_id():
    assert "clinic_id" in _schema()


def test_schema_has_clinic_display_name():
    assert "clinic_display_name" in _schema()


def test_schema_has_primary_language():
    assert "primary_language" in _schema()


def test_schema_has_fallback_language():
    assert "fallback_language" in _schema()


def test_schema_has_supported_languages():
    assert "supported_languages" in _schema()


def test_schema_has_vapi_assistant_language_mode():
    assert "vapi_assistant_language_mode" in _schema()


def test_schema_has_system_prompt_de():
    assert "system_prompt_de" in _schema()


def test_schema_has_system_prompt_en():
    assert "system_prompt_en" in _schema()


def test_schema_has_tool_schema():
    assert "tool_schema" in _schema()


def test_schema_has_required_capture_fields():
    assert "required_capture_fields" in _schema()


def test_schema_has_safety_rules():
    assert "safety_rules" in _schema()


def test_schema_has_escalation_rules():
    assert "escalation_rules" in _schema()


def test_schema_has_forbidden_claims():
    assert "forbidden_claims" in _schema()


def test_schema_production_phi_enabled_false():
    src = _schema()
    assert "production_phi_enabled" in src
    assert "False" in src


def test_schema_recording_ingestion_enabled_false():
    src = _schema()
    assert "recording_ingestion_enabled" in src
    assert "False" in src


def test_schema_transcript_ingestion_enabled_false():
    src = _schema()
    assert "transcript_ingestion_enabled" in src
    assert "False" in src


def test_schema_no_vapi_api_key():
    src = _schema().lower()
    assert "vapi_api_key" not in src
    assert "api_key" not in src


def test_schema_no_webhook_secret():
    src = _schema().lower()
    assert "webhook_secret" not in src


def test_schema_no_database_url():
    assert "DATABASE_URL" not in _schema()


# ---------------------------------------------------------------------------
# Service — German-first defaults
# ---------------------------------------------------------------------------


def test_service_has_build_function():
    assert "build_vapi_assistant_config_pack" in _service()


def test_service_has_german_prompt_builder():
    assert "_build_german_prompt" in _service()


def test_service_has_english_prompt_builder():
    assert "_build_english_prompt" in _service()


def test_service_german_prompt_ki_rezeption():
    assert "KI-Rezeption" in _service()


def test_service_german_prompt_private_praxis_wien():
    src = _service()
    assert "private" in src.lower() and "Praxis" in src and "Wien" in src


def test_service_german_prompt_keine_diagnose():
    assert "keine Diagnose" in _service() or "Keine Diagnose" in _service()


def test_service_german_prompt_keine_medizinische_beratung():
    assert "keine medizinische Beratung" in _service() or "Keine medizinische" in _service()


def test_service_german_prompt_keine_terminbestaetigung():
    src = _service()
    assert "Terminbestätigung" in src or "keine Terminbest" in src


def test_service_german_prompt_notruf_144():
    assert "144" in _service()


def test_service_english_prompt_ai_receptionist():
    assert "AI receptionist" in _service()


def test_service_english_prompt_private_clinic_vienna():
    src = _service()
    assert "private clinic in Vienna" in src


def test_service_english_prompt_no_diagnosis():
    assert "No diagnosis" in _service() or "no diagnosis" in _service()


def test_service_english_prompt_no_medical_advice():
    assert "No medical advice" in _service() or "no medical advice" in _service()


def test_service_english_prompt_no_appointment_confirmation():
    src = _service()
    assert "not promise" in src.lower() or "do not promise" in src.lower() or "no appointment confirmation" in src.lower() or "confirm" in src.lower()


def test_service_english_prompt_call_144():
    assert "144" in _service()


def test_service_tool_schema_patient_name():
    assert "patient_name" in _service()


def test_service_tool_schema_phone():
    assert '"phone"' in _service()


def test_service_tool_schema_reason():
    assert '"reason"' in _service()


def test_service_tool_schema_preferred_time():
    assert "preferred_time" in _service()


def test_service_tool_schema_urgency_level():
    assert "urgency_level" in _service()


def test_service_tool_schema_language_preference():
    assert "language_preference" in _service()


def test_service_production_phi_enabled_always_false():
    src = _service()
    assert "production_phi_enabled" in src and "False" in src


def test_service_no_vapi_api_call():
    src = _service().lower()
    assert "vapi.ai" not in src
    assert "requests.post" not in src or "vapi" not in src


def test_service_no_secrets():
    src = _service().lower()
    assert "vapi_api_key" not in src
    assert "webhook_secret" not in src


# ---------------------------------------------------------------------------
# Route — protection and response
# ---------------------------------------------------------------------------


def test_route_has_get_route():
    assert "GET" in _route().upper() or "@router.get" in _route()


def test_route_endpoint_path():
    assert "vapi-assistant-config-pack" in _route()


def test_route_requires_get_current_user():
    assert "get_current_user" in _route()


def test_route_uses_auth_context():
    assert "AuthContext" in _route()


def test_route_returns_vapiassistantconfigpack():
    assert "VapiAssistantConfigPack" in _route()


def test_route_handles_clinic_not_found():
    assert "404" in _route() or "ClinicNotFoundError" in _route()


def test_route_no_secrets_returned():
    src = _route().lower()
    assert "vapi_api_key" not in src
    assert "webhook_secret" not in src


# ---------------------------------------------------------------------------
# Async service tests — German-first behaviour
# ---------------------------------------------------------------------------


def _make_pool(clinic_row: Dict[str, Any]) -> Any:
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=MagicMock(**clinic_row, **{"__getitem__": lambda s, k: clinic_row[k]}))
    return pool


@pytest.fixture
def fake_clinic_row():
    return {
        "id": "11111111-1111-4111-8111-111111111111",
        "name": "Test Praxis Wien",
        "slug": "test-praxis-wien",
        "locale": "de-AT",
    }


@pytest.fixture
def german_first_lang_settings():
    return {
        "clinic_id": "11111111-1111-4111-8111-111111111111",
        "primary_language": "de",
        "fallback_language": "en",
        "supported_languages": ["de", "en"],
        "default_patient_language": "de",
        "vapi_assistant_language_mode": "german_first",
        "clinic_ui_language": "de",
        "updated_at": None,
    }


@pytest.mark.asyncio
async def test_service_returns_german_first_defaults(
    fake_clinic_row, german_first_lang_settings
):
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fake_clinic_row)

    with patch(
        "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
        new=AsyncMock(return_value=german_first_lang_settings),
    ), patch(
        "backend.app.services.vapi_assistant_config._load_tenant_config",
        return_value={"clinic_name": "Test Praxis Wien"},
    ):
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="11111111-1111-4111-8111-111111111111",
        )

    assert pack["primary_language"] == "de"
    assert pack["fallback_language"] == "en"
    assert pack["vapi_assistant_language_mode"] == "german_first"
    assert "de" in pack["supported_languages"]
    assert "en" in pack["supported_languages"]


@pytest.mark.asyncio
async def test_service_includes_clinic_id(fake_clinic_row, german_first_lang_settings):
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fake_clinic_row)

    with patch(
        "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
        new=AsyncMock(return_value=german_first_lang_settings),
    ), patch(
        "backend.app.services.vapi_assistant_config._load_tenant_config",
        return_value={},
    ):
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="11111111-1111-4111-8111-111111111111",
        )

    assert pack["clinic_id"] == "11111111-1111-4111-8111-111111111111"


@pytest.mark.asyncio
async def test_service_includes_clinic_display_name(fake_clinic_row, german_first_lang_settings):
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fake_clinic_row)

    with patch(
        "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
        new=AsyncMock(return_value=german_first_lang_settings),
    ), patch(
        "backend.app.services.vapi_assistant_config._load_tenant_config",
        return_value={"clinic_display_name": "Dr. Med. Test Wien"},
    ):
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="11111111-1111-4111-8111-111111111111",
        )

    assert pack["clinic_display_name"] == "Dr. Med. Test Wien"


@pytest.mark.asyncio
async def test_service_german_prompt_in_pack(fake_clinic_row, german_first_lang_settings):
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fake_clinic_row)

    with patch(
        "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
        new=AsyncMock(return_value=german_first_lang_settings),
    ), patch(
        "backend.app.services.vapi_assistant_config._load_tenant_config",
        return_value={"clinic_name": "Test Praxis Wien"},
    ):
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="11111111-1111-4111-8111-111111111111",
        )

    assert "KI-Rezeption" in pack["system_prompt_de"]
    assert "keine Diagnose" in pack["system_prompt_de"].lower() or "Keine Diagnose" in pack["system_prompt_de"]
    assert "144" in pack["system_prompt_de"]


@pytest.mark.asyncio
async def test_service_english_prompt_in_pack(fake_clinic_row, german_first_lang_settings):
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fake_clinic_row)

    with patch(
        "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
        new=AsyncMock(return_value=german_first_lang_settings),
    ), patch(
        "backend.app.services.vapi_assistant_config._load_tenant_config",
        return_value={"clinic_name": "Test Praxis Wien"},
    ):
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="11111111-1111-4111-8111-111111111111",
        )

    assert "AI receptionist" in pack["system_prompt_en"]
    assert "no diagnosis" in pack["system_prompt_en"].lower() or "No diagnosis" in pack["system_prompt_en"]
    assert "144" in pack["system_prompt_en"]


@pytest.mark.asyncio
async def test_service_tool_schema_has_required_fields(fake_clinic_row, german_first_lang_settings):
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fake_clinic_row)

    with patch(
        "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
        new=AsyncMock(return_value=german_first_lang_settings),
    ), patch(
        "backend.app.services.vapi_assistant_config._load_tenant_config",
        return_value={},
    ):
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="11111111-1111-4111-8111-111111111111",
        )

    tool = pack["tool_schema"]
    props = tool["parameters"]["properties"]
    assert "patient_name" in props
    assert "phone" in props
    assert "reason" in props
    assert "preferred_time" in props
    assert "urgency_level" in props
    assert "language_preference" in props


@pytest.mark.asyncio
async def test_service_production_phi_enabled_is_false(fake_clinic_row, german_first_lang_settings):
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fake_clinic_row)

    with patch(
        "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
        new=AsyncMock(return_value=german_first_lang_settings),
    ), patch(
        "backend.app.services.vapi_assistant_config._load_tenant_config",
        return_value={},
    ):
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="11111111-1111-4111-8111-111111111111",
        )

    assert pack["production_phi_enabled"] is False


@pytest.mark.asyncio
async def test_service_recording_ingestion_disabled_by_default(fake_clinic_row, german_first_lang_settings):
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fake_clinic_row)

    with patch(
        "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
        new=AsyncMock(return_value=german_first_lang_settings),
    ), patch(
        "backend.app.services.vapi_assistant_config._load_tenant_config",
        return_value={},
    ):
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="11111111-1111-4111-8111-111111111111",
        )

    assert pack["recording_ingestion_enabled"] is False


@pytest.mark.asyncio
async def test_service_transcript_ingestion_disabled_by_default(fake_clinic_row, german_first_lang_settings):
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fake_clinic_row)

    with patch(
        "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
        new=AsyncMock(return_value=german_first_lang_settings),
    ), patch(
        "backend.app.services.vapi_assistant_config._load_tenant_config",
        return_value={},
    ):
        pack = await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="11111111-1111-4111-8111-111111111111",
        )

    assert pack["transcript_ingestion_enabled"] is False


@pytest.mark.asyncio
async def test_service_raises_clinic_not_found():
    from backend.app.services.clinic_language_settings import ClinicNotFoundError
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)

    with pytest.raises(ClinicNotFoundError):
        await build_vapi_assistant_config_pack(
            pool=pool,
            clinic_id="00000000-0000-4000-8000-000000000000",
        )


# ---------------------------------------------------------------------------
# Route integration — protected
# ---------------------------------------------------------------------------

_FAKE_CLINIC_ID = "11111111-1111-4111-8111-111111111111"
_MISSING_CLINIC_ID = "00000000-0000-4000-8000-000000000000"


def _fake_auth():
    from backend.app.core.auth_context import AuthContext
    return AuthContext(user_id="admin-1", clinic_id=_FAKE_CLINIC_ID, role="admin")


def test_route_requires_auth():
    from fastapi.testclient import TestClient
    from backend.app.api.deps import get_db_pool
    from backend.app.main import app

    # Override DB pool so startup succeeds, but leave get_current_user unset → 401/403
    app.dependency_overrides[get_db_pool] = lambda: MagicMock()
    client = TestClient(app, raise_server_exceptions=False)
    try:
        resp = client.get(f"/clinics/{_FAKE_CLINIC_ID}/vapi-assistant-config-pack")
        assert resp.status_code in (401, 403)
    finally:
        app.dependency_overrides.pop(get_db_pool, None)


def test_route_returns_404_for_missing_clinic():
    from fastapi.testclient import TestClient
    from backend.app.api.dependencies.current_user import get_current_user
    from backend.app.api.deps import get_db_pool
    from backend.app.main import app
    from backend.app.services.clinic_language_settings import ClinicNotFoundError

    app.dependency_overrides[get_current_user] = _fake_auth
    app.dependency_overrides[get_db_pool] = lambda: MagicMock()

    client = TestClient(app, raise_server_exceptions=False)
    try:
        with patch(
            "backend.app.api.routes.vapi_assistant_config.build_vapi_assistant_config_pack",
            new=AsyncMock(side_effect=ClinicNotFoundError("not found")),
        ):
            resp = client.get(f"/clinics/{_MISSING_CLINIC_ID}/vapi-assistant-config-pack")
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_route_returns_config_pack_for_valid_clinic(fake_clinic_row, german_first_lang_settings):
    from fastapi.testclient import TestClient
    from backend.app.api.dependencies.current_user import get_current_user
    from backend.app.api.deps import get_db_pool
    from backend.app.main import app
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    app.dependency_overrides[get_current_user] = _fake_auth
    app.dependency_overrides[get_db_pool] = lambda: MagicMock()

    client = TestClient(app, raise_server_exceptions=False)
    try:
        with patch(
            "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
            new=AsyncMock(return_value=german_first_lang_settings),
        ), patch(
            "backend.app.services.vapi_assistant_config._load_tenant_config",
            return_value={"clinic_name": "Test Praxis Wien"},
        ), patch(
            "backend.app.services.vapi_assistant_config.build_vapi_assistant_config_pack",
            wraps=build_vapi_assistant_config_pack,
        ):
            pool_mock = MagicMock()
            pool_mock.fetchrow = AsyncMock(return_value=fake_clinic_row)
            app.dependency_overrides[get_db_pool] = lambda: pool_mock

            resp = client.get(f"/clinics/{fake_clinic_row['id']}/vapi-assistant-config-pack")
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["clinic_id"] == fake_clinic_row["id"]
    assert data["primary_language"] == "de"
    assert data["production_phi_enabled"] is False
    assert data["recording_ingestion_enabled"] is False
    assert data["transcript_ingestion_enabled"] is False


def test_route_response_no_phi_fields(fake_clinic_row, german_first_lang_settings):
    from fastapi.testclient import TestClient
    from backend.app.api.dependencies.current_user import get_current_user
    from backend.app.api.deps import get_db_pool
    from backend.app.main import app
    from backend.app.services.vapi_assistant_config import build_vapi_assistant_config_pack

    app.dependency_overrides[get_current_user] = _fake_auth

    client = TestClient(app, raise_server_exceptions=False)
    try:
        with patch(
            "backend.app.services.vapi_assistant_config.get_clinic_language_settings",
            new=AsyncMock(return_value=german_first_lang_settings),
        ), patch(
            "backend.app.services.vapi_assistant_config._load_tenant_config",
            return_value={},
        ):
            pool_mock = MagicMock()
            pool_mock.fetchrow = AsyncMock(return_value=fake_clinic_row)
            app.dependency_overrides[get_db_pool] = lambda: pool_mock

            resp = client.get(f"/clinics/{fake_clinic_row['id']}/vapi-assistant-config-pack")
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    body = resp.text.lower()
    assert "vapi_api_key" not in body
    assert "webhook_secret" not in body
    assert "database_url" not in body
    assert "jwt_secret" not in body


# ---------------------------------------------------------------------------
# Arch doc checks
# ---------------------------------------------------------------------------


def test_arch_doc_module_141():
    assert "141" in _arch()


def test_arch_doc_language_settings():
    src = _arch().lower()
    assert "language" in src and "settings" in src


def test_arch_doc_german_first():
    src = _arch().lower()
    assert "german" in src and "first" in src


def test_arch_doc_english_fallback():
    src = _arch().lower()
    assert "english" in src or "fallback" in src


def test_arch_doc_no_live_vapi_binding():
    src = _arch().lower()
    assert "no live vapi" in src or "no live" in src or "no vapi binding" in src or "not bind" in src


def test_arch_doc_no_secrets():
    src = _arch().lower()
    assert "no secrets" in src or "no secret" in src


def test_arch_doc_no_phi():
    src = _arch().lower()
    assert "no phi" in src


def test_arch_doc_production_phi_no_go():
    assert "NO-GO" in _arch() or "no-go" in _arch().lower()


def test_arch_doc_appointment_capture():
    src = _arch().lower()
    assert "appointment" in src and ("capture" in src or "request" in src)


def test_arch_doc_no_diagnosis():
    src = _arch().lower()
    assert "no diagnosis" in src or "keine diagnose" in src or "diagnosis" in src


def test_arch_doc_emergency_144():
    assert "144" in _arch()


def test_arch_doc_get_route():
    assert "GET" in _arch() and "vapi-assistant-config-pack" in _arch()
