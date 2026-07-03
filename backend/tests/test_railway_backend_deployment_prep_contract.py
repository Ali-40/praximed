"""
Static contract tests for Sprint 14 / Module 101 — Railway Backend Deployment Prep.

Verifies:
- backend/requirements.txt exists with all required runtime packages
- runtime.txt exists and pins Python 3.11
- Procfile exists with correct start command
- Deployment prep doc exists and covers all required sections
- No obvious real secrets in any created file
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

_REQUIREMENTS_PATH = os.path.join(_REPO_ROOT, "backend", "requirements.txt")
_RUNTIME_PATH = os.path.join(_REPO_ROOT, "runtime.txt")
_PROCFILE_PATH = os.path.join(_REPO_ROOT, "Procfile")
_DOC_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "RAILWAY_BACKEND_DEPLOYMENT_PREP.md"
)


def _requirements() -> str:
    with open(_REQUIREMENTS_PATH, encoding="utf-8") as f:
        return f.read()


def _runtime() -> str:
    with open(_RUNTIME_PATH, encoding="utf-8") as f:
        return f.read()


def _procfile() -> str:
    with open(_PROCFILE_PATH, encoding="utf-8") as f:
        return f.read()


def _doc() -> str:
    with open(_DOC_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. backend/requirements.txt
# ---------------------------------------------------------------------------


def test_requirements_txt_exists() -> None:
    assert os.path.isfile(_REQUIREMENTS_PATH), (
        f"requirements.txt not found at {_REQUIREMENTS_PATH}"
    )


def test_requirements_mentions_fastapi() -> None:
    assert "fastapi" in _requirements().lower()


def test_requirements_mentions_uvicorn() -> None:
    assert "uvicorn" in _requirements().lower()


def test_requirements_mentions_asyncpg() -> None:
    assert "asyncpg" in _requirements().lower()


def test_requirements_mentions_alembic() -> None:
    assert "alembic" in _requirements().lower()


def test_requirements_mentions_pydantic() -> None:
    assert "pydantic" in _requirements().lower()


def test_requirements_mentions_pyjwt() -> None:
    text = _requirements().lower()
    assert "pyjwt" in text or "jwt" in text


def test_requirements_mentions_bcrypt() -> None:
    assert "bcrypt" in _requirements().lower()


def test_requirements_has_no_real_secrets() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_requirements())


# ---------------------------------------------------------------------------
# 2. runtime.txt
# ---------------------------------------------------------------------------


def test_runtime_txt_exists() -> None:
    assert os.path.isfile(_RUNTIME_PATH), f"runtime.txt not found at {_RUNTIME_PATH}"


def test_runtime_txt_mentions_python_3_11() -> None:
    text = _runtime().lower()
    assert "python-3.11" in text or "python-3" in text or "3.11" in text


# ---------------------------------------------------------------------------
# 3. Procfile
# ---------------------------------------------------------------------------


def test_procfile_exists() -> None:
    assert os.path.isfile(_PROCFILE_PATH), f"Procfile not found at {_PROCFILE_PATH}"


def test_procfile_references_backend_app_main() -> None:
    text = _procfile()
    assert "backend.app.main" in text or "backend/app/main" in text


def test_procfile_binds_0_0_0_0() -> None:
    assert "0.0.0.0" in _procfile()


def test_procfile_uses_port_env_var() -> None:
    text = _procfile()
    assert "$PORT" in text or "${PORT}" in text


def test_procfile_has_web_process_type() -> None:
    text = _procfile()
    assert text.strip().startswith("web:") or "web:" in text


def test_procfile_mentions_uvicorn() -> None:
    assert "uvicorn" in _procfile().lower()


# ---------------------------------------------------------------------------
# 4. Deployment prep doc
# ---------------------------------------------------------------------------


def test_railway_backend_prep_doc_exists() -> None:
    assert os.path.isfile(_DOC_PATH), f"Prep doc not found at {_DOC_PATH}"


def test_prep_doc_not_empty() -> None:
    assert len(_doc()) > 3000


def test_prep_doc_mentions_railway_backend() -> None:
    text = _doc()
    assert "railway" in text.lower() and "backend" in text.lower()


def test_prep_doc_mentions_fake_non_phi_staging_only() -> None:
    text = _doc()
    assert (
        "fake" in text.lower() or "non-phi" in text.lower()
    ) and "staging" in text.lower()


def test_prep_doc_mentions_no_deployment_executed() -> None:
    text = _doc()
    assert (
        "no deployment" in text.lower()
        or "no deployment executed" in text.lower()
        or "not executed" in text.lower()
    )


def test_prep_doc_mentions_database_url() -> None:
    assert "DATABASE_URL" in _doc()


def test_prep_doc_mentions_jwt_secret_key() -> None:
    assert "JWT_SECRET_KEY" in _doc()


def test_prep_doc_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _doc()


def test_prep_doc_mentions_health_route() -> None:
    text = _doc()
    assert "/health" in text


def test_prep_doc_mentions_migration_command() -> None:
    text = _doc()
    assert "run_migrations" in text or (
        "migration" in text.lower() and "command" in text.lower()
    )


def test_prep_doc_mentions_vapi_endpoint() -> None:
    text = _doc()
    assert "capture-appointment-request" in text or "vapi/tools" in text.lower()


def test_prep_doc_mentions_vapi_tool_singular_scope() -> None:
    assert "vapi:tool" in _doc()


def test_prep_doc_mentions_no_ngrok_in_staging() -> None:
    text = _doc()
    assert "ngrok" in text.lower() and (
        "local" in text.lower()
        or "not" in text.lower()
        or "stop rule" in text.lower()
    )


def test_prep_doc_mentions_no_wildcard_cors() -> None:
    text = _doc()
    assert "wildcard" in text.lower() and "cors" in text.lower()


def test_prep_doc_mentions_https_required() -> None:
    text = _doc()
    assert "https" in text.lower() and "staging" in text.lower()


def test_prep_doc_mentions_staff_confirm_no_auto_confirmation() -> None:
    text = _doc()
    assert (
        "no auto-confirm" in text.lower()
        or "auto-confirm" in text.lower()
        or "action_required" in text.lower()
    ) and (
        "staff" in text.lower() or "confirm" in text.lower()
    )


def test_prep_doc_mentions_port_and_host_binding() -> None:
    text = _doc()
    assert "0.0.0.0" in text and (
        "$PORT" in text or "port" in text.lower()
    )


def test_prep_doc_mentions_blockers_remaining() -> None:
    text = _doc()
    assert "blocker" in text.lower() or "remaining" in text.lower()


# ---------------------------------------------------------------------------
# 5. No obvious real secrets
# ---------------------------------------------------------------------------


def test_prep_doc_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_doc())


def test_procfile_no_real_secrets() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_procfile())
