# Railway PostgreSQL Provisioning and Migration Runbook — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 15 / Module 106
**Status:** Planning only — no deployment executed by Claude in this module

---

## 1. Purpose

This is a human-executable step-by-step guide for provisioning the Railway PostgreSQL
staging database, wiring `DATABASE_URL` to the backend service, and running migrations
for the first time against the staging DB.

**What this runbook is:**
- Exact steps for adding Railway PostgreSQL to the staging project
- The migration execution sequence and evidence capture checklist
- A failure triage reference for common provisioning and migration issues

**What this runbook is not:**
- A deployment executed by Claude — no Railway API calls are made here
- A production DB guide — this covers fake-data staging only
- A Vercel frontend guide — that is Module 107
- A document containing real secrets or real `DATABASE_URL` values

Staging uses fake/non-PHI data only. No deployment is executed in this module.
No real patient data. No production secrets.

---

## 2. Current Status

| Item | Status | Source |
|---|---|---|
| Railway backend service creation runbook | READY | Module 105 |
| `python backend/scripts/run_migrations.py` | READY | Module 45 |
| `backend/scripts/db_smoke_test.py` | READY | Module 45 |
| Migration 0001: `0001_initial_schema` | READY | Module 45 |
| Migration 0002: `0002_add_password_hash_to_clinic_users` | READY | Module 59 |
| `backend/alembic.ini` — `script_location = %(here)s/migrations` | READY | Module 45 |
| Staging fake tenant/user provisioning strategy | READY | Module 103 |
| Railway PostgreSQL add-on created | **PENDING** | External — developer action required |
| `DATABASE_URL` injected into Railway backend service | **PENDING** | Follows PostgreSQL add-on creation |
| Migrations run against staging DB | **PENDING** | Follows `DATABASE_URL` injection |
| Staging fake clinic/user provisioned | **PENDING** | Follows successful migration |
| Migration evidence captured | **PENDING** | See `RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` |

---

## 3. Preconditions for the Developer

Verify all of the following before starting PostgreSQL provisioning:

### 3.1 Module 105 Preconditions

- [ ] Railway backend service exists (Module 105 runbook followed)
- [ ] `GET https://<railway-backend-url>/health` returns `{"status": "ok"}` — 200
- [ ] Railway backend service `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET` env vars are set in Railway Variables panel

### 3.2 Data Safety Check

- [ ] Confirm no real patient data will be stored in the staging DB
- [ ] Confirm staging Railway PostgreSQL will be completely isolated from any future production DB
- [ ] Confirm the local Docker `DATABASE_URL` (`postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local`) will NOT be used in Railway
- [ ] Confirm no production `DATABASE_URL` exists yet (production DB not yet provisioned)

---

## 4. Railway PostgreSQL Creation Steps

### Step 4.1 — Open the Railway Staging Project

1. Log in to https://railway.app
2. Open the `praxismed-staging` project (or whichever project contains the backend service from Module 105)

### Step 4.2 — Add PostgreSQL Database

1. In the Railway project, click **+ New** or **Add Service**
2. Choose **Database** → **PostgreSQL**
3. Railway provisions a managed PostgreSQL instance and adds it to the project

**Recommended database service name:** `praxismed-postgres-staging`

Railway will assign a private `DATABASE_URL` to the PostgreSQL service automatically.

### Step 4.3 — Confirm DATABASE_URL Availability

After PostgreSQL is provisioned:
1. Open the PostgreSQL service → **Variables** tab
2. Confirm `DATABASE_URL` is present — it will look like `postgresql://postgres:<generated-password>@<railway-postgres-host>:<port>/<db-name>`
3. **Do not copy this value into any document or chat.** Record only that it exists.

### Step 4.4 — Link DATABASE_URL to the Backend Service

Railway can auto-inject `DATABASE_URL` from the PostgreSQL service into the backend service:

1. Open the Railway backend service → **Variables** tab
2. Click **+ New Variable** → choose **Add Reference**
3. Select the PostgreSQL service's `DATABASE_URL` variable as the reference
4. Alternatively: in the Railway backend service Variables panel, add a variable named `DATABASE_URL` with value `${{praxismed-postgres-staging.DATABASE_URL}}` (Railway variable reference syntax)
5. Confirm `DATABASE_URL` appears in the backend service Variables panel (value shown as a Railway reference, not the raw connection string)

Railway will automatically redeploy the backend service with `DATABASE_URL` injected.

### Step 4.5 — Wait for PostgreSQL "Running" Status

Before running migrations, confirm:
- The Railway PostgreSQL service shows **Running** in the Railway dashboard
- The Railway backend service has redeployed with the new `DATABASE_URL`
- `GET /health/ready` on the backend should now return 200 (if the pool connected successfully)

`run_migrations.py` has no DB-ready retry loop — if PostgreSQL is still starting, the
migration will fail immediately. Wait for the "Running" status before proceeding.

---

## 5. Backend DATABASE_URL Wiring Verification

Before running migrations, verify `DATABASE_URL` is correctly wired:

| Check | How to Verify | Safe Result |
|---|---|---|
| `DATABASE_URL` name appears in backend Variables panel | Railway dashboard → backend service → Variables | Variable name `DATABASE_URL` visible; value is a reference (not raw string) |
| Backend service redeployed after injection | Railway dashboard → backend service → Deployments | Deployment timestamp newer than PostgreSQL provisioning |
| `/health/ready` returns 200 | `curl https://<railway-backend-url>/health/ready` | `{"status": "ready"}` or DB-connected 200 response |
| Railway backend log shows DB pool initialized | Railway backend service → Logs | Line similar to: `Database pool initialised successfully` |

**Safety rules:**
- Never paste the raw `DATABASE_URL` value into any document, chat, or log
- Confirm the `DATABASE_URL` points to the Railway staging PostgreSQL (not local Docker, not production)
- Never use `DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local` in Railway

---

## 6. Migration Execution

### 6.1 When to Run

Run the migration command only after:
1. Railway PostgreSQL is provisioned and shows "Running"
2. `DATABASE_URL` is injected into the Railway backend service
3. `/health/ready` returns 200 (confirms DB pool connected)

### 6.1a PostgreSQL Driver Requirements

Alembic/SQLAlchemy migrations require a **synchronous** PostgreSQL driver at runtime.
The PraxisMed backend uses two drivers with different roles:

| Driver | Package | Role | Required For |
|---|---|---|---|
| `asyncpg` | `asyncpg==0.31.0` | Async driver | Runtime API — `backend/app/db/pool.py` connection pool; all API request handlers |
| `psycopg2-binary` | `psycopg2-binary==2.9.9` | Sync driver | SQLAlchemy/Alembic migrations — `run_migrations.py` uses `alembic upgrade head` which needs a sync driver |

**Both must be installed.** Removing `asyncpg` breaks the runtime API. Removing `psycopg2-binary`
causes migration failures with:

```
ModuleNotFoundError: No module named 'psycopg2'
ERROR: Migration failed
```

This was confirmed by a real Railway migration failure where `psycopg2-binary` was missing
from `requirements.txt`. The fix is to ensure both packages appear in `requirements.txt`
(repo root) and `backend/requirements.txt`.

### 6.2 Migration Command

Run this command via the Railway backend service **Shell** panel or **Run Command** feature:

```
python backend/scripts/run_migrations.py
```

This command:
1. Reads `DATABASE_URL` from the Railway environment (auto-injected)
2. Resolves `backend/alembic.ini` (at `backend/alembic.ini` relative to repo root)
3. Runs `alembic -c backend/alembic.ini upgrade head`
4. Applies two migrations in sequence:
   - `0001_initial_schema` — creates 11 tables (clinics, clinic_users, clinic_calendar_connections, clinic_calendar_blocks, clinic_calendar_sync_events, audit_log, clinic_call_logs, appointment_requests, clinic_notifications, patients, consultation_sessions)
   - `0002_password_hash` — adds `password_hash TEXT` column to `clinic_users`
5. Exits 0 on success; exits non-zero on failure

### 6.3 Migration Execution Rules

| Rule | Detail |
|---|---|
| Wait for Railway PostgreSQL "Running" status | No DB-ready retry in `run_migrations.py`; fails immediately if DB not yet accepting connections |
| Stop if migration exits non-zero | Do not proceed to fake data provisioning or smoke if migration fails |
| Do not run from Procfile | The web process must not auto-run migrations; this is a manual predeploy step |
| Do not print `DATABASE_URL` | Capture sanitized output only; no connection strings in evidence |
| Capture the exit code | Exit 0 = success; any non-zero = migration failed |
| Idempotency | `alembic upgrade head` checks `alembic_version` table; safe to rerun if already at head |

### 6.4 Expected Migration Output (Sanitized Template)

When migrations succeed, the Railway "Run Command" output will look similar to:

```
Running: alembic -c backend/alembic.ini upgrade head
INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial_schema, Initial schema baseline
INFO  [alembic.runtime.migration] Running upgrade 0001_initial_schema -> 0002_password_hash, Add password_hash column
```

If already at head (idempotent rerun):
```
Running: alembic -c backend/alembic.ini upgrade head
INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

---

## 7. Migration Verification

### 7.1 DB Smoke Test

After `run_migrations.py` exits 0, run the DB smoke test via Railway "Run Command":

```
python backend/scripts/db_smoke_test.py
```

Expected output:
```
✓ Database connectivity OK (SELECT 1 passed)
✓ Table 'clinics' exists
✓ Table 'patients' exists
✓ Table 'consultation_sessions' exists
✓ Table 'audit_log' exists

Smoke test passed. Database is ready for local development.
```

If any table is missing, the output will show a failure line and exit non-zero.
Stop and investigate before proceeding.

### 7.2 Alembic Version Check (Optional)

To confirm the exact migration revision applied, run via Railway "Run Command":

```
alembic -c backend/alembic.ini current
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
0002_password_hash (head)
```

---

## 8. Health/Readiness Expectations

| Stage | `/health` | `/health/ready` | Notes |
|---|---|---|---|
| Before `DATABASE_URL` injection | 200 | 503 | Expected — `db_pool = None` |
| After `DATABASE_URL` injection, before migration | 200 | 200 (if pool connected) or 503 | Pool may connect; tables don't exist yet; DB routes will fail at query time |
| After migration, before fake data | 200 | 200 | Tables exist; clinic/user rows not yet present |
| After fake data provisioning | 200 | 200 | Full staging DB ready for login smoke |

Note: `/health/ready` returning 200 after `DATABASE_URL` injection does not mean
migrations have run — it only means the asyncpg pool connected. Migrations create the
schema; the pool connecting does not.

---

## 9. Staging Fake Data Provisioning

After migrations succeed, provision the staging fake clinic and user. This is a separate
step from migrations; it inserts data rows, not schema.

**Do NOT run `seed_local_data.py` against the staging DB.** That script uses hardcoded
local-dev UUIDs (`11111111-...`, `22222222-...`) and hashes `local-dev-password`. Running
it in staging would contaminate staging with local-dev assumptions (per Module 103 assessment).

### 9.1 Generate Staging UUIDs

Run locally (not on Railway) to generate fresh UUIDs for staging:

```
python -c "import uuid; print(uuid.uuid4())"
```

Run twice: once for the staging clinic UUID, once for the staging user UUID. Store the
values in a password manager or secure notes — they are not secrets but should be
consistent across all staging smoke steps.

### 9.2 Generate Staging bcrypt Hash

Run locally (not on Railway, not committed):

```python
python -c "
from backend.app.core.password_hashing import hash_password
print(hash_password('<your-chosen-staging-password>'))
"
```

The `$2b$...` output is the bcrypt hash. Store the plaintext password in a password
manager. Do not commit either value.

### 9.3 Provisioning SQL

Run the following via Railway backend service "Run Command" (replace all placeholders):

```sql
-- Run as a psql command or via a Python snippet against DATABASE_URL
-- Do not paste DATABASE_URL into docs; use Railway's shell environment

-- Staging fake clinic
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

-- Staging fake staff user
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

**Alternatively**, run a Python snippet via Railway backend service "Run Command" that
connects to the DB via `asyncpg` using the injected `DATABASE_URL`.

### 9.4 Verification Queries

After provisioning, confirm the rows exist:

```sql
SELECT id, slug, name, status FROM clinics WHERE slug = 'staging-fake-clinic';
SELECT id, email, role, status FROM clinic_users WHERE email = 'doctor.staging@praximed.test';
```

Expected: 1 row each. Record the staging clinic UUID — it is needed for Vapi test
assistant configuration (Module 108).

---

## 10. Evidence to Capture

Record the following after provisioning and migration. No secret values, no `DATABASE_URL`
value, no bcrypt hashes.

| Evidence Item | Value to Record | Notes |
|---|---|---|
| Commit SHA deployed (backend) | Full SHA from Railway deployment log | Confirms exact code version |
| Railway project name | e.g., `praxismed-staging` | From Railway dashboard |
| Railway backend service name | e.g., `praxismed-backend-staging` | From Railway dashboard |
| Railway PostgreSQL service name | e.g., `praxismed-postgres-staging` | From Railway dashboard |
| `DATABASE_URL` injection confirmed | "DATABASE_URL variable reference appears in backend Variables panel" | Do NOT record value |
| Migration command run | `python backend/scripts/run_migrations.py` | Exact command |
| Migration timestamp | UTC timestamp | When the command was run |
| Migration exit status | `0` (success) or non-zero (failure) | Required |
| Sanitized migration output | INFO lines from `alembic upgrade head` | No connection string values |
| Final migration revision | `0002_password_hash (head)` | From `alembic current` or migration output |
| DB smoke test result | All 4 tables confirmed present | From `db_smoke_test.py` output |
| `/health/ready` HTTP status | `200` | After `DATABASE_URL` wired and migration complete |
| Staging fake clinic UUID | `<staging-fake-clinic-id>` | Not a secret; needed for Vapi config |
| Staging fake user email | `doctor.staging@praximed.test` | Not a secret |
| No secrets in evidence | Confirmed | Verify before recording |

---

## 11. Failure Triage

| Symptom | Likely Cause | Where to Inspect | Safe Next Action |
|---|---|---|---|
| `DATABASE_URL` not set in backend Variables | PostgreSQL service not linked | Railway backend service → Variables panel | Link PostgreSQL `DATABASE_URL` as a variable reference; redeploy |
| `/health/ready` still 503 after `DATABASE_URL` injection | Backend not redeployed after injection; or PostgreSQL not yet "Running" | Railway backend service → Deployments | Trigger a manual redeploy; wait for PostgreSQL "Running" status |
| Migration fails: `ERROR: DATABASE_URL environment variable is not set` | Migration run before `DATABASE_URL` was injected | Railway "Run Command" output | Inject `DATABASE_URL` into backend service first; redeploy; then retry |
| Migration fails: `Connection refused` or `could not connect` | PostgreSQL still cold-starting | Railway PostgreSQL service → Status | Wait for PostgreSQL to show "Running"; retry migration |
| Migration fails: `alembic.ini not found` | Command run from wrong directory | Railway "Run Command" output | Use `python backend/scripts/run_migrations.py` (runs from repo root) — do not `cd backend/` first |
| Migration fails: `ModuleNotFoundError: No module named 'psycopg2'` | `psycopg2-binary` missing from `requirements.txt` — Alembic/SQLAlchemy needs the sync driver even when `asyncpg` is present | Railway "Run Command" output | Add `psycopg2-binary==2.9.9` to `requirements.txt` (repo root) and `backend/requirements.txt`; push and redeploy Railway before retrying |
| Migration fails: `ModuleNotFoundError: No module named 'alembic'` | `backend/requirements.txt` deps not installed in the Railway environment | Railway backend build log | Confirm `alembic==1.18.5` in `backend/requirements.txt` and Nixpacks build installed it |
| Migration fails: `SSL connection required` | Railway PostgreSQL requires SSL; asyncpg/alembic connection string needs `?ssl=require` | Migration error output | Add `?ssl=require` to `DATABASE_URL` in Railway Variables if Railway requires it |
| `db_smoke_test.py` fails: table not found | Migrations did not complete | `db_smoke_test.py` output | Rerun migration; check alembic revision state with `alembic current` |
| Staging provisioning SQL fails: `duplicate key` | Row already exists from a previous attempt | SQL output | Use the `ON CONFLICT DO UPDATE` clause as shown in Section 9.3; it handles re-runs safely |
| Credentials appear in Railway log output | `DATABASE_URL` printed accidentally | Railway log stream | Audit `run_migrations.py` and `db_smoke_test.py` — both are designed not to print the URL; check for any custom logging |
| Production DB accidentally targeted | Wrong `DATABASE_URL` used | Railway Variables panel | Stop; remove the wrong `DATABASE_URL`; confirm you are in the correct Railway project and environment |

---

## 12. Stop Rules

Stop immediately if any of the following are observed:

| Stop Rule | Trigger |
|---|---|
| `DATABASE_URL` points to local Docker DB | Value contains `localhost`, `127.0.0.1:5433`, or `praxismed_local_password` |
| `DATABASE_URL` points to a production DB | Any production host or credentials detected |
| Railway prints secrets in log output | Any `JWT_SECRET_KEY`, `openssl`-generated value, or `DATABASE_URL` password visible in logs |
| Migration targets wrong database | Evidence shows tables from an unexpected schema; stop and verify target |
| Real patient data appears in any query result | Any real name, phone number, DOB, or medical record; staging uses fake data only |
| Migration exits non-zero | Stop; diagnose root cause before retrying or proceeding to smoke |
| Production DB touched | Any write to a production DB row; staging must never connect to production |
| Developer cannot verify project/service identity | If there is any ambiguity about which Railway project or PostgreSQL service is being targeted, stop and verify before running migrations |

---

## 13. Result States

| State | Meaning |
|---|---|
| **PASS** | Real Railway PostgreSQL created; `DATABASE_URL` wired to backend service; `python backend/scripts/run_migrations.py` ran and exited 0; `db_smoke_test.py` confirmed all 4 tables; `/health/ready` returns 200; sanitized evidence captured |
| **BLOCKED/PENDING** | Railway PostgreSQL not yet created; or migration not yet run; or evidence not yet available |
| **FAIL** | Provisioning or migration was attempted and failed with a documented error that blocks further progress |

**Current result: BLOCKED/PENDING** — Railway PostgreSQL has not yet been provisioned
and migration evidence has not been provided. See `RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md`
for the current evidence status.

---

## 14. What This Runbook Does Not Cover

| Topic | Covered In |
|---|---|
| Railway backend service creation | Module 105 |
| Vercel frontend project creation | Module 107 |
| `NEXT_PUBLIC_API_BASE_URL` configuration | Module 107 |
| `FRONTEND_CORS_ORIGINS` final value | Module 107 (after Vercel URL is known) |
| CORS preflight verification | Module 108 |
| Vapi test assistant staging URL | Module 108 |
| n8n staging workflow | Module 108 |
| Full staging smoke execution | Module 109 |
| Auth/session hardening | Post-smoke; Sprint 15 |
| Production DB provisioning | Production PHI remains NO-GO |

---

## 15. Recommended Next Step — Module 107

**Sprint 15 / Module 107 — Vercel Frontend Project Creation Runbook**

After completing this runbook and confirming:
- `/health/ready` returns 200
- Migrations applied; all tables exist
- Staging fake clinic and user provisioned
- Staging clinic UUID recorded for Vapi configuration

Proceed to Module 107 to create the Vercel frontend project and set `NEXT_PUBLIC_API_BASE_URL`
to the Railway backend HTTPS URL.
