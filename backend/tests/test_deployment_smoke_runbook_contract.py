"""
Static contract tests for Sprint 12 / Module 94 — Deployment Smoke Runbook.

Verifies:
- Runbook document exists and covers all required smoke areas
- Security rules and negative-test guidance are present
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

_RUNBOOK_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "DEPLOYMENT_SMOKE_RUNBOOK.md"
)


def _runbook() -> str:
    with open(_RUNBOOK_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Runbook document exists
# ---------------------------------------------------------------------------


def test_runbook_exists() -> None:
    assert os.path.isfile(_RUNBOOK_PATH), f"Runbook not found at {_RUNBOOK_PATH}"


def test_runbook_not_empty() -> None:
    assert len(_runbook()) > 1000


# ---------------------------------------------------------------------------
# 2. Deployment tiers covered
# ---------------------------------------------------------------------------


def test_runbook_mentions_local_tier() -> None:
    text = _runbook()
    assert "local" in text.lower() or "Local" in text


def test_runbook_mentions_staging_tier() -> None:
    text = _runbook()
    assert "staging" in text.lower() or "Staging" in text


def test_runbook_mentions_production_tier() -> None:
    text = _runbook()
    assert "production" in text.lower() or "Production" in text


# ---------------------------------------------------------------------------
# 3. Pre-smoke checklist
# ---------------------------------------------------------------------------


def test_runbook_mentions_pre_smoke_checklist() -> None:
    text = _runbook()
    assert "prerequisite" in text.lower() or "pre-smoke" in text.lower() or "checklist" in text.lower()


def test_runbook_mentions_env_vars() -> None:
    assert "DATABASE_URL" in _runbook()


def test_runbook_mentions_no_placeholder_secrets_in_staging_prod() -> None:
    text = _runbook()
    assert "placeholder" in text.lower() and "staging" in text.lower()


# ---------------------------------------------------------------------------
# 4. Backend health
# ---------------------------------------------------------------------------


def test_runbook_mentions_health_endpoint() -> None:
    text = _runbook()
    assert "/health" in text


def test_runbook_mentions_health_ready_endpoint() -> None:
    text = _runbook()
    assert "/health/ready" in text


# ---------------------------------------------------------------------------
# 5. Frontend
# ---------------------------------------------------------------------------


def test_runbook_mentions_frontend_login() -> None:
    text = _runbook()
    assert "/login" in text or "login page" in text.lower()


def test_runbook_mentions_npm_run_build() -> None:
    text = _runbook()
    assert "npm run build" in text


def test_runbook_mentions_next_start() -> None:
    text = _runbook()
    assert "npm start" in text or "next start" in text


# ---------------------------------------------------------------------------
# 6. Migrations and database
# ---------------------------------------------------------------------------


def test_runbook_mentions_migrations() -> None:
    text = _runbook()
    assert "migration" in text.lower() or "alembic" in text.lower()


def test_runbook_mentions_postgresql_or_database() -> None:
    text = _runbook()
    assert "postgresql" in text.lower() or "database" in text.lower()


def test_runbook_mentions_migration_failure_stops_deployment() -> None:
    text = _runbook()
    assert (
        "migration fail" in text.lower()
        or "exit code 0" in text
        or "exit non-zero" in text.lower()
    )


def test_runbook_mentions_backup_before_production_migration() -> None:
    text = _runbook()
    assert "backup" in text.lower() and "migration" in text.lower()


# ---------------------------------------------------------------------------
# 7. CORS
# ---------------------------------------------------------------------------


def test_runbook_mentions_cors_exact_origins() -> None:
    text = _runbook()
    assert "cors" in text.lower() and (
        "exact" in text.lower() or "Access-Control-Allow-Origin" in text
    )


def test_runbook_mentions_no_wildcard_cors() -> None:
    text = _runbook()
    assert "wildcard" in text.lower() and "cors" in text.lower()


def test_runbook_mentions_https_stable_domain() -> None:
    text = _runbook()
    assert "https" in text.lower() and "stable" in text.lower()


def test_runbook_mentions_no_ngrok_in_production() -> None:
    text = _runbook()
    assert "ngrok" in text.lower() and "production" in text.lower()


# ---------------------------------------------------------------------------
# 8. Auth / session
# ---------------------------------------------------------------------------


def test_runbook_mentions_session_storage_jwt_risk() -> None:
    text = _runbook()
    assert "sessionStorage" in text and (
        "risk" in text.lower() or "not suitable" in text.lower() or "module 93" in text.lower()
    )


def test_runbook_mentions_protected_dashboard() -> None:
    text = _runbook()
    assert "protected" in text.lower() and "dashboard" in text.lower()


def test_runbook_mentions_logout() -> None:
    text = _runbook()
    assert "logout" in text.lower()


# ---------------------------------------------------------------------------
# 9. Vapi smoke
# ---------------------------------------------------------------------------


def test_runbook_mentions_vapi_endpoint() -> None:
    assert "/vapi/tools/capture-appointment-request" in _runbook()


def test_runbook_mentions_vapi_scope_singular() -> None:
    assert "vapi:tool" in _runbook()


def test_runbook_mentions_staff_confirm_no_auto_confirmation() -> None:
    text = _runbook()
    assert (
        "no auto-confirmation" in text.lower()
        or "auto-confirm" in text.lower()
    )


# ---------------------------------------------------------------------------
# 10. n8n / calendar smoke
# ---------------------------------------------------------------------------


def test_runbook_mentions_n8n_webhook() -> None:
    text = _runbook()
    assert "n8n" in text.lower() or "calendar-sync" in text.lower()


# ---------------------------------------------------------------------------
# 11. No real patient data
# ---------------------------------------------------------------------------


def test_runbook_mentions_no_real_patient_data() -> None:
    text = _runbook()
    assert "no real patient" in text.lower() or "fake" in text.lower() or "synthetic" in text.lower()


# ---------------------------------------------------------------------------
# 12. Logging safety
# ---------------------------------------------------------------------------


def test_runbook_mentions_no_secrets_in_logs() -> None:
    text = _runbook()
    assert "log" in text.lower() and "secret" in text.lower()


def test_runbook_mentions_no_authorization_header_logging() -> None:
    text = _runbook()
    assert "Authorization" in text and "log" in text.lower()


# ---------------------------------------------------------------------------
# 13. Rollback
# ---------------------------------------------------------------------------


def test_runbook_mentions_rollback() -> None:
    text = _runbook()
    assert "rollback" in text.lower()


# ---------------------------------------------------------------------------
# 14. Production launch gate
# ---------------------------------------------------------------------------


def test_runbook_mentions_production_launch_not_approved_by_smoke() -> None:
    text = _runbook()
    assert (
        "does not approve" in text.lower()
        or "does not approve a production launch" in text.lower()
        or "not approve" in text.lower()
    )


def test_runbook_mentions_architecture_checkpoint_12() -> None:
    text = _runbook()
    assert "Architecture Checkpoint 12" in text or "Checkpoint 12" in text


# ---------------------------------------------------------------------------
# 15. No real secrets in the document
# ---------------------------------------------------------------------------


def test_runbook_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    matches = real_key_pattern.findall(_runbook())
    assert not matches, f"Possible real key in runbook: {matches}"


def test_runbook_no_real_db_password() -> None:
    text = _runbook()
    # The local placeholder password is allowed; a different real-looking password should not be
    for line in text.splitlines():
        if "postgresql://" in line and "praxismed_local_password" not in line:
            # If there's a postgresql:// URL without the known local placeholder, it may be real
            assert "example.com" in line or "placeholder" in line.lower() or "#" in line, (
                f"Unexpected non-placeholder DATABASE_URL found: {line!r}"
            )
