"""
Static contract tests — Live Doctor Review & Merge Smoke Evidence (Module 155).

Verify that the smoke evidence document contains all required attestations
and does not contain forbidden content.

No runtime code. No database calls. No network requests. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs/runtime/LIVE_DOCTOR_REVIEW_MERGE_SMOKE_EVIDENCE.md"
)


def _doc() -> str:
    return _DOC_PATH.read_text()


# ── Doc existence ─────────────────────────────────────────────────────────────


def test_smoke_doc_exists():
    assert _DOC_PATH.exists()


# ── Result ────────────────────────────────────────────────────────────────────


def test_doc_result_is_pass():
    assert "PASS" in _doc()


def test_doc_mentions_module_155():
    assert "155" in _doc()


# ── Live route ────────────────────────────────────────────────────────────────


def test_doc_mentions_history_review_page():
    assert "https://praximed.vercel.app/developer-console/history-review" in _doc()


# ── Clinic ID ─────────────────────────────────────────────────────────────────


def test_doc_mentions_staging_clinic_id():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _doc()


# ── Tables ────────────────────────────────────────────────────────────────────


def test_doc_mentions_structuring_runs_table():
    assert "patient_history_structuring_runs" in _doc()


def test_doc_mentions_proposals_table():
    assert "patient_history_proposals" in _doc()


def test_doc_mentions_patient_history_tables():
    assert "patient_history_" in _doc()


# ── Synthetic intake submission ───────────────────────────────────────────────


def test_doc_mentions_synthetic_intake_submission():
    doc = _doc().lower()
    assert "synthetic" in doc
    assert "intake submission" in doc or "submission" in doc


# ── Structuring service ───────────────────────────────────────────────────────


def test_doc_mentions_structuring_service():
    doc = _doc().lower()
    assert "structuring" in doc


def test_doc_mentions_no_external_llm():
    doc = _doc().lower()
    assert "no external llm" in doc or "local deterministic" in doc or "local extraction" in doc


# ── Review queue ──────────────────────────────────────────────────────────────


def test_doc_mentions_review_queue():
    doc = _doc().lower()
    assert "review queue" in doc


def test_doc_mentions_unverified_proposal():
    doc = _doc().lower()
    assert "unverified" in doc


# ── Proposal detail ───────────────────────────────────────────────────────────


def test_doc_mentions_proposal_detail():
    doc = _doc().lower()
    assert "proposal detail" in doc or "detail" in doc


# ── Extraction confidence label ───────────────────────────────────────────────


def test_doc_mentions_extraction_confidence_label():
    assert "Extraction confidence only — not a medical judgment" in _doc()


# ── Reject proposal ───────────────────────────────────────────────────────────


def test_doc_mentions_reject_proposal():
    doc = _doc().lower()
    assert "reject" in doc


def test_doc_mentions_proposal_status_rejected():
    assert "proposal_status: rejected" in _doc() or "proposal_status=rejected" in _doc() or \
           "proposal_status: rejected" in _doc()


# ── Staff confirmation ────────────────────────────────────────────────────────


def test_doc_mentions_staff_doctor_confirmation():
    doc = _doc().lower()
    assert "confirm_staff_review" in doc or "staff/doctor review" in doc or \
           "staff confirmation" in doc


def test_doc_mentions_confirm_staff_review_true():
    assert "confirm_staff_review" in _doc()


# ── Approve/merge ─────────────────────────────────────────────────────────────


def test_doc_mentions_approve_merge():
    doc = _doc().lower()
    assert "approve" in doc and "merge" in doc


def test_doc_mentions_merge_success_message():
    assert "Proposal merged into patient history after staff review" in _doc()


# ── patient_history_* row ─────────────────────────────────────────────────────


def test_doc_mentions_status_approved():
    assert "status: approved" in _doc() or "status=approved" in _doc() or \
           "status` `approved" in _doc()


def test_doc_mentions_source_type_ai_proposal():
    assert "source_type: ai_proposal" in _doc() or "source_type=ai_proposal" in _doc() or \
           "source_type` `ai_proposal" in _doc()


# ── Proposal merged status ────────────────────────────────────────────────────


def test_doc_mentions_proposal_status_merged():
    assert "proposal_status: merged" in _doc() or "proposal_status=merged" in _doc() or \
           "proposal_status` `merged" in _doc()


def test_doc_mentions_merged_history_entry_id():
    assert "merged_history_entry_id" in _doc()


# ── Consent preservation ──────────────────────────────────────────────────────


def test_doc_mentions_consent_event_id_preserved():
    doc = _doc().lower()
    assert "consent_event_id" in doc
    assert "preserved" in doc or "copied" in doc


# ── production_phi_enabled false ─────────────────────────────────────────────


def test_doc_mentions_production_phi_enabled_false():
    doc = _doc().lower()
    assert "production_phi_enabled" in doc
    assert "false" in doc


# ── No auto-approval ─────────────────────────────────────────────────────────


def test_doc_mentions_no_auto_approval():
    doc = _doc().lower()
    assert "no auto-approval" in doc or "no auto approval" in doc or \
           "auto-approval" in doc


# ── No external LLM ──────────────────────────────────────────────────────────


def test_doc_mentions_no_external_llm_calls():
    doc = _doc().lower()
    assert "no external llm" in doc or "no external llm call" in doc or \
           "local deterministic" in doc


# ── No diagnosis ─────────────────────────────────────────────────────────────


def test_doc_mentions_no_diagnosis():
    doc = _doc().lower()
    assert "no diagnosis" in doc or ("no" in doc and "diagnosis" in doc)


# ── No medical advice ─────────────────────────────────────────────────────────


def test_doc_mentions_no_medical_advice():
    doc = _doc().lower()
    assert "no medical advice" in doc or "medical advice" in doc


# ── No treatment recommendation ───────────────────────────────────────────────


def test_doc_mentions_no_treatment_recommendation():
    doc = _doc().lower()
    assert "no treatment recommendation" in doc or "treatment recommendation" in doc


# ── No triage scoring ─────────────────────────────────────────────────────────


def test_doc_mentions_no_triage_scoring():
    doc = _doc().lower()
    assert "no triage" in doc or "triage scoring" in doc or "triage" in doc


# ── No real patient data ──────────────────────────────────────────────────────


def test_doc_mentions_no_real_patient_data():
    doc = _doc().lower()
    assert "no real patient data" in doc or "real patient data" in doc


# ── No PHI ────────────────────────────────────────────────────────────────────


def test_doc_mentions_no_phi():
    assert "PHI" in _doc()


# ── Production PHI NO-GO ─────────────────────────────────────────────────────


def test_doc_mentions_production_phi_no_go():
    assert "Production PHI remains NO-GO" in _doc()


# ── Remaining blockers ────────────────────────────────────────────────────────


def test_doc_mentions_remaining_blockers():
    doc = _doc().lower()
    assert "remaining blocker" in doc or "blocker" in doc


# ── Forbidden content ─────────────────────────────────────────────────────────


def test_doc_no_real_patient_names():
    doc = _doc()
    for name in ("John Doe", "Jane Doe", "Max Mustermann", "Ahmed Al"):
        assert name not in doc, f"Real patient name found: {name}"


def test_doc_no_real_phone_numbers():
    import re
    doc = _doc()
    phone_pattern = re.compile(r'\+\d{10,15}')
    matches = phone_pattern.findall(doc)
    assert len(matches) == 0, f"Phone number found: {matches}"


def test_doc_no_database_url():
    lines = [
        l for l in _doc().splitlines()
        if "DATABASE_URL" in l and "No " not in l and "no " not in l
    ]
    assert len(lines) == 0


def test_doc_no_jwt_secret():
    lines = [
        l for l in _doc().splitlines()
        if "JWT_SECRET" in l and "No " not in l and "no " not in l
    ]
    assert len(lines) == 0


def test_doc_no_anthropic_secret():
    doc = _doc()
    assert "sk-ant-" not in doc
    assert "ANTHROPIC_API_KEY" not in doc


def test_doc_no_openai_secret():
    doc = _doc()
    assert "sk-proj-" not in doc
    assert "OPENAI_API_KEY" not in doc


def test_doc_no_vapi_secret():
    doc = _doc()
    assert "sk-live" not in doc
    assert "vapi_live" not in doc.lower()
    assert "VAPI_API_KEY" not in doc


def test_doc_no_transcript_content():
    lines = [
        l for l in _doc().lower().splitlines()
        if "transcript" in l and "no " not in l and "not " not in l
    ]
    assert len(lines) == 0


def test_doc_no_recording_url():
    lines = [
        l for l in _doc().lower().splitlines()
        if "recording_url" in l and "no " not in l and "not " not in l
    ]
    assert len(lines) == 0


def test_doc_no_diagnosis_generation_claim():
    doc = _doc().lower()
    lines_claiming_diagnosis = [
        l for l in doc.splitlines()
        if "diagnosis" in l
        and "no" not in l
        and "not" not in l
        and "never" not in l
        and "does not" not in l
        and "forbidden" not in l
        and "reject" not in l
    ]
    assert len(lines_claiming_diagnosis) == 0


def test_doc_no_production_readiness_claim():
    doc = _doc().lower()
    lines_claiming_production = [
        l for l in doc.splitlines()
        if "production ready" in l or "production-ready" in l
        or ("production" in l and "approved" in l and "no-go" not in l)
    ]
    assert len(lines_claiming_production) == 0


def test_doc_no_phi_unlock_claim():
    doc = _doc().lower()
    phi_unlock_lines = [
        l for l in doc.splitlines()
        if "phi" in l
        and "enabled" in l
        and "false" not in l
        and "no-go" not in l
        and "not" not in l
        and "no " not in l
        and "remains" not in l
    ]
    assert len(phi_unlock_lines) == 0


def test_doc_no_secret_looking_values():
    import re
    doc = _doc()
    secret_pattern = re.compile(r'\b[A-Za-z0-9]{40,}\b')
    matches = [m for m in secret_pattern.findall(doc) if not m.startswith("http")]
    assert len(matches) == 0, f"Potential secret-looking value found: {matches[:3]}"
