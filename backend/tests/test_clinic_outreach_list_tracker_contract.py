"""
Static contract tests for Sprint 18 / Module 128 — Clinic Outreach List Tracker Foundation.

Inspects the tracker doc on disk. No database, no network.
No secrets. No real patient data.
"""

from __future__ import annotations

from pathlib import Path

TRACKER_DOC = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "business"
    / "CLINIC_OUTREACH_LIST_TRACKER.md"
)


def _text() -> str:
    assert TRACKER_DOC.is_file(), f"Tracker doc not found: {TRACKER_DOC}"
    return TRACKER_DOC.read_text(encoding="utf-8")


# 1. Tracker document exists
def test_tracker_doc_exists():
    assert TRACKER_DOC.is_file()


# 2. 50 rows referenced
def test_doc_mentions_50_rows():
    assert "50" in _text()


# 3. Private clinics in Vienna referenced
def test_doc_mentions_private_clinics_vienna():
    text = _text().lower()
    assert "vienna" in text or "wien" in text or "privatarzt" in text


# 4. Not contacted stage present
def test_doc_mentions_not_contacted():
    assert "Not contacted" in _text()


# 5. Email sent stage present
def test_doc_mentions_email_sent():
    assert "Email sent" in _text()


# 6. Called stage present
def test_doc_mentions_called():
    assert "Called" in _text()


# 7. Demo booked stage present
def test_doc_mentions_demo_booked():
    assert "Demo booked" in _text()


# 8. Pilot interested stage present
def test_doc_mentions_pilot_interested():
    assert "Pilot interested" in _text()


# 9. Fit score present
def test_doc_mentions_fit_score():
    assert "Fit score" in _text() or "fit score" in _text().lower()


# 10. Follow-up mentioned
def test_doc_mentions_follow_up():
    assert "follow-up" in _text().lower() or "Follow-up" in _text()


# 11. Fake-data staging demo boundary stated
def test_doc_mentions_fake_data_staging_demo():
    text = _text().lower()
    assert "fake-data staging demo" in text or "staging demo" in text or "synthetic data" in text


# 12. No real patient data boundary stated
def test_doc_mentions_no_real_patient_data():
    assert "no real patient data" in _text().lower()


# 13. No production PHI boundary stated
def test_doc_mentions_no_production_phi():
    text = _text().lower()
    assert "production phi" in text and "no-go" in text


# 14. Add 10 clinics per day rule present
def test_doc_mentions_add_10_clinics_per_day():
    assert "10" in _text() and ("clinic" in _text().lower() or "per day" in _text().lower())


# 15. Contact 5 per day minimum present
def test_doc_mentions_contact_5_per_day():
    assert "5" in _text() and "per day" in _text().lower()
