# Sprint 15 / Module 106 — Railway PostgreSQL Provisioning and Migration Evidence

Status: pending Module 105 review.

## Context

Module 105 complete:
- `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` created (15 sections)
- Railway backend service creation guide: exact settings, env vars, start command, evidence checklist
- 32 contract tests; full suite: 2135/2135 passed

After the developer follows the Module 105 runbook and the Railway backend service is
running with `/health` returning 200, the next step is:
1. Add Railway PostgreSQL add-on
2. Wire `DATABASE_URL` to the backend service
3. Run migrations against the staging DB
4. Provision staging fake clinic and user

Module 106 covers these steps with exact Railway UI guidance, evidence templates, and
stop rules.

If the Railway backend service from Module 105 has not yet been created, Module 106
should document the blocker and not proceed to PostgreSQL provisioning steps.

## Scope

Docs/static tests only. No deployment. No real secrets. No runtime changes.

### 1. Read and audit current state

Read:
- docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md — Module 105
- docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md — Module 103 strategy
- docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md — env var spec
- docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md — DATABASE_URL details
- docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md — current blocker list
- backend/scripts/run_migrations.py — migration runner
- backend/scripts/db_smoke_test.py — table verification script

### 2. Create `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_RUNBOOK.md`

Sections:
1. **Purpose** — human-executable Railway PostgreSQL provisioning guide; no Claude deployment
2. **Preconditions** — Module 105 Railway backend service must exist; `/health` must return 200
3. **Step 1: Add Railway PostgreSQL add-on** — exact Railway dashboard steps; Plugin vs. service
4. **Step 2: Link DATABASE_URL to backend service** — Railway auto-injects; confirm injection in Variables panel
5. **Step 3: Wait for PostgreSQL to show "Running" status** — Railway DB cold-start timing
6. **Step 4: Run migrations** — `python backend/scripts/run_migrations.py` via Railway "Run Command"; expected output; stop if non-zero
7. **Step 5: Verify migrations** — `python backend/scripts/db_smoke_test.py` via Railway "Run Command"; expected 4-table check
8. **Step 6: Verify /health/ready** — should return 200 now that DB is connected; expected JSON
9. **Step 7: Provision staging fake clinic and user** — Option A SQL from Module 103 Section 8; uuid generation; bcrypt hash generation; INSERT statements with placeholders; idempotent ON CONFLICT
10. **Step 8: Verify fake data** — SELECT queries to confirm rows exist; expected column values
11. **DATABASE_URL safety rules** — never local Docker; never production; auto-injected only
12. **Evidence to capture** — PostgreSQL service name; DATABASE_URL injection confirmed; migration output (sanitized); db_smoke_test result; fake clinic UUID; fake user email; /health/ready 200
13. **Failure triage** — DB not ready; migration fails; bcrypt import fails; duplicate key on provisioning; /health/ready still 503 after migrations
14. **Stop rules** — wrong DATABASE_URL; real patient data; secrets in logs; migration non-zero; production DB touched
15. **What this runbook does not cover** — Vercel frontend (Module 107); CORS wiring (Module 107-108); Vapi config (Module 108); smoke execution (Module 109)
16. **Recommended next** — Module 107: Vercel Frontend Project Creation Runbook

### 3. Static contract tests

Create `backend/tests/test_railway_postgresql_provisioning_runbook_contract.py`:
- Runbook doc exists
- Mentions Railway PostgreSQL
- Mentions add-on or plugin
- Mentions DATABASE_URL auto-injected
- Mentions run_migrations.py
- Mentions `python backend/scripts/run_migrations.py`
- Mentions alembic upgrade head
- Mentions db_smoke_test.py
- Mentions /health/ready
- Mentions staging fake clinic
- Mentions doctor.staging@praximed.test
- Mentions bcrypt
- Mentions no local Docker DATABASE_URL
- Mentions no production DATABASE_URL
- Mentions evidence capture
- Mentions stop rules
- Mentions Module 107 Vercel
- No obvious real secrets

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 105 and Module 106
- `docs/claude/NEXT_MODULE.md` — Sprint 15 / Module 107: Vercel Frontend Project Creation Runbook

## What not to do

- Do not provision a Railway PostgreSQL add-on
- Do not run migrations against any database
- Do not add real secrets
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint
- Do not change DB schema or migration files
- Do not run npm install

## Acceptance

- `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_RUNBOOK.md` created
- Contract tests pass
- Full test suite passes (2135/2135 minimum)
- Commit: `Sprint 15 / Module 106 — Railway PostgreSQL provisioning and migration evidence`
