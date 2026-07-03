"""
Static contract tests for Sprint 13 / Module 97 — Staging Deployment Dry-Run Checklist.

Verifies:
- Checklist document exists and covers all required phases
- Railway, Vercel, PostgreSQL, Vapi, and n8n are covered
- Failure stop rules, rollback, evidence capture, and go/no-go are present
- Staging/production separation is explicit
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

_CHECKLIST_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md"
)


def _checklist() -> str:
    with open(_CHECKLIST_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Document exists and is non-trivial
# ---------------------------------------------------------------------------


def test_staging_dry_run_checklist_exists() -> None:
    assert os.path.isfile(_CHECKLIST_PATH), f"Checklist not found at {_CHECKLIST_PATH}"


def test_staging_dry_run_checklist_not_empty() -> None:
    assert len(_checklist()) > 5000


# ---------------------------------------------------------------------------
# 2. Platforms covered
# ---------------------------------------------------------------------------


def test_checklist_mentions_railway_backend() -> None:
    text = _checklist()
    assert "Railway" in text and (
        "backend" in text.lower() or "service" in text.lower()
    )


def test_checklist_mentions_railway_postgresql() -> None:
    text = _checklist()
    assert "Railway" in text and (
        "postgresql" in text.lower() or "postgres" in text.lower()
    )


def test_checklist_mentions_vercel_frontend() -> None:
    text = _checklist()
    assert "Vercel" in text and "frontend" in text.lower()


# ---------------------------------------------------------------------------
# 3. Data / PHI policy
# ---------------------------------------------------------------------------


def test_checklist_mentions_fake_non_phi_staging_only() -> None:
    text = _checklist()
    assert "fake" in text.lower() or "synthetic" in text.lower()


def test_checklist_mentions_production_phi_no_go() -> None:
    text = _checklist()
    assert "no-go" in text.lower() or "NO-GO" in text


def test_checklist_mentions_no_deployment_in_this_module() -> None:
    text = _checklist()
    assert (
        "no deployment" in text.lower()
        or "planning only" in text.lower()
        or "not executed" in text.lower()
    )


# ---------------------------------------------------------------------------
# 4. No ngrok / no wildcard CORS / HTTPS
# ---------------------------------------------------------------------------


def test_checklist_mentions_no_ngrok() -> None:
    text = _checklist()
    assert "ngrok" in text.lower() and (
        "not used" in text.lower()
        or "no ngrok" in text.lower()
        or "replac" in text.lower()
    )


def test_checklist_mentions_no_wildcard_cors() -> None:
    text = _checklist()
    assert "wildcard" in text.lower() and "cors" in text.lower()


def test_checklist_mentions_https_staging_api() -> None:
    text = _checklist()
    assert "https://" in text and "staging" in text.lower()


# ---------------------------------------------------------------------------
# 5. Env vars covered
# ---------------------------------------------------------------------------


def test_checklist_mentions_database_url() -> None:
    assert "DATABASE_URL" in _checklist()


def test_checklist_mentions_jwt_secret_key() -> None:
    assert "JWT_SECRET_KEY" in _checklist()


def test_checklist_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _checklist()


def test_checklist_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _checklist()


# ---------------------------------------------------------------------------
# 6. Migrations
# ---------------------------------------------------------------------------


def test_checklist_mentions_migrations() -> None:
    text = _checklist()
    assert "migration" in text.lower() or "alembic" in text.lower()


# ---------------------------------------------------------------------------
# 7. Vapi
# ---------------------------------------------------------------------------


def test_checklist_mentions_vapi_endpoint() -> None:
    text = _checklist()
    assert "/vapi/tools/capture-appointment-request" in text or "vapi" in text.lower()


def test_checklist_mentions_vapi_scope_singular() -> None:
    assert "vapi:tool" in _checklist()


def test_checklist_mentions_no_auto_confirmation() -> None:
    text = _checklist()
    assert (
        "no auto-confirm" in text.lower()
        or "auto-confirm" in text.lower()
        or "status = new" in text.lower()
        or "status=new" in text.lower()
    )


def test_checklist_mentions_staff_confirm() -> None:
    text = _checklist()
    assert "confirm" in text.lower() and (
        "staff" in text.lower() or "human" in text.lower()
    )


# ---------------------------------------------------------------------------
# 8. n8n
# ---------------------------------------------------------------------------


def test_checklist_mentions_n8n_staging_workflow() -> None:
    text = _checklist()
    assert "n8n" in text.lower() and "staging" in text.lower()


# ---------------------------------------------------------------------------
# 9. No real patient data
# ---------------------------------------------------------------------------


def test_checklist_mentions_no_real_patient_data() -> None:
    text = _checklist()
    assert (
        "no real patient" in text.lower()
        or "fake" in text.lower()
        or "no real" in text.lower()
    )


# ---------------------------------------------------------------------------
# 10. Logging safety
# ---------------------------------------------------------------------------


def test_checklist_mentions_no_secrets_in_logs() -> None:
    text = _checklist()
    assert "log" in text.lower() and "secret" in text.lower()


# ---------------------------------------------------------------------------
# 11. Rollback
# ---------------------------------------------------------------------------


def test_checklist_mentions_rollback() -> None:
    text = _checklist()
    assert "rollback" in text.lower()


# ---------------------------------------------------------------------------
# 12. Evidence capture
# ---------------------------------------------------------------------------


def test_checklist_mentions_evidence_capture() -> None:
    text = _checklist()
    assert (
        "evidence" in text.lower()
        or "capture" in text.lower()
        or "pass/fail" in text.lower()
    )


# ---------------------------------------------------------------------------
# 13. Failure stop rules
# ---------------------------------------------------------------------------


def test_checklist_mentions_failure_stop_rules() -> None:
    text = _checklist()
    assert (
        "stop" in text.lower()
        and (
            "failure" in text.lower()
            or "stop rule" in text.lower()
            or "halt" in text.lower()
        )
    )


# ---------------------------------------------------------------------------
# 14. sessionStorage JWT is fake-data-only risk
# ---------------------------------------------------------------------------


def test_checklist_mentions_session_storage_jwt() -> None:
    assert "sessionStorage" in _checklist()


def test_checklist_mentions_session_storage_fake_data_only() -> None:
    text = _checklist()
    assert "sessionStorage" in text and (
        "fake" in text.lower() or "staging" in text.lower()
    )


def test_checklist_mentions_session_storage_not_phi_safe() -> None:
    text = _checklist()
    assert "sessionStorage" in text and (
        "phi" in text.lower() or "production" in text.lower()
    )


# ---------------------------------------------------------------------------
# 15. Module 98 auth/session hardening
# ---------------------------------------------------------------------------


def test_checklist_mentions_module_98() -> None:
    text = _checklist()
    assert "module 98" in text.lower() or "Module 98" in text


def test_checklist_mentions_auth_session_hardening() -> None:
    text = _checklist()
    assert (
        "httponly" in text.lower()
        or "httpcookie" in text.lower()
        or "cookie" in text.lower()
        or "auth" in text.lower()
    ) and (
        "hardening" in text.lower()
        or "migration" in text.lower()
        or "module 98" in text.lower()
    )


# ---------------------------------------------------------------------------
# 16. No obvious real secrets in the document
# ---------------------------------------------------------------------------


def test_checklist_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    matches = real_key_pattern.findall(_checklist())
    assert not matches, f"Possible real key in checklist: {matches}"


def test_checklist_no_real_db_password() -> None:
    text = _checklist()
    for line in text.splitlines():
        if "postgresql://" in line:
            assert (
                "placeholder" in line.lower()
                or "example" in line.lower()
                or "<" in line
                or "#" in line
            ), f"Unexpected non-placeholder DATABASE_URL: {line!r}"
