"""
Sprint 19 / Module 138 — Tenant Language Settings API Foundation.

Static + unit + route integration tests.
Fake data only. No real PHI. No secrets. No Vapi credentials.
No real database connection. File I/O is patched in unit tests.
"""

from __future__ import annotations

import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.api.dependencies.current_user import get_current_user
from backend.app.api.deps import get_db_pool
from backend.app.core.auth_context import AuthContext
from backend.app.main import app
from backend.app.schemas.clinic_language_settings import (
    ALLOWED_LANGUAGES,
    ALLOWED_VAPI_MODES,
    ClinicLanguageSettingsRead,
    ClinicLanguageSettingsUpdate,
)
from backend.app.services.clinic_language_settings import (
    GERMAN_FIRST_DEFAULTS,
    ClinicNotFoundError,
    LanguageSettingsValidationError,
    _locale_to_primary_language,
    _primary_language_to_locale,
    get_clinic_language_settings,
    update_clinic_language_settings,
)

ROOT        = pathlib.Path(__file__).parent.parent.parent
SCHEMA_FILE = ROOT / "backend" / "app" / "schemas" / "clinic_language_settings.py"
SERVICE_FILE = ROOT / "backend" / "app" / "services" / "clinic_language_settings.py"
ROUTE_FILE  = ROOT / "backend" / "app" / "api" / "routes" / "clinic_language_settings.py"
ARCH_DOC    = ROOT / "docs" / "architecture" / "TENANT_LANGUAGE_SETTINGS_API_FOUNDATION.md"
PROV_FILE   = ROOT / "backend" / "app" / "services" / "tenant_provisioning.py"

# ---------------------------------------------------------------------------
# Fake data
# ---------------------------------------------------------------------------

FAKE_CLINIC_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
FAKE_USER_ID   = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"

FAKE_CLINIC_ROW = {
    "id":         FAKE_CLINIC_ID,
    "name":       "Test Praxis Wien",
    "slug":       "test-praxis-wien-abc12345",
    "status":     "pilot_setup",
    "locale":     "de-AT",
    "updated_at": "2026-07-06T10:00:00+00:00",
}

FAKE_EN_CLINIC_ROW = {**FAKE_CLINIC_ROW, "locale": "en-US"}

FAKE_UPDATED_ROW = {"updated_at": "2026-07-06T11:00:00+00:00"}


def _staff_auth() -> AuthContext:
    return AuthContext(
        user_id=FAKE_USER_ID,
        clinic_id=FAKE_CLINIC_ID,
        role="admin",
    )


def _pool(fetchrow_returns=None) -> MagicMock:
    pool = MagicMock()
    if callable(fetchrow_returns):
        pool.fetchrow = fetchrow_returns
    else:
        pool.fetchrow = AsyncMock(return_value=fetchrow_returns)
    return pool


# ---------------------------------------------------------------------------
# 1. Static contract tests — file existence
# ---------------------------------------------------------------------------


def test_schema_file_exists():
    assert SCHEMA_FILE.exists()


def test_service_file_exists():
    assert SERVICE_FILE.exists()


def test_route_file_exists():
    assert ROUTE_FILE.exists()


def test_arch_doc_exists():
    assert ARCH_DOC.exists(), f"Missing arch doc: {ARCH_DOC}"


# ---------------------------------------------------------------------------
# 2. Static contract tests — route content
# ---------------------------------------------------------------------------


def _route_src() -> str:
    return ROUTE_FILE.read_text(encoding="utf-8")


def _service_src() -> str:
    return SERVICE_FILE.read_text(encoding="utf-8")


def _schema_src() -> str:
    return SCHEMA_FILE.read_text(encoding="utf-8")


def _arch_src() -> str:
    return ARCH_DOC.read_text(encoding="utf-8")


def test_route_has_get_language_settings():
    assert "language-settings" in _route_src()
    assert "GET" in _route_src() or "@router.get" in _route_src()


def test_route_has_patch_language_settings():
    assert "@router.patch" in _route_src()


def test_route_uses_get_current_user():
    assert "get_current_user" in _route_src()


def test_route_prefix_clinics():
    assert 'prefix="/clinics"' in _route_src()


def test_route_no_phi_fields():
    src = _route_src().lower()
    assert "patient_name" not in src
    assert "diagnosis" not in src
    assert "ssn" not in src


def test_route_no_vapi_credentials():
    src = _route_src().lower()
    assert "vapi_api_key" not in src
    assert "webhook_secret" not in src


def test_route_no_database_url():
    assert "DATABASE_URL" not in _route_src()


def test_service_has_german_first_defaults():
    assert "GERMAN_FIRST_DEFAULTS" in _service_src()
    assert "german_first" in _service_src()


def test_service_has_get_function():
    assert "get_clinic_language_settings" in _service_src()


def test_service_has_update_function():
    assert "update_clinic_language_settings" in _service_src()


def test_service_no_phi_stored():
    src = _service_src().lower()
    assert "patient_name" not in src
    assert "diagnosis" not in src


def test_service_no_vapi_credentials():
    src = _service_src().lower()
    assert "vapi_api_key" not in src
    assert "webhook_secret" not in src


def test_service_no_production_phi_activation():
    assert "production_phi_enabled" not in _service_src()


def test_schema_has_allowed_languages():
    assert "ALLOWED_LANGUAGES" in _schema_src()
    assert '"de"' in _schema_src() or "'de'" in _schema_src()
    assert '"en"' in _schema_src() or "'en'" in _schema_src()


def test_schema_has_allowed_vapi_modes():
    assert "ALLOWED_VAPI_MODES" in _schema_src()
    assert "german_first" in _schema_src()
    assert "english_first" in _schema_src()
    assert "bilingual_auto" in _schema_src()


def test_schema_no_phi_fields():
    src = _schema_src().lower()
    assert "patient_name" not in src
    assert "diagnosis" not in src


def test_schema_no_secrets():
    src = _schema_src().lower()
    assert "vapi_api_key" not in src
    assert "webhook_secret" not in src
    assert "database_url" not in src


def test_provisioning_service_writes_language_config():
    prov_src = PROV_FILE.read_text(encoding="utf-8")
    assert "_write_language_config_to_file" in prov_src


def test_provisioning_service_sets_vapi_mode_german():
    prov_src = PROV_FILE.read_text(encoding="utf-8")
    assert "german_first" in prov_src


def test_provisioning_service_sets_default_patient_language():
    prov_src = PROV_FILE.read_text(encoding="utf-8")
    assert "default_patient_language" in prov_src


# ---------------------------------------------------------------------------
# 3. Arch doc checks
# ---------------------------------------------------------------------------


def test_arch_doc_module_138():
    assert "138" in _arch_src()


def test_arch_doc_german_first():
    src = _arch_src().lower()
    assert "german" in src and "first" in src


def test_arch_doc_english_fallback():
    src = _arch_src().lower()
    assert "english" in src or "fallback" in src


def test_arch_doc_vapi_assistant_language_mode():
    assert "vapi_assistant_language_mode" in _arch_src() or "vapi" in _arch_src().lower()


def test_arch_doc_clinic_ui_language():
    assert "clinic_ui_language" in _arch_src()


def test_arch_doc_no_phi():
    src = _arch_src().lower()
    assert "no phi" in src or "no production phi" in src or "production phi" in src


def test_arch_doc_no_vapi_credentials():
    src = _arch_src().lower()
    assert "vapi credentials" in src or "no vapi" in src


def test_arch_doc_production_phi_no_go():
    assert "NO-GO" in _arch_src() or "no-go" in _arch_src().lower()


def test_arch_doc_storage_approach():
    src = _arch_src().lower()
    assert "locale" in src or "json" in src


def test_arch_doc_get_route():
    assert "GET" in _arch_src() and "language-settings" in _arch_src()


def test_arch_doc_patch_route():
    assert "PATCH" in _arch_src() and "language-settings" in _arch_src()


# ---------------------------------------------------------------------------
# 4. Schema unit tests — defaults
# ---------------------------------------------------------------------------


def test_schema_read_defaults_german_first():
    r = ClinicLanguageSettingsRead(clinic_id="test-id")
    assert r.primary_language == "de"
    assert r.fallback_language == "en"
    assert r.vapi_assistant_language_mode == "german_first"
    assert r.clinic_ui_language == "de"
    assert r.default_patient_language == "de"
    assert r.supported_languages == ["de", "en"]


def test_schema_read_ok_true_by_default():
    r = ClinicLanguageSettingsRead(clinic_id="x")
    assert r.ok is True


def test_schema_update_all_optional():
    u = ClinicLanguageSettingsUpdate()
    assert u.primary_language is None
    assert u.fallback_language is None


# ---------------------------------------------------------------------------
# 5. Schema validation — rejections
# ---------------------------------------------------------------------------


def test_schema_rejects_invalid_primary_language():
    with pytest.raises(ValidationError):
        ClinicLanguageSettingsUpdate(primary_language="fr")


def test_schema_rejects_invalid_fallback_language():
    with pytest.raises(ValidationError):
        ClinicLanguageSettingsUpdate(fallback_language="es")


def test_schema_rejects_empty_supported_languages():
    with pytest.raises(ValidationError):
        ClinicLanguageSettingsUpdate(supported_languages=[])


def test_schema_rejects_unsupported_language_in_list():
    with pytest.raises(ValidationError):
        ClinicLanguageSettingsUpdate(supported_languages=["de", "fr"])


def test_schema_rejects_invalid_vapi_mode():
    with pytest.raises(ValidationError):
        ClinicLanguageSettingsUpdate(vapi_assistant_language_mode="invalid_mode")


def test_schema_rejects_invalid_clinic_ui_language():
    with pytest.raises(ValidationError):
        ClinicLanguageSettingsUpdate(clinic_ui_language="fr")


def test_schema_rejects_primary_not_in_supported():
    with pytest.raises(ValidationError):
        ClinicLanguageSettingsUpdate(
            primary_language="de",
            supported_languages=["en"],
        )


def test_schema_accepts_valid_german_first():
    u = ClinicLanguageSettingsUpdate(
        primary_language="de",
        fallback_language="en",
        supported_languages=["de", "en"],
        vapi_assistant_language_mode="german_first",
        clinic_ui_language="de",
    )
    assert u.primary_language == "de"


def test_schema_accepts_english_first():
    u = ClinicLanguageSettingsUpdate(
        primary_language="en",
        supported_languages=["de", "en"],
        vapi_assistant_language_mode="english_first",
    )
    assert u.primary_language == "en"


def test_schema_accepts_bilingual_auto():
    u = ClinicLanguageSettingsUpdate(vapi_assistant_language_mode="bilingual_auto")
    assert u.vapi_assistant_language_mode == "bilingual_auto"


# ---------------------------------------------------------------------------
# 6. Service helper unit tests
# ---------------------------------------------------------------------------


def test_locale_to_primary_language_de_at():
    assert _locale_to_primary_language("de-AT") == "de"


def test_locale_to_primary_language_en_us():
    assert _locale_to_primary_language("en-US") == "en"


def test_locale_to_primary_language_de_plain():
    assert _locale_to_primary_language("de") == "de"


def test_locale_to_primary_language_unknown_defaults_de():
    assert _locale_to_primary_language("xx-YY") == "de"


def test_primary_language_to_locale_de():
    assert _primary_language_to_locale("de") == "de-AT"


def test_primary_language_to_locale_en():
    assert _primary_language_to_locale("en") == "en-US"


def test_primary_language_to_locale_unknown_defaults_de_at():
    assert _primary_language_to_locale("xx") == "de-AT"


def test_german_first_defaults_complete():
    for key in (
        "primary_language",
        "fallback_language",
        "supported_languages",
        "default_patient_language",
        "vapi_assistant_language_mode",
        "clinic_ui_language",
    ):
        assert key in GERMAN_FIRST_DEFAULTS


def test_german_first_defaults_are_german():
    assert GERMAN_FIRST_DEFAULTS["primary_language"] == "de"
    assert GERMAN_FIRST_DEFAULTS["vapi_assistant_language_mode"] == "german_first"
    assert GERMAN_FIRST_DEFAULTS["clinic_ui_language"] == "de"
    assert GERMAN_FIRST_DEFAULTS["default_patient_language"] == "de"


def test_allowed_languages_set():
    assert "de" in ALLOWED_LANGUAGES
    assert "en" in ALLOWED_LANGUAGES
    assert "fr" not in ALLOWED_LANGUAGES


def test_allowed_vapi_modes_set():
    assert "german_first" in ALLOWED_VAPI_MODES
    assert "english_first" in ALLOWED_VAPI_MODES
    assert "bilingual_auto" in ALLOWED_VAPI_MODES
    assert "invalid" not in ALLOWED_VAPI_MODES


# ---------------------------------------------------------------------------
# 7. Service async unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_settings_clinic_not_found():
    pool = _pool(fetchrow_returns=None)
    with patch("backend.app.services.clinic_language_settings._load_language_config_from_file", return_value={}):
        with pytest.raises(ClinicNotFoundError):
            await get_clinic_language_settings(pool, "no-such-clinic")


@pytest.mark.asyncio
async def test_get_settings_german_first_from_de_at_locale():
    pool = _pool(fetchrow_returns=FAKE_CLINIC_ROW)
    with patch("backend.app.services.clinic_language_settings._load_language_config_from_file", return_value={}):
        result = await get_clinic_language_settings(pool, FAKE_CLINIC_ID)
    assert result["primary_language"] == "de"
    assert result["vapi_assistant_language_mode"] == "german_first"
    assert result["clinic_ui_language"] == "de"
    assert result["fallback_language"] == "en"


@pytest.mark.asyncio
async def test_get_settings_english_from_en_us_locale():
    pool = _pool(fetchrow_returns=FAKE_EN_CLINIC_ROW)
    with patch("backend.app.services.clinic_language_settings._load_language_config_from_file", return_value={}):
        result = await get_clinic_language_settings(pool, FAKE_CLINIC_ID)
    assert result["primary_language"] == "en"


@pytest.mark.asyncio
async def test_get_settings_uses_file_config():
    file_cfg = {
        "primary_language": "en",
        "fallback_language": "de",
        "supported_languages": ["en", "de"],
        "default_patient_language": "en",
        "vapi_assistant_language_mode": "english_first",
        "clinic_ui_language": "en",
    }
    pool = _pool(fetchrow_returns=FAKE_CLINIC_ROW)
    with patch("backend.app.services.clinic_language_settings._load_language_config_from_file", return_value=file_cfg):
        result = await get_clinic_language_settings(pool, FAKE_CLINIC_ID)
    assert result["primary_language"] == "en"
    assert result["vapi_assistant_language_mode"] == "english_first"


@pytest.mark.asyncio
async def test_get_settings_returns_clinic_id():
    pool = _pool(fetchrow_returns=FAKE_CLINIC_ROW)
    with patch("backend.app.services.clinic_language_settings._load_language_config_from_file", return_value={}):
        result = await get_clinic_language_settings(pool, FAKE_CLINIC_ID)
    assert result["clinic_id"] == FAKE_CLINIC_ID


@pytest.mark.asyncio
async def test_update_settings_clinic_not_found():
    pool = _pool(fetchrow_returns=None)
    with pytest.raises(ClinicNotFoundError):
        await update_clinic_language_settings(pool, "no-such", {})


@pytest.mark.asyncio
async def test_update_settings_primary_not_in_supported():
    call_count = 0

    async def _fetchrow_side(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return FAKE_CLINIC_ROW   # _get_clinic_row for update
        return FAKE_CLINIC_ROW       # _get_clinic_row for get (inside update)

    pool = MagicMock()
    pool.fetchrow = _fetchrow_side

    with patch("backend.app.services.clinic_language_settings._load_language_config_from_file", return_value={}):
        with pytest.raises(LanguageSettingsValidationError):
            await update_clinic_language_settings(
                pool,
                FAKE_CLINIC_ID,
                {"primary_language": "en", "supported_languages": ["de"]},
            )


@pytest.mark.asyncio
async def test_update_settings_applies_partial_update():
    call_count = 0

    async def _fetchrow_side(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        sql = str(args[0]) if args else ""
        if "UPDATE" in sql:
            return FAKE_UPDATED_ROW
        return FAKE_CLINIC_ROW

    pool = MagicMock()
    pool.fetchrow = _fetchrow_side

    with patch("backend.app.services.clinic_language_settings._load_language_config_from_file", return_value={}):
        with patch("backend.app.services.clinic_language_settings._write_language_config_to_file") as mock_write:
            result = await update_clinic_language_settings(
                pool,
                FAKE_CLINIC_ID,
                {"vapi_assistant_language_mode": "bilingual_auto"},
            )
    assert result["vapi_assistant_language_mode"] == "bilingual_auto"
    assert result["primary_language"] == "de"   # unchanged
    mock_write.assert_called_once()


@pytest.mark.asyncio
async def test_update_settings_updates_locale_in_db():
    sql_calls = []

    async def _fetchrow_side(*args, **kwargs):
        sql_calls.append(str(args[0]) if args else "")
        if "UPDATE" in str(args[0]):
            return FAKE_UPDATED_ROW
        return FAKE_CLINIC_ROW

    pool = MagicMock()
    pool.fetchrow = _fetchrow_side

    with patch("backend.app.services.clinic_language_settings._load_language_config_from_file", return_value={}):
        with patch("backend.app.services.clinic_language_settings._write_language_config_to_file"):
            await update_clinic_language_settings(
                pool,
                FAKE_CLINIC_ID,
                {"primary_language": "en", "supported_languages": ["de", "en"]},
            )

    update_sqls = [s for s in sql_calls if "UPDATE" in s]
    assert len(update_sqls) >= 1
    assert "locale" in update_sqls[0]


@pytest.mark.asyncio
async def test_update_settings_writes_file():
    async def _fetchrow_side(*args, **kwargs):
        if "UPDATE" in str(args[0]):
            return FAKE_UPDATED_ROW
        return FAKE_CLINIC_ROW

    pool = MagicMock()
    pool.fetchrow = _fetchrow_side

    with patch("backend.app.services.clinic_language_settings._load_language_config_from_file", return_value={}):
        with patch("backend.app.services.clinic_language_settings._write_language_config_to_file") as mock_write:
            await update_clinic_language_settings(pool, FAKE_CLINIC_ID, {})
    mock_write.assert_called_once()


# ---------------------------------------------------------------------------
# 8. Provisioning language integration
# ---------------------------------------------------------------------------


def test_provisioning_sets_vapi_german_first_for_german_clinic():
    prov_src = PROV_FILE.read_text(encoding="utf-8")
    assert "german_first" in prov_src
    assert "vapi_assistant_language_mode" in prov_src


def test_provisioning_preserves_preferred_language_as_primary():
    prov_src = PROV_FILE.read_text(encoding="utf-8")
    assert "preferred_language" in prov_src
    assert "primary_language" in prov_src


def test_provisioning_preserves_default_patient_language():
    prov_src = PROV_FILE.read_text(encoding="utf-8")
    assert "default_patient_language" in prov_src


def test_provisioning_preserves_clinic_ui_language():
    prov_src = PROV_FILE.read_text(encoding="utf-8")
    assert "clinic_ui_language" in prov_src


def test_provisioning_calls_write_language_config():
    prov_src = PROV_FILE.read_text(encoding="utf-8")
    assert "_write_language_config_to_file" in prov_src


def test_provisioning_locale_derivation_german():
    # de-AT locale → primary_language de (tested via helper)
    assert _locale_to_primary_language("de-AT") == "de"


# ---------------------------------------------------------------------------
# 9. Route integration tests
# ---------------------------------------------------------------------------


FAKE_SETTINGS = {
    "clinic_id":                    FAKE_CLINIC_ID,
    "primary_language":             "de",
    "fallback_language":            "en",
    "supported_languages":          ["de", "en"],
    "default_patient_language":     "de",
    "vapi_assistant_language_mode": "german_first",
    "clinic_ui_language":           "de",
    "updated_at":                   "2026-07-06T10:00:00+00:00",
}


@pytest.fixture()
def authed_client():
    app.dependency_overrides[get_db_pool] = lambda: MagicMock()
    app.dependency_overrides[get_current_user] = _staff_auth
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def unauthed_client():
    app.dependency_overrides[get_db_pool] = lambda: MagicMock()
    app.dependency_overrides.pop(get_current_user, None)
    yield TestClient(app)
    app.dependency_overrides.pop(get_db_pool, None)


def test_route_get_requires_auth(unauthed_client):
    resp = unauthed_client.get(f"/clinics/{FAKE_CLINIC_ID}/language-settings")
    assert resp.status_code in (401, 403)


def test_route_patch_requires_auth(unauthed_client):
    resp = unauthed_client.patch(
        f"/clinics/{FAKE_CLINIC_ID}/language-settings",
        json={"primary_language": "de"},
    )
    assert resp.status_code in (401, 403)


def test_route_get_clinic_not_found(authed_client):
    with patch(
        "backend.app.api.routes.clinic_language_settings.get_clinic_language_settings",
        side_effect=ClinicNotFoundError("not found"),
    ):
        resp = authed_client.get(f"/clinics/{FAKE_CLINIC_ID}/language-settings")
    assert resp.status_code == 404


def test_route_patch_clinic_not_found(authed_client):
    with patch(
        "backend.app.api.routes.clinic_language_settings.update_clinic_language_settings",
        side_effect=ClinicNotFoundError("not found"),
    ):
        resp = authed_client.patch(
            f"/clinics/{FAKE_CLINIC_ID}/language-settings",
            json={"primary_language": "de"},
        )
    assert resp.status_code == 404


def test_route_get_success(authed_client):
    with patch(
        "backend.app.api.routes.clinic_language_settings.get_clinic_language_settings",
        return_value=FAKE_SETTINGS,
    ):
        resp = authed_client.get(f"/clinics/{FAKE_CLINIC_ID}/language-settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["primary_language"] == "de"
    assert data["vapi_assistant_language_mode"] == "german_first"
    assert data["clinic_id"] == FAKE_CLINIC_ID


def test_route_get_no_phi_in_response(authed_client):
    with patch(
        "backend.app.api.routes.clinic_language_settings.get_clinic_language_settings",
        return_value=FAKE_SETTINGS,
    ):
        resp = authed_client.get(f"/clinics/{FAKE_CLINIC_ID}/language-settings")
    data = resp.json()
    assert "patient_name" not in data
    assert "diagnosis" not in data
    assert "vapi_api_key" not in data


def test_route_patch_success(authed_client):
    updated = {**FAKE_SETTINGS, "vapi_assistant_language_mode": "bilingual_auto"}
    with patch(
        "backend.app.api.routes.clinic_language_settings.update_clinic_language_settings",
        return_value=updated,
    ):
        resp = authed_client.patch(
            f"/clinics/{FAKE_CLINIC_ID}/language-settings",
            json={"vapi_assistant_language_mode": "bilingual_auto"},
        )
    assert resp.status_code == 200
    assert resp.json()["vapi_assistant_language_mode"] == "bilingual_auto"


def test_route_patch_invalid_language_422(authed_client):
    resp = authed_client.patch(
        f"/clinics/{FAKE_CLINIC_ID}/language-settings",
        json={"primary_language": "fr"},
    )
    assert resp.status_code == 422


def test_route_patch_invalid_vapi_mode_422(authed_client):
    resp = authed_client.patch(
        f"/clinics/{FAKE_CLINIC_ID}/language-settings",
        json={"vapi_assistant_language_mode": "auto"},
    )
    assert resp.status_code == 422


def test_route_patch_empty_supported_languages_422(authed_client):
    resp = authed_client.patch(
        f"/clinics/{FAKE_CLINIC_ID}/language-settings",
        json={"supported_languages": []},
    )
    assert resp.status_code == 422


def test_route_patch_validation_error_400(authed_client):
    with patch(
        "backend.app.api.routes.clinic_language_settings.update_clinic_language_settings",
        side_effect=LanguageSettingsValidationError("primary not in supported"),
    ):
        resp = authed_client.patch(
            f"/clinics/{FAKE_CLINIC_ID}/language-settings",
            json={"primary_language": "de"},
        )
    assert resp.status_code == 400


def test_route_patch_response_has_all_fields(authed_client):
    with patch(
        "backend.app.api.routes.clinic_language_settings.update_clinic_language_settings",
        return_value=FAKE_SETTINGS,
    ):
        resp = authed_client.patch(
            f"/clinics/{FAKE_CLINIC_ID}/language-settings",
            json={"primary_language": "de"},
        )
    data = resp.json()
    for field in (
        "ok", "clinic_id", "primary_language", "fallback_language",
        "supported_languages", "default_patient_language",
        "vapi_assistant_language_mode", "clinic_ui_language",
    ):
        assert field in data, f"Missing field in response: {field}"
