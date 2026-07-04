"""
Sprint 16 / Module 116 — Backend staging login smoke evidence contract tests.

Static tests verifying the login smoke evidence doc records real PASS results
with correct sanitized evidence and no secrets.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE_DOC = (
    ROOT / "docs" / "runtime" / "BACKEND_STAGING_LOGIN_SMOKE_EVIDENCE.md"
)


def _text() -> str:
    return EVIDENCE_DOC.read_text()


def test_login_smoke_evidence_doc_exists():
    assert EVIDENCE_DOC.exists(), (
        "BACKEND_STAGING_LOGIN_SMOKE_EVIDENCE.md must exist"
    )


def test_login_smoke_evidence_mentions_pass():
    assert "PASS" in _text(), "evidence doc must record PASS result"


def test_login_smoke_evidence_mentions_health_endpoint():
    assert "/health" in _text(), (
        "evidence doc must record GET /health result"
    )


def test_login_smoke_evidence_mentions_health_ready_endpoint():
    assert "/health/ready" in _text(), (
        "evidence doc must record GET /health/ready result"
    )


def test_login_smoke_evidence_mentions_auth_login_endpoint():
    assert "/auth/login" in _text(), (
        "evidence doc must record POST /auth/login result"
    )


def test_login_smoke_evidence_mentions_status_200():
    assert "200" in _text(), (
        "evidence doc must record HTTP 200 status"
    )


def test_login_smoke_evidence_mentions_staging_email():
    assert "doctor.staging@praximed.test" in _text(), (
        "evidence doc must record the staging user email used in login"
    )


def test_login_smoke_evidence_mentions_clinic_uuid():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _text(), (
        "evidence doc must record the staging clinic_id used in login"
    )


def test_login_smoke_evidence_access_token_present():
    text = _text()
    assert "access_token" in text, (
        "evidence doc must confirm access_token was present in the response"
    )


def test_login_smoke_evidence_token_redacted():
    text = _text()
    assert "REDACTED" in text or "redacted" in text.lower(), (
        "evidence doc must confirm the token value is redacted/not recorded"
    )


def test_login_smoke_evidence_token_type_bearer():
    assert "bearer" in _text(), (
        "evidence doc must confirm token_type is bearer"
    )


def test_login_smoke_evidence_password_not_recorded():
    text = _text()
    assert "password not recorded" in text.lower() or "Password not recorded" in text, (
        "evidence doc must explicitly confirm password is not recorded"
    )


def test_login_smoke_evidence_bcrypt_hash_not_recorded():
    text = _text()
    assert "hash not recorded" in text.lower() or "bcrypt hash" in text.lower(), (
        "evidence doc must explicitly confirm bcrypt hash is not recorded"
    )


def test_login_smoke_evidence_database_url_not_recorded():
    assert "DATABASE_URL" in _text(), (
        "evidence doc must confirm DATABASE_URL is not recorded"
    )


def test_login_smoke_evidence_no_real_patient_data():
    text = _text()
    assert "no real patient" in text.lower() or "No real patient" in text, (
        "evidence doc must confirm no real patient data"
    )


def test_login_smoke_evidence_fake_non_phi_staging():
    text = _text()
    assert "fake" in text.lower() and "non-PHI" in text, (
        "evidence doc must confirm fake/non-PHI staging only"
    )


def test_login_smoke_evidence_vercel_still_pending():
    text = _text()
    assert "Vercel" in text and (
        "NOT PROVEN" in text or "PENDING" in text or "not deployed" in text.lower()
    ), (
        "evidence doc must note Vercel frontend is still pending"
    )


def test_login_smoke_evidence_cors_still_pending():
    text = _text()
    assert "CORS" in text and (
        "NOT PROVEN" in text or "PENDING" in text or "not wired" in text.lower()
    ), (
        "evidence doc must note CORS is still pending"
    )


def test_login_smoke_evidence_browser_dashboard_still_pending():
    text = _text()
    assert "dashboard" in text.lower() and (
        "NOT PROVEN" in text or "PENDING" in text or "not executed" in text.lower()
    ), (
        "evidence doc must note browser dashboard smoke is still pending"
    )


def test_login_smoke_evidence_vapi_still_pending():
    text = _text()
    assert "Vapi" in text and (
        "NOT PROVEN" in text or "PENDING" in text
    ), (
        "evidence doc must note Vapi staging is still pending"
    )


def test_login_smoke_evidence_mentions_module_117():
    assert "Module 117" in _text(), (
        "evidence doc must reference Module 117 for Vercel frontend deployment/wiring"
    )
