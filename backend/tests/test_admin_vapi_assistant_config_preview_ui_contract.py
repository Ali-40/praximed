"""
Sprint 19 / Module 142 — Admin Vapi Assistant Config Preview UI

Static contract tests: read raw TSX/TypeScript source and verify the
Vapi config preview page, developer console nav, api.ts helpers, and arch doc
meet the specification.

No imports, no database, no network. All assertions are substring checks.
"""

from pathlib import Path

PAGE_PATH    = Path("frontend/app/developer-console/vapi-config/page.tsx")
CONSOLE_PATH = Path("frontend/app/developer-console/page.tsx")
API_PATH     = Path("frontend/lib/api.ts")
ARCH_DOC     = Path("docs/architecture/ADMIN_VAPI_ASSISTANT_CONFIG_PREVIEW_UI.md")


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


def test_page_title_vapi_assistant_config_preview():
    assert "Vapi Assistant Config Preview" in _page()


def test_page_read_only_tenant_assistant_configuration():
    src = _page().lower()
    assert "read-only" in src and "tenant" in src and "assistant" in src


def test_page_admin_staging_badge():
    assert "ADMIN / STAGING" in _page()


# ---------------------------------------------------------------------------
# Clinic ID input
# ---------------------------------------------------------------------------


def test_page_has_clinic_id_input():
    src = _page()
    assert "clinicId" in src or "clinic_id" in src or "Clinic ID" in src


def test_page_has_load_config_pack():
    src = _page().lower()
    assert "load config" in src


def test_page_shows_staging_clinic_example():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _page()


# ---------------------------------------------------------------------------
# API call
# ---------------------------------------------------------------------------


def test_page_calls_vapi_assistant_config_pack_endpoint():
    assert "vapi-assistant-config-pack" in _page()


def test_page_uses_credentials_include():
    assert "credentials: 'include'" in _page()


# ---------------------------------------------------------------------------
# Display sections
# ---------------------------------------------------------------------------


def test_page_has_german_first_prompt():
    src = _page().lower()
    assert "german" in src and ("first" in src or "prompt" in src)


def test_page_has_english_fallback_prompt():
    src = _page().lower()
    assert "english" in src and ("fallback" in src or "prompt" in src)


def test_page_has_required_capture_fields():
    src = _page().lower()
    assert "required capture fields" in src or "required_capture_fields" in src


def test_page_has_tool_schema():
    src = _page().lower()
    assert "tool schema" in src or "tool_schema" in src


def test_page_has_safety_rules():
    src = _page().lower()
    assert "safety rules" in src or "safety_rules" in src


def test_page_has_forbidden_claims():
    src = _page().lower()
    assert "forbidden claims" in src or "forbidden_claims" in src


def test_page_has_readiness_flags():
    src = _page().lower()
    assert "readiness" in src or "flags" in src


# ---------------------------------------------------------------------------
# Specific field names displayed
# ---------------------------------------------------------------------------


def test_page_shows_patient_name():
    assert "patient_name" in _page()


def test_page_shows_phone():
    src = _page()
    assert "phone" in src


def test_page_shows_reason():
    assert "reason" in _page()


def test_page_shows_preferred_time():
    assert "preferred_time" in _page()


def test_page_shows_language_preference():
    assert "language_preference" in _page()


def test_page_shows_urgency_level():
    assert "urgency_level" in _page()


def test_page_shows_x_vapi_service_name():
    assert "X-Vapi-Service-Name" in _page()


def test_page_shows_x_vapi_clinic_id():
    assert "X-Vapi-Clinic-Id" in _page()


def test_page_shows_x_vapi_scopes():
    assert "X-Vapi-Scopes" in _page()


# ---------------------------------------------------------------------------
# Capture endpoint reference
# ---------------------------------------------------------------------------


def test_page_mentions_capture_appointment_request():
    src = _page()
    assert "capture-appointment-request" in src or "capture_appointment_request" in src


# ---------------------------------------------------------------------------
# Safety flags displayed
# ---------------------------------------------------------------------------


def test_page_shows_production_phi_enabled():
    assert "production_phi_enabled" in _page()


def test_page_shows_recording_ingestion_enabled():
    assert "recording_ingestion_enabled" in _page()


def test_page_shows_transcript_ingestion_enabled():
    assert "transcript_ingestion_enabled" in _page()


# ---------------------------------------------------------------------------
# Safety copy
# ---------------------------------------------------------------------------


def test_page_no_vapi_credentials():
    src = _page().lower()
    assert "no vapi credentials" in src or "vapi credentials" in src


def test_page_production_phi_remains_no_go():
    assert "Production PHI remains NO-GO" in _page()


def test_page_preview_only():
    src = _page().lower()
    assert "preview only" in src or "read-only preview" in src


def test_page_no_live_vapi_binding():
    src = _page().lower()
    assert "no live vapi binding" in src or "no live" in src or "vapi binding" in src


# ---------------------------------------------------------------------------
# Error states
# ---------------------------------------------------------------------------


def test_page_has_admin_session_required():
    assert "Admin session required" in _page()


def test_page_handles_401():
    assert "401" in _page()


def test_page_handles_403():
    assert "403" in _page()


def test_page_handles_404():
    assert "404" in _page()


def test_page_has_clinic_not_found():
    src = _page().lower()
    assert "not found" in src


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


def test_console_links_to_vapi_config():
    assert "/developer-console/vapi-config" in _console()


def test_console_has_vapi_config_panel():
    src = _console()
    assert "Vapi" in src and ("Config" in src or "config" in src)


def test_console_has_preview_vapi_config_link():
    src = _console()
    assert "vapi-config" in src


def test_console_no_session_storage():
    assert "sessionStorage" not in _console()


def test_console_no_local_storage():
    assert "localStorage" not in _console()


# ---------------------------------------------------------------------------
# api.ts helpers
# ---------------------------------------------------------------------------


def test_api_has_fetch_vapi_assistant_config_pack():
    assert "fetchVapiAssistantConfigPack" in _api()


def test_api_fetch_calls_vapi_config_pack_path():
    assert "vapi-assistant-config-pack" in _api()


def test_api_uses_credentials_include():
    assert "credentials: 'include'" in _api()


def test_api_has_vapi_assistant_config_pack_interface():
    assert "VapiAssistantConfigPack" in _api()


def test_api_interface_has_system_prompt_de():
    assert "system_prompt_de" in _api()


def test_api_interface_has_system_prompt_en():
    assert "system_prompt_en" in _api()


def test_api_interface_has_production_phi_enabled():
    assert "production_phi_enabled" in _api()


def test_api_interface_has_required_capture_fields():
    assert "required_capture_fields" in _api()


def test_api_interface_has_safety_rules():
    assert "safety_rules" in _api()


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


def test_arch_doc_module_142():
    assert "142" in _arch()


def test_arch_doc_vapi_config_preview():
    src = _arch().lower()
    assert "vapi" in src and ("preview" in src or "config" in src)


def test_arch_doc_german_first():
    src = _arch().lower()
    assert "german" in src and "first" in src


def test_arch_doc_english_fallback():
    src = _arch().lower()
    assert "english" in src or "fallback" in src


def test_arch_doc_no_phi():
    src = _arch().lower()
    assert "no phi" in src


def test_arch_doc_no_vapi_credentials():
    src = _arch().lower()
    assert "vapi credentials" in src or "no vapi" in src


def test_arch_doc_production_phi_no_go():
    assert "NO-GO" in _arch() or "no-go" in _arch().lower()


def test_arch_doc_no_live_vapi_binding():
    src = _arch().lower()
    assert "no live vapi" in src or "no live" in src or "vapi binding" in src


def test_arch_doc_get_route():
    assert "GET" in _arch() and "vapi-assistant-config-pack" in _arch()
