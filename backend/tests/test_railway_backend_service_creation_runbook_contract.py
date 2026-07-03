"""
Static contract tests for Sprint 15 / Module 105 — Railway Backend Service Creation Runbook.

Verifies:
- Runbook doc exists and covers all required sections
- Exact settings, env vars, and safety rules are present
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
    _REPO_ROOT, "docs", "deployment", "RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md"
)


def _doc() -> str:
    with open(_DOC_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Doc existence and size
# ---------------------------------------------------------------------------


def test_runbook_doc_exists() -> None:
    assert os.path.isfile(_DOC_PATH), f"Runbook not found at {_DOC_PATH}"


def test_runbook_not_empty() -> None:
    assert len(_doc()) > 3000


# ---------------------------------------------------------------------------
# 2. Purpose and scope
# ---------------------------------------------------------------------------


def test_doc_mentions_railway_backend_service() -> None:
    text = _doc().lower()
    assert "railway" in text and "backend service" in text


def test_doc_mentions_fake_non_phi_staging_only() -> None:
    text = _doc().lower()
    assert ("fake" in text or "non-phi" in text) and "staging" in text


def test_doc_mentions_no_deployment_executed_by_claude() -> None:
    text = _doc().lower()
    assert (
        "no deployment executed" in text
        or "not executed" in text
        or "human-executable" in text
        or "developer follows" in text
    )


# ---------------------------------------------------------------------------
# 3. Service identification
# ---------------------------------------------------------------------------


def test_doc_mentions_service_name() -> None:
    text = _doc().lower()
    assert "service name" in text or "praxismed-backend-staging" in text


def test_doc_mentions_github_repo() -> None:
    text = _doc().lower()
    assert "github" in text and ("repo" in text or "repository" in text)


def test_doc_mentions_root_directory() -> None:
    text = _doc().lower()
    assert "root directory" in text or "root" in text


# ---------------------------------------------------------------------------
# 4. Start command settings
# ---------------------------------------------------------------------------


def test_doc_mentions_procfile() -> None:
    assert "Procfile" in _doc()


def test_doc_mentions_start_command() -> None:
    text = _doc().lower()
    assert "start command" in text


def test_doc_mentions_backend_app_main_app() -> None:
    assert "backend.app.main:app" in _doc()


def test_doc_mentions_host_0_0_0_0() -> None:
    assert "0.0.0.0" in _doc()


def test_doc_mentions_port_env_var() -> None:
    text = _doc()
    assert "$PORT" in text or "${PORT}" in text


# ---------------------------------------------------------------------------
# 5. Python runtime and dependencies
# ---------------------------------------------------------------------------


def test_doc_mentions_runtime_txt() -> None:
    assert "runtime.txt" in _doc()


def test_doc_mentions_python_3_11() -> None:
    text = _doc().lower()
    assert "python-3.11" in text or "python 3.11" in text


def test_doc_mentions_backend_requirements_txt() -> None:
    assert "backend/requirements.txt" in _doc()


# ---------------------------------------------------------------------------
# 6. Health check
# ---------------------------------------------------------------------------


def test_doc_mentions_health_route() -> None:
    assert "/health" in _doc()


# ---------------------------------------------------------------------------
# 7. Environment variables
# ---------------------------------------------------------------------------


def test_doc_mentions_database_url() -> None:
    assert "DATABASE_URL" in _doc()


def test_doc_mentions_jwt_secret_key() -> None:
    assert "JWT_SECRET_KEY" in _doc()


def test_doc_mentions_vapi_webhook_secret() -> None:
    assert "VAPI_WEBHOOK_SECRET" in _doc()


def test_doc_mentions_n8n_webhook_secret() -> None:
    assert "N8N_WEBHOOK_SECRET" in _doc()


def test_doc_mentions_internal_webhook_secret() -> None:
    assert "INTERNAL_WEBHOOK_SECRET" in _doc()


def test_doc_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _doc()


def test_doc_mentions_openssl_rand() -> None:
    assert "openssl rand" in _doc()


# ---------------------------------------------------------------------------
# 8. DATABASE_URL safety
# ---------------------------------------------------------------------------


def test_doc_mentions_no_local_docker_database_url() -> None:
    text = _doc().lower()
    assert (
        "local docker" in text
        or "localhost" in text
        or "127.0.0.1" in text
    ) and (
        "never" in text or "do not" in text or "must not" in text or "not use" in text
    )


def test_doc_mentions_no_production_database_url() -> None:
    text = _doc().lower()
    assert (
        "production" in text
        and (
            "never" in text
            or "do not" in text
            or "must not" in text
            or "not use" in text
        )
    )


# ---------------------------------------------------------------------------
# 9. Migration command
# ---------------------------------------------------------------------------


def test_doc_mentions_migration_command() -> None:
    assert "python backend/scripts/run_migrations.py" in _doc()


# ---------------------------------------------------------------------------
# 10. Evidence capture
# ---------------------------------------------------------------------------


def test_doc_mentions_evidence_capture() -> None:
    text = _doc().lower()
    assert "evidence" in text and ("capture" in text or "record" in text)


# ---------------------------------------------------------------------------
# 11. Failure triage and stop rules
# ---------------------------------------------------------------------------


def test_doc_mentions_failure_triage() -> None:
    text = _doc().lower()
    assert "failure" in text and ("triage" in text or "cause" in text)


def test_doc_mentions_stop_rules() -> None:
    text = _doc().lower()
    assert "stop" in text and ("rule" in text or "stop rule" in text or "stop if" in text)


# ---------------------------------------------------------------------------
# 12. Next step reference
# ---------------------------------------------------------------------------


def test_doc_mentions_module_106_railway_postgresql() -> None:
    text = _doc().lower()
    assert "module 106" in text and (
        "postgresql" in text or "postgres" in text
    )


# ---------------------------------------------------------------------------
# 13. No obvious real secrets
# ---------------------------------------------------------------------------


def test_doc_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_doc())
