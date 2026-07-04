# Sprint 16 / Module 118 — Vapi Staging Dashboard Loop Evidence

Status: pending manual Vapi staging assistant/tool-call wiring and fake appointment test.

## Context

Module 117 complete:
- Vercel frontend URL: `https://praximed.vercel.app`
- `FRONTEND_CORS_ORIGINS=https://praximed.vercel.app` set in Railway (no wildcard)
- Browser login PASS with `doctor.staging@praximed.test`
- Dashboard loaded: all four sections visible (0 rows — expected before Vapi call)
- Full test suite: 2424/2424 passed
- Commit: (see git log)

Railway backend URL (confirmed): `https://web-production-fd91d.up.railway.app`
Staging clinic_id (confirmed): `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`

## Scope

Evidence doc + static tests. No deployment by Claude.
No real secrets. No production data. No real patient PII.

### The developer must:

1. Configure the Vapi test assistant to call the Railway backend:
   - Server URL: `https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request`
   - Header `X-Vapi-Scopes: vapi:tool` — **singular** (`vapi:tools` plural returns HTTP 403)
   - Header `X-Clinic-Ref: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056`
   - Vapi webhook secret must match the `VAPI_WEBHOOK_SECRET` env var on Railway backend

2. Trigger a fake Vapi test call using synthetic caller data:
   - No real phone numbers
   - No real patient names, DOBs, or medical data
   - Use clearly fake test data (e.g. "Test Patient", "Checkup", fake phone)

3. Confirm the tool call returns HTTP 200

4. Log into the Vercel dashboard (`https://praximed.vercel.app`) with fake staging credentials

5. Confirm a new appointment row appears in the Appointments section with:
   - `status=new`
   - `action_required=True`
   - No auto-confirmation

6. If the dashboard UI supports it, click the staff Confirm button:
   - Confirm the row updates to `status=confirmed`
   - Confirm this required explicit staff action (no auto-confirm)

7. Confirm `GET /health/ready` → 200 (DB still healthy after write)

### Evidence to capture (no secrets):

- Vapi tool server URL (no secret values)
- Vapi tool call HTTP status: expected 200
- Dashboard appointment row count before Vapi call: 0
- Dashboard appointment row count after Vapi call: 1
- Row `status`: `new`
- Row `action_required`: `True`
- Staff Confirm result: `status=confirmed` (if tested)
- Confirmation: no auto-confirmation observed
- Confirmation: no real patient PII in the Vapi test call data
- `GET /health/ready` → 200 after write
- `VAPI_WEBHOOK_SECRET` variable name only — not the value

### Module 118 will create/update:

1. `docs/runtime/VAPI_STAGING_DASHBOARD_LOOP_EVIDENCE.md` (new) — PASS or BLOCKED/PENDING
2. Contract tests for Vapi staging loop evidence
3. Update `STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — mark Vapi test call PASS if confirmed
4. Update `STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — mark Vapi/staff Confirm checks PASS if confirmed; if all checks PASS, overall staging smoke transitions to PASS
5. Update `CURRENT_STATE.md` and `NEXT_MODULE.md` → Architecture Checkpoint 16 (if full smoke PASS) or Module 119 (n8n staging, if required)

## What not to do

- Do not deploy Railway from Claude
- Do not record the `VAPI_WEBHOOK_SECRET` value
- Do not record JWT tokens or passwords
- Do not use real patient phone numbers or PII in the Vapi test call
- Do not fabricate PASS evidence
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint

## Acceptance

- `docs/runtime/VAPI_STAGING_DASHBOARD_LOOP_EVIDENCE.md` created (PASS or BLOCKED/PENDING with real evidence)
- PASS only with real Vapi tool call HTTP 200 + dashboard row confirmed
- Contract tests pass
- Full test suite passes (2424/2424 minimum)
- Commit: `Sprint 16 / Module 118 — Vapi staging dashboard loop evidence`
