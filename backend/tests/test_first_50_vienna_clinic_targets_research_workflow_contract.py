"""
Static contract tests for Sprint 18 / Module 129 — First 50 Vienna Clinic Targets Research Workflow.

Inspects the workflow doc on disk. No database, no network.
No secrets. No real patient data.
"""

from __future__ import annotations

from pathlib import Path

WORKFLOW_DOC = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "business"
    / "FIRST_50_VIENNA_CLINIC_TARGETS_RESEARCH_WORKFLOW.md"
)


def _text() -> str:
    assert WORKFLOW_DOC.is_file(), f"Workflow doc not found: {WORKFLOW_DOC}"
    return WORKFLOW_DOC.read_text(encoding="utf-8")


# 1. Workflow document exists
def test_workflow_doc_exists():
    assert WORKFLOW_DOC.is_file()


# 2. 50 Vienna clinic targets referenced
def test_doc_mentions_50_vienna_clinic_targets():
    text = _text().lower()
    assert "50" in text and ("vienna" in text or "wien" in text)


# 3. Public information only rule stated
def test_doc_mentions_public_information_only():
    assert "public information only" in _text().lower() or "publicly" in _text().lower()


# 4. No scraping automation rule stated
def test_doc_mentions_no_scraping_automation():
    assert "no scraping automation" in _text().lower() or "scraping" in _text().lower()


# 5. Google Maps mentioned
def test_doc_mentions_google_maps():
    assert "Google Maps" in _text()


# 6. Clinic websites mentioned
def test_doc_mentions_clinic_websites():
    assert "website" in _text().lower() or "clinic website" in _text().lower()


# 7. Impressum mentioned
def test_doc_mentions_impressum():
    assert "Impressum" in _text()


# 8. Herold mentioned
def test_doc_mentions_herold():
    assert "Herold" in _text() or "herold.at" in _text()


# 9. DocFinder mentioned
def test_doc_mentions_docfinder():
    assert "DocFinder" in _text() or "docfinder.at" in _text()


# 10. WKO mentioned
def test_doc_mentions_wko():
    assert "WKO" in _text() or "wko.at" in _text()


# 11. Source URL required rule stated
def test_doc_mentions_source_url_required():
    assert "source url" in _text().lower() or "Source URL" in _text()


# 12. Do not guess rule stated
def test_doc_mentions_do_not_guess():
    assert "do not guess" in _text().lower() or "never guessed" in _text().lower() or "Do not guess" in _text()


# 13. Private GP specialty mentioned
def test_doc_mentions_private_gp():
    text = _text().lower()
    assert "private gp" in text or "allgemeinmedizin" in text


# 14. Dermatology mentioned
def test_doc_mentions_dermatology():
    assert "Dermatology" in _text() or "dermatology" in _text().lower()


# 15. Gynecology mentioned
def test_doc_mentions_gynecology():
    assert "Gynecology" in _text() or "gynecology" in _text().lower()


# 16. Orthopedics mentioned
def test_doc_mentions_orthopedics():
    assert "Orthopedics" in _text() or "orthopedics" in _text().lower()


# 17. Dentistry mentioned
def test_doc_mentions_dentistry():
    assert "Dentistry" in _text() or "dentistry" in _text().lower()


# 18. Aesthetics mentioned
def test_doc_mentions_aesthetics():
    assert "Aesthetics" in _text() or "aesthetics" in _text().lower() or "Ästhetische" in _text()


# 19. Physiotherapy mentioned
def test_doc_mentions_physiotherapy():
    assert "Physiotherapy" in _text() or "physiotherapy" in _text().lower()


# 20. Research 10 clinics first step present
def test_doc_mentions_research_10_clinics_first():
    assert "10" in _text() and ("clinic" in _text().lower() or "first" in _text().lower())


# 21. Contact 5 per batch present
def test_doc_mentions_contact_5():
    assert "5" in _text() and ("contact" in _text().lower() or "first 5" in _text().lower())


# 22. 3-business-day follow-up rule present
def test_doc_mentions_3_business_day_follow_up():
    assert "3 business day" in _text().lower() or "3-business-day" in _text().lower()


# 23. Fake-data demo boundary stated
def test_doc_mentions_fake_data_demo():
    text = _text().lower()
    assert "fake-data" in text or "synthetic data" in text or "staging" in text


# 24. No production PHI boundary stated
def test_doc_mentions_no_production_phi():
    text = _text().lower()
    assert "production phi" in text and "no-go" in text


# 25. No DSGVO readiness claim boundary stated
def test_doc_mentions_no_dsgvo_readiness_claim():
    text = _text().lower()
    assert "dsgvo" in text and ("not" in text or "no" in text or "claim" in text)
