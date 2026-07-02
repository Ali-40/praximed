# Sprint 11 / Module 84 — Vapi Intake to Dashboard Browser Smoke

Status: pending Module 83 review.

## Context

Module 83 built the Vapi appointment intake smoke harness and fixed two bugs in the
capture service (`config_loader.get` → `config_loader.load`; `config.clinic_id` →
`config.tenant_id`). One gap remains before the smoke script can exercise the live
backend: `main.py` does not initialize `app.state.config_loader`. Without this,
`POST /vapi/tools/capture-appointment-request` returns HTTP 503.

The config_loader gap is the only blocker. Everything else is in place:
- Capture endpoint exists and accepts the correct payload shape
- Machine auth (`X-Vapi-*` headers, `vapi:tool` scope) is proven to work
- Smoke script (`backend/scripts/smoke_vapi_appointment_intake.py`) is ready
- Local tenant config file exists on disk for the seed clinic UUID

## Scope

### 1. Wire app.state.config_loader in main.py

In `backend/app/main.py`, inside the lifespan startup block (after `app.state.db_pool`
is set), add:

```python
from backend.app.core.config_loader import ClinicConfigLoader
app.state.config_loader = ClinicConfigLoader(pool=pool)
```

This gives the capture route a working config loader that can resolve the local seed
clinic UUID from the disk config file.

Add a corresponding teardown in the shutdown block:
```python
app.state.config_loader = None
```

### 2. Add a contract test for the config_loader wiring

Create or extend a contract test to assert:
- `main.py` imports `ClinicConfigLoader` or references it
- `app.state.config_loader` is set during lifespan startup
- `app.state.config_loader` is reset on shutdown

Place new tests in `backend/tests/test_app_lifespan_db_pool.py` (existing file) or
`backend/tests/test_app_config_loader_wiring.py` (new file).

### 3. Run the smoke script against the live backend

With the config_loader wired:

```bash
# 1. Start PostgreSQL
docker-compose -f docker-compose.postgres.yml up -d

# 2. Run migrations
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
cd backend && alembic upgrade head && cd ..

# 3. Seed data
python backend/scripts/seed_local_data.py

# 4. Start backend (with config_loader wired)
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

### 5. Create smoke evidence doc

`docs/runtime/VAPI_INTAKE_DASHBOARD_SMOKE_RESULTS.md`:
- Steps completed
- Evidence: smoke script output (HTTP 200, appointment request ID)
- Evidence: dashboard row appeared without seed script
- Evidence: Confirm action worked on the new row
- What this proves
- What remains

### 6. Update docs

- `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` — mark all unknowns RESOLVED
- `docs/claude/CURRENT_STATE.md` — record Module 84
- `docs/claude/NEXT_MODULE.md` — Sprint 11 / Module 85 — Reject Action

## What not to do

- Do not use real patient data or real Vapi credentials
- Do not auto-confirm appointment requests or create calendar events
- Do not change auth, JWT, machine auth, webhook signature, or seed data
- Do not require ngrok or a live Vapi connection

## Acceptance

- `main.py` wires `app.state.config_loader` in lifespan startup
- `POST /vapi/tools/capture-appointment-request` returns HTTP 200 with local fake payload
- New appointment request row appears in dashboard without the seed script
- Staff can Confirm the row in the browser
- Smoke evidence documented
- Full backend tests pass: `pytest -v backend/tests`
- Commit: `Sprint 11 / Module 84 — Vapi intake to dashboard browser smoke`
