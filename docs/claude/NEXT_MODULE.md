# Sprint 14 / Module 101 — Railway Backend Deployment Prep

Status: pending Module 100 review.

## Context

Module 100 (Staging Deployment Config File Inventory) identified two hard blockers before
the Railway backend can deploy:

1. **No `backend/requirements.txt`** — Railway's Nixpacks cannot install Python packages
2. **No `Procfile` (or `railway.toml`)** — Railway does not know the start command

Additional high-priority gaps:
- No `runtime.txt` — Python version not pinned for Nixpacks
- No `frontend/.gitignore` — `frontend/.next/`, `node_modules/`, `.env.local`, `next-env.d.ts` untracked
- Root `.gitignore` does not cover `backend/.env` or `frontend/.env.local`
- `run_migrations.py` has no DB-ready retry loop (Railway PostgreSQL may start after backend)

Module 101 resolves the backend deployment blockers and `.gitignore` gaps. No actual
Railway deployment. No real secrets. Minimal code/config additions only.

## Scope

### 1. Read and audit current state

Read:
- `docs/deployment/STAGING_DEPLOYMENT_CONFIG_FILE_INVENTORY.md` — full blocker list
- `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` — start command reference
- `backend/scripts/run_migrations.py` — current migration runner
- `backend/app/main.py` — import path and PORT binding confirmation
- `backend/.env.example` — env var reference
- `.gitignore` — current coverage
- `frontend/package.json` — build/start commands

### 2. Create or update files

#### 2.1 Create `backend/requirements.txt`

Must include all pinned packages the backend uses (from `pip show` inspection in Module 100):
- `fastapi==0.138.2`
- `uvicorn[standard]==0.49.0`
- `asyncpg==0.31.0`
- `alembic==1.18.5`
- `pydantic==2.13.4`
- `PyJWT==2.4.0`
- `cryptography==42.0.2`
- `bcrypt==3.2.0`
- `httpx==0.26.0`

Notes:
- Backend uses `PyJWT` directly for JWT (not `python-jose`)
- Backend uses `bcrypt` directly for password hashing (not `passlib`)
- `uvicorn[standard]` installs uvloop and httptools for production performance
- `httpx` is used by FastAPI's TestClient (test dependency; include for Railway build parity)

#### 2.2 Create `Procfile` at repo root

```
web: python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Notes:
- Must run from repo root (so `backend.app.main:app` import path resolves)
- `$PORT` is auto-injected by Railway
- `run_migrations.py` exits non-zero on failure → `&&` halts uvicorn start on migration failure
- Process type is `web` (Railway expects this for HTTP services)

#### 2.3 Create `runtime.txt` at repo root

```
python-3.11
```

Notes:
- Pins Python 3.11 for Railway's Nixpacks auto-detection
- Prevents Railway from using an unexpected Python version

#### 2.4 Update `.gitignore`

Add to root `.gitignore`:
```
# Backend local env
backend/.env

# Frontend local env and build artifacts
frontend/.env.local
frontend/.next/
frontend/node_modules/
frontend/package-lock.json
frontend/next-env.d.ts
```

Notes:
- `frontend/package-lock.json` — typically committed for reproducible builds; include in
  .gitignore only if intentionally not committing; document the choice
- After this update, `git status` should show no untracked files that risk leaking secrets

#### 2.5 Assess `run_migrations.py` DB-ready retry

Inspect whether Railway starts the PostgreSQL add-on before the backend service. If
Railway guarantees PostgreSQL is ready before the backend starts (via healthcheck
dependency), no retry is needed. If not, document the risk and optionally add a
simple retry loop.

**Action:** Document the Railway PostgreSQL startup order in the inventory update.
Add a retry loop only if confirmed necessary. Do not add unnecessary complexity.

### 3. Create `docs/deployment/STAGING_CONFIG_FILE_INVENTORY.md` updates (if needed)

Update the inventory to reflect the new files created in this module.

### 4. Static contract tests

Create `backend/tests/test_railway_backend_deployment_prep_contract.py`:
- `backend/requirements.txt` exists
- `requirements.txt` mentions fastapi
- `requirements.txt` mentions uvicorn
- `requirements.txt` mentions asyncpg
- `requirements.txt` mentions alembic
- `requirements.txt` mentions pydantic
- `requirements.txt` mentions PyJWT
- `requirements.txt` mentions bcrypt
- `Procfile` exists at repo root
- `Procfile` mentions uvicorn
- `Procfile` mentions backend.app.main
- `Procfile` mentions $PORT or PORT
- `Procfile` mentions run_migrations
- `runtime.txt` exists at repo root
- `runtime.txt` mentions python-3.11 or python-3
- `.gitignore` covers `backend/.env`
- `.gitignore` covers `frontend/.env.local`
- `.gitignore` covers `frontend/.next/`
- `.gitignore` covers `frontend/node_modules/`
- No obvious real secrets in any new file

### 5. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 101
- `docs/claude/NEXT_MODULE.md` — Sprint 14 / Module 102: Vercel Frontend Deployment Prep

## What not to do

- Do not create a real Railway service or Vercel project
- Do not add real production secrets
- Do not implement httpOnly cookie auth
- Do not change backend/frontend runtime behavior
- Do not change CORS implementation
- Do not change DB schema or migration files
- Do not start Fabel 5/UX sprint

## Acceptance

- `backend/requirements.txt` created with all pinned dependencies
- `Procfile` created at repo root with correct start command
- `runtime.txt` created at repo root with Python 3.11
- `.gitignore` updated to cover all identified gaps
- Contract tests pass
- Full test suite passes (1987/1987 minimum)
- Commit: `Sprint 14 / Module 101 — Railway backend deployment prep`
