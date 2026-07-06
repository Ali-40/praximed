"""
Static contract tests for Sprint 18 / Module 126C-FABEL5-FINAL — Doctor-facing interface polish.

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
# 1. Tenant identity — "Dr. Med. Alexander Huber | Innere Medizin Wien"
# ---------------------------------------------------------------------------

def test_tenant_display_has_doctor_identity():
    """tenantDisplay.ts must map the staging clinic to the premium doctor identity."""
    content = _read("lib/tenantDisplay.ts")
    assert "Dr. Med. Alexander Huber" in content
    assert "Innere Medizin Wien" in content


def test_tenant_display_maps_staging_clinic_id():
    """The staging clinic_id must be mapped in tenantDisplay.ts."""
    content = _read("lib/tenantDisplay.ts")
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in content


def test_dashboard_uses_get_clinic_display_name():
    """Dashboard must use getClinicDisplayName to render the tenant identity."""
    content = _read("app/dashboard/page.tsx")
    assert "getClinicDisplayName" in content
    assert "clinicDisplayName" in content


def test_dashboard_does_not_hardcode_doctor_name():
    """Doctor identity must come from tenantDisplay.ts, not be hardcoded in the dashboard."""
    content = _read("app/dashboard/page.tsx")
    assert "Dr. Med. Alexander Huber" not in content


# ---------------------------------------------------------------------------
# 2. Transcript panel — label and placeholder text
# ---------------------------------------------------------------------------

def test_dashboard_has_audio_transcript_and_call_recording_label():
    content = _read("app/dashboard/page.tsx")
    assert "Audio Transcript" in content and "Call Recording" in content


def test_dashboard_has_vapi_recording_ingestion_placeholder():
    """Placeholder sentence must mention Vapi recording ingestion."""
    content = _read("app/dashboard/page.tsx")
    assert "Vapi recording ingestion" in content or "recording ingestion" in content.lower()


def test_dashboard_transcript_no_fake_transcripts():
    """No invented patient transcript content in the dashboard."""
    content = _read("app/dashboard/page.tsx").lower()
    assert "patient said" not in content
    assert "doctor said" not in content


def test_dashboard_transcript_no_diagnosis():
    assert "diagnosis" not in _read("app/dashboard/page.tsx").lower()


def test_dashboard_transcript_no_medical_advice():
    assert "medical advice" not in _read("app/dashboard/page.tsx").lower()


# ---------------------------------------------------------------------------
# 3. Dev Console link removed from clinical dashboard header
# ---------------------------------------------------------------------------

def test_dashboard_header_does_not_show_dev_console_link():
    """The clinical dashboard nav must not expose the Dev Console link to doctors."""
    content = _read("app/dashboard/page.tsx")
    # A visible <a> to /developer-console must not exist in the clinical header nav.
    # The route is still accessible directly — it just should not appear in the nav.
    lines = content.splitlines()
    non_comment_lines = [ln for ln in lines if not ln.strip().startswith("//") and not ln.strip().startswith("/*") and not ln.strip().startswith("*")]
    non_comment = "\n".join(non_comment_lines)
    assert 'href="/developer-console"' not in non_comment


def test_developer_console_route_still_exists():
    """The /developer-console page route must still exist as a standalone page."""
    assert os.path.isfile(os.path.join(FRONTEND, "app", "developer-console", "page.tsx"))


def test_developer_console_has_required_safety_content():
    content = _read("app/developer-console/page.tsx")
    assert "Never paste secrets" in content or "secrets" in content.lower()
    assert "Production PHI" in content or "production phi" in content.lower()


# ---------------------------------------------------------------------------
# 4. Preserved features — regression guard
# ---------------------------------------------------------------------------

def test_dashboard_has_incoming_ai_intake():
    content = _read("app/dashboard/page.tsx")
    assert "Incoming AI Intake" in content


def test_dashboard_has_patient_registry():
    content = _read("app/dashboard/page.tsx")
    assert "Patient Registry" in content


def test_dashboard_has_intake_resolution_workspace():
    content = _read("app/dashboard/page.tsx")
    assert "Intake Resolution" in content or "workspace" in content.lower()


def test_dashboard_has_view_summary():
    content = _read("app/dashboard/page.tsx")
    assert "View summary" in content or 'data-action="view-summary"' in content


def test_dashboard_has_hide_summary():
    content = _read("app/dashboard/page.tsx")
    assert "Hide summary" in content


def test_dashboard_has_confirm_action():
    content = _read("app/dashboard/page.tsx")
    assert 'data-action="confirm"' in content


def test_dashboard_has_staging_demo():
    content = _read("app/dashboard/page.tsx")
    assert "STAGING DEMO" in content or "Staging demo" in content or "staging" in content.lower()


def test_dashboard_has_no_real_patient_data_wording():
    content = _read("app/dashboard/page.tsx")
    text = content.lower()
    assert "no real patient data" in text or "fake" in text


def test_dashboard_has_production_phi_no_go():
    content = _read("app/dashboard/page.tsx")
    assert "Production PHI" in content or "production phi" in content.lower()


def test_dashboard_preserves_data_section_appointments():
    assert 'data-section="appointments"' in _read("app/dashboard/page.tsx")


def test_dashboard_preserves_data_section_patients():
    assert 'data-section="patients"' in _read("app/dashboard/page.tsx")


def test_dashboard_preserves_data_section_notifications():
    assert 'data-section="notifications"' in _read("app/dashboard/page.tsx")


def test_dashboard_preserves_data_section_consultations():
    assert 'data-section="consultations"' in _read("app/dashboard/page.tsx")


def test_dashboard_no_session_storage():
    content = _read("app/dashboard/page.tsx")
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "sessionStorage" not in non_comment


def test_dashboard_no_local_storage():
    content = _read("app/dashboard/page.tsx")
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "localStorage" not in non_comment


def test_credentials_include_in_api():
    content = _read("lib/api.ts")
    assert "credentials" in content and "include" in content


# ---------------------------------------------------------------------------
# 5. Onboarding route still exists and contains pilot safety note
# ---------------------------------------------------------------------------

def test_onboarding_page_still_exists():
    assert os.path.isfile(os.path.join(FRONTEND, "app", "onboarding", "page.tsx"))


def test_onboarding_has_safety_note():
    content = _read("app/onboarding/page.tsx")
    text = content.lower()
    assert "production" in text and ("review" in text or "hardening" in text or "real patient" in text)


# ---------------------------------------------------------------------------
# 6. No hardcoded secrets across new files
# ---------------------------------------------------------------------------

def test_no_hardcoded_secrets():
    for rel in (
        "app/dashboard/page.tsx",
        "lib/tenantDisplay.ts",
        "app/onboarding/page.tsx",
        "app/developer-console/page.tsx",
    ):
        content = _read(rel)
        assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), f"{rel}: hardcoded JWT"
        assert "sk-" not in content, f"{rel}: API key"
