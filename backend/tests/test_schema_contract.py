"""
Schema contract tests for backend/app/db/schema.sql

All assertions are made against the raw SQL text — no database connection
is required.  The tests are intentionally structural rather than
semantic: they prove the schema file contains exactly the tables, columns,
indexes, constraints, and foreign keys specified in the Sprint 1 / Module 3
contract so that regressions are caught before a migration is applied.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Load the SQL file once for the entire session.
# ---------------------------------------------------------------------------

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "app" / "db" / "schema.sql"
)


@pytest.fixture(scope="session")
def sql() -> str:
    assert _SCHEMA_PATH.is_file(), f"schema.sql not found at {_SCHEMA_PATH}"
    return _SCHEMA_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def sql_lower(sql: str) -> str:
    """Case-folded copy used for case-insensitive substring checks."""
    return sql.lower()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _table_block(sql_lower: str, table_name: str) -> str:
    """
    Extract the CREATE TABLE … ; block for *table_name* from the lowercased
    SQL so column and constraint assertions are scoped to the right table
    (avoids false positives from same-named columns in other tables).

    Returns the slice from 'create table … <table_name>' up to the next
    semicolon, or raises AssertionError if the table is not found.
    """
    pattern = rf"create\s+table\s+(?:if\s+not\s+exists\s+)?{re.escape(table_name)}\s*\("
    match = re.search(pattern, sql_lower)
    assert match, f"Table '{table_name}' not found in schema.sql"
    start = match.start()
    end = sql_lower.index(";", start)
    return sql_lower[start:end]


# ---------------------------------------------------------------------------
# 1. All required table names exist
# ---------------------------------------------------------------------------

REQUIRED_TABLES = [
    "clinics",
    "clinic_users",
    "clinic_calendar_connections",
    "clinic_calendar_blocks",
    "clinic_calendar_sync_events",
    "audit_log",
    "clinic_call_logs",
]


@pytest.mark.parametrize("table", REQUIRED_TABLES)
def test_table_exists(sql_lower: str, table: str):
    pattern = rf"create\s+table\s+(?:if\s+not\s+exists\s+)?{re.escape(table)}\s*\("
    assert re.search(pattern, sql_lower), (
        f"Expected 'CREATE TABLE … {table}' not found in schema.sql"
    )


# ---------------------------------------------------------------------------
# 2. Critical columns exist in each table
# ---------------------------------------------------------------------------

# Map of table → required column names (all lowercase)
REQUIRED_COLUMNS: dict[str, list[str]] = {
    "clinics": [
        "id", "slug", "name", "status", "config_path",
        "config_version", "timezone", "locale", "created_at", "updated_at",
    ],
    "clinic_users": [
        "id", "clinic_id", "email", "full_name", "role",
        "status", "created_at", "updated_at",
    ],
    "clinic_calendar_connections": [
        "id", "clinic_id", "provider", "external_calendar_id",
        "sync_status", "last_synced_at", "created_at", "updated_at",
    ],
    "clinic_calendar_blocks": [
        "id", "clinic_id", "connection_id", "external_event_id",
        "title", "block_type", "starts_at", "ends_at",
        "is_all_day", "source", "raw_payload", "created_at", "updated_at",
    ],
    "clinic_calendar_sync_events": [
        "id", "clinic_id", "connection_id", "event_type",
        "status", "message", "raw_payload", "created_at",
    ],
    "audit_log": [
        "id", "clinic_id", "actor_type", "actor_id", "action",
        "resource_type", "resource_id", "metadata", "created_at",
    ],
    "clinic_call_logs": [
        "id", "clinic_id", "provider", "external_call_id",
        "caller_phone", "direction", "call_status",
        "started_at", "ended_at", "duration_seconds",
        "transcript_text", "summary", "action_required",
        "urgency_level", "raw_payload", "created_at", "updated_at",
    ],
}


@pytest.mark.parametrize("table,column", [
    (table, col)
    for table, cols in REQUIRED_COLUMNS.items()
    for col in cols
])
def test_column_exists(sql_lower: str, table: str, column: str):
    block = _table_block(sql_lower, table)
    assert column in block, (
        f"Column '{column}' not found in CREATE TABLE {table} block"
    )


# ---------------------------------------------------------------------------
# 3. Required indexes exist
# ---------------------------------------------------------------------------

REQUIRED_INDEXES = [
    # (partial name that must appear in an ON … clause, table, columns)
    ("idx_clinics_slug",                          "clinics",                      "slug"),
    ("idx_clinics_status",                        "clinics",                      "status"),
    ("idx_clinic_users_clinic_id",                "clinic_users",                 "clinic_id"),
    ("idx_clinic_calendar_connections_clinic_id", "clinic_calendar_connections",  "clinic_id"),
    ("idx_clinic_calendar_blocks_clinic_time",    "clinic_calendar_blocks",       "starts_at"),
    ("idx_clinic_calendar_blocks_clinic_type",    "clinic_calendar_blocks",       "block_type"),
    ("idx_clinic_calendar_sync_events_clinic_created", "clinic_calendar_sync_events", "created_at"),
    ("idx_audit_log_clinic_created",              "audit_log",                    "created_at"),
    ("idx_clinic_call_logs_clinic_created",       "clinic_call_logs",             "created_at"),
    ("idx_clinic_call_logs_clinic_status",        "clinic_call_logs",             "call_status"),
    ("idx_clinic_call_logs_clinic_action",        "clinic_call_logs",             "action_required"),
    ("idx_clinic_call_logs_clinic_urgency",       "clinic_call_logs",             "urgency_level"),
]


@pytest.mark.parametrize("idx_name,table,column", REQUIRED_INDEXES)
def test_index_exists(sql_lower: str, idx_name: str, table: str, column: str):
    # The index definition must mention the index name, the table, and the column.
    assert idx_name in sql_lower, (
        f"Index '{idx_name}' not found in schema.sql"
    )
    # Find the CREATE INDEX line and verify it references the expected table.
    pattern = rf"create\s+index\s+(?:if\s+not\s+exists\s+)?{re.escape(idx_name)}\s+on\s+{re.escape(table)}"
    assert re.search(pattern, sql_lower), (
        f"Index '{idx_name}' does not reference table '{table}'"
    )
    # Verify the indexed column appears in the index definition.
    idx_match = re.search(
        rf"create\s+index\s+(?:if\s+not\s+exists\s+)?{re.escape(idx_name)}.*?;",
        sql_lower,
        re.DOTALL,
    )
    assert idx_match, f"Could not extract index block for '{idx_name}'"
    assert column in idx_match.group(), (
        f"Column '{column}' not found in index '{idx_name}'"
    )


# ---------------------------------------------------------------------------
# 4. clinic_calendar_blocks CHECK constraint (ends_at > starts_at)
# ---------------------------------------------------------------------------


def test_calendar_blocks_check_ends_after_starts(sql_lower: str):
    block = _table_block(sql_lower, "clinic_calendar_blocks")
    # The CHECK expression must contain both column names and the > operator.
    assert "check" in block, (
        "No CHECK constraint found in clinic_calendar_blocks"
    )
    assert "ends_at" in block and "starts_at" in block, (
        "CHECK constraint in clinic_calendar_blocks must reference ends_at and starts_at"
    )
    # Verify the direction: ends_at > starts_at (not the reverse)
    check_match = re.search(r"check\s*\(([^)]+)\)", block)
    assert check_match, "Could not parse CHECK expression in clinic_calendar_blocks"
    expr = check_match.group(1)
    assert re.search(r"ends_at\s*>\s*starts_at", expr), (
        f"CHECK expression must be 'ends_at > starts_at', got: {expr!r}"
    )


# ---------------------------------------------------------------------------
# 5. Foreign keys reference clinics(id)
# ---------------------------------------------------------------------------

# Tables that must have a FK to clinics(id)
FK_TABLES = [
    "clinic_users",
    "clinic_calendar_connections",
    "clinic_calendar_blocks",
    "clinic_calendar_sync_events",
    "audit_log",
    "clinic_call_logs",
]


@pytest.mark.parametrize("table", FK_TABLES)
def test_foreign_key_references_clinics(sql_lower: str, table: str):
    block = _table_block(sql_lower, table)
    # The FK declaration must name clinics(id) as the referenced table/column.
    assert re.search(r"references\s+clinics\s*\(\s*id\s*\)", block), (
        f"Table '{table}' must have a REFERENCES clinics(id) foreign key"
    )


# ---------------------------------------------------------------------------
# 6. UUID primary keys — every table must declare id as UUID PRIMARY KEY
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("table", REQUIRED_TABLES)
def test_uuid_primary_key(sql_lower: str, table: str):
    block = _table_block(sql_lower, table)
    assert re.search(r"\bid\b\s+uuid\s+primary\s+key", block), (
        f"Table '{table}' must declare 'id UUID PRIMARY KEY'"
    )


# ---------------------------------------------------------------------------
# 7. TIMESTAMPTZ used for timestamp columns (not bare TIMESTAMP)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("table", REQUIRED_TABLES)
def test_timestamps_are_timestamptz(sql_lower: str, table: str):
    block = _table_block(sql_lower, table)
    # All timestamp columns must use TIMESTAMPTZ.
    # Ensure bare TIMESTAMP (without TZ) does not appear for our columns.
    # Strategy: find every occurrence of a timestamp type and assert none
    # is the bare form.
    bare = re.findall(r"\btimestamp\b(?!\s*tz\b)(?!\s*with\b)", block)
    assert not bare, (
        f"Table '{table}' uses bare TIMESTAMP instead of TIMESTAMPTZ: {bare}"
    )


# ---------------------------------------------------------------------------
# 8. UNIQUE constraints
# ---------------------------------------------------------------------------


def test_clinics_slug_is_unique(sql_lower: str):
    block = _table_block(sql_lower, "clinics")
    assert re.search(r"\bslug\b.*\bunique\b|\bunique\b.*\bslug\b", block), (
        "clinics.slug must be declared UNIQUE"
    )


def test_clinic_users_unique_clinic_email(sql_lower: str):
    block = _table_block(sql_lower, "clinic_users")
    assert re.search(r"unique\s*\(\s*clinic_id\s*,\s*email\s*\)", block), (
        "clinic_users must have UNIQUE(clinic_id, email)"
    )


def test_calendar_connections_unique_triple(sql_lower: str):
    block = _table_block(sql_lower, "clinic_calendar_connections")
    assert re.search(
        r"unique\s*\(\s*clinic_id\s*,\s*provider\s*,\s*external_calendar_id\s*\)",
        block,
    ), "clinic_calendar_connections must have UNIQUE(clinic_id, provider, external_calendar_id)"


# ---------------------------------------------------------------------------
# 9. ON DELETE behaviour for foreign keys
# ---------------------------------------------------------------------------

ON_DELETE_CASCADE_TABLES = [
    ("clinic_users",                 "on delete cascade"),
    ("clinic_calendar_connections",  "on delete cascade"),
    ("clinic_calendar_blocks",       "on delete cascade"),
    ("clinic_calendar_sync_events",  "on delete cascade"),
    ("clinic_call_logs",             "on delete cascade"),
]


@pytest.mark.parametrize("table,expected", ON_DELETE_CASCADE_TABLES)
def test_fk_on_delete_cascade(sql_lower: str, table: str, expected: str):
    block = _table_block(sql_lower, table)
    assert expected in block, (
        f"Table '{table}' FK to clinics must include '{expected.upper()}'"
    )


def test_audit_log_fk_on_delete_set_null(sql_lower: str):
    block = _table_block(sql_lower, "audit_log")
    assert "on delete set null" in block, (
        "audit_log FK to clinics must be ON DELETE SET NULL"
    )


def test_call_logs_unique_triple(sql_lower: str):
    block = _table_block(sql_lower, "clinic_call_logs")
    assert re.search(
        r"unique\s*\(\s*clinic_id\s*,\s*provider\s*,\s*external_call_id\s*\)",
        block,
    ), "clinic_call_logs must have UNIQUE(clinic_id, provider, external_call_id)"
