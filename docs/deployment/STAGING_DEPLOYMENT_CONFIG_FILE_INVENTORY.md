# Staging Deployment Config File Inventory — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 14 / Module 100
**Status:** Inventory only — no deployment executed in this module; no runtime code changed

---

## 1. Purpose

This document inventories every deployment-relevant config file, command, path, and
platform setting in the PraxisMed repository and identifies what is present, what is
missing, and what must be created before the actual staging deployment attempt.

The staging deployment dry-run checklist (Module 97) and production deployment execution
plan (Module 99) assume certain files and commands exist. This module audits those
assumptions against the actual repository state.

**What this document is:**
- A precise inventory of the repo's deployment readiness state
- A catalogue of missing files and gaps that block staging deployment
- The input reference for Module 101 (Railway Backend Deployment Prep) and Module 102
  (Vercel Frontend Deployment Prep)

**What this document is not:**
- A deployment execution (no deployment occurs in this module)
- A production launch document (production PHI launch remains NO-GO)
- An auth/session hardening implementation
- A runtime code change

Staging uses fake/non-PHI data only. Production PHI launch remains NO-GO until all
12 blockers from Architecture Checkpoint 12 are resolved.

---

## 2. Current Repository Layout

Actual structure as of Module 100 inspection:

```
praximed/                         ← repo root (working directory for all commands)
├── .gitignore                    ← EXISTS — gaps documented in Section 8
├── conftest.py                   ← EXISTS — adds repo root to sys.path for pytest
├── pytest.ini                   ← EXISTS — asyncio_mode=auto; testpaths=backend/tests
├── docker-compose.postgres.yml   ← EXISTS — local-dev PostgreSQL only; not for staging
├── backend/
│   ├── alembic.ini               ← EXISTS — script_location=%(here)s/migrations
│   ├── app/
│   │   ├── main.py               ← EXISTS — app import path: backend.app.main:app
│   │   ├── api/routes/           ← EXISTS — all PHI and machine-auth routes
│   │   └── core/                 ← EXISTS — JWT, auth, password hashing
│   ├── migrations/
│   │   ├── versions/
│   │   │   ├── 0001_initial_schema.py      ← EXISTS
│   │   │   └── 0002_add_password_hash_to_clinic_users.py  ← EXISTS
│   │   └── env.py                ← EXISTS — reads DATABASE_URL
│   ├── scripts/
│   │   ├── run_migrations.py     ← EXISTS — see Section 4
│   │   └── seed_local_data.py    ← EXISTS — local-only; must NOT run in staging
│   ├── tests/                    ← EXISTS — 1946 tests; all pass
│   ├── tenants/                  ← EXISTS — clinic config JSON files
│   ├── .env.example              ← EXISTS — local-dev placeholder values only
│   ├── requirements.txt          ← MISSING — BLOCKER for Railway
│   └── pyproject.toml            ← MISSING
├── frontend/
│   ├── app/                      ← EXISTS — Next.js App Router pages
│   ├── lib/
│   │   ├── api.ts                ← EXISTS — apiFetch() with Bearer header injection
│   │   └── auth.ts               ← EXISTS — sessionStorage JWT (local-dev labeled)
│   ├── package.json              ← EXISTS — Next.js 14.2.3; build/start/dev/lint scripts
│   ├── next.config.js            ← EXISTS — no output setting (standard Next.js output)
│   ├── tsconfig.json             ← EXISTS
│   ├── .env.example              ← EXISTS — NEXT_PUBLIC_API_BASE_URL placeholder
│   ├── .gitignore                ← MISSING — frontend/.next etc untracked in git status
│   ├── .next/                    ← UNTRACKED (build artifact; not in .gitignore)
│   ├── node_modules/             ← UNTRACKED (deps; not in .gitignore)
│   ├── package-lock.json         ← UNTRACKED (lockfile; not in .gitignore)
│   └── next-env.d.ts             ← UNTRACKED (Next.js generated; not in .gitignore)
├── Procfile                      ← MISSING — needed OR railway.toml
├── railway.toml                  ← MISSING — Railway service config (alternative to Procfile)
├── runtime.txt                   ← MISSING — Python version pin for Railway Nixpacks
├── vercel.json                   ← NOT NEEDED — Vercel auto-detects Next.js 14 (see Section 7)
└── Dockerfile                    ← NOT NEEDED — Railway uses Nixpacks; Vercel native
```

---

## 3. Railway Backend Requirements Inventory

Railway uses **Nixpacks** to auto-detect the build and start process. Nixpacks detects a
Python project by finding `.py` files, but requires a dependency file (`requirements.txt`
or `pyproject.toml`) to install packages.

| Item | Current Repo Status | Required for Railway? | Recommended Action | Blocker Level |
|---|---|---|---|---|
| `requirements.txt` | **MISSING** | YES — Nixpacks reads this to install packages | Create `backend/requirements.txt` with all pinned dependencies | **BLOCKER** |
| Python version pin | **MISSING** — no `runtime.txt` or `[tool.python]` version spec | YES — pin Python 3.11 | Create `runtime.txt` with `python-3.11` OR add `[tool.requires]` in `pyproject.toml` | **HIGH** |
| Backend start command | **NOT CONFIGURED** — no Procfile or `railway.toml` | YES — Railway needs to know the command | Create `Procfile` OR `railway.toml` with start command | **BLOCKER** |
| App import path | `backend.app.main:app` — verified from `main.py` comment | YES — must be specified in start command | Use: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | **BLOCKER** |
| `$PORT` binding | Backend dev command uses `--port 8000`; Railway auto-injects `$PORT` | YES — must bind `0.0.0.0:$PORT` | Start command must use `--port $PORT`; confirmed in Module 97 checklist | **BLOCKER** |
| `0.0.0.0` binding | Local command uses `--host 127.0.0.1`; Railway requires `0.0.0.0` | YES — `127.0.0.1` is unreachable externally | Start command must use `--host 0.0.0.0` | **BLOCKER** |
| `GET /health` route | EXISTS — `backend/app/api/routes/health.py` | YES — Railway uses this for health checks | No action needed; route exists | NONE |
| `DATABASE_URL` env var | Backend reads from env; Railway auto-injects from PostgreSQL add-on | YES — Railway PostgreSQL injects automatically | Set via Railway PostgreSQL add-on; no manual config needed | NONE |
| `JWT_SECRET_KEY` env var | Read from env in `jwt_tokens.py`; missing raises `MissingJWTSecretError` | YES | Set in Railway dashboard with `openssl rand -hex 32` | **HIGH** |
| `VAPI_WEBHOOK_SECRET` | Read from env; missing returns 401 | YES | Set in Railway dashboard | **HIGH** |
| `N8N_WEBHOOK_SECRET` | Read from env | YES | Set in Railway dashboard | HIGH |
| `INTERNAL_WEBHOOK_SECRET` | Read from env | YES | Set in Railway dashboard | HIGH |
| `FRONTEND_CORS_ORIGINS` | Read from env; defaults to localhost (wrong for staging) | YES | Set to exact Vercel staging URL; no wildcard | **HIGH** |
| `APP_ENV` | Read from env; optional | YES (recommended) | Set to `staging` | LOW |
| Migration command | `run_migrations.py` exists and exits non-zero on failure | YES — must run before uvicorn | Use in start command before uvicorn (see Section 4) | **HIGH** |
| DB-ready retry | `run_migrations.py` has NO retry loop | Advisable for Railway cold start | Document gap; add retry in Module 101 if needed | MEDIUM |
| Static files | No static file serving configured | No — Railway backend serves only API | No action needed | NONE |
| Railway root directory | Railway must deploy from repo root (for `backend.app.main:app` import path) | YES | Set Railway root to repo root (default) | MEDIUM |

### 3.1 Backend Start Command

The start command established in Module 97 is:

```
python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

This must be specified in one of:
- A `Procfile` at repo root: `web: python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- A `railway.toml` at repo root: `[deploy] startCommand = "python backend/scripts/run_migrations.py && ..."`

Without one of these, Railway's Nixpacks will attempt to guess the start command and will
likely fail or use the wrong entrypoint.

### 3.2 Required `requirements.txt` Contents

Based on `pip show` inspection of the installed packages the backend currently uses:

| Package | Installed Version | Role |
|---|---|---|
| `fastapi` | 0.138.2 | Web framework |
| `uvicorn[standard]` | 0.49.0 | ASGI server |
| `asyncpg` | 0.31.0 | PostgreSQL async driver |
| `alembic` | 1.18.5 | Database migrations |
| `pydantic` | 2.13.4 | Request/response validation |
| `PyJWT` | 2.4.0 | JWT encoding/decoding (`import jwt` in `jwt_tokens.py`) |
| `cryptography` | 42.0.2 | JWT RSA/EC algorithms (PyJWT dependency) |
| `bcrypt` | 3.2.0 | Password hashing (`import bcrypt` in `password_hashing.py`) |
| `httpx` | 0.26.0 | Test client (httpx via FastAPI TestClient) |

Note: `python-jose` and `passlib` are NOT used. The backend uses `PyJWT` directly for JWT
and `bcrypt` directly for password hashing. Any `requirements.txt` created must reflect this.

---

## 4. Railway PostgreSQL Inventory

| Item | Status | Notes |
|---|---|---|
| Managed PostgreSQL | NOT PROVISIONED | Railway PostgreSQL add-on; provision in Module 101 |
| `DATABASE_URL` injection | Auto-injected by Railway PostgreSQL add-on | No manual config needed after add-on is created |
| Migration target | `backend/alembic.ini` + `backend/migrations/versions/` | 2 migration files: `0001_initial_schema`, `0002_add_password_hash` |
| Migration execution | `python backend/scripts/run_migrations.py` | Exits non-zero on failure; safe to run in start command |
| No DB-ready retry | `run_migrations.py` has no wait/retry loop | If Railway PostgreSQL starts after the backend, migration fails immediately; documented gap |
| Backup/PITR | Railway PostgreSQL provides automatic backups | Verify in Railway dashboard after provisioning |
| Local Docker DB | `docker-compose.postgres.yml` — local only | Must never be used in staging; DATABASE_URL must point to Railway add-on |
| No production DB | Production PostgreSQL does not exist yet | Staging DB is isolated from future production DB |
| Staging fake tenant strategy | NOT DEFINED — staging needs a fake clinic record and user | `seed_local_data.py` is local-only; staging needs equivalent (manual SQL or a staging-specific seed command) |
| `seed_local_data.py` | EXISTS — local-only with hardcoded local UUIDs | Must NOT run in staging (local UUIDs, local-dev password hash) |
| Blocker: staging seed | No staging seed/provisioning strategy defined | Gap: staging smoke requires at least one fake clinic + user record; documented for Module 103 |
| `POSTGRES_DB/USER/PASSWORD` | Not needed — Railway auto-manages; `DATABASE_URL` is the single connection string | Module 97 checklist includes these as optional reference |

---

## 5. Vercel Frontend Requirements Inventory

| Item | Current Repo Status | Required for Vercel? | Recommended Action | Blocker Level |
|---|---|---|---|---|
| Frontend root directory | `frontend/` — not at repo root | YES — Vercel must be told root is `frontend/` | Set **Root Directory** to `frontend` in Vercel project settings | **BLOCKER** |
| `package.json` | EXISTS at `frontend/package.json` | YES — Vercel reads this for framework detection | No action needed | NONE |
| Build command | `npm run build` → `next build` | YES — Vercel auto-detects from package.json | No action needed; Vercel uses `npm run build` by default | NONE |
| Output directory | `frontend/.next` (standard Next.js build output) | AUTO — Vercel manages `.next/` internally | No action needed; Vercel handles this natively | NONE |
| Framework detection | Next.js 14.2.3 | AUTO — Vercel auto-detects `next` package | No action needed | NONE |
| `output: 'standalone'` | NOT SET in `next.config.js` | NOT NEEDED for Vercel | No action needed; standalone is only for Docker/self-hosted | NONE |
| `vercel.json` | MISSING | NOT NEEDED — Vercel auto-detects Next.js 14 | No action needed unless custom rewrites/headers needed | NONE |
| `NEXT_PUBLIC_API_BASE_URL` | `frontend/.env.example` has placeholder | YES — must be set in Vercel project env vars | Set to staging Railway HTTPS URL in Vercel dashboard | **HIGH** |
| No backend secrets in frontend env | `NEXT_PUBLIC_*` vars are public (baked into browser bundle) | YES — no JWT secrets, DB passwords, or webhook secrets | Vercel frontend only gets `NEXT_PUBLIC_API_BASE_URL`; all secrets are backend-only | **HIGH** |
| `frontend/.gitignore` | MISSING | YES — `frontend/.next/`, `node_modules/`, `.env.local` untracked in git | Create `frontend/.gitignore` in Module 101 | MEDIUM |
| Login route | `frontend/app/login/` | AUTO — Vercel serves Next.js App Router routes | No action needed | NONE |
| Dashboard route | `frontend/app/dashboard/` | AUTO | No action needed | NONE |
| Static assets | No static assets beyond Next.js defaults | AUTO | No action needed | NONE |
| Install command | `npm install` (Vercel default) | AUTO — Vercel runs `npm install` before build | No action needed | NONE |
| Node version | Not pinned in `package.json` or `.nvmrc` | LOW risk — Vercel uses current LTS | Document; pin if build fails | LOW |

---

## 6. Cross-Platform URL/Domain Inventory

| Item | Status | Notes |
|---|---|---|
| Staging backend URL | Placeholder: `https://staging-api.up.railway.app` | Actual Railway URL assigned at service creation; update `FRONTEND_CORS_ORIGINS` and Vapi config |
| Staging frontend URL | Placeholder: `https://staging-app.vercel.app` | Actual Vercel URL assigned at project creation; update `FRONTEND_CORS_ORIGINS` |
| `FRONTEND_CORS_ORIGINS` | Must be set to exact Vercel staging URL | Backend Railway env var; no wildcard; no ngrok |
| `NEXT_PUBLIC_API_BASE_URL` | Must be set to exact Railway staging URL | Frontend Vercel env var; not a secret; baked into browser bundle |
| No wildcard CORS | `_cors_origins()` in `main.py` never returns `*` | Confirmed; no wildcard allowed |
| No ngrok in staging | ngrok is local-dev only | Any ngrok URL in staging env vars = immediate stop rule |
| HTTPS required | Both URLs must be HTTPS for cookie auth and Vapi | Railway and Vercel provide HTTPS by default on their subdomains |
| Cross-domain SameSite issue | `*.up.railway.app` ≠ `*.vercel.app` → different eTLD+1 | Browser fetch is cross-site; `SameSite=Lax` cookies will not send; `SameSite=None; Secure` required when cookie auth is implemented (Sprint 14 / post-M2) |

---

## 7. Migration/Seed Command Inventory

| Command | Location | Local Use | Staging Use | Notes |
|---|---|---|---|---|
| `python backend/scripts/run_migrations.py` | `backend/scripts/run_migrations.py` | YES | YES — runs in start command | Exits non-zero on failure; no retry loop |
| `alembic upgrade head` (direct) | Via `run_migrations.py` | YES | YES — called by `run_migrations.py` | `alembic.ini` in `backend/`; resolved from script location |
| `python backend/scripts/seed_local_data.py` | `backend/scripts/seed_local_data.py` | YES | **MUST NOT RUN** | Contains local-dev UUIDs and local-dev password hash; not staging-safe |
| `pytest backend/tests` | Repo root | YES | CI only — not a deploy command | 1946 tests; confirms app code correct before deploy |
| `python backend/scripts/smoke_vapi_appointment_intake.py` | `backend/scripts/` | YES (local smoke) | Partial — needs staging URL | Local smoke script; may need URL override for staging |
| `python backend/scripts/sign_webhook_payload.py` | `backend/scripts/` | YES (local signing) | YES — test n8n webhooks | Requires `INTERNAL_WEBHOOK_SECRET` |
| `python backend/scripts/db_smoke_test.py` | `backend/scripts/` | YES | Possibly staging | Tests DB connectivity; needs `DATABASE_URL` |
| `docker compose -f docker-compose.postgres.yml up -d` | Repo root | YES | **MUST NOT RUN** — local Docker only | Local-dev PostgreSQL only; staging uses Railway managed PostgreSQL |

**Staging seed gap:** Staging needs at least one fake clinic record and one fake clinic user
to run the 13-step smoke. Neither `seed_local_data.py` nor any staging-equivalent seed script
exists. Options:
- Manual SQL INSERT with a staging-specific fake clinic UUID (recommended for Module 103)
- A staging-safe seed script that reads from env (no hardcoded local UUIDs)

This gap is documented for Module 103 (Staging DB Migration/Seed Strategy).

---

## 8. `.gitignore` Coverage Inventory

### 8.1 Root `.gitignore` (EXISTS)

| Pattern | Covered |
|---|---|
| `__pycache__/` | YES |
| `*.py[cod]` | YES |
| `.pytest_cache/` | YES |
| `.DS_Store` | YES |
| `.env` | YES — covers root `.env` only |
| `.venv/` | YES |
| `venv/` | YES |

### 8.2 Gaps (items untracked but not ignored)

| Path | In `.gitignore`? | Risk | Recommended Fix |
|---|---|---|---|
| `backend/.env` | NO — root `.gitignore` covers `.env` at root only | **HIGH** — could commit local secrets | Add `backend/.env` to root `.gitignore` |
| `frontend/.env.local` | NO | **HIGH** — could commit staging/local API URL with token | Add `frontend/.env.local` to root `.gitignore` OR create `frontend/.gitignore` |
| `frontend/.next/` | NO — confirmed untracked in `git status` | MEDIUM — large build artifact | Add to root `.gitignore` or `frontend/.gitignore` |
| `frontend/node_modules/` | NO — confirmed untracked in `git status` | HIGH — thousands of files | Add to root `.gitignore` or `frontend/.gitignore` |
| `frontend/package-lock.json` | NO — confirmed untracked in `git status` | LOW — lockfile should ideally be committed | Commit or explicitly ignore; typically committed for reproducible builds |
| `frontend/next-env.d.ts` | NO — confirmed untracked in `git status` | LOW — Next.js generated type declaration | Add to `frontend/.gitignore` |

**Recommended resolution (Module 101):** Create `frontend/.gitignore` and update root
`.gitignore` to cover `backend/.env` and `frontend/.env.local`.

---

## 9. Vapi/n8n Config Inventory

| Item | Status | Notes |
|---|---|---|
| Vapi tool endpoint | `POST /vapi/tools/capture-appointment-request` | Route exists; no ngrok needed in staging |
| `vapi:tool` scope (singular) | Enforced in `require_vapi_tool_access` | `vapi:tools` plural returns HTTP 403 |
| Vapi machine auth headers | `X-Clinic-Ref`, `X-Vapi-Scopes: vapi:tool` | Machine-auth; no browser CORS dependency |
| `VAPI_WEBHOOK_SECRET` | Read from env; HMAC-SHA256 verification | Must match Vapi assistant configuration |
| Staging Vapi test assistant | NOT CREATED | Must create a test Vapi assistant pointing to staging Railway URL in Module 104 |
| n8n staging workflow | NOT ENABLED for initial staging | n8n is optional; not required for initial staging smoke |
| `N8N_WEBHOOK_SECRET` | Read from env; HMAC verification active | Set even if n8n disabled; `sign_webhook_payload.py` can generate test signatures |
| No browser CORS dependency | Vapi and n8n use server-to-server machine auth | No `FRONTEND_CORS_ORIGINS` dependency for Vapi/n8n paths |
| No auto-confirmation | `status='new'`, `action_required=True` hardcoded | No code path auto-confirms; stop rule if ever observed |

---

## 10. Required Config Files/Commands Summary

### 10.1 Existing and Usable As-Is

| File/Command | Location | Notes |
|---|---|---|
| `backend/scripts/run_migrations.py` | EXISTS | Runs `alembic upgrade head`; exits non-zero on failure |
| `backend/alembic.ini` | EXISTS | Reads `DATABASE_URL` from env; never exposes credentials |
| `backend/migrations/versions/` | EXISTS (2 files) | All committed; apply cleanly to local DB |
| `backend/app/main.py` (`backend.app.main:app`) | EXISTS | ASGI app entrypoint; reads PORT from env |
| `frontend/package.json` | EXISTS | `build: next build`; `start: next start`; Next.js 14.2.3 |
| `frontend/next.config.js` | EXISTS | No special config needed for Vercel |
| `backend/.env.example` | EXISTS | Documents all required backend env vars |
| `frontend/.env.example` | EXISTS | Documents `NEXT_PUBLIC_API_BASE_URL` |

### 10.2 Existing but Local-Only (must NOT be used in staging)

| File/Command | Notes |
|---|---|
| `docker-compose.postgres.yml` | Local Docker PostgreSQL only |
| `backend/scripts/seed_local_data.py` | Local-dev UUIDs and password hash; not staging-safe |
| `backend/.env.example` values | Placeholder values; not real secrets |
| `http://127.0.0.1:8000` (local backend URL) | Not used in staging; replaced by Railway HTTPS URL |

### 10.3 Missing and Required Before Staging Deploy

| Missing Item | Priority | Module to Create | Notes |
|---|---|---|---|
| `backend/requirements.txt` | **BLOCKER** | Module 101 | Railway Nixpacks cannot install packages without it |
| `Procfile` (or `railway.toml`) | **BLOCKER** | Module 101 | Railway needs explicit start command |
| `runtime.txt` (Python version) | HIGH | Module 101 | Pin Python 3.11 for Railway Nixpacks |
| `frontend/.gitignore` | MEDIUM | Module 101 | Cover `.next/`, `node_modules/`, `.env.local`, `next-env.d.ts` |
| Root `.gitignore` additions | MEDIUM | Module 101 | Add `backend/.env`, `frontend/.env.local` |
| Staging seed strategy | HIGH | Module 103 | Fake clinic + user provisioning for smoke |
| DB-ready retry in `run_migrations.py` | MEDIUM | Module 101 | Handle Railway PostgreSQL cold-start delay |

### 10.4 Not Needed

| Item | Reason |
|---|---|
| `vercel.json` | Vercel auto-detects Next.js 14; no custom config needed |
| `Dockerfile` | Railway uses Nixpacks; Vercel uses native Next.js build |
| `output: 'standalone'` in `next.config.js` | Needed for Docker/self-hosted only; not for Vercel |
| `nixpacks.toml` | Optional; Nixpacks auto-detects correctly if `requirements.txt` present |

---

## 11. Blockers Before Actual Staging Deploy Attempt

| # | Blocker | Level | Module |
|---|---|---|---|
| 1 | No `requirements.txt` — Railway cannot install Python packages | **BLOCKER** | Module 101 |
| 2 | No `Procfile` or `railway.toml` — Railway does not know the start command | **BLOCKER** | Module 101 |
| 3 | No Python version pin (`runtime.txt`) — Nixpacks uses undefined Python | HIGH | Module 101 |
| 4 | No staging seed/provisioning strategy — smoke cannot log in without a fake clinic user | HIGH | Module 103 |
| 5 | `frontend/.gitignore` missing — `frontend/.next/`, `node_modules/`, `.env.local` untracked | MEDIUM | Module 101 |
| 6 | Root `.gitignore` gaps — `backend/.env`, `frontend/.env.local` not explicitly covered | MEDIUM | Module 101 |
| 7 | No DB-ready retry in `run_migrations.py` — cold-start Railway PostgreSQL may cause transient fail | MEDIUM | Module 101 |
| 8 | No staging Vapi test assistant configured — Vapi smoke step cannot run | HIGH | Module 104 |
| 9 | No actual Railway service or Vercel project created yet | HIGH | Module 101/102 |
| 10 | Actual staging HTTPS URLs unknown until services are created | MEDIUM | Modules 101/102 |
| 11 | `FRONTEND_CORS_ORIGINS` value unknown until Vercel URL is assigned | MEDIUM | Module 102 |
| 12 | `sessionStorage` JWT acceptable for fake-data staging only — PHI blocker for production | (Known; documented) | M3 / Sprint 14 auth sprint |

---

## 12. Recommended Next Actions

### Module 101 — Railway Backend Deployment Prep

Create the minimum files needed to deploy the backend to Railway:
- `backend/requirements.txt` with pinned package versions (verified from pip show)
- `Procfile` at repo root with the complete start command
- `runtime.txt` with `python-3.11`
- `frontend/.gitignore` covering build artifacts and local env files
- Root `.gitignore` additions for `backend/.env` and `frontend/.env.local`
- Assess `run_migrations.py` DB-ready retry gap; add retry if straightforward
- Document Railway service creation steps (no actual service created in Module 101)

No actual Railway deployment in Module 101. No real secrets.

### Module 102 — Vercel Frontend Deployment Prep

- Document Vercel project creation steps (root directory = `frontend/`)
- Confirm Vercel auto-detects Next.js 14.2.3 correctly
- Confirm build command (`npm run build`) and output directory (`.next/`)
- Define `NEXT_PUBLIC_API_BASE_URL` placeholder (actual URL known after Module 101 service creation)
- No real Vercel project created in Module 102 unless trivial

### Module 103 — Staging DB Migration/Seed Strategy

- Define the staging fake clinic UUID and user provisioning strategy
- Confirm migration execution order at deploy time
- Define a minimal staging seed (SQL INSERT or staging-safe script) that creates exactly what the 13-step smoke requires
- Document what the staging DB must contain before smoke begins

### Module 104 — Staging Smoke Execution Evidence

- Execute the 13-step smoke runbook from Module 97
- Capture pass/fail evidence per step
- Record any failure and rollback actions taken

---

## 13. Non-Goals

- No deployment execution in this module
- No production launch — production PHI launch remains NO-GO
- No real patient data
- No auth/session hardening implementation (planned Sprint 14, post-M2)
- No Fabel 5 / frontend UX sprint
- No appointment workflow expansion
- No actual Railway service or Vercel project creation
- No real staging secrets or production secrets
