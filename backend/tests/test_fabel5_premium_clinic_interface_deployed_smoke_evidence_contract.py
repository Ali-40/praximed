"""
Static contract tests for Sprint 18 / Module 126D — Fabel 5 premium clinic interface
deployed smoke evidence.

Verifies file content only. No JS/TS runtime. No database. No network. No secrets.
No real patient data.
"""

from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
DOCS_RUNTIME = os.path.join(_REPO_ROOT, "docs", "runtime")

SMOKE_DOC = os.path.join(
    DOCS_RUNTIME,
    "FABEL5_PREMIUM_CLINIC_INTERFACE_DEPLOYED_SMOKE_EVIDENCE.md",
)


def _doc() -> str:
    with open(SMOKE_DOC, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Document exists
# ---------------------------------------------------------------------------

def test_smoke_evidence_doc_exists():
    assert os.path.isfile(SMOKE_DOC)


# ---------------------------------------------------------------------------
# 2. Module / sprint identity
# ---------------------------------------------------------------------------

def test_doc_references_module_126d():
    content = _doc()
    assert "Module 126D" in content


def test_doc_references_fabel5_final_commit():
    content = _doc()
    assert "0d0f952" in content or "126C-FABEL5-FINAL" in content


def test_doc_has_sprint_18():
    assert "Sprint 18" in _doc()


# ---------------------------------------------------------------------------
# 3. Status line
# ---------------------------------------------------------------------------

def test_doc_has_pass_status():
    content = _doc()
    assert "PASS" in content


def test_doc_not_fabricated():
    content = _doc().replace("\n", " ")
    assert "No evidence is fabricated" in content or "no fabricated" in content.lower()


# ---------------------------------------------------------------------------
# 4. /dashboard smoke checks
# ---------------------------------------------------------------------------

def test_doc_verifies_dashboard_loads():
    content = _doc()
    assert "/dashboard" in content and ("loads" in content or "PASS" in content)


def test_doc_verifies_3_column_interface():
    content = _doc()
    assert "3-column" in content or "3-panel" in content or "three" in content.lower()


def test_doc_verifies_incoming_ai_intake_queue():
    assert "Incoming AI Intake Queue" in _doc()


def test_doc_verifies_active_resolution_workspace():
    content = _doc()
    assert "Active Resolution Workspace" in content or "Resolution Workspace" in content


def test_doc_verifies_audio_transcript_and_call_recording():
    assert "Audio Transcript" in _doc() and "Call Recording" in _doc()


def test_doc_verifies_patient_registry():
    assert "Patient Registry" in _doc()


def test_doc_verifies_doctor_clinic_banner():
    content = _doc()
    assert "Dr. Med. Alexander Huber" in content
    assert "Innere Medizin Wien" in content


def test_doc_verifies_dev_console_absent_from_clinical_nav():
    content = _doc()
    assert "Dev Console" in content and ("absent" in content or "not present" in content or "not in clinical nav" in content or "absent from clinical nav" in content)


# ---------------------------------------------------------------------------
# 5. Tenant identity
# ---------------------------------------------------------------------------

def test_doc_mentions_tenant_display_helper():
    content = _doc()
    assert "tenantDisplay" in content or "getClinicDisplayName" in content


def test_doc_mentions_staging_clinic_id():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _doc()


# ---------------------------------------------------------------------------
# 6. /onboarding smoke checks
# ---------------------------------------------------------------------------

def test_doc_verifies_onboarding_loads():
    content = _doc()
    assert "/onboarding" in content and ("loads" in content or "PASS" in content)


def test_doc_verifies_review_pilot_activation_text():
    content = _doc()
    assert "Review" in content and "Pilot Activation" in content


def test_doc_verifies_no_amp_entity_in_onboarding():
    content = _doc()
    assert "Review" in content and "Pilot Activation" in content and "entity leak" in content


# ---------------------------------------------------------------------------
# 7. /developer-console smoke checks
# ---------------------------------------------------------------------------

def test_doc_verifies_developer_console_loads():
    content = _doc()
    assert "/developer-console" in content and ("loads" in content or "PASS" in content)


def test_doc_verifies_dark_admin_theme():
    content = _doc()
    assert "dark" in content.lower() and ("admin" in content.lower() or "INK" in content)


def test_doc_verifies_never_paste_secrets_guardrail():
    content = _doc()
    assert "Never paste secrets" in content or "never paste secrets" in content.lower()


def test_doc_verifies_production_phi_no_go_guardrail():
    content = _doc()
    assert "Production PHI" in content and "NO-GO" in content


def test_doc_mentions_direct_route_accessible():
    content = _doc()
    assert "direct" in content or "directly" in content


# ---------------------------------------------------------------------------
# 8. Safety boundaries
# ---------------------------------------------------------------------------

def test_doc_mentions_staging_demo():
    content = _doc()
    assert "STAGING DEMO" in content or "staging demo" in content.lower()


def test_doc_mentions_no_real_patient_data():
    content = _doc()
    assert "no real patient data" in content.lower() or "No real patient data" in content


def test_doc_confirms_production_phi_no_go():
    content = _doc()
    assert "Production PHI" in content and "NO-GO" in content


def test_doc_mentions_fake_data():
    content = _doc()
    assert "fake" in content.lower()


def test_doc_no_hardcoded_secrets():
    content = _doc()
    import re
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), "JWT found in smoke doc"
    assert "sk-" not in content, "API key found in smoke doc"


# ---------------------------------------------------------------------------
# 9. Contract test coverage reference
# ---------------------------------------------------------------------------

def test_doc_references_3071_tests():
    content = _doc()
    assert "3071" in content


def test_doc_references_polish_contract_tests():
    content = _doc()
    assert "test_doctor_facing_interface_polish_contract" in content or "126C-FABEL5-FINAL" in content


def test_doc_references_dashboard_activation_contract_tests():
    content = _doc()
    assert "test_premium_frontend_dashboard_activation_contract" in content


def test_doc_references_interface_expansion_contract_tests():
    content = _doc()
    assert "test_premium_frontend_interface_expansion_contract" in content


# ---------------------------------------------------------------------------
# 10. What This Does Not Prove — honesty section
# ---------------------------------------------------------------------------

def test_doc_has_does_not_prove_section():
    content = _doc()
    assert "does not prove" in content.lower() or "What This Does Not Prove" in content


def test_doc_acknowledges_phi_hardening_blockers():
    content = _doc()
    assert "C3" in content and "C8" in content and ("hardening" in content or "blocker" in content)


def test_doc_acknowledges_vapi_ingestion_pending():
    content = _doc()
    assert "Vapi" in content and ("pending" in content or "ingestion" in content)
