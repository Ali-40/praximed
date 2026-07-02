# Sprint 11 / Module 85 — UUID Validation Fix and Smoke Completion

Status: ready — blocked only by UUID regex in config_loader.py

## Context

Module 84 wired `app.state.config_loader` in `main.py` lifespan, eliminating the HTTP 503
that blocked `POST /vapi/tools/capture-appointment-request`. Running
`smoke_vapi_appointment_intake.py` revealed a new HTTP 500 blocker:

```
{"detail": "Internal error capturing appointment request: tenant_id must be a valid UUID (v1–v5); got '11111111-1111-1111-1111-111111111111'"}
```

Root cause: `_assert_valid_uuid()` in `backend/app/core/config_loader.py` uses a regex
that requires the clock-seq high nibble to be `[89ab]` (RFC 4122 variant-1). The seed
clinic UUID `11111111-1111-1111-1111-111111111111` has `1` in that position.

The UUID check's security purpose is to prevent path traversal — blocking input that
contains `..`, `/`, or non-hex characters from being used as a filesystem path segment.
The variant byte constraint (`[89ab]`) is incidental to that goal and is not needed for
path safety. Relaxing it does not weaken the protection.

Everything else is in place:
- `app.state.config_loader` is wired (Module 84) — 503 fixed
- Smoke script, payload, and machine auth are ready (Module 83)
- Capture service bugs are fixed (Module 83)
- Dashboard Confirm action works (Module 81)
- Seed clinic UUID exists in DB with FK-valid row

## Scope

### 1. Fix UUID validation in config_loader.py

In `backend/app/core/config_loader.py`, relax `_UUID_RE` to accept any hex digit in the
variant byte position instead of requiring `[89ab]`:

```python
# Before (too strict — rejects structurally valid local-dev UUIDs):
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

# After (relaxed variant byte — still blocks path traversal):
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
```

Also update the error message in `_assert_valid_uuid()` from `"must be a valid UUID (v1–v5)"` to
`"must be a valid UUID (v1–v5, any variant)"` so the error text accurately reflects what
is accepted.

### 2. Update config_loader tests

In `backend/tests/test_config_loader.py` (or wherever `_assert_valid_uuid` is tested):
- Confirm the seed UUID `11111111-1111-1111-1111-111111111111` now passes
- Confirm that standard RFC 4122 UUIDs with `[89ab]` variant still pass
- Confirm that path-traversal and malformed inputs still fail (these must not regress)

### 3. Run the smoke script against the live backend

With the UUID fix applied:

```bash
# 1. Start PostgreSQL
docker-compose -f docker-compose.postgres.yml up -d

# 2. Run migrations
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
cd backend && alembic upgrade head && cd ..

# 3. Seed data
python backend/scripts/seed_local_data.py

# 4. Start backend
export JWT_SECRET_KEY=local-dev-jwt-secret-key-change-in-production
uvicorn backend.app.main:app --reload --port 8000

# 5. Run intake smoke
python backend/scripts/smoke_vapi_appointment_intake.py
```

Expected output: HTTP 200, appointment request ID, status: new.

### 4. Close the dashboard loop in the browser

After the smoke succeeds:
- Open `http://localhost:3000/dashboard`
- Confirm the new Vapi-intake appointment row appears (distinct from the seed row)
- Click Confirm — status updates to "confirmed"

### 5. Update smoke evidence doc

Update `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_SMOKE_RESULTS.md`:
- Mark verdict as PASS
- Add smoke script output (HTTP 200, appointment request ID)
- Add dashboard row evidence (appeared without seed script)
- Add Confirm action evidence

### 6. Update docs

- `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` — mark UUID blocker RESOLVED
- `docs/claude/CURRENT_STATE.md` — record Module 85
- `docs/claude/NEXT_MODULE.md` — Sprint 11 / Module 86 — Reject Action

## What not to do

- Do not use real patient data or real Vapi credentials
- Do not auto-confirm appointment requests or create calendar events
- Do not change auth, JWT, machine auth, webhook signature, or seed data
- Do not require ngrok or a live Vapi connection
- Do not change the seed clinic UUID (it must stay `11111111-1111-1111-1111-111111111111` to match existing FK rows)

## Acceptance

- `_UUID_RE` in `config_loader.py` accepts `11111111-1111-1111-1111-111111111111`
- Path traversal and malformed UUID tests still pass (no regression)
- `POST /vapi/tools/capture-appointment-request` returns HTTP 200 with local fake payload
- New appointment request row appears in dashboard without the seed script
- Staff can Confirm the row in the browser
- Smoke evidence updated in `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_SMOKE_RESULTS.md`
- Full backend tests pass: `pytest -v backend/tests`
- Commit: `Sprint 11 / Module 85 — UUID validation fix and smoke completion`
