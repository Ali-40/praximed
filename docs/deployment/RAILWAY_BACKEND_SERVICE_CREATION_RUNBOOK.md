# Railway Backend Service Creation Runbook — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 15 / Module 105
**Status:** Planning only — no deployment executed by Claude in this module

---

## 1. Purpose

This is a human-executable step-by-step guide for creating the Railway backend service
for PraxisMed fake-data staging. The developer follows this runbook manually in the
Railway dashboard or Railway CLI.

**What this runbook is:**
- Exact steps for creating the Railway backend service for staging
- The required settings, env var names, and evidence to capture at each step
- A failure triage reference for common Railway setup issues

**What this runbook is not:**
- A deployment executed by Claude — no Railway API calls are made here
- A production launch plan — production PHI launch remains NO-GO
- A Railway PostgreSQL provisioning guide — that is Module 106
- A Vercel frontend deployment guide — that is Module 107
- A document containing real secrets — all values are placeholders

Staging uses fake/non-PHI data only. No deployment is executed in this module.
No real patient data. No production secrets.

---

## 2. Current Repo Readiness

The repository has all files Railway requires. No further code changes are needed
before creating the Railway backend service.

| Item | Path | Status | Notes |
|---|---|---|---|
| Start command | `Procfile` (repo root) | READY | `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
| Python version | `runtime.txt` (repo root) | READY | `python-3.11` — Railway Nixpacks reads this |
| Runtime dependencies | `backend/requirements.txt` | READY | 7 pinned deps: fastapi, uvicorn[standard], asyncpg, alembic, pydantic, PyJWT, bcrypt |
| Application entry point | `backend/app/main.py` | READY | `backend.app.main:app` — FastAPI `app` object |
| Health endpoint | `GET /health` | READY | Returns `{"status": "ok", "service": "PraxisMed API"}` — no DB required |
| DB-ready endpoint | `GET /health/ready` | READY | Returns 503 if DB pool is None; returns 200 once `DATABASE_URL` is wired |
| Migration runner | `backend/scripts/run_migrations.py` | READY | Reads `DATABASE_URL`; runs `alembic upgrade head`; exits non-zero on failure |
| CORS implementation | `backend/app/main.py` — `_cors_origins()` | READY | Reads `FRONTEND_CORS_ORIGINS`; never returns `*` |
| All backend tests | `backend/tests/` | READY | 2103/2103 passed as of Architecture Checkpoint 14 |

---

## 3. Preconditions for the Developer

Verify all of the following before starting the Railway service creation steps:

### 3.1 Account and Access

- [ ] Railway account created (https://railway.app — personal or team account)
- [ ] Railway workspace/project space available
- [ ] GitHub account connected to Railway (Railway needs read access to the repo)
- [ ] PraxisMed GitHub repository accessible from Railway
- [ ] Current git branch is `master` (the branch Railway should deploy from)

### 3.2 Secrets Prepared

Generate the following values using `openssl rand -hex 32` before opening the Railway
dashboard. Do NOT paste them into any document or chat. Store them in a password manager
or local notes that will not be committed.

- `JWT_SECRET_KEY` — one freshly generated value; not the local-dev placeholder
- `VAPI_WEBHOOK_SECRET` — one freshly generated value; must match Vapi staging assistant config
- `N8N_WEBHOOK_SECRET` — one freshly generated value; must match n8n staging workflow config
- `INTERNAL_WEBHOOK_SECRET` — one freshly generated value

**Command to generate each:**
```
openssl rand -hex 32
```

Run this four times; store each value securely before proceeding.

### 3.3 Data Safety Check

- [ ] Confirm no real patient data will be used in any staging test
- [ ] Confirm the local-dev placeholder values (`local-dev-jwt-secret-key-change-in-production`, etc.) will NOT be used as staging secrets
- [ ] Confirm staging Railway PostgreSQL will be a separate service from any future production DB

---

## 4. Railway Project and Service Creation Steps

### Step 4.1 — Create or Select a Railway Project

1. Log in to https://railway.app
2. Click **New Project**
3. Choose **Deploy from GitHub repo**
4. Authorize Railway to access your GitHub organization/account if prompted
5. Search for and select the PraxisMed repository
6. Railway will detect the repository and present service options

**Recommended project name:** `praxismed-staging`
**Recommended service name:** `praxismed-backend-staging`

### Step 4.2 — Configure the Service from GitHub

Railway will attempt to auto-detect the project type using Nixpacks:

1. Railway reads `runtime.txt` at repo root → detects Python 3.11
2. Railway reads `requirements.txt` at repo root → this file contains `-r backend/requirements.txt`, which causes pip to install the 7 pinned runtime deps from `backend/requirements.txt`
3. Railway reads `Procfile` at repo root → sets the start command to `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

**Root `requirements.txt` is a Nixpacks detection bridge.** Nixpacks looks for `requirements.txt`
at the service root. The repo root `requirements.txt` contains only `-r backend/requirements.txt`
and delegates all dependency pins to `backend/requirements.txt`. Do not duplicate pins.

**Verify Nixpacks detected the correct settings before first deploy.** If Railway
asks you to confirm a build command or start command, verify it matches exactly:

```
web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

### Step 4.3 — Set the Deployment Branch

In the Railway service settings:
- Set the **source branch** to `master` (the current working branch for this project)
- Confirm the branch exists in GitHub

### Step 4.4 — Auto-Deploy Setting

Railway can auto-deploy on every push to the source branch. For the first staging
deployment:
- **Recommended:** Disable auto-deploy initially, or leave enabled but understand that
  every push to `master` will trigger a new Railway deploy
- **Risk if enabled:** A broken push will deploy a broken backend; Railway rolls back to
  previous deployment if health check fails, but this requires health check to be configured

---

## 5. Backend Service Settings

Configure these settings in the Railway service → **Settings** panel:

| Setting | Value | Notes |
|---|---|---|
| **Service name** | `praxismed-backend-staging` (or similar) | Displayed in Railway dashboard |
| **Root directory** | **Leave as repo root (empty / blank)** — do NOT set to `backend` | Setting root to `backend` causes `ModuleNotFoundError: No module named 'backend'` because `backend.app.main:app` is resolved from inside `backend/`, where the `backend` package does not exist |
| **Start command** | (from Procfile — Railway reads automatically) `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | Do NOT override unless Railway fails to read Procfile |
| **Build command** | (Nixpacks automatic — `pip install -r requirements.txt` → delegates to `backend/requirements.txt`) | Do NOT override |
| **Python version** | 3.11 (from `runtime.txt`) | Railway Nixpacks reads `runtime.txt` at repo root |
| **Health check path** | `/health` | Set in Railway service → Settings → Health Check; Railway uses this to determine if the deploy succeeded |
| **Source branch** | `master` | The current working branch |
| **Deployment region** | Choose the region closest to your users (e.g., EU West for Austrian clinic) | Optional; Railway defaults to US if not set |

### 5.1 Why `--host 0.0.0.0` Is Required

The local development uvicorn command uses `--host 127.0.0.1`, which binds only to
localhost. On Railway, the process must bind to `0.0.0.0` so Railway's network layer
can route external HTTPS traffic to the service. If the process binds to `127.0.0.1`
on Railway, the service will appear to start but all inbound requests will time out.

### 5.2 Why `$PORT` Is Required

Railway injects the `PORT` environment variable automatically. The service must listen
on `$PORT`, not a hard-coded port like `8000`. If `--port 8000` is used instead of
`--port $PORT`, Railway health checks will fail because the process is not listening on
the port Railway assigned.

### 5.3 Why `backend.app.main:app` Is the Correct Import Path

The FastAPI `app` object lives at `backend/app/main.py`. Because Railway runs the
service from the repo root (not from `backend/`), the module must be referenced as
`backend.app.main:app`. Running `python -m uvicorn app.main:app` (without the
`backend.` prefix) would fail with `ModuleNotFoundError`.

### 5.4 Why Root Directory Must NOT Be Set to `backend`

Setting the Railway service root directory to `backend/` causes a fatal import error:

```
ModuleNotFoundError: No module named 'backend'
```

This happens because:
- The start command is `python -m uvicorn backend.app.main:app`
- When the working directory is `backend/`, Python resolves `backend` as a top-level package
  relative to `backend/` — but the `backend` package does not exist inside `backend/`
- The `backend` package exists at repo root (`/backend/app/main.py`)
- Only when the working directory is the repo root can Python find `backend.app.main`

**Always leave the Railway root directory blank (repo root).** This was confirmed by a real
failed deployment where root was set to `backend`: the app crashed immediately on startup
with `ModuleNotFoundError: No module named 'backend'`.

---

## 6. Required Railway Backend Environment Variables

Set all of the following in the Railway service → **Variables** panel before the first
deploy. Values marked `<placeholder>` must be replaced with real staging values; they
must not contain the local-dev placeholder strings.

| Variable | Value (placeholder) | Secret? | Set before first deploy? | Failure mode if missing |
|---|---|---|---|---|
| `DATABASE_URL` | `<railway-postgres-url>` — auto-injected when Railway PostgreSQL add-on is linked | Yes | No — add after PostgreSQL provisioning (Module 106) | App starts with `db_pool = None`; `/health` returns 200 but `/health/ready` returns 503; all DB-backed routes return 503 |
| `JWT_SECRET_KEY` | `<staging-high-entropy-secret>` from `openssl rand -hex 32` | Yes | YES — required for auth routes | `MissingJWTSecretError` → 503 on startup or on first auth request |
| `VAPI_WEBHOOK_SECRET` | `<staging-high-entropy-secret>` from `openssl rand -hex 32` | Yes | YES — required for Vapi tool route | 401/403 on Vapi webhook requests |
| `N8N_WEBHOOK_SECRET` | `<staging-high-entropy-secret>` from `openssl rand -hex 32` | Yes | Recommended — required for n8n route | 401/403 on n8n webhook requests |
| `INTERNAL_WEBHOOK_SECRET` | `<staging-high-entropy-secret>` from `openssl rand -hex 32` | Yes | Recommended | 401/403 on internal webhook requests |
| `FRONTEND_CORS_ORIGINS` | `<vercel-staging-frontend-url>` — exact Vercel HTTPS URL (no trailing slash) | No | NO — set after Vercel URL is known (Module 107) | CORS defaults to localhost origins; browser requests from Vercel will fail preflight |
| `APP_ENV` | `staging` | No | Optional but recommended | App runs without it; useful for conditional logging |

**How to set env vars in Railway:**
1. Open the Railway service → **Variables** tab
2. Click **+ New Variable**
3. Enter the variable name exactly as shown above
4. Enter the value (never commit values to any file)
5. Railway will redeploy automatically when variables are saved (if auto-deploy is enabled)

**Do not print variable values** in logs, Railway "Run Command" output, or any document.

---

## 7. DATABASE_URL Binding Note

`DATABASE_URL` is not set manually when using the Railway PostgreSQL add-on:

1. Create the Railway PostgreSQL plugin (Module 106)
2. Railway automatically injects `DATABASE_URL` into the backend service environment
3. The backend reads `DATABASE_URL` via `os.environ.get("DATABASE_URL")` in `main.py`
4. If `DATABASE_URL` is absent at startup, `app.state.db_pool` is set to `None` and
   all DB-backed routes return 503; `/health` still returns 200

**Safety rules:**
- Never use the local Docker `DATABASE_URL` (`postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local`) in Railway
- Never use a production `DATABASE_URL` in staging
- Never hard-code any `DATABASE_URL` in any source file
- Confirm the Railway `DATABASE_URL` points to the Railway PostgreSQL staging add-on before running migrations

---

## 8. First Backend Deploy Expectations

When the Railway backend service deploys for the first time:

| Phase | Expected | If Different |
|---|---|---|
| Nixpacks build | Detects Python 3.11 from `runtime.txt`; installs 7 packages from `backend/requirements.txt` | Check Railway build logs; see Section 12 |
| Process start | Runs `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`; binds to Railway-assigned PORT | Procfile not detected? See Section 12 |
| Lifespan startup | Reads `DATABASE_URL`; if absent, logs warning and sets `db_pool = None` | Expected — PostgreSQL not yet provisioned |
| `/health` response | `{"status": "ok", "service": "PraxisMed API"}` — 200 | Fail → service not running; check logs |
| `/health/ready` response | 503 until `DATABASE_URL` is wired and DB is accessible | Expected until Module 106 PostgreSQL provisioning |
| DB-backed routes | 503 (pool is None) | Expected — no PostgreSQL yet |
| CORS | Requests from `localhost:3000` succeed; requests from Vercel fail until `FRONTEND_CORS_ORIGINS` is set | Expected — set after Module 107 |

**A first deploy where `/health` returns 200 but `/health/ready` returns 503 is a
successful partial deploy.** It confirms the service is running; the DB-ready routes
will be unblocked after Module 106 (Railway PostgreSQL provisioning).

---

## 9. Migration Command

Migrations are NOT run automatically by the web process (Procfile). They must be
run manually after Railway PostgreSQL is provisioned and `DATABASE_URL` is available.

**Do not run this command until Module 106 is complete and `DATABASE_URL` is confirmed.**

When ready (Module 106), run via Railway "Run Command" (service → **Shell** or **Run Command** panel):

```
python backend/scripts/run_migrations.py
```

This command:
1. Reads `DATABASE_URL` from the Railway environment (auto-injected by the PostgreSQL add-on)
2. Resolves `backend/alembic.ini`
3. Runs `alembic -c backend/alembic.ini upgrade head`
4. Applies two migrations: `0001_initial_schema` (11 tables) → `0002_password_hash` (adds `password_hash` column to `clinic_users`)
5. Exits 0 on success; exits non-zero on failure

**Stop if the migration command exits non-zero.** Do not proceed to fake data provisioning
or smoke execution if migrations fail.

**Do not print `DATABASE_URL`** in any output or evidence capture. The Railway dashboard
displays `DATABASE_URL` in the Variables panel — this is normal; do not paste its value
into any document.

---

## 10. Health Check Verification

After the first Railway deploy completes, verify the health endpoint manually:

```
curl https://<railway-backend-url>/health
```

Expected response:
```json
{"status": "ok", "service": "PraxisMed API"}
```

Expected HTTP status: `200 OK`

For the readiness endpoint (verify after Module 106 — PostgreSQL provisioning):
```
curl https://<railway-backend-url>/health/ready
```

Expected response after DB is connected and migrations applied:
```json
{"status": "ready", "checks": {"app": "ok", "db": "ok"}}
```

If `/health` returns 200 and `/health/ready` returns 503 before PostgreSQL is provisioned,
this is the expected state. Proceed to Module 106.

---

## 11. Evidence to Capture

Record the following after the Railway backend service is created and the first deploy
completes. Record only sanitized information — no secret values, no `DATABASE_URL` value.

| Evidence Item | Value to Record | Notes |
|---|---|---|
| Railway service name | e.g., `praxismed-backend-staging` | From Railway dashboard |
| Railway service URL | `https://<service-name>.up.railway.app` | The public HTTPS URL assigned by Railway |
| Source branch | `master` | Confirm in Railway service settings |
| Commit SHA deployed | Full SHA from Railway deployment log | Confirms exact code version deployed |
| Build status | Success / Failure | From Railway build log |
| Nixpacks Python version detected | `3.11` | From Railway build log |
| Start command detected | `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | From Railway service settings or deploy log |
| Env var names set (not values) | `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET` | Confirm names only; never record values |
| `DATABASE_URL` status | Absent (expected at this stage) | Set to absent until Module 106 |
| `FRONTEND_CORS_ORIGINS` status | Absent (expected at this stage) | Set to absent until Module 107 |
| `GET /health` HTTP status | `200` | Curl or browser |
| `GET /health` response body | `{"status": "ok", "service": "PraxisMed API"}` | Confirm exact JSON |
| `GET /health/ready` HTTP status | `503` (expected — no DB yet) | Expected until Module 106 |
| Railway build log snippet | First 10–15 lines of build output (sanitized) | No secret values in log snippet |
| Any errors or warnings | Describe without pasting secrets | e.g., "WARNING: DATABASE_URL is not set" in uvicorn log |

---

## 12. Failure Triage

| Symptom | Likely Cause | Where to Inspect | Safe Next Action |
|---|---|---|---|
| App crashes: `ModuleNotFoundError: No module named 'backend'` | Railway root directory set to `backend/` instead of repo root — uvicorn runs from inside `backend/` where `backend` package does not exist | Railway runtime log | Set root directory to blank (repo root) in Railway service settings; redeploy |
| Build fails: `ModuleNotFoundError` at import | Wrong import path in start command | Railway build log | Confirm Procfile has `backend.app.main:app`; confirm root is repo root |
| Build fails: `No module named 'fastapi'` | `requirements.txt` at repo root missing or not referencing `backend/requirements.txt` | Railway build log | Confirm repo root `requirements.txt` exists with `-r backend/requirements.txt`; check Railway root directory setting |
| Build fails: Python version mismatch | `runtime.txt` not detected | Railway build log | Confirm `runtime.txt` is at repo root; contains `python-3.11` |
| Service starts but all requests time out | Process bound to `127.0.0.1` instead of `0.0.0.0` | Railway deployment settings / Procfile | Confirm Procfile has `--host 0.0.0.0` |
| Service starts but health check fails: "connection refused" | Process not listening on Railway-assigned `$PORT` | Railway deployment log | Confirm Procfile has `--port $PORT` (not `--port 8000`) |
| `/health` returns 500 | Application startup error | Railway service log stream | Check for missing `JWT_SECRET_KEY` or other startup-time dependency |
| `/health` returns 200 but `/health/ready` returns 503 | `DATABASE_URL` not yet set / DB pool is None | Railway service log | Expected at this stage — proceed to Module 106 (PostgreSQL provisioning) |
| CORS error in browser | `FRONTEND_CORS_ORIGINS` not set or wrong value | Browser network tab | Set `FRONTEND_CORS_ORIGINS` to exact Vercel URL after Module 107 |
| Migration fails: `DATABASE_URL not set` | Migration run before `DATABASE_URL` was injected | Railway "Run Command" output | Confirm Railway PostgreSQL add-on is linked and `DATABASE_URL` is visible in Variables panel |
| Migration fails: `alembic.ini not found` | Script run from wrong working directory | Railway "Run Command" output | Ensure command is `python backend/scripts/run_migrations.py` (from repo root) |
| Railway asks for production secrets | Railway environment accidentally set to production | Railway Variables panel | Stop; verify you are in the correct Railway project and environment |

---

## 13. Stop Rules

Stop staging deployment immediately if any of the following are observed:

| Stop Rule | Trigger |
|---|---|
| Railway asks to configure production secrets | Any prompt for production values; staging and production must be fully isolated |
| `DATABASE_URL` points to local Docker or production DB | The URL contains `localhost`, `127.0.0.1`, or a known production host |
| Real patient data appears in any log line | Any real name, phone number, DOB, or medical record |
| Secrets appear in Railway logs | `JWT_SECRET_KEY`, any `openssl`-generated value, or any `DATABASE_URL` password visible in public log output |
| The start command or build requires a code change | The repo is ready as-is; if Railway cannot start the service without a code change, diagnose the misconfiguration (do not patch code to work around Railway settings) |
| `/health` continues to fail after obvious config corrections | Investigate root cause; do not proceed to PostgreSQL provisioning until `/health` returns 200 |
| Migrations are run before `DATABASE_URL` is wired | Run `python backend/scripts/run_migrations.py` only after Module 106 confirms `DATABASE_URL` is injected |

---

## 14. What This Runbook Does Not Cover

| Topic | Covered In |
|---|---|
| Railway PostgreSQL add-on creation | Module 106 |
| `DATABASE_URL` wiring to backend service | Module 106 |
| Migration execution and evidence | Module 106 |
| Staging fake clinic/user SQL provisioning | Module 106 (per Module 103 strategy) |
| Vercel frontend project creation | Module 107 |
| `NEXT_PUBLIC_API_BASE_URL` configuration | Module 107 |
| `FRONTEND_CORS_ORIGINS` final value | Module 107 (after Vercel URL is known) |
| CORS preflight verification | Module 108 |
| Vapi test assistant staging URL configuration | Module 108 |
| n8n staging workflow configuration | Module 108 |
| Full staging smoke execution | Module 109 |
| Production launch | Production PHI launch remains NO-GO |
| Auth/session hardening (httpOnly cookie) | Post-staging-smoke; Sprint 15 |
| Fabel 5 / frontend UX sprint | Deferred |

---

## 15. Recommended Next Step — Module 106

**Sprint 15 / Module 106 — Railway PostgreSQL Provisioning and Migration Evidence**

After completing this runbook and confirming `/health` returns 200:

1. Add the Railway PostgreSQL plugin to the staging Railway project
2. Confirm `DATABASE_URL` is auto-injected into the backend service
3. Wait for Railway PostgreSQL to show "Running" status
4. Run `python backend/scripts/run_migrations.py` via Railway "Run Command"
5. Capture sanitized migration evidence
6. Verify `db_smoke_test.py` passes
7. Provision staging fake clinic and user (per Module 103 Section 8 SQL template)
8. Confirm `/health/ready` returns 200

Module 106 covers all of these steps with evidence templates and stop rules.
