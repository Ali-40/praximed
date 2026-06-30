# Sprint 1 / Module 16 — Appointment Request Repository

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

All are committed. Do not modify completed modules unless absolutely required.

## Task scope
Create the database repository layer for appointment_requests.

Create only:
1. `backend/app/db/repositories/appointment_request_repo.py`
2. `backend/tests/test_appointment_request_repo.py`

Do not create API routes yet.
Do not modify Vapi modules yet.
Do not build WhatsApp.
Do not build frontend.
Do not use a real database in tests.

## Repository requirements

### Custom exceptions
- `AppointmentRequestRepoError`
- `InvalidAppointmentRequestError`

### Public async functions

#### 1. `create_appointment_request`
```
create_appointment_request(
    pool,
    clinic_id,
    source,
    patient_name,
    source_ref=None,
    patient_phone=None,
    patient_email=None,
    date_of_birth=None,
    reason=None,
    preferred_starts_at=None,
    preferred_ends_at=None,
    status="new",
    urgency_level="normal",
    action_required=True,
    assigned_user_id=None,
    raw_payload=None,
)
```

Behavior:
- Validate clinic_id, source, and patient_name are not empty.
- Validate preferred_ends_at > preferred_starts_at if both are provided.
- Validate source is one of: vapi, whatsapp, web, staff, system.
- Validate status is one of: new, confirmed, rejected, callback_needed, cancelled, archived.
- Validate urgency_level is one of: low, normal, urgent, emergency.
- Use parameterized SQL only.
- Insert into appointment_requests.
- Return created row.

#### 2. `get_appointment_request_by_id(pool, clinic_id, request_id)`
- Return matching row or None.
- Must filter by clinic_id.

#### 3. `list_appointment_requests(pool, clinic_id, status=None, action_required=None, limit=50)`
- Return recent appointment requests.
- Limit must be between 1 and 100.
- Optional filters for status and action_required.
- Must filter by clinic_id.

#### 4. `update_appointment_request_status(pool, clinic_id, request_id, status, action_required=None)`
- Validate status.
- Update status and optionally action_required.
- Return updated row.

#### 5. `assign_appointment_request(pool, clinic_id, request_id, assigned_user_id)`
- Assign request to a clinic user.
- Return updated row.

#### 6. `mark_callback_needed(pool, clinic_id, request_id)`
- Set status to callback_needed and action_required to true.
- Return updated row.

#### 7. `archive_appointment_request(pool, clinic_id, request_id)`
- Set status to archived and action_required to false.
- Return updated row.

## Tests required
1. create_appointment_request calls fetchrow.
2. create_appointment_request raises InvalidAppointmentRequestError for empty clinic_id.
3. create_appointment_request raises InvalidAppointmentRequestError for empty patient_name.
4. create_appointment_request validates invalid source.
5. create_appointment_request validates invalid status.
6. create_appointment_request validates invalid urgency_level.
7. create_appointment_request validates invalid preferred time range.
8. get_appointment_request_by_id calls fetchrow and filters by clinic_id.
9. list_appointment_requests calls fetch.
10. list_appointment_requests validates limit.
11. list_appointment_requests supports status filter.
12. list_appointment_requests supports action_required filter.
13. update_appointment_request_status calls fetchrow.
14. update_appointment_request_status validates status.
15. assign_appointment_request calls fetchrow.
16. mark_callback_needed calls fetchrow.
17. archive_appointment_request calls fetchrow.
18. SQL uses parameterized placeholders, not string formatting.

## Run
`pytest -v backend/tests/test_appointment_request_repo.py`

Then run all tests:
`pytest -v backend/tests`

## Acceptance criteria
- All Module 16 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Only appointment_request_repo.py and its tests are created.
- CURRENT_STATE.md and NEXT_MODULE.md are updated.
- Commit all changes only if tests pass.

## Commit message
`Sprint 1 / Module 16 — Appointment request repository`
