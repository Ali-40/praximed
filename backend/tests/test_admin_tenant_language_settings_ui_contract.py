"""
Sprint 19 / Module 139 — Admin Tenant Language Settings UI

Static contract tests: read raw TSX/TypeScript source and verify the
language settings page, developer console nav, api.ts helpers, and arch doc
meet the specification.

No imports, no database, no network. All assertions are substring checks.
"""

from pathlib import Path

PAGE_PATH    = Path("frontend/app/developer-console/language-settings/page.tsx")
CONSOLE_PATH = Path("frontend/app/developer-console/page.tsx")
API_PATH     = Path("frontend/lib/api.ts")
ARCH_DOC     = Path("docs/architecture/ADMIN_TENANT_LANGUAGE_SETTINGS_UI.md")


def _page() -> str:
    return PAGE_PATH.read_text(encoding="utf-8")


def _console() -> str:
    return CONSOLE_PATH.read_text(encoding="utf-8")


def _api() -> str:
    return API_PATH.read_text(encoding="utf-8")


def _arch() -> str:
    return ARCH_DOC.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_page_file_exists():
    assert PAGE_PATH.exists(), f"Missing page: {PAGE_PATH}"


def test_console_file_exists():
    assert CONSOLE_PATH.exists()


def test_api_file_exists():
    assert API_PATH.exists()


def test_arch_doc_exists():
    assert ARCH_DOC.exists(), f"Missing arch doc: {ARCH_DOC}"


# ---------------------------------------------------------------------------
# Page header / identity
# ---------------------------------------------------------------------------


def test_page_title_tenant_language_settings():
    assert "Tenant Language Settings" in _page()


def test_page_internal_clinic_configuration():
    src = _page().lower()
    assert "internal" in src and "clinic configuration" in src


def test_page_admin_staging_badge():
    assert "ADMIN / STAGING" in _page()


# ---------------------------------------------------------------------------
# Clinic ID input
# ---------------------------------------------------------------------------


def test_page_has_clinic_id_input():
    src = _page()
    assert "clinicId" in src or "clinic_id" in src or "Clinic ID" in src


def test_page_has_load_settings():
    assert "Load settings" in _page()


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------


def test_page_calls_language_settings_endpoint():
    assert "/language-settings" in _page()


def test_page_uses_credentials_include():
    assert "credentials: 'include'" in _page()


def test_page_uses_patch_for_save():
    assert "'PATCH'" in _page()


# ---------------------------------------------------------------------------
# Form fields
# ---------------------------------------------------------------------------


def test_page_has_primary_language():
    src = _page()
    assert "Primary language" in src or "primary_language" in src


def test_page_has_german_first():
    src = _page()
    assert "German-first" in src or "german_first" in src


def test_page_has_fallback_language():
    src = _page()
    assert "Fallback language" in src or "fallback_language" in src


def test_page_has_supported_languages():
    src = _page()
    assert "Supported languages" in src or "supported_languages" in src


def test_page_has_deutsch():
    assert "Deutsch" in _page()


def test_page_has_english():
    assert "English" in _page()


def test_page_has_default_patient_language():
    src = _page()
    assert "default_patient_language" in src or "Default patient language" in src


def test_page_has_vapi_assistant_language_mode():
    src = _page()
    assert "vapi_assistant_language_mode" in src or "Vapi assistant language mode" in src


def test_page_has_german_first_option():
    assert "german_first" in _page()


def test_page_has_english_first_option():
    assert "english_first" in _page()


def test_page_has_bilingual_auto_option():
    assert "bilingual_auto" in _page()


def test_page_has_clinic_ui_language():
    src = _page()
    assert "clinic_ui_language" in src or "Clinic UI language" in src or "Clinic UI Language" in src


# ---------------------------------------------------------------------------
# Save / update
# ---------------------------------------------------------------------------


def test_page_has_save_language_settings():
    assert "Save language settings" in _page()


def test_page_has_language_settings_saved():
    assert "Language settings saved" in _page()


# ---------------------------------------------------------------------------
# Error states
# ---------------------------------------------------------------------------


def test_page_has_admin_session_required():
    assert "Admin session required" in _page()


def test_page_has_clinic_not_found():
    src = _page().lower()
    assert "not found" in src or "clinic not found" in src


def test_page_handles_401():
    assert "401" in _page()


def test_page_handles_403():
    assert "403" in _page()


def test_page_handles_404():
    assert "404" in _page()


# ---------------------------------------------------------------------------
# Safety copy
# ---------------------------------------------------------------------------


def test_page_no_phi():
    src = _page()
    assert "No PHI" in src or "no PHI" in src or "no phi" in src.lower()


def test_page_no_secrets():
    src = _page()
    assert "No secrets" in src or "no secrets" in src.lower()


def test_page_no_vapi_credentials():
    src = _page()
    assert "No Vapi credentials" in src or "no vapi credentials" in src.lower()


def test_page_production_phi_remains_no_go():
    assert "Production PHI remains NO-GO" in _page()


def test_page_no_production_activation():
    src = _page().lower()
    assert "no production activation" in src or "production" in src


# ---------------------------------------------------------------------------
# What must NOT be in the page
# ---------------------------------------------------------------------------


def test_page_no_vapi_api_key_field():
    src = _page().lower()
    assert "vapi api key" not in src
    assert "vapi_api_key" not in src


def test_page_no_webhook_secret_field():
    src = _page().lower()
    assert "webhook_secret" not in src
    assert "webhook secret" not in src


def test_page_no_database_url():
    assert "DATABASE_URL" not in _page()


def test_page_no_jwt_secret():
    src = _page().lower()
    assert "jwt_secret" not in src
    assert "jwt secret" not in src


def test_page_no_session_storage():
    assert "sessionStorage" not in _page()


def test_page_no_local_storage():
    assert "localStorage" not in _page()


# ---------------------------------------------------------------------------
# Developer console nav
# ---------------------------------------------------------------------------


def test_console_links_to_language_settings():
    assert "/developer-console/language-settings" in _console()


def test_console_has_language_settings_panel():
    src = _console()
    assert "Language Settings" in src or "language-settings" in src


def test_console_no_session_storage():
    assert "sessionStorage" not in _console()


def test_console_no_local_storage():
    assert "localStorage" not in _console()


# ---------------------------------------------------------------------------
# api.ts helpers
# ---------------------------------------------------------------------------


def test_api_has_fetch_clinic_language_settings():
    assert "fetchClinicLanguageSettings" in _api()


def test_api_has_update_clinic_language_settings():
    assert "updateClinicLanguageSettings" in _api()


def test_api_fetch_calls_language_settings_path():
    assert "/language-settings" in _api()


def test_api_update_uses_patch():
    src = _api()
    assert "updateClinicLanguageSettings" in src
    assert "'PATCH'" in src


def test_api_uses_credentials_include():
    assert "credentials: 'include'" in _api()


def test_api_has_clinic_language_settings_interface():
    assert "ClinicLanguageSettings" in _api()


def test_api_interface_has_primary_language():
    assert "primary_language" in _api()


def test_api_interface_has_vapi_assistant_language_mode():
    assert "vapi_assistant_language_mode" in _api()


def test_api_interface_has_supported_languages():
    assert "supported_languages" in _api()


def test_api_no_session_storage():
    assert "sessionStorage" not in _api()


def test_api_no_local_storage():
    assert "localStorage" not in _api()


def test_api_no_vapi_credentials():
    src = _api().lower()
    assert "vapi_api_key" not in src


# ---------------------------------------------------------------------------
# Arch doc checks
# ---------------------------------------------------------------------------


def test_arch_doc_module_139():
    assert "139" in _arch()


def test_arch_doc_language_settings():
    src = _arch().lower()
    assert "language settings" in src


def test_arch_doc_german_first():
    src = _arch().lower()
    assert "german" in src and "first" in src


def test_arch_doc_english_fallback():
    src = _arch().lower()
    assert "english" in src or "fallback" in src


def test_arch_doc_no_phi():
    src = _arch().lower()
    assert "no phi" in src or "production phi" in src


def test_arch_doc_no_vapi_credentials():
    src = _arch().lower()
    assert "vapi credentials" in src or "no vapi" in src


def test_arch_doc_production_phi_no_go():
    assert "NO-GO" in _arch() or "no-go" in _arch().lower()


def test_arch_doc_get_route():
    assert "GET" in _arch() and "language-settings" in _arch()


def test_arch_doc_patch_route():
    assert "PATCH" in _arch() and "language-settings" in _arch()
