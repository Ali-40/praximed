"""
Static contract tests for Sprint 19 / Module 147
— Live Vapi Binding Metadata Smoke Evidence.

Verifies that the smoke evidence document exists and covers all required
sections. No real secrets. No PHI. No live Vapi calls.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent.parent
_DOC = _REPO_ROOT / "docs/runtime/LIVE_VAPI_BINDING_METADATA_SMOKE_EVIDENCE.md"


def _src() -> str:
    return _DOC.read_text(encoding="utf-8")


def _low() -> str:
    return _src().lower()


# ===========================================================================
# 1. File existence
# ===========================================================================


def test_evidence_doc_exists():
    assert _DOC.exists(), f"Missing smoke evidence doc: {_DOC}"


def test_evidence_doc_non_empty():
    assert len(_src()) > 500


# ===========================================================================
# 2. Overall result
# ===========================================================================


def test_evidence_result_pass():
    assert "PASS" in _src()


def test_evidence_not_blocked_pending():
    assert "BLOCKED" not in _src()
    assert "PENDING" not in _src().split("## 15")[0]


# ===========================================================================
# 3. Sprint and commit identity
# ===========================================================================


def test_evidence_module_147():
    assert "Module 147" in _src() or "module 147" in _low()


def test_evidence_sprint_19():
    assert "Sprint 19" in _src() or "sprint 19" in _low()


def test_evidence_commit_47c6940():
    assert "47c6940" in _src()


# ===========================================================================
# 4. Frontend URL
# ===========================================================================


def test_evidence_frontend_url():
    assert "https://praximed.vercel.app/developer-console/vapi-bindings" in _src()


def test_evidence_vapi_bindings_route():
    assert "/developer-console/vapi-bindings" in _src()


# ===========================================================================
# 5. Staging clinic ID
# ===========================================================================


def test_evidence_staging_clinic_id():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _src()


def test_evidence_staging_clinic_not_real():
    low = _low()
    assert "fake" in low or "staging" in low


# ===========================================================================
# 6. clinic_vapi_bindings table
# ===========================================================================


def test_evidence_clinic_vapi_bindings_table():
    assert "clinic_vapi_bindings" in _src()


def test_evidence_migration_0005():
    assert "0005" in _src()


# ===========================================================================
# 7. Backend routes
# ===========================================================================


def test_evidence_get_vapi_bindings_route():
    assert "GET /clinics/{clinic_id}/vapi-bindings" in _src() or \
           "GET /clinics/" in _src()


def test_evidence_post_vapi_bindings_route():
    assert "POST /clinics/{clinic_id}/vapi-bindings" in _src() or \
           "POST /clinics/" in _src()


def test_evidence_patch_status_route():
    assert "PATCH /clinic-vapi-bindings/{binding_id}/status" in _src() or \
           "PATCH /clinic-vapi-bindings/" in _src()


def test_evidence_get_returns_200():
    assert "200" in _src()


def test_evidence_post_returns_201():
    assert "201" in _src()


# ===========================================================================
# 8. Reference names used — no secret values
# ===========================================================================


def test_evidence_api_key_ref_name():
    assert "VAPI_API_KEY_REF_STAGING_DEMO" in _src()


def test_evidence_webhook_ref_name():
    assert "VAPI_WEBHOOK_SECRET_REF_STAGING_DEMO" in _src()


def test_evidence_reference_names_only():
    low = _low()
    assert "reference name" in low or "reference label" in low or "reference names only" in low


def test_evidence_no_actual_secret_values():
    low = _low()
    assert "no actual secret" in low or "no actual vapi" in low or "not entered" in low


# ===========================================================================
# 9. Success confirmation
# ===========================================================================


def test_evidence_save_success_message():
    assert "Vapi binding metadata saved" in _src()


def test_evidence_status_update_success_message():
    assert "Binding status updated" in _src()


def test_evidence_binding_id_visible():
    low = _low()
    assert "binding id" in low or "binding_id" in low


# ===========================================================================
# 10. Status values
# ===========================================================================


def test_evidence_status_draft():
    assert "draft" in _src()


def test_evidence_status_configured():
    assert "configured" in _src()


def test_evidence_status_disabled():
    assert "disabled" in _src()


def test_evidence_status_draft_initial():
    assert "status: draft" in _src() or "status=draft" in _src() or "status draft" in _low()


def test_evidence_language_mode_german_first():
    assert "german_first" in _src()


# ===========================================================================
# 11. Invalid input rejection
# ===========================================================================


def test_evidence_invalid_input_rejected():
    low = _low()
    assert "rejected" in low or "rejection" in low


def test_evidence_422_validation():
    assert "422" in _src()


def test_evidence_lowercase_rejected():
    low = _low()
    assert "lowercase" in low or "sk-" in low


# ===========================================================================
# 12. production_phi_enabled false
# ===========================================================================


def test_evidence_production_phi_enabled_false():
    assert "production_phi_enabled" in _src()
    low = _low()
    assert "production_phi_enabled=false" in low or \
           "production_phi_enabled: false" in low or \
           "production_phi_enabled remains false" in low


def test_evidence_phi_false_all_responses():
    low = _low()
    assert "production_phi_enabled" in low
    assert "false" in low


# ===========================================================================
# 13. Safety boundaries
# ===========================================================================


def test_evidence_no_real_vapi_api_key():
    low = _low()
    assert "no actual vapi_api_key" in low or \
           "no actual api key" in low or \
           "no real vapi api key" in low or \
           "no actual vapi" in low


def test_evidence_no_webhook_secret_value():
    low = _low()
    assert "no actual webhook" in low or \
           "no webhook secret value" in low or \
           "no actual vapi_webhook" in low


def test_evidence_no_live_vapi_calls():
    low = _low()
    assert "no live vapi" in low or "no live api call" in low or "no live vapi api" in low


def test_evidence_no_phi():
    low = _low()
    assert "no phi" in low


def test_evidence_no_patient_data():
    low = _low()
    assert "no patient" in low or "no real patient" in low


def test_evidence_no_transcript():
    low = _low()
    assert "no transcript" in low or "transcript entered" in low or "transcript ingestion" in low


def test_evidence_no_recording_url():
    low = _low()
    assert "no recording" in low or "recording url" in low or "recording ingestion" in low


def test_evidence_production_phi_no_go():
    assert "NO-GO" in _src() or "no-go" in _low()


# ===========================================================================
# 14. What this proves / does not prove
# ===========================================================================


def test_evidence_has_proves_section():
    low = _low()
    assert "what this proves" in low


def test_evidence_has_does_not_prove_section():
    low = _low()
    assert "what this does not prove" in low


def test_evidence_proves_end_to_end():
    low = _low()
    assert "end to end" in low or "end-to-end" in low


def test_evidence_does_not_prove_production_readiness():
    low = _low()
    assert "production readiness" in low or "production phi" in low


def test_evidence_does_not_prove_dsgvo():
    low = _low()
    assert "gdpr" in low or "dsgvo" in low or "article 28" in low


# ===========================================================================
# 15. Remaining blockers
# ===========================================================================


def test_evidence_remaining_blockers_section():
    low = _low()
    assert "remaining blocker" in low


def test_evidence_c3_c8_blockers():
    src = _src()
    assert "C3" in src or "C4" in src
    assert "C8" in src


def test_evidence_production_phi_no_go_blockers():
    low = _low()
    assert "no-go" in low


# ===========================================================================
# 16. Forbidden content — no secret values, no PHI in doc
# ===========================================================================


def test_evidence_no_actual_secret_in_doc():
    src = _src()
    # "sk-..." and "vapi_live_..." may appear as *pattern descriptions* in the doc
    # (explaining what the validator rejects). What must NOT appear is an actual
    # secret-looking credential value: a long alphanumeric string following the prefix.
    import re
    assert not re.search(r"sk-[A-Za-z0-9]{10,}", src), \
        "Actual sk-... key value found in doc"
    assert not re.search(r"vapi_live_[A-Za-z0-9]{6,}", src), \
        "Actual vapi_live_... key value found in doc"


def test_evidence_no_patient_names_in_doc():
    assert "patient_name" not in _src().split("## 12")[0]


def test_evidence_no_diagnosis_language():
    low = _low()
    assert "diagnosis" not in low or "no diagnosis" in low


def test_evidence_no_medical_advice_language():
    low = _low()
    assert "medical advice" not in low or "no medical advice" in low
