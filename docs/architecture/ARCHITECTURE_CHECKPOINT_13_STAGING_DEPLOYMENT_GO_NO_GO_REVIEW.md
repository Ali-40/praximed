# Architecture Checkpoint 13 — Staging Deployment Go/No-Go Review

**Date:** 2026-07-03
**Sprint:** Sprint 13 complete (Modules 95–99)
**Backend tests:** 1946/1946 passed
**Status:** Sprint 13 reviewed. Fake-data staging deployment attempt: GO. Production PHI launch: NO-GO.

---

## 1. Current Status

Sprint 13 delivered the complete staging deployment and auth planning documentation set.
No deployment was executed. No real patient data was used. No runtime code was changed.

| Deliverable | Module | Commit | Status |
|---|---|---|---|
| Staging deployment topology plan (Railway + Vercel) | 95 | 3102ab7 | Complete |
| Staging environment variable matrix | 96 | 5761683 | Complete |
| Staging deployment dry-run checklist | 97 | 5f7122d | Complete |
| Auth/session hardening implementation plan (httpOnly cookie) | 98 | fcaf667 | Complete |
| Production deployment execution plan | 99 | 6897406 | Complete |

**Test suite:** 1946/1946 passed (54 new tests added in Module 99)

**No deployment executed.** No real patient data used. No production secrets. No runtime
code changes. No auth refactor. Production PHI launch remains NO-GO.

---

## 2. Sprint 13 Review

### 2.1 Module 95 — Staging Deployment Topology Plan

Five staging platform options were scored and compared:
- Option A: Railway (backend + PostgreSQL) + Vercel (frontend) — ★★★★★ **Selected**
- Option B: Render backend + Render PostgreSQL + Vercel frontend — ★★★★
- Option C: Fly.io backend + Fly.io PostgreSQL + Vercel frontend — ★★★
- Option D: Supabase + Vercel — ★★★
- Option E: Single VPS — ★★

**Decision rationale:** Railway is the only PaaS with a managed PostgreSQL add-on that
auto-injects `DATABASE_URL`, natively supports Python/FastAPI, and requires no Docker or
infrastructure configuration. Vercel is the canonical Next.js deployment target.

**Staging domain placeholders:**
- Backend: `https://staging-api.up.railway.app`
- Frontend: `https://staging-app.vercel.app`

**Architecture:**
```
Vapi (test assistant)
  → POST /vapi/tools/capture-appointment-request
    → Railway backend (HTTPS)
      → Railway PostgreSQL
        → Vercel frontend (staff dashboard)
          → PATCH /appointment-requests/{id}/status (staff Confirm)
```

**Key constraints established:**
- Fake/non-PHI data only; no `seed_local_data.py` in staging
- Vapi test assistant only; no production assistant
- `X-Vapi-Scopes: vapi:tool` (singular) — plural returns HTTP 403
- sessionStorage JWT acceptable for fake-data staging; not PHI-safe for production
- No ngrok in staging; stable HTTPS throughout
- No wildcard CORS; `FRONTEND_CORS_ORIGINS` must be exact Vercel origin

### 2.2 Module 96 — Staging Environment Variable Matrix

Complete per-variable specification for all staging components.

**Backend env vars (Railway dashboard, all required):**

| Variable | Injection | Secret | Source |
|---|---|---|---|
| `DATABASE_URL` | Railway auto-injects from PostgreSQL add-on | Yes | Railway auto |
| `JWT_SECRET_KEY` | Manual; Railway dashboard | Yes | `openssl rand -hex 32` |
| `VAPI_WEBHOOK_SECRET` | Manual; Railway dashboard | Yes | `openssl rand -hex 32` |
| `N8N_WEBHOOK_SECRET` | Manual; Railway dashboard | Yes | `openssl rand -hex 32` |
| `INTERNAL_WEBHOOK_SECRET` | Manual; Railway dashboard | Yes | `openssl rand -hex 32` |
| `FRONTEND_CORS_ORIGINS` | Manual; Railway dashboard | No | Exact Vercel staging URL |
| `APP_ENV` | Manual; Railway dashboard | No | `staging` |

**Frontend env var (Vercel dashboard):**

| Variable | Value | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `https://staging-api.up.railway.app` | Public build-time variable; not a secret |

**Critical isolation rule:** Staging secrets must be distinct from local-dev placeholder
values (`local-dev-jwt-secret-key-change-in-production`) and from future production secrets.

**SameSite note (cross-domain complication):** Railway (`*.up.railway.app`) and Vercel
(`*.vercel.app`) have different eTLD+1 domains. Browser fetch from Vercel to Railway is
cross-site. `SameSite=Lax` cookies will NOT be sent for cross-site fetch/XHR. When
cookie auth is implemented (Sprint 14), staging requires `SameSite=None; Secure`.

**13-scenario failure matrix:** All documented in Module 96, covering incorrect values,
missing secrets, wildcard CORS, wrong database, and local-dev placeholder leakage.

### 2.3 Module 97 — Staging Deployment Dry-Run Checklist

19-section step-by-step checklist covering every deployment phase.

**Phases covered:**
1. Codebase and account readiness preconditions
2. Target topology confirmation
3. Railway backend service setup (env vars, start command, health check)
4. Railway PostgreSQL add-on provisioning and DATABASE_URL injection
5. Vercel frontend project setup (root `frontend/`, build command, env vars)
6. Domain and CORS verification (no wildcard; OPTIONS preflight)
7. Per-variable validation checklist
8. Migration gate verification (`run_migrations.py` exits 0 before uvicorn starts)
9. Auth/dashboard smoke (sessionStorage JWT; fake credentials only)
10. Vapi staging checklist (test assistant; `vapi:tool` singular; no auto-confirm)
11. n8n staging (NOT ENABLED for initial staging; documented as optional)
12. 13-step smoke execution order
13. Evidence capture per step
14. 14 failure stop rules
15. Rollback paths (Railway revision rollback; Vercel rollback; PostgreSQL PITR)
16. Go/no-go decision table

**Backend start command established:**
```
python backend/scripts/run_migrations.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```
Non-zero exit from `run_migrations.py` halts the deploy before any traffic is served.

### 2.4 Module 98 — Auth/Session Hardening Implementation Plan

Complete migration plan from `sessionStorage` JWT to httpOnly Secure SameSite cookie.

**Current architecture (code-exact):**
- `POST /auth/login` returns JWT in JSON body → `sessionStorage.setItem('praximed_access_token', token)`
- `apiFetch()` injects `Authorization: Bearer <token>` header on every request
- `get_current_user` reads `HTTPBearer` credentials; no cookie path
- No `POST /auth/logout` route; logout only clears `sessionStorage`
- `clinic_id` decoded client-side from JWT payload via `atob()`

**Target architecture (Sprint 14):**
- `POST /auth/login` sets `Set-Cookie: praximed_session=<token>; HttpOnly; Secure; SameSite=<tier>; Path=/; Max-Age=3600`
- `get_current_user` reads `praximed_session` cookie first; falls back to Bearer during migration window
- `POST /auth/logout` → `response.delete_cookie('praximed_session', Max-Age=0)`
- Frontend `api.ts` adds `credentials: 'include'`; removes manual `Authorization` header
- `clinic_id` stored in `localStorage` from login JSON response body (`user.clinic_id`)

**SameSite per tier:**
- Local: `Lax`
- Staging (Railway + Vercel — cross-domain): `None; Secure` (required)
- Production (same registrable domain): `Lax`

**Sprint 14 implementation scope:** backend auth.py + logout route + current_user.py + frontend auth.ts + api.ts + login page + dashboard

### 2.5 Module 99 — Production Deployment Execution Plan

Ordered milestone sequence from staging deployment through production PHI launch.

**11 milestones (M1–M11):**
- M1: Staging deployment
- M2: Staging smoke validation
- M3: Auth/session hardening (httpOnly cookie)
- M4: Production domain and TLS
- M5: Production secrets provisioning
- M6: Production database (managed PostgreSQL + PITR)
- M7: Production Vapi assistant
- M8: Legal/GDPR/compliance review (**hard gate**)
- M9: CI/CD pipeline
- M10: Production monitoring
- M11: Production PHI launch (all prior gates required)

**12 production blockers:** all OPEN; 0 resolved by Sprint 13 (planning only)

---

## 3. Staging Go/No-Go Assessment

### A. Ready for Fake-Data Staging Deployment Attempt

| Criterion | Status |
|---|---|
| Integration loop proven locally (Vapi → backend → dashboard → staff Confirm) | PROVEN |
| Backend test suite passing (1946/1946) | PASS |
| `npm run build` passes locally | VERIFIED (Module 77) |
| Staging platform selected (Railway + Vercel) | COMPLETE |
| Staging env var matrix defined | COMPLETE |
| Staging deployment dry-run checklist ready | COMPLETE |
| Smoke runbook ready | COMPLETE (`DEPLOYMENT_SMOKE_RUNBOOK.md`) |
| No real patient data required | CONFIRMED |
| sessionStorage JWT acceptable for fake-data staging | CONFIRMED (auth.ts comment) |
| No production secrets required for staging | CONFIRMED |
| Rollback plan defined | COMPLETE (Module 97) |
| Failure stop rules defined | COMPLETE (Module 97 — 14 rules) |

**Conclusion:** Fake-data staging deployment attempt is **GO**.

### B. Not Ready for Production PHI Launch

| Blocker | Status |
|---|---|
| `sessionStorage` JWT — XSS-accessible (PHI blocker) | OPEN |
| No httpOnly Secure SameSite cookie implementation (PHI blocker) | OPEN |
| No production managed PostgreSQL with PITR | OPEN |
| No production secrets manager configured | OPEN |
| No stable production HTTPS domains | OPEN |
| No production CORS configuration applied | OPEN |
| No production Vapi assistant | OPEN |
| No production n8n/calendar configuration | OPEN |
| No CI/CD pipeline | OPEN |
| No rollback verification | OPEN |
| No legal/GDPR/Austrian healthcare compliance review (PHI blocker) | OPEN |
| No production monitoring / alerting | OPEN |

**Conclusion:** Production PHI launch is **NO-GO**. All 12 blockers remain open.

---

## 4. Staging Constraints

All staging deployment activity is bound by the following non-negotiable constraints.
Any violation is a stop rule — deployment must halt immediately.

| Constraint | Requirement |
|---|---|
| **Data** | Fake/non-PHI data only; no real patient names, phone numbers, or medical records |
| **Secrets** | Isolated staging secrets; distinct from local-dev placeholders and future production secrets |
| **Database** | Isolated staging Railway PostgreSQL add-on; no connection to any local or production database |
| **Vapi** | Test Vapi assistant only; no production assistant; no auto-confirmation |
| **n8n** | Staging n8n workflow only (NOT ENABLED for initial staging deployment) |
| **CORS** | Exact staging Vercel origin only in `FRONTEND_CORS_ORIGINS`; no wildcard (`*`) ever |
| **HTTPS** | Stable HTTPS staging URL required for both backend and frontend; no plain HTTP |
| **ngrok** | No ngrok in any staging env var; not allowed in staging |
| **Real clinic traffic** | No real clinic staff; no real patients; test interactions only |
| **Smoke runbook** | Full 13-step smoke runbook must pass before staging is accepted |
| **Stop rules** | All 14 Module 97 failure stop rules are active; any trigger = immediate halt |

---

## 5. Auth/Session Decision

### 5.1 Current State

The current `sessionStorage` JWT mechanism is:
- Explicitly labeled "local development only" in `frontend/lib/auth.ts` lines 3–5
- Acceptable for fake-data staging: XSS on a test account with fake data is not a PHI risk
- A hard PHI blocker for production: XSS with real patient data would expose PHI

### 5.2 Decision

| Decision | Ruling |
|---|---|
| sessionStorage JWT for fake-data staging | **ACCEPTABLE** — no real PHI at risk |
| sessionStorage JWT for production PHI | **NOT ACCEPTABLE** — PHI blocker; blocks Blocker #1 and #2 |
| httpOnly cookie implementation (Sprint 14) | **GO** — may begin after fake-data staging deployment evidence is captured |
| Auth hardening timing | After M1/M2 (staging deployment + smoke), before M3 production PHI |

### 5.3 SameSite Complication

Railway (`*.up.railway.app`) and Vercel (`*.vercel.app`) are different registered domains
(different eTLD+1). Browser fetch requests from Vercel to Railway are cross-site.
`SameSite=Lax` does not send cookies for cross-site fetch/XHR (only top-level navigation GETs).

**Consequence for Sprint 14:** when implementing cookie auth, staging environment must
use `SameSite=None; Secure`. Production (single registrable domain) uses `SameSite=Lax`.
This is a documented known risk; Module 98 plan covers it with the tier-specific SameSite
matrix.

---

## 6. Deployment Readiness Blockers

The following blockers must all be resolved before production PHI launch. None are minor
config items; each requires explicit implementation or infrastructure work.

| # | Blocker | Resolves At | Risk Level |
|---|---|---|---|
| 1 | Auth/session hardening not implemented (sessionStorage PHI risk) | M3 (Sprint 14) | High / PHI blocker |
| 2 | httpOnly Secure SameSite cookie not built | M3 (Sprint 14) | High / PHI blocker |
| 3 | No production managed PostgreSQL with backups/PITR | M6 | Blocker |
| 4 | No production secrets manager configured | M5 | Blocker |
| 5 | No stable production HTTPS domains | M4 | Blocker |
| 6 | No production CORS configuration applied | M4 | Blocker |
| 7 | No production Vapi assistant configured | M7 | Blocker |
| 8 | No production n8n/calendar configuration | M7+ | Blocker |
| 9 | No CI/CD pipeline implemented | M9 | High |
| 10 | No rollback verification tested | M2 | High |
| 11 | No legal/GDPR/Austrian healthcare compliance review | M8 | High / PHI blocker (hard gate) |
| 12 | No production monitoring / alerting configured | M10 | Medium |

---

## 7. Decision

| Item | Decision |
|---|---|
| **Fake-data staging deployment attempt** | **GO** |
| **Production PHI launch** | **NO-GO** — all 12 blockers open |
| **Auth/session hardening (httpOnly cookie)** | **GO** for Sprint 14; implement after M1/M2 evidence |
| **SameSite=None for staging** | Required; documented in Module 98; implement in Sprint 14 |
| **Fabel 5 / frontend UX sprint** | **DEFERRED** — wait until staging confirmed and auth hardened |
| **Appointment workflow expansion** | **DEFERRED** — out of current scope |
| **CI/CD pipeline** | **DEFERRED** — planned for M9; not blocking staging |
| **Legal/GDPR compliance review** | **REQUIRED** before production PHI; hard gate at M8 |

---

## 8. Recommended Sprint 14 Sequence

Sprint 14 begins actual fake-data staging deployment preparation and execution.

| Module | Description | Deliverable |
|---|---|---|
| 100 | Staging Deployment Config File Inventory | Inspect what config files, start commands, build commands, and Railway/Vercel config are present or missing; no deployment yet |
| 101 | Railway Backend Deployment Prep | Create Railway service; configure env vars per Module 96; confirm backend start command; no real deploy |
| 102 | Vercel Frontend Deployment Prep | Create Vercel project; configure `NEXT_PUBLIC_API_BASE_URL`; confirm build command; no real deploy |
| 103 | Staging DB Migration/Seed Strategy | Confirm migration gate works; fake clinic UUID strategy; no real data |
| 104 | Staging Smoke Execution Evidence | Execute the 13-step smoke runbook; capture evidence; pass/fail per step |
| Checkpoint 14 | Staging Deployment Review | Review evidence; go/no-go for auth hardening Sprint |

**Parallel to or after M1/M2:**
- Auth/session hardening implementation (httpOnly cookie, Module 98 plan) begins once fake-data staging smoke evidence is captured

---

## 9. Recommended Next Module

**Sprint 14 / Module 100 — Staging Deployment Config File Inventory**

Before creating real Railway or Vercel projects, inspect the repository for everything
deployment-related: config files, start commands, build outputs, Procfiles, Railway config
files, migration scripts, and any gaps between what the dry-run checklist assumes and what
actually exists in the repo.

**Module 100 scope:**
- Inspect what exists: `backend/scripts/run_migrations.py`, `frontend/package.json` build/start
  commands, `next.config.js`, any `Procfile` or `railway.toml`, `.gitignore` coverage
- Identify what is missing or needs to be created for Railway/Vercel deploy (e.g., a
  `railway.toml` service config, a `Procfile`, confirmed `npm run build` output directory)
- Document findings as a config inventory
- Do not deploy; no real secrets; no runtime changes unless a missing config file
  (e.g., `railway.toml`) is trivially added

---

## 10. Final Go/No-Go Table

| Item | Decision | Rationale |
|---|---|---|
| Fake-data staging deployment prep | **GO** | All planning complete; topology, env matrix, checklist, and smoke runbook ready |
| Actual staging deployment attempt | **GO** | Proceed in Sprint 14 per Module 97 checklist; fake data only |
| Production PHI launch | **NO-GO** | All 12 blockers remain open; auth not hardened; no managed DB; no HTTPS domain; no legal review |
| Auth/session hardening implementation | **GO** — Sprint 14 | Plan complete (Module 98); implement after M1/M2 evidence; before production PHI |
| Fabel 5 / frontend UX sprint | **DEFERRED** | Wait until staging confirmed and auth hardened |
| Appointment workflow expansion | **DEFERRED** | Outside current scope |

---

## 11. Security Review

All security measures from Sprints 1–13 remain intact. No regressions in Sprint 13.

### 11.1 What Is Enforced

| Concern | Status |
|---|---|
| JWT auth protects all PHI routes | ACTIVE |
| Machine auth protects Vapi/n8n routes | ACTIVE |
| Tenant isolation — `clinic_id` on all queries | ACTIVE |
| `clinic_ref` from machine auth header only — patient payload cannot inject tenant | ACTIVE |
| No auto-confirmation by AI | ACTIVE — `status='new'`, `action_required=True` hardcoded |
| No calendar booking on Confirm | ACTIVE — not built |
| bcrypt password hashing | ACTIVE |
| Audit logging on PHI mutations | ACTIVE |
| HMAC signature verification on webhooks | ACTIVE |
| CORS — explicit origins only | ACTIVE — `_cors_origins()` never returns wildcard |
| No real secrets committed to version control | CONFIRMED |
| No real patient data in tests or docs | CONFIRMED |

### 11.2 Unresolved Production Security Risks

| Risk | Detail | Resolved At |
|---|---|---|
| `sessionStorage` JWT — XSS-accessible | Labeled local-dev only in auth.ts; acceptable for fake-data staging | M3 — Sprint 14 |
| No token refresh | 60-min expiry; no auto-redirect on silent expiry | Deferred Sprint 14+ |
| No CSP header | Not yet deployed | Deferred |
| Client-side auth guard only | Next.js middleware not implemented | Deferred |
| `raw_payload` PHI storage | GDPR/DSG retention policy not reviewed | M8 — legal review |

---

## 12. Next Step

**Sprint 14 / Module 100 — Staging Deployment Config File Inventory**

Inspect the repository for all deployment-relevant config files and identify gaps before
creating real Railway/Vercel projects. Docs and static contract tests only. No deployment.
No real secrets. No runtime changes (unless a trivial config file like `railway.toml` is added).
