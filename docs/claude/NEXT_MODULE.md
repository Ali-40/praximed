# Sprint 14 / Module 100 — Staging Deployment Config File Inventory

Status: pending Architecture Checkpoint 13 review.

## Context

Architecture Checkpoint 13 has approved:
- Fake-data staging deployment attempt: GO
- Actual staging deployment attempt: GO
- Production PHI launch: NO-GO (all 12 blockers open)

Before creating real Railway or Vercel projects, inspect the repository for every
deployment-relevant config file, start command, build command, and output assumption.
The dry-run checklist (Module 97) assumes certain commands and file paths exist — this
module verifies those assumptions against the actual repo state and documents what is
present, what is missing, and what must be created before deployment.

Module 100 is docs-first. No deployment execution. No real secrets. No runtime code changes
unless a missing trivial config file (e.g., `railway.toml`) is added.

## Scope

### 1. Inspect deployment config needs

Read and inventory:

**Backend:**
- `backend/scripts/run_migrations.py` — does it exist? What does it do? Does it exit non-zero on failure?
- Is there a `Procfile` or `railway.toml` in the repo root or backend directory?
- What is the exact start command that Railway needs? (`python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`)
- Does Railway need a `railway.toml` config file to know the start command?
- What Python version does the backend require? Is there a `runtime.txt` or `pyproject.toml` version spec?
- What is `backend/requirements.txt` or `backend/pyproject.toml`? Are all dependencies pinned?

**Frontend:**
- `frontend/package.json` — what are the `build` and `start` scripts?
- What is the `next.config.js` output setting? Does it need `output: 'standalone'` for Vercel?
- Does Vercel's auto-detection handle Next.js 14.2.3 with `frontend/` as root? What is the Vercel root directory setting?
- What is the build output directory? (`frontend/.next`)
- Is there a `vercel.json` in the frontend directory or repo root?
- Does the frontend `.gitignore` cover `frontend/.next/`, `frontend/node_modules/`?

**Migrations:**
- `backend/scripts/run_migrations.py` — does it run `alembic upgrade head`? Does it handle connection retries?
- What happens if the database is not ready when the backend starts? Is there a retry loop?
- What Alembic version is installed? Are all migration files committed?

**`.gitignore`:**
- Does `.gitignore` cover `backend/.env`, `frontend/.env.local`, `frontend/node_modules/`, `frontend/.next/`, `frontend/package-lock.json`?

### 2. Create `docs/deployment/STAGING_CONFIG_FILE_INVENTORY.md`

Sections:
1. **Purpose** — inventory what exists vs. what is needed for Railway/Vercel staging deploy
2. **Backend start command** — exact command; source (current recommendation from Module 97)
3. **Railway config requirements** — does Railway auto-detect Python? Does it need `railway.toml`?
4. **`run_migrations.py` review** — what it does; whether it exits non-zero on failure; whether it handles DB-not-ready
5. **Python version and dependencies** — version spec; `requirements.txt` or `pyproject.toml`; any missing prod deps
6. **Frontend build command** — `npm run build`; output directory; Next.js version
7. **Vercel config requirements** — root directory setting; does it need `vercel.json`?
8. **`.gitignore` coverage** — what is covered; any gaps that could leak secrets or build artifacts
9. **Env var injection points** — where each var is consumed; confirms Module 96 matrix is complete
10. **Gaps and action items** — list of missing files or changes needed before deployment
11. **Module 101 next step**

### 3. Static contract tests

Create `backend/tests/test_staging_config_file_inventory_contract.py`:
- Inventory doc exists
- Mentions backend start command
- Mentions `run_migrations.py`
- Mentions Railway config
- Mentions Vercel config
- Mentions frontend build command
- Mentions `.gitignore`
- Mentions Python version or dependencies
- Mentions gaps or action items
- Mentions Module 101
- No obvious real secrets

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 100
- `docs/claude/NEXT_MODULE.md` — Sprint 14 / Module 101: Railway Backend Deployment Prep

## What not to do

- Do not execute any deployment
- Do not provision real Railway or Vercel projects
- Do not add real production secrets
- Do not implement the httpOnly cookie auth (that is Module 105+ after staging smoke evidence)
- Do not change backend/frontend runtime code
- Do not start the Fabel 5/UX sprint

## Acceptance

- `docs/deployment/STAGING_CONFIG_FILE_INVENTORY.md` created
- Contract tests pass
- Full test suite passes (1946/1946 minimum)
- Commit: `Sprint 14 / Module 100 — Staging deployment config file inventory`
