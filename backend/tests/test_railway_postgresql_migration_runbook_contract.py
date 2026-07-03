"""
Static contract tests for Sprint 15 / Module 106 — Railway PostgreSQL Provisioning
and Migration Evidence.

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
    "RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md",
)

_EVIDENCE_PATH = os.path.join(
    _REPO_ROOT,
    "docs",
    "runtime",
    "RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md",
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
# 2. Railway PostgreSQL coverage
# ---------------------------------------------------------------------------


def test_runbook_mentions_railway_postgresql() -> None:
    text = _runbook().lower()
    assert "railway" in text and "postgresql" in text


def test_runbook_mentions_add_on_or_plugin() -> None:
    text = _runbook().lower()
    assert "add-on" in text or "plugin" in text or "add on" in text


# ---------------------------------------------------------------------------
# 3. Data safety
# ---------------------------------------------------------------------------


def test_runbook_mentions_fake_non_phi_staging_only() -> None:
    text = _runbook().lower()
    assert ("fake" in text or "non-phi" in text) and "staging" in text


def test_runbook_mentions_no_production_db() -> None:
    text = _runbook().lower()
    assert "production" in text and (
        "no production" in text or "never" in text or "must not" in text or "not yet" in text
    )


def test_runbook_mentions_no_real_patient_data() -> None:
    text = _runbook().lower()
    assert "no real patient" in text or (
        "real" in text and "patient" in text and (
            "not" in text or "no " in text or "never" in text or "fake" in text
        )
    )


# ---------------------------------------------------------------------------
# 4. DATABASE_URL coverage
# ---------------------------------------------------------------------------


def test_runbook_mentions_database_url() -> None:
    assert "DATABASE_URL" in _runbook()


def test_runbook_mentions_database_url_auto_injected() -> None:
    text = _runbook().lower()
    assert "database_url" in text and (
        "auto" in text or "inject" in text or "reference" in text
    )


def test_runbook_mentions_no_local_docker_database_url() -> None:
    text = _runbook().lower()
    assert (
        "local docker" in text or "localhost" in text or "praxismed_local" in text
    ) and (
        "never" in text or "do not" in text or "must not" in text or "not use" in text
    )


def test_runbook_mentions_no_production_database_url() -> None:
    text = _runbook().lower()
    assert "production" in text and (
        "never" in text or "do not" in text or "must not" in text
    )


# ---------------------------------------------------------------------------
# 5. Migration command
# ---------------------------------------------------------------------------


def test_runbook_mentions_run_migrations_py() -> None:
    assert "python backend/scripts/run_migrations.py" in _runbook()


def test_runbook_mentions_migrations_not_in_procfile() -> None:
    text = _runbook().lower()
    assert "procfile" in text and "migration" in text and (
        "not" in text or "do not" in text or "must not" in text or "never" in text
    )


# ---------------------------------------------------------------------------
# 6. Evidence and safety
# ---------------------------------------------------------------------------


def test_runbook_mentions_sanitized_evidence() -> None:
    text = _runbook().lower()
    assert "sanitized" in text and ("evidence" in text or "output" in text)


def test_runbook_mentions_no_secrets() -> None:
    text = _runbook().lower()
    assert (
        "no secret" in text
        or "not print" in text
        or "do not print" in text
        or "never record" in text
        or "no connection string" in text
    )


# ---------------------------------------------------------------------------
# 7. Seed script assessment
# ---------------------------------------------------------------------------


def test_runbook_mentions_seed_local_data_py_local_only() -> None:
    text = _runbook()
    assert "seed_local_data.py" in text and (
        "local" in text.lower() or "local-dev" in text.lower()
    )


# ---------------------------------------------------------------------------
# 8. Result states
# ---------------------------------------------------------------------------


def test_runbook_mentions_pass_blocked_pending_fail_states() -> None:
    text = _runbook().upper()
    assert "PASS" in text and ("BLOCKED" in text or "PENDING" in text) and "FAIL" in text


# ---------------------------------------------------------------------------
# 9. Stop rules and failure triage
# ---------------------------------------------------------------------------


def test_runbook_mentions_stop_rules() -> None:
    text = _runbook().lower()
    assert "stop" in text and (
        "rule" in text or "stop if" in text or "stop rule" in text
    )


def test_runbook_mentions_failure_triage() -> None:
    text = _runbook().lower()
    assert "failure" in text and (
        "triage" in text or "cause" in text or "symptom" in text
    )


# ---------------------------------------------------------------------------
# 10. Evidence doc accuracy
# ---------------------------------------------------------------------------


def test_evidence_mentions_blocked_pending() -> None:
    text = _evidence().upper()
    assert "BLOCKED" in text or "PENDING" in text


# ---------------------------------------------------------------------------
# 11. Next step reference
# ---------------------------------------------------------------------------


def test_runbook_mentions_module_107_vercel() -> None:
    text = _runbook().lower()
    assert "module 107" in text and "vercel" in text


# ---------------------------------------------------------------------------
# 12. No obvious real secrets
# ---------------------------------------------------------------------------


def test_runbook_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_runbook())


def test_evidence_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_evidence())
