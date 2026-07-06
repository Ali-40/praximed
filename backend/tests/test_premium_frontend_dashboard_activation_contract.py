"""
Static contract tests for Sprint 18 / Module 126C-FIX — Activate Premium 3-Panel Dashboard Interface.

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
# Colour constants — must appear inline in the dashboard source so the
# 3-panel shell renders even when CSS variables haven't loaded.
# ---------------------------------------------------------------------------

def test_dashboard_has_navy_hex_inline():
    """#0F172A (Deep Midnight Navy) must be hardcoded in the dashboard source."""
    content = _read("app/dashboard/page.tsx")
    assert "#0F172A" in content or "#0f172a" in content.lower()


def test_dashboard_has_teal_hex_inline():
    """#0D9488 (Crisp Teal) must be hardcoded in the dashboard source."""
    content = _read("app/dashboard/page.tsx")
    assert "#0D9488" in content or "#0d9488" in content.lower()


# ---------------------------------------------------------------------------
# 3-panel structure labels
# ---------------------------------------------------------------------------

def test_dashboard_has_incoming_ai_intake():
    content = _read("app/dashboard/page.tsx")
    assert "Incoming AI Intake" in content


def test_dashboard_has_intake_resolution_workspace():
    content = _read("app/dashboard/page.tsx")
    assert "Intake Resolution Workspace" in content


def test_dashboard_has_patient_registry():
    content = _read("app/dashboard/page.tsx")
    assert "Patient Registry" in content


def test_dashboard_has_audio_transcript_and_call_recording():
    content = _read("app/dashboard/page.tsx")
    assert "Audio Transcript" in content and "Call Recording" in content


# ---------------------------------------------------------------------------
# Self-contained layout CSS (embedded — not solely relying on globals.css)
# ---------------------------------------------------------------------------

def test_dashboard_has_embedded_grid_css():
    content = _read("app/dashboard/page.tsx")
    assert "display:grid" in content or "display: grid" in content or "display:grid" in content.replace(" ", "")


def test_dashboard_has_embedded_responsive_breakpoints():
    content = _read("app/dashboard/page.tsx")
    assert "max-width" in content and ("1200px" in content or "768px" in content)


def test_dashboard_has_three_column_template():
    content = _read("app/dashboard/page.tsx")
    assert "264px" in content or "grid-template-columns" in content


# ---------------------------------------------------------------------------
# Panel data attributes
# ---------------------------------------------------------------------------

def test_dashboard_has_left_panel():
    content = _read("app/dashboard/page.tsx")
    assert 'data-panel="left"' in content


def test_dashboard_has_center_panel():
    content = _read("app/dashboard/page.tsx")
    assert 'data-panel="center"' in content


def test_dashboard_has_right_panel():
    content = _read("app/dashboard/page.tsx")
    assert 'data-panel="right"' in content


# ---------------------------------------------------------------------------
# Core UI elements
# ---------------------------------------------------------------------------

def test_dashboard_has_view_summary():
    content = _read("app/dashboard/page.tsx")
    assert "View summary" in content


def test_dashboard_has_hide_summary():
    content = _read("app/dashboard/page.tsx")
    assert "Hide summary" in content


def test_dashboard_has_confirm_action():
    content = _read("app/dashboard/page.tsx")
    assert 'data-action="confirm"' in content


def test_dashboard_has_confirm_create_profile():
    content = _read("app/dashboard/page.tsx")
    assert "Create Profile" in content and "disabled" in content


def test_dashboard_has_staging_demo():
    content = _read("app/dashboard/page.tsx")
    assert "Staging demo" in content or "staging" in content.lower()


def test_dashboard_has_fake_data_wording():
    content = _read("app/dashboard/page.tsx")
    text = content.lower()
    assert "fake-data" in text or "fake data" in text


def test_dashboard_has_no_real_patient_data_wording():
    content = _read("app/dashboard/page.tsx")
    assert "No real patient data" in content or "no real patient data" in content.lower()


def test_dashboard_has_production_phi_wording():
    content = _read("app/dashboard/page.tsx")
    assert "Production PHI" in content or "production phi" in content.lower()


# ---------------------------------------------------------------------------
# Tenant display helper
# ---------------------------------------------------------------------------

def test_dashboard_imports_tenant_display_helper():
    content = _read("app/dashboard/page.tsx")
    assert "getClinicDisplayName" in content


def test_dashboard_uses_clinic_display_name_in_state():
    content = _read("app/dashboard/page.tsx")
    assert "clinicDisplayName" in content


# ---------------------------------------------------------------------------
# Preserved data-section attributes (regression from Module 126)
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


def test_dashboard_preserves_summary_panel():
    content = _read("app/dashboard/page.tsx")
    assert 'data-state="summary-panel"' in content


def test_dashboard_preserves_suggested_next_action():
    content = _read("app/dashboard/page.tsx")
    assert "suggested_next_action" in content


def test_dashboard_preserves_safety_note():
    content = _read("app/dashboard/page.tsx")
    assert "safety_note" in content


# ---------------------------------------------------------------------------
# Security / token storage invariants
# ---------------------------------------------------------------------------

def test_dashboard_no_session_storage():
    content = _read("app/dashboard/page.tsx")
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "sessionStorage" not in non_comment


def test_dashboard_no_local_storage():
    content = _read("app/dashboard/page.tsx")
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "localStorage" not in non_comment


def test_dashboard_no_diagnosis():
    assert "diagnosis" not in _read("app/dashboard/page.tsx").lower()


def test_dashboard_no_medical_advice():
    assert "medical advice" not in _read("app/dashboard/page.tsx").lower()


def test_credentials_include_in_api():
    content = _read("lib/api.ts")
    assert "credentials" in content and "include" in content


# ---------------------------------------------------------------------------
# No hardcoded secrets
# ---------------------------------------------------------------------------

def test_no_hardcoded_secrets():
    for rel in ("app/dashboard/page.tsx", "lib/api.ts", "lib/tenantDisplay.ts"):
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), f"{rel}: hardcoded JWT"
        assert "sk-" not in content, f"{rel}: API key"


# ---------------------------------------------------------------------------
# /onboarding and /developer-console still intact
# ---------------------------------------------------------------------------

def test_onboarding_page_still_intact():
    content = _read("app/onboarding/page.tsx")
    assert "Start with PraxisMed" in content or "PraxisMed" in content
    assert "pilot" in content.lower()


def test_developer_console_still_intact():
    content = _read("app/developer-console/page.tsx")
    assert "Never paste secrets" in content or "secrets" in content.lower()
    assert "Production PHI" in content or "production phi" in content.lower()
