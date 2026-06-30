# Sprint 2 / Module 25 — Patient Repository

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Module 24: patient schema contract committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create the database repository layer for patients.

## Purpose
PraxisMed needs a clean patient repository before building patient API routes, consultation sessions, audio transcription, AI summaries, doctor approval, and patient timelines.

## Create or update only

1. `backend/app/db/repositories/patient_repo.py`
2. `backend/tests/test_patient_repo.py`
3. `docs/claude/CURRENT_STATE.md`
4. `docs/claude/NEXT_MODULE.md`

Do not create API routes yet.
Do not create consultation tables yet.
Do not create transcription code.
Do not create AI summary code.
Do not build frontend.
Do not build authentication.
Do not use a real database in tests.

## Allowed status values

`active`, `inactive`, `archived`

## Public async functions

### 1. `create_patient(pool, clinic_id, full_name, external_patient_id=None, date_of_birth=None, phone=None, email=None, preferred_language="de-AT", status="active", notes=None, raw_payload=None)`

- Validate `clinic_id` not empty.
- Validate `full_name` not empty.
- Validate `preferred_language` not empty.
- Validate `status` is one of allowed values.
- Parameterised SQL, INSERT, RETURNING *.

### 2. `upsert_patient_by_external_id(pool, clinic_id, external_patient_id, full_name, date_of_birth=None, phone=None, email=None, preferred_language="de-AT", status="active", notes=None, raw_payload=None)`

- Validate `clinic_id`, `external_patient_id`, `full_name` not empty.
- Validate `preferred_language` and `status`.
- ON CONFLICT (clinic_id, external_patient_id) DO UPDATE.
- Return created/updated row.

### 3. `get_patient_by_id(pool, clinic_id, patient_id)`
- Return matching patient or None. Filter by `clinic_id`.

### 4. `get_patient_by_external_id(pool, clinic_id, external_patient_id)`
- Return matching patient or None. Filter by `clinic_id`.

### 5. `list_patients(pool, clinic_id, status=None, search=None, limit=50)`
- Filter by `clinic_id`. Limit 1–100. Optional `status` and `search` filters.
- Search uses ILIKE across `full_name`, `phone`, `email`, `external_patient_id`.
- Validate `status` if provided.

### 6. `update_patient(pool, clinic_id, patient_id, full_name=None, date_of_birth=None, phone=None, email=None, preferred_language=None, status=None, notes=None, raw_payload=None)`
- Validate at least one update field provided.
- Validate `full_name` not empty if provided.
- Validate `preferred_language` not empty if provided.
- Validate `status` if provided. Filter by `clinic_id`.

### 7. `archive_patient(pool, clinic_id, patient_id)`
- Set `status='archived'`. Return updated row.

## Tests required

1. `create_patient` calls `fetchrow`.
2. `create_patient` raises `InvalidPatientError` for empty `clinic_id`.
3. `create_patient` raises `InvalidPatientError` for empty `full_name`.
4. `create_patient` raises `InvalidPatientError` for empty `preferred_language`.
5. `create_patient` validates invalid `status`.
6. `upsert_patient_by_external_id` calls `fetchrow`.
7. `upsert_patient_by_external_id` requires `external_patient_id`.
8. Upsert SQL uses `ON CONFLICT`.
9. `get_patient_by_id` calls `fetchrow` and filters by `clinic_id`.
10. `get_patient_by_external_id` calls `fetchrow` and filters by `clinic_id`.
11. `list_patients` calls `fetch`.
12. `list_patients` validates `limit`.
13. `list_patients` validates `status` filter.
14. `list_patients` supports `search` filter.
15. `update_patient` calls `fetchrow`.
16. `update_patient` validates at least one update field.
17. `update_patient` validates invalid `status`.
18. `update_patient` validates empty `full_name` if provided.
19. `archive_patient` calls `fetchrow`.
20. SQL uses parameterised placeholders, not string formatting.

## Run

```
pytest -v backend/tests/test_patient_repo.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 25 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Only `patient_repo.py`, its tests, and orchestration docs are changed.
- No API route yet.
- No consultation/session code yet.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 25 — Patient repository`
