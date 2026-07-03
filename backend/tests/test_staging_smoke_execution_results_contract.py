"""
Static contract tests for Sprint 14 / Module 104 — Staging Smoke Execution Results.

Verifies:
- Staging smoke results doc exists and covers all required sections
- Accuracy boundary is maintained (BLOCKED/PENDING if no services; no fabricated evidence)
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
    _REPO_ROOT, "docs", "runtime", "STAGING_SMOKE_EXECUTION_RESULTS.md"
)


def _doc() -> str:
    with open(_DOC_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Doc existence and size
# ---------------------------------------------------------------------------


def test_staging_smoke_execution_results_doc_exists() -> None:
    assert os.path.isfile(_DOC_PATH), f"Results doc not found at {_DOC_PATH}"


def test_doc_not_empty() -> None:
    assert len(_doc()) > 3000


# ---------------------------------------------------------------------------
# 2. Accuracy boundary — PASS/BLOCKED/PENDING
# ---------------------------------------------------------------------------


def test_doc_mentions_pass_blocked_pending_accuracy_boundary() -> None:
    text = _doc().upper()
    assert "PASS" in text and ("BLOCKED" in text or "PENDING" in text)


def test_doc_mentions_no_fabricated_evidence() -> None:
    text = _doc().lower()
    assert (
        "fabricat" in text
        or "no fabricated" in text
        or "invented" in text
        or "not fabricat" in text
    )


# ---------------------------------------------------------------------------
# 3. Platform coverage
# ---------------------------------------------------------------------------


def test_doc_mentions_railway_backend() -> None:
    text = _doc().lower()
    assert "railway" in text and "backend" in text


def test_doc_mentions_railway_postgresql() -> None:
    text = _doc().lower()
    assert "railway" in text and "postgresql" in text


def test_doc_mentions_vercel_frontend() -> None:
    text = _doc().lower()
    assert "vercel" in text and "frontend" in text


def test_doc_mentions_staging_api_https_url() -> None:
    text = _doc().lower()
    assert "staging" in text and "api" in text and (
        "https" in text or "url" in text
    )


def test_doc_mentions_staging_frontend_https_url() -> None:
    text = _doc().lower()
    assert "staging" in text and "frontend" in text and (
        "https" in text or "url" in text or "vercel" in text
    )


# ---------------------------------------------------------------------------
# 4. Smoke check coverage
# ---------------------------------------------------------------------------


def test_doc_mentions_backend_health() -> None:
    text = _doc().lower()
    assert "/health" in text or "health" in text


def test_doc_mentions_migrations() -> None:
    assert "migration" in _doc().lower()


def test_doc_mentions_frontend_login() -> None:
    assert "/login" in _doc()


def test_doc_mentions_cors() -> None:
    assert "cors" in _doc().lower()


def test_doc_mentions_fake_staging_user() -> None:
    text = _doc().lower()
    assert (
        "doctor.staging@praximed.test" in text
        or "fake staging user" in text
        or "staging fake user" in text
    )


def test_doc_mentions_vapi_test_assistant() -> None:
    text = _doc().lower()
    assert "vapi" in text and (
        "test assistant" in text or "staging" in text
    )


def test_doc_mentions_vapi_tool_scope() -> None:
    text = _doc().lower()
    assert "vapi:tool" in text or "vapi tool" in text or "vapi test assistant" in text


def test_doc_mentions_n8n_staging_workflow() -> None:
    text = _doc().lower()
    assert "n8n" in text and "staging" in text


def test_doc_mentions_staff_confirm_no_auto_confirmation() -> None:
    text = _doc().lower()
    assert (
        "staff confirm" in text
        or "no auto-confirm" in text
        or "no auto-confirmation" in text
        or "no code path auto-confirms" in text
        or (
            "confirm" in text
            and ("auto" in text or "action_required" in text)
        )
    )


# ---------------------------------------------------------------------------
# 5. Data safety
# ---------------------------------------------------------------------------


def test_doc_mentions_no_real_patient_data() -> None:
    text = _doc().lower()
    assert (
        "no real patient" in text
        or "fake" in text and "patient" in text
        or "non-phi" in text
    )


def test_doc_mentions_no_production_secrets() -> None:
    text = _doc().lower()
    assert (
        "no production secrets" in text
        or (
            "production" in text
            and ("secret" in text or "no " in text or "must not" in text)
        )
    )


def test_doc_mentions_no_ngrok_in_staging() -> None:
    text = _doc().lower()
    assert "ngrok" in text


def test_doc_mentions_no_wildcard_cors() -> None:
    text = _doc().lower()
    assert "wildcard" in text and "cors" in text


# ---------------------------------------------------------------------------
# 6. Evidence and blockers
# ---------------------------------------------------------------------------


def test_doc_mentions_evidence_required_or_available() -> None:
    text = _doc().lower()
    assert "evidence" in text and (
        "required" in text or "available" in text or "not available" in text
    )


def test_doc_mentions_blockers_or_preconditions() -> None:
    text = _doc().lower()
    assert "blocker" in text or "precondition" in text


# ---------------------------------------------------------------------------
# 7. Next step
# ---------------------------------------------------------------------------


def test_doc_mentions_architecture_checkpoint_14() -> None:
    text = _doc().lower()
    assert "architecture checkpoint 14" in text or "checkpoint 14" in text


# ---------------------------------------------------------------------------
# 8. No obvious real secrets
# ---------------------------------------------------------------------------


def test_doc_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_doc())
