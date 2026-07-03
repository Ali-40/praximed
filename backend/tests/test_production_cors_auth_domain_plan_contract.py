"""
Static contract tests for Sprint 12 / Module 93 — Production CORS/Auth/Domain Plan.

Verifies:
- Plan document exists and covers required planning content
- Security rules and recommendations are present
- No real secrets in the document
"""

from __future__ import annotations

import os
import re


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

_PLAN_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md"
)


def _plan() -> str:
    with open(_PLAN_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Plan document exists
# ---------------------------------------------------------------------------


def test_plan_doc_exists() -> None:
    assert os.path.isfile(_PLAN_PATH), f"Plan doc not found at {_PLAN_PATH}"


def test_plan_doc_not_empty() -> None:
    assert len(_plan()) > 1000


# ---------------------------------------------------------------------------
# 2. Local frontend/backend URLs documented
# ---------------------------------------------------------------------------


def test_plan_mentions_local_frontend_url() -> None:
    assert "localhost:3000" in _plan()


def test_plan_mentions_local_backend_url() -> None:
    assert "127.0.0.1:8000" in _plan()


# ---------------------------------------------------------------------------
# 3. Staging and production domain placeholders
# ---------------------------------------------------------------------------


def test_plan_mentions_staging_domain() -> None:
    text = _plan()
    assert "staging" in text.lower()


def test_plan_mentions_production_domain_placeholder() -> None:
    text = _plan()
    assert "praximed.example.com" in text or "placeholder" in text.lower()


def test_plan_mentions_https_urls() -> None:
    assert "https://" in _plan()


# ---------------------------------------------------------------------------
# 4. CORS rules
# ---------------------------------------------------------------------------


def test_plan_mentions_no_wildcard_cors() -> None:
    text = _plan()
    assert "wildcard" in text.lower()


def test_plan_mentions_no_ngrok_in_production() -> None:
    text = _plan()
    assert "ngrok" in text.lower() and "production" in text.lower()


def test_plan_mentions_https_required() -> None:
    text = _plan()
    assert "HTTPS" in text or "https" in text


def test_plan_mentions_authorization_header() -> None:
    assert "Authorization" in _plan()


def test_plan_mentions_content_type_header() -> None:
    assert "Content-Type" in _plan()


# ---------------------------------------------------------------------------
# 5. sessionStorage JWT risk
# ---------------------------------------------------------------------------


def test_plan_mentions_session_storage_risk() -> None:
    text = _plan()
    assert "sessionStorage" in text and ("risk" in text.lower() or "xss" in text.lower() or "XSS" in text)


def test_plan_mentions_xss() -> None:
    text = _plan()
    assert "XSS" in text or "xss" in text.lower() or "cross-site scripting" in text.lower()


# ---------------------------------------------------------------------------
# 6. httpOnly Secure SameSite cookie migration path
# ---------------------------------------------------------------------------


def test_plan_mentions_httponly_cookie() -> None:
    text = _plan()
    assert "httpOnly" in text or "HttpOnly" in text or "http-only" in text.lower()


def test_plan_mentions_secure_cookie() -> None:
    text = _plan()
    assert "Secure" in text and "cookie" in text.lower()


def test_plan_mentions_samesite() -> None:
    text = _plan()
    assert "SameSite" in text or "same-site" in text.lower()


def test_plan_mentions_csrf() -> None:
    text = _plan()
    assert "CSRF" in text or "csrf" in text.lower()


# ---------------------------------------------------------------------------
# 7. Vapi machine-to-machine (not browser CORS)
# ---------------------------------------------------------------------------


def test_plan_mentions_vapi_scope_singular() -> None:
    assert "vapi:tool" in _plan()


def test_plan_mentions_machine_to_machine_not_browser_cors() -> None:
    text = _plan()
    assert (
        "machine" in text.lower() and
        ("server-to-server" in text.lower() or "not browser" in text.lower() or "not originate" in text.lower())
    )


def test_plan_mentions_clinic_id_from_machine_header() -> None:
    text = _plan()
    assert "X-Vapi-Clinic-Id" in text or ("clinic" in text.lower() and "machine auth" in text.lower())


# ---------------------------------------------------------------------------
# 8. Env vars
# ---------------------------------------------------------------------------


def test_plan_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _plan()


def test_plan_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _plan()


def test_plan_no_secrets_in_frontend_env() -> None:
    text = _plan()
    assert "no secrets" in text.lower() or "must never contain" in text.lower() or "not a secret" in text.lower()


# ---------------------------------------------------------------------------
# 9. Security headers
# ---------------------------------------------------------------------------


def test_plan_mentions_hsts() -> None:
    text = _plan()
    assert "HSTS" in text or "Strict-Transport-Security" in text


def test_plan_mentions_csp() -> None:
    text = _plan()
    assert "CSP" in text or "Content-Security-Policy" in text


# ---------------------------------------------------------------------------
# 10. Go/no-go and next module
# ---------------------------------------------------------------------------


def test_plan_mentions_not_ready_for_production() -> None:
    text = _plan()
    assert "not ready" in text.lower() or "Not ready" in text


def test_plan_mentions_deployment_smoke_runbook() -> None:
    text = _plan()
    assert "smoke runbook" in text.lower() or "Deployment Smoke Runbook" in text


def test_plan_mentions_next_module_94() -> None:
    text = _plan()
    assert "Module 94" in text or "module 94" in text.lower()


def test_plan_mentions_no_implementation_in_this_module() -> None:
    text = _plan()
    assert (
        "no implementation" in text.lower()
        or "planning only" in text.lower()
        or "no runtime" in text.lower()
    )


# ---------------------------------------------------------------------------
# 11. No real secrets in the document
# ---------------------------------------------------------------------------


def test_plan_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    matches = real_key_pattern.findall(_plan())
    assert not matches, f"Possible real key found in plan doc: {matches}"


def test_plan_no_real_passwords() -> None:
    text = _plan()
    assert "praxismed_local_password" not in text
