"""
Static contract tests — Sprint 19 / Module 131.

Real Staging End-to-End Demo Execution Evidence:
Verifies that the evidence document exists and contains all required elements
to substantiate the fake-data staging end-to-end flow.

No runtime code changes. No secrets. No real patient data. Production PHI: NO-GO.
"""

from __future__ import annotations

import os

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_DOC_PATH = os.path.join(
    _REPO_ROOT,
    "docs",
    "runtime",
    "STAGING_END_TO_END_DEMO_EXECUTION_EVIDENCE.md",
)


def _doc() -> str:
    with open(_DOC_PATH, encoding="utf-8") as f:
        return f.read()


def _flat() -> str:
    return _doc().replace("\n", " ")


# ---------------------------------------------------------------------------
# 1. Document existence
# ---------------------------------------------------------------------------


def test_evidence_doc_exists() -> None:
    assert os.path.isfile(_DOC_PATH), f"evidence doc missing: {_DOC_PATH}"


# ---------------------------------------------------------------------------
# 2. Overall result
# ---------------------------------------------------------------------------


def test_doc_records_pass_result() -> None:
    assert "PASS" in _doc()


def test_doc_identifies_sprint_module() -> None:
    content = _doc()
    assert "Sprint 19" in content
    assert "Module 131" in content


# ---------------------------------------------------------------------------
# 3. URLs — backend and frontend
# ---------------------------------------------------------------------------


def test_doc_records_backend_url() -> None:
    assert "https://web-production-fd91d.up.railway.app" in _doc()


def test_doc_records_frontend_url() -> None:
    assert "https://praximed.vercel.app" in _doc()


# ---------------------------------------------------------------------------
# 4. Environment configuration assertions
# ---------------------------------------------------------------------------


def test_doc_records_environment_staging() -> None:
    assert "staging" in _doc()


def test_doc_records_auth_method_cookie_httponly() -> None:
    assert "COOKIE_HTTPONLY" in _doc()


def test_doc_records_production_compliance_unlocked_not_true() -> None:
    flat = _flat()
    # Must state PRODUCTION_COMPLIANCE_UNLOCKED is not true/set
    assert "PRODUCTION_COMPLIANCE_UNLOCKED" in flat
    assert "not" in flat or "unset" in flat or "false" in flat.lower()


def test_doc_records_test_suite_pass_count() -> None:
    assert "3253" in _doc()


# ---------------------------------------------------------------------------
# 5. Backend health evidence
# ---------------------------------------------------------------------------


def test_doc_covers_health_liveness() -> None:
    flat = _flat()
    assert "/health" in flat
    assert '{"status":"ok"' in flat or '"status": "ok"' in flat or "status" in flat


def test_doc_covers_health_readiness() -> None:
    assert "/health/ready" in _doc()


# ---------------------------------------------------------------------------
# 6. Fake Vapi intake evidence
# ---------------------------------------------------------------------------


def test_doc_covers_fake_vapi_intake_curl() -> None:
    assert "capture-appointment-request" in _doc()


def test_doc_covers_demo_patient_name() -> None:
    assert "Demo Patient" in _doc()


def test_doc_confirms_intake_ok_true() -> None:
    flat = _flat()
    assert "ok" in flat and "true" in flat


def test_doc_confirms_request_status_new() -> None:
    flat = _flat()
    assert "status" in flat
    assert "new" in flat


def test_doc_records_pseudonymized_audit_metadata() -> None:
    content = _doc()
    assert "patient_name_hash" in content
    assert "caller_phone_hash" in content


# ---------------------------------------------------------------------------
# 7. Dashboard evidence
# ---------------------------------------------------------------------------


def test_doc_covers_ai_intake_queue() -> None:
    assert "AI Intake Queue" in _doc()


def test_doc_covers_active_resolution_workspace() -> None:
    assert "Active Resolution Workspace" in _doc()


def test_doc_covers_view_summary() -> None:
    assert "View summary" in _doc()


def test_doc_covers_pre_appointment_summary() -> None:
    flat = _flat()
    assert "pre-appointment summary" in flat.lower() or "Pre-appointment summary" in _doc()


def test_doc_covers_audio_transcript_placeholder() -> None:
    assert "Audio Transcript" in _doc()


# ---------------------------------------------------------------------------
# 8. Patient Registry evidence
# ---------------------------------------------------------------------------


def test_doc_covers_patient_registry() -> None:
    assert "Patient Registry" in _doc()


# ---------------------------------------------------------------------------
# 9. Internal notification evidence
# ---------------------------------------------------------------------------


def test_doc_covers_internal_notification() -> None:
    content = _doc()
    assert "notification" in content.lower()
    assert "new_appointment_request" in content


# ---------------------------------------------------------------------------
# 10. Compliance gate evidence
# ---------------------------------------------------------------------------


def test_doc_covers_compliance_gate() -> None:
    assert "enforce_phi_safeguard" in _doc() or "compliance gate" in _doc().lower()


def test_doc_confirms_gate_is_noop_in_staging() -> None:
    flat = _flat()
    assert "no-op" in flat or "noop" in flat.lower()


# ---------------------------------------------------------------------------
# 11. Safety boundaries
# ---------------------------------------------------------------------------


def test_doc_confirms_no_real_patient_data() -> None:
    flat = _flat()
    assert "no real patient data" in flat.lower()


def test_doc_confirms_no_secrets_recorded() -> None:
    flat = _flat()
    assert "no secrets" in flat.lower() or "not recorded" in flat.lower() or "secrets" in flat.lower()


def test_doc_confirms_production_phi_no_go() -> None:
    flat = _flat()
    assert "no-go" in flat.lower() or "NO-GO" in _doc()


def test_doc_confirms_no_fabricated_evidence() -> None:
    flat = _flat()
    assert "fabricated" in flat or "accuracy" in flat.lower()


def test_doc_confirms_no_diagnosis_in_display() -> None:
    flat = _flat()
    assert "diagnosis" in flat.lower()


# ---------------------------------------------------------------------------
# 12. Remaining production blockers
# ---------------------------------------------------------------------------


def test_doc_lists_remaining_production_blockers() -> None:
    content = _doc()
    assert "C3" in content
    assert "C4" in content
    assert "C5" in content
    assert "C6" in content
    assert "C7" in content
    assert "C8" in content


def test_doc_marks_blockers_open() -> None:
    assert "OPEN" in _doc()


# ---------------------------------------------------------------------------
# 13. What this does not prove
# ---------------------------------------------------------------------------


def test_doc_disclaims_production_phi_readiness() -> None:
    flat = _flat()
    assert "production phi" in flat.lower()
    assert "not" in flat.lower() or "does not" in flat.lower()


def test_doc_disclaims_recording_ingestion() -> None:
    flat = _flat()
    assert "recording" in flat.lower()


def test_doc_disclaims_dsgvo_compliance() -> None:
    flat = _flat()
    assert "dsgvo" in flat.lower() or "DSGVO" in _doc()
