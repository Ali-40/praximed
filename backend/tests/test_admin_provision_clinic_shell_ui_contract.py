"""
Sprint 19 / Module 136 — Admin Provision Clinic Shell UI

Static contract tests: read raw TSX/TypeScript source and verify the
provisioning button, safety copy, error states, and api.ts helper
are present and meet the specification.

No imports, no database, no network. All assertions are substring checks.
"""

from pathlib import Path

PAGE_PATH = Path(
    "frontend/app/developer-console/onboarding-requests/page.tsx"
)
API_PATH = Path("frontend/lib/api.ts")
ARCH_DOC_PATH = Path("docs/architecture/ADMIN_PROVISION_CLINIC_SHELL_UI.md")


def _page() -> str:
    return PAGE_PATH.read_text(encoding="utf-8")


def _api() -> str:
    return API_PATH.read_text(encoding="utf-8")


def _arch() -> str:
    return ARCH_DOC_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_page_file_exists():
    assert PAGE_PATH.exists(), f"Missing page: {PAGE_PATH}"


def test_api_file_exists():
    assert API_PATH.exists(), f"Missing api.ts: {API_PATH}"


def test_arch_doc_exists():
    assert ARCH_DOC_PATH.exists(), f"Missing arch doc: {ARCH_DOC_PATH}"


# ---------------------------------------------------------------------------
# ProvisionState type
# ---------------------------------------------------------------------------


def test_provision_state_type_defined():
    assert "ProvisionState" in _page()


def test_provision_state_idle():
    assert "'idle'" in _page()


def test_provision_state_provisioning():
    assert "'provisioning'" in _page()


def test_provision_state_provisioned():
    assert "'provisioned'" in _page()


def test_provision_state_error():
    # 'error' appears in multiple types — just check ProvisionState context
    src = _page()
    assert "ProvisionState" in src and "'error'" in src


# ---------------------------------------------------------------------------
# ProvisionResult interface
# ---------------------------------------------------------------------------


def test_provision_result_interface_defined():
    assert "ProvisionResult" in _page()


def test_provision_result_has_clinic_id():
    assert "clinic_id" in _page()


def test_provision_result_has_clinic_name():
    assert "clinic_name" in _page()


def test_provision_result_has_clinic_slug():
    assert "clinic_slug" in _page()


def test_provision_result_has_preferred_language():
    assert "preferred_language" in _page()


def test_provision_result_has_production_phi_enabled():
    assert "production_phi_enabled" in _page()


def test_provision_result_has_already_provisioned():
    assert "already_provisioned" in _page()


# ---------------------------------------------------------------------------
# State variables
# ---------------------------------------------------------------------------


def test_provision_state_state_var():
    assert "provisionState" in _page()


def test_provision_result_state_var():
    assert "provisionResult" in _page()


def test_provision_error_state_var():
    assert "provisionError" in _page()


# ---------------------------------------------------------------------------
# handleProvision function
# ---------------------------------------------------------------------------


def test_handle_provision_function_defined():
    assert "handleProvision" in _page()


def test_provision_calls_provision_clinic_shell_endpoint():
    assert "/provision-clinic-shell" in _page()


def test_provision_uses_post_method():
    src = _page()
    assert "provision-clinic-shell" in src
    assert "'POST'" in src


def test_provision_uses_credentials_include():
    src = _page()
    assert "provision-clinic-shell" in src
    assert "credentials: 'include'" in src


def test_provision_handles_401():
    assert "401" in _page()


def test_provision_handles_403():
    assert "403" in _page()


def test_provision_handles_409():
    assert "409" in _page()


def test_provision_admin_session_required_error():
    assert "Admin session required" in _page()


def test_provision_must_be_pilot_approved_error():
    assert "Request must be pilot_approved before provisioning" in _page()


def test_provision_generic_error():
    assert "Provisioning failed. Please retry or check backend logs" in _page()


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------


def test_provision_clinic_shell_button_text():
    assert "Provision Clinic Shell" in _page()


def test_button_disabled_when_not_pilot_approved():
    src = _page()
    assert "pilot_approved" in src
    assert "disabled" in src


def test_button_disabled_during_provisioning():
    src = _page()
    assert "provisionState === 'provisioning'" in src


def test_button_label_during_provisioning():
    assert "Provisioning…" in _page()


# ---------------------------------------------------------------------------
# Disabled helper text
# ---------------------------------------------------------------------------


def test_set_status_to_pilot_approved_helper_text():
    assert "Set status to pilot_approved before provisioning" in _page()


def test_pilot_approved_condition_gates_button():
    src = _page()
    # The page must gate the button on pilot_approved status
    assert "selected.status !== 'pilot_approved'" in src or \
           "selected.status === 'pilot_approved'" in src


# ---------------------------------------------------------------------------
# Section header
# ---------------------------------------------------------------------------


def test_clinic_shell_provisioning_section_header():
    assert "Clinic Shell Provisioning" in _page()


# ---------------------------------------------------------------------------
# Safety copy
# ---------------------------------------------------------------------------


def test_safety_copy_no_production_phi():
    src = _page()
    assert "does not activate production PHI" in src or \
           "does not enable production PHI" in src or \
           "No production PHI" in src


def test_safety_copy_no_vapi_credentials():
    src = _page()
    assert "no Vapi credentials" in src or \
           "Vapi credentials" in src


def test_safety_copy_no_patient_records():
    src = _page()
    assert "no patient records" in src or \
           "patient records" in src


def test_safety_copy_production_phi_remains_no_go():
    assert "Production PHI remains NO-GO" in _page()


# ---------------------------------------------------------------------------
# Success state
# ---------------------------------------------------------------------------


def test_success_shows_clinic_shell_provisioned():
    assert "Clinic shell provisioned" in _page()


def test_success_shows_clinic_id():
    src = _page()
    assert "clinic_id" in src
    assert "provisionResult" in src


def test_success_shows_clinic_name():
    src = _page()
    assert "clinic_name" in src


def test_success_shows_clinic_slug():
    src = _page()
    assert "clinic_slug" in src


def test_success_shows_preferred_language():
    src = _page()
    assert "preferred_language" in src


def test_success_message_production_phi_disabled():
    assert "Production PHI remains disabled" in _page()


# ---------------------------------------------------------------------------
# Already provisioned
# ---------------------------------------------------------------------------


def test_already_provisioned_branch():
    assert "already_provisioned" in _page()


def test_already_provisioned_shows_clinic_id():
    src = _page()
    assert "already_provisioned" in src
    assert "clinic_id" in src


# ---------------------------------------------------------------------------
# Reset on request selection
# ---------------------------------------------------------------------------


def test_select_request_resets_provision_state():
    src = _page()
    # selectRequest must reset provisionState
    assert "setProvisionState('idle')" in src


def test_select_request_resets_provision_result():
    src = _page()
    assert "setProvisionResult(null)" in src


def test_select_request_resets_provision_error():
    src = _page()
    assert "setProvisionError(null)" in src


# ---------------------------------------------------------------------------
# Storage safety
# ---------------------------------------------------------------------------


def test_no_session_storage():
    assert "sessionStorage" not in _page()


def test_no_local_storage():
    assert "localStorage" not in _page()


# ---------------------------------------------------------------------------
# No sensitive credential fields in page
# ---------------------------------------------------------------------------


def test_no_vapi_api_key_field():
    assert "Vapi API key" not in _page()
    assert "vapi_api_key" not in _page()


def test_no_webhook_secret_field():
    assert "webhook_secret" not in _page()
    assert "Webhook Secret" not in _page()


def test_no_database_url_exposed():
    assert "DATABASE_URL" not in _page()


# ---------------------------------------------------------------------------
# api.ts — provisionClinicShell helper
# ---------------------------------------------------------------------------


def test_api_has_provision_clinic_shell():
    assert "provisionClinicShell" in _api()


def test_api_provision_calls_provision_clinic_shell_path():
    assert "/provision-clinic-shell" in _api()


def test_api_provision_uses_post():
    src = _api()
    assert "provisionClinicShell" in src
    assert "'POST'" in src


def test_api_provision_uses_credentials_include():
    # apiFetch always uses credentials: 'include'
    assert "credentials: 'include'" in _api()


def test_api_provision_result_interface_defined():
    assert "ClinicShellProvisionResult" in _api()


def test_api_provision_result_has_clinic_id():
    assert "clinic_id" in _api()


def test_api_provision_result_has_production_phi_enabled():
    assert "production_phi_enabled" in _api()


def test_api_provision_result_has_already_provisioned():
    assert "already_provisioned" in _api()


def test_api_provision_no_vapi_credentials():
    src = _api()
    assert "vapi_api_key" not in src or "provisionClinicShell" in src
    # Specifically: provisionClinicShell must not reference vapi credentials
    lines = [ln for ln in src.splitlines() if "provisionClinicShell" in ln or "provision-clinic-shell" in ln]
    for ln in lines:
        assert "vapi_api_key" not in ln


def test_api_no_session_storage():
    assert "sessionStorage" not in _api()


def test_api_no_local_storage():
    assert "localStorage" not in _api()


# ---------------------------------------------------------------------------
# Arch doc checks
# ---------------------------------------------------------------------------


def test_arch_doc_module_136():
    assert "136" in _arch()


def test_arch_doc_provision_clinic_shell():
    assert "provision" in _arch().lower()


def test_arch_doc_pilot_approved():
    assert "pilot_approved" in _arch()


def test_arch_doc_no_production_phi():
    src = _arch()
    assert "production PHI" in src or "production_phi" in src


def test_arch_doc_no_vapi_credentials():
    assert "Vapi" in _arch() or "vapi" in _arch()
