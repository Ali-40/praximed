"""
Static contract tests for Sprint 15 / Module 107 — Vercel Frontend Project Creation
Runbook.

Verifies:
- Runbook doc and evidence doc exist and cover all required sections
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
    "VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md",
)

_EVIDENCE_PATH = os.path.join(
    _REPO_ROOT,
    "docs",
    "runtime",
    "VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md",
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


def test_runbook_doc_exists() -> None:
    assert os.path.isfile(_RUNBOOK_PATH), f"Runbook not found at {_RUNBOOK_PATH}"


def test_evidence_doc_exists() -> None:
    assert os.path.isfile(_EVIDENCE_PATH), f"Evidence doc not found at {_EVIDENCE_PATH}"


def test_runbook_not_empty() -> None:
    assert len(_runbook()) > 3000


def test_evidence_not_empty() -> None:
    assert len(_evidence()) > 1000


# ---------------------------------------------------------------------------
# 2. Vercel frontend project coverage
# ---------------------------------------------------------------------------


def test_runbook_mentions_vercel_frontend_project() -> None:
    text = _runbook().lower()
    assert "vercel" in text and "frontend" in text


def test_runbook_mentions_no_claude_deployment() -> None:
    text = _runbook().lower()
    assert (
        "no claude" in text
        or "not deploy" in text
        or "human-executable" in text
        or "no deployment" in text
    )


# ---------------------------------------------------------------------------
# 3. Data safety
# ---------------------------------------------------------------------------


def test_runbook_mentions_fake_non_phi_staging() -> None:
    text = _runbook().lower()
    assert ("fake" in text or "non-phi" in text) and "staging" in text


def test_runbook_mentions_no_production_launch() -> None:
    text = _runbook().lower()
    assert "production" in text and (
        "no production" in text
        or "not yet" in text
        or "never" in text
        or "must not" in text
        or "staging only" in text
    )


# ---------------------------------------------------------------------------
# 4. Root directory = frontend (critical)
# ---------------------------------------------------------------------------


def test_runbook_mentions_root_directory_frontend() -> None:
    text = _runbook().lower()
    assert "root directory" in text and "frontend" in text


def test_runbook_root_directory_is_critical() -> None:
    text = _runbook().lower()
    assert "critical" in text or "required" in text or "must" in text


# ---------------------------------------------------------------------------
# 5. Next.js auto-detect and build settings
# ---------------------------------------------------------------------------


def test_runbook_mentions_nextjs_auto_detect() -> None:
    text = _runbook().lower()
    assert "next.js" in text and (
        "auto" in text or "auto-detect" in text or "detect" in text
    )


def test_runbook_mentions_npm_run_build() -> None:
    assert "npm run build" in _runbook()


# ---------------------------------------------------------------------------
# 6. NEXT_PUBLIC_API_BASE_URL
# ---------------------------------------------------------------------------


def test_runbook_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _runbook()


def test_runbook_mentions_railway_backend_https_url() -> None:
    text = _runbook().lower()
    assert "railway" in text and (
        "https" in text or "backend url" in text or "backend https" in text
    )


def test_runbook_mentions_public_build_time_variable() -> None:
    text = _runbook().lower()
    assert (
        "build-time" in text
        or "build time" in text
        or "baked" in text
        or "public" in text
    ) and (
        "not a secret" in text
        or "public variable" in text
        or "public var" in text
        or "browser" in text
    )


# ---------------------------------------------------------------------------
# 7. No backend secrets in Vercel env
# ---------------------------------------------------------------------------


def test_runbook_mentions_no_backend_secrets_in_vercel_env() -> None:
    text = _runbook().lower()
    assert (
        "no backend secret" in text
        or "must not" in text
        or "never" in text
        or "forbidden" in text
    ) and "vercel" in text


def test_runbook_forbids_database_url_in_vercel() -> None:
    assert "DATABASE_URL" in _runbook()


def test_runbook_forbids_jwt_secret_in_vercel() -> None:
    assert "JWT_SECRET_KEY" in _runbook()


# ---------------------------------------------------------------------------
# 8. FRONTEND_CORS_ORIGINS dependency
# ---------------------------------------------------------------------------


def test_runbook_mentions_frontend_cors_origins_dependency() -> None:
    text = _runbook().lower()
    assert "frontend_cors_origins" in text and (
        "module 108" in text or "cors" in text
    )


def test_runbook_mentions_cors_dependency_on_vercel_url() -> None:
    text = _runbook().lower()
    assert "cors" in text and (
        "vercel url" in text
        or "vercel.app" in text
        or "after" in text
        or "before" in text
        or "depends" in text
    )


# ---------------------------------------------------------------------------
# 9. Evidence capture
# ---------------------------------------------------------------------------


def test_runbook_mentions_evidence_capture() -> None:
    text = _runbook().lower()
    assert "evidence" in text and (
        "capture" in text or "record" in text or "document" in text
    )


def test_runbook_mentions_no_secret_values_in_evidence() -> None:
    text = _runbook().lower()
    assert (
        "no secret" in text
        or "not record" in text
        or "do not record" in text
        or "never record" in text
        or "sanitized" in text
    )


# ---------------------------------------------------------------------------
# 10. Stop rules
# ---------------------------------------------------------------------------


def test_runbook_mentions_stop_rules() -> None:
    text = _runbook().lower()
    assert "stop" in text and (
        "rule" in text or "stop if" in text or "stop rule" in text
    )


# ---------------------------------------------------------------------------
# 11. Result states
# ---------------------------------------------------------------------------


def test_runbook_mentions_pass_blocked_pending_fail_states() -> None:
    text = _runbook().upper()
    assert "PASS" in text and ("BLOCKED" in text or "PENDING" in text) and "FAIL" in text


# ---------------------------------------------------------------------------
# 12. Module 108 reference
# ---------------------------------------------------------------------------


def test_runbook_mentions_module_108() -> None:
    text = _runbook().lower()
    assert "module 108" in text


# ---------------------------------------------------------------------------
# 13. Evidence doc accuracy
# ---------------------------------------------------------------------------


def test_evidence_mentions_blocked_pending() -> None:
    text = _evidence().upper()
    assert "BLOCKED" in text or "PENDING" in text


# ---------------------------------------------------------------------------
# 14. No obvious real secrets
# ---------------------------------------------------------------------------


def test_runbook_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_runbook())


def test_evidence_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_evidence())
