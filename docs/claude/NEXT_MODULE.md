# Sprint 14 / Module 102 — Vercel Frontend Deployment Prep

Status: pending Module 101 review.

## Context

Module 101 resolved the Railway backend deployment blockers:
- `backend/requirements.txt` created with 7 pinned runtime deps
- `Procfile` created (web: uvicorn; migrations are a separate manual predeploy step)
- `runtime.txt` created (python-3.11)
- `.gitignore` updated to cover `backend/.env`, `frontend/.env.local`, `frontend/.next/`, `frontend/node_modules/`

The remaining staging deployment blockers on the frontend side:
- Vercel project not yet created
- `NEXT_PUBLIC_API_BASE_URL` not yet set (depends on Railway URL from Module 101 execution)
- `FRONTEND_CORS_ORIGINS` not yet set in Railway (depends on Vercel URL)
- `frontend/.gitignore` — covered by root `.gitignore` additions in Module 101; verify coverage

Module 102 prepares Vercel frontend deployment documentation. No actual Vercel project.
No real secrets. No UX/Fabel 5 work.

## Scope

### 1. Read and audit current state

Read:
- `docs/deployment/STAGING_DEPLOYMENT_CONFIG_FILE_INVENTORY.md` — Vercel section findings
- `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` — Railway URL placeholder
- `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` — frontend env vars
- `frontend/package.json` — build/start commands
- `frontend/next.config.js` — output config
- `frontend/app/` — routes to verify (login, dashboard)
- `frontend/lib/api.ts` — NEXT_PUBLIC_API_BASE_URL usage
- `.gitignore` — verify frontend coverage from Module 101

### 2. Create `docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md`

Sections:
1. **Purpose** — Vercel frontend prep; no deployment; fake/non-PHI only; PHI no-go
2. **Selected Vercel approach** — Next.js 14.2.3 auto-detection; no vercel.json needed
3. **Vercel project settings** — root directory (`frontend`); framework preset (Next.js auto); build command (`npm run build`); output directory (`.next/` managed by Vercel); install command (`npm install`)
4. **Required Vercel environment variable** — `NEXT_PUBLIC_API_BASE_URL` = Railway staging HTTPS URL (placeholder until Railway URL is known); public variable; not a secret; baked into browser bundle
5. **No backend secrets in frontend env** — NEXT_PUBLIC_* vars are public; no JWT secrets, DB passwords, or webhook secrets may appear here
6. **CORS dependency** — Railway `FRONTEND_CORS_ORIGINS` must be set to the exact Vercel URL after the Vercel project is created
7. **Frontend routes** — login (`/login`); dashboard (`/dashboard`); auth guard (client-side only); sessionStorage JWT acceptable for fake-data staging
8. **Build and deploy verification checklist** — `npm run build` passes locally; no TypeScript errors; no missing env var at build time (NEXT_PUBLIC_API_BASE_URL can be placeholder during build)
9. **`.gitignore` coverage** — verify Module 101 additions cover frontend artifacts
10. **Blockers remaining** — Vercel project not created; Railway URL not yet known; FRONTEND_CORS_ORIGINS not yet set; staging seed not defined
11. **Recommended next actions** — Module 103 (Staging DB Migration/Seed Strategy)
12. **Non-goals**

### 3. Verify `npm run build` passes locally

Run `npm run build` in `frontend/` to confirm the frontend builds cleanly with the
current source. Document the result. Do not fix build errors if they exist — report them
as blockers.

### 4. Static contract tests

Create `backend/tests/test_vercel_frontend_deployment_prep_contract.py`:
- Vercel prep doc exists
- Doc mentions Vercel
- Doc mentions frontend root directory (`frontend`)
- Doc mentions Next.js auto-detection
- Doc mentions `npm run build`
- Doc mentions `NEXT_PUBLIC_API_BASE_URL`
- Doc mentions no backend secrets in frontend env
- Doc mentions `FRONTEND_CORS_ORIGINS`
- Doc mentions fake/non-PHI staging only
- Doc mentions no deployment executed
- Doc mentions production PHI no-go
- Doc mentions sessionStorage JWT acceptable for fake-data staging
- Doc mentions blockers remaining
- Doc mentions Module 103
- No obvious real secrets in doc

### 5. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 102
- `docs/claude/NEXT_MODULE.md` — Sprint 14 / Module 103: Staging DB Migration/Seed Strategy

## What not to do

- Do not create a real Vercel project
- Do not add real production or staging secrets
- Do not implement httpOnly cookie auth
- Do not change backend/frontend runtime behavior
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint
- Do not change DB schema or migration files

## Acceptance

- `docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md` created
- Contract tests pass
- Full test suite passes (2024/2024 minimum)
- Commit: `Sprint 14 / Module 102 — Vercel frontend deployment prep`
