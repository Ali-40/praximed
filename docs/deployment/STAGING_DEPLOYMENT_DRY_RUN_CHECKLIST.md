# Staging Deployment Dry-Run Checklist — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 13 / Module 97
**Status:** Planning only — no deployment executed in this module; no runtime code changed

---

## 1. Purpose

This document is the pre-deployment dry-run checklist for the PraxisMed staging
environment. It covers every step that must be verified before and during the first
real staging deployment attempt.

**What this document is:**
- A step-by-step dry-run checklist for Railway backend, Railway PostgreSQL, Vercel
  frontend, Vapi test assistant, and n8n staging workflow
- The direct input for executing the staging deployment (a future module)
- A failure stop reference: conditions that must halt deployment immediately

**What this document is not:**
- A deployment execution record — no deployment is run in this module
- A production launch plan — production PHI launch remains NO-GO per Architecture
  Checkpoint 12
- An auth/session hardening plan — that is Module 98
- A Fabel 5 / frontend UX sprint plan
- A document that contains real secrets

**Staging constraint:** fake/non-PHI data only. No real clinic staff, no real patients,
no real Vapi production assistant, no production database connection.

---

## 2. Preconditions

All items below must be true before any staging deployment attempt begins.

### 2.1 Codebase Readiness

- [ ] `git status` shows clean working tree on the deploy branch (no uncommitted changes)
- [ ] All backend tests pass: `pytest backend/tests/` — minimum 1832 tests
- [ ] `npm run build` passes locally in the `frontend/` directory with no errors
- [ ] No real secrets committed to any file in the repository
- [ ] `.gitignore` includes `backend/.env`, `frontend/.env.local`, `frontend/node_modules/`, `frontend/.next/`
- [ ] Deployment branch / tag strategy decided (e.g., deploy from `master` or a dedicated `staging` branch)

### 2.2 Account and Platform Readiness

- [ ] Railway account created and workspace available
- [ ] Vercel account created and connected to the same GitHub account or organization
- [ ] GitHub repository accessible from both Railway and Vercel for auto-deploy on push
- [ ] Vapi account accessible; test assistant can be edited
- [ ] n8n instance accessible (or n8n staging is marked NOT ENABLED for this deployment)

### 2.3 Data and Security

- [ ] No real patient data will be used in any staging test
- [ ] No production secrets are available to the staging deployment (production secrets
  do not exist yet; confirm this holds when production secrets are eventually created)
- [ ] Local-dev placeholder secrets (`local-dev-jwt-secret-key-change-in-production`,
  `local-vapi-secret-change-me`, etc.) will NOT be used in any staging env var
- [ ] `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` reviewed and understood
- [ ] `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` reviewed
- [ ] Rollback owner identified: who is responsible for reverting the deploy if needed

### 2.4 Staging Domain Placeholders

- [ ] Staging backend URL placeholder confirmed: `https://staging-api.up.railway.app`
  (Railway auto-provisioned; actual subdomain assigned by Railway at service creation)
- [ ] Staging frontend URL placeholder confirmed: `https://staging-app.vercel.app`
  (Vercel auto-provisioned; actual subdomain assigned by Vercel at project creation)
- [ ] Both URLs are distinct from `http://127.0.0.1:8000` and `http://localhost:3000`
- [ ] No custom domain is required for staging (auto-provisioned subdomains are sufficient)

---

## 3. Target Staging Topology

Confirmed from Module 95 (Staging Deployment Topology Plan):

| Component | Platform | Notes |
|---|---|---|
| **Backend API** | Railway (Python / FastAPI / uvicorn) | Listens on `$PORT`; auto-assigned by Railway |
| **PostgreSQL** | Railway managed PostgreSQL add-on | `DATABASE_URL` auto-injected; not a separate cloud DB |
| **Frontend** | Vercel (Next.js 14 static build + Edge) | `NEXT_PUBLIC_API_BASE_URL` set to Railway backend URL |
| **Vapi test assistant** | Vapi dashboard | Server URL updated to Railway HTTPS URL |
| **n8n staging workflow** | External n8n instance (or NOT ENABLED) | Webhook URL updated to Railway HTTPS URL |
| **Staging HTTPS API URL** | `https://staging-api.up.railway.app` | Stable; replaces ngrok entirely |
| **Staging frontend origin** | `https://staging-app.vercel.app` | Exact origin for `FRONTEND_CORS_ORIGINS` |
| **ngrok** | **Not used in staging** | Railway URL is stable; no tunnel needed |
| **Wildcard CORS** | **Never used** | `_cors_origins()` in `main.py` never returns `*` |

---

## 4. Repository Readiness Checklist

- [ ] **Backend entrypoint identified:** `backend/app/main.py`; invoked as
  `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- [ ] **Frontend root identified:** `frontend/` directory; `package.json` at `frontend/package.json`
- [ ] **Migration command identified:** `python backend/scripts/run_migrations.py`
  (reads `DATABASE_URL` from env; reads `backend/alembic.ini`; exits non-zero on failure)
- [ ] **Test command identified:** `pytest backend/tests/` from project root
- [ ] **Frontend build command confirmed:** `cd frontend && npm run build`
- [ ] **Frontend start command confirmed:** `cd frontend && npm start` (`next start`)
- [ ] **Seed strategy confirmed:** Do NOT run `backend/scripts/seed_local_data.py` in staging;
  staging clinic and staff user will be provisioned via a one-time SQL insert or staging-only script
- [ ] **`.env.example` files present:** `backend/.env.example` and `frontend/.env.example`
  document all variable names; neither contains real secrets
- [ ] **No real secrets committed:** `git grep -i "secret\|password\|token" backend/.env.example`
  returns only placeholder values; no real keys present

---

## 5. Railway Backend Dry-Run Checklist

**Planning only — these steps are the checklist for execution, not execution itself.**

### 5.1 Service Creation

- [ ] Create a new Railway project named `praximed-staging` (or equivalent)
- [ ] Add a new Railway service: `praximed-backend` (or equivalent)
- [ ] Connect the service to the GitHub repository; set the deploy branch
- [ ] Confirm Railway detects Python (or set the build command manually)
- [ ] Confirm the source root is the project root (not `backend/` alone — the backend
  imports `backend.app.main` as a Python package from the project root)

### 5.2 Start Command

Set the Railway service start command to:
```
python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

- [ ] Migration gate confirmed: `run_migrations.py` exits non-zero on failure; `&&` prevents uvicorn from starting if migrations fail
- [ ] `$PORT` used (not a hardcoded port); Railway injects `$PORT` automatically
- [ ] `--host 0.0.0.0` used (not `127.0.0.1`); required for Railway to route external traffic

### 5.3 Railway Backend Environment Variables

Set in Railway dashboard → Service → Variables. All are staging-specific values:

- [ ] `DATABASE_URL` — auto-injected by Railway PostgreSQL add-on (verify after add-on is attached; do not set manually)
- [ ] `JWT_SECRET_KEY` — high-entropy staging value; not the local placeholder; generated via `openssl rand -hex 32`
- [ ] `VAPI_WEBHOOK_SECRET` — high-entropy staging value; must match Vapi staging assistant signing secret
- [ ] `N8N_WEBHOOK_SECRET` — high-entropy staging value; must match n8n staging workflow HMAC secret
- [ ] `INTERNAL_WEBHOOK_SECRET` — high-entropy staging value; no external dependency
- [ ] `FRONTEND_CORS_ORIGINS` — set to exact Vercel staging frontend origin (e.g., `https://staging-app.vercel.app`); no wildcard; no trailing slash; no localhost

Optional:
- [ ] `APP_ENV=staging` — informational; not consumed by app logic

### 5.4 Health Route Verification

After deploy, verify:
- [ ] `GET https://staging-api.up.railway.app/health` → `{"status": "ok", "service": "PraxisMed API"}`
- [ ] `GET https://staging-api.up.railway.app/health/ready` → `{"status": "ready", "checks": {"app": "ok"}}`

If `/health/ready` returns `503`: `DATABASE_URL` is not set or pool failed. Check Railway logs.

### 5.5 Log Safety Check

- [ ] Verify Railway log stream does not contain raw `JWT_SECRET_KEY` value
- [ ] Verify Railway log stream does not contain raw `DATABASE_URL` value (contains password)
- [ ] Verify Railway log stream does not contain raw `Authorization: Bearer <token>` header values
- [ ] Verify Railway log stream does not contain raw patient names, phone numbers, or transcript text

### 5.6 Backend Rollback

- [ ] Previous Railway deployment identified in Railway dashboard
- [ ] Rollback method confirmed: Railway dashboard → Deployments → re-deploy previous build
- [ ] Rollback does not require a code change or git revert

---

## 6. Railway PostgreSQL Dry-Run Checklist

### 6.1 Provisioning

- [ ] Add PostgreSQL add-on to the `praximed-staging` Railway project
- [ ] Railway auto-creates a managed PostgreSQL 16 instance
- [ ] Confirm `DATABASE_URL` appears automatically in the `praximed-backend` service variables
  (Railway injects it; do not copy-paste the connection string manually)
- [ ] Note: `DATABASE_URL` uses Railway's internal private URL (`.railway.internal` suffix);
  a separate public URL may be available for one-off access (e.g., running migrations from local)

### 6.2 Isolation Confirmation

- [ ] This DB is isolated from local Docker PostgreSQL (port 5433)
- [ ] This DB is isolated from any future production database
- [ ] `DATABASE_URL` in the staging service does NOT point to a production database
- [ ] Local `docker-compose.postgres.yml` is not used in staging; it is a local-only file

### 6.3 Backup and Data Expectations

- [ ] Railway PostgreSQL provides basic snapshotting; data loss in staging is acceptable
- [ ] No production-grade PITR (point-in-time recovery) required for staging
- [ ] If staging DB data is lost: re-run migrations, re-provision staging fake clinic/user

### 6.4 Migration Execution

- [ ] Migration runs automatically as part of the Railway start command
- [ ] Railway deploy logs confirm `alembic upgrade head` exit code 0
- [ ] If migration fails: Railway marks the deploy as failed; traffic is NOT routed to the new build
- [ ] Verify Alembic migration status: staging DB tables exist (`clinic_users`, `patients`,
  `consultations`, `appointment_requests`, `audit_logs`, `clinic_call_logs`, etc.)

### 6.5 Staging Seed Strategy

- [ ] Do NOT run `backend/scripts/seed_local_data.py` against the staging DB (it uses local
  deterministic UUIDs `11111111-...` not suitable for staging)
- [ ] Staging fake clinic UUID chosen: a new UUID distinct from `11111111-1111-1111-1111-111111111111`
- [ ] Staging fake clinic UUID placeholder: `<staging-fake-clinic-uuid>`
- [ ] Staging staff user created via one-time SQL insert or staging seed script:
  - fake name (not a real person)
  - fake email (not a real address)
  - bcrypt-hashed password (staging-only credential)
  - clinic_id matches `<staging-fake-clinic-uuid>`
- [ ] No real patient records, no real names, no real phone numbers in staging DB

### 6.6 PostgreSQL Rollback

- [ ] For staging: rollback = re-run migrations on a restored snapshot or re-provision
- [ ] No migration rollback automation is required for staging at this scale

---

## 7. Vercel Frontend Dry-Run Checklist

### 7.1 Project Creation

- [ ] Create a new Vercel project linked to the GitHub repository
- [ ] Set the project root to `frontend/` (the Next.js app lives in `frontend/`, not the repo root)
- [ ] Vercel should auto-detect Next.js framework
- [ ] Build command: `npm run build` (confirmed in `frontend/package.json`)
- [ ] Output directory: `.next` (Next.js default; Vercel detects automatically)
- [ ] Install command: `npm install`

### 7.2 Vercel Environment Variables

Set in Vercel project → Settings → Environment Variables:

- [ ] `NEXT_PUBLIC_API_BASE_URL` = `https://staging-api.up.railway.app`
  - Public build-time variable; baked into the browser bundle at build time
  - Not a secret; exposed to browser
  - Must not be `http://127.0.0.1:8000` (the local fallback in `frontend/lib/api.ts`)
  - Must match the Railway backend URL exactly (no trailing slash)

Do NOT set in Vercel:
- [ ] No `DATABASE_URL` — this is a backend secret; must never reach the frontend
- [ ] No `JWT_SECRET_KEY` — backend secret
- [ ] No webhook secrets — backend secrets

### 7.3 Build Verification

- [ ] `npm run build` completes without TypeScript errors or Next.js build errors
- [ ] No `NEXT_PUBLIC_API_BASE_URL` warning: if the value is not set at build time, the
  local fallback (`http://127.0.0.1:8000`) is embedded — all API calls will fail in Vercel
- [ ] Vercel function logs available after deploy

### 7.4 Frontend Routes

- [ ] `/login` page loads (HTTP 200) — the login form is visible
- [ ] `/` redirects to `/login` (via `frontend/app/page.tsx`)
- [ ] `/dashboard` before login redirects to `/login` (client-side auth guard)
- [ ] `/dashboard` after login renders all four sections: Appointments, Patients,
  Notifications, Consultations

### 7.5 Vercel Rollback

- [ ] Previous Vercel deployment identified in Vercel dashboard
- [ ] Rollback method: Vercel dashboard → Deployments → Promote previous deployment
- [ ] Rollback does not require a code change or git revert
- [ ] After `NEXT_PUBLIC_API_BASE_URL` change: must trigger a new build (it is a build-time
  variable; the old build still has the old value baked in)

---

## 8. Domain and CORS Dry-Run Checklist

### 8.1 Staging URL Confirmation

- [ ] Staging backend URL: `https://staging-api.up.railway.app` (stable Railway subdomain; no ngrok)
- [ ] Staging frontend URL: `https://staging-app.vercel.app` (stable Vercel subdomain)
- [ ] Both URLs use HTTPS — HTTP is not accepted in staging
- [ ] Neither URL is localhost or `127.0.0.1`

### 8.2 CORS Variable Alignment

- [ ] `FRONTEND_CORS_ORIGINS` in Railway = exact staging frontend origin (e.g., `https://staging-app.vercel.app`)
- [ ] `NEXT_PUBLIC_API_BASE_URL` in Vercel = exact staging backend URL (e.g., `https://staging-api.up.railway.app`)
- [ ] No wildcard (`*`) in `FRONTEND_CORS_ORIGINS` — `_cors_origins()` in `main.py` never returns a wildcard
- [ ] No ngrok URL in any env var — Railway URL is stable and replaces ngrok entirely

### 8.3 Expected Browser Preflight

When the staging frontend makes an API request, the browser sends an OPTIONS preflight:
```
OPTIONS https://staging-api.up.railway.app/auth/login
Origin: https://staging-app.vercel.app
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
```

Expected Railway backend response:
```
Access-Control-Allow-Origin: https://staging-app.vercel.app
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS, PUT
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

- [ ] `Access-Control-Allow-Origin` matches staging frontend URL exactly
- [ ] `Authorization` header is in `Access-Control-Allow-Headers` (required for JWT Bearer)
- [ ] `Access-Control-Allow-Credentials: true` (required for credentials: "same-origin" fetch)

### 8.4 Machine Auth Not Affected by CORS

Vapi and n8n send requests server-to-server directly to the Railway API. They do not
go through the browser. Machine auth headers (`X-Vapi-*`, `X-N8N-*`) are not browser
CORS headers and do not need to appear in `allow_headers`.

- [ ] Confirmed: `FRONTEND_CORS_ORIGINS` does not affect Vapi or n8n requests
- [ ] Confirmed: Vapi/n8n requests will not encounter CORS errors

---

## 9. Staging Env Var Dry-Run Checklist

For each variable, confirm the following before triggering the first staging deploy.

| Variable | Platform | Secret? | Checklist |
|---|---|---|---|
| `DATABASE_URL` | Railway (auto) | Yes | [ ] Auto-injected by PostgreSQL add-on; visible in Railway variables; NOT set manually |
| `JWT_SECRET_KEY` | Railway | Yes | [ ] High-entropy value set; not the local placeholder; verified present in Railway variables |
| `VAPI_WEBHOOK_SECRET` | Railway | Yes | [ ] Unique staging value; matches Vapi assistant signing secret; not local placeholder |
| `N8N_WEBHOOK_SECRET` | Railway | Yes | [ ] Unique staging value; matches n8n workflow HMAC secret; not local placeholder |
| `INTERNAL_WEBHOOK_SECRET` | Railway | Yes | [ ] Unique staging value; no external dependency |
| `FRONTEND_CORS_ORIGINS` | Railway | No | [ ] Exact Vercel staging origin; no wildcard; no trailing slash |
| `NEXT_PUBLIC_API_BASE_URL` | Vercel | No | [ ] Exact Railway backend URL; no trailing slash; set before build |
| `POSTGRES_DB/USER/PASSWORD` | Railway (auto-managed) | PASSWORD: Yes | [ ] Not set manually; Railway manages these within `DATABASE_URL` |
| `APP_ENV` | Railway (optional) | No | [ ] Set to `staging` if desired; no failure if absent |

**For every secret above, also confirm:**
- [ ] Not the local-dev placeholder value
- [ ] Not a production secret value (production secrets do not exist yet)
- [ ] Not visible in git history, docs, screenshots, or Slack messages
- [ ] Not logged by the backend application

---

## 10. Migration Dry-Run Checklist

### 10.1 Pre-Migration

- [ ] `DATABASE_URL` in Railway points to the staging PostgreSQL (auto-injected; verified
  in Railway service variables)
- [ ] `DATABASE_URL` does NOT point to local Docker PostgreSQL (`localhost:5433`)
- [ ] `DATABASE_URL` does NOT point to any production database
- [ ] Snapshot/backup taken if staging DB has any data (acceptable to skip on first deploy)

### 10.2 Migration Execution (via Start Command)

The Railway start command runs migrations automatically:
```
python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

- [ ] `run_migrations.py` reads `DATABASE_URL` from the environment (set by Railway)
- [ ] `run_migrations.py` reads `backend/alembic.ini` (relative path from project root)
- [ ] `alembic upgrade head` applies all pending migrations in order
- [ ] If exit code is 0: migrations succeeded; uvicorn starts
- [ ] If exit code is non-zero: migration failed; `&&` short-circuits; uvicorn does NOT start;
  Railway marks the deploy as failed; no traffic is routed to the failed deploy

### 10.3 Migration Success Verification

In Railway deploy logs, look for:
- `Running: alembic -c backend/alembic.ini upgrade head`
- No ERROR lines from `run_migrations.py`
- Alembic output: `Running upgrade ... -> ...` followed by successful migration IDs
- uvicorn startup: `Application startup complete` or similar

### 10.4 Migration Failure Triage

| Symptom | Likely Cause | Safe Check |
|---|---|---|
| `ERROR: DATABASE_URL environment variable is not set` | `DATABASE_URL` not injected | Verify PostgreSQL add-on is attached to the service |
| `ERROR: alembic.ini not found` | Source root is wrong | Confirm Railway deploys from project root, not `backend/` subdirectory |
| `alembic.util.exc.CommandError: Can't locate revision` | Corrupt migration history | Check Railway logs; may need to reset Alembic version table |
| `asyncpg.exceptions.PostgresConnectionError` | Wrong `DATABASE_URL` | Verify host/port in DATABASE_URL |

### 10.5 Migration Rollback

Staging: acceptable to drop and recreate the DB. No migration rollback automation needed.

---

## 11. Auth and Dashboard Dry-Run Checklist

### 11.1 Staging Credentials

- [ ] Staging staff user provisioned in staging DB (fake name, fake email, bcrypt password)
- [ ] Staging login credential known to the tester (fake email + staging-only password)
- [ ] No real clinic staff credentials used in staging

### 11.2 Login Flow

- [ ] `POST https://staging-api.up.railway.app/auth/login` with staging credentials →
  returns `{"access_token": "<jwt>"}` (HTTP 200)
- [ ] Token is stored in `sessionStorage` (`praximed_access_token` key) — expected behavior
  in staging; PHI-incompatible for production
- [ ] Failed login returns generic error (no email/password distinction revealed)

### 11.3 Dashboard

- [ ] `GET https://staging-app.vercel.app/dashboard` without token → redirects to `/login`
- [ ] `GET https://staging-app.vercel.app/dashboard` after login → dashboard renders
  (empty sections expected before any Vapi calls)
- [ ] All four sections visible: Appointments, Patients, Notifications, Consultations
- [ ] No CORS error in browser devtools on any API call

### 11.4 Session Risk Acknowledgment

The staging environment uses `sessionStorage` JWT (stored in `frontend/lib/auth.ts`).
This is:
- **Acceptable for fake-data staging** — no PHI present; no real patients
- **Not acceptable for production PHI** — XSS-accessible; explicitly labeled
  `local-dev only` in `auth.ts`; production PHI requires httpOnly cookie (Module 98)

- [ ] Confirmed: staging login uses `sessionStorage` (expected; not a staging blocker)
- [ ] Confirmed: no real patient data accessed via the staging dashboard

### 11.5 Logout

- [ ] Logout button clears `sessionStorage` and redirects to `/login`
- [ ] After logout, navigating to `/dashboard` redirects to `/login`

---

## 12. Vapi Staging Dry-Run Checklist

### 12.1 Vapi Test Assistant Configuration

- [ ] Using Vapi **test assistant** — not a production assistant
- [ ] Server URL updated in Vapi dashboard to:
  `https://staging-api.up.railway.app/vapi/tools/capture-appointment-request`
- [ ] No ngrok URL in the Vapi test assistant server URL
- [ ] HTTP headers configured in Vapi dashboard:
  - `X-Vapi-Service-Name: vapi`
  - `X-Vapi-Clinic-Id: <staging-fake-clinic-uuid>` (must match the clinic UUID in staging DB)
  - `X-Vapi-Scopes: vapi:tool` (**singular** — `vapi:tools` plural is rejected with HTTP 403)
- [ ] Webhook signing secret in Vapi dashboard matches `VAPI_WEBHOOK_SECRET` in Railway

### 12.2 Vapi Fake Test Call

- [ ] Trigger a fake Vapi test call (fake patient name; no real phone number; no real patient)
- [ ] Vapi POSTs to Railway backend; Railway logs show the incoming request
- [ ] Expected HTTP 200 response from Railway backend
- [ ] Appointment row created in staging DB:
  - `status = new`
  - `source = vapi`
  - `action_required = True`
  - `clinic_id = <staging-fake-clinic-uuid>`

### 12.3 No Auto-Confirmation

- [ ] Appointment row has `status = new` immediately after creation — no auto-confirmation
- [ ] No code path in the backend sets `status = confirmed` without an explicit staff action
- [ ] Staff Confirm requires a human to click the Confirm button in the dashboard

### 12.4 Dashboard Confirmation

- [ ] After Vapi test call, staging dashboard shows the new row with `status = new`
- [ ] Staff clicks Confirm →
  `PATCH https://staging-api.up.railway.app/appointment-requests/{id}/status`
  with Bearer JWT
- [ ] Row transitions to `status = confirmed`; Confirm button disappears
- [ ] No calendar booking triggered

### 12.5 Log Safety

- [ ] Railway logs do not show raw patient name or phone number from the Vapi call body
- [ ] Railway logs show `call_id` and `clinic_id` (permitted) but not PHI fields

---

## 13. n8n Staging Dry-Run Checklist

### 13.1 n8n Status for Staging

n8n is **optional** for the initial staging deployment. If n8n is not yet configured
for staging, mark this section **NOT ENABLED** and defer to a later module.

### 13.2 n8n Staging Configuration (if enabled)

- [ ] Using staging n8n workflow — isolated from local and any production workflow
- [ ] Webhook URL updated in n8n workflow HTTP request node to:
  `https://staging-api.up.railway.app/webhooks/n8n/calendar-sync`
- [ ] Machine auth headers set in n8n:
  - `X-Service-Name: n8n`
  - `X-Service-Clinic-Id: <staging-fake-clinic-uuid>`
  - `X-Service-Scopes: calendar:sync`
- [ ] HMAC signing secret in n8n matches `N8N_WEBHOOK_SECRET` in Railway
- [ ] Signed header: `X-N8N-Signature: sha256=<hmac>` (accepted aliases: `X-N8n-Signature`, `X-Signature`)
- [ ] Test/fake calendar configured — no production calendar writes

### 13.3 n8n Fake Signed Request

- [ ] Trigger a fake n8n workflow firing to the staging webhook URL
- [ ] Backend returns HTTP 200 (correct HMAC)
- [ ] Backend returns HTTP 401 when sent with a wrong signature (negative test)
- [ ] Railway logs confirm request received; no patient PHI in logs

### 13.4 No Browser CORS Dependency

- [ ] n8n sends requests server-to-server; no browser involved
- [ ] CORS preflight does not apply to n8n requests

---

## 14. Smoke Execution Order

Execute smoke checks in this exact order after the initial staging deploy.

| Step | Action | Expected Result | Stop if |
|---|---|---|---|
| 1 | `GET /health` on Railway backend | `{"status": "ok", "service": "PraxisMed API"}` | Any non-200 response |
| 2 | `GET /health/ready` on Railway backend | `{"status": "ready", "checks": {"app": "ok"}}` | `503` → DB pool failed; check `DATABASE_URL` |
| 3 | Confirm migration logs | Alembic upgrade exit code 0; all tables created | Non-zero exit or missing tables |
| 4 | Open `https://staging-app.vercel.app/login` in browser | Login form visible; no console errors | Blank page; CORS error; JS error |
| 5 | Verify browser Network: OPTIONS preflight | `Access-Control-Allow-Origin` matches Vercel staging URL | Wildcard; missing header; wrong origin |
| 6 | Login with staging credentials | Redirected to `/dashboard`; token in `sessionStorage` | HTTP 401 → check `JWT_SECRET_KEY`; HTTP 500 → missing secret |
| 7 | Dashboard renders | Four sections visible (may be empty) | CORS error; 401 on data fetch |
| 8 | Trigger Vapi test call | HTTP 200 from Railway; appointment row created | HTTP 401 → `VAPI_WEBHOOK_SECRET` mismatch; HTTP 403 → check `vapi:tool` singular scope |
| 9 | Verify dashboard shows Vapi row | Row with `status=new`, `source=vapi` visible | No row → check `clinic_id` alignment; empty dashboard |
| 10 | Staff clicks Confirm on Vapi row | Status transitions to `confirmed`; button disappears | HTTP 401 → Bearer token issue; HTTP 403 → auth scope issue |
| 11 | n8n fake signed request (if enabled) | HTTP 200; HTTP 401 on bad signature | HTTP 401 on good signature → `N8N_WEBHOOK_SECRET` mismatch |
| 12 | Review Railway log stream | No secrets; no PHI fields; no `Authorization` header values; no `DATABASE_URL` | Any secret value visible in logs |
| 13 | Logout | `sessionStorage` cleared; redirect to `/login` | Dashboard still accessible after logout |

---

## 15. Evidence Capture Checklist

For each smoke check, capture the following before marking it PASS:

- [ ] **Command or action performed** — exact URL, HTTP method, or UI action
- [ ] **HTTP status code** — expected vs actual
- [ ] **Response body** — for health checks; for appointment creation; sanitized (no PHI, no tokens)
- [ ] **Browser screenshot** — for UI checks (login page, dashboard, Confirm action); no PHI visible
- [ ] **Railway log snippet** — for backend startup, migration, and Vapi/n8n calls; redact secret values
- [ ] **Commit SHA** — the exact git commit deployed (`git rev-parse HEAD`)
- [ ] **Environment** — `staging` (not `local`; not `production`)
- [ ] **Timestamp** — ISO 8601 date/time of the check
- [ ] **Pass/Fail verdict** — explicit; no "partial"
- [ ] **Blocker if failed** — exact symptom and which env var or configuration item to investigate

---

## 16. Failure Stop Rules

**Stop the staging deployment attempt immediately if any of the following are true.**
Document the blocker and do not route traffic.

- [ ] **Any required secret is missing** — Railway variables show empty or placeholder value for
  `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, or `INTERNAL_WEBHOOK_SECRET`
- [ ] **`DATABASE_URL` points to wrong DB** — connection string contains `localhost`, `127.0.0.1`,
  or a production host
- [ ] **`FRONTEND_CORS_ORIGINS` contains wildcard** — `*` would allow any origin; stop immediately
- [ ] **ngrok URL used in any env var** — Railway URL must replace ngrok; ngrok is not stable for staging
- [ ] **HTTPS missing** — any staging URL is HTTP rather than HTTPS
- [ ] **Backend tests failing** — `pytest backend/tests/` returns non-zero exit before deploy
- [ ] **`npm run build` failing** — Next.js build fails; do not deploy broken frontend
- [ ] **Migration fails** — Alembic non-zero exit; backend does not start; investigate before retry
- [ ] **Login fails after correct credentials** — `JWT_SECRET_KEY` likely missing or wrong
- [ ] **Vapi call creates auto-confirmed appointment** — `status = confirmed` without staff action;
  indicates a critical regression; stop immediately
- [ ] **Real patient data appears in staging DB or logs** — stop; audit data source; do not continue
- [ ] **Secret values appear in Railway or Vercel logs** — stop; rotate affected secrets immediately
- [ ] **`DATABASE_URL` printed in Railway logs** — contains DB password; rotate DB password; investigate logging
- [ ] **Production DB touched** — any connection attempt to a production database; stop; isolate staging

---

## 17. Rollback Dry-Run Checklist

### 17.1 Rollback Readiness (Before Deploy)

- [ ] Previous stable Railway deployment identified and noted (commit SHA)
- [ ] Previous stable Vercel deployment identified and noted (deployment ID)
- [ ] Rollback owner confirmed (who will execute the rollback if needed)

### 17.2 Backend Rollback

- [ ] Railway dashboard → Deployments → select previous successful deployment → Redeploy
- [ ] No code change or git revert required
- [ ] After rollback: re-run smoke steps 1–3 (`/health`, `/health/ready`, migration status)
- [ ] If Railway deployment history is empty (first deploy): rollback means removing the
  Railway service; local environment is unaffected

### 17.3 Frontend Rollback

- [ ] Vercel dashboard → Deployments → select previous successful deployment → Promote
- [ ] If `NEXT_PUBLIC_API_BASE_URL` was the cause of failure: update Vercel env var and
  trigger a new build (build-time variable; cannot hot-patch)
- [ ] After rollback: re-run smoke steps 4–7 (frontend login and dashboard)

### 17.4 Vapi URL Rollback

- [ ] If Vapi test assistant was previously pointing at ngrok (local dev): revert the
  server URL in the Vapi dashboard to the ngrok URL until Railway is stable
- [ ] If Vapi was unused before: no Vapi rollback needed

### 17.5 n8n Rollback (if enabled)

- [ ] Revert n8n staging workflow webhook URL to previous value (or disable the workflow)
- [ ] Revert n8n HMAC secret to match the previous `N8N_WEBHOOK_SECRET` in Railway (if rotated)

### 17.6 Database Rollback

- [ ] For staging: acceptable to re-run migrations on a fresh DB; no production-grade rollback needed
- [ ] No migration down-run (`alembic downgrade`) is required for staging at this scale
- [ ] If DB is corrupted: delete Railway PostgreSQL add-on; recreate; re-run migrations; re-seed

### 17.7 Post-Rollback Smoke

After any rollback, run at minimum:
- [ ] `GET /health` and `GET /health/ready`
- [ ] Login smoke
- [ ] Dashboard smoke
- [ ] Declare rollback PASS or FAIL before re-attempting the forward deploy

---

## 18. Go/No-Go Summary

| Decision | Verdict | Condition |
|---|---|---|
| **Staging deployment attempt** | **GO (when dry-run complete)** | All Phase 1–13 checklists signed off; no failure stop rules triggered |
| **Staging smoke after deploy** | **GO** | All smoke steps 1–13 pass; evidence captured |
| **Production PHI launch** | **NO-GO** | 12 unresolved blockers per Architecture Checkpoint 12; httpOnly cookie auth not implemented; no production domain; no managed prod DB |
| **Fabel 5 / frontend UX sprint** | **WAIT** | Deferred until staging deployment is confirmed working |
| **Appointment workflow expansion** | **WAIT** | Deferred until staging topology clear |
| **Auth/session hardening (httpOnly cookie)** | **PLAN IN MODULE 98** | Must complete before any real clinic staff access production; staging approval does not substitute |

**Staging approval is NOT production approval.** Completing this checklist and passing
the staging smoke runbook confirms the system works with fake data on Railway + Vercel.
It does not resolve any of the 12 production blockers documented in Architecture
Checkpoint 12.

---

## 19. Recommended Next Step

**Sprint 13 / Module 98 — Auth/Session Hardening Implementation Plan**

With the staging topology, env var matrix, and dry-run checklist complete, the largest
remaining production blocker is the `sessionStorage` JWT. Module 98 produces a
detailed implementation plan for httpOnly Secure SameSite cookie auth:

- Current `sessionStorage` flow in `frontend/lib/auth.ts`
- Backend changes needed: `Set-Cookie` on login; cookie-based auth dependency; `POST /auth/logout`
- Frontend changes needed: remove manual `Authorization` header injection; `credentials: "include"`
- CSRF mitigation strategy (SameSite=Lax + same registered domain)
- Test plan for the cookie migration
- No implementation in Module 98 — plan only; execution is Sprint 14
