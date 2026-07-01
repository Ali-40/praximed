# Sprint 4 / Module 41 — Database Migration Foundation

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–34: all committed.
- Sprint 3, Modules 35–40: all committed.
- Architecture Checkpoint 03: committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create the database migration foundation for PraxisMed.

## Purpose
PraxisMed currently has a strong schema contract in `backend/app/db/schema.sql`, but no migration system. Before real PostgreSQL setup, Vapi/n8n integration, frontend work, or pilots, the project needs a migration foundation so schema changes can be applied safely and versioned.

This module creates the migration scaffold and baseline migration only.

Do not connect to a real database.
Do not run real migrations against PostgreSQL.
Do not change the current database schema.
Do not modify production runtime behavior.
Do not create new tables beyond what already exists in schema.sql.

## Create or update only

1. `backend/alembic.ini`
2. `backend/migrations/env.py`
3. `backend/migrations/script.py.mako`
4. `backend/migrations/versions/0001_initial_schema.py`
5. `backend/tests/test_migration_contract.py`
6. `docs/claude/CURRENT_STATE.md`
7. `docs/claude/NEXT_MODULE.md`

## Migration requirements

1. Alembic-style migration scaffold.
2. Baseline migration of the current schema.sql state.
3. `revision = "0001_initial_schema"`, `down_revision = None`.
4. `upgrade()` creates all tables from schema.sql, including constraints, FKs, indexes.
5. `downgrade()` drops tables in safe reverse dependency order.
6. Static and deterministic — no real database required for tests.

## Acceptance criteria

- All Module 41 tests pass.
- All previous tests still pass.
- No real database connection used.
- No schema changes introduced.
- schema.sql remains unchanged.
- Commit only if all tests pass.

## Commit message

`Sprint 4 / Module 41 — Database migration foundation`
