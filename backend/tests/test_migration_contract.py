"""Static contract tests for Module 41 — Database Migration Foundation.

These tests inspect migration files on disk without connecting to any database.
No asyncpg, no SQLAlchemy engine, no live PostgreSQL required.
"""

from __future__ import annotations

import ast
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BACKEND = Path(__file__).parent.parent
MIGRATIONS = BACKEND / "migrations"
VERSIONS = MIGRATIONS / "versions"
MIGRATION_FILE = VERSIONS / "0001_initial_schema.py"

# ---------------------------------------------------------------------------
# 1-4  Infrastructure files exist
# ---------------------------------------------------------------------------

def test_alembic_ini_exists():
    assert (BACKEND / "alembic.ini").is_file()


def test_env_py_exists():
    assert (MIGRATIONS / "env.py").is_file()


def test_script_mako_exists():
    assert (MIGRATIONS / "script.py.mako").is_file()


def test_migration_0001_exists():
    assert MIGRATION_FILE.is_file()


# ---------------------------------------------------------------------------
# 5-6  Revision identifiers
# ---------------------------------------------------------------------------

def test_revision_id():
    text = MIGRATION_FILE.read_text()
    assert 'revision = "0001_initial_schema"' in text


def test_down_revision_is_none():
    text = MIGRATION_FILE.read_text()
    assert "down_revision = None" in text


# ---------------------------------------------------------------------------
# 7-8  upgrade / downgrade functions present (AST)
# ---------------------------------------------------------------------------

def _migration_ast() -> ast.Module:
    return ast.parse(MIGRATION_FILE.read_text())


def _function_names() -> set[str]:
    tree = _migration_ast()
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


def test_upgrade_function_exists():
    assert "upgrade" in _function_names()


def test_downgrade_function_exists():
    assert "downgrade" in _function_names()


# ---------------------------------------------------------------------------
# 9  All 11 tables mentioned in migration text
# ---------------------------------------------------------------------------

EXPECTED_TABLES = [
    "clinics",
    "clinic_users",
    "clinic_calendar_connections",
    "clinic_calendar_blocks",
    "clinic_calendar_sync_events",
    "audit_log",
    "clinic_call_logs",
    "appointment_requests",
    "clinic_notifications",
    "patients",
    "consultation_sessions",
]


def test_all_tables_mentioned():
    text = MIGRATION_FILE.read_text()
    missing = [t for t in EXPECTED_TABLES if t not in text]
    assert not missing, f"Tables missing from migration: {missing}"


# ---------------------------------------------------------------------------
# 10  All 39 indexes mentioned
# ---------------------------------------------------------------------------

EXPECTED_INDEXES = [
    "idx_clinics_slug",
    "idx_clinics_status",
    "idx_clinic_users_clinic_id",
    "idx_clinic_calendar_connections_clinic_id",
    "idx_clinic_calendar_blocks_clinic_time",
    "idx_clinic_calendar_blocks_clinic_type",
    "idx_clinic_calendar_sync_events_clinic_created",
    "idx_audit_log_clinic_created",
    "idx_clinic_call_logs_clinic_created",
    "idx_clinic_call_logs_clinic_status",
    "idx_clinic_call_logs_clinic_action",
    "idx_clinic_call_logs_clinic_urgency",
    "idx_appointment_requests_clinic_created",
    "idx_appointment_requests_clinic_status",
    "idx_appointment_requests_clinic_action",
    "idx_appointment_requests_clinic_urgency",
    "idx_appointment_requests_clinic_preferred_starts",
    "idx_appointment_requests_clinic_source",
    "idx_clinic_notifications_clinic_created",
    "idx_clinic_notifications_clinic_status",
    "idx_clinic_notifications_clinic_priority",
    "idx_clinic_notifications_clinic_type",
    "idx_clinic_notifications_clinic_recipient",
    "idx_clinic_notifications_clinic_scheduled",
    "idx_clinic_notifications_clinic_resource",
    "idx_patients_clinic_created",
    "idx_patients_clinic_full_name",
    "idx_patients_clinic_dob",
    "idx_patients_clinic_phone",
    "idx_patients_clinic_email",
    "idx_patients_clinic_status",
    "idx_patients_clinic_external_id",
    "idx_consultation_sessions_clinic_created",
    "idx_consultation_sessions_clinic_patient",
    "idx_consultation_sessions_clinic_doctor",
    "idx_consultation_sessions_clinic_status",
    "idx_consultation_sessions_clinic_approval",
    "idx_consultation_sessions_clinic_approved_at",
    "idx_consultation_sessions_clinic_source",
]


def test_all_indexes_mentioned():
    text = MIGRATION_FILE.read_text()
    missing = [i for i in EXPECTED_INDEXES if i not in text]
    assert not missing, f"Indexes missing from migration: {missing}"


# ---------------------------------------------------------------------------
# 11-13  Structural keywords present
# ---------------------------------------------------------------------------

def test_foreign_key_references_present():
    text = MIGRATION_FILE.read_text()
    assert "REFERENCES" in text


def test_check_constraints_present():
    text = MIGRATION_FILE.read_text()
    assert "CHECK" in text


def test_unique_constraints_present():
    text = MIGRATION_FILE.read_text()
    assert "UNIQUE" in text


# ---------------------------------------------------------------------------
# 14-16  downgrade DROP TABLE order (children before parents)
# ---------------------------------------------------------------------------

def _downgrade_text() -> str:
    text = MIGRATION_FILE.read_text()
    # Extract everything after "def downgrade"
    marker = "def downgrade"
    idx = text.find(marker)
    assert idx != -1, "downgrade function not found"
    return text[idx:]


def test_consultation_sessions_dropped_before_patients():
    dg = _downgrade_text()
    assert dg.index("consultation_sessions") < dg.index("patients")


def test_patients_dropped_before_clinics():
    dg = _downgrade_text()
    assert dg.index("patients") < dg.index("clinics")


def test_child_tables_dropped_before_clinics():
    dg = _downgrade_text()
    clinics_pos = dg.rindex("clinics")  # last occurrence = the root table drop
    child_tables = [
        "consultation_sessions",
        "patients",
        "clinic_notifications",
        "appointment_requests",
        "clinic_call_logs",
        "audit_log",
        "clinic_calendar_sync_events",
        "clinic_calendar_blocks",
        "clinic_calendar_connections",
        "clinic_users",
    ]
    for table in child_tables:
        assert dg.index(table) < clinics_pos, (
            f"{table} must be dropped before clinics in downgrade()"
        )


# ---------------------------------------------------------------------------
# 17-18  env.py safety checks
# ---------------------------------------------------------------------------

def test_env_py_reads_database_url():
    text = (MIGRATIONS / "env.py").read_text()
    assert "DATABASE_URL" in text


def test_env_py_has_no_hardcoded_connection_string():
    text = (MIGRATIONS / "env.py").read_text()
    hardcoded_patterns = [
        "postgresql://",
        "postgresql+asyncpg://",
        "postgresql+psycopg2://",
        "postgres://",
    ]
    for pattern in hardcoded_patterns:
        assert pattern not in text, (
            f"env.py must not hard-code a connection string; found: {pattern!r}"
        )


# ---------------------------------------------------------------------------
# 19  asyncpg not imported during static test run
# ---------------------------------------------------------------------------

def test_asyncpg_not_imported_by_migration_files():
    """Migration infrastructure files must not import asyncpg directly."""
    for path in [MIGRATIONS / "env.py", MIGRATION_FILE]:
        text = path.read_text()
        assert "import asyncpg" not in text, (
            f"{path.name} must not import asyncpg"
        )


# ---------------------------------------------------------------------------
# 20  Migration file parses without syntax errors
# ---------------------------------------------------------------------------

def test_migration_file_parses_cleanly():
    source = MIGRATION_FILE.read_text()
    # ast.parse raises SyntaxError on failure
    tree = ast.parse(source)
    assert tree is not None


# ---------------------------------------------------------------------------
# 21-23  Revision ID length — alembic_version VARCHAR(32) constraint
# ---------------------------------------------------------------------------

def _all_migration_files() -> list[Path]:
    return [p for p in VERSIONS.glob("*.py") if p.name != "__init__.py"]


def _extract_revision(path: Path) -> str | None:
    """Return the value of the `revision` variable from a migration file."""
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith('revision = "') or stripped.startswith("revision = '"):
            # e.g.  revision = "0001_initial_schema"
            return stripped.split("=", 1)[1].strip().strip('"\'')
    return None


def test_all_revision_ids_fit_in_32_chars():
    """Test 21 — Every migration revision ID must be ≤32 characters (alembic_version constraint)."""
    for path in _all_migration_files():
        rev = _extract_revision(path)
        if rev is None:
            continue
        assert len(rev) <= 32, (
            f"{path.name}: revision {rev!r} is {len(rev)} chars — exceeds the 32-char "
            f"alembic_version VARCHAR(32) limit"
        )


def test_migration_0002_exists():
    """Test 22 — Migration 0002 (password_hash) file exists."""
    assert (VERSIONS / "0002_add_password_hash_to_clinic_users.py").is_file()


def test_migration_0002_revision_id_is_short():
    """Test 23 — Migration 0002 revision ID is ≤32 chars and matches expected value."""
    path = VERSIONS / "0002_add_password_hash_to_clinic_users.py"
    rev = _extract_revision(path)
    assert rev is not None, "Could not parse revision from 0002 migration file"
    assert rev == "0002_password_hash", (
        f"Expected revision '0002_password_hash', got {rev!r}"
    )
    assert len(rev) <= 32, f"revision {rev!r} is {len(rev)} chars — exceeds 32"
