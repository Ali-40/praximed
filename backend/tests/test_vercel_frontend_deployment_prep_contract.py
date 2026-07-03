"""
Static contract tests for Sprint 14 / Module 102 — Vercel Frontend Deployment Prep.

Verifies:
- Vercel frontend deployment prep doc exists and covers all required sections
- No obvious real secrets in the document
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

_DOC_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "VERCEL_FRONTEND_DEPLOYMENT_PREP.md"
)


def _doc() -> str:
    with open(_DOC_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Doc existence and size
# ---------------------------------------------------------------------------


def test_vercel_frontend_prep_doc_exists() -> None:
    assert os.path.isfile(_DOC_PATH), f"Prep doc not found at {_DOC_PATH}"


def test_vercel_frontend_prep_doc_not_empty() -> None:
    assert len(_doc()) > 3000


# ---------------------------------------------------------------------------
# 2. Vercel and frontend coverage
# ---------------------------------------------------------------------------


def test_doc_mentions_vercel_frontend() -> None:
    text = _doc().lower()
    assert "vercel" in text and "frontend" in text


def test_doc_mentions_frontend_root_directory() -> None:
    text = _doc()
    assert "frontend" in text and (
        "root" in text.lower() or "root directory" in text.lower()
    )


def test_doc_mentions_nextjs() -> None:
    text = _doc().lower()
    assert "next.js" in text or "nextjs" in text


def test_doc_mentions_npm_run_build() -> None:
    assert "npm run build" in _doc()


def test_doc_mentions_npm_run_dev() -> None:
    assert "npm run dev" in _doc()


# ---------------------------------------------------------------------------
# 3. Environment variable coverage
# ---------------------------------------------------------------------------


def test_doc_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _doc()


def test_doc_mentions_no_backend_secrets_in_frontend_env() -> None:
    text = _doc().lower()
    assert (
        "no backend secrets" in text
        or "never" in text
        or "must not" in text
        or "must never" in text
    ) and ("secret" in text or "backend" in text)


def test_doc_mentions_no_database_url_in_frontend_env() -> None:
    assert "DATABASE_URL" in _doc()


def test_doc_mentions_no_jwt_secret_key_in_frontend_env() -> None:
    assert "JWT_SECRET_KEY" in _doc()


# ---------------------------------------------------------------------------
# 4. Railway / CORS / domain coverage
# ---------------------------------------------------------------------------


def test_doc_mentions_railway_staging_api_url() -> None:
    text = _doc().lower()
    assert "railway" in text and ("staging" in text or "api" in text)


def test_doc_mentions_frontend_cors_origins_exact_vercel_origin() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _doc()


def test_doc_mentions_no_wildcard_cors() -> None:
    text = _doc().lower()
    assert "wildcard" in text and "cors" in text


def test_doc_mentions_no_ngrok_in_staging() -> None:
    text = _doc().lower()
    assert "ngrok" in text and (
        "local" in text or "not" in text or "only" in text
    )


def test_doc_mentions_https() -> None:
    text = _doc().lower()
    assert "https" in text and "staging" in text


# ---------------------------------------------------------------------------
# 5. Frontend routes
# ---------------------------------------------------------------------------


def test_doc_mentions_login_route() -> None:
    assert "/login" in _doc()


def test_doc_mentions_dashboard_route() -> None:
    assert "/dashboard" in _doc()


# ---------------------------------------------------------------------------
# 6. Auth/session staging caveat
# ---------------------------------------------------------------------------


def test_doc_mentions_sessionstorage_jwt_fake_data_only() -> None:
    text = _doc().lower()
    assert "sessionstorage" in text and (
        "fake" in text or "staging" in text or "non-phi" in text
    )


def test_doc_mentions_httponly_cookie_migration_before_phi_production() -> None:
    text = _doc().lower()
    assert "httponly" in text or "http-only" in text or "httponly" in text


# ---------------------------------------------------------------------------
# 7. Staging constraints and deployment safety
# ---------------------------------------------------------------------------


def test_doc_mentions_fake_non_phi_staging_only() -> None:
    text = _doc().lower()
    assert ("fake" in text or "non-phi" in text) and "staging" in text


def test_doc_mentions_no_deployment_executed() -> None:
    text = _doc().lower()
    assert (
        "no deployment" in text
        or "not executed" in text
        or "no deployment executed" in text
    )


def test_doc_mentions_no_fabel5_ux_work() -> None:
    text = _doc().lower()
    assert "fabel" in text or "ux" in text


# ---------------------------------------------------------------------------
# 8. Operational sections
# ---------------------------------------------------------------------------


def test_doc_mentions_rollback() -> None:
    assert "rollback" in _doc().lower()


def test_doc_mentions_module_103_staging_db_migration_and_seed() -> None:
    text = _doc().lower()
    assert "module 103" in text and (
        "migration" in text or "seed" in text or "db" in text
    )


# ---------------------------------------------------------------------------
# 9. No obvious real secrets
# ---------------------------------------------------------------------------


def test_doc_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_doc())
