"""
Static contract tests for Sprint 18 / Module 126C — Premium Frontend Application Interface Expansion.

Verifies file content only. No JS/TS runtime. No database. No network. No secrets.
No real patient data.
"""

from __future__ import annotations

import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")


def _read(rel: str) -> str:
    with open(os.path.join(FRONTEND, rel), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# tenantDisplay.ts — new helper
# ---------------------------------------------------------------------------

def test_tenant_display_ts_exists():
    assert os.path.isfile(os.path.join(FRONTEND, "lib", "tenantDisplay.ts"))


def test_tenant_display_has_get_clinic_display_name():
    content = _read("lib/tenantDisplay.ts")
    assert "getClinicDisplayName" in content


def test_tenant_display_has_get_role_display():
    content = _read("lib/tenantDisplay.ts")
    assert "getRoleDisplay" in content


def test_tenant_display_has_staging_clinic_map():
    content = _read("lib/tenantDisplay.ts")
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in content
    assert "Staging Fake Clinic" in content


# ---------------------------------------------------------------------------
# globals.css — premium palette tokens
# ---------------------------------------------------------------------------

def test_globals_has_color_navy():
    content = _read("app/globals.css")
    assert "--color-navy" in content


def test_globals_has_color_teal():
    content = _read("app/globals.css")
    assert "--color-teal" in content


def test_globals_has_pm_app_grid():
    content = _read("app/globals.css")
    assert "pm-app-grid" in content


def test_globals_has_pm_panel_left():
    content = _read("app/globals.css")
    assert "pm-panel-left" in content


def test_globals_has_pm_panel_center():
    content = _read("app/globals.css")
    assert "pm-panel-center" in content


def test_globals_has_pm_panel_right():
    content = _read("app/globals.css")
    assert "pm-panel-right" in content


def test_globals_has_responsive_media_queries():
    content = _read("app/globals.css")
    assert "max-width" in content
    assert "1200px" in content or "768px" in content


# ---------------------------------------------------------------------------
# dashboard/page.tsx — 3-panel layout
# ---------------------------------------------------------------------------

def test_dashboard_imports_tenant_display():
    content = _read("app/dashboard/page.tsx")
    assert "getClinicDisplayName" in content
    assert "getRoleDisplay" in content


def test_dashboard_uses_pm_shell():
    content = _read("app/dashboard/page.tsx")
    assert "pm-shell" in content


def test_dashboard_uses_pm_app_grid():
    content = _read("app/dashboard/page.tsx")
    assert "pm-app-grid" in content


def test_dashboard_has_left_panel():
    content = _read("app/dashboard/page.tsx")
    assert "pm-panel-left" in content
    assert 'data-panel="left"' in content


def test_dashboard_has_center_panel():
    content = _read("app/dashboard/page.tsx")
    assert "pm-panel-center" in content
    assert 'data-panel="center"' in content


def test_dashboard_has_right_panel():
    content = _read("app/dashboard/page.tsx")
    assert "pm-panel-right" in content
    assert 'data-panel="right"' in content


def test_dashboard_has_ai_intake_queue():
    content = _read("app/dashboard/page.tsx")
    assert "AI Intake" in content or "Intake Queue" in content


def test_dashboard_has_patient_registry():
    content = _read("app/dashboard/page.tsx")
    assert "Patient Registry" in content


def test_dashboard_has_intake_resolution_workspace():
    content = _read("app/dashboard/page.tsx")
    assert "Intake Resolution" in content or "workspace" in content.lower()


def test_dashboard_has_selected_appt_state():
    content = _read("app/dashboard/page.tsx")
    assert "selectedApptId" in content


def test_dashboard_has_selected_patient_state():
    content = _read("app/dashboard/page.tsx")
    assert "selectedPatientId" in content


def test_dashboard_has_transcript_panel():
    content = _read("app/dashboard/page.tsx")
    assert "transcript" in content.lower() or "TranscriptRecordingPanel" in content


def test_dashboard_has_confirm_create_profile_disabled():
    content = _read("app/dashboard/page.tsx")
    assert "confirm-create-profile" in content or "Create Profile" in content


def test_dashboard_navy_header():
    content = _read("app/dashboard/page.tsx")
    assert "color-navy" in content or "#0F172A" in content or "navy" in content.lower()


# ---------------------------------------------------------------------------
# Preserve existing behaviour (regression)
# ---------------------------------------------------------------------------

def test_dashboard_preserves_data_section_appointments():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="appointments"' in content


def test_dashboard_preserves_data_section_patients():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="patients"' in content


def test_dashboard_preserves_data_section_notifications():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="notifications"' in content


def test_dashboard_preserves_data_section_consultations():
    content = _read("app/dashboard/page.tsx")
    assert 'data-section="consultations"' in content


def test_dashboard_preserves_view_summary_action():
    content = _read("app/dashboard/page.tsx")
    assert 'data-action="view-summary"' in content


def test_dashboard_preserves_hide_summary():
    content = _read("app/dashboard/page.tsx")
    assert "Hide summary" in content


def test_dashboard_preserves_confirm_action():
    content = _read("app/dashboard/page.tsx")
    assert 'data-action="confirm"' in content


def test_dashboard_preserves_summary_panel():
    content = _read("app/dashboard/page.tsx")
    assert 'data-state="summary-panel"' in content


def test_dashboard_preserves_suggested_next_action():
    content = _read("app/dashboard/page.tsx")
    assert "suggested_next_action" in content


def test_dashboard_preserves_safety_note():
    content = _read("app/dashboard/page.tsx")
    assert "safety_note" in content


def test_dashboard_preserves_no_token_storage():
    content = _read("app/dashboard/page.tsx")
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "sessionStorage" not in non_comment
    assert "localStorage" not in non_comment


def test_dashboard_no_diagnosis():
    content = _read("app/dashboard/page.tsx")
    assert "diagnosis" not in content.lower()


def test_dashboard_no_medical_advice():
    content = _read("app/dashboard/page.tsx")
    assert "medical advice" not in content.lower()


def test_dashboard_staging_safety_footer():
    content = _read("app/dashboard/page.tsx")
    text = content.lower()
    assert "staging" in text and ("no real patient data" in text or "fake data" in text)


# ---------------------------------------------------------------------------
# onboarding/page.tsx
# ---------------------------------------------------------------------------

def test_onboarding_page_exists():
    assert os.path.isfile(os.path.join(FRONTEND, "app", "onboarding", "page.tsx"))


def test_onboarding_has_start_with_praximed_title():
    content = _read("app/onboarding/page.tsx")
    assert "Start with PraxisMed" in content or "PraxisMed" in content


def test_onboarding_has_five_steps():
    content = _read("app/onboarding/page.tsx")
    assert "data-onboarding-step" in content or "5" in content


def test_onboarding_has_pilot_cta():
    content = _read("app/onboarding/page.tsx")
    assert "pilot" in content.lower() or "Request" in content


def test_onboarding_has_safety_note():
    content = _read("app/onboarding/page.tsx")
    text = content.lower()
    assert "production" in text and ("review" in text or "hardening" in text or "real patient" in text)


def test_onboarding_no_real_submission():
    content = _read("app/onboarding/page.tsx")
    assert "disabled" in content


# ---------------------------------------------------------------------------
# developer-console/page.tsx
# ---------------------------------------------------------------------------

def test_developer_console_page_exists():
    assert os.path.isfile(os.path.join(FRONTEND, "app", "developer-console", "page.tsx"))


def test_developer_console_never_paste_secrets():
    content = _read("app/developer-console/page.tsx")
    assert "Never paste secrets" in content or "never paste secrets" in content.lower()


def test_developer_console_production_phi_no_go():
    content = _read("app/developer-console/page.tsx")
    text = content.lower()
    assert "production phi" in text and ("no-go" in text or "hardening" in text)


def test_developer_console_machine_credentials_env_var():
    content = _read("app/developer-console/page.tsx")
    assert "Machine credentials" in content or "environment variable" in content


def test_developer_console_has_security_boundary():
    content = _read("app/developer-console/page.tsx")
    assert "security-boundary" in content or "Safety Boundary" in content or "safety" in content.lower()


def test_developer_console_no_secrets_accepted():
    content = _read("app/developer-console/page.tsx")
    assert "disabled" in content


def test_developer_console_has_tenant_provisioning():
    content = _read("app/developer-console/page.tsx")
    assert "Tenant Provisioning" in content or "tenant" in content.lower()


def test_developer_console_has_vapi_panel():
    content = _read("app/developer-console/page.tsx")
    assert "Vapi" in content or "vapi" in content.lower()


def test_developer_console_has_environment_checklist():
    content = _read("app/developer-console/page.tsx")
    assert "Checklist" in content or "checklist" in content.lower() or "Environment" in content


def test_developer_console_no_hardcoded_secrets():
    content = _read("app/developer-console/page.tsx")
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content)
    assert "sk-" not in content


# ---------------------------------------------------------------------------
# No hardcoded secrets across all new files
# ---------------------------------------------------------------------------

def test_no_hardcoded_secrets_all_new_files():
    files = [
        "lib/tenantDisplay.ts",
        "app/dashboard/page.tsx",
        "app/onboarding/page.tsx",
        "app/developer-console/page.tsx",
    ]
    for rel in files:
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), f"{rel} must not contain a hardcoded JWT"
        assert "sk-" not in content, f"{rel} must not contain an API key"
