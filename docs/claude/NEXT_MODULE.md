# Sprint 2 / Module 24 — Patient Schema Contract

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Architecture Checkpoint 01: committed.

Do not modify completed modules unless absolutely required.

## Task scope
Add the database schema contract for clinic patients.

## Purpose
PraxisMed needs a multi-tenant patient table before building consultation sessions, audio transcription, AI summaries, doctor approval, and patient timelines.

## Create or update only

1. `backend/app/db/schema.sql`
2. `backend/tests/test_schema_contract.py`
3. `docs/claude/CURRENT_STATE.md`
4. `docs/claude/NEXT_MODULE.md`

Do not create repository code yet.
Do not create API routes yet.
Do not create consultation tables yet.
Do not create transcription code.
Do not create AI summary code.
Do not build frontend.
Do not build authentication.
No real database connection during tests.

## Schema requirement

Add table: `patients`

### Required columns

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PRIMARY KEY |
| clinic_id | UUID NOT NULL | REFERENCES clinics(id) ON DELETE CASCADE |
| external_patient_id | TEXT | |
| full_name | TEXT NOT NULL | |
| date_of_birth | DATE | |
| phone | TEXT | |
| email | TEXT | |
| preferred_language | TEXT NOT NULL | DEFAULT 'de-AT' |
| status | TEXT NOT NULL | DEFAULT 'active' |
| notes | TEXT | |
| raw_payload | JSONB | |
| created_at | TIMESTAMPTZ NOT NULL | DEFAULT now() |
| updated_at | TIMESTAMPTZ NOT NULL | DEFAULT now() |

### Constraints

- `UNIQUE(clinic_id, external_patient_id)`
- `CHECK (status IN ('active', 'inactive', 'archived'))`
- `CHECK (preferred_language <> '')`
- `CHECK (full_name <> '')`

### Indexes

- `patients(clinic_id, created_at)`
- `patients(clinic_id, full_name)`
- `patients(clinic_id, date_of_birth)`
- `patients(clinic_id, phone)`
- `patients(clinic_id, email)`
- `patients(clinic_id, status)`
- `patients(clinic_id, external_patient_id)`

### Design rules

- Every patient belongs to exactly one clinic via `clinic_id`.
- This table stores patient identity/contact/admin data only.
- No clinical notes, consultation summaries, recordings, or diagnosis fields.
- Clinical history belongs in future consultation/session/timeline tables.
- Do not store secrets.

## Update test_schema_contract.py to verify

1. `patients` table exists.
2. All critical columns exist.
3. `clinic_id` references `clinics(id)`.
4. `UNIQUE(clinic_id, external_patient_id)` exists.
5. Status check constraint exists.
6. `preferred_language` non-empty check exists.
7. `full_name` non-empty check exists.
8. All required indexes exist.
9. Existing schema contract tests still pass.

## Run

```
pytest -v backend/tests/test_schema_contract.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 24 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Only schema contract and orchestration docs are changed.
- No repository code yet.
- No API route yet.
- No consultation/session code yet.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 24 — Patient schema contract`
