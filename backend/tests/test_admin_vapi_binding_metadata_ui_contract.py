"""
Static contract tests — Sprint 19 / Module 146 — Admin Vapi Binding Metadata UI.

Verifies:
- /developer-console/vapi-bindings page exists with the dark admin theme
- Loads/creates binding metadata using secret reference names only
- Status update flow (draft/configured/disabled/revoked)
- Safety copy: no live Vapi calls, no secrets, no PHI, production PHI NO-GO
- api.ts helpers use credentials: "include"; no browser token storage
- No secret-value inputs, no forbidden fields, no real secrets anywhere

No live Vapi API calls. No actual Vapi secrets. No PHI.
Production PHI remains NO-GO.
"""

from __future__ import annotations

import os
import re

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_FRONTEND = os.path.join(_REPO_ROOT, "frontend")
_DOCS = os.path.join(_REPO_ROOT, "docs")

_PAGE_REL = os.path.join("app", "developer-console", "vapi-bindings", "page.tsx")


def _read(rel: str) -> str:
    with open(os.path.join(_FRONTEND, rel), encoding="utf-8") as f:
        return f.read()


def _read_doc(rel: str) -> str:
    with open(os.path.join(_DOCS, rel), encoding="utf-8") as f:
        return f.read()


def _page() -> str:
    return _read(_PAGE_REL)


def _api() -> str:
    return _read(os.path.join("lib", "api.ts"))


def _console() -> str:
    return _read(os.path.join("app", "developer-console", "page.tsx"))


# ---------------------------------------------------------------------------
# 1. Page existence and identity
# ---------------------------------------------------------------------------


def test_vapi_bindings_page_exists() -> None:
    assert os.path.isfile(os.path.join(_FRONTEND, _PAGE_REL))


def test_page_title() -> None:
    assert "Vapi Binding Metadata" in _page()


def test_page_subtitle() -> None:
    assert "Internal secret-reference configuration" in _page()


def test_page_admin_staging_badge() -> None:
    assert "ADMIN / STAGING" in _page()


def test_page_dark_console_theme() -> None:
    content = _page()
    assert "#0B132B" in content   # ink background
    assert "#008080" in content   # teal accents
    assert "#E63946" in content   # red guardrails
    assert "#FFB703" in content   # amber warnings


def test_page_header_safety_warning() -> None:
    content = _page()
    assert "Reference names only. No Vapi secrets are stored or transmitted." in content
    assert "No live Vapi API calls" in content
    assert "Production PHI remains NO-GO" in content


# ---------------------------------------------------------------------------
# 2. Load flow
# ---------------------------------------------------------------------------


def test_page_has_clinic_id_input() -> None:
    content = _page()
    assert "Clinic ID" in content
    assert "clinic-id-input" in content


def test_page_has_load_bindings_button() -> None:
    assert "Load bindings" in _page()


def test_page_helper_text_and_staging_example() -> None:
    content = _page()
    assert "Paste a provisioned clinic_id or the staging clinic_id" in content
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in content


def test_page_uses_api_helpers() -> None:
    content = _page()
    assert "fetchClinicVapiBindings" in content
    assert "createClinicVapiBinding" in content
    assert "updateClinicVapiBindingStatus" in content


def test_page_safe_error_messages() -> None:
    content = _page()
    assert "Admin session required. Please log in first." in content
    assert "Clinic not found or no access." in content
    assert "Could not load Vapi binding metadata." in content


def test_page_empty_state() -> None:
    assert "No Vapi binding found for this clinic." in _page()


# ---------------------------------------------------------------------------
# 3. Binding fields displayed / editable
# ---------------------------------------------------------------------------


def test_page_has_required_reference_fields() -> None:
    content = _page()
    assert "api_key_secret_ref" in content
    assert "webhook_secret_ref" in content


def test_page_shows_optional_metadata_fields() -> None:
    content = _page()
    assert "assistant_id" in content
    assert "phone_number_id" in content
    assert "vapi_project_id" in content
    assert "assistant_config_version" in content


def test_page_has_language_modes() -> None:
    content = _page()
    assert "language_mode" in content
    assert "german_first" in content
    assert "english_first" in content
    assert "bilingual_auto" in content


def test_page_has_all_statuses() -> None:
    content = _page()
    assert "status" in content
    for s in ("draft", "configured", "disabled", "revoked"):
        assert f"'{s}'" in content or f'"{s}"' in content, f"missing status {s!r}"


def test_page_reference_name_placeholders() -> None:
    content = _page()
    assert "VAPI_API_KEY_REF_CLINIC_DEMO" in content
    assert "VAPI_WEBHOOK_SECRET_REF_CLINIC_DEMO" in content


def test_page_reference_only_helper_copy() -> None:
    content = _page()
    assert "environment-variable reference names only" in content
    assert "never secret values" in content


def test_page_client_side_secret_ref_guard() -> None:
    # Client-side pattern mirrors the backend: uppercase env-var reference names only.
    assert "SECRET_REF_PATTERN" in _page()
    assert "A-Z0-9_" in _page()


# ---------------------------------------------------------------------------
# 4. Create and status-update flows
# ---------------------------------------------------------------------------


def test_page_create_success_copy() -> None:
    assert "Vapi binding metadata saved" in _page()


def test_page_secret_values_not_allowed_copy() -> None:
    assert "Secret values are not allowed" in _page()


def test_page_status_update_flow() -> None:
    content = _page()
    assert "Update status" in content
    assert "Binding status updated." in content


# ---------------------------------------------------------------------------
# 5. Safety copy
# ---------------------------------------------------------------------------


def test_page_safety_boundary_copy() -> None:
    content = _page()
    assert "No live Vapi API calls" in content
    assert "No Vapi secrets" in content
    assert "No webhook secret values" in content
    assert "No PHI" in content
    assert "No patient data" in content
    assert "No production activation" in content
    assert "Production PHI remains NO-GO" in content


# ---------------------------------------------------------------------------
# 6. Forbidden content on the bindings page
# ---------------------------------------------------------------------------


def test_page_has_no_secret_value_inputs() -> None:
    content = _page()
    # No input labelled as an actual Vapi API key or webhook secret value.
    assert "Vapi API key value" not in content
    assert 'placeholder="VAPI_API_KEY"' not in content
    assert "webhook secret value field" not in content
    assert "type=\"password\"" not in content


def test_page_has_no_forbidden_fields() -> None:
    content = _page()
    assert "DATABASE_URL" not in content
    assert "JWT" not in content
    assert "patient_name" not in content
    assert "transcript" not in content.lower()
    assert "recording_url" not in content


def test_page_no_browser_token_storage() -> None:
    content = _page()
    assert "sessionStorage" not in content
    assert "localStorage" not in content


def test_page_no_diagnosis_language() -> None:
    text = _page().lower()
    assert "diagnosis" not in text
    assert "medical advice" not in text


# ---------------------------------------------------------------------------
# 7. api.ts helpers
# ---------------------------------------------------------------------------


def test_api_helpers_defined() -> None:
    api = _api()
    assert "export async function fetchClinicVapiBindings" in api
    assert "export async function createClinicVapiBinding" in api
    assert "export async function updateClinicVapiBindingStatus" in api


def test_api_helpers_call_correct_endpoints() -> None:
    api = _api()
    assert "/vapi-bindings" in api
    assert "/clinic-vapi-bindings/" in api
    assert "/status" in api


def test_api_helpers_use_cookie_credentials() -> None:
    api = _api()
    # All binding helpers go through apiFetch, which sets credentials: "include".
    assert "credentials" in api and "include" in api
    assert api.count("apiFetch(") >= 3


def test_api_binding_interface_reference_names_only() -> None:
    api = _api()
    assert "ClinicVapiBinding" in api
    assert "api_key_secret_ref" in api
    assert "webhook_secret_ref" in api
    assert "production_phi_enabled" in api


def test_api_no_browser_token_storage() -> None:
    api = _api()
    assert "sessionStorage" not in api
    assert "localStorage" not in api


# ---------------------------------------------------------------------------
# 8. Developer console navigation
# ---------------------------------------------------------------------------


def test_console_links_to_vapi_bindings() -> None:
    console = _console()
    assert "/developer-console/vapi-bindings" in console
    assert "Vapi Binding Metadata" in console


def test_console_link_card_has_safety_copy() -> None:
    console = _console()
    assert "secret reference names only" in console.lower()
    assert "Production PHI remains NO-GO" in console


# ---------------------------------------------------------------------------
# 9. No hardcoded secrets or real data in touched files
# ---------------------------------------------------------------------------


def test_no_hardcoded_secrets_or_real_data() -> None:
    for rel in (
        _PAGE_REL,
        os.path.join("lib", "api.ts"),
        os.path.join("app", "developer-console", "page.tsx"),
    ):
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), f"{rel}: hardcoded JWT-like token"
        assert "sk-" not in content, f"{rel}: API key marker"
        assert "vapi_live_" not in content, f"{rel}: live credential marker"
        for marker in ("SVNR", "sozialversicherung", "DOB:"):
            assert marker not in content, f"{rel}: real patient data marker {marker!r}"


# ---------------------------------------------------------------------------
# 10. Docs
# ---------------------------------------------------------------------------


def test_arch_doc_exists() -> None:
    assert os.path.isfile(
        os.path.join(_DOCS, "architecture", "ADMIN_VAPI_BINDING_METADATA_UI.md")
    )


def test_arch_doc_covers_required_topics() -> None:
    text = _read_doc(os.path.join("architecture", "ADMIN_VAPI_BINDING_METADATA_UI.md"))
    lower = text.lower()
    assert "vapi binding metadata" in lower
    assert "reference names" in lower
    assert "no live vapi" in lower
    assert "no phi" in lower
    assert "no-go" in lower
    assert "/developer-console/vapi-bindings" in text
    assert "secret" in lower and "environment variable" in lower


def test_current_state_mentions_module_146() -> None:
    text = _read_doc(os.path.join("claude", "CURRENT_STATE.md"))
    assert "Module 146" in text
    assert "Vapi Binding Metadata UI" in text or "Vapi binding metadata UI" in text


def test_next_module_points_to_future_module() -> None:
    text = _read_doc(os.path.join("claude", "NEXT_MODULE.md"))
    assert "Module 1" in text
