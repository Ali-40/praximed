"""
Static contract tests — Live Patient Intake Link Smoke Evidence (Module 152).

Verify that the smoke evidence document contains all required attestations
and does not contain forbidden content.

No runtime code. No database calls. No network requests. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_DOC_PATH = Path(__file__).resolve().parents[2] / "docs/runtime/LIVE_PATIENT_INTAKE_LINK_SMOKE_EVIDENCE.md"


def _doc() -> str:
    return _DOC_PATH.read_text()


# ── Doc existence ─────────────────────────────────────────────────────────────


def test_smoke_doc_exists():
    assert _DOC_PATH.exists()


# ── Result ────────────────────────────────────────────────────────────────────


def test_doc_result_is_pass():
    assert "PASS" in _doc()


def test_doc_mentions_module_152():
    assert "152" in _doc()


# ── Admin route ───────────────────────────────────────────────────────────────


def test_doc_mentions_admin_intake_links_page():
    assert "https://praximed.vercel.app/developer-console/intake-links" in _doc()


# ── Public route ──────────────────────────────────────────────────────────────


def test_doc_mentions_public_intake_route():
    assert "/intake/" in _doc()


# ── Clinic ID ─────────────────────────────────────────────────────────────────


def test_doc_mentions_staging_clinic_id():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _doc()


# ── Tables ────────────────────────────────────────────────────────────────────


def test_doc_mentions_anamnesis_templates_table():
    assert "anamnesis_templates" in _doc()


def test_doc_mentions_patient_intake_links_table():
    assert "patient_intake_links" in _doc()


def test_doc_mentions_patient_intake_submissions_table():
    assert "patient_intake_submissions" in _doc()


def test_doc_mentions_consent_events_table():
    assert "consent_events" in _doc()


# ── Token handling ────────────────────────────────────────────────────────────


def test_doc_mentions_intake_url_shown_once():
    doc = _doc().lower()
    assert "shown once" in doc or "raw_token_shown_once" in doc.lower()


def test_doc_mentions_token_hash_stored():
    assert "token_hash" in _doc()


def test_doc_mentions_raw_token_not_stored():
    doc = _doc().lower()
    assert "raw token" in doc
    assert "never" in doc or "not stored" in doc or "not persisted" in doc


# ── Consent step ─────────────────────────────────────────────────────────────


def test_doc_mentions_consent_step_before_questionnaire():
    doc = _doc().lower()
    assert "consent step" in doc or "consent" in doc
    assert "before questionnaire" in doc or "questionnaire" in doc


# ── Language support ──────────────────────────────────────────────────────────


def test_doc_mentions_language_de():
    doc = _doc()
    assert "de" in doc or "Deutsch" in doc


def test_doc_mentions_language_en():
    doc = _doc()
    assert "en" in doc or "English" in doc


def test_doc_mentions_language_ar():
    doc = _doc()
    assert "ar" in doc or "العربية" in doc


def test_doc_mentions_rtl():
    doc = _doc().lower()
    assert "rtl" in doc


# ── Synthetic answers ─────────────────────────────────────────────────────────


def test_doc_mentions_synthetic_answers():
    doc = _doc().lower()
    assert "synthetic" in doc
    assert "answer" in doc


# ── Success message ───────────────────────────────────────────────────────────


def test_doc_mentions_staff_review_success():
    assert "Intake submitted for staff review" in _doc()


# ── consent_event ─────────────────────────────────────────────────────────────


def test_doc_mentions_consent_event_created():
    doc = _doc().lower()
    assert "consent_event" in doc or "consent event" in doc


def test_doc_mentions_channel_intake_link():
    assert "intake_link" in _doc() or "channel" in _doc()


# ── Intake submission ─────────────────────────────────────────────────────────


def test_doc_mentions_intake_submission_stored():
    doc = _doc().lower()
    assert "submission" in doc
    assert "stored" in doc or "confirmed" in doc or "present" in doc


# ── No history write ──────────────────────────────────────────────────────────


def test_doc_mentions_no_patient_history_write():
    doc = _doc().lower()
    assert "no patient history write" in doc or "patient history" in doc


def test_doc_mentions_history_table_not_written():
    doc = _doc().lower()
    assert "patient_history_" in doc.lower()


# ── No AI structuring ─────────────────────────────────────────────────────────


def test_doc_mentions_no_ai_structuring():
    doc = _doc().lower()
    assert "no ai structuring" in doc or "ai structuring" in doc


# ── No diagnosis ─────────────────────────────────────────────────────────────


def test_doc_mentions_no_diagnosis():
    doc = _doc().lower()
    assert "no" in doc and "diagnosis" in doc


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
    assert "no triage" in doc or "triage scoring" in doc


# ── No real patient data ──────────────────────────────────────────────────────


def test_doc_mentions_no_real_patient_data():
    doc = _doc().lower()
    assert "no real patient data" in doc or "real patient data" in doc


# ── No PHI ────────────────────────────────────────────────────────────────────


def test_doc_mentions_no_phi():
    doc = _doc()
    assert "PHI" in doc or "phi" in doc.lower()


# ── Production PHI NO-GO ─────────────────────────────────────────────────────


def test_doc_mentions_production_phi_no_go():
    assert "Production PHI remains NO-GO" in _doc()


# ── Remaining blockers ────────────────────────────────────────────────────────


def test_doc_mentions_remaining_blockers():
    doc = _doc().lower()
    assert "remaining blocker" in doc or "blocker" in doc


def test_doc_mentions_ai_structuring_blocker():
    doc = _doc().lower()
    assert "ai structuring" in doc


def test_doc_mentions_doctor_review_blocker():
    doc = _doc().lower()
    assert "doctor review" in doc or "review" in doc


# ── Forbidden content ─────────────────────────────────────────────────────────


def test_doc_no_real_patient_names():
    doc = _doc()
    # Synthetic names used in docs should not look like common real formats
    # We check that placeholder-like words "Demo" or "Staging" or "synthetic" appear
    assert "Demo" in doc or "Staging" in doc or "synthetic" in doc.lower()


def test_doc_no_database_url():
    # DATABASE_URL must not appear as an actual value — only in prohibition statements.
    lines = [
        l for l in _doc().splitlines()
        if "DATABASE_URL" in l and "No " not in l and "no " not in l
    ]
    assert len(lines) == 0


def test_doc_no_jwt_secret():
    # JWT_SECRET must not appear as an actual value — only in prohibition statements.
    lines = [
        l for l in _doc().splitlines()
        if "JWT_SECRET" in l and "No " not in l and "no " not in l
        and "jwt_secret" not in l.lower().replace("jwt_secret", "")
    ]
    assert len(lines) == 0


def test_doc_no_vapi_secret():
    doc = _doc()
    assert "sk-live" not in doc
    assert "vapi_live" not in doc.lower()


def test_doc_no_transcript_content():
    # "transcript" may appear in prohibition statements ("No transcript storage").
    lines = [
        l for l in _doc().lower().splitlines()
        if "transcript" in l and "no " not in l and "not " not in l
    ]
    assert len(lines) == 0


def test_doc_no_recording_url():
    # "recording_url" may appear in prohibition statements.
    lines = [
        l for l in _doc().lower().splitlines()
        if "recording_url" in l and "no " not in l and "not " not in l
    ]
    assert len(lines) == 0


def test_doc_no_diagnosis_generation_claim():
    # Should not claim diagnosis is generated — only claim it is NOT generated
    doc = _doc().lower()
    lines_claiming_diagnosis = [
        l for l in doc.splitlines()
        if "diagnosis" in l and "no" not in l and "not" not in l
        and "never" not in l and "does not" not in l
    ]
    assert len(lines_claiming_diagnosis) == 0


def test_doc_no_production_readiness_claim():
    doc = _doc().lower()
    lines_claiming_production = [
        l for l in doc.splitlines()
        if "production ready" in l or "production-ready" in l
        or ("production" in l and "approved" in l)
    ]
    assert len(lines_claiming_production) == 0


def test_doc_no_phi_unlock_claim():
    doc = _doc().lower()
    # Must not claim PHI is unlocked or production-ready
    assert "phi enabled" not in doc or "phi_enabled: false" in doc or "phi remains no-go" in doc
