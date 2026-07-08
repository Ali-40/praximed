"""
Contract tests for Sprint 20 / Module 149A — patient history migration JSONB defaults.

Validates that migration 0007 renders valid PostgreSQL JSONB defaults ('{}'::jsonb)
and does not contain the invalid escaped form ('{{}}'::jsonb) that caused the
Railway migration failure.

No real patient PHI. No secrets. Production PHI remains NO-GO.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
_MIGRATION = _REPO_ROOT / "backend/migrations/versions/0007_patient_history_data_model.py"
_SCHEMA_SQL = _REPO_ROOT / "backend/app/db/schema.sql"
_CURRENT_STATE = _REPO_ROOT / "docs/claude/CURRENT_STATE.md"


def _load_migration():
    spec = importlib.util.spec_from_file_location("m0007", str(_MIGRATION))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ── migration exists ─────────────────────────────────────────────────────────


def test_migration_0007_exists():
    assert _MIGRATION.exists()


def test_migration_revision_correct():
    src = _MIGRATION.read_text()
    assert 'revision = "0007_patient_history_data_model"' in src


# ── no invalid JSONB default in source ──────────────────────────────────────


def test_migration_source_no_double_brace_jsonb():
    src = _MIGRATION.read_text()
    assert "'{{}}'::jsonb" not in src, (
        "Migration source still contains invalid JSONB default '{{}}'::jsonb. "
        "Use '{}'::jsonb or _EMPTY_JSONB constant."
    )


def test_migration_source_no_quadruple_brace():
    src = _MIGRATION.read_text()
    assert "{{{{" not in src, "Unexpected quadruple-brace escaping found"


def test_schema_sql_no_double_brace_jsonb():
    src = _SCHEMA_SQL.read_text()
    assert "'{{}}'::jsonb" not in src


# ── rendered output is correct ───────────────────────────────────────────────


def test_common_cols_fhir_payload_renders_valid_jsonb():
    m = _load_migration()
    cols = m._common_cols()
    assert "'{}'::jsonb" in cols, "_common_cols() must render '{}'::jsonb for fhir_payload"
    assert "'{{}}'::jsonb" not in cols


def test_common_cols_metadata_renders_valid_jsonb():
    m = _load_migration()
    cols = m._common_cols()
    lines = [l for l in cols.splitlines() if "metadata" in l and "jsonb" in l.lower()]
    assert any("'{}'::jsonb" in l for l in lines), (
        "metadata column must render with valid DEFAULT '{}'::jsonb"
    )


def test_common_cols_renders_no_invalid_jsonb():
    m = _load_migration()
    cols = m._common_cols()
    assert "'{{}}'::jsonb" not in cols


def test_empty_jsonb_constant_value():
    m = _load_migration()
    assert m._EMPTY_JSONB == "'{}'::jsonb"


# ── schema.sql has valid defaults ────────────────────────────────────────────


def test_schema_sql_patient_history_allergies_jsonb_defaults():
    src = _SCHEMA_SQL.read_text()
    # Should find valid JSONB defaults in patient_history_allergies section
    assert "fhir_payload            JSONB       NOT NULL DEFAULT '{}'::jsonb" in src


def test_schema_sql_no_double_brace_anywhere_in_patient_history():
    src = _SCHEMA_SQL.read_text()
    # Extract only the patient_history section
    start = src.find("patient_history_allergies")
    if start == -1:
        return
    patient_section = src[start:]
    assert "'{{}}'::jsonb" not in patient_section


# ── safety invariants ────────────────────────────────────────────────────────


def test_migration_no_database_url():
    src = _MIGRATION.read_text()
    assert "DATABASE_URL" not in src


def test_migration_no_actual_sk_key():
    src = _MIGRATION.read_text()
    assert not re.search(r"sk-[A-Za-z0-9]{10,}", src)


def test_migration_production_phi_enabled_false():
    src = _MIGRATION.read_text()
    assert "production_phi_enabled" in src
    assert "false" in src.lower()


def test_schema_sql_production_phi_false_in_patient_history():
    src = _SCHEMA_SQL.read_text()
    assert "production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false" in src
