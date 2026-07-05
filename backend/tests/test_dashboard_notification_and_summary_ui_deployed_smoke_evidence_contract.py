"""
Static contract tests for Module 125B — Deployed Dashboard Notification and Summary UI Smoke Evidence.

Inspects the evidence document on disk. No database, no network.
No secrets. No real patient data.
"""

from __future__ import annotations

from pathlib import Path

EVIDENCE_DOC = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "runtime"
    / "DASHBOARD_NOTIFICATION_AND_SUMMARY_UI_DEPLOYED_SMOKE_EVIDENCE.md"
)


def _text() -> str:
    assert EVIDENCE_DOC.is_file(), f"Evidence doc not found: {EVIDENCE_DOC}"
    return EVIDENCE_DOC.read_text(encoding="utf-8")


# 1. Evidence document exists
def test_evidence_doc_exists():
    assert EVIDENCE_DOC.is_file()


# 2. Overall result is PASS
def test_evidence_doc_mentions_pass():
    assert "PASS" in _text()


# 3. Deployed commit ab08b7a referenced
def test_evidence_doc_mentions_commit():
    assert "ab08b7a" in _text()


# 4. Frontend URL referenced
def test_evidence_doc_mentions_frontend_url():
    assert "https://praximed.vercel.app" in _text()


# 5. Dashboard URL referenced
def test_evidence_doc_mentions_dashboard_url():
    assert "/dashboard" in _text()


# 6. Appointments count visible referenced
def test_evidence_doc_mentions_appointments_count():
    text = _text().lower()
    assert "appointments count" in text or "appointments count visible" in text or "appointments" in text


# 7. Doctor Notification Patient referenced
def test_evidence_doc_mentions_doctor_notification_patient():
    assert "Doctor Notification Patient" in _text()


# 8. View summary referenced
def test_evidence_doc_mentions_view_summary():
    assert "View summary" in _text()


# 9. Hide summary referenced
def test_evidence_doc_mentions_hide_summary():
    assert "Hide summary" in _text()


# 10. Patient field referenced
def test_evidence_doc_mentions_patient_field():
    assert "Patient" in _text()


# 11. Type field referenced
def test_evidence_doc_mentions_type_field():
    assert "Type" in _text()


# 12. Reason field referenced
def test_evidence_doc_mentions_reason_field():
    assert "Reason" in _text()


# 13. Urgency field referenced
def test_evidence_doc_mentions_urgency_field():
    assert "Urgency" in _text()


# 14. Prior visits field referenced
def test_evidence_doc_mentions_prior_visits_field():
    assert "Prior visits" in _text()


# 15. Suggested action field referenced
def test_evidence_doc_mentions_suggested_action_field():
    assert "Suggested action" in _text()


# 16. Safety note field referenced
def test_evidence_doc_mentions_safety_note_field():
    assert "Safety note" in _text()


# 17. No medical advice mentioned
def test_evidence_doc_mentions_no_medical_advice():
    assert "medical advice" in _text().lower()


# 18. No diagnosis mentioned
def test_evidence_doc_mentions_no_diagnosis():
    assert "diagnosis" in _text().lower()


# 19. Doctor/staff review required mentioned
def test_evidence_doc_mentions_doctor_staff_review():
    text = _text().lower()
    assert "doctor" in text and ("review" in text or "staff" in text)


# 20. Confirm referenced
def test_evidence_doc_mentions_confirm():
    assert "Confirm" in _text()


# 21. No real patient data mentioned
def test_evidence_doc_mentions_no_real_patient_data():
    assert "no real patient data" in _text().lower()


# 22. Production PHI NO-GO mentioned
def test_evidence_doc_mentions_production_phi_no_go():
    text = _text().lower()
    assert "production phi" in text and "no-go" in text


# 23. No secrets recorded mentioned
def test_evidence_doc_mentions_no_secrets_recorded():
    assert "no secrets recorded" in _text().lower()


# 24. Fabel 5 premium UI/UX referenced
def test_evidence_doc_mentions_fabel_5():
    assert "Fabel 5" in _text()


# 25. Module 126 Fabel 5 referenced as next
def test_evidence_doc_mentions_module_126():
    assert "Module 126" in _text()
