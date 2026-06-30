# Sprint 2 / Module 26 — Patient API Routes

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Module 24: patient schema contract committed.
- Sprint 2, Module 25: patient repository committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create API schemas and FastAPI routes for managing clinic patients.

## Purpose
PraxisMed needs patient API routes before building consultation sessions, audio transcription, AI summaries, doctor approval, and patient timelines.

## Create or update only

1. `backend/app/schemas/patients.py`
2. `backend/app/api/routes/patients.py`
3. `backend/app/api/router.py`
4. `backend/tests/test_patient_schemas.py`
5. `backend/tests/test_patient_routes.py`
6. `docs/claude/CURRENT_STATE.md`
7. `docs/claude/NEXT_MODULE.md`

Do not create consultation tables yet.
Do not create consultation API routes yet.
Do not create transcription code.
Do not create AI summary code.
Do not build frontend.
Do not build authentication.
Do not modify patient_repo.py unless absolutely required by tests.
Do not use a real database in tests.

## Schema requirements

### 1. `PatientCreate`
- `clinic_id`: str — must not be empty
- `full_name`: str — must not be empty
- `external_patient_id`: str | None = None
- `date_of_birth`: date | None = None
- `phone`: str | None = None
- `email`: str | None = None
- `preferred_language`: str = "de-AT" — must not be empty
- `status`: str = "active" — must be one of: active, inactive, archived
- `notes`: str | None = None
- `raw_payload`: dict | None = None

### 2. `PatientUpsertByExternalId`
- `clinic_id`: str — must not be empty
- `external_patient_id`: str — must not be empty
- `full_name`: str — must not be empty
- `date_of_birth`: date | None = None
- `phone`: str | None = None
- `email`: str | None = None
- `preferred_language`: str = "de-AT" — must not be empty
- `status`: str = "active" — must be one of: active, inactive, archived
- `notes`: str | None = None
- `raw_payload`: dict | None = None

### 3. `PatientUpdate`
- All fields optional
- At least one field must be provided
- `full_name`, if provided, must not be empty
- `preferred_language`, if provided, must not be empty
- `status`, if provided, must be one of: active, inactive, archived

### 4. `PatientResponse`
- `ok`: bool
- `patient`: dict | None = None
- `message`: str | None = None

### 5. `PatientListResponse`
- `ok`: bool
- `patients`: list[dict]
- `message`: str | None = None

## Routes requirements

### Endpoints

1. `POST /patients` — create_patient → PatientResponse
2. `POST /patients/upsert-by-external-id` — upsert_patient_by_external_id → PatientResponse
3. `GET /patients` — list_patients (query: clinic_id, status, search, limit=50) → PatientListResponse
4. `GET /patients/by-external-id/{external_patient_id}` — get_patient_by_external_id (query: clinic_id) → PatientResponse | 404
5. `GET /patients/{patient_id}` — get_patient_by_id (query: clinic_id) → PatientResponse | 404
6. `PATCH /patients/{patient_id}` — update_patient (query: clinic_id, body: PatientUpdate) → PatientResponse | 404
7. `POST /patients/{patient_id}/archive` — archive_patient (query: clinic_id) → PatientResponse | 404

### Error handling
- Missing db_pool → HTTP 503
- InvalidPatientError → HTTP 400
- Not found → HTTP 404
- Unexpected error → HTTP 500

## Tests required

### test_patient_schemas.py (12 tests)
1. Valid PatientCreate passes.
2. Empty clinic_id fails.
3. Empty full_name fails.
4. Empty preferred_language fails.
5. Invalid status fails.
6. Valid PatientUpsertByExternalId passes.
7. Empty external_patient_id fails.
8. Valid PatientUpdate passes.
9. Empty PatientUpdate fails.
10. PatientUpdate invalid status fails.
11. PatientResponse accepts patient dict.
12. PatientListResponse accepts list of dicts.

### test_patient_routes.py (19 tests)
1. POST /patients returns 200.
2. POST route calls create_patient.
3. POST /patients/upsert-by-external-id returns 200.
4. Upsert route calls upsert_patient_by_external_id.
5. GET /patients returns 200 list.
6. GET list passes status/search/limit filters.
7. GET /patients/{patient_id} returns 200 when found.
8. GET /patients/{patient_id} returns 404 when repo returns None.
9. GET /patients/by-external-id/{external_patient_id} returns 200 when found.
10. GET /patients/by-external-id/{external_patient_id} returns 404 when not found.
11. PATCH /patients/{patient_id} returns 200.
12. PATCH /patients/{patient_id} returns 404 when repo returns None.
13. POST /patients/{patient_id}/archive returns 200.
14. POST /patients/{patient_id}/archive returns 404 when repo returns None.
15. Missing db_pool returns HTTP 503.
16. Invalid request body returns HTTP 422.
17. Repository validation error maps to HTTP 400.
18. Unexpected repository error maps to HTTP 500.
19. Existing health, Vapi, availability, appointment request, and notification routes still work.

## Run

```
pytest -v backend/tests/test_patient_schemas.py
pytest -v backend/tests/test_patient_routes.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 26 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Patient API routes are mounted.
- No consultation/session code yet.
- Commit all changes only if tests pass.

## Commit message

`Sprint 2 / Module 26 — Patient API routes`
