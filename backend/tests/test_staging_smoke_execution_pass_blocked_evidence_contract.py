"""
Static contract tests for Sprint 15 / Module 109 — Staging Smoke Execution
PASS/BLOCKED Evidence.

Verifies:
- Evidence doc exists and covers all required smoke sections
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

_EVIDENCE_PATH = os.path.join(
    _REPO_ROOT,
    "docs",
    "runtime",
    "STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md",
)


def _evidence() -> str:
    with open(_EVIDENCE_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Doc existence
# ---------------------------------------------------------------------------


def test_evidence_doc_exists() -> None:
    assert os.path.isfile(_EVIDENCE_PATH), f"Evidence doc not found at {_EVIDENCE_PATH}"


def test_evidence_not_empty() -> None:
    assert len(_evidence()) > 3000


# ---------------------------------------------------------------------------
# 2. PASS/BLOCKED/PENDING accuracy
# ---------------------------------------------------------------------------


def test_evidence_mentions_pass_blocked_pending() -> None:
    text = _evidence().upper()
    assert "PASS" in text and ("BLOCKED" in text or "PENDING" in text)


def test_evidence_mentions_no_fabricated_evidence() -> None:
    text = _evidence().lower()
    assert (
        "no fabricated" in text
        or "not fabricat" in text
        or "fabricating evidence" in text
        or "accuracy policy" in text
    )


# ---------------------------------------------------------------------------
# 3. Railway backend
# ---------------------------------------------------------------------------


def test_evidence_mentions_railway_backend() -> None:
    text = _evidence().lower()
    assert "railway" in text and "backend" in text


def test_evidence_mentions_railway_postgresql() -> None:
    text = _evidence().lower()
    assert "railway" in text and ("postgresql" in text or "database" in text)


# ---------------------------------------------------------------------------
# 4. Vercel frontend
# ---------------------------------------------------------------------------


def test_evidence_mentions_vercel_frontend() -> None:
    text = _evidence().lower()
    assert "vercel" in text and "frontend" in text


# ---------------------------------------------------------------------------
# 5. Health endpoint
# ---------------------------------------------------------------------------


def test_evidence_mentions_backend_health() -> None:
    text = _evidence().lower()
    assert "/health" in text


# ---------------------------------------------------------------------------
# 6. DATABASE_URL
# ---------------------------------------------------------------------------


def test_evidence_mentions_database_url() -> None:
    assert "DATABASE_URL" in _evidence()


# ---------------------------------------------------------------------------
# 7. Migrations
# ---------------------------------------------------------------------------


def test_evidence_mentions_migrations() -> None:
    text = _evidence().lower()
    assert "migration" in text


# ---------------------------------------------------------------------------
# 8. Fake staging clinic / user
# ---------------------------------------------------------------------------


def test_evidence_mentions_fake_staging_clinic_user() -> None:
    text = _evidence().lower()
    assert (
        "fake staging" in text
        or "staging fake" in text
        or "doctor.staging@praximed.test" in text
        or ("fake" in text and "clinic" in text)
    )


# ---------------------------------------------------------------------------
# 9. Login
# ---------------------------------------------------------------------------


def test_evidence_mentions_login() -> None:
    text = _evidence().lower()
    assert "/login" in text or "login" in text


# ---------------------------------------------------------------------------
# 10. CORS
# ---------------------------------------------------------------------------


def test_evidence_mentions_cors() -> None:
    text = _evidence().lower()
    assert "cors" in text


# ---------------------------------------------------------------------------
# 11. Dashboard
# ---------------------------------------------------------------------------


def test_evidence_mentions_dashboard() -> None:
    text = _evidence().lower()
    assert "dashboard" in text


# ---------------------------------------------------------------------------
# 12. Appointment Confirm
# ---------------------------------------------------------------------------


def test_evidence_mentions_appointment_confirm() -> None:
    text = _evidence().lower()
    assert (
        "confirm" in text
        or "appointment" in text
    )


# ---------------------------------------------------------------------------
# 13. Vapi test assistant
# ---------------------------------------------------------------------------


def test_evidence_mentions_vapi_test_assistant() -> None:
    text = _evidence().lower()
    assert "vapi" in text and (
        "test assistant" in text
        or "test call" in text
        or "test assistant" in text
        or "vapi test" in text
    )


def test_evidence_mentions_vapi_created_appointment_row() -> None:
    text = _evidence().lower()
    assert "vapi" in text and (
        "row" in text or "appointment_requests" in text or "created" in text
    )


# ---------------------------------------------------------------------------
# 14. status=new / action_required=True
# ---------------------------------------------------------------------------


def test_evidence_mentions_status_new_action_required() -> None:
    text = _evidence().lower()
    assert (
        "status=new" in text
        or "status='new'" in text
        or "status new" in text
        or "action_required" in text
    )


# ---------------------------------------------------------------------------
# 15. Staff Confirm / no auto-confirmation
# ---------------------------------------------------------------------------


def test_evidence_mentions_staff_confirm_no_auto_confirm() -> None:
    text = _evidence().lower()
    assert (
        "staff confirm" in text
        or "staff action" in text
        or "no auto-confirm" in text
        or "no auto" in text
        or "no automatic" in text
    )


# ---------------------------------------------------------------------------
# 16. n8n staging
# ---------------------------------------------------------------------------


def test_evidence_mentions_n8n_staging() -> None:
    text = _evidence().lower()
    assert "n8n" in text and (
        "staging" in text or "deferred" in text or "not enabled" in text
    )


# ---------------------------------------------------------------------------
# 17. Logs sanitized
# ---------------------------------------------------------------------------


def test_evidence_mentions_logs_sanitized() -> None:
    text = _evidence().lower()
    assert "log" in text and (
        "sanitized" in text or "no secrets" in text or "no pii" in text
    )


# ---------------------------------------------------------------------------
# 18. Rollback
# ---------------------------------------------------------------------------


def test_evidence_mentions_rollback() -> None:
    text = _evidence().lower()
    assert "rollback" in text


# ---------------------------------------------------------------------------
# 19. No real patient data
# ---------------------------------------------------------------------------


def test_evidence_mentions_no_real_patient_data() -> None:
    text = _evidence().lower()
    assert "no real patient" in text or (
        "real" in text and "patient" in text and (
            "not" in text or "no " in text or "never" in text or "fake" in text
        )
    )


# ---------------------------------------------------------------------------
# 20. No production secrets
# ---------------------------------------------------------------------------


def test_evidence_mentions_no_production_secrets() -> None:
    text = _evidence().lower()
    assert "no production secret" in text or (
        "production" in text and (
            "no secret" in text or "not" in text or "never" in text or "must not" in text
        )
    )


# ---------------------------------------------------------------------------
# 21. No ngrok in staging
# ---------------------------------------------------------------------------


def test_evidence_mentions_no_ngrok_in_staging() -> None:
    text = _evidence().lower()
    assert "ngrok" in text and (
        "no ngrok" in text or "not" in text or "never" in text
    )


# ---------------------------------------------------------------------------
# 22. No wildcard CORS
# ---------------------------------------------------------------------------


def test_evidence_mentions_no_wildcard_cors() -> None:
    text = _evidence().lower()
    assert "wildcard" in text and (
        "no wildcard" in text or "forbidden" in text or "never" in text or "must not" in text
    )


# ---------------------------------------------------------------------------
# 23. sessionStorage JWT risk
# ---------------------------------------------------------------------------


def test_evidence_mentions_sessionstorage_jwt_fake_data_only() -> None:
    text = _evidence().lower()
    assert "sessionstorage" in text and (
        "fake" in text or "staging" in text or "only" in text
    )


# ---------------------------------------------------------------------------
# 24. Architecture Checkpoint 15
# ---------------------------------------------------------------------------


def test_evidence_mentions_architecture_checkpoint_15() -> None:
    text = _evidence().lower()
    assert "architecture checkpoint 15" in text or "checkpoint 15" in text


# ---------------------------------------------------------------------------
# 25. No obvious real secrets
# ---------------------------------------------------------------------------


def test_evidence_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_evidence())
