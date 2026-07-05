# Sprint 16 / Module 118B — Vapi Staging Direct Endpoint and Dashboard Retest

Status: pending push, Railway redeploy, Vapi header correction, direct endpoint smoke, DB verification, dashboard verification.

## Context

Module 118A complete:
- Staging tenant config created: `backend/tenants/configs/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/clinic_config.json`
- Diagnostic confirmed three blockers:
  1. `X-Vapi-Service-Name: vapi` header was missing → HTTP 401
  2. `X-Clinic-Ref` is not a recognized alias → use `X-Vapi-Clinic-Id`
  3. No tenant config for staging UUID → ConfigNotFoundError → HTTP 404 (fixed)
- Vapi UI showed "completed successfully" but `staging_count=0`; no DB row was inserted
- Full test suite: [see last passing run]
- Commit: Sprint 16 / Module 118A

Railway backend URL (confirmed): `https://web-production-fd91d.up.railway.app`
Staging clinic_id (confirmed): `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`

## Scope

Evidence doc + static tests. No deployment by Claude.
No real secrets. No production data. No real patient PII.

### The developer must:

1. Push the Module 118A commit → Railway auto-redeploys with tenant config fix

2. Update Vapi assistant tool configuration — correct headers (replace what was there):
   - Server URL: `https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request`
   - `Content-Type: application/json`
   - `X-Vapi-Service-Name: vapi`
   - `X-Vapi-Clinic-Id: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056`
   - `X-Vapi-Scopes: vapi:tool` — **singular** (`vapi:tools` plural returns HTTP 403)
   - Remove `X-Clinic-Ref` entirely
   - Vapi webhook secret must match the `VAPI_WEBHOOK_SECRET` env var on Railway backend

3. Run a direct endpoint smoke (bypass Vapi entirely) to confirm HTTP 200:

   ```bash
   curl -s -w "\n%{http_code}" \
     -X POST \
     "https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request" \
     -H "Content-Type: application/json" \
     -H "X-Vapi-Service-Name: vapi" \
     -H "X-Vapi-Clinic-Id: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056" \
     -H "X-Vapi-Scopes: vapi:tool" \
     -d '{
       "clinic_ref": "1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
       "call_id": "test-direct-smoke-001",
       "patient_name": "Test Patient",
       "reason": "Checkup",
       "preferred_time": "morning"
     }'
   ```

   Expected: HTTP 200. If 401 → headers still wrong. If 404 → tenant config not deployed yet.

4. Verify DB row exists (Railway "Run Command" console):

   ```python
   python - <<'EOF'
   import asyncio, asyncpg, os

   async def check():
       conn = await asyncpg.connect(os.environ["DATABASE_URL"])
       rows = await conn.fetch(
           "SELECT id, patient_name, status, action_required, source, created_at "
           "FROM appointment_requests "
           "WHERE clinic_id = '1a5bbc75-c1b0-4488-94aa-64b3f1c50056' "
           "ORDER BY created_at DESC LIMIT 5"
       )
       for r in rows:
           print(dict(r))
       print("staging_count=" + str(len(rows)))
       await conn.close()

   asyncio.run(check())
   EOF
   ```

   Expected: `staging_count=1` (or more); row with `status='new'`, `action_required=True`, `source='vapi'`

5. Trigger a Vapi test call using synthetic caller data:
   - No real phone numbers
   - No real patient names, DOBs, or medical data
   - Use clearly fake test data (e.g. "Test Patient", "Checkup", fake phone)

6. Log into the Vercel dashboard (`https://praximed.vercel.app`) with fake staging credentials

7. Confirm a new appointment row appears in the Appointments section with:
   - `status=new`
   - `action_required=True`
   - No auto-confirmation

8. If the dashboard UI supports it, click the staff Confirm button:
   - Confirm the row updates to `status=confirmed`
   - Confirm this required explicit staff action (no auto-confirm)

9. Confirm `GET /health/ready` → 200 (DB still healthy after write)

### Evidence to capture (no secrets):

- Direct endpoint smoke HTTP status: expected 200
- DB check output: `staging_count=1`; row `status='new'`; `action_required=True`
- Vapi test call HTTP status: expected 200
- Dashboard appointment row count before Vapi call: 0
- Dashboard appointment row count after Vapi call: 1
- Row `status`: `new`
- Row `action_required`: `True`
- Staff Confirm result: `status=confirmed` (if tested)
- Confirmation: no auto-confirmation observed
- Confirmation: no real patient PII in the Vapi test call data
- `GET /health/ready` → 200 after write
- `VAPI_WEBHOOK_SECRET` variable name only — not the value

### Module 118B will create/update:

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
- PASS only with real direct endpoint smoke HTTP 200 + DB row confirmed + dashboard row confirmed
- Contract tests pass
- Full test suite passes (minimum: last passing count)
- Commit: `Sprint 16 / Module 118B — Vapi staging direct endpoint and dashboard retest`
