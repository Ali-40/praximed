# Staging DB Migration and Seed Strategy — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 14 / Module 103
**Status:** Planning only — no DB mutation executed in this module

---

## 1. Purpose

This document defines the strategy for migrating and seeding the Railway PostgreSQL staging
database before the first staging smoke execution (Module 104).

**What this document is:**
- The migration execution sequence for the Railway staging DB
- An assessment of existing scripts and what is safe to reuse vs. what is local-only
- A fake staging tenant/user provisioning strategy that does not reuse local-dev data
- The prerequisite reference for Module 104 (Staging Smoke Execution Evidence)

**What this document is not:**
- A deployment execution guide — no database is mutated in this module
- A production launch plan — production PHI launch remains NO-GO
- A real credentials document — no real passwords, tokens, or connection strings appear here
- A staging seed script implementation — the strategy is defined here; implementation is deferred
- A document containing real patient data, real clinic data, or real PHI

Staging uses fake/non-PHI data only. No DB mutation is executed in this module.
Production PHI launch remains NO-GO (all 12 production blockers remain open).

---

## 2. Current DB/Migration Inventory

Actual discovered state as of Module 103 inspection:

| Item | Discovered Value | Notes |
|---|---|---|
| Alembic config | `backend/alembic.ini` | `script_location = %(here)s/migrations` → resolves to `backend/migrations/` |
| Migration folder | `backend/migrations/versions/` | Contains two version files |
| Migration 0001 | `0001_initial_schema.py` | Full schema baseline (11 tables); revision `0001_initial_schema`; `down_revision = None` |
| Migration 0002 | `0002_add_password_hash_to_clinic_users.py` | Adds `password_hash TEXT` to `clinic_users`; revision `0002_password_hash`; `down_revision = "0001_initial_schema"` |
| Migration chain | `None → 0001_initial_schema → 0002_password_hash` | Two migrations; `alembic upgrade head` runs both |
| Migration command | `python backend/scripts/run_migrations.py` | Resolves `backend/alembic.ini` relative to script; runs `alembic -c backend/alembic.ini upgrade head` |
| Migration runner gap | No DB-ready retry loop | If PostgreSQL is not yet accepting connections, migration fails immediately; requires manual timing |
| Seed script | `backend/scripts/seed_local_data.py` | Inserts deterministic local-only UUIDs; see Section 7 for why it must not run in staging |
| Smoke script | `backend/scripts/smoke_vapi_appointment_intake.py` | Hardcodes `LOCAL_CLINIC_ID = "11111111-1111-1111-1111-111111111111"`; local-only |
| DB smoke test | `backend/scripts/db_smoke_test.py` | Verifies 4 core tables exist after migrations; reads `DATABASE_URL` from env; no write operations |
| Local Docker DB | `docker-compose.postgres.yml` — `postgres:16`, port `5433`, DB `praxismed_local` | Local development only; must never be the staging target |
| Local env example | `backend/.env.example` | Shows `DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local`; placeholder secrets only |
| `DATABASE_URL` at runtime | Read from env by both `run_migrations.py` and `backend/app/db/pool.py` | Never hard-coded; must be set in Railway dashboard before any staging command |

**Tables created after both migrations run (`alembic upgrade head`):**
- `clinics` — root tenant table
- `clinic_users` — staff/admin users (includes `password_hash` column after migration 0002)
- `clinic_calendar_connections`
- `clinic_calendar_blocks`
- `clinic_calendar_sync_events`
- `audit_log`
- `clinic_call_logs`
- `appointment_requests`
- `clinic_notifications`
- `patients`
- `consultation_sessions`

---

## 3. Staging Database Target

| Item | Value | Notes |
|---|---|---|
| Platform | Railway managed PostgreSQL | Provisioned as a Railway add-on via the Railway dashboard; distinct from local Docker DB |
| `DATABASE_URL` | Auto-injected by Railway after the PostgreSQL add-on is linked to the service | Never set manually; never hard-coded; never committed to source control |
| Isolation from local | Railway PostgreSQL is a separate service from `docker-compose.postgres.yml` | The local Docker DB on `localhost:5433` is unreachable from Railway |
| Isolation from production | Production database does not exist yet; when created, it must be a separate Railway project or service | Staging and production must never share a DB or connection string |
| Data policy | Fake/non-PHI data only | No real patient names, phone numbers, DOBs, medical records, or real clinic credentials |
| Connection string format | `postgresql://user:password@host:port/dbname` | Railway provides this; format is compatible with `asyncpg.connect()` and `alembic` |
| PostgreSQL version | Railway default (PostgreSQL 14+ or 15+) | Compatible with `asyncpg`, the schema, and all migrations — no version-specific syntax used |
| pgcrypto extension | Required — `CREATE EXTENSION IF NOT EXISTS pgcrypto` in migration 0001 | Railway PostgreSQL supports pgcrypto; `IF NOT EXISTS` makes it idempotent |

---

## 4. Migration Execution Strategy

### 4.1 When to Run Migrations

Migrations must run **after** the Railway PostgreSQL add-on is provisioned and
**before** any staging backend traffic is accepted. The web process (uvicorn) does not
auto-run migrations — this is intentional per Module 101. The Procfile has no migration
command.

### 4.2 Recommended Migration Command

```
python backend/scripts/run_migrations.py
```

Run this from the Railway shell ("Run Command" panel in the Railway dashboard) after the
PostgreSQL add-on is linked to the service and shows "Running" status.

The command:
1. Reads `DATABASE_URL` from the Railway service environment
2. Resolves `backend/alembic.ini`
3. Runs `alembic -c backend/alembic.ini upgrade head`
4. Exits 0 on success; exits non-zero on failure (stop deployment if non-zero)

### 4.3 Migration Execution Rules

| Rule | Detail |
|---|---|
| Wait for Railway PostgreSQL "Running" status | `run_migrations.py` has no DB-ready retry loop; run only after the add-on is confirmed healthy |
| Stop if migrations fail | If the migration command exits non-zero, do not proceed to backend traffic or seed provisioning |
| Do not put migrations in Procfile | Web process (`uvicorn`) must not auto-run migrations; see Procfile in repo root |
| Do not print `DATABASE_URL` | `run_migrations.py` does not log the connection string; verify sanitized output only |
| Capture migration output | Record the sanitized console output, migration revision reached, and timestamp as evidence |
| Idempotency | `alembic upgrade head` is safe to rerun; it checks `alembic_version` table and skips already-applied revisions |

### 4.4 Migration Verification After Run

After `python backend/scripts/run_migrations.py` completes:

```
python backend/scripts/db_smoke_test.py
```

This script verifies that `clinics`, `patients`, `consultation_sessions`, and `audit_log`
exist after migrations. It reads `DATABASE_URL` from env; no write operations. Use it
as a lightweight post-migration sanity check via Railway "Run Command".

### 4.5 Expected Final Migration State

After `alembic upgrade head` completes on the staging DB:
- `alembic_version` table contains `0002_password_hash`
- All 11 tables listed in Section 2 exist with correct columns, indexes, and constraints
- `clinic_users.password_hash` column exists (added by migration 0002)

---

## 5. Migration Readiness Gaps

| Gap | Detail | Risk | Mitigation |
|---|---|---|---|
| No DB-ready retry loop in `run_migrations.py` | Script fails immediately if PostgreSQL is not yet accepting connections | Railway cold-start: PostgreSQL may not be ready when Run Command fires | Wait for Railway PostgreSQL "Running" status before executing; manual timing |
| No migration status verification command | No `alembic current` step included in the migration runner | Cannot easily confirm which revision is applied without running alembic manually | Run `alembic -c backend/alembic.ini current` after migration as a manual check |
| No automatic predeploy command | `railway.toml` `preDeployCommand` not created (per Module 101 decision) | Migration must be run manually for every schema-changing deploy | Acceptable for staging; automate only after dry-run evidence collected |
| **Future improvement** | Add DB-ready retry wrapper that polls `pg_isready` before running `alembic upgrade head` | Eliminates cold-start race condition | Document for Module 104+ implementation if needed |

---

## 6. Fake Staging Tenant/User Strategy

The staging DB must have a fake clinic and a fake staff user before the login smoke can
pass. These rows must be distinct from both local-dev values and any future production
records.

### 6.1 Staging Fake Clinic

| Field | Value | Notes |
|---|---|---|
| `id` (clinic UUID) | `<staging-fake-clinic-id>` (placeholder — generate with `python -c "import uuid; print(uuid.uuid4())"`) | Must not be `11111111-1111-1111-1111-111111111111` (local-dev UUID) |
| `slug` | `staging-fake-clinic` | Distinct from `local-test-clinic` |
| `name` | `Staging Fake Clinic` | Non-PHI; clearly fake label |
| `status` | `active` | Required for authentication and Vapi routing |
| `timezone` | `Europe/Vienna` | Matches the local-dev default; acceptable for staging |
| `locale` | `de-AT` | Matches the local-dev default; acceptable for staging |

### 6.2 Staging Fake Staff User

| Field | Value | Notes |
|---|---|---|
| `id` (user UUID) | `<staging-fake-user-id>` (placeholder — generate with `python -c "import uuid; print(uuid.uuid4())"`) | Must not be `22222222-2222-2222-2222-222222222222` (local-dev UUID) |
| `clinic_id` | `<staging-fake-clinic-id>` from above | Foreign key to staging clinic row |
| `email` | `doctor.staging@praximed.test` | Distinct from `doctor.local@praximed.test`; `.test` TLD is non-routable |
| `full_name` | `Dr. Staging Test` | Clearly fake; no real name |
| `role` | `doctor` | Required for dashboard access |
| `status` | `active` | Required for login |
| `password_hash` | bcrypt hash of a staging-only password — see Section 9 | Must not be the hash of `local-dev-password` |

### 6.3 Isolation Rules

| Rule | Detail |
|---|---|
| No local-dev UUIDs in staging | `11111111-...` and `22222222-...` must not appear in the staging DB |
| No local-dev password hash in staging | Hash of `local-dev-password` must not be used; generate a new staging-only password |
| No real clinic/user data | Staging clinic name, slug, email are all clearly fake |
| No production overlap | When production is eventually provisioned, its clinic UUID and user records must be distinct from staging |
| Staging clinic UUID in Vapi | The staging Vapi test assistant must use `X-Clinic-Ref: <staging-fake-clinic-id>` | Must match the staging DB row |

---

## 7. Local Seed Script Assessment

`backend/scripts/seed_local_data.py` must **not** be run against the staging database
without review and adaptation. Reasons:

| Issue | Detail |
|---|---|
| Hardcoded local-dev UUIDs | `LOCAL_CLINIC_ID = "11111111-1111-1111-1111-111111111111"` and five other deterministic UUIDs are baked into the script; these are labelled "local-only — NEVER used in production" |
| Local-dev email | `LOCAL_LOGIN_EMAIL = "doctor.local@praximed.test"` — explicitly local naming |
| Local-dev password | `LOCAL_LOGIN_PASSWORD_LABEL = "local-dev-password"` — the exact placeholder value that must be absent from staging |
| Local-only labels in output | Script prints "LOCAL-DEV LOGIN (fake/local only — NOT for production)" to stdout — a signal of its intended scope |
| Inserts patients and consultation_sessions | Staging smoke does not require seeded patients or consultation sessions; these rows are noise in staging before Vapi creates real test rows |
| Safe local role | The script serves its intended purpose well: deterministic, idempotent, fast local DB setup after `docker compose up` |
| Staging adaptation | The seed script could be adapted for staging by parameterising the UUIDs and credentials, but this is out of scope for Module 103 — document only |

**Verdict:** `seed_local_data.py` is a local-dev-only script. It must not be executed
against the Railway staging DB in its current form. A separate staging provisioning step
is required (see Section 8).

---

## 8. Recommended Staging Provisioning Approach

For the **first staging smoke** (Module 104), the recommended approach is:

**Option A — Controlled one-time manual SQL provisioning (recommended for Module 104)**

Execute reviewed SQL directly against the Railway staging DB using the Railway shell.
Advantage: no script to maintain; full visibility into what is inserted; no code changes.

Minimum SQL to provision staging fake tenant and user (template — do not execute without
substituting all placeholders and generating a real bcrypt hash):

```sql
-- Staging fake clinic (insert only — idempotent if re-run with ON CONFLICT)
INSERT INTO clinics (id, slug, name, status, timezone, locale)
VALUES (
    '<staging-fake-clinic-id>',
    'staging-fake-clinic',
    'Staging Fake Clinic',
    'active',
    'Europe/Vienna',
    'de-AT'
)
ON CONFLICT (id) DO UPDATE SET
    name       = EXCLUDED.name,
    updated_at = now();

-- Staging fake staff user (insert only — idempotent)
INSERT INTO clinic_users (id, clinic_id, email, full_name, role, status, password_hash)
VALUES (
    '<staging-fake-user-id>',
    '<staging-fake-clinic-id>',
    'doctor.staging@praximed.test',
    'Dr. Staging Test',
    'doctor',
    'active',
    '<bcrypt-hash-of-staging-password>'
)
ON CONFLICT (id) DO UPDATE SET
    email         = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash,
    updated_at    = now();
```

**Option B — Future `backend/scripts/seed_staging_fake_data.py` script**

A staging-specific seed script with parameterised UUIDs and no hardcoded local-dev
values could be created in a future module. This is the right long-term approach but is
out of scope for Module 103.

**Option C — Railway one-time command with reviewed data**

Run a reviewed Python snippet via Railway "Run Command" that inserts fake clinic and user
rows using `asyncpg` and `DATABASE_URL`. Similar to Option A but Python instead of SQL.

**Module 103 recommendation:** Use Option A for the first staging smoke. Option B may be
created in a future module if repeated staging resets are needed.

No automatic production seed. No seed that touches non-staging databases.

---

## 9. Password Hashing for Staging

The staging staff user requires a bcrypt hash of a staging-specific password. The
password itself must not appear in any committed file, log line, or document.

### 9.1 Generate a Staging bcrypt Hash (Safe Method)

Run locally (not committed, not logged):

```
python -c "
from backend.app.core.password_hashing import hash_password
print(hash_password('<your-chosen-staging-password>'))
"
```

The resulting `$2b$...` hash is safe to store in the Railway staging DB and safe to
reference in staging provisioning SQL. The plaintext password must be stored only in a
secure location (password manager or Railway "Variables" panel as a non-printed value).

### 9.2 Password Rules

| Rule | Detail |
|---|---|
| Never commit the plaintext staging password | The plaintext is for the operator only; it belongs in a password manager or Railway secret |
| Never reuse `local-dev-password` | The local-dev placeholder must not become the staging password |
| Never print the password in logs | `seed_local_data.py` prints the password label to stdout; a staging provisioning step must not do this |
| High entropy | The staging password should be at least 16 characters; use a password manager to generate |
| Staging-only | When production is launched, a distinct production password with its own bcrypt hash must be used |

---

## 10. Required Staging Data for Smoke

Minimum fake data required before Module 104 smoke begins:

| Data | Table | Required for | Notes |
|---|---|---|---|
| Fake staging clinic | `clinics` | Login, Vapi routing, all API calls | UUIDs from Section 6.1 |
| Fake staging staff user | `clinic_users` | Login (`POST /auth/login`) | Password hash from Section 9 |
| Fake appointment request (optional seed) | `appointment_requests` | Dashboard appointments section pre-Vapi | Vapi test call will create one; not required to pre-seed |
| Fake patient (optional) | `patients` | Dashboard patients section | Optional for minimal smoke; dashboard renders empty list if none |
| Fake notification (optional) | `clinic_notifications` | Dashboard notifications section | Optional; not required for core login/Vapi smoke |
| Fake consultation (optional) | `consultation_sessions` | Dashboard consultations section | Optional; not required for core login/Vapi smoke |

### 10.1 Expected Dashboard Smoke with Minimal Data

Starting with only clinic + clinic_user provisioned:

| Smoke Step | Expected | Passes With Minimal Data? |
|---|---|---|
| `GET /health` → `{"status": "ok"}` | 200 | Yes — no DB rows required |
| Frontend loads at Vercel URL | 200 | Yes — static build |
| `/login` renders | Form visible | Yes — no DB rows required |
| Login with `doctor.staging@praximed.test` | JWT returned | Yes — requires clinic + clinic_user rows |
| `/dashboard` loads | Dashboard visible | Yes — sections render empty if no rows |
| Appointments section | Empty list (or Vapi-created row) | Yes — empty is valid before Vapi smoke |
| Vapi test call → `POST /vapi/tools/capture-appointment-request` | `status=new`, `action_required=true` | Yes — creates the first appointment_request row |
| Staff Confirm button | `PATCH /appointment-requests/{id}/status` → `confirmed` | Yes — requires JWT and the Vapi-created row |
| CORS success | No CORS error in browser console | Yes — requires correct `FRONTEND_CORS_ORIGINS` on Railway |

---

## 11. Vapi/n8n DB Interaction

### 11.1 Vapi Appointment Intake (Staging)

| Item | Value | Notes |
|---|---|---|
| Endpoint | `POST /vapi/tools/capture-appointment-request` | Railway HTTPS URL + path |
| Clinic routing | `X-Clinic-Ref: <staging-fake-clinic-id>` | Must match the staging DB clinic row |
| Machine auth scope | `X-Vapi-Scopes: vapi:tool` | Singular — `vapi:tools` plural returns HTTP 403 |
| `VAPI_WEBHOOK_SECRET` | Staging-specific secret set in Railway dashboard | Must match Vapi test assistant webhook secret |
| Result in DB | `appointment_requests` row with `status='new'`, `action_required=True` | Created by the endpoint; never auto-confirmed |
| No auto-confirmation | `status='new'` and `action_required=True` are hardcoded on creation | No code path auto-confirms; stop rule if ever observed differently |
| Staff Confirm | `PATCH /appointment-requests/{id}/status` with `{"status": "confirmed"}` | Requires valid JWT; staff action only |
| No real patient calls | Vapi staging test assistant uses fake caller data | No real phone numbers or patient PII |

### 11.2 n8n Calendar Sync (Staging)

| Item | Value | Notes |
|---|---|---|
| Endpoint | `POST /webhooks/n8n/calendar-sync` | Railway HTTPS URL + path |
| Auth | HMAC-signed `X-Signature` header using `N8N_WEBHOOK_SECRET` | Staging n8n workflow must use the staging-specific `N8N_WEBHOOK_SECRET` |
| DB writes | `clinic_calendar_blocks` and `clinic_calendar_sync_events` | Writes to staging DB only; no production calendar |
| Calendar source | Test calendar or fake calendar event JSON | No production Google Calendar connection at staging |
| Module 104 scope | n8n staging smoke is optional for the first smoke pass | Vapi + login + dashboard smoke are higher priority; n8n can follow |

---

## 12. Backup/Rollback Strategy

| Item | Detail |
|---|---|
| Pre-migration snapshot | Railway PostgreSQL supports point-in-time recovery (PITR) on paid plans; request a snapshot before running migrations if the Railway plan supports it |
| Migration rollback | Run `alembic -c backend/alembic.ini downgrade -1` to reverse the last migration; or `downgrade base` to revert all |
| Staging data rollback | Staging data is all fake; if the DB is corrupted, drop and recreate the Railway PostgreSQL add-on; re-run migrations and reprovisioning |
| Production rollback | Out of scope — production DB does not exist; this strategy covers staging only |
| Rollback owner | The developer executing the staging deployment is responsible for rollback decisions |
| Restore test | After any major schema change, verify `alembic current` shows the expected revision and `db_smoke_test.py` passes |
| Failure stop rule | If migrations fail, stop. Do not proceed to seed provisioning, backend traffic, or smoke. Diagnose and fix before retrying. |

---

## 13. Evidence Capture

For each migration/provisioning step in Module 104, capture:

| Evidence Item | Detail |
|---|---|
| Command run | Exact command (sanitized — no `DATABASE_URL` value) |
| Timestamp | UTC timestamp when the command was run |
| Commit SHA | Git commit SHA of the code being deployed |
| Environment | Railway service name; staging tier label |
| Migration output | Sanitized `alembic upgrade head` console output (INFO lines; no credentials) |
| Final migration revision | `0002_password_hash` expected after `upgrade head` |
| DB smoke test result | Output of `db_smoke_test.py` (table existence check; no credentials) |
| Staging fake clinic UUID | The staging clinic UUID used (not a secret; not PHI) |
| Staging fake user email | `doctor.staging@praximed.test` (not a secret) |
| Login smoke result | HTTP 200 + JWT returned (mask the JWT value in logs) |
| No secrets/PII in evidence | Verify before recording: no `DATABASE_URL` values, no passwords, no bcrypt hashes, no real patient data |

---

## 14. Failure Stop Rules

Stop staging execution immediately if any of the following are observed:

| Rule | Trigger |
|---|---|
| Wrong DATABASE_URL target | `DATABASE_URL` points to local Docker DB (`localhost:5433`) or production DB |
| Migration failure | `run_migrations.py` exits non-zero; stop before seed provisioning |
| Credentials in logs | `DATABASE_URL`, JWT_SECRET_KEY, bcrypt hash, or any secret appears in a log line |
| Real patient data appears | Any real name, phone number, DOB, or medical record visible in DB, logs, or dashboard |
| Seed script targets wrong DB | `seed_local_data.py` run against staging DB (wrong script for staging) |
| Production DB touched | Any write to a production database row |
| Duplicate clinic/user blocks login | ON CONFLICT handling fails; login returns 401 unexpectedly |
| Auto-confirmed appointment request | Any `appointment_requests` row with `status='confirmed'` that was not explicitly confirmed via `PATCH` by a staff user |
| n8n writes to production calendar | n8n staging workflow connection points to a production calendar service |
| Vapi test assistant uses production phone number | Any real caller phone number in staging Vapi test call |

---

## 15. Open Blockers Before Actual Staging DB Setup

The following cannot proceed until the Railway services are created and configured:

| # | Blocker | Level | Module |
|---|---|---|---|
| 1 | Railway PostgreSQL add-on not yet provisioned | **HIGH** | Module 104 execution |
| 2 | `DATABASE_URL` not yet available (injected by Railway after provisioning) | **HIGH** | Module 104 execution |
| 3 | Staging fake clinic UUID not yet generated (placeholder in this doc) | **HIGH** | Module 104 pre-smoke |
| 4 | Staging fake user UUID not yet generated (placeholder in this doc) | **HIGH** | Module 104 pre-smoke |
| 5 | Staging password not yet created or hashed | **HIGH** | Module 104 pre-smoke |
| 6 | `VAPI_WEBHOOK_SECRET` not yet set in Railway dashboard | **HIGH** | Module 104 pre-smoke |
| 7 | `N8N_WEBHOOK_SECRET` not yet set in Railway dashboard | MEDIUM | Module 104 pre-smoke |
| 8 | Migration command not yet run against staging DB | **HIGH** | Module 104 execution |
| 9 | DB-ready retry not implemented in `run_migrations.py` | MEDIUM | Known gap; manual timing sufficient for first smoke |
| 10 | Staging fake clinic/user SQL not yet reviewed and executed | **HIGH** | Module 104 pre-smoke |
| 11 | Vapi test assistant not yet configured for staging Railway URL and staging clinic UUID | **HIGH** | Module 104 setup |
| 12 | Staging smoke not yet executed | **HIGH** | Module 104 |

---

## 16. Non-Goals

- No database mutation in this module
- No deployment or Railway service creation
- No production launch (all 12 production blockers remain open)
- No real patient data, real clinic data, or PHI
- No auth/session hardening implementation (deferred; Sprint 14 post-smoke evidence)
- No staging seed script implementation (strategy documented; implementation is future)
- No Fabel 5 / frontend UX work
- No appointment workflow expansion
- No real secrets in any file created by this module
- No `npm install` or frontend changes

---

## 17. Recommended Next Step — Module 104

**Sprint 14 / Module 104 — Staging Smoke Execution Evidence**

Before Module 104 can be executed, the Railway and Vercel services must be created
manually by the developer (outside this Claude Code session). Once created:

- Railway backend service deployed with correct env vars
- Railway PostgreSQL add-on linked; `DATABASE_URL` injected
- Migrations run via Railway "Run Command"
- Staging fake clinic and user provisioned (Section 8)
- Vercel frontend deployed with `NEXT_PUBLIC_API_BASE_URL` set to Railway URL
- `FRONTEND_CORS_ORIGINS` on Railway updated to exact Vercel URL

Module 104 should:
- Document the actual staging smoke evidence (backend health, frontend load, DB migration
  verification, login/dashboard, Vapi fake call, staff Confirm)
- If Railway/Vercel services do not yet exist, document the exact blockers preventing
  smoke execution rather than claiming a pass
- Not use real patient data, real credentials, or PHI at any step
