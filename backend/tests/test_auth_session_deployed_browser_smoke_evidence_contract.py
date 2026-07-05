"""
Sprint 17 / Module 120B — Auth/session deployed browser smoke evidence contract tests.

Static tests verifying the evidence doc records:
- PASS result for deployed browser auth/session smoke
- All browser smoke checks (login, dashboard, refresh, logout, post-logout block)
- Cookie/session context (praximed_session, HttpOnly, Secure, SameSite=None, credentials include)
- Safety constraints (no password/token/cookie value/secrets/real patient data)
- Production PHI NO-GO
- Recommended next module (Module 121)
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE_DOC = (
    ROOT
    / "docs"
    / "security"
    / "AUTH_SESSION_DEPLOYED_BROWSER_SMOKE_EVIDENCE.md"
)


def _text() -> str:
    return EVIDENCE_DOC.read_text()


def test_evidence_doc_exists():
    assert EVIDENCE_DOC.exists(), (
        "AUTH_SESSION_DEPLOYED_BROWSER_SMOKE_EVIDENCE.md must exist"
    )


def test_evidence_doc_records_pass():
    assert "PASS" in _text(), (
        "evidence doc must record overall result as PASS"
    )


def test_evidence_doc_mentions_frontend_url():
    assert "https://praximed.vercel.app" in _text(), (
        "evidence doc must mention the Vercel frontend URL"
    )


def test_evidence_doc_mentions_backend_url():
    assert "https://web-production-fd91d.up.railway.app" in _text(), (
        "evidence doc must mention the Railway backend URL"
    )


def test_evidence_doc_mentions_login_pass():
    text = _text()
    assert "login" in text.lower() and "PASS" in text, (
        "evidence doc must record browser login as PASS"
    )


def test_evidence_doc_mentions_dashboard_load_pass():
    text = _text()
    assert "dashboard" in text.lower() and "PASS" in text, (
        "evidence doc must record dashboard load as PASS"
    )


def test_evidence_doc_mentions_refresh_keeps_session():
    text = _text()
    assert "refresh" in text.lower() and "session" in text.lower(), (
        "evidence doc must record that session survives page refresh"
    )


def test_evidence_doc_mentions_logout_clears_session():
    text = _text()
    assert "logout" in text.lower() and ("clears" in text.lower() or "clear" in text.lower()), (
        "evidence doc must record that logout clears the session"
    )


def test_evidence_doc_mentions_post_logout_blocks():
    text = _text()
    assert "logout" in text.lower() and (
        "blocks" in text.lower() or "redirects" in text.lower() or "redirect" in text.lower()
    ), (
        "evidence doc must record that /dashboard after logout blocks or redirects"
    )


def test_evidence_doc_mentions_praximed_session_cookie():
    assert "praximed_session" in _text(), (
        "evidence doc must mention the praximed_session cookie name"
    )


def test_evidence_doc_mentions_httponly():
    text = _text()
    assert "httponly" in text.lower() or "HttpOnly" in text, (
        "evidence doc must mention HttpOnly cookie attribute"
    )


def test_evidence_doc_mentions_secure():
    text = _text()
    assert "secure" in text.lower() or "Secure" in text, (
        "evidence doc must mention Secure cookie attribute"
    )


def test_evidence_doc_mentions_samesite_none():
    text = _text()
    assert (
        "samesite=none" in text.lower()
        or "SameSite=None" in text
        or "SameSite" in text and "None" in text
    ), (
        "evidence doc must mention SameSite=None for cross-site staging"
    )


def test_evidence_doc_mentions_credentials_include():
    text = _text()
    assert "credentials" in text.lower() and "include" in text.lower(), (
        "evidence doc must mention credentials: include"
    )


def test_evidence_doc_mentions_no_token_recorded():
    text = _text()
    assert "no token recorded" in text.lower() or "token not recorded" in text.lower(), (
        "evidence doc must confirm no token is recorded"
    )


def test_evidence_doc_mentions_no_password_recorded():
    text = _text()
    assert "no password recorded" in text.lower() or "password not recorded" in text.lower(), (
        "evidence doc must confirm no password is recorded"
    )


def test_evidence_doc_mentions_no_cookie_value_recorded():
    text = _text()
    assert "no cookie value recorded" in text.lower() or "cookie value" in text.lower(), (
        "evidence doc must confirm no cookie value is recorded"
    )


def test_evidence_doc_mentions_no_real_patient_data():
    text = _text()
    assert "no real patient data" in text.lower() or "No real patient data" in text, (
        "evidence doc must confirm no real patient data"
    )


def test_evidence_doc_mentions_fake_non_phi_staging():
    text = _text()
    assert "fake" in text.lower() and (
        "non-phi" in text.lower() or "non phi" in text.lower() or "non-PHI" in text
    ), (
        "evidence doc must confirm fake/non-PHI staging only"
    )


def test_evidence_doc_mentions_production_phi_no_go():
    text = _text()
    assert "production phi" in text.lower() and (
        "no-go" in text.lower() or "NO-GO" in text
    ), (
        "evidence doc must confirm production PHI readiness remains NO-GO"
    )


def test_evidence_doc_mentions_module_121():
    text = _text()
    assert "Module 121" in text and (
        "secrets" in text.lower() or "environment" in text.lower()
    ), (
        "evidence doc must recommend Module 121 — Secrets and Environment Hardening Review"
    )
