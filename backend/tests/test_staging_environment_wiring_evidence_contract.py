"""
Static contract tests for Sprint 15 / Module 108 — Staging Environment Wiring Evidence.

Verifies:
- Wiring runbook and evidence doc exist and cover all required sections
- No obvious real secrets in either document
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
    _REPO_ROOT,
    "docs",
    "deployment",
    "STAGING_ENVIRONMENT_WIRING_RUNBOOK.md",
)

_EVIDENCE_PATH = os.path.join(
    _REPO_ROOT,
    "docs",
    "runtime",
    "STAGING_ENVIRONMENT_WIRING_EVIDENCE.md",
)


def _runbook() -> str:
    with open(_RUNBOOK_PATH, encoding="utf-8") as f:
        return f.read()


def _evidence() -> str:
    with open(_EVIDENCE_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Doc existence
# ---------------------------------------------------------------------------


def test_wiring_runbook_exists() -> None:
    assert os.path.isfile(_RUNBOOK_PATH), f"Runbook not found at {_RUNBOOK_PATH}"


def test_wiring_evidence_doc_exists() -> None:
    assert os.path.isfile(_EVIDENCE_PATH), f"Evidence doc not found at {_EVIDENCE_PATH}"


def test_runbook_not_empty() -> None:
    assert len(_runbook()) > 3000


def test_evidence_not_empty() -> None:
    assert len(_evidence()) > 1000


# ---------------------------------------------------------------------------
# 2. Staging environment coverage
# ---------------------------------------------------------------------------


def test_runbook_mentions_staging_environment_wiring() -> None:
    text = _runbook().lower()
    assert "staging" in text and ("wiring" in text or "environment" in text)


def test_runbook_mentions_fake_non_phi_staging() -> None:
    text = _runbook().lower()
    assert ("fake" in text or "non-phi" in text) and "staging" in text


def test_runbook_mentions_no_claude_deployment() -> None:
    text = _runbook().lower()
    assert (
        "no claude" in text
        or "no deployment" in text
        or "human-executable" in text
        or "not executed by claude" in text
    )


# ---------------------------------------------------------------------------
# 3. Railway backend
# ---------------------------------------------------------------------------


def test_runbook_mentions_railway_backend() -> None:
    text = _runbook().lower()
    assert "railway" in text and "backend" in text


def test_evidence_mentions_railway_backend() -> None:
    text = _evidence().lower()
    assert "railway" in text and "backend" in text


# ---------------------------------------------------------------------------
# 4. Railway PostgreSQL
# ---------------------------------------------------------------------------


def test_runbook_mentions_railway_postgresql() -> None:
    text = _runbook().lower()
    assert "railway" in text and "postgresql" in text


def test_evidence_mentions_railway_postgresql() -> None:
    text = _evidence().lower()
    assert "railway" in text and ("postgresql" in text or "database" in text)


# ---------------------------------------------------------------------------
# 5. Vercel frontend
# ---------------------------------------------------------------------------


def test_runbook_mentions_vercel_frontend() -> None:
    text = _runbook().lower()
    assert "vercel" in text and "frontend" in text


def test_evidence_mentions_vercel_frontend() -> None:
    text = _evidence().lower()
    assert "vercel" in text and "frontend" in text


# ---------------------------------------------------------------------------
# 6. DATABASE_URL
# ---------------------------------------------------------------------------


def test_runbook_mentions_database_url() -> None:
    assert "DATABASE_URL" in _runbook()


def test_evidence_mentions_database_url() -> None:
    assert "DATABASE_URL" in _evidence()


# ---------------------------------------------------------------------------
# 7. FRONTEND_CORS_ORIGINS
# ---------------------------------------------------------------------------


def test_runbook_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _runbook()


def test_evidence_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _evidence()


# ---------------------------------------------------------------------------
# 8. NEXT_PUBLIC_API_BASE_URL
# ---------------------------------------------------------------------------


def test_runbook_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _runbook()


def test_evidence_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _evidence()


# ---------------------------------------------------------------------------
# 9. Vapi endpoint
# ---------------------------------------------------------------------------


def test_runbook_mentions_vapi_endpoint() -> None:
    text = _runbook().lower()
    assert "vapi" in text and (
        "capture-appointment-request" in text
        or "/vapi/tools/" in text
        or "tool endpoint" in text
    )


def test_runbook_mentions_vapi_tool_scope() -> None:
    text = _runbook().lower()
    assert "vapi:tool" in text


# ---------------------------------------------------------------------------
# 10. n8n staging
# ---------------------------------------------------------------------------


def test_runbook_mentions_n8n_staging() -> None:
    text = _runbook().lower()
    assert "n8n" in text and "staging" in text


def test_evidence_mentions_n8n_staging() -> None:
    text = _evidence().lower()
    assert "n8n" in text


# ---------------------------------------------------------------------------
# 11. Health endpoint
# ---------------------------------------------------------------------------


def test_runbook_mentions_health_endpoint() -> None:
    text = _runbook().lower()
    assert "/health" in text


def test_evidence_mentions_health_endpoint() -> None:
    text = _evidence().lower()
    assert "/health" in text


# ---------------------------------------------------------------------------
# 12. Login
# ---------------------------------------------------------------------------


def test_runbook_mentions_login() -> None:
    text = _runbook().lower()
    assert "/login" in text or "login" in text


def test_evidence_mentions_login() -> None:
    text = _evidence().lower()
    assert "/login" in text or "login" in text


# ---------------------------------------------------------------------------
# 13. CORS
# ---------------------------------------------------------------------------


def test_runbook_mentions_cors() -> None:
    text = _runbook().lower()
    assert "cors" in text


def test_evidence_mentions_cors() -> None:
    text = _evidence().lower()
    assert "cors" in text


# ---------------------------------------------------------------------------
# 14. Migrations
# ---------------------------------------------------------------------------


def test_runbook_mentions_migrations() -> None:
    text = _runbook().lower()
    assert "migration" in text


def test_evidence_mentions_migrations() -> None:
    text = _evidence().lower()
    assert "migration" in text


# ---------------------------------------------------------------------------
# 15. Fake staging user
# ---------------------------------------------------------------------------


def test_runbook_mentions_fake_staging_user() -> None:
    text = _runbook().lower()
    assert (
        "doctor.staging@praximed.test" in text
        or ("fake" in text and "user" in text)
        or "staging fake" in text
    )


def test_evidence_mentions_fake_staging_user() -> None:
    text = _evidence().lower()
    assert (
        "doctor.staging@praximed.test" in text
        or ("fake" in text and "user" in text)
        or "staging fake" in text
    )


# ---------------------------------------------------------------------------
# 16. Staff Confirm / no auto-confirmation
# ---------------------------------------------------------------------------


def test_runbook_mentions_staff_confirm_no_auto_confirm() -> None:
    text = _runbook().lower()
    assert (
        "staff confirm" in text
        or "no auto-confirm" in text
        or "no automatic" in text
        or "auto-confirmation" in text
    )


def test_evidence_mentions_staff_confirm_no_auto_confirm() -> None:
    text = _evidence().lower()
    assert (
        "staff confirm" in text
        or "no auto-confirm" in text
        or "auto-confirm" in text
        or "action_required" in text
    )


# ---------------------------------------------------------------------------
# 17. No real patient data
# ---------------------------------------------------------------------------


def test_runbook_mentions_no_real_patient_data() -> None:
    text = _runbook().lower()
    assert "no real patient" in text or (
        "real" in text and "patient" in text and (
            "not" in text or "no " in text or "never" in text or "fake" in text
        )
    )


def test_evidence_mentions_no_real_patient_data() -> None:
    text = _evidence().lower()
    assert "no real patient" in text or (
        "real" in text and "patient" in text and (
            "not" in text or "no " in text or "never" in text or "fake" in text
        )
    )


# ---------------------------------------------------------------------------
# 18. No production secrets
# ---------------------------------------------------------------------------


def test_runbook_mentions_no_production_secrets() -> None:
    text = _runbook().lower()
    assert "no production secret" in text or (
        "production" in text and (
            "no secret" in text or "not" in text or "never" in text or "must not" in text
        )
    )


def test_evidence_mentions_no_production_secrets() -> None:
    text = _evidence().lower()
    assert "no production secret" in text or (
        "production" in text and (
            "no" in text or "not" in text or "never" in text
        )
    )


# ---------------------------------------------------------------------------
# 19. No ngrok in staging
# ---------------------------------------------------------------------------


def test_runbook_mentions_no_ngrok_in_staging() -> None:
    text = _runbook().lower()
    assert "ngrok" in text and (
        "not" in text or "no ngrok" in text or "never" in text or "not used" in text
    )


# ---------------------------------------------------------------------------
# 20. No wildcard CORS
# ---------------------------------------------------------------------------


def test_runbook_mentions_no_wildcard_cors() -> None:
    text = _runbook().lower()
    assert "wildcard" in text and (
        "no wildcard" in text or "forbidden" in text or "never" in text or "must not" in text
    )


def test_evidence_mentions_no_wildcard_cors() -> None:
    text = _evidence().lower()
    assert "wildcard" in text or "no wildcard" in text or (
        "cors" in text and ("*" in text or "wildcard" in text)
    )


# ---------------------------------------------------------------------------
# 21. PASS/BLOCKED/PENDING states
# ---------------------------------------------------------------------------


def test_runbook_mentions_pass_blocked_pending_states() -> None:
    text = _runbook().upper()
    assert "PASS" in text and ("BLOCKED" in text or "PENDING" in text)


def test_evidence_mentions_blocked_pending() -> None:
    text = _evidence().upper()
    assert "BLOCKED" in text or "PENDING" in text


# ---------------------------------------------------------------------------
# 22. No fabricated success
# ---------------------------------------------------------------------------


def test_runbook_mentions_no_fabricated_success() -> None:
    text = _runbook().lower()
    assert (
        "no fabricated" in text
        or "not fabricat" in text
        or "accuracy" in text
        or "blocked/pending" in text
    )


def test_evidence_mentions_no_fabricated_success() -> None:
    text = _evidence().lower()
    assert (
        "no fabricated" in text
        or "not fabricat" in text
        or "accuracy" in text
        or "no evidence is fabricated" in text
    )


# ---------------------------------------------------------------------------
# 23. Module 109 reference
# ---------------------------------------------------------------------------


def test_runbook_mentions_module_109_staging_smoke() -> None:
    text = _runbook().lower()
    assert "module 109" in text and (
        "smoke" in text or "staging smoke" in text
    )


# ---------------------------------------------------------------------------
# 24. No obvious real secrets
# ---------------------------------------------------------------------------


def test_runbook_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_runbook())


def test_evidence_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_evidence())
