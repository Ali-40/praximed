# Sprint 1 / Module 18 — Vapi Appointment Capture Integration

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
14. Module 17: appointment request API schemas and routes

All are committed. Do not modify completed modules unless absolutely required.

## Task scope
Create the Vapi appointment capture integration so the Vapi phone agent can create structured appointment requests after collecting patient information.

**Important business rule:**
This module must NOT confirm or book appointments automatically.
It only creates an appointment request for staff review.

Create or update only:
1. `backend/app/modules/vapi/vapi_appointment_capture.py`
2. `backend/app/schemas/vapi.py`
3. `backend/app/api/routes/vapi_tools.py`
4. `backend/tests/test_vapi_appointment_capture.py`
5. `backend/tests/test_vapi_tool_routes.py`
6. `docs/claude/CURRENT_STATE.md`
7. `docs/claude/NEXT_MODULE.md`

Do not build WhatsApp.
Do not build frontend.
Do not create authentication.
Do not create real Vapi API calls.
Do not modify `appointment_request_repo.py` unless absolutely required by tests.
Do not use a real database in tests.

## Module service requirements

### File: `backend/app/modules/vapi/vapi_appointment_capture.py`

### Custom exceptions
- `VapiAppointmentCaptureError`
- `InvalidVapiAppointmentCaptureError`

### Public async function

```
capture_vapi_appointment_request(
    pool,
    config_loader,
    clinic_ref,
    call_id,
    patient_name,
    caller_phone=None,
    patient_email=None,
    date_of_birth=None,
    reason=None,
    preferred_starts_at=None,
    preferred_ends_at=None,
    urgency_level="normal",
    raw_payload=None,
) -> dict
```

**Behavior:**
- Validate `clinic_ref`, `call_id`, and `patient_name` are not empty.
- Load clinic config using `await config_loader.get(clinic_ref)`.
- Use `config.clinic_id` as the `clinic_id`.
- Validate `preferred_ends_at > preferred_starts_at` when both are provided.
- Call `appointment_request_repo.create_appointment_request` with:
  - `clinic_id = config.clinic_id`
  - `source = "vapi"`
  - `source_ref = call_id`
  - `patient_name = patient_name`
  - `patient_phone = caller_phone`
  - `patient_email = patient_email`
  - `date_of_birth = date_of_birth`
  - `reason = reason`
  - `preferred_starts_at = preferred_starts_at`
  - `preferred_ends_at = preferred_ends_at`
  - `status = "new"`
  - `urgency_level = urgency_level`
  - `action_required = True`
  - `raw_payload = raw_payload`
- Return dict:
  - `ok: true`
  - `clinic_id`
  - `request`
  - `message`

**Message** must clearly say the request was captured and clinic staff must confirm it.

Do not call availability engine here.
Availability should be checked by existing Vapi availability tools before capture.
This capture module only records the request.

## Schema requirements

### Update `backend/app/schemas/vapi.py` with:

#### 1. `VapiAppointmentCaptureRequest`
Fields:
- `clinic_ref: str`
- `call_id: str`
- `patient_name: str`
- `caller_phone: str | None = None`
- `patient_email: str | None = None`
- `date_of_birth: date | None = None`
- `reason: str | None = None`
- `preferred_starts_at: datetime | None = None`
- `preferred_ends_at: datetime | None = None`
- `urgency_level: str = "normal"`
- `raw_payload: dict | None = None`

Validation:
- `clinic_ref` must not be empty
- `call_id` must not be empty
- `patient_name` must not be empty
- `urgency_level` must be one of: `low`, `normal`, `urgent`, `emergency`
- If both `preferred_starts_at` and `preferred_ends_at` are provided, `preferred_ends_at` must be after `preferred_starts_at`

#### 2. `VapiAppointmentCaptureResponse`
Fields:
- `ok: bool`
- `message: str`
- `request: dict | None = None`

## Route requirements

### Update `backend/app/api/routes/vapi_tools.py` with:

#### `POST /vapi/tools/capture-appointment-request`

Behavior:
- Accept `VapiAppointmentCaptureRequest`.
- Use existing `get_db_pool` dependency.
- Use existing `get_config_loader` dependency.
- Call `capture_vapi_appointment_request`.
- Return `VapiAppointmentCaptureResponse`.

Response message:
- Must tell Vapi that the appointment request was captured.
- Must say staff confirmation is required.
- Must NOT say the appointment is confirmed.

Error handling:
- Missing `db_pool` → HTTP 503 via existing dependency
- Missing `config_loader` → HTTP 503 via existing dependency
- Invalid capture input → HTTP 400
- Repository validation error → HTTP 400
- Config loader error → HTTP 404 or HTTP 400 depending on existing exception types
- Unexpected error → HTTP 500

## Tests for `test_vapi_appointment_capture.py`
1. `capture_vapi_appointment_request` loads clinic config.
2. `capture_vapi_appointment_request` calls `create_appointment_request`.
3. It passes `source="vapi"`.
4. It passes `source_ref=call_id`.
5. It sets `status="new"`.
6. It sets `action_required=True`.
7. It returns a message that says staff confirmation is required.
8. Empty `clinic_ref` raises `InvalidVapiAppointmentCaptureError`.
9. Empty `call_id` raises `InvalidVapiAppointmentCaptureError`.
10. Empty `patient_name` raises `InvalidVapiAppointmentCaptureError`.
11. Invalid preferred time range raises `InvalidVapiAppointmentCaptureError`.
12. Repository error is handled or propagated cleanly according to implementation.

## Tests for `test_vapi_tool_routes.py`
Add tests without breaking existing Vapi tool tests.

New route tests:
1. `POST /vapi/tools/capture-appointment-request` returns 200 for valid payload.
2. Route calls `capture_vapi_appointment_request`.
3. Route passes app DB pool to capture service.
4. Route passes app `config_loader` to capture service.
5. Response message does not claim appointment is confirmed.
6. Missing `db_pool` returns HTTP 503.
7. Missing `config_loader` returns HTTP 503.
8. Invalid request body returns HTTP 422.
9. Invalid capture input maps to HTTP 400.
10. Unexpected capture error maps to HTTP 500.

## Run
```
pytest -v backend/tests/test_vapi_appointment_capture.py
pytest -v backend/tests/test_vapi_tool_routes.py
```

Then run all tests:
```
pytest -v backend/tests
```

## Acceptance criteria
- All Module 18 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Vapi can create an appointment request.
- Vapi does NOT confirm or book the appointment automatically.
- Existing Vapi availability tool routes still work.
- Commit all changes only if tests pass.

## Commit message
`Sprint 1 / Module 18 — Vapi appointment capture integration`
