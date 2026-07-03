"""
Static contract tests for Sprint 14 / Module 100 — Staging Deployment Config File Inventory.

Verifies:
- Inventory document exists and covers all required sections
- Railway backend, PostgreSQL, and Vercel frontend are addressed
- Missing config file blockers are documented
- Fake/non-PHI staging constraint and PHI no-go are explicit
- No deployment executed in this module
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

_INVENTORY_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "STAGING_DEPLOYMENT_CONFIG_FILE_INVENTORY.md"
)


def _doc() -> str:
    with open(_INVENTORY_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Document exists and is non-trivial
# ---------------------------------------------------------------------------


def test_staging_config_inventory_exists() -> None:
    assert os.path.isfile(_INVENTORY_PATH), f"Inventory not found at {_INVENTORY_PATH}"


def test_staging_config_inventory_not_empty() -> None:
    assert len(_doc()) > 5000


# ---------------------------------------------------------------------------
# 2. Railway backend
# ---------------------------------------------------------------------------


def test_inventory_mentions_railway_backend() -> None:
    text = _doc()
    assert "railway" in text.lower() and (
        "backend" in text.lower() or "service" in text.lower()
    )


def test_inventory_mentions_backend_start_command() -> None:
    text = _doc()
    assert "start command" in text.lower() or "startcommand" in text.lower()


def test_inventory_mentions_uvicorn() -> None:
    text = _doc()
    assert "uvicorn" in text.lower()


def test_inventory_mentions_app_import_path() -> None:
    text = _doc()
    assert "backend.app.main:app" in text or "backend.app.main" in text


def test_inventory_mentions_port_binding() -> None:
    text = _doc()
    assert "$port" in text.lower() or "0.0.0.0" in text.lower()


def test_inventory_mentions_health_route() -> None:
    text = _doc()
    assert "/health" in text or "health route" in text.lower()


def test_inventory_mentions_requirements_txt_missing() -> None:
    text = _doc()
    assert "requirements.txt" in text and (
        "missing" in text.lower() or "blocker" in text.lower()
    )


def test_inventory_mentions_procfile_or_railway_toml() -> None:
    text = _doc()
    assert "procfile" in text.lower() or "railway.toml" in text.lower()


def test_inventory_mentions_python_version() -> None:
    text = _doc()
    assert (
        "python 3.11" in text.lower()
        or "runtime.txt" in text.lower()
        or "python version" in text.lower()
    )


def test_inventory_mentions_nixpacks() -> None:
    text = _doc()
    assert "nixpacks" in text.lower()


# ---------------------------------------------------------------------------
# 3. Railway PostgreSQL
# ---------------------------------------------------------------------------


def test_inventory_mentions_railway_postgresql() -> None:
    text = _doc()
    assert "railway" in text.lower() and (
        "postgresql" in text.lower() or "postgres" in text.lower()
    )


def test_inventory_mentions_database_url_injection() -> None:
    text = _doc()
    assert "DATABASE_URL" in text and (
        "inject" in text.lower() or "auto" in text.lower()
    )


def test_inventory_mentions_migrations() -> None:
    text = _doc()
    assert "migration" in text.lower() and (
        "run_migrations" in text.lower() or "alembic" in text.lower()
    )


def test_inventory_mentions_seed_strategy_gap() -> None:
    text = _doc()
    assert (
        "seed" in text.lower()
        and (
            "gap" in text.lower()
            or "missing" in text.lower()
            or "strategy" in text.lower()
        )
    )


def test_inventory_mentions_seed_local_data_must_not_run_in_staging() -> None:
    text = _doc()
    assert "seed_local_data" in text and (
        "must not" in text.lower()
        or "not run" in text.lower()
        or "local-only" in text.lower()
    )


def test_inventory_mentions_no_db_ready_retry() -> None:
    text = _doc()
    assert "retry" in text.lower() and (
        "run_migrations" in text.lower()
        or "migration" in text.lower()
        or "cold" in text.lower()
    )


# ---------------------------------------------------------------------------
# 4. Vercel frontend
# ---------------------------------------------------------------------------


def test_inventory_mentions_vercel_frontend() -> None:
    text = _doc()
    assert "vercel" in text.lower() and "frontend" in text.lower()


def test_inventory_mentions_frontend_root_directory() -> None:
    text = _doc()
    assert (
        "frontend/" in text or "root directory" in text.lower()
    ) and "vercel" in text.lower()


def test_inventory_mentions_package_json_and_build_command() -> None:
    text = _doc()
    assert "package.json" in text and (
        "npm run build" in text.lower()
        or "next build" in text.lower()
        or "build command" in text.lower()
    )


def test_inventory_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _doc()


def test_inventory_mentions_no_backend_secrets_in_frontend_env() -> None:
    text = _doc()
    assert (
        "no backend secret" in text.lower()
        or "not a secret" in text.lower()
        or "public" in text.lower()
    ) and "next_public" in text.lower()


def test_inventory_mentions_frontend_gitignore_missing() -> None:
    text = _doc()
    assert "frontend/.gitignore" in text or (
        "frontend" in text.lower() and "gitignore" in text.lower() and "missing" in text.lower()
    )


# ---------------------------------------------------------------------------
# 5. Cross-platform CORS and domains
# ---------------------------------------------------------------------------


def test_inventory_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _doc()


def test_inventory_mentions_no_wildcard_cors() -> None:
    text = _doc()
    assert "wildcard" in text.lower() and "cors" in text.lower()


def test_inventory_mentions_no_ngrok() -> None:
    text = _doc()
    assert "ngrok" in text.lower() and (
        "not" in text.lower() or "must not" in text.lower() or "local" in text.lower()
    )


def test_inventory_mentions_https_required() -> None:
    text = _doc()
    assert "https" in text.lower() and "staging" in text.lower()


def test_inventory_mentions_cross_domain_samesite_issue() -> None:
    text = _doc()
    assert (
        "samesite" in text.lower()
        or "cross-domain" in text.lower()
        or "cross-site" in text.lower()
    ) and "staging" in text.lower()


# ---------------------------------------------------------------------------
# 6. Vapi and n8n
# ---------------------------------------------------------------------------


def test_inventory_mentions_vapi_endpoint() -> None:
    text = _doc()
    assert "capture-appointment-request" in text or "vapi/tools" in text.lower()


def test_inventory_mentions_vapi_tool_singular_scope() -> None:
    text = _doc()
    assert "vapi:tool" in text


def test_inventory_mentions_n8n_staging() -> None:
    text = _doc()
    assert "n8n" in text.lower() and "staging" in text.lower()


# ---------------------------------------------------------------------------
# 7. sessionStorage JWT fake-data-only risk
# ---------------------------------------------------------------------------


def test_inventory_mentions_session_storage_jwt_acceptable_for_staging() -> None:
    text = _doc()
    assert "sessionstorage" in text.lower() and (
        "fake" in text.lower()
        or "staging" in text.lower()
        or "acceptable" in text.lower()
    )


def test_inventory_mentions_session_storage_phi_blocker() -> None:
    text = _doc()
    assert "sessionstorage" in text.lower() and (
        "phi" in text.lower()
        or "production" in text.lower()
        or "blocker" in text.lower()
    )


# ---------------------------------------------------------------------------
# 8. Fake/non-PHI staging, production PHI no-go
# ---------------------------------------------------------------------------


def test_inventory_mentions_fake_non_phi_staging_only() -> None:
    text = _doc()
    assert (
        "fake" in text.lower() or "non-phi" in text.lower() or "synthetic" in text.lower()
    ) and "staging" in text.lower()


def test_inventory_mentions_production_phi_no_go() -> None:
    text = _doc()
    assert "phi" in text.lower() and (
        "no-go" in text.lower() or "NO-GO" in text or "remains" in text.lower()
    )


# ---------------------------------------------------------------------------
# 9. No deployment in this module
# ---------------------------------------------------------------------------


def test_inventory_mentions_no_deployment_in_this_module() -> None:
    text = _doc()
    assert (
        "no deployment" in text.lower()
        or "inventory only" in text.lower()
        or "no deployment execution" in text.lower()
    )


# ---------------------------------------------------------------------------
# 10. Module 101 next step
# ---------------------------------------------------------------------------


def test_inventory_mentions_module_101() -> None:
    text = _doc()
    assert "module 101" in text.lower() or "Module 101" in text


def test_inventory_mentions_module_101_railway_prep() -> None:
    text = _doc()
    assert "module 101" in text.lower() and (
        "railway" in text.lower()
        or "backend" in text.lower()
        or "prep" in text.lower()
    )


# ---------------------------------------------------------------------------
# 11. No obvious real secrets
# ---------------------------------------------------------------------------


def test_inventory_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    matches = real_key_pattern.findall(_doc())
    assert not matches, f"Possible real key in inventory: {matches}"


def test_inventory_no_real_db_password() -> None:
    text = _doc()
    for line in text.splitlines():
        if "postgresql://" in line:
            assert (
                "placeholder" in line.lower()
                or "example" in line.lower()
                or "<" in line
                or "#" in line
                or "..." in line
            ), f"Unexpected non-placeholder DATABASE_URL: {line!r}"
