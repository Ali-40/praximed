# Sprint 14 / Module 103 — Staging DB Migration and Seed Strategy

Status: pending Module 102 review.

## Context

Module 102 resolved the Vercel frontend deployment blockers:
- `docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md` created (13 sections)
- Vercel project settings documented (root=`frontend`; Next.js auto-detect; no vercel.json)
- `NEXT_PUBLIC_API_BASE_URL` documented as the only required Vercel env var
- CORS bootstrap sequence documented (Railway URL → Vercel URL → FRONTEND_CORS_ORIGINS)
- Auth/session staging caveat documented (sessionStorage JWT fake-data-only; httpOnly cookie deferred)
- Contract tests: 26/26 passed; full suite: 2050/2050 passed

The remaining staging deployment blockers:
- Staging DB migration execution sequence not defined
- Staging fake clinic + user provisioning strategy not defined
- `seed_local_data.py` is local-dev only (hardcoded local UUIDs and local-dev password hash); cannot be reused
- Staging seed strategy unclear: staging-safe seed script vs. manual SQL inserts

Module 103 defines the staging DB migration and seed strategy. No actual migration execution.
No real secrets. No runtime code changes. No deployment.

## Scope

### 1. Read and audit current state

Read:
- `backend/scripts/run_migrations.py` — migration runner script
- `backend/alembic/versions/` — migration files (list and review)
- `backend/scripts/seed_local_data.py` — understand why it is local-only
- `backend/app/db/models/` — clinic, clinic_user, appointment_request tables
- `docs/deployment/STAGING_DEPLOYMENT_CONFIG_FILE_INVENTORY.md` — staging seed gap section
- `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` — migration strategy section

### 2. Create `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md`

Sections:
1. **Purpose** — define staging DB migration and seed strategy; no execution; fake/non-PHI only
2. **Migration execution sequence** — exact commands and order for Railway staging DB
3. **Migration files** — list all Alembic migrations; expected final schema state
4. **run_migrations.py behavior** — what it does, gaps (no retry loop), when to run it on Railway
5. **Why seed_local_data.py cannot be used in staging** — hardcoded UUIDs; local-dev password hashes
6. **Staging fake data requirements** — what must exist before smoke begins (clinic row; clinic_user row; fake appointment rows)
7. **Staging seed strategy** — manual SQL inserts vs. staging seed script; recommendation
8. **Staging fake tenant spec** — exact field values for the staging clinic and user (fake; no real PII)
9. **Password hashing for staging** — how to generate a staging-safe bcrypt hash without running local code
10. **Smoke test data dependency** — which smoke steps require which DB rows
11. **Rollback** — how to reset the staging DB if needed
12. **Blockers remaining** — what cannot proceed until this module is reviewed
13. **Non-goals** — no migration execution; no production data; no PHI; no real credentials

### 3. Static contract tests

Create `backend/tests/test_staging_db_migration_and_seed_strategy_contract.py`:
- Staging DB migration and seed strategy doc exists
- Doc mentions migration execution sequence
- Doc mentions run_migrations.py
- Doc mentions alembic upgrade head
- Doc mentions why seed_local_data.py cannot be used in staging
- Doc mentions staging fake clinic tenant
- Doc mentions staging fake clinic_user
- Doc mentions bcrypt password hash
- Doc mentions smoke test data dependency
- Doc mentions rollback
- Doc mentions fake/non-PHI staging only
- Doc mentions no deployment executed
- Doc mentions no real credentials
- Doc mentions Module 104
- No obvious real secrets in doc

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 103
- `docs/claude/NEXT_MODULE.md` — Sprint 14 / Module 104: Staging Smoke Execution

## What not to do

- Do not execute migrations against any database
- Do not create or modify any migration files
- Do not create a real staging seed script (document the strategy only)
- Do not use real clinic names, patient names, or real credentials
- Do not run npm install or touch frontend
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint
- Do not change DB schema

## Acceptance

- `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md` created
- Contract tests pass
- Full test suite passes (2050/2050 minimum)
- Commit: `Sprint 14 / Module 103 — Staging DB migration and seed strategy`
