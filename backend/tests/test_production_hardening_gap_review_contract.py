"""
Sprint 17 / Module 119 — Production hardening gap review contract tests.

Static tests verifying the gap review doc records:
- production PHI NO-GO
- all critical/high/medium blockers
- the recommended module order (120–126)
- safety constraints (no secrets, no real patient data)
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
GAP_REVIEW_DOC = ROOT / "docs" / "architecture" / "PRODUCTION_HARDENING_GAP_REVIEW.md"


def _text() -> str:
    return GAP_REVIEW_DOC.read_text()


def test_gap_review_doc_exists():
    assert GAP_REVIEW_DOC.exists(), (
        "PRODUCTION_HARDENING_GAP_REVIEW.md must exist"
    )


def test_gap_review_mentions_production_phi_no_go():
    assert "PRODUCTION PHI NO-GO" in _text(), (
        "gap review must state PRODUCTION PHI NO-GO"
    )


def test_gap_review_mentions_fake_data_staging():
    text = _text()
    assert "fake-data staging" in text.lower() or "fake data staging" in text.lower(), (
        "gap review must reference the fake-data staging core that is already PASS"
    )


def test_gap_review_mentions_auth_session_hardening():
    text = _text()
    assert "auth/session hardening" in text.lower(), (
        "gap review must mention auth/session hardening as a critical blocker"
    )


def test_gap_review_mentions_token_storage():
    text = _text()
    assert "token storage" in text.lower(), (
        "gap review must mention token storage risk (sessionStorage XSS-accessible)"
    )


def test_gap_review_mentions_production_secrets():
    text = _text()
    assert "production secrets" in text.lower(), (
        "gap review must mention production secrets rotation/review"
    )


def test_gap_review_mentions_phi_logging():
    text = _text()
    assert "phi logging" in text.lower() or "PHI logging" in text, (
        "gap review must mention PHI logging/redaction as a critical blocker"
    )


def test_gap_review_mentions_tenant_isolation():
    text = _text()
    assert "tenant isolation" in text.lower(), (
        "gap review must mention tenant isolation assurance"
    )


def test_gap_review_mentions_audit():
    text = _text()
    assert "audit" in text.lower(), (
        "gap review must mention audit log completeness"
    )


def test_gap_review_mentions_backups():
    text = _text()
    assert "backup" in text.lower() or "backups" in text.lower(), (
        "gap review must mention backups and restore strategy"
    )


def test_gap_review_mentions_rollback():
    text = _text()
    assert "rollback" in text.lower(), (
        "gap review must mention incident response and rollback plan"
    )


def test_gap_review_mentions_monitoring():
    text = _text()
    assert "monitoring" in text.lower(), (
        "gap review must mention monitoring and alerting"
    )


def test_gap_review_mentions_rate_limiting():
    text = _text()
    assert "rate limiting" in text.lower() or "rate limit" in text.lower(), (
        "gap review must mention rate limiting and abuse protection"
    )


def test_gap_review_mentions_cors_domain_finalization():
    text = _text()
    assert "CORS" in text and ("domain" in text.lower() or "finalization" in text.lower()), (
        "gap review must mention CORS/domain finalization"
    )


def test_gap_review_mentions_n8n_staging():
    text = _text()
    assert "n8n staging" in text.lower() or "n8n" in text, (
        "gap review must mention n8n staging as a medium-priority item"
    )


def test_gap_review_mentions_no_real_patient_data():
    text = _text()
    assert "no real patient data" in text.lower() or "No real patient data" in text, (
        "gap review must confirm no real patient data"
    )


def test_gap_review_mentions_no_production_phi():
    text = _text()
    assert "no production phi" in text.lower() or "No production PHI" in text, (
        "gap review must confirm no production PHI"
    )


def test_gap_review_mentions_no_secrets_recorded():
    text = _text()
    assert "no secrets recorded" in text.lower() or "No secrets recorded" in text, (
        "gap review must confirm no secrets are recorded"
    )


def test_gap_review_recommends_module_120_auth_session_hardening():
    assert "Module 120" in _text() and "auth/session hardening" in _text().lower(), (
        "gap review must recommend Module 120 — Auth/session hardening implementation"
    )


def test_gap_review_mentions_module_121():
    assert "Module 121" in _text(), (
        "gap review must mention Module 121 (secrets and environment hardening)"
    )


def test_gap_review_mentions_module_122():
    assert "Module 122" in _text(), (
        "gap review must mention Module 122 (PHI logging/redaction and audit hardening)"
    )


def test_gap_review_mentions_module_123():
    assert "Module 123" in _text(), (
        "gap review must mention Module 123 (tenant isolation and access-control verification)"
    )


def test_gap_review_mentions_module_124():
    assert "Module 124" in _text(), (
        "gap review must mention Module 124 (backup/restore and rollback runbook)"
    )


def test_gap_review_mentions_module_125():
    assert "Module 125" in _text(), (
        "gap review must mention Module 125 (monitoring/alerts/rate-limit plan)"
    )


def test_gap_review_mentions_module_126():
    assert "Module 126" in _text(), (
        "gap review must mention Module 126 (n8n staging workflow)"
    )
