# Railway Backend Deployment Prep — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 14 / Module 101
**Status:** Planning and config prep only — no deployment executed in this module

---

## 1. Purpose

This document defines the Railway backend deployment configuration for PraxisMed staging.
It records the chosen approach, the files created, the required Railway env vars, the
migration strategy, and the remaining blockers before an actual Railway deployment attempt.

**What this document is:**
- A reference for the actual Railway service creation (Module 102 or later)
- A record of the config files created in Module 101
- The Railway-specific section of the staging deployment preparation sequence

**What this document is not:**
- A deployment execution (no Railway service is created in this module)
- A production launch plan (production PHI launch remains NO-GO)
- An auth/session hardening implementation
- A document containing real secrets

Staging uses fake/non-PHI data only. No deployment is executed in this module.

---

## 2. Selected Railway Backend Approach

| Decision | Choice | Rationale |
|---|---|---|
| Platform | Railway | PaaS; managed PostgreSQL add-on; Nixpacks Python auto-detection; no Docker required |
| Build system | Nixpacks (Railway default) | Auto-detects Python from `runtime.txt` + `requirements.txt` at repo root (which references `backend/requirements.txt`) |
| Start command source | `Procfile` at repo root | Simplest Railway config; Railway reads `web:` process type automatically |
| Migration strategy | Manual predeploy step | Web process does not auto-run migrations; avoids unintended DB mutations on every restart |
| Service root | Repo root | Required so `backend.app.main:app` import path resolves correctly |

---

## 3. Config Files Created in Module 101

### 3.0 `requirements.txt` (repo root — Railway/Railpack direct dependencies)

```
fastapi==0.138.2
uvicorn[standard]==0.49.0
asyncpg==0.31.0
alembic==1.18.5
pydantic==2.13.4
PyJWT==2.4.0
bcrypt==3.2.0
```

Railway (Railpack/Nixpacks) looks for `requirements.txt` at the service root and installs
from it during a cached build step. The root file must list all dependencies directly.

**Do not use `-r backend/requirements.txt` in the root `requirements.txt`.** A nested
include reference causes a Railway build failure because Railway cannot resolve it during
its install cache step. This was confirmed by a real Railway build failure. The root file
must be a flat list of pinned packages matching `backend/requirements.txt`.

**Do not set Railway root directory to `backend/`.** Setting root to `backend/` causes:
```
ModuleNotFoundError: No module named 'backend'
```
because the start command `backend.app.main:app` resolves from inside `backend/` where
the `backend` package does not exist. Always leave root directory blank (repo root).

### 3.1 `backend/requirements.txt`

```
fastapi==0.138.2
uvicorn[standard]==0.49.0
asyncpg==0.31.0
alembic==1.18.5
pydantic==2.13.4
PyJWT==2.4.0
bcrypt==3.2.0
```

**Package notes:**
- `fastapi` — web framework; `fastapi.security` and `fastapi.middleware.cors` used
- `uvicorn[standard]` — ASGI server; `[standard]` installs uvloop and httptools for production throughput
- `asyncpg` — PostgreSQL async driver; used by `backend/app/db/pool.py`
- `alembic` — migrations; auto-installs SQLAlchemy and Mako as transitive deps
- `pydantic` — request/response schema validation
- `PyJWT` — JWT encode/decode via `import jwt` in `backend/app/core/jwt_tokens.py`; HS256 only
- `bcrypt` — password hashing via `import bcrypt` in `backend/app/core/password_hashing.py`

**Not included (correctly):**
- `python-jose` — not used; backend uses `PyJWT` directly
- `passlib` — not used; backend uses `bcrypt` directly
- `httpx` — test-only (FastAPI TestClient); not needed at runtime on Railway
- `pytest`, `pytest-asyncio`, `anyio` — development/test tools only
- `cryptography` — only needed for RSA/EC JWT algorithms; backend uses HS256 only

### 3.2 `runtime.txt` (repo root)

```
python-3.11
```

Railway's Nixpacks reads `runtime.txt` to pin the Python version. Without it, Nixpacks
uses its default Python version (which may differ from the development environment).

### 3.3 `Procfile` (repo root)

```
web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

**Binding notes:**
- `--host 0.0.0.0` — required; `127.0.0.1` (local dev default) is unreachable from Railway's network
- `--port $PORT` — required; Railway auto-injects `$PORT`; hard-coding 8000 will fail
- `python -m uvicorn` — runs uvicorn as a module; correct for this project structure
- `backend.app.main:app` — import path requires the service root to be the repo root

**Migration exclusion:** Migrations are NOT in the `web` start command. The web process
should not mutate the database automatically on every restart until the migration policy
and deployment pipeline are mature. See Section 6 for the migration strategy.

### 3.4 `.gitignore` additions

Root `.gitignore` updated to cover previously untracked files:
- `backend/.env` — local secrets; never committed
- `frontend/.env.local` — local frontend env; never committed
- `frontend/.next/` — Next.js build output
- `frontend/next-env.d.ts` — Next.js generated type declaration
- `frontend/node_modules/` — npm dependencies
- `frontend/package-lock.json` — npm lockfile (remove from `.gitignore` if committing)

---

## 4. Required Railway Environment Variables

All variables must be set in the Railway service's **Environment** panel before deployment.
No real values are specified in this document. Use `openssl rand -hex 32` for all secrets.

| Variable | Source | Secret? | Notes |
|---|---|---|---|
| `DATABASE_URL` | Auto-injected by Railway PostgreSQL add-on | Yes | Do not set manually; Railway injects this |
| `JWT_SECRET_KEY` | Railway dashboard — manual | Yes | `openssl rand -hex 32`; missing raises `MissingJWTSecretError` → 503 |
| `VAPI_WEBHOOK_SECRET` | Railway dashboard — manual | Yes | Must match Vapi staging assistant config; `openssl rand -hex 32` |
| `N8N_WEBHOOK_SECRET` | Railway dashboard — manual | Yes | Must match n8n staging workflow config; `openssl rand -hex 32` |
| `INTERNAL_WEBHOOK_SECRET` | Railway dashboard — manual | Yes | Internal webhook HMAC verification; `openssl rand -hex 32` |
| `FRONTEND_CORS_ORIGINS` | Railway dashboard — manual | No | Exact Vercel staging frontend URL (e.g., `https://staging-app.vercel.app`); no wildcard; no ngrok |
| `APP_ENV` | Railway dashboard — manual | No | Set to `staging`; optional but recommended |

**Staging secret isolation rules:**
- All staging secrets must be distinct from local-dev placeholder values
  (`local-dev-jwt-secret-key-change-in-production`, etc.)
- Staging secrets must be distinct from future production secrets
- No local-dev placeholder values may appear in any Railway staging env var
- No production secrets may appear in any Railway staging env var

---

## 5. Railway PostgreSQL Binding

| Item | Notes |
|---|---|
| Add-on type | Railway managed PostgreSQL (via Railway dashboard → Add Plugin → PostgreSQL) |
| `DATABASE_URL` injection | Auto-injected by Railway after the PostgreSQL add-on is linked to the service |
| Connection string format | `postgresql://user:password@host:port/dbname` (Railway provides this) |
| Isolation | Staging PostgreSQL is a separate Railway add-on from any future production DB |
| Local Docker DB | `docker-compose.postgres.yml` is local-only; must NOT be referenced in staging |
| No production DB | Production database does not exist; staging must not share a DB with production |

---

## 6. Migration Strategy

Migrations are NOT auto-run by the `web` process (Procfile). Instead, run migrations
manually before or after deploy using one of:

**Option A — Railway "Run Command" panel (recommended for staging):**
```
python backend/scripts/run_migrations.py
```
Run this once from the Railway dashboard "Run Command" feature after the service and
PostgreSQL add-on are created.

**Option B — Railway predeploy command in `railway.toml` (future automation):**
```toml
[deploy]
preDeployCommand = "python backend/scripts/run_migrations.py"
startCommand = "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"
```
This runs migrations before the web process starts on each deploy. Appropriate when
the migration policy is validated and a CI/CD pipeline is in place. Not created in
Module 101; documented here for reference.

**Migration runner notes (`backend/scripts/run_migrations.py`):**
- Reads `DATABASE_URL` from env; exits with code 1 if `DATABASE_URL` is not set
- Reads `backend/alembic.ini`; exits with code 1 if not found
- Runs `alembic upgrade head`; exits with code 1 if Alembic reports a failure
- Exits with code 0 on success
- Has no DB-ready retry loop — if PostgreSQL is not yet accepting connections,
  the migration will fail immediately. For manual runs, wait for Railway PostgreSQL
  to show "Running" status before executing.
- Migration files: `0001_initial_schema`, `0002_add_password_hash_to_clinic_users`

---

## 7. Health Check

Railway can be configured to use the health endpoint to determine service readiness.

| Route | Expected response | Notes |
|---|---|---|
| `GET /health` | `{"status": "ok"}` | Responds even without a database connection |
| `GET /health/ready` | `{"status": "ready"}` | Returns 503 if database pool is None |

**Railway health check recommendation:**
- Set health check path to `/health` in Railway service settings
- `/health` is the correct choice for liveness; `/health/ready` for readiness

---

## 8. Log Safety

The following must hold at all times in staging:

| Rule | Detail |
|---|---|
| No secrets in logs | `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET` must never appear in any log line |
| No raw PII in logs | No patient names, phone numbers, or appointment details in logs |
| No `Authorization` header logging | FastAPI does not log request headers by default; no custom middleware must add this |
| DB credentials not logged | `DATABASE_URL` contains credentials; must not be logged |
| Log level | Uvicorn default (`INFO`); do not set to `DEBUG` in staging without reviewing what gets logged |

---

## 9. Vapi Integration

| Item | Value | Notes |
|---|---|---|
| Staging Vapi endpoint | `POST /vapi/tools/capture-appointment-request` | Railway HTTPS URL + this path |
| Required machine auth scope | `X-Vapi-Scopes: vapi:tool` | Singular — `vapi:tools` plural returns HTTP 403 |
| `X-Clinic-Ref` header | Staging fake clinic UUID (TBD in Module 103) | Must match a real record in the staging DB |
| `VAPI_WEBHOOK_SECRET` | Staging secret; must match Vapi assistant webhook secret | Distinct from local-dev and production values |
| No ngrok in staging | Vapi assistant must point to Railway HTTPS URL | ngrok is local-dev only; stop rule if ngrok URL appears |
| No auto-confirmation | Appointment request is always created with `status='new'`, `action_required=True` | No code path auto-confirms; stop rule if ever observed |
| Staff Confirm required | `PATCH /appointment-requests/{id}/status` — requires JWT auth and human action | Cannot be bypassed by AI |

---

## 10. CORS and Domain Safety

| Rule | Detail |
|---|---|
| No wildcard CORS | `_cors_origins()` in `main.py` never returns `*`; confirmed in all prior checkpoints |
| `FRONTEND_CORS_ORIGINS` must be exact | Must be the exact Vercel staging URL (e.g., `https://staging-app.vercel.app`) |
| HTTPS required | Both Railway backend URL and Vercel frontend URL must be HTTPS; Railway and Vercel provide HTTPS on their subdomains by default |
| No ngrok in `FRONTEND_CORS_ORIGINS` | ngrok is local-dev only; its presence in a staging env var is a stop rule |
| No real patient data | CORS policy does not affect this; data constraint is absolute |

---

## 11. Remaining Blockers Before Actual Railway Deployment

The following items are NOT resolved in Module 101. They block the actual staging
deployment attempt.

| # | Blocker | Module |
|---|---|---|
| 1 | Railway service not yet created | Module 101 execution / actual deploy |
| 2 | Railway PostgreSQL add-on not yet provisioned | Module 101 execution / actual deploy |
| 3 | Actual Railway HTTPS backend URL unknown until service created | Post-creation |
| 4 | `FRONTEND_CORS_ORIGINS` value unknown until Vercel URL assigned (Module 102) | Module 102 |
| 5 | `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET` not yet set in Railway dashboard | Deploy time |
| 6 | Migrations not yet applied to staging DB | After DB provisioned |
| 7 | Staging fake clinic + user provisioning strategy not defined | Module 103 |
| 8 | Vapi staging test assistant not yet configured | Module 104 |
| 9 | No staging smoke execution yet | Module 104 |
| 10 | Staging frontend (Vercel) not yet deployed | Module 102 |

---

## 12. Non-Goals

- No deployment execution in this module
- No production launch (production PHI launch remains NO-GO; all 12 blockers open)
- No real patient data or real clinic data
- No auth/session hardening implementation (planned post-M2 smoke evidence)
- No Fabel 5 / frontend UX sprint
- No appointment workflow expansion
- No real Railway service or Vercel project creation
- No real secrets in any file created by this module
