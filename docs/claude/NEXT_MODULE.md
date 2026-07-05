# Sprint 16 / Module 119 — n8n Staging Workflow Wiring Evidence

Status: pending manual n8n staging workflow configuration and fake-data smoke.

## Context

Module 118B complete:
- Vapi staging dashboard loop confirmed PASS with real deployed staging evidence
- Appointments count reached 2 then 3 in Vercel dashboard
- Two Test Patient rows confirmed with status: new; priority: normal; Confirm button visible
- Staff Confirm updated two rows to status: confirmed; one row remained status: new; no auto-confirm
- Full test suite: [see last passing run]
- Commit: Sprint 16 / Module 118B

Railway backend URL (confirmed): `https://web-production-fd91d.up.railway.app`
Staging clinic_id (confirmed): `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`
Vercel frontend URL (confirmed): `https://praximed.vercel.app`

## Scope

Evidence doc + static tests. No deployment by Claude.
No real secrets. No production data. No real patient PII.
n8n staging is optional for the initial core smoke — it is DEFERRED if not yet configured.

## Decision point

Before starting Module 119, the developer must decide:

**Option A — Configure n8n staging now:**
- Proceed with n8n staging workflow wiring
- Connect n8n only to Railway staging backend
- Use staging webhook secret (`N8N_WEBHOOK_SECRET` name only — value not recorded)
- Fake data only — no real calendar writes, no production data

**Option B — Defer n8n staging:**
- Mark n8n as DEFERRED in evidence docs
- Proceed to Architecture Checkpoint 16 (Sprint 16 staging smoke review)
- n8n staging can be revisited in a later sprint

If Option B is chosen, update `NEXT_MODULE.md` to:

```
Sprint 17 / Architecture Checkpoint 16 — Sprint 16 Staging Smoke Review
```

## If Option A (n8n staging):

### The developer must:

1. Configure the n8n staging workflow to receive a signed POST from Railway backend:
   - Staging n8n webhook URL (no production URL)
   - `N8N_WEBHOOK_SECRET` must match the env var on Railway backend
   - Method: POST; signature header: `X-Signature` (HMAC-SHA256)

2. Trigger a fake staging event (no real calendar writes, no real patient data)

3. Confirm the n8n workflow receives and processes the fake event:
   - n8n workflow execution status: success
   - No production calendar write
   - No real patient data in the n8n payload

4. Confirm `GET /health/ready` → 200 (DB still healthy after n8n event)

### Evidence to capture (no secrets):

- n8n staging webhook URL (no secret values)
- n8n workflow execution status: success
- Confirmation: no production calendar write
- Confirmation: no real patient data in n8n payload
- `N8N_WEBHOOK_SECRET` variable name only — not the value
- `GET /health/ready` → 200 after n8n event

### Module 119 will create/update:

1. `docs/runtime/N8N_STAGING_WORKFLOW_WIRING_EVIDENCE.md` (new) — PASS or DEFERRED
2. Contract tests for n8n staging evidence
3. Update `STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — mark n8n PASS or DEFERRED
4. Update `STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — mark n8n check PASS or NOT ENABLED
5. Update `CURRENT_STATE.md` and `NEXT_MODULE.md` → Architecture Checkpoint 16

## What not to do

- Do not deploy Railway or n8n from Claude
- Do not record the `N8N_WEBHOOK_SECRET` value
- Do not record JWT tokens or passwords
- Do not use real patient data in any n8n test payload
- Do not fabricate PASS evidence
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint

## Acceptance

- `docs/runtime/N8N_STAGING_WORKFLOW_WIRING_EVIDENCE.md` created (PASS or DEFERRED with real evidence)
- PASS only with real n8n workflow execution evidence
- Contract tests pass
- Full test suite passes
- Commit: `Sprint 16 / Module 119 — n8n staging workflow wiring evidence`
