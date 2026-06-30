# Sprint 1 / Module 17 — Appointment Request API Schemas and Routes

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
1. Module 1: config loader
2. Module 2: asyncpg pool
3. Module 3: PostgreSQL schema contract
4. Module 4: calendar repository
5. Module 5: availability engine
6. Module 6: calendar sync service
7. Module 7: FastAPI skeleton and health routes
8. Module 8: n8n calendar sync webhook route
9. Modules 9–10: availability schemas and API routes
10. Modules 11–12: Vapi prompt builder and tool routes
11. Modules 13–14: Vapi call logs and call event webhook
12. Module 15: appointment request schema contract
13. Module 16: appointment request repository

All are committed. Do not modify completed modules unless absolutely required.

## Task scope
Create API schemas and FastAPI routes for managing appointment requests.

Create or update only:
1. `backend/app/schemas/appointment_requests.py`
2. `backend/app/api/routes/appointment_requests.py`
3. `backend/app/api/router.py`
4. `backend/tests/test_appointment_request_schemas.py`
5. `backend/tests/test_appointment_request_routes.py`

Do not modify Vapi modules yet.
Do not build WhatsApp.
Do not build frontend.
Do not create authentication.
Do not use a real database in tests.

## Schemas required

### 1. `AppointmentRequestCreate`
Fields:
- `clinic_id: str`
- `source: str`
- `patient_name: str`
- `source_ref: str | None = None`
- `patient_phone: str | None = None`
- `patient_email: str | None = None`
- `date_of_birth: date | None = None`
- `reason: str | None = None`
- `preferred_starts_at: datetime | None = None`
- `preferred_ends_at: datetime | None = None`
- `urgency_level: str = "normal"`
- `raw_payload: dict | None = None`

Validation:
- `clinic_id` not empty
- `patient_name` not empty
- `source` in: `vapi`, `whatsapp`, `web`, `staff`, `system`
- `urgency_level` in: `low`, `normal`, `urgent`, `emergency`
- If both `preferred_starts_at` and `preferred_ends_at` are provided, `preferred_ends_at` must be after `preferred_starts_at`

### 2. `AppointmentRequestUpdateStatus`
Fields:
- `status: str`
- `action_required: bool | None = None`

Validation:
- `status` in: `new`, `confirmed`, `rejected`, `callback_needed`, `cancelled`, `archived`

### 3. `AppointmentRequestAssign`
Fields:
- `assigned_user_id: str`

Validation:
- `assigned_user_id` not empty

### 4. `AppointmentRequestResponse`
Fields:
- `ok: bool`
- `request: dict | None = None`
- `message: str | None = None`

### 5. `AppointmentRequestListResponse`
Fields:
- `ok: bool`
- `requests: list[dict]`
- `message: str | None = None`

## Routes required

### 1. `POST /appointment-requests`
- Accept `AppointmentRequestCreate`
- Use existing `get_db_pool` dependency
- Call `appointment_request_repo.create_appointment_request`
- Return `AppointmentRequestResponse`

### 2. `GET /appointment-requests`
Query params:
- `clinic_id: str`
- `status: str | None = None`
- `action_required: bool | None = None`
- `limit: int = 50`

- Call `appointment_request_repo.list_appointment_requests`
- Return `AppointmentRequestListResponse`

### 3. `GET /appointment-requests/{request_id}`
Query params:
- `clinic_id: str`

- Call `appointment_request_repo.get_appointment_request_by_id`
- If `None`, return 404
- Return `AppointmentRequestResponse`

### 4. `PATCH /appointment-requests/{request_id}/status`
Query params:
- `clinic_id: str`

Body:
- `AppointmentRequestUpdateStatus`

- Call `appointment_request_repo.update_appointment_request_status`
- Return `AppointmentRequestResponse`

### 5. `PATCH /appointment-requests/{request_id}/assign`
Query params:
- `clinic_id: str`

Body:
- `AppointmentRequestAssign`

- Call `appointment_request_repo.assign_appointment_request`
- Return `AppointmentRequestResponse`

### 6. `POST /appointment-requests/{request_id}/callback-needed`
Query params:
- `clinic_id: str`

- Call `appointment_request_repo.mark_callback_needed`
- Return `AppointmentRequestResponse`

### 7. `POST /appointment-requests/{request_id}/archive`
Query params:
- `clinic_id: str`

- Call `appointment_request_repo.archive_appointment_request`
- Return `AppointmentRequestResponse`

## Error handling
- Missing `db_pool` → HTTP 503 via existing dependency
- Invalid repository input (`InvalidAppointmentRequestError`) → HTTP 400
- Not found → HTTP 404
- Unexpected repository error → HTTP 500

## Tests for schemas
1. Valid create schema passes.
2. Empty `clinic_id` fails.
3. Empty `patient_name` fails.
4. Invalid `source` fails.
5. Invalid `urgency_level` fails.
6. Invalid preferred time range fails.
7. Valid status update passes.
8. Invalid status update fails.
9. Empty `assigned_user_id` fails.

## Tests for routes
Use FastAPI `TestClient`.
No real database.
Attach fake `db_pool` to `app.state`.
Use `monkeypatch` to mock `appointment_request_repo` functions.

Test cases:
1. `POST /appointment-requests` returns 200.
2. POST route calls `create_appointment_request`.
3. `GET /appointment-requests` returns 200 list.
4. GET list passes `status`/`action_required`/`limit` filters.
5. `GET /appointment-requests/{id}` returns 200 when found.
6. `GET /appointment-requests/{id}` returns 404 when repo returns `None`.
7. `PATCH` status route returns 200.
8. `PATCH` assign route returns 200.
9. `POST` callback-needed route returns 200.
10. `POST` archive route returns 200.
11. Missing `db_pool` returns 503.
12. Invalid request body returns 422.
13. Repository validation error maps to 400.
14. Unexpected repository error maps to 500.
15. Existing health, Vapi, and availability routes still work.

## Run
```
pytest -v backend/tests/test_appointment_request_schemas.py
pytest -v backend/tests/test_appointment_request_routes.py
```

Then run all tests:
```
pytest -v backend/tests
```

## Acceptance criteria
- All Module 17 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Appointment request routes are mounted.
- Do not build Vapi appointment capture yet.
- Commit all changes only if tests pass.

## Commit message
`Sprint 1 / Module 17 — Appointment request API routes`
