"""
Static contract tests for Sprint 18 / Module 127 — Clinic Outreach and 30-Day Pilot Offer Pack.

Inspects the business doc on disk. No database, no network.
No secrets. No real patient data.
"""

from __future__ import annotations

from pathlib import Path

OUTREACH_DOC = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "business"
    / "CLINIC_OUTREACH_30_DAY_PILOT_PACK.md"
)


def _text() -> str:
    assert OUTREACH_DOC.is_file(), f"Outreach doc not found: {OUTREACH_DOC}"
    return OUTREACH_DOC.read_text(encoding="utf-8")


# 1. Document exists
def test_outreach_doc_exists():
    assert OUTREACH_DOC.is_file()


# 2. PraxisMed positioning present
def test_doc_mentions_praxismed_positioning():
    assert "PraxisMed" in _text()


# 3. AI receptionist claim present
def test_doc_mentions_ai_receptionist():
    assert "AI receptionist" in _text() or "AI-powered receptionist" in _text() or "KI-Rezeption" in _text()


# 4. Clinic workflow mentioned
def test_doc_mentions_clinic_workflow():
    assert "clinic workflow" in _text().lower() or "workflow" in _text().lower()


# 5. Private clinics as target mentioned
def test_doc_mentions_private_clinics():
    assert "private clinic" in _text().lower() or "Privatpraxis" in _text()


# 6. 30-day pilot offer present
def test_doc_mentions_30_day_pilot():
    assert "30-day pilot" in _text() or "30-Tage-Pilot" in _text()


# 7. Fake-data staging demo boundary stated
def test_doc_mentions_fake_data_staging():
    text = _text().lower()
    assert "fake" in text or "synthetic" in text or "staging demo" in text


# 8. No production PHI claim — must say no PHI or staging only
def test_doc_mentions_no_production_phi():
    text = _text().lower()
    assert "production phi" in text or "no-go" in text or "no real patient data" in text


# 9. No real patient data boundary stated
def test_doc_mentions_no_real_patient_data():
    assert "no real patient data" in _text().lower()


# 10. Production readiness not claimed — framing language present
def test_doc_mentions_production_readiness_not_claimed():
    text = _text().lower()
    assert "production hardening" in text or "not claim" in text or "must not claim" in text


# 11. Pre-appointment summaries mentioned
def test_doc_mentions_pre_appointment_summaries():
    assert "pre-appointment summar" in _text().lower()


# 12. Internal notifications mentioned
def test_doc_mentions_internal_notifications():
    assert "internal notification" in _text().lower() or "internal alert" in _text().lower()


# 13. Staff Confirm mentioned
def test_doc_mentions_staff_confirm():
    text = _text().lower()
    assert "confirm" in text and ("staff" in text or "review" in text)


# 14. Pricing €299 present
def test_doc_mentions_pricing_299():
    assert "299" in _text()


# 15. Pricing €499 present
def test_doc_mentions_pricing_499():
    assert "499" in _text()


# 16. Setup fee waived mentioned
def test_doc_mentions_setup_fee_waived():
    assert "setup fee waived" in _text().lower() or "waived" in _text().lower()


# 17. 50-clinic outreach list mentioned
def test_doc_mentions_50_clinic_outreach_list():
    assert "50" in _text() and "outreach list" in _text().lower()


# 18. Email script present
def test_doc_mentions_email_script():
    text = _text().lower()
    assert "email" in text and ("script" in text or "outreach" in text)


# 19. German script present
def test_doc_mentions_german_script():
    text = _text()
    assert "Deutsch" in text or "German" in text or "Sehr geehrte" in text


# 20. Phone script present
def test_doc_mentions_phone_script():
    text = _text().lower()
    assert "phone" in text and ("script" in text or "call" in text)


# 21. Demo script present
def test_doc_mentions_demo_script():
    assert "Demo Script" in _text() or "demo script" in _text().lower()


# 22. Objection handling present
def test_doc_mentions_objection_handling():
    assert "Objection" in _text() or "objection" in _text().lower()


# 23. Follow-up sequence present
def test_doc_mentions_follow_up_sequence():
    assert "Follow-Up" in _text() or "follow-up sequence" in _text().lower() or "Follow-up" in _text()


# 24. Legal / compliance boundary stated
def test_doc_mentions_legal_compliance_boundary():
    text = _text().lower()
    assert "dsgvo" in text or "gdpr" in text or "legal" in text or "compliance" in text


# 25. Daily outreach targets present
def test_doc_mentions_daily_outreach_targets():
    text = _text().lower()
    assert "daily" in text and ("target" in text or "outreach" in text)
