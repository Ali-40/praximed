# Vercel Frontend Deployment Prep — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 14 / Module 102
**Status:** Planning and prep only — no deployment executed in this module

---

## 1. Purpose

This document defines the Vercel frontend deployment configuration for PraxisMed staging.
It records the recommended Vercel project settings, the required environment variable, the
frontend/backend URL contract, and the remaining blockers before an actual Vercel deploy.

**What this document is:**
- A reference for the actual Vercel project creation (a future deployment module)
- A record of the Vercel configuration choices made in Module 102
- The frontend-specific section of the staging deployment preparation sequence

**What this document is not:**
- A deployment execution (no Vercel project is created in this module)
- A production launch plan (production PHI launch remains NO-GO)
- An auth/session hardening implementation (that is Sprint 14, post-M2 smoke evidence)
- A Fabel 5 / frontend UX redesign (deferred)
- A document containing real secrets

Staging uses fake/non-PHI data only. No deployment is executed in this module.
No Fabel 5/UX work. No appointment workflow expansion.

---

## 2. Current Frontend Inventory

Actual structure as of Module 102 inspection:

| Item | Discovered Value | Notes |
|---|---|---|
| Frontend root path | `frontend/` at repo root | Not the repo root itself |
| Next.js version | 14.2.3 (from `frontend/package.json` dependencies) | Vercel auto-detects Next.js |
| App Router | YES — `frontend/app/` directory with App Router convention | Next.js 13+ App Router |
| Build script | `"build": "next build"` | Invoked via `npm run build` |
| Dev script | `"dev": "next dev"` | Local development only |
| Start script | `"start": "next start"` | Runs compiled Next.js; Vercel manages this internally |
| Lint script | `"lint": "next lint"` | Not required for deploy |
| `frontend/.env.example` | EXISTS — documents `NEXT_PUBLIC_API_BASE_URL` placeholder | Copy to `.env.local` for local dev |
| `frontend/next.config.js` | EXISTS — empty config object; no `output` setting | Default Next.js output; no standalone mode |
| `frontend/tsconfig.json` | EXISTS — strict TypeScript; `noEmit: true`; paths `@/*` | Standard Next.js TS config |
| ESLint config | NOT FOUND as a standalone file — `next lint` uses built-in config | No `.eslintrc.json` in repo root or `frontend/` |
| API client | `frontend/lib/api.ts` | Reads `NEXT_PUBLIC_API_BASE_URL`; falls back to `http://127.0.0.1:8000` |
| Auth helper | `frontend/lib/auth.ts` | sessionStorage JWT; labeled "local development only" in comments |
| Login route | `frontend/app/login/page.tsx` | Next.js App Router page |
| Dashboard route | `frontend/app/dashboard/page.tsx` | Next.js App Router page |
| `.gitignore` coverage | Root `.gitignore` (updated Module 101) covers all frontend artifacts | `frontend/.next/`, `frontend/node_modules/`, `frontend/.env.local`, `frontend/next-env.d.ts`, `frontend/package-lock.json` |
| Separate `frontend/.gitignore` | NOT NEEDED — root `.gitignore` coverage complete from Module 101 | No additional file required |

---

## 3. Recommended Vercel Project Settings

The following settings must be configured in the Vercel project dashboard when the project
is created.

| Setting | Value | Notes |
|---|---|---|
| **Root Directory** | `frontend` | Required — the Next.js app is in `frontend/`, not the repo root; must set this in Vercel project settings |
| **Framework Preset** | Next.js | Vercel auto-detects from `next` package in `package.json`; confirm at project creation |
| **Install Command** | `npm install` (Vercel default) | npm is the package manager (`package.json` present; no `pnpm-lock.yaml` or `yarn.lock`) |
| **Build Command** | `npm run build` (Vercel default for Next.js) | Resolves to `next build` per `package.json` scripts |
| **Output Directory** | `.next` (Vercel manages automatically for Next.js) | Do not override; Vercel handles Next.js output natively |
| **Development Command** | `npm run dev` | Local use only; Vercel does not use this for deployed builds |
| **Node Version** | Not pinned (Vercel uses current LTS) | Next.js 14.2.3 supports Node 18+; Vercel's default LTS is compatible |
| **Deployment target** | Staging environment only | No production traffic; fake/non-PHI data only |
| `vercel.json` | NOT NEEDED | Vercel auto-detects Next.js 14.2.3 without custom config |
| `output: 'standalone'` | NOT NEEDED | `standalone` is only for Docker/self-hosted deploys; not for Vercel |

**Root directory is the critical setting.** Without it, Vercel will attempt to build from
the repo root and fail because there is no `package.json` at the repo root.

---

## 4. Vercel Environment Variables

### 4.1 Required Variable

| Variable | Value (staging) | Scope | Secret? | Failure mode if wrong |
|---|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `https://staging-api.up.railway.app` (placeholder — actual URL assigned when Railway service is created) | Preview + Production | NO — public build-time variable; baked into browser bundle | Frontend cannot reach Railway API; all API calls fail with connection error |

**Key notes:**
- `NEXT_PUBLIC_API_BASE_URL` is read at **build time** by Next.js and baked into the browser
  JavaScript bundle. Changing the value requires a redeploy — it is not a runtime env var.
- The fallback in `frontend/lib/api.ts` is `'http://127.0.0.1:8000'` (local dev). If
  `NEXT_PUBLIC_API_BASE_URL` is not set on Vercel, deployed frontend will attempt to call
  `localhost`, which always fails in the browser.
- Set this variable before the first Vercel build.

### 4.2 No Backend Secrets in Vercel Frontend Env

The following secrets must NEVER appear in Vercel frontend environment variables:

| Secret | Reason |
|---|---|
| `JWT_SECRET_KEY` | Backend-only; in Vercel `NEXT_PUBLIC_*` vars it would be exposed in the browser bundle |
| `DATABASE_URL` | Backend-only; belongs in Railway dashboard only |
| `VAPI_WEBHOOK_SECRET` | Backend-only; HMAC verification server-side only |
| `N8N_WEBHOOK_SECRET` | Backend-only |
| `INTERNAL_WEBHOOK_SECRET` | Backend-only |
| Any PostgreSQL credentials | Backend-only |

`NEXT_PUBLIC_*` variables are public by design — they are included in the JavaScript bundle
served to every browser. Any secret placed in a `NEXT_PUBLIC_*` variable is effectively
public. The only Vercel env var this frontend requires is `NEXT_PUBLIC_API_BASE_URL`, which
is not a secret.

---

## 5. Frontend/Backend URL Contract

The staging deployment requires both the Railway backend URL and the Vercel frontend URL
to be known before the CORS configuration is complete.

| URL | Placeholder | Known when |
|---|---|---|
| Railway staging API URL | `https://staging-api.up.railway.app` | After Railway service creation (Module 101 execution) |
| Vercel staging frontend URL | `https://staging-app.vercel.app` | After first Vercel project creation and deploy |

### 5.1 CORS Bootstrap Sequence

Railway's `FRONTEND_CORS_ORIGINS` must be the exact Vercel staging frontend URL. This
creates a sequencing dependency:

1. Deploy Railway backend (get actual Railway HTTPS URL)
2. Create Vercel project (root: `frontend`); set `NEXT_PUBLIC_API_BASE_URL` to Railway URL
3. Deploy Vercel project (get actual Vercel HTTPS URL)
4. Update Railway `FRONTEND_CORS_ORIGINS` to the exact Vercel URL
5. Redeploy or restart Railway backend (picks up new CORS origins)
6. Verify CORS preflight: `OPTIONS /auth/login` from Vercel origin → correct headers

This sequence ensures no wildcard CORS is ever set and the exact origin is used from the
first working end-to-end request.

### 5.2 URL Contract Rules

| Rule | Detail |
|---|---|
| No wildcard CORS | `FRONTEND_CORS_ORIGINS` must be exact origin; `_cors_origins()` in `main.py` never returns `*` |
| No ngrok in staging | No ngrok URLs in `FRONTEND_CORS_ORIGINS` or `NEXT_PUBLIC_API_BASE_URL`; ngrok is local-dev only |
| HTTPS required | Both Railway and Vercel provide HTTPS by default on their subdomains; no plain HTTP in staging |
| Exact origin match | `FRONTEND_CORS_ORIGINS` must match Vercel URL exactly (no trailing slash; correct subdomain) |
| API calls use Bearer token | Under the current fake-data staging auth flow, `apiFetch()` injects `Authorization: Bearer <token>`; this works with the current sessionStorage JWT and the backend's `HTTPBearer` dependency |

---

## 6. Auth/Session Staging Caveat

| Aspect | Current State | Notes |
|---|---|---|
| Token storage | `sessionStorage.setItem('praximed_access_token', token)` | Browser tab-scoped; cleared on tab close |
| Auth comment | `frontend/lib/auth.ts` lines 2–6: "local development only" | Explicit in-code label |
| Acceptable for staging | YES — fake/non-PHI data only | XSS risk is not a PHI risk when only fake data is present |
| PHI production blocker | YES — `sessionStorage` JWT is XSS-accessible | Blocker #1 and #2 from Architecture Checkpoint 12 |
| Resolution | httpOnly Secure SameSite=None cookie (for Railway+Vercel cross-domain staging) | Module 98 plan; Sprint 14 auth sprint begins after M1/M2 smoke evidence |
| SameSite complication | Railway (`*.up.railway.app`) and Vercel (`*.vercel.app`) are different eTLD+1 → cross-site | Cookie auth requires `SameSite=None; Secure` for staging; `SameSite=Lax` for production on same domain |
| No auth implementation in this module | Auth hardening is deferred | `sessionStorage` JWT used for fake-data staging only; no changes to `auth.ts` or `api.ts` |

---

## 7. Build Verification Plan

| Step | Status | Notes |
|---|---|---|
| `npm run build` confirmed locally | Previously verified (Sprint 9 / Module 77) | `next build` completed successfully; dashboard and login rendered |
| Fresh build verification in Module 102 | NOT RUN — `npm install` not executed in this module | `frontend/node_modules/` not present; cannot run build without installing |
| TypeScript strict mode | Enabled (`strict: true` in `tsconfig.json`) | Build fails on type errors; all prior sprints passed |
| Build artifacts committed | MUST NOT be committed | `frontend/.next/` is in root `.gitignore` (added Module 101) |
| `frontend/node_modules/` committed | MUST NOT be committed | `frontend/node_modules/` is in root `.gitignore` (added Module 101) |
| Build status for actual Vercel deploy | Vercel runs `npm install && npm run build` automatically | If build fails, Vercel does not deploy; check Vercel build logs |

**Build verification action (future module):** Confirm `npm run build` passes in a clean
environment before the first actual Vercel deployment. Vercel will run this automatically;
if it fails, the deploy does not go live.

---

## 8. Vercel Routing Expectations

| Route | Path | Notes |
|---|---|---|
| Login page | `/login` → `frontend/app/login/page.tsx` | Next.js App Router; Vercel serves this as a static/SSR page |
| Dashboard | `/dashboard` → `frontend/app/dashboard/page.tsx` | Auth-guarded client-side; redirects to `/login` if not authenticated |
| Root redirect | `/` → `frontend/app/page.tsx` | Likely redirects to `/login` or `/dashboard` |
| API routes | None — all API calls go to Railway backend | Frontend is a pure client; no Next.js API routes |
| 404 | Next.js default | No custom 404 page configured |

**Auth guard:** Dashboard protection is client-side only — `useEffect` checks
`isAuthenticated()` (reads `sessionStorage`) and redirects to `/login` if false. This is
accepted for fake-data staging. For production, a Next.js middleware server-side guard
is deferred.

**Backend API:** All `fetch` calls go to `NEXT_PUBLIC_API_BASE_URL` (Railway staging URL).
The frontend makes no calls to Vercel functions or other origin.

---

## 9. Staging Smoke Expectations After Vercel Deploy

Once the Vercel frontend is deployed and CORS is configured (Section 5.1 sequence):

| Smoke Step | Expected | Notes |
|---|---|---|
| Frontend loads at Vercel staging HTTPS URL | 200 OK | Vercel CDN serves the Next.js build |
| `/login` renders | Login form visible | No backend call at this stage |
| Login with fake staging user credentials | JWT returned; `sessionStorage` populated | Backend must have fake clinic user (Module 103) |
| `/dashboard` loads | Four sections: appointments, patients, consultations, notifications | Requires fake clinic data in staging DB |
| Browser API calls reach Railway staging API | 200 responses | Requires CORS and `NEXT_PUBLIC_API_BASE_URL` correct |
| CORS success | No CORS error in browser console | `OPTIONS` preflight passes; no wildcard |
| Staff Confirm button works | `PATCH /appointment-requests/{id}/status` → `status=confirmed` | Requires JWT and fake appointment row in DB |
| Vapi-created appointment appears | `status=new`; `action_required=true` | After staging Vapi smoke (Module 104) |
| No real patient data visible | All rows are fake/synthetic | Enforced by Module 103 seed strategy |

---

## 10. Rollback Plan

| Scenario | Action |
|---|---|
| Broken Vercel deploy | Roll back via Vercel dashboard → Deployments → previous deployment → "Promote to Production" |
| Wrong `NEXT_PUBLIC_API_BASE_URL` | Update the env var in Vercel dashboard → trigger new deployment (env var changes require redeploy) |
| Wrong `FRONTEND_CORS_ORIGINS` on Railway | Update Railway env var → Railway restarts the service automatically |
| Frontend shows connection errors | Verify `NEXT_PUBLIC_API_BASE_URL` matches exact Railway HTTPS URL; verify Railway service is running |
| CORS error in browser | Verify `FRONTEND_CORS_ORIGINS` on Railway matches exact Vercel URL (no trailing slash, correct subdomain) |
| Smoke step fails | Halt; diagnose before continuing; rollback per Module 97 checklist rules |

---

## 11. Blockers Before Actual Vercel Deploy

| # | Blocker | Level | Module |
|---|---|---|---|
| 1 | Exact Railway staging API URL unknown until Railway service is created | **HIGH** | Module 101 execution |
| 2 | Exact Vercel staging frontend URL unknown until first Vercel deploy | MEDIUM | First deploy |
| 3 | `NEXT_PUBLIC_API_BASE_URL` cannot be finalized without Railway URL | HIGH | Module 101 execution |
| 4 | `FRONTEND_CORS_ORIGINS` on Railway cannot be set without Vercel URL | MEDIUM | After first Vercel deploy |
| 5 | Staging fake clinic + user provisioning not defined | HIGH | Module 103 |
| 6 | `npm run build` not freshly verified in clean environment | MEDIUM | Pre-deploy verification |
| 7 | `sessionStorage` JWT — acceptable for fake-data staging only; PHI blocker for production | (Known) | M3 auth sprint |
| 8 | No actual Railway service or Railway PostgreSQL add-on created yet | HIGH | Module 101 execution |

---

## 12. Non-Goals

- No deployment execution in this module
- No production launch (production PHI launch remains NO-GO)
- No real patient data or real clinic data
- No auth/session hardening implementation (deferred; Sprint 14 post-smoke evidence)
- No Fabel 5 / frontend UX redesign
- No appointment workflow expansion
- No real Vercel project creation in this module
- No `npm install` or `npm run build` execution in this module
- No real secrets in any file created by this module

---

## 13. Recommended Next Step — Module 103

**Sprint 14 / Module 103 — Staging DB Migration and Seed Strategy**

Backend and frontend deployment prep are now documented. Before the actual staging
deployment attempt, define:
- The exact migration execution sequence for the Railway staging DB
- A safe fake staging tenant (clinic) + user provisioning strategy that does not reuse
  `seed_local_data.py` (which uses hardcoded local-dev UUIDs and a local-dev password hash)
- What the staging DB must contain before the smoke runbook begins
- Whether a staging-safe seed script is needed or whether manual SQL inserts suffice
