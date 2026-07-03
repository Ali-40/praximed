# Sprint 15 / Module 109 — Staging Smoke Execution Evidence

Status: pending Module 108 review.

## Context

Module 108 complete:
- `docs/deployment/STAGING_ENVIRONMENT_WIRING_RUNBOOK.md` created (13 sections)
- `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` created (BLOCKED/PENDING — no wiring evidence yet)
- 49 contract tests; full suite: 2237/2237 passed

Sprint 15 sequence so far:
- Module 105 — Railway backend service creation runbook (READY)
- Module 106 — Railway PostgreSQL provisioning/migration runbook + evidence (BLOCKED/PENDING)
- Module 107 — Vercel frontend project creation runbook + evidence (BLOCKED/PENDING)
- Module 108 — Staging environment wiring runbook + evidence (BLOCKED/PENDING)
- Module 109 — Staging smoke execution evidence ← NEXT

Module 109 documents the full staging smoke execution: Vercel frontend loads, fake login
succeeds, Vapi test call creates a row, staff Confirm works, no auto-confirmation, no
real data. PASS only if real external service evidence exists.

No actual deployment inside Claude. No real secrets. No runtime code changes.

## Scope

Docs/static tests only. No deployment. No real secrets. No runtime changes.

### 1. Read and audit current state

Read:
- docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md — Module 104 (current BLOCKED/PENDING)
- docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md — Module 108
- docs/deployment/STAGING_ENVIRONMENT_WIRING_RUNBOOK.md — Module 108
- docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md — Module 97
- docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md — Module 103
- docs/architecture/ARCHITECTURE_CHECKPOINT_14_STAGING_DEPLOYMENT_REVIEW.md
- docs/claude/CURRENT_STATE.md

### 2. Update `docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md`

If no user-provided real smoke evidence exists:
- Keep result BLOCKED/PENDING
- Update blockers list to reference Module 108 wiring evidence as the next required step
- Add Module 109 as the document where PASS evidence will be recorded when smoke is executed

If user has provided real smoke evidence:
- Update each smoke step result with real evidence
- Set overall result to PASS only if all required steps passed
- Capture sanitized evidence only — no secrets, no real patient data

### 3. Create `docs/runtime/STAGING_SMOKE_PASS_EVIDENCE.md`

A new dedicated PASS evidence document (separate from the results document):

Sections:
1. **Purpose** — accuracy policy; no fabricated evidence; PASS only with real proof
2. **Current result** — BLOCKED/PENDING if no evidence; PASS if user provides
3. **Smoke environment** — Railway URL; Vercel URL; branch; commit SHA; date
4. **Backend smoke** — /health; /health/ready; alembic current; db_smoke_test; env var names
5. **Frontend smoke** — /login loads; CORS preflight; fake login; dashboard loads
6. **Vapi smoke** — test call result; row created; status=new; action_required=True; staff Confirm
7. **n8n smoke** — staging endpoint result (PASS or DEFERRED)
8. **Safety validation** — no real patient data; no production secrets; no wildcard CORS; no auto-confirm
9. **Evidence table** — all smoke steps with pass/fail/pending status
10. **Blockers if pending** — ordered list
11. **Recommended next** — Architecture Checkpoint 15 or auth hardening

### 4. Static contract tests

Create `backend/tests/test_staging_smoke_pass_evidence_contract.py`:
- Results doc exists (STAGING_SMOKE_EXECUTION_RESULTS.md)
- Pass evidence doc exists (STAGING_SMOKE_PASS_EVIDENCE.md)
- Mentions BLOCKED/PENDING or PASS (not fabricated)
- Mentions no fabricated evidence
- Mentions Railway backend URL
- Mentions Vercel frontend URL
- Mentions /health
- Mentions /health/ready
- Mentions migrations
- Mentions /login
- Mentions CORS preflight
- Mentions fake login
- Mentions Vapi test call
- Mentions status=new
- Mentions action_required
- Mentions staff Confirm
- Mentions no auto-confirmation
- Mentions no real patient data
- Mentions no production secrets
- Mentions no wildcard CORS
- Mentions no ngrok
- Mentions n8n (PASS or DEFERRED)
- Mentions Architecture Checkpoint 15 or auth hardening next
- No obvious real secrets in either doc

### 5. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 108 (already done) and Module 109
- `docs/claude/NEXT_MODULE.md` — Sprint 15 / Architecture Checkpoint 15

## What not to do

- Do not deploy to Railway or Vercel
- Do not run `npm install` or `npm run build`
- Do not add real secrets
- Do not fabricate smoke PASS evidence
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint
- Do not change DB schema or migration files
- Do not expand appointment workflow

## Acceptance

- `docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md` updated (BLOCKED/PENDING or PASS)
- `docs/runtime/STAGING_SMOKE_PASS_EVIDENCE.md` created (BLOCKED/PENDING unless real evidence)
- Contract tests pass
- Full test suite passes (2237/2237 minimum)
- Commit: `Sprint 15 / Module 109 — Staging smoke execution evidence`
