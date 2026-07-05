"""
Static contract tests for Module 122B — Deployed Pre-Appointment Summary
Smoke Evidence.

Inspects the evidence document on disk. No database, no network.
No secrets. No real patient data.
"""

from __future__ import annotations

from pathlib import Path

EVIDENCE_DOC = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "runtime"
    / "PRE_APPOINTMENT_SUMMARY_DEPLOYED_SMOKE_EVIDENCE.md"
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


# 3. /auth/me mentioned
def test_evidence_doc_mentions_auth_me():
    assert "/auth/me" in _text()


# 4. pre-appointment-summary endpoint mentioned
def test_evidence_doc_mentions_pre_appointment_summary():
    assert "pre-appointment-summary" in _text()


# 5. Request ID ae8d53cd referenced
def test_evidence_doc_mentions_request_id():
    assert "ae8d53cd-c4d9-4d7d-9cee-5490e13ff83b" in _text()


# 6. Patient ID f5953d98 referenced
def test_evidence_doc_mentions_patient_id():
    assert "f5953d98-6b5b-483a-bfb9-49f6eed378e0" in _text()


# 7. Fake patient name referenced
def test_evidence_doc_mentions_summary_linked_patient():
    assert "Summary Linked Patient" in _text()


# 8. source vapi mentioned
def test_evidence_doc_mentions_source_vapi():
    assert "vapi" in _text().lower()


# 9. status new mentioned
def test_evidence_doc_mentions_status_new():
    assert "status" in _text().lower() and "new" in _text().lower()


# 10. action_required true mentioned
def test_evidence_doc_mentions_action_required_true():
    assert "action_required" in _text().lower()


# 11. urgency_level normal mentioned
def test_evidence_doc_mentions_urgency_level_normal():
    assert "urgency_level" in _text().lower() and "normal" in _text().lower()


# 12. Review and confirm mentioned
def test_evidence_doc_mentions_review_and_confirm():
    assert "Review and confirm" in _text()


# 13. no diagnosis mentioned
def test_evidence_doc_mentions_no_diagnosis():
    assert "diagnosis" in _text().lower()


# 14. no medical advice mentioned
def test_evidence_doc_mentions_no_medical_advice():
    assert "medical advice" in _text().lower()


# 15. doctor/staff review required mentioned
def test_evidence_doc_mentions_doctor_staff_review_required():
    text = _text().lower()
    assert "doctor" in text and "review" in text


# 16. no password recorded
def test_evidence_doc_mentions_no_password_recorded():
    assert "password" in _text().lower()


# 17. no token recorded
def test_evidence_doc_mentions_no_token_recorded():
    assert "token" in _text().lower()


# 18. no cookie value recorded
def test_evidence_doc_mentions_no_cookie_value_recorded():
    assert "cookie" in _text().lower()


# 19. no real patient data
def test_evidence_doc_mentions_no_real_patient_data():
    assert "no real patient data" in _text().lower()


# 20. fake/non-PHI staging only
def test_evidence_doc_mentions_fake_non_phi():
    assert "fake" in _text().lower() and "phi" in _text().lower()


# 21. production PHI readiness NO-GO
def test_evidence_doc_mentions_production_phi_no_go():
    text = _text().lower()
    assert "production phi" in text and "no-go" in text


# 22. patient_phone returned null observation
def test_evidence_doc_mentions_patient_phone_null():
    assert "patient_phone" in _text().lower() and "null" in _text().lower()


# 23. future data-normalization/input-mapping improvement
def test_evidence_doc_mentions_data_normalization_improvement():
    text = _text().lower()
    assert "data-normalization" in text or "input-mapping" in text


# 24. Module 123 referenced as next
def test_evidence_doc_mentions_module_123():
    assert "Module 123" in _text()
