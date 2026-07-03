# Architecture Checkpoint 14 — Staging Deployment Review

**Date:** 2026-07-03
**Sprint:** Sprint 14 complete (Modules 100–104)
**Backend tests:** 2103/2103 passed
**Status:** Sprint 14 reviewed. Actual fake-data staging service creation: GO. Production PHI launch: NO-GO.

---

## 1. Current Status

Sprint 14 delivered the complete staging deployment preparation set. No deployment was
executed. No external Railway or Vercel services were created. No real patient data was
used. No runtime code was changed.

| Deliverable | Module | Commit | Status |
|---|---|---|---|
| Staging deployment config file inventory | 100 | 3312049 | Complete |
| Railway backend deployment prep (requirements.txt, Procfile, runtime.txt) | 101 | 8934fd7 | Complete |
| Vercel frontend deployment prep documentation | 102 | 0a88cd5 | Complete |
| Staging DB migration and seed strategy | 103 | e72fb40 | Complete |
| Staging smoke execution results (BLOCKED/PENDING — no services yet) | 104 | 8cb4c60 | Complete |

**Test suite:** 2103/2103 passed (103 new tests added across Sprint 14)

**No deployment executed.** No external services created. No real patient data used.
No production secrets. No runtime code changes. No auth refactor. Production PHI launch
remains NO-GO.

---

## 2. Sprint 14 Review

### 2.1 Module 100 — Staging Deployment Config File Inventory

A comprehensive inspection of the repo against Railway and Vercel deployment requirements.

**Key findings:**
- `backend/requirements.txt` — MISSING (BLOCKER; Railway cannot install Python packages without it)
- `Procfile` / `railway.toml` — MISSING (BLOCKER; Railway cannot determine start command)
- `runtime.txt` — MISSING (Railway Nixpacks cannot pin Python version)
- Root `.gitignore` gaps — `backend/.env`, `frontend/.env.local`, `frontend/.next/`, `frontend/node_modules/` uncovered
- Backend uses `PyJWT` (not `python-jose`) and `bcrypt` directly (not `passlib`) — both confirmed by source inspection
- `run_migrations.py` has no DB-ready retry loop — known gap documented
- `seed_local_data.py` is local-dev-only (hardcoded UUIDs; must not run in staging)
- `vercel.json` — NOT needed; `output: 'standalone'` — NOT needed; Vercel handles Next.js natively
- 12 deployment blockers inventoried

### 2.2 Module 101 — Railway Backend Deployment Prep

Created the three files Railway requires and updated `.gitignore`:

| File | Content |
|---|---|
| `backend/requirements.txt` | `fastapi==0.138.2`, `uvicorn[standard]==0.49.0`, `asyncpg==0.31.0`, `alembic==1.18.5`, `pydantic==2.13.4`, `PyJWT==2.4.0`, `bcrypt==3.2.0` |
| `runtime.txt` | `python-3.11` |
| `Procfile` | `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
| `.gitignore` additions | `backend/.env`, `frontend/.env.local`, `frontend/.next/`, `frontend/next-env.d.ts`, `frontend/node_modules/`, `frontend/package-lock.json` |

**Critical decision (user-confirmed):** Migrations are NOT in the Procfile web command.
Migration is a manual predeploy step run via Railway "Run Command":
`python backend/scripts/run_migrations.py`

### 2.3 Module 102 — Vercel Frontend Deployment Prep

Documented the complete Vercel frontend configuration strategy. No Vercel project created.

**Key confirmed settings:**
- Root directory: `frontend` (critical — without this, Vercel fails to find `package.json`)
- Framework preset: Next.js (auto-detected; no `vercel.json` needed)
- Install command: `npm install`
- Build command: `npm run build`
- Only env var: `NEXT_PUBLIC_API_BASE_URL` (public build-time var; not a secret)
- No backend secrets in Vercel frontend env — `NEXT_PUBLIC_*` are baked into the browser bundle

**CORS bootstrap dependency documented:** Railway URL → Vercel URL → set `FRONTEND_CORS_ORIGINS`
on Railway → restart → verify preflight.

**`sessionStorage` JWT caveat:** Acceptable for fake-data staging only. Not PHI-safe for
production. The SameSite cross-domain complication is documented (Railway `*.up.railway.app`
and Vercel `*.vercel.app` are different eTLD+1; cookie auth requires `SameSite=None; Secure`
for staging when httpOnly cookie auth is implemented).

### 2.4 Module 103 — Staging DB Migration and Seed Strategy

Defined the complete strategy for migrating and seeding the Railway PostgreSQL staging DB.

**Migration chain confirmed:** `0001_initial_schema` → `0002_password_hash` — two migrations;
`alembic upgrade head` runs both; expected final revision: `0002_password_hash`.

**`seed_local_data.py` must not run against staging:** Hardcoded local-dev UUIDs
(`11111111-...`, `22222222-...`); uses `local-dev-password` hash; local-only email
(`doctor.local@praximed.test`). Running it in staging would contaminate staging with
local-dev assumptions.

**Staging fake tenant/user spec:**
- Staging clinic: `slug=staging-fake-clinic`, `name=Staging Fake Clinic`, UUID freshly generated
- Staging user: `doctor.staging@praximed.test`, `full_name=Dr. Staging Test`, bcrypt hash of a staging-only password
- Provisioning method: Option A (manual SQL via Railway "Run Command" — recommended for first smoke)

**DB-ready retry gap:** `run_migrations.py` has no retry loop. Manual timing required:
wait for Railway PostgreSQL to show "Running" status before executing migration command.

### 2.5 Module 104 — Staging Smoke Execution Results (BLOCKED/PENDING)

Staging smoke cannot be executed because no external staging services exist.
The result is accurately recorded as `BLOCKED/PENDING` — this is not a failure.

**All repo-side items are READY.** All 15 external blockers are documented. A 19-step
smoke checklist and 18-step ordered provisioning sequence are defined and ready to
execute once services are created.

**No smoke evidence was fabricated.** The document explicitly enforces an accuracy policy:
no step is marked PASS without real evidence from a real service.

---

## 3. Repo-Side Readiness

As of Sprint 14 completion, the repository is fully prepared for staging deployment.
No further runtime code changes are required before the first Railway service creation.

| Item | Status | Source |
|---|---|---|
| `backend/requirements.txt` — 7 pinned runtime deps | READY | Module 101 |
| `Procfile` — `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | READY | Module 101 |
| `runtime.txt` — `python-3.11` | READY | Module 101 |
| `.gitignore` — all build artifacts and local secrets covered | READY | Module 101 |
| `backend/scripts/run_migrations.py` — reads `DATABASE_URL`; runs `alembic upgrade head`; exits non-zero on failure | READY | Module 45 |
| `backend/scripts/db_smoke_test.py` — verifies 4 core tables post-migration | READY | Module 45 |
| `backend/migrations/versions/0001_initial_schema.py` — 11-table schema | READY | Module 45 |
| `backend/migrations/versions/0002_add_password_hash_to_clinic_users.py` | READY | Module 59 |
| `backend/alembic.ini` — `script_location = backend/migrations/` | READY | Module 45 |
| Frontend `npm run build` — passes locally; no `output:standalone`; no `vercel.json` | READY | Verified Module 77/102 |
| `frontend/lib/api.ts` — reads `NEXT_PUBLIC_API_BASE_URL`; Bearer token injection | READY | Verified Module 102 |
| `frontend/lib/auth.ts` — `sessionStorage` JWT; labeled local-dev-only; acceptable for fake-data staging | READY | Verified Module 102 |
| Auth route `POST /auth/login` | READY | Module 59/60 |
| Appointment PATCH route `PATCH /appointment-requests/{id}/status` | READY | Module 17 |
| Vapi tool route `POST /vapi/tools/capture-appointment-request` | READY | Module 18 |
| CORS implementation — `_cors_origins()` never returns `*`; reads `FRONTEND_CORS_ORIGINS` | READY | Prior sprints |
| All backend tests — 2103/2103 passed | READY | Module 104 |
| `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` — step-by-step pre-deploy checklist | READY | Module 97 |
| `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` — smoke verification steps and failure triage | READY | Module 94 |
| `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` — per-variable spec for all components | READY | Module 96 |
| `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` | READY | Module 101 |
| `docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md` | READY | Module 102 |
| `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md` | READY | Module 103 |
| `docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md` — smoke checklist template and blocker list | READY | Module 104 |

---

## 4. External Blockers Remaining

The following require manual developer action outside this Claude Code session. No
code change in this repository unblocks them — they require creating external services.

| # | Blocker | Unblocked By |
|---|---|---|
| 1 | Railway backend service not created | Developer: create Railway project; link GitHub repo |
| 2 | Railway PostgreSQL add-on not provisioned | Developer: add Railway PostgreSQL plugin to service |
| 3 | Vercel frontend project not created | Developer: create Vercel project; root = `frontend` |
| 4 | Staging API HTTPS URL unknown | Assigned by Railway after service creation |
| 5 | Staging frontend HTTPS URL unknown | Assigned by Vercel after first deployment |
| 6 | `JWT_SECRET_KEY` not set in Railway dashboard | Developer: `openssl rand -hex 32` → Railway env |
| 7 | `VAPI_WEBHOOK_SECRET` not set in Railway dashboard | Developer: `openssl rand -hex 32` → Railway env |
| 8 | `N8N_WEBHOOK_SECRET` not set in Railway dashboard | Developer: `openssl rand -hex 32` → Railway env |
| 9 | `INTERNAL_WEBHOOK_SECRET` not set in Railway dashboard | Developer: `openssl rand -hex 32` → Railway env |
| 10 | `FRONTEND_CORS_ORIGINS` not set (requires Vercel URL — step 5) | Set after Vercel URL known |
| 11 | `NEXT_PUBLIC_API_BASE_URL` not set in Vercel (requires Railway URL — step 4) | Set after Railway URL known |
| 12 | Staging fake clinic UUID not generated; clinic row not provisioned | Developer: `python -c "import uuid; print(uuid.uuid4())"` then SQL insert |
| 13 | Staging fake user (`doctor.staging@praximed.test`) not provisioned | Developer: bcrypt hash + SQL insert |
| 14 | Migrations not run against staging DB | Developer: Railway "Run Command" → `python backend/scripts/run_migrations.py` |
| 15 | Vapi test assistant not pointed to staging API URL | Developer: update Vapi assistant tool URL and `X-Clinic-Ref` header |
| 16 | n8n staging workflow not configured | Deferred; NOT ENABLED for first smoke |
| 17 | Staging smoke evidence not captured | Follows completion of blockers 1–15 |
| 18 | Rollback path not tested | Follows first successful deploy |

---

## 5. Decision

| Decision | Outcome | Rationale |
|---|---|---|
| **Actual fake-data staging service creation** | **GO** | Repo is fully ready. All deployment prep docs complete. Dry-run checklist ready. Module 104 BLOCKED/PENDING accurately documents what needs to happen. No further planning modules are needed before service creation. |
| **Production PHI launch** | **NO-GO** | All 12 production blockers from Architecture Checkpoint 12 remain open. Staging smoke not yet executed. Auth/session hardening not yet implemented. Legal/GDPR review not completed. |
| **Auth/session hardening (httpOnly cookie)** | **After staging smoke evidence** | Module 98 contains the full implementation plan. Implementation begins after M1 (staging deploy) + M2 (staging smoke) evidence confirms the staging environment is stable. SameSite=None; Secure required for Railway+Vercel cross-domain staging. |
| **Fabel 5 / frontend UX sprint** | **Deferred** | Wait until staging topology confirmed and auth hardened. |
| **Appointment workflow expansion** | **Deferred** | Deferred per all prior checkpoints. |

---

## 6. Safety Constraints for Next Sprint

All of the following must hold throughout Sprint 15 (actual staging service creation):

| Constraint | Detail |
|---|---|
| Fake/non-PHI data only | No real patient names, phone numbers, DOBs, or medical records |
| Isolated staging secrets | New high-entropy secrets per `openssl rand -hex 32`; never reuse local-dev placeholders or production secrets |
| Isolated staging DB | Railway PostgreSQL is a separate service; not connected to any future production DB |
| No local-dev password in staging | Hash of `local-dev-password` must not appear in staging `clinic_users.password_hash` |
| No production secrets | Production secrets do not exist yet; when created, they must be distinct from staging |
| No production DB | `DATABASE_URL` on staging must never point to a production database |
| No real patients | Staging `appointment_requests` and `patients` rows must be synthetic |
| No ngrok in staging | Vapi test assistant and `FRONTEND_CORS_ORIGINS` must use Railway/Vercel HTTPS URLs only |
| No wildcard CORS | `FRONTEND_CORS_ORIGINS` must be the exact Vercel staging URL; `_cors_origins()` never returns `*` |
| HTTPS staging URLs only | Both Railway and Vercel provide HTTPS by default on their subdomains |
| Vapi test assistant only | No production Vapi assistant used in staging |
| No auto-confirmation | `appointment_requests.status` must be `'new'` and `action_required=True` on creation; stop rule if auto-confirmed |
| Staff Confirm required | `PATCH /appointment-requests/{id}/status` requires valid JWT and explicit human action |

---

## 7. Recommended Sprint 15 Sequence

Sprint 15 converts the staging prep documentation into actual service creation and smoke
execution evidence. Each module is a concrete execution step with evidence capture.

| Module | Title | Scope |
|---|---|---|
| **105** | Railway Backend Service Creation Runbook | Step-by-step Railway service creation guide: exact UI/CLI steps, env vars, start command (`web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`), health check path, evidence checklist. No code changes. |
| **106** | Railway PostgreSQL Provisioning and Migration Evidence | Step-by-step Railway PostgreSQL provisioning: add Plugin, `DATABASE_URL` injection, migration run command, `db_smoke_test.py` verification, staging fake clinic/user SQL provisioning. Evidence template. |
| **107** | Vercel Frontend Project Creation Runbook | Step-by-step Vercel project creation: root directory = `frontend`, framework = Next.js auto-detect, env var `NEXT_PUBLIC_API_BASE_URL`, first deploy, Vercel URL capture, `FRONTEND_CORS_ORIGINS` update on Railway. Evidence template. |
| **108** | Staging Environment Wiring Evidence | Verify CORS preflight works; confirm all env vars are set and correct; verify no wildcard CORS; verify HTTPS; evidence capture. |
| **109** | Staging Smoke Execution PASS/BLOCKED Evidence | Execute smoke checklist from `STAGING_SMOKE_EXECUTION_RESULTS.md`; record actual PASS or BLOCKED evidence per step; update Module 104 doc with real results. |
| **Checkpoint 15** | Staging Deployment Evidence Review | Review Module 104 PASS/BLOCKED status; decide auth hardening timing; assess production readiness progress. |

**Module 105 is the immediate next step.** It does not execute any Railway commands
itself — it creates a human-executable runbook so the developer has exact steps to
follow when creating the service. The runbook should be accurate and complete enough
that Module 104 can be updated to PASS once the developer follows it.

---

## 8. Recommended Next Module

**Sprint 15 / Module 105 — Railway Backend Service Creation Runbook**

The repo is ready. The immediate next blocker is the Railway backend service creation.
Module 105 should:
- Provide the exact Railway UI/CLI steps for creating the backend service
- Specify required settings: service root (repo root), start command (from Procfile), Python runtime, health check path (`/health`)
- Specify required env vars with generation commands (`openssl rand -hex 32` for all secrets)
- Define evidence to capture: Railway service URL, deploy log screenshot, `/health` curl result
- Not execute any Railway commands or claim any service was created
- Not require any code changes — the Procfile, runtime.txt, and requirements.txt are all ready

---

## 9. Final Go/No-Go Table

| Item | Decision | Rationale |
|---|---|---|
| **Repo-side staging prep** | **GO** | All deployment prep files, docs, and test suite in place; no further repo changes required before service creation |
| **Railway backend service creation** | **GO** | Procfile, runtime.txt, requirements.txt ready; env var spec documented; health route exists; migration command ready |
| **Railway PostgreSQL creation** | **GO** | Migration files and runner ready; seed strategy defined; provisioning SQL template defined |
| **Vercel frontend creation** | **GO** | Next.js 14.2.3 auto-detected; root directory documented; `NEXT_PUBLIC_API_BASE_URL` spec ready; no vercel.json needed |
| **Staging smoke pass** | **PENDING** | Requires external service creation; smoke checklist ready; will be re-evaluated in Module 109 |
| **Production PHI launch** | **NO-GO** | 12 production blockers open; staging smoke not yet executed; auth hardening not yet implemented; Legal/GDPR review not completed |
| **Auth/session hardening** | **GO — after staging smoke** | Module 98 plan complete; implement after M1/M2 staging evidence; SameSite=None required for Railway+Vercel cross-domain staging |
| **Fabel 5 / UX sprint** | **DEFERRED** | Wait until staging confirmed and auth hardened |

---

## 10. Non-Goals

- No deployment execution in this checkpoint
- No Railway or Vercel service creation
- No production launch or production PHI
- No auth/session hardening implementation (deferred to Sprint 15 post-smoke)
- No Fabel 5 / frontend UX sprint
- No appointment workflow expansion
- No real secrets in any file created by this checkpoint
- No runtime code changes
