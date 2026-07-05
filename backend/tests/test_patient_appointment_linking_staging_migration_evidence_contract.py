"""
Static contract tests for Module 121B — Staging Patient and Appointment
Linking Migration Evidence.

These tests inspect the evidence document on disk without any database
connection or network request.  No secrets.  No real patient data.
"""

from __future__ import annotations

from pathlib import Path

EVIDENCE_DOC = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "runtime"
    / "PATIENT_APPOINTMENT_LINKING_STAGING_MIGRATION_EVIDENCE.md"
)


def _text() -> str:
    assert EVIDENCE_DOC.is_file(), f"Evidence doc not found: {EVIDENCE_DOC}"
    return EVIDENCE_DOC.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Evidence document exists
# ---------------------------------------------------------------------------

def test_evidence_doc_exists():
    assert EVIDENCE_DOC.is_file(), "PATIENT_APPOINTMENT_LINKING_STAGING_MIGRATION_EVIDENCE.md must exist"


# ---------------------------------------------------------------------------
# 2. Overall result is PASS
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_pass():
    assert "PASS" in _text(), "Evidence doc must contain PASS"


# ---------------------------------------------------------------------------
# 3. Commit 02e8896 referenced
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_commit():
    assert "02e8896" in _text(), "Evidence doc must reference commit 02e8896"


# ---------------------------------------------------------------------------
# 4. Migration 0003 referenced
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_migration_0003():
    assert "0003_patient_id_appt_requests" in _text(), (
        "Evidence doc must mention 0003_patient_id_appt_requests"
    )


# ---------------------------------------------------------------------------
# 5. patient_id column referenced
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_patient_id_column():
    assert "appointment_requests.patient_id" in _text(), (
        "Evidence doc must mention appointment_requests.patient_id"
    )


# ---------------------------------------------------------------------------
# 6. Index referenced
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_index():
    assert "idx_appointment_requests_clinic_patient" in _text(), (
        "Evidence doc must mention idx_appointment_requests_clinic_patient"
    )


# ---------------------------------------------------------------------------
# 7. Migration command referenced
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_migration_command():
    assert "python backend/scripts/run_migrations.py" in _text(), (
        "Evidence doc must mention python backend/scripts/run_migrations.py"
    )


# ---------------------------------------------------------------------------
# 8. Direct Vapi endpoint smoke referenced
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_vapi_endpoint_smoke():
    text = _text().lower()
    assert "vapi" in text and "smoke" in text, (
        "Evidence doc must mention direct Vapi endpoint smoke"
    )


# ---------------------------------------------------------------------------
# 9. Fake patient name referenced
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_linked_test_patient():
    assert "Linked Test Patient" in _text(), (
        "Evidence doc must mention Linked Test Patient"
    )


# ---------------------------------------------------------------------------
# 10. patient_id in DB verification section
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_patient_id():
    assert "patient_id" in _text(), "Evidence doc must mention patient_id"


# ---------------------------------------------------------------------------
# 11. Joined patients row mentioned
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_joined_patients_row():
    assert "joined patients row" in _text().lower(), (
        "Evidence doc must mention joined patients row"
    )


# ---------------------------------------------------------------------------
# 12. source vapi mentioned
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_source_vapi():
    assert "source" in _text().lower() and "vapi" in _text().lower(), (
        "Evidence doc must mention source vapi"
    )


# ---------------------------------------------------------------------------
# 13. status new mentioned
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_status_new():
    assert "status" in _text().lower() and "new" in _text().lower(), (
        "Evidence doc must mention status new"
    )


# ---------------------------------------------------------------------------
# 14. action_required true mentioned
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_action_required_true():
    assert "action_required" in _text().lower(), (
        "Evidence doc must mention action_required"
    )


# ---------------------------------------------------------------------------
# 15. clinic_id scoped linking mentioned
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_clinic_id_scoped_linking():
    text = _text().lower()
    assert "clinic_id" in text, "Evidence doc must mention clinic_id scoped linking"


# ---------------------------------------------------------------------------
# 16. Pre-appointment summary PENDING
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_pre_appointment_summary_pending():
    text = _text().lower()
    assert "pre-appointment summary" in text, (
        "Evidence doc must mention pre-appointment summary as pending"
    )


# ---------------------------------------------------------------------------
# 17. Doctor notification PENDING
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_doctor_notification_pending():
    text = _text().lower()
    assert "doctor" in text and "notification" in text, (
        "Evidence doc must mention doctor notification as pending"
    )


# ---------------------------------------------------------------------------
# 18. No real patient data
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_no_real_patient_data():
    text = _text().lower()
    assert "no real patient data" in text, (
        "Evidence doc must state no real patient data"
    )


# ---------------------------------------------------------------------------
# 19. No production PHI
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_no_production_phi():
    text = _text().lower()
    assert "production phi" in text, (
        "Evidence doc must state no production PHI"
    )


# ---------------------------------------------------------------------------
# 20. No secrets recorded
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_no_secrets_recorded():
    text = _text().lower()
    assert "no" in text and "secret" in text, (
        "Evidence doc must state no secrets recorded"
    )


# ---------------------------------------------------------------------------
# 21. Module 122 referenced as next
# ---------------------------------------------------------------------------

def test_evidence_doc_mentions_module_122():
    text = _text()
    assert "Module 122" in text, (
        "Evidence doc must mention Module 122 — Pre-Appointment Summary Foundation as next"
    )
