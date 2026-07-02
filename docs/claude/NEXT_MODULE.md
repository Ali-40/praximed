# Sprint 11 / Module 86 — Vapi Intake to Dashboard Browser Smoke Evidence

Status: pending Module 85 review.

## Context

Module 85 completed the backend half of the Vapi intake loop:

- `POST /vapi/tools/capture-appointment-request` returns HTTP 200
- Appointment request created: ID `509211a7-784e-4e45-90f1-d9af6f8d7981`, `status: new`, `source: vapi`
- `action_required: true` — staff review required; not auto-confirmed

The remaining step is the browser confirm loop: a staff member opens the dashboard,
sees the Vapi-created row (without running the seed script), and clicks Confirm.

Everything is in place:
- Backend serving on `http://127.0.0.1:8000` (verified)
- Frontend `npm run dev` on `http://localhost:3000`
- Vapi-created row now in the DB alongside the seed row
- Confirm button works (Module 81 — proven in Module 82 browser smoke)

## Scope

### 1. Re-seed to get a clean starting state (optional)

If needed, run seed to reset the `55555555-…` seed row:
```bash
python backend/scripts/seed_local_data.py
```

### 2. Re-run the intake smoke to create a fresh Vapi row

```bash
python backend/scripts/smoke_vapi_appointment_intake.py
```

Expected: HTTP 200, new appointment ID different from `55555555-…`.

### 3. Open the dashboard and close the loop in the browser

```bash
open http://localhost:3000/dashboard
```

Steps:
1. Log in with local-dev credentials (doctor.local@praximed.test / local-dev-password)
2. Go to Appointments section
3. Confirm a new row with `source: vapi` appears (patient: "Local Vapi Test Caller")
4. Click Confirm on that row
5. Verify status badge changes from "new" to "confirmed"
6. Verify Confirm button disappears
7. Verify the seed row (`55555555-…`) is unaffected

### 4. Create smoke evidence doc

`docs/runtime/VAPI_INTAKE_DASHBOARD_SMOKE_RESULTS.md`:
- Environment table
- Steps completed
- Evidence: smoke script output (HTTP 200, appointment request ID)
- Evidence: dashboard row appeared without seed script
- Evidence: Confirm action worked on the new Vapi row
- What this proves
- What remains

### 5. Update docs

- `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_SMOKE_RESULTS.md` — add browser-loop evidence
- `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` — mark all unknowns RESOLVED
- `docs/claude/CURRENT_STATE.md` — record Module 86
- `docs/claude/NEXT_MODULE.md` — Sprint 11 / Module 87 — Reject Action

## What not to do

- Do not use real patient data or real Vapi credentials
- Do not auto-confirm appointment requests or create calendar events
- Do not change auth, JWT, machine auth, webhook signature, or seed data
- Do not require ngrok or a live Vapi connection
- Do not modify backend routes

## Acceptance

- New Vapi-created row appears in dashboard without seed script
- Staff can click Confirm on the Vapi row
- Status updates from "new" to "confirmed"; Confirm button disappears
- Seed row (`55555555-…`) is unaffected
- Evidence documented in `docs/runtime/VAPI_INTAKE_DASHBOARD_SMOKE_RESULTS.md`
- Full backend tests pass: `pytest -v backend/tests`
- Commit: `Sprint 11 / Module 86 — Vapi intake to dashboard browser smoke evidence`
