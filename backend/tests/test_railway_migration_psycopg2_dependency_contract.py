"""
Sprint 16 / Module 113 — Railway migration psycopg2 dependency contract tests.

Static tests verifying that psycopg2-binary is present in both requirements files
and that migration docs accurately record the real failure and fix.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_REQ = ROOT / "backend" / "requirements.txt"
ROOT_REQ = ROOT / "requirements.txt"
MIGRATION_RUNBOOK = (
    ROOT
    / "docs"
    / "deployment"
    / "RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md"
)
MIGRATION_EVIDENCE = (
    ROOT / "docs" / "runtime" / "RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md"
)


# ---------------------------------------------------------------------------
# Root requirements.txt
# ---------------------------------------------------------------------------


def test_root_requirements_exists():
    assert ROOT_REQ.exists(), "requirements.txt must exist at repo root"


def test_root_requirements_contains_psycopg2_binary():
    text = ROOT_REQ.read_text()
    assert "psycopg2-binary" in text, (
        "root requirements.txt must contain psycopg2-binary "
        "(required by Alembic/SQLAlchemy for migrations)"
    )


def test_root_requirements_still_contains_asyncpg():
    text = ROOT_REQ.read_text()
    assert "asyncpg" in text, (
        "root requirements.txt must still contain asyncpg "
        "(required for runtime async DB access)"
    )


# ---------------------------------------------------------------------------
# backend/requirements.txt
# ---------------------------------------------------------------------------


def test_backend_requirements_exists():
    assert BACKEND_REQ.exists(), "backend/requirements.txt must exist"


def test_backend_requirements_contains_psycopg2_binary():
    text = BACKEND_REQ.read_text()
    assert "psycopg2-binary" in text, (
        "backend/requirements.txt must contain psycopg2-binary "
        "(kept in sync with root requirements)"
    )


def test_backend_requirements_still_contains_asyncpg():
    text = BACKEND_REQ.read_text()
    assert "asyncpg" in text, (
        "backend/requirements.txt must still contain asyncpg "
        "(runtime async driver must not be removed)"
    )


# ---------------------------------------------------------------------------
# Migration runbook
# ---------------------------------------------------------------------------


def test_migration_runbook_exists():
    assert MIGRATION_RUNBOOK.exists(), (
        "RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md must exist"
    )


def test_migration_runbook_mentions_psycopg2_binary():
    text = MIGRATION_RUNBOOK.read_text()
    assert "psycopg2-binary" in text, (
        "migration runbook must document psycopg2-binary requirement"
    )


def test_migration_runbook_mentions_asyncpg():
    text = MIGRATION_RUNBOOK.read_text()
    assert "asyncpg" in text, (
        "migration runbook must document asyncpg as the runtime async driver"
    )


def test_migration_runbook_mentions_module_not_found_error():
    text = MIGRATION_RUNBOOK.read_text()
    assert "ModuleNotFoundError" in text, (
        "migration runbook must document the real ModuleNotFoundError failure"
    )


def test_migration_runbook_mentions_run_migrations_script():
    text = MIGRATION_RUNBOOK.read_text()
    assert "python backend/scripts/run_migrations.py" in text, (
        "migration runbook must document the migration command"
    )


# ---------------------------------------------------------------------------
# Migration evidence doc
# ---------------------------------------------------------------------------


def test_migration_evidence_exists():
    assert MIGRATION_EVIDENCE.exists(), (
        "RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md must exist"
    )


def test_migration_evidence_records_psycopg2_failure():
    text = MIGRATION_EVIDENCE.read_text()
    assert "psycopg2" in text, (
        "migration evidence doc must record the real psycopg2 failure"
    )


def test_migration_evidence_no_secrets_policy():
    text = MIGRATION_EVIDENCE.read_text()
    assert "No secrets" in text or "no secrets" in text or "non-PHI" in text, (
        "migration evidence doc must confirm no secrets / non-PHI policy"
    )
