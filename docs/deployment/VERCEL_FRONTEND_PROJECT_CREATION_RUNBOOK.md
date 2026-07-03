# Vercel Frontend Project Creation Runbook — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 15 / Module 107
**Status:** Planning only — no deployment executed by Claude in this module

---

## 1. Purpose

This is a human-executable step-by-step guide for creating the Vercel frontend project
for PraxisMed fake-data staging. The developer follows this runbook manually in the
Vercel dashboard.

**What this runbook is:**
- Exact steps for importing the PraxisMed frontend into Vercel
- The required project settings, environment variable, and evidence to capture
- A failure triage reference for common Vercel setup issues

**What this runbook is not:**
- A deployment executed by Claude — no Vercel API calls are made here
- A production launch plan — production PHI launch remains NO-GO
- A UI/Fabel 5 redesign — no frontend code is changed in this module
- A Railway backend guide — that is Module 105/106
- A document containing real secrets

Staging uses fake/non-PHI data only. No deployment is executed in this module.
No real patient data. No production secrets. No auth/session changes.

---

## 2. Current Repo Readiness

The repository has all files Vercel requires to build and serve the Next.js frontend.
No further code changes are needed before creating the Vercel project.

| Item | Path | Status | Notes |
|---|---|---|---|
| Frontend directory | `frontend/` | READY | Root of the Next.js app; must be set as Vercel root directory |
| `package.json` | `frontend/package.json` | READY | `"build": "next build"`, `"start": "next start"`, Next.js 14.2.3 |
| Next.js app router | `frontend/app/` | READY | `page.tsx`, `login/page.tsx`, `dashboard/page.tsx` |
| Next.js config | `frontend/next.config.js` | READY | Empty config; no `output: 'standalone'`; no `vercel.json` needed |
| Environment example | `frontend/.env.example` | READY | Documents `NEXT_PUBLIC_API_BASE_URL` as the only required var |
| API client | `frontend/lib/api.ts` | READY | Reads `process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000'` at build time |
| Auth helper | `frontend/lib/auth.ts` | READY | `sessionStorage` JWT; acceptable for fake-data staging only |
| Login route | `frontend/app/login/page.tsx` | READY | Login form; calls `POST /auth/login` |
| Dashboard route | `frontend/app/dashboard/page.tsx` | READY | Protected; redirects to `/login` if not authenticated |
| Root redirect | `frontend/app/page.tsx` | READY | Redirects to `/login` or `/dashboard` |
| `.gitignore` coverage | Root `.gitignore` | READY | `frontend/.next/`, `frontend/node_modules/`, `frontend/.env.local` excluded |
| Vercel prep doc | `docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md` | READY | Settings confirmed in Module 102 |
| Backend tests | `backend/tests/` | READY | 2160/2160 passed as of Module 106 |

**`NEXT_PUBLIC_API_BASE_URL` is a build-time variable** — it is baked into the compiled
JavaScript bundle at build time. Changing it requires a Vercel redeploy, not just a
server restart.

---

## 3. Preconditions for the Developer

Verify all of the following before starting the Vercel project creation steps:

### 3.1 Account and Access

- [ ] Vercel account created (https://vercel.com — personal or team account)
- [ ] GitHub account connected to Vercel (Vercel needs read access to the repo)
- [ ] PraxisMed GitHub repository accessible from Vercel
- [ ] Railway backend staging URL is known (from Module 105 evidence) or a placeholder is accepted for the initial build

### 3.2 Railway Backend URL Dependency

The `NEXT_PUBLIC_API_BASE_URL` env var must be set to the Railway backend HTTPS URL
before the first Vercel build. If the Railway backend URL is not yet known:

- Option A: Set `NEXT_PUBLIC_API_BASE_URL` to a placeholder (e.g., `https://placeholder.up.railway.app`) for the first Vercel build, then update it and redeploy once the Railway URL is confirmed
- Option B: Complete Module 105 (Railway backend service creation) first to obtain the URL

**If the placeholder option is used**, API calls from the deployed frontend will fail until
the env var is updated and a redeploy is triggered. This is acceptable and documented.

### 3.3 Data Safety Check

- [ ] Confirm no real patient data will be visible in the staging frontend
- [ ] Confirm no backend secrets will be placed in Vercel environment variables
- [ ] Confirm the Vercel frontend will not be configured with a production custom domain

---

## 4. Vercel Project Creation Steps

### Step 4.1 — Create a New Vercel Project

1. Log in to https://vercel.com
2. Click **Add New…** → **Project**
3. Choose **Import Git Repository**
4. Authorize Vercel to access your GitHub organization/account if prompted
5. Search for and select the PraxisMed repository

### Step 4.2 — Set the Root Directory

**This is the most critical setting.** Without it, Vercel will try to build from the
repo root, fail to find `package.json`, and refuse to deploy.

In the project configuration screen:
1. Under **Root Directory**, click **Edit** or the folder icon
2. Set to: `frontend`
3. Confirm the path shows `frontend/` in the preview

Vercel will now resolve all build commands relative to `frontend/`.

### Step 4.3 — Configure Framework and Build Settings

After setting the root directory, Vercel will auto-detect Next.js 14.2.3 from
`frontend/package.json`. Confirm or set:

| Setting | Value | Notes |
|---|---|---|
| **Framework Preset** | Next.js | Auto-detected from `next` package in `package.json`; confirm it is set |
| **Install Command** | `npm install` (Vercel default) | No override needed |
| **Build Command** | `npm run build` (Vercel default for Next.js) | Resolves to `next build` per `package.json` scripts |
| **Output Directory** | `.next` (Vercel manages automatically) | Do NOT override; Vercel handles Next.js output natively |
| **Node.js Version** | Vercel default LTS (18+) | Next.js 14.2.3 supports Node 18+; Vercel's default is compatible |

**Do not** set `output: 'standalone'` in `next.config.js` — that setting is for
Docker/self-hosted deploys only; Vercel handles the output directory automatically.

**No `vercel.json` is needed** — Vercel auto-detects Next.js 14.2.3 without a custom
configuration file.

### Step 4.4 — Set the Deployment Branch

Confirm the deployment branch:
- Set to `master` (the current working branch)
- Vercel will deploy on push to this branch if auto-deploy is enabled

### Step 4.5 — Do Not Attach a Custom Domain Yet

Do not configure a custom production domain at this stage. Vercel will assign a
`*.vercel.app` subdomain automatically. The staging URL will look like:
`https://praximed-frontend-staging.vercel.app` (or similar — assigned by Vercel).

---

## 5. Required Vercel Environment Variables

Set the following in the Vercel project → **Settings** → **Environment Variables** panel
**before the first deploy** (or trigger a redeploy after setting if the first build has
already run).

| Variable | Value (placeholder) | Secret? | Scope | Required Before First Build? |
|---|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `<railway-staging-backend-https-url>` — the Railway HTTPS URL from Module 105 | **NO** — public build-time variable; baked into browser bundle | Production + Preview | YES — if absent, frontend falls back to `http://127.0.0.1:8000` and all API calls fail in the browser |

**How to set in Vercel:**
1. Open the Vercel project → **Settings** → **Environment Variables**
2. Click **Add**
3. Name: `NEXT_PUBLIC_API_BASE_URL`
4. Value: the Railway backend HTTPS URL (e.g., `https://praxismed-backend-staging.up.railway.app`)
5. Scope: select **Production** and **Preview**
6. Click **Save**
7. Trigger a new deployment (env var changes require a Vercel redeploy — the value is baked at build time)

**`NEXT_PUBLIC_API_BASE_URL` is NOT a secret.** It is embedded in the compiled JavaScript
bundle and visible to any browser inspector. It is a public URL, not a credential.

**After changing `NEXT_PUBLIC_API_BASE_URL`**, a new Vercel deployment must be triggered
for the change to take effect. Vercel does not hot-reload build-time variables.

### 5.1 Forbidden Vercel Environment Variables

The following must NEVER appear in Vercel frontend environment variables. `NEXT_PUBLIC_*`
variables are baked into the browser bundle and visible to anyone who inspects the
JavaScript source.

| Forbidden Variable | Why |
|---|---|
| `DATABASE_URL` | Backend-only; PostgreSQL credentials must never reach the browser |
| `JWT_SECRET_KEY` | Backend-only; HMAC signing secret; exposing it allows forged JWTs |
| `VAPI_WEBHOOK_SECRET` | Backend-only; HMAC verification key for Vapi webhooks |
| `N8N_WEBHOOK_SECRET` | Backend-only; HMAC verification key for n8n webhooks |
| `INTERNAL_WEBHOOK_SECRET` | Backend-only; internal webhook HMAC key |
| `POSTGRES_PASSWORD` | Backend-only; database credential |
| Any `openssl rand -hex 32` generated value | Backend secrets; never go to the browser |

---

## 6. Frontend/Backend URL Wiring

The staging topology requires three URL values to be set in the correct order:

| Step | Action | Required For |
|---|---|---|
| 1 | Railway backend deployed → Railway HTTPS URL known | Setting `NEXT_PUBLIC_API_BASE_URL` in Vercel |
| 2 | `NEXT_PUBLIC_API_BASE_URL` set in Vercel → first Vercel build | Frontend can call Railway API |
| 3 | Vercel deployed → Vercel HTTPS URL known | Setting `FRONTEND_CORS_ORIGINS` on Railway |
| 4 | `FRONTEND_CORS_ORIGINS` set on Railway (exact Vercel URL) → Railway restarts | CORS preflight succeeds from browser |
| 5 | CORS verified → login smoke proceeds | Module 108 |

**No wildcard CORS.** `FRONTEND_CORS_ORIGINS` on the Railway backend must be the exact
Vercel URL (e.g., `https://praximed-frontend-staging.vercel.app`). The backend's
`_cors_origins()` function never returns `*`.

**No ngrok.** Neither `NEXT_PUBLIC_API_BASE_URL` nor `FRONTEND_CORS_ORIGINS` should
contain ngrok URLs. Ngrok is local-dev only.

**HTTPS required.** Both Railway and Vercel provide HTTPS on their default subdomains.
Do not use plain HTTP URLs in either env var.

**Setting `FRONTEND_CORS_ORIGINS` on Railway** (Module 108 task, after Vercel URL is known):
1. Open Railway backend service → Variables panel
2. Add `FRONTEND_CORS_ORIGINS` = exact Vercel HTTPS URL (no trailing slash)
3. Railway auto-restarts; backend picks up new CORS origins

---

## 7. First Vercel Deploy Expectations

| Phase | Expected | If Different |
|---|---|---|
| Build: `npm install` | Installs Next.js 14.2.3 and TypeScript deps from `frontend/package.json` | Build fails → check root directory setting; see Section 10 |
| Build: `next build` | Compiles App Router pages; TypeScript strict mode must pass | TypeScript errors → fix before redeploy; see Section 10 |
| Build: `NEXT_PUBLIC_API_BASE_URL` baked in | URL is embedded in the compiled JS bundle | If env var not set, falls back to `http://127.0.0.1:8000`; API calls will fail in browser |
| Deploy: Vercel URL assigned | `https://<project-name>.vercel.app` | Displayed in Vercel dashboard after first deploy |
| `/` redirect | Redirects to `/login` or `/dashboard` | Expected App Router behavior |
| `/login` loads | Login form renders; no backend call on load | Login form is a static-rendered component |
| API call from login form | `POST https://<railway-backend-url>/auth/login` | If Railway URL not set, calls `http://127.0.0.1:8000` — fails in browser |
| CORS on first API call | May fail if `FRONTEND_CORS_ORIGINS` not yet set on Railway | Expected at this stage — set after capturing Vercel URL; Module 108 |

**A first deploy where `/login` loads but API calls fail due to CORS or wrong URL is a
successful partial deploy.** It confirms the Next.js build and Vercel serving work. The
API integration is completed in Module 108.

---

## 8. Browser Smoke After Vercel Deploy

Run these checks after the Vercel frontend is deployed and before proceeding to Module 108:

| Check | Expected | Status |
|---|---|---|
| Open `https://<vercel-url>` in browser | Redirects to `/login` | Verify URL |
| `/login` page renders | Login form visible; email/password/clinic ID fields | Screenshot |
| Browser network tab: no JavaScript errors | Clean console | Inspect browser console |
| Browser network tab: API URL in outbound requests | Should point to Railway staging HTTPS URL, not `localhost` | Verify `NEXT_PUBLIC_API_BASE_URL` was set correctly |
| CORS preflight | May fail at this stage if `FRONTEND_CORS_ORIGINS` not yet set on Railway | Expected — resolved in Module 108 |
| Login attempt with fake staging user | May fail if CORS not yet resolved | Expected — resolved in Module 108 |
| No real patient data visible | No real names, phone numbers, or medical records | Always enforced |

---

## 9. Evidence to Capture

Record the following after the Vercel project is created and the first deploy completes.
No secret values; no sensitive data.

| Evidence Item | Value to Record | Notes |
|---|---|---|
| Vercel project name | e.g., `praximed-frontend-staging` | From Vercel dashboard |
| Vercel deployment URL | `https://<project-name>.vercel.app` | The public HTTPS URL assigned by Vercel — needed for Module 108 `FRONTEND_CORS_ORIGINS` |
| Source branch | `master` | Confirm in Vercel project settings |
| Commit SHA deployed | Full SHA from Vercel deployment log | Confirms exact code version |
| Build status | Success / Failure | From Vercel deployment log |
| Root directory confirmed | `frontend` | From Vercel project settings |
| Framework preset confirmed | Next.js | From Vercel project settings |
| Build command confirmed | `npm run build` | From Vercel project settings |
| `NEXT_PUBLIC_API_BASE_URL` name set | Confirmed (name only; not value) | From Vercel Variables panel |
| `/login` HTTP status | 200 | Browser or curl |
| `/login` renders correctly | Login form visible | Browser screenshot |
| API URL in outbound requests | Points to Railway backend HTTPS URL | Browser network tab |
| Any CORS errors | Note if present | Expected until `FRONTEND_CORS_ORIGINS` set in Module 108 |
| Build log snippet (sanitized) | First few lines of build output | No secret values in snippet |

---

## 10. Failure Triage

| Symptom | Likely Cause | Where to Inspect | Safe Next Action |
|---|---|---|---|
| Build fails: `No package.json found` | Root directory not set to `frontend/` | Vercel project settings → Root Directory | Set Root Directory to `frontend`; trigger redeploy |
| Build fails: `Cannot find module 'next'` | Root directory wrong; `frontend/node_modules/` not installed from correct location | Vercel build log | Confirm root is `frontend`; Vercel installs deps from that directory |
| Build fails: TypeScript errors | Code has strict-mode type errors | Vercel build log | Fix TypeScript errors; commit; redeploy |
| Build fails: `next build` exit non-zero | Various — missing env var (unlikely for Next.js build), TypeScript error | Vercel build log | Read exact error; do not patch around it |
| `/login` shows 404 | App Router pages not found; wrong root directory | Browser; Vercel build log | Confirm root is `frontend`; re-check build output |
| API calls go to `http://127.0.0.1:8000` | `NEXT_PUBLIC_API_BASE_URL` not set in Vercel before build | Browser network tab | Set env var in Vercel Variables panel; trigger redeploy (env var change requires rebuild) |
| API calls fail with network error | Railway backend not yet running; or wrong Railway URL in `NEXT_PUBLIC_API_BASE_URL` | Browser network tab; Railway dashboard | Confirm Railway backend is deployed and `/health` returns 200 |
| CORS error in browser | `FRONTEND_CORS_ORIGINS` not yet set on Railway backend | Browser console | Expected at this stage — set after capturing Vercel URL; see Module 108 |
| Login fails: 401 | Staging fake user not yet provisioned in DB | Browser network tab | Complete Module 106 (provisioning) before login smoke |
| Env var changed but old value persists | Build-time env var change requires a new Vercel deployment | Vercel Deployments tab | Trigger a new deployment after env var change |

---

## 11. Stop Rules

Stop Vercel frontend setup immediately if any of the following are observed:

| Stop Rule | Trigger |
|---|---|
| Vercel asks for backend secrets in frontend env | Any prompt or suggestion to add `DATABASE_URL`, `JWT_SECRET_KEY`, or other backend secrets to Vercel Variables |
| Production custom domain is being configured | Any attachment of a real production domain to the staging Vercel project |
| Real patient data appears in any screenshot or log | Any real name, phone number, DOB, or medical record |
| Secrets appear in build logs or screenshots | Any secret value visible in Vercel build output or browser inspector |
| Build or deploy requires runtime frontend code changes | The repo is ready as-is; if Vercel cannot build without a code change, diagnose the misconfiguration |
| Frontend `NEXT_PUBLIC_API_BASE_URL` points to a production API | The staging frontend must only call the staging Railway API |
| Wildcard CORS is proposed | `FRONTEND_CORS_ORIGINS` on Railway must be the exact Vercel URL; `*` is never acceptable |

---

## 12. Result States

| State | Meaning |
|---|---|
| **PASS** | Vercel project created; build/deploy succeeded; `/login` loads at Vercel HTTPS URL; `NEXT_PUBLIC_API_BASE_URL` set to Railway staging URL; sanitized evidence captured; Vercel URL recorded for Module 108 `FRONTEND_CORS_ORIGINS` update |
| **BLOCKED/PENDING** | Vercel project not yet created; or first build not yet triggered; or evidence not yet available |
| **FAIL** | Vercel project creation or build was attempted and failed with a documented error that blocks further progress |

**Current result: BLOCKED/PENDING** — Vercel frontend project has not yet been created
and deployment evidence has not been provided. See `VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md`
for the current evidence status.

---

## 13. What This Runbook Does Not Cover

| Topic | Covered In |
|---|---|
| Railway backend service creation | Module 105 |
| Railway PostgreSQL provisioning and migration | Module 106 |
| Setting `FRONTEND_CORS_ORIGINS` on Railway after Vercel URL is known | Module 108 |
| CORS preflight verification | Module 108 |
| Vapi test assistant staging URL configuration | Module 108 |
| n8n staging workflow | Module 108 |
| Full staging smoke execution | Module 109 |
| Auth/session hardening (httpOnly cookie) | Post-smoke; Sprint 15 |
| UI/Fabel 5 frontend redesign | Deferred |
| Production launch | Production PHI remains NO-GO |

---

## 14. Recommended Next Step — Module 108

**Sprint 15 / Module 108 — Staging Environment Wiring Evidence**

After completing this runbook and capturing the Vercel HTTPS URL:

1. Set `FRONTEND_CORS_ORIGINS` on Railway backend to the exact Vercel HTTPS URL
2. Trigger Railway backend restart (or redeploy) to pick up the new CORS origin
3. Verify CORS preflight: `OPTIONS /auth/login` from Vercel origin returns correct headers
4. Configure Vapi test assistant staging tool URL to the Railway backend URL
5. Run the login smoke step with `doctor.staging@praximed.test`
6. Document all environment wiring evidence

Module 108 covers all of these steps with evidence templates and stop rules.
