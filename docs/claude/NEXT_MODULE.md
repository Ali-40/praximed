# Sprint 14 / Module 104 — Staging Smoke Execution Evidence

Status: pending Module 103 review.

## Context

Module 103 resolved the staging DB migration and seed strategy:
- `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md` created (17 sections)
- Migration sequence defined: `python backend/scripts/run_migrations.py` via Railway "Run Command"
- Staging fake tenant/user strategy defined (distinct UUIDs; `doctor.staging@praximed.test`)
- `seed_local_data.py` assessed as local-only; must not run against staging DB
- Option A (manual SQL via Railway shell) recommended for first smoke provisioning
- Contract tests: 27/27 passed; full suite: 2077/2077 passed

The remaining staging deployment blockers (all require actual Railway/Vercel services to be
created manually by the developer outside this Claude Code session):
- Railway backend service not yet deployed
- Railway PostgreSQL add-on not yet provisioned
- `DATABASE_URL` not yet available
- Staging fake clinic and user UUIDs not yet generated and inserted
- `VAPI_WEBHOOK_SECRET` and other secrets not yet set in Railway dashboard
- Vercel frontend not yet deployed
- `NEXT_PUBLIC_API_BASE_URL` not yet set in Vercel
- `FRONTEND_CORS_ORIGINS` on Railway not yet set

Module 104 documents staging smoke execution evidence **only if** the Railway and Vercel
services have been created and configured manually. If they have not been created, Module
104 documents the exact blockers preventing smoke execution — it does not claim a pass.

No fake smoke evidence. No deployment in this module. No real patient data.

## Scope

### 1. Check if staging services exist

Before writing any smoke evidence:
- Ask the user whether the Railway backend service and Vercel frontend have been created
- If not created: document the open blockers and defer smoke to a future module
- If created: collect and document actual smoke evidence

### 2. If staging services exist — collect and document evidence

Read from user or environment (not from guesses):
- Actual Railway staging API HTTPS URL
- Actual Vercel staging frontend HTTPS URL
- Migration execution result (sanitized)
- DB smoke test result
- Login smoke result
- Dashboard load result
- Vapi test call result
- Staff Confirm result

### 3. Create `docs/deployment/STAGING_SMOKE_EVIDENCE.md`

Sections:
1. **Purpose** — actual staging smoke evidence; fake/non-PHI only; production PHI no-go
2. **Staging topology used** — Railway URL; Vercel URL; staging clinic UUID; no real data
3. **Pre-smoke checklist** — all items from Module 97 checklist verified
4. **Migration evidence** — command run; timestamp; revision reached; sanitized output
5. **DB smoke test evidence** — `db_smoke_test.py` result; tables verified
6. **Staging provisioning evidence** — fake clinic and user confirmed in DB
7. **Backend health smoke** — `GET /health` → `{"status": "ok"}`; `GET /health/ready`
8. **CORS smoke** — `OPTIONS /auth/login` preflight from Vercel origin → correct headers
9. **Auth smoke** — login with `doctor.staging@praximed.test` → JWT returned
10. **Frontend smoke** — Vercel URL loads; `/login` renders; `/dashboard` loads after login
11. **Vapi appointment intake smoke** — test call → `status=new`; `action_required=true`
12. **Staff Confirm smoke** — `PATCH /appointment-requests/{id}/status` → `confirmed`
13. **n8n calendar sync smoke** (optional) — `POST /webhooks/n8n/calendar-sync` → 200
14. **Failures and deviations** — any smoke step that did not pass; triage and resolution
15. **Stop rules triggered** — any stop rule from Module 103/97 that fired
16. **Go/No-Go decision** — staging smoke: GO or NO-GO for next milestone
17. **Open blockers after smoke** — what remains before auth hardening (M3)
18. **Non-goals** — no production PHI; no real patients; no auth hardening in this module

### 4. Static contract tests

Create `backend/tests/test_staging_smoke_evidence_contract.py`:
- Smoke evidence doc exists
- Mentions Railway staging API URL
- Mentions Vercel staging frontend URL
- Mentions fake/non-PHI staging
- Mentions no production PHI
- Mentions migration evidence
- Mentions /health route result
- Mentions CORS smoke
- Mentions login smoke / auth smoke
- Mentions Vapi appointment intake
- Mentions status=new / action_required
- Mentions staff Confirm
- Mentions no auto-confirmation
- Mentions go/no-go decision
- Mentions Module 105 or next step
- No obvious real secrets

### 5. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 103 commit and Module 104
- `docs/claude/NEXT_MODULE.md` — Sprint 14 / Module 105 or Architecture Checkpoint 14

## If staging services do not yet exist

If the Railway and Vercel services have not been created:
- Document the open blockers clearly
- Do not fabricate smoke evidence
- Recommend the developer create the services manually, then re-run Module 104
- Update NEXT_MODULE.md to reflect that Module 104 is a deployment execution step requiring
  manual developer action, not a documentation-only module

## What not to do

- Do not fabricate smoke evidence
- Do not claim a smoke pass without actual service responses
- Do not deploy Railway or Vercel services from within Claude Code
- Do not use real patient data, real clinic data, or PHI
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint
- Do not change DB schema or migration files
- Do not add real secrets to any file

## Acceptance

- `docs/deployment/STAGING_SMOKE_EVIDENCE.md` created (or blocker doc if services don't exist)
- Contract tests pass
- Full test suite passes (2077/2077 minimum)
- Commit: `Sprint 14 / Module 104 — Staging smoke execution evidence`
