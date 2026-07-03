# Railway PostgreSQL Migration Evidence — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 15 / Module 106
**Status:** BLOCKED/PENDING — Railway PostgreSQL has not yet been provisioned

---

## 1. Purpose

This document records the actual evidence from Railway PostgreSQL provisioning and
migration execution for PraxisMed fake-data staging.

**Accuracy policy:** No evidence step is marked PASS without real proof from a real
Railway PostgreSQL service. No evidence is fabricated. If a step has not been executed
against a real service, its status is PENDING or BLOCKED.

Staging uses fake/non-PHI data only. No production DB. No real patient data.

---

## 2. Current Result

**Overall result: BLOCKED/PENDING**

Railway PostgreSQL has not yet been provisioned and migration evidence has not been
provided. This result is accurate — it is not a failure. The runbook
(`RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md`) defines all steps required
to move this document to PASS.

This document will be updated to PASS when:
1. Railway PostgreSQL add-on is created and shows "Running"
2. `DATABASE_URL` is injected into the Railway backend service
3. `python backend/scripts/run_migrations.py` exits 0
4. `python backend/scripts/db_smoke_test.py` confirms all 4 tables
5. `/health/ready` returns 200
6. Staging fake clinic and user are provisioned
7. Sanitized evidence is captured for each step above

---

## 3. Preconditions Available/Missing

| Precondition | Status | Notes |
|---|---|---|
| Railway backend service exists (Module 105) | **PENDING** | Module 105 runbook published; service not yet confirmed created |
| `/health` returns 200 on Railway backend | **PENDING** | Depends on Module 105 completion |
| Railway PostgreSQL add-on created | **MISSING** | Not yet provisioned |
| `DATABASE_URL` injected into Railway backend service | **MISSING** | Follows PostgreSQL creation |
| Railway PostgreSQL shows "Running" status | **MISSING** | Not yet provisioned |
| Backend redeployed with `DATABASE_URL` | **MISSING** | Follows injection |
| `/health/ready` returns 200 | **MISSING** | Requires DB pool connection |
| `python backend/scripts/run_migrations.py` run against staging DB | **MISSING** | Not yet executed |
| `python backend/scripts/db_smoke_test.py` run after migration | **MISSING** | Not yet executed |
| Staging fake clinic provisioned | **MISSING** | Follows migration success |
| Staging fake user (`doctor.staging@praximed.test`) provisioned | **MISSING** | Follows migration success |
| Sanitized migration evidence captured | **NOT AVAILABLE YET** | No evidence to capture |

**Repo-side readiness (no external services required):**

| Item | Status |
|---|---|
| `backend/scripts/run_migrations.py` | READY |
| `backend/scripts/db_smoke_test.py` | READY |
| `backend/migrations/versions/0001_initial_schema.py` | READY |
| `backend/migrations/versions/0002_add_password_hash_to_clinic_users.py` | READY |
| `backend/alembic.ini` | READY |
| Module 103 staging fake tenant/user provisioning strategy | READY |

---

## 4. Migration Evidence Table

| Evidence Item | Evidence Available? | Current Value | Status |
|---|---|---|---|
| Railway project name | Not available yet | — | PENDING |
| Railway backend service name | Not available yet | — | PENDING |
| Railway PostgreSQL service name | Not available yet | — | PENDING |
| Commit SHA deployed | Not available yet | — | PENDING |
| `DATABASE_URL` injection confirmed | Not available yet | — | PENDING |
| Migration command run | Not available yet | — | PENDING |
| Migration timestamp | Not available yet | — | PENDING |
| Migration exit status | Not available yet | — | PENDING |
| Sanitized migration output | Not available yet | — | PENDING |
| Final migration revision | Not available yet | Expected: `0002_password_hash (head)` | PENDING |
| DB smoke test result | Not available yet | Expected: 4 tables confirmed | PENDING |
| `/health/ready` HTTP status | Not available yet | Expected: `200` | PENDING |
| Staging fake clinic UUID | Not available yet | — | PENDING |
| Staging fake user email | Not available yet | Expected: `doctor.staging@praximed.test` | PENDING |
| No secrets in evidence (confirmed) | Not available yet | — | PENDING |

---

## 5. Blockers

The following external actions must be completed before any evidence row can be captured.
All require manual developer action.

| # | Blocker | Level |
|---|---|---|
| 1 | Railway PostgreSQL add-on not provisioned | **HIGH** |
| 2 | `DATABASE_URL` not injected into Railway backend service | **HIGH** |
| 3 | Railway PostgreSQL not yet showing "Running" status | **HIGH** |
| 4 | Migration command not yet run against staging DB | **HIGH** |
| 5 | DB smoke test not yet run | **HIGH** |
| 6 | Staging fake clinic UUID not yet generated | **HIGH** |
| 7 | Staging fake user not yet provisioned | **HIGH** |
| 8 | `/health/ready` not yet returning 200 | MEDIUM |

---

## 6. Next Evidence Needed

To update this document from BLOCKED/PENDING to PASS, the developer must:

1. Follow `RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` Sections 4–9
2. Capture each evidence item from Section 4 of that runbook
3. Update this document with real values
4. Confirm no secrets or PII appear in any recorded evidence

Once this document is updated to PASS, proceed to Module 107 (Vercel frontend project
creation).
