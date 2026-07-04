# Railway PostgreSQL Migration Evidence — PraxisMed

**Date:** 2026-07-04
**Sprint:** Sprint 16 / Module 114
**Status:** PASS — migrations applied; DB smoke passed; /health still 200

---

## 1. Purpose

This document records the actual evidence from Railway PostgreSQL provisioning and
migration execution for PraxisMed fake-data staging.

**Accuracy policy:** No evidence step is marked PASS without real proof from a real
Railway PostgreSQL service. No evidence is fabricated. If a step has not been executed
against a real service, its status is PENDING or BLOCKED.

Staging uses fake/non-PHI data only. No production DB. No real patient data.
No secrets recorded in this document.

---

## 2. Current Result

**Overall result: PASS**

Railway PostgreSQL is provisioned and `DATABASE_URL` is wired to the backend service.
`psycopg2-binary==2.9.9` was added in Module 113 to resolve the earlier
`ModuleNotFoundError: No module named 'psycopg2'` failure. After redeploy, the
migration command succeeded and DB smoke confirmed all 4 required tables exist.

---

## 3. Migration Failure History

| Module | Event | Status |
|---|---|---|
| Module 113 (attempt 1) | `python backend/scripts/run_migrations.py` failed — `ModuleNotFoundError: No module named 'psycopg2'` | FAIL |
| Module 113 (fix) | `psycopg2-binary==2.9.9` added to `requirements.txt` and `backend/requirements.txt` | FIX APPLIED |
| Module 114 (retest) | Migration command rerun after redeploy — exit 0 | **PASS** |

Root cause of Module 113 failure: SQLAlchemy/Alembic requires a synchronous PostgreSQL
driver (`psycopg2`) for migrations even when `asyncpg` (async runtime driver) is
installed. Both must coexist in requirements.

---

## 4. Evidence

| Evidence Item | Value | Status |
|---|---|---|
| Railway backend URL | `https://web-production-fd91d.up.railway.app` | **PASS** |
| `GET /health` HTTP status | `200` | **PASS** |
| `GET /health` response body | `{"status":"ok","service":"PraxisMed API"}` | **PASS** |
| Railway PostgreSQL service status | Online / Running | **PASS** |
| `DATABASE_URL` injection confirmed | Confirmed wired to Railway backend service (name only — value not recorded) | **PASS** |
| Migration command | `python backend/scripts/run_migrations.py` | **PASS** |
| Migration exit status | `0` | **PASS** |
| Migration revision 0001 applied | `Running upgrade -> 0001_initial_schema, Initial schema baseline — PraxisMed Modules 1–40` | **PASS** |
| Migration revision 0002 applied | `Running upgrade 0001_initial_schema -> 0002_password_hash, Add password_hash column to clinic_users — PraxisMed Sprint 7 / Module 59` | **PASS** |
| Final migration revision | `0002_password_hash (head)` | **PASS** |
| DB smoke command | `python backend/scripts/db_smoke_test.py` | **PASS** |
| Database connectivity | `✓ Database connectivity OK (SELECT 1 passed)` | **PASS** |
| Table `clinics` exists | `✓ Table 'clinics' exists` | **PASS** |
| Table `patients` exists | `✓ Table 'patients' exists` | **PASS** |
| Table `consultation_sessions` exists | `✓ Table 'consultation_sessions' exists` | **PASS** |
| Table `audit_log` exists | `✓ Table 'audit_log' exists` | **PASS** |
| DB smoke final result | `Smoke test passed. Database is ready for local development.` | **PASS** |
| Staging fake clinic UUID | Not yet provisioned | PENDING |
| Staging fake user email | Not yet provisioned | Expected: `doctor.staging@praximed.test` | PENDING |
| `/health/ready` HTTP status | Not yet confirmed (fake user not yet provisioned) | PENDING |
| No secrets in evidence | Confirmed — `DATABASE_URL` value not recorded; no passwords in evidence | **PASS** |
| No real patient data | Confirmed — no real patient records inserted | **PASS** |
| Fake/non-PHI staging only | Confirmed — staging uses synthetic test data only | **PASS** |

---

## 5. Sanitized Migration Output

```
Running: alembic -c /app/backend/alembic.ini upgrade head
INFO [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO [alembic.runtime.migration] Will assume transactional DDL.
INFO [alembic.runtime.migration] Running upgrade -> 0001_initial_schema, Initial schema baseline — PraxisMed Modules 1–40.
INFO [alembic.runtime.migration] Running upgrade 0001_initial_schema -> 0002_password_hash, Add password_hash column to clinic_users — PraxisMed Sprint 7 / Module 59.
```

No `DATABASE_URL` value appears in migration output. No secrets. No PII.

---

## 6. Sanitized DB Smoke Output

```
✓ Database connectivity OK (SELECT 1 passed)
✓ Table 'clinics' exists
✓ Table 'patients' exists
✓ Table 'consultation_sessions' exists
✓ Table 'audit_log' exists
Smoke test passed. Database is ready for local development.
```

---

## 7. What This Proves

- **Railway PostgreSQL exists and is reachable from the Railway backend service** —
  `SELECT 1` passed; DB connectivity confirmed
- **Backend can connect to Railway PostgreSQL** — Alembic context initialized without
  connection error; `asyncpg` runtime driver + `psycopg2-binary` migration driver both
  installed and functional
- **Both required migrations applied successfully** — `0001_initial_schema` and
  `0002_password_hash` applied in sequence; final head confirmed
- **All 4 required core tables exist** — `clinics`, `patients`, `consultation_sessions`,
  `audit_log` all confirmed by `db_smoke_test.py`
- **`DATABASE_URL` is wired correctly into the Railway backend service** — migration
  command resolved the DB URL without manual configuration
- **`psycopg2-binary==2.9.9` fix resolved the Module 113 migration failure** — no
  `ModuleNotFoundError` in retest

---

## 8. What This Does Not Prove

| Area | Status | Next Step |
|---|---|---|
| Staging fake clinic provisioned | NOT PROVEN | Module 115 |
| Staging fake user (`doctor.staging@praximed.test`) provisioned | NOT PROVEN | Module 115 |
| `/health/ready` returns 200 | NOT PROVEN | Module 115 (after fake user provisioned) |
| Vercel frontend deployed | NOT PROVEN | Module 116 |
| `NEXT_PUBLIC_API_BASE_URL` set to Railway URL | NOT PROVEN | Module 116 |
| CORS wired (`FRONTEND_CORS_ORIGINS` = Vercel URL) | NOT PROVEN | Module 117 |
| Browser login works | NOT PROVEN | Module 117 |
| Vapi test assistant pointed to staging | NOT PROVEN | Module 117 |
| n8n staging workflow configured | NOT PROVEN | Module 117 |
| Full staging smoke passed | NOT PROVEN | Module 118 |
| Production PHI readiness | NOT PROVEN | Production PHI launch remains NO-GO |

---

## 9. Safety Boundary

| Rule | Status |
|---|---|
| Staging uses fake/non-PHI data only | CONFIRMED — no real patient data in any staging component |
| No secrets recorded | CONFIRMED — `DATABASE_URL` value not recorded; no passwords appear in any evidence |
| No real patient data | CONFIRMED — only schema tables exist; no data rows other than what was explicitly inserted |
| No production secrets | CONFIRMED — staging credentials are staging-only; no production credentials |
| Fake/non-PHI staging only | CONFIRMED |
| Production PHI launch | **NO-GO** — fake staging clinic/user not yet provisioned; Vercel not deployed; CORS not wired |

---

## 10. Remaining Blockers

| # | Blocker | Level | Next Step |
|---|---|---|---|
| 1 | Staging fake clinic not provisioned | **HIGH** | Module 115 |
| 2 | Staging fake user not provisioned | **HIGH** | Module 115 |
| 3 | `/health/ready` not yet returning 200 | **HIGH** | Module 115 |
| 4 | Vercel frontend not deployed | **HIGH** | Module 116 |
| 5 | `NEXT_PUBLIC_API_BASE_URL` not set in Vercel | **HIGH** | Module 116 |
| 6 | `FRONTEND_CORS_ORIGINS` not set in Railway | **HIGH** | Module 117 |
| 7 | CORS preflight not verified | **HIGH** | Module 117 |
| 8 | Fake login not tested | **HIGH** | Module 117 |
| 9 | Vapi test assistant not pointed to staging URL | **HIGH** | Module 117 |
| 10 | n8n staging workflow not configured | LOW (optional for initial smoke) | Module 117 |
| 11 | Full staging smoke not executed | **HIGH** | Module 118 |

---

## 11. Recommended Next Step — Module 115

**Sprint 16 / Module 115 — Fake Staging Clinic and User Provisioning Evidence**

Now that migrations are confirmed applied and all 4 tables exist, the next step is:

1. Connect to Railway PostgreSQL (via Railway console or `psql`)
2. INSERT a fake staging clinic row (`slug='staging-fake-clinic'`; new UUID; no real data)
3. INSERT a fake staging user (`doctor.staging@praximed.test`; bcrypt hash of a
   staging-only password; not `local-dev-password`)
4. Confirm `SELECT` returns both rows
5. Confirm `GET /health/ready` → 200 with DB pool connected
6. Record clinic UUID (not a secret) and user email in evidence

Follow `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md`
Section 7 for exact SQL and evidence to capture.
