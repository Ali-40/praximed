# Sprint 16 / Module 114 — Railway PostgreSQL Migration Retest Evidence

Status: pending push, Railway redeploy, and migration rerun.

## Context

Module 113 complete:
- `psycopg2-binary==2.9.9` added to both `requirements.txt` and `backend/requirements.txt`
- Root cause of migration failure documented: SQLAlchemy/Alembic requires synchronous psycopg2 driver even when asyncpg is installed for runtime async DB access
- Migration runbook updated with Section 6.1a (driver requirements) and new failure triage row
- Migration evidence doc updated: PostgreSQL Online PASS; DATABASE_URL wired PASS; migration still PENDING (awaiting rerun after fix)
- Full test suite: 2338/2338 passed
- Commit: (see git log)

Railway PostgreSQL is already provisioned and DATABASE_URL is already wired.
The only remaining step is to push the psycopg2-binary fix, redeploy the backend, and rerun the migration.

Railway backend URL: `https://web-production-fd91d.up.railway.app`

## Scope

Evidence doc + static tests. No deployment by Claude.
No real secrets. No production data.

### The developer must:

1. Push current branch to GitHub (the psycopg2-binary fix is now in the repo)
2. Railway will auto-redeploy from the push (or trigger manually)
3. Confirm Railway backend redeploy succeeds — `/health` → 200
4. Run `python backend/scripts/run_migrations.py` via Railway "Run Command"
   - Stop if exit code is non-zero
   - Capture sanitized output (no DATABASE_URL value in output)
5. Run `python backend/scripts/db_smoke_test.py` via Railway "Run Command"
   - Confirm 4 tables: clinics, patients, consultation_sessions, audit_log
6. Run `alembic current` via Railway "Run Command" — confirm `0002_password_hash (head)`
7. Confirm `GET /health/ready` → 200 with `{"status":"ready","checks":{"app":"ok","db":"ok"}}`
8. Provision staging fake clinic and user via SQL (one-time INSERT):
   - Use newly generated UUIDs (not `11111111-...` local UUID)
   - Use `doctor.staging@praximed.test` email
   - Use bcrypt hash of a staging-only password (not `local-dev-password`)
   - Do not commit the password itself to any document

### Evidence to capture (no secret values):

- Railway backend redeploy status after psycopg2-binary fix
- `GET /health` → 200 after redeploy (confirm backend still healthy)
- Migration command: `python backend/scripts/run_migrations.py`
- Migration exit status: `0`
- Sanitized migration output (first/last lines; no DB credentials)
- `alembic current` output: `0002_password_hash (head)`
- `db_smoke_test.py` output (4 tables confirmed)
- `GET /health/ready` → 200 response body
- Staging fake clinic UUID (not a secret; stable identifier)
- Staging fake user email: `doctor.staging@praximed.test`
- Confirmation that no real patient data was inserted

### Module 114 will create/update:

1. `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` — update from BLOCKED/PENDING to PASS if migration succeeds; document exact blocker if still failing
2. Contract tests for migration retest evidence
3. Update `STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — mark DATABASE_URL wired, migrations, fake clinic/user as PASS if confirmed
4. Update `STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — mark DB checks as PASS if confirmed
5. Update `CURRENT_STATE.md` and `NEXT_MODULE.md` → Module 115 (Vercel frontend creation evidence)

## What not to do

- Do not deploy Railway from Claude
- Do not add real secrets
- Do not fabricate PASS evidence
- Do not run `seed_local_data.py` — local UUIDs must not appear in staging
- Do not use `local-dev-password` hash in staging
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint

## Acceptance

- `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` updated (PASS or BLOCKED/PENDING with real evidence)
- PASS only with real migration output from real Railway service
- Contract tests pass
- Full test suite passes (2338/2338 minimum)
- Commit: `Sprint 16 / Module 114 — Railway PostgreSQL migration retest evidence`
