# Sprint 16 / Module 113 — Railway PostgreSQL Provisioning and Migration Execution Evidence

Status: pending manual Railway PostgreSQL creation and migration execution.

## Context

Module 112 complete:
- Railway backend service: **PASS** — `https://web-production-fd91d.up.railway.app`
- `GET /health` → `{"status":"ok","service":"PraxisMed API"}` — HTTP 200
- Commit deployed: `081121b`
- Full suite: 2324/2324 passed

Railway backend URL is now known: `https://web-production-fd91d.up.railway.app`

This is the URL to use for:
- `NEXT_PUBLIC_API_BASE_URL` in Vercel (Module 114)
- Vapi test assistant server URL (Module 115)
- n8n staging endpoint (Module 115)

## Scope

Evidence doc + static tests. No deployment by Claude.
No real secrets. No production data.

### The developer must:

Follow `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md`:

1. In the Railway project (same project as the backend service), add a PostgreSQL plugin
2. Confirm Railway auto-injects `DATABASE_URL` into the backend service environment
3. Wait for Railway PostgreSQL to show "Running" status
4. Redeploy Railway backend — confirm `/health/ready` → 200
5. Run `python backend/scripts/run_migrations.py` via Railway "Run Command"
   - Stop if exit code is non-zero
   - Capture sanitized output (no `DATABASE_URL` value in output)
6. Run `python backend/scripts/db_smoke_test.py` via Railway "Run Command"
   - Confirm 4 tables: clinics, patients, consultation_sessions, audit_log
7. Provision staging fake clinic and user via SQL (one-time INSERT):
   - Use newly generated UUIDs (not `11111111-...` local UUID)
   - Use `doctor.staging@praximed.test` email
   - Use bcrypt hash of a staging-only password (not `local-dev-password`)
   - Do not commit the password itself to any document
8. Confirm `GET /health/ready` → 200 with `{"status":"ready","checks":{"app":"ok","db":"ok"}}`

### Evidence to capture (no secret values):

- Railway PostgreSQL service name
- `DATABASE_URL` injection confirmed (name only — not value)
- Railway backend redeploy status after DATABASE_URL injection
- `GET /health/ready` → 200 response body (after DB wired)
- Migration command: `python backend/scripts/run_migrations.py`
- Migration exit status: `0`
- Sanitized migration output (first/last lines; no DB credentials)
- `alembic current` output: `0002_password_hash (head)`
- `db_smoke_test.py` output (4 tables confirmed)
- Staging fake clinic UUID (not a secret; stable identifier)
- Staging fake user email: `doctor.staging@praximed.test`
- Confirmation that no real patient data was inserted

### Module 113 will create:

1. `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` — update from BLOCKED/PENDING to PASS if evidence provided; otherwise document exact blocker
2. Contract tests
3. Update `STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — mark DATABASE_URL wired, migrations, fake clinic/user as PASS if confirmed
4. Update `STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — mark DB checks as PASS if confirmed
5. Update `CURRENT_STATE.md` and `NEXT_MODULE.md` → Module 114 (Vercel frontend creation evidence)

## What not to do

- Do not deploy Railway PostgreSQL from Claude
- Do not add real secrets
- Do not fabricate PASS evidence
- Do not run `seed_local_data.py` — local UUIDs must not appear in staging
- Do not use `local-dev-password` hash in staging
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint

## Acceptance

- `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` updated (PASS or BLOCKED/PENDING)
- PASS only with real migration evidence
- Contract tests pass
- Full test suite passes (2324/2324 minimum)
- Commit: `Sprint 16 / Module 113 — Railway PostgreSQL provisioning and migration evidence`
