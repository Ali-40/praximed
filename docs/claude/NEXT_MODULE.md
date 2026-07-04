# Sprint 16 / Module 115 — Fake Staging Clinic and User Provisioning Evidence

Status: pending manual fake staging clinic/user provisioning in Railway PostgreSQL.

## Context

Module 114 complete:
- Railway PostgreSQL migration retest: **PASS**
- `run_migrations.py` exit 0; both revisions applied (`0001_initial_schema`, `0002_password_hash`)
- `db_smoke_test.py` PASS: clinics, patients, consultation_sessions, audit_log all confirmed
- `/health` still `{"status":"ok","service":"PraxisMed API"}` — HTTP 200
- Full test suite: 2360/2360 passed
- Commit: (see git log)

Railway backend URL: `https://web-production-fd91d.up.railway.app`
Database tables confirmed ready. No fake data rows inserted yet.

## Scope

Evidence doc + static tests. No deployment by Claude.
No real secrets. No production data. No real patient data.

### The developer must:

Follow `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` Section 7:

1. Connect to Railway PostgreSQL via Railway console (Data tab → psql or query editor)
2. INSERT a fake staging clinic row:
   - Generate a new UUID (do NOT use `11111111-1111-1111-1111-111111111111`)
   - `slug='staging-fake-clinic'` or similar fake identifier
   - No real clinic name, address, or contact data
3. INSERT a fake staging user row:
   - Email: `doctor.staging@praximed.test`
   - bcrypt hash of a staging-only password (NOT `local-dev-password`)
   - Do not record the password itself in any document
   - clinic_id = the fake clinic UUID from step 2
4. Confirm `SELECT * FROM clinics WHERE slug='staging-fake-clinic'` returns 1 row
5. Confirm `SELECT email FROM clinic_users WHERE email='doctor.staging@praximed.test'` returns 1 row
6. Confirm `GET /health/ready` → 200 with `{"status":"ready","checks":{"app":"ok","db":"ok"}}`

### Evidence to capture (no secret values):

- Staging fake clinic UUID (not a secret; stable staging identifier)
- Staging fake clinic slug/name (fake data only)
- Staging fake user email: `doctor.staging@praximed.test`
- `SELECT` confirmation (row count or redacted row — no password hash in evidence)
- `GET /health/ready` → 200 response body
- Confirmation that no real patient data was inserted
- Confirmation that no local-dev password hash was used

### Module 115 will create/update:

1. `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` — add fake clinic/user PASS rows; add `/health/ready` PASS
2. Contract tests for fake staging clinic/user provisioning evidence
3. Update `STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — mark fake clinic/user PASS; `/health/ready` PASS
4. Update `STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — mark check 2 (`/health/ready`) PASS; mark fake login row PASS if confirmed; fake login still PENDING without Vercel
5. Update `CURRENT_STATE.md` and `NEXT_MODULE.md` → Module 116 (Vercel frontend creation evidence)

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
- PASS only with real SELECT confirmation from real Railway PostgreSQL
- Contract tests pass
- Full test suite passes (2360/2360 minimum)
- Commit: `Sprint 16 / Module 115 — Fake staging clinic and user provisioning evidence`
