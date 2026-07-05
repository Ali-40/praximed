"""
Static contract tests for Sprint 18 / Module 126B — Deployed Fabel 5 Premium Dashboard Smoke Evidence.

Inspects the evidence document on disk. No database, no network.
No secrets. No real patient data.
"""

from __future__ import annotations

from pathlib import Path

EVIDENCE_DOC = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "runtime"
    / "FABEL_5_PREMIUM_DASHBOARD_DEPLOYED_SMOKE_EVIDENCE.md"
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


# 3. Deployed commit 36b91be referenced
def test_evidence_doc_mentions_commit():
    assert "36b91be" in _text()


# 4. Vercel Ready referenced
def test_evidence_doc_mentions_vercel_ready():
    assert "Ready" in _text()


# 5. Frontend URL referenced
def test_evidence_doc_mentions_frontend_url():
    assert "https://praximed.vercel.app" in _text()


# 6. Dashboard URL referenced
def test_evidence_doc_mentions_dashboard_url():
    assert "/dashboard" in _text()


# 7. Premium header referenced
def test_evidence_doc_mentions_premium_header():
    text = _text()
    assert "PraxisMed" in text and ("header" in text.lower() or "Clinic Dashboard" in text)


# 8. Staging demo badge referenced
def test_evidence_doc_mentions_staging_demo():
    assert "Staging demo" in _text()


# 9. Clinic Overview heading referenced
def test_evidence_doc_mentions_clinic_overview():
    assert "Clinic Overview" in _text()


# 10. Fake-data staging subtitle referenced
def test_evidence_doc_mentions_fake_data_staging():
    text = _text().lower()
    assert "fake-data staging" in text or "fake data" in text


# 11. Appointments 9 referenced
def test_evidence_doc_mentions_appointments_9():
    assert "9" in _text() and "Appointment" in _text()


# 12. Patients 6 referenced
def test_evidence_doc_mentions_patients_6():
    assert "6" in _text() and "Patient" in _text()


# 13. Notifications 1 referenced
def test_evidence_doc_mentions_notifications_1():
    assert "1" in _text() and "Notification" in _text()


# 14. Pending confirmations 0 referenced
def test_evidence_doc_mentions_pending_confirmations():
    assert "Pending confirmations" in _text() or "pending confirmation" in _text().lower()


# 15. Appointment Requests primary card referenced
def test_evidence_doc_mentions_appointment_requests_card():
    assert "Appointment Requests" in _text()


# 16. Confirmed badges referenced
def test_evidence_doc_mentions_confirmed_badges():
    text = _text().lower()
    assert "confirmed" in text and "badge" in text


# 17. Normal urgency badges referenced
def test_evidence_doc_mentions_normal_urgency_badges():
    assert "Normal urgency" in _text() or "normal" in _text().lower()


# 18. View summary referenced
def test_evidence_doc_mentions_view_summary():
    assert "View summary" in _text()


# 19. Notifications card referenced
def test_evidence_doc_mentions_notifications_card():
    assert "Notifications card" in _text() or "Notifications" in _text()


# 20. Pending notification badge referenced
def test_evidence_doc_mentions_pending_notification_badge():
    text = _text().lower()
    assert "pending" in text and "notification" in text and "badge" in text


# 21. Footer safety text referenced
def test_evidence_doc_mentions_footer_safety_text():
    text = _text()
    assert "footer" in text.lower() or "Production PHI: NO-GO" in text


# 22. No real patient data referenced
def test_evidence_doc_mentions_no_real_patient_data():
    assert "no real patient data" in _text().lower()


# 23. Production PHI NO-GO referenced
def test_evidence_doc_mentions_production_phi_no_go():
    text = _text().lower()
    assert "production phi" in text and "no-go" in text


# 24. No secrets recorded referenced
def test_evidence_doc_mentions_no_secrets_recorded():
    assert "no secrets recorded" in _text().lower()


# 25. External notification delivery pending referenced
def test_evidence_doc_mentions_external_delivery_pending():
    text = _text().lower()
    assert "external" in text and ("delivery" in text or "notification" in text)


# 26. Outreach referenced
def test_evidence_doc_mentions_outreach():
    assert "outreach" in _text().lower()


# 27. Clinic outreach list referenced
def test_evidence_doc_mentions_clinic_outreach_list():
    assert "clinic outreach list" in _text().lower() or "outreach list" in _text().lower()
