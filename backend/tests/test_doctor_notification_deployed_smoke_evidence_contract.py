"""
Static contract tests for Module 124 — Deployed Doctor Notification Smoke Evidence.

Inspects the evidence document on disk. No database, no network.
No secrets. No real patient data.
"""

from __future__ import annotations

from pathlib import Path

EVIDENCE_DOC = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "runtime"
    / "DOCTOR_NOTIFICATION_DEPLOYED_SMOKE_EVIDENCE.md"
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


# 3. Deployed commit b74a7ee referenced
def test_evidence_doc_mentions_commit():
    assert "b74a7ee" in _text()


# 4. 2709/2709 tests referenced
def test_evidence_doc_mentions_test_count():
    assert "2709/2709" in _text()


# 5. notification_count=1 referenced
def test_evidence_doc_mentions_notification_count():
    assert "notification_count=1" in _text()


# 6. Notification id 5d84860d referenced
def test_evidence_doc_mentions_notification_id():
    assert "5d84860d-0adc-45bb-995b-955e388d46e5" in _text()


# 7. channel internal referenced
def test_evidence_doc_mentions_channel_internal():
    assert "internal" in _text()


# 8. notification_type appointment_request referenced
def test_evidence_doc_mentions_notification_type():
    assert "appointment_request" in _text()


# 9. title New appointment request referenced
def test_evidence_doc_mentions_title():
    assert "New appointment request" in _text()


# 10. Fake patient name referenced
def test_evidence_doc_mentions_patient_name():
    assert "Doctor Notification Patient" in _text()


# 11. Fake reason referenced
def test_evidence_doc_mentions_reason():
    assert "Routine checkup doctor notification smoke" in _text()


# 12. Review and confirm referenced
def test_evidence_doc_mentions_review_and_confirm():
    assert "Review and confirm" in _text()


# 13. status pending referenced
def test_evidence_doc_mentions_status_pending():
    assert "pending" in _text()


# 14. related_resource_type appointment_requests referenced
def test_evidence_doc_mentions_related_resource_type():
    assert "appointment_requests" in _text()


# 15. related_resource_id a7d25ac1 referenced
def test_evidence_doc_mentions_related_resource_id():
    assert "a7d25ac1-31a8-4179-904e-6a06617e040f" in _text()


# 16. no external delivery mentioned
def test_evidence_doc_mentions_no_external_delivery():
    text = _text().lower()
    assert "no external delivery" in text or "external delivery" in text


# 17. no diagnosis mentioned
def test_evidence_doc_mentions_no_diagnosis():
    assert "diagnosis" in _text().lower()


# 18. no medical advice mentioned
def test_evidence_doc_mentions_no_medical_advice():
    assert "medical advice" in _text().lower()


# 19. no real patient data mentioned
def test_evidence_doc_mentions_no_real_patient_data():
    assert "no real patient data" in _text().lower()


# 20. production PHI NO-GO mentioned
def test_evidence_doc_mentions_production_phi_no_go():
    text = _text().lower()
    assert "production phi" in text and "no-go" in text


# 21. no secrets recorded mentioned
def test_evidence_doc_mentions_no_secrets_recorded():
    assert "no secrets recorded" in _text().lower()


# 22. dashboard notification UI not proven mentioned
def test_evidence_doc_mentions_dashboard_notification_ui_pending():
    text = _text().lower()
    assert "dashboard notification" in text and ("pending" in text or "not proven" in text)


# 23. Fabel 5 premium UI/UX referenced
def test_evidence_doc_mentions_fabel_5():
    assert "Fabel 5" in _text()


# 24. Module 125 referenced as next
def test_evidence_doc_mentions_module_125():
    assert "Module 125" in _text()
