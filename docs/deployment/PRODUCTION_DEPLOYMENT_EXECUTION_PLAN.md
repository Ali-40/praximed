# Production Deployment Execution Plan — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 13 / Module 99
**Status:** Planning document only — no deployment executed in this module

---

## 1. Purpose

This document sequences every milestone from staging deployment through production PHI launch.
It converts the Sprint 12–13 planning artifacts into an ordered execution plan with explicit
go/no-go gates at each step.

**What this document is:**
- An ordered sequence of milestones from staging through production launch
- A go/no-go gate at each milestone
- A tracker of the 12 production blockers from Architecture Checkpoint 12
- A reference for sprint estimation and decision escalation

**What this document is not:**
- A deployment execution (no deployment occurs in this module)
- A real infrastructure provisioning guide
- A real production secrets document
- An auth/session hardening implementation (that is Sprint 14)
- A production PHI launch approval (production PHI launch is NO-GO until all gates pass)

No deployment is executed in this module. No production secrets. No runtime code changes.
No production PHI launch.

---

## 2. Current Status

### 2.1 What Is Complete

| Item | Status | Sprint |
|---|---|---|
| Local integration loop (Vapi → backend → dashboard → staff Confirm) | PROVEN | Sprint 1–12 |
| Full backend test suite (1892 tests) | PASSING | Sprint 13 |
| Staging topology plan (Railway backend + Railway PostgreSQL + Vercel frontend) | COMPLETE | Sprint 13 / Module 95 |
| Staging environment variable matrix (9 backend vars + 1 frontend var) | COMPLETE | Sprint 13 / Module 96 |
| Staging deployment dry-run checklist (19 sections) | COMPLETE | Sprint 13 / Module 97 |
| Auth/session hardening implementation plan (httpOnly cookie migration) | COMPLETE | Sprint 13 / Module 98 |
| Production deployment execution plan (this document) | COMPLETE | Sprint 13 / Module 99 |

### 2.2 What Is NOT Done

| Item | Status |
|---|---|
| Staging environment not yet deployed | PENDING — Milestone 1 |
| Auth/session httpOnly cookie not yet implemented | PENDING — Milestone 3 / Sprint 14 |
| Production domain and TLS not yet configured | PENDING — Milestone 4 |
| Production secrets not yet provisioned | PENDING — Milestone 5 |
| Production database not yet provisioned | PENDING — Milestone 6 |
| Production Vapi assistant not yet configured | PENDING — Milestone 7 |
| Legal/GDPR/Austrian healthcare compliance review not yet conducted | PENDING — Milestone 8 |
| CI/CD pipeline not yet configured | PENDING — Milestone 9 |
| Production monitoring not yet configured | PENDING — Milestone 10 |
| Production PHI launch | NO-GO — blocked by all 12 open blockers |

---

## 3. Production Blockers Tracker

From Architecture Checkpoint 12, 12 blockers prevent production PHI launch. Sprint 13
delivered planning artifacts that address several blockers but resolves none — resolving
a blocker requires implementation or infrastructure provisioning, not documentation alone.

| # | Blocker | Risk Level | Sprint 13 Progress | Status |
|---|---|---|---|---|
| 1 | `sessionStorage` JWT — XSS-accessible | **High / PHI blocker** | Module 98 plan ready | OPEN — implement Sprint 14 |
| 2 | No httpOnly Secure SameSite cookie implementation | **High / PHI blocker** | Module 98 plan ready | OPEN — implement Sprint 14 |
| 3 | No production managed PostgreSQL with backups | **Blocker** | Staging topology chosen (Module 95) | OPEN — provision Milestone 6 |
| 4 | No production secrets manager configured | **Blocker** | Staging var matrix defined (Module 96) | OPEN — provision Milestone 5 |
| 5 | No stable production HTTPS domains | **Blocker** | Staging domain placeholders defined (Module 95) | OPEN — configure Milestone 4 |
| 6 | No production CORS configuration applied | **Blocker** | Staging CORS strategy defined (Module 96) | OPEN — apply at Milestones 1 and 4 |
| 7 | No production Vapi assistant | **Blocker** | Staging Vapi strategy defined (Module 95) | OPEN — configure Milestone 7 |
| 8 | No production n8n/calendar configuration | **Blocker** | Staging n8n strategy defined (Module 95) | OPEN — configure post-Milestone 7 |
| 9 | No CI/CD pipeline | **High** | Not addressed in Sprint 13 | OPEN — Milestone 9 |
| 10 | No rollback verification | **High** | Rollback plan in Module 97 checklist | OPEN — verify at Milestone 2 |
| 11 | No legal/GDPR/Austrian healthcare compliance review | **High / PHI blocker** | Not addressed in Sprint 13 | OPEN — Milestone 8 (hard gate) |
| 12 | No production monitoring / alerting | **Medium** | Not addressed in Sprint 13 | OPEN — Milestone 10 |

**Resolved blockers this sprint:** 0 (Sprint 13 = planning and documentation only)
**Open blockers:** 12 / 12

Production PHI launch is blocked until all 12 blockers are resolved and all go/no-go gates pass.

---

## 4. Milestone Sequence

| Milestone | Description | Go/No-Go Gate | Sprint Estimate |
|---|---|---|---|
| M1 | Staging deployment | Module 97 checklist complete; Railway/Vercel deploy succeeds; migrations applied | Sprint 14 |
| M2 | Staging smoke validation | All 13 smoke steps pass; evidence captured; no stop rule triggered | Sprint 14 |
| M3 | Auth/session hardening | httpOnly cookie working on staging; smoke re-passes with cookie auth | Sprint 14 |
| M4 | Production domain and TLS | Stable HTTPS domains; TLS certs valid; DNS propagated; no ngrok | Sprint 14–15 |
| M5 | Production secrets provisioning | All production secrets in secrets manager; no placeholders | Sprint 15 |
| M6 | Production database | Managed PostgreSQL with PITR; migrations applied clean | Sprint 15 |
| M7 | Production Vapi assistant | Production Vapi assistant pointing at production HTTPS URL; no ngrok | Sprint 15 |
| M8 | Legal/GDPR/compliance review | Austrian healthcare data protection review complete; `raw_payload` PHI policy approved | Sprint 15–16 (hard gate) |
| M9 | CI/CD pipeline | Automated test gate on push; deployment automation; no secrets in CI logs | Sprint 15–16 |
| M10 | Production monitoring | APM, structured logs, alerting, on-call runbook active | Sprint 16 |
| M11 | Production PHI launch | All M1–M10 gates passed; Architecture Checkpoint 13 go/no-go decision | Sprint 16+ |

Gates are sequential. No milestone may begin execution until its predecessor is in a GO state.
Production PHI launch (M11) is blocked until all prior gates pass.

---

## 5. Milestone 1 — Staging Deployment

**Objective:** Deploy the PraxisMed backend, PostgreSQL database, and frontend to staging
infrastructure using fake/non-PHI data only.

**Platform:** Railway (backend + PostgreSQL) + Vercel (frontend) per Module 95 topology plan.

**Prerequisite documents:**
- `docs/deployment/STAGING_DEPLOYMENT_TOPOLOGY_PLAN.md` — platform choice and architecture
- `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` — all staging env vars
- `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` — step-by-step checklist

**Execution:** Execute the Module 97 dry-run checklist in order:
1. Confirm repository readiness (no local-dev secrets committed; `.gitignore` covers `backend/.env`)
2. Create Railway service for backend; set all 7 env vars per Module 96 matrix
3. Create Railway PostgreSQL add-on; confirm `DATABASE_URL` auto-injection
4. Deploy backend; confirm migration gate executes on startup (`run_migrations.py` exits 0)
5. Create Vercel project; set `NEXT_PUBLIC_API_BASE_URL` to staging Railway HTTPS URL
6. Deploy frontend; confirm build succeeds
7. Confirm `FRONTEND_CORS_ORIGINS` on Railway matches Vercel origin exactly (no wildcard)

**Data constraint:** Fake/non-PHI test data only. No real patient data. No real clinic staff
data. `seed_local_data.py` must NOT be run in staging.

**Staging domains (placeholder):**
- Backend: `https://staging-api.up.railway.app`
- Frontend: `https://staging-app.vercel.app`

No ngrok allowed in staging. Staging uses HTTPS throughout.

**Failure stop rules:**
- Wildcard CORS origin returned by backend → immediate rollback
- ngrok URL present in any env var → halt; not allowed in staging
- Migration non-zero exit → halt; diagnose before retry
- Secret visible in application logs → immediate halt and secret rotation
- Auto-confirmed appointment (status ≠ new on creation) → immediate halt and code audit

**Rollback:**
- Railway backend: deploy previous Railway revision via Railway dashboard
- Vercel frontend: roll back to previous deployment via Vercel dashboard
- Railway PostgreSQL: point-in-time restore if migration corrupts schema

**Go/no-go gate (Decision Gate A):** All Module 97 checklist items signed off;
`GET /health` returns 200; `GET /health/ready` returns 200; frontend loads; proceed to
Milestone 2.

---

## 6. Milestone 2 — Staging Smoke Validation

**Objective:** Execute the full smoke runbook against the staging environment to confirm every
integration path works end-to-end with fake test data.

**Reference:** `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md`

**Smoke execution order (13 steps):**
1. `GET /health` → 200 OK
2. `GET /health/ready` → 200 OK (confirms DB connectivity)
3. Confirm migration table shows correct Alembic revision
4. Frontend loads at staging Vercel HTTPS URL
5. CORS preflight `OPTIONS /auth/login` from Vercel origin → correct headers; no wildcard
6. Login with fake credentials → JWT returned; `sessionStorage` populated
7. Dashboard renders all four sections (appointments, patients, consultations, notifications)
8. Vapi test call → `POST /vapi/tools/capture-appointment-request` → appointment created
   with `status=new`, `action_required=True`
9. Staff Confirm button → `PATCH /appointment-requests/{id}/status` → `status=confirmed`
10. No auto-confirmation occurs at any step
11. n8n calendar sync (if enabled) → `POST /webhooks/n8n/calendar-sync` with HMAC signature
12. Confirm no PHI, secrets, or tokens appear in application logs
13. Logout clears `sessionStorage`; redirect to `/login`

**Evidence capture:** For each smoke step, record pass/fail with timestamp and any error output.
Store evidence in a team-accessible location for the go/no-go review.

**sessionStorage note:** `sessionStorage` JWT is acceptable for staging with fake data only.
It is XSS-accessible and is explicitly labeled local-dev only in `frontend/lib/auth.ts`. It must
not be used when real patient data or real clinic staff credentials are present. Blockers 1 and 2
are addressed by Milestone 3.

**Rollback verification:** Confirm rollback procedures from Milestone 1 are tested and
functional. Record rollback procedure verification as evidence (Blocker 10).

**Failure stop rules:**
- Any smoke step fails → halt; diagnose before continuing
- Wildcard CORS origin returned → immediate rollback
- ngrok URL referenced in any response → immediate halt
- Appointment auto-confirmed without staff action → immediate rollback and code audit
- PHI, secret, or token value in logs → immediate halt and secret rotation

**Go/no-go gate (Decision Gate B):** All 13 smoke steps pass; evidence captured; no stop rule
triggered; rollback procedure verified; Blocker 10 resolved; proceed to Milestone 3.

---

## 7. Milestone 3 — Auth/Session Hardening

**Objective:** Implement the httpOnly Secure SameSite cookie migration from the Module 98 plan.
Re-run smoke against staging with cookie auth active.

**Reference:** `docs/security/AUTH_SESSION_HARDENING_IMPLEMENTATION_PLAN.md`

**Sprint 14 implementation scope:**
- Backend `auth.py`: add `Set-Cookie: praximed_session=<token>; HttpOnly; Secure; SameSite=None;
  Path=/; Max-Age=3600` on login response
  (Staging requires `SameSite=None; Secure` — Railway and Vercel are different eTLD+1; cross-site
  fetch from Vercel to Railway is blocked by `SameSite=Lax`)
- Backend `auth.py`: add `POST /auth/logout` route → `response.delete_cookie('praximed_session',
  Max-Age=0)`
- Backend `current_user.py`: read `praximed_session` cookie first; fall back to Bearer header
  during migration window; remove fallback after full rollout
- Frontend `auth.ts`: remove `storeToken`/`getToken`/`clearToken`; add `storeClinicId`/
  `getClinicId` from `localStorage` (reading `clinic_id` from login JSON response body)
- Frontend `api.ts`: add `credentials: 'include'`; remove Bearer Authorization header injection
- Frontend `login/page.tsx`: replace `storeToken` with `storeClinicId` from response body
- Frontend `dashboard/page.tsx`: add `POST /auth/logout` call on logout

**SameSite policy by tier:**
- Staging (Railway + Vercel — different eTLD+1): `SameSite=None; Secure` (required)
- Production (same registrable domain): `SameSite=Lax`

**`clinic_id` resolution:** After cookie migration, `clinic_id` is no longer readable from the
JWT (httpOnly cookie is not JS-accessible). The login JSON response body already includes
`user.clinic_id` (confirmed in `LoginResponse` schema). Frontend stores `clinic_id` in
`localStorage` from the login response body.

**CSRF:** `SameSite=None` (staging) requires an Origin check or CSRF double-submit cookie.
`SameSite=Lax` (production) provides CSRF protection for state-mutating requests from
cross-site navigations.

**Smoke re-run:** After implementing httpOnly cookie auth, re-run all 13 smoke steps against
staging with cookie auth. Confirm:
- Login response sets `praximed_session` cookie (HttpOnly, Secure, SameSite=None on staging)
- No `Authorization: Bearer` header sent from frontend after migration
- All PHI routes remain protected; unauthenticated requests return 401
- Logout clears cookie; subsequent PHI route requests return 401

**Go/no-go gate (Decision Gate C):** httpOnly cookie auth working on staging; all 13 smoke
steps pass with cookie auth; Blockers 1 and 2 resolved; proceed to Milestone 4.

---

## 8. Milestone 4 — Production Domain and TLS

**Objective:** Establish stable HTTPS domains for backend and frontend in the production
environment. Configure TLS certificates and DNS.

**Requirements:**
- Stable production HTTPS API domain (placeholder: `https://api.<production-domain>`)
- Stable production HTTPS frontend domain (placeholder: `https://app.<production-domain>`)
- TLS certificate valid and auto-renewing (Let's Encrypt or platform-managed)
- DNS propagated globally
- Backend and frontend on same registrable domain so `SameSite=Lax` cookie auth works
  without requiring CSRF tokens
- No ngrok URL in any production env var
- No placeholder domain names in production secrets or config

**CORS:** Set `FRONTEND_CORS_ORIGINS` to exact production frontend HTTPS URL. Confirm no
wildcard. Confirm OPTIONS preflight returns `Access-Control-Allow-Origin: <exact-origin>`.

**Data constraint:** No PHI in this milestone. Domain and TLS configuration only.

**Go/no-go gate:** Both HTTPS domains respond with valid TLS; DNS propagated; CORS preflight
returns correct headers with no wildcard; Blockers 5 and 6 resolved; proceed to Milestone 5.

---

## 9. Milestone 5 — Production Secrets Provisioning

**Objective:** Provision all production secrets in a production secrets manager with high-entropy
values. No secrets in environment files, shell exports, or source code.

**Secrets required (all high-entropy; placeholders not allowed in production):**

| Secret | Min Entropy | Storage | Notes |
|---|---|---|---|
| `JWT_SECRET_KEY` | 32 bytes / 256 bits | Railway production dashboard | Rotate if compromised |
| `VAPI_WEBHOOK_SECRET` | 32 bytes | Railway production dashboard | Must match production Vapi assistant |
| `N8N_WEBHOOK_SECRET` | 32 bytes | Railway production dashboard | Must match production n8n config |
| `INTERNAL_WEBHOOK_SECRET` | 32 bytes | Railway production dashboard | Internal webhook verification |

**Verification:**
- Confirm no placeholder values remain (e.g., `local-dev-jwt-secret-key-change-in-production`)
- Confirm `JWT_SECRET_KEY` generates decodable tokens (login returns 200)
- Confirm Vapi HMAC signature verification passes with production secret
- Confirm no secret value appears in Railway deployment logs

**Rotation policy:** Per `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md`

**Go/no-go gate:** All 4 production secrets provisioned with high-entropy values; no placeholder
in production environment; Blocker 4 resolved; proceed to Milestone 6.

---

## 10. Milestone 6 — Production Database

**Objective:** Provision managed PostgreSQL in the production environment with backups and
point-in-time recovery (PITR). Apply all Alembic migrations clean.

**Requirements:**
- Managed PostgreSQL 16 (Railway managed add-on or equivalent)
- Automated daily backups enabled and verified
- Point-in-time recovery (PITR) enabled and tested
- `DATABASE_URL` set in production backend env vars; never committed to source code
- All Alembic migrations applied clean; `alembic current` matches `alembic heads`
- No seed data; no test data; no fake clinic records in production database
- Production database completely isolated from staging and local databases

**Migration gate:** The backend start command runs `python backend/scripts/run_migrations.py`
before starting uvicorn. A non-zero exit from migrations halts the deploy — no traffic is
served until all migrations succeed.

**Isolation:** Production PostgreSQL uses separate Railway add-on from staging. Different
credentials, different network, separate `DATABASE_URL`.

**Go/no-go gate:** Managed PostgreSQL provisioned with backups and PITR; all Alembic migrations
apply clean; `GET /health/ready` returns 200 in production environment; Blocker 3 resolved;
proceed to Milestone 7.

---

## 11. Milestone 7 — Production Vapi Assistant

**Objective:** Configure a dedicated production Vapi assistant pointing at the production HTTPS
API URL. No ngrok. No test assistant in production.

**Requirements:**
- Dedicated production Vapi assistant (separate from local and staging test assistants)
- Server URL: production HTTPS backend URL (e.g., `https://api.<production-domain>/vapi/tools/capture-appointment-request`)
- `VAPI_WEBHOOK_SECRET` in Vapi assistant config matches the production secret from Milestone 5
- Machine auth scope must be `vapi:tool` (singular) — `vapi:tools` plural returns HTTP 403
- No ngrok URL in production Vapi assistant configuration
- No auto-confirmation; all appointment requests remain `status=new`, `action_required=True`

**Smoke verification:**
- Vapi test call to production assistant → `POST /vapi/tools/capture-appointment-request` →
  appointment created with `status=new`
- Staff Confirm in production frontend → `PATCH /appointment-requests/{id}/status` →
  `status=confirmed`
- No auto-confirmation observed at any step

**Go/no-go gate:** Production Vapi assistant active; test call creates appointment correctly;
no auto-confirm; no ngrok; Blocker 7 resolved; proceed to Milestone 8.

---

## 12. Milestone 8 — Legal/GDPR/Compliance Review

**Objective:** Conduct the Austrian healthcare data protection review before any real patient
data enters production.

**This is a hard blocker. Production PHI launch cannot proceed without this review.**

**Items for review:**

| Item | Detail |
|---|---|
| `raw_payload` PHI storage | `appointment_requests.raw_payload` stores the full Vapi tool-call JSON body; may contain patient name, phone, reason for visit |
| PHI retention policy | How long may `raw_payload` be stored; when must it be deleted |
| GDPR right-to-erasure | Is there a patient data deletion mechanism; what is the deletion path |
| Austrian DSG compliance | Austrian healthcare data protection (DSG 2000 / GDPR implementation) specific requirements |
| Data processor agreements | Written agreements with Railway, Vercel, Vapi, n8n as data processors |
| Breach notification | Procedure for notifying supervisory authority and patients in event of breach |
| Pseudonymisation / minimisation | Whether `raw_payload` can be reduced to non-PHI fields |

**What this review is not:**
- A developer sprint item (requires legal/compliance team input)
- Resolvable by code changes alone (policy decisions are prerequisites)

**Go/no-go gate:** Legal/GDPR/Austrian healthcare compliance review complete; `raw_payload` PHI
retention policy approved in writing; data processor agreements in place; Blocker 11 resolved;
proceed to Milestone 9.

---

## 13. Milestone 9 — CI/CD Pipeline

**Objective:** Automate the test gate on every push and deployment pipeline for staging and
production.

**Requirements:**
- CI: automated pytest run on every pull request and push to main branch
- CI gate: full test suite (1892+ tests) must pass before merge to main
- CD staging: staging auto-deploys on merge to main (Railway + Vercel deployment hooks)
- CD production: production deployment requires CI green AND manual approval gate
- No deployment to production without CI green
- No secrets or PHI in CI logs; secrets injected via platform secret store (GitHub Actions
  secrets or equivalent)

**Scope:**
- GitHub Actions (or equivalent CI) for automated test gate
- Railway deployment webhook for staging backend auto-deploy
- Vercel deployment hook for staging/production frontend auto-deploy
- Production pipeline requires manual approval step after CI green

**Go/no-go gate:** CI test gate passing on every push; staging auto-deploy working; production
deploy requires manual approval; Blocker 9 resolved; proceed to Milestone 10.

---

## 14. Milestone 10 — Production Monitoring

**Objective:** Deploy APM, structured logging, alerting, and an on-call runbook before any
real PHI enters the production environment.

**Requirements:**
- Application performance monitoring (APM): backend request latency (p50/p95/p99), error rates
- Structured JSON logs: every log line includes `clinic_id`, request ID, route, HTTP status code
- No PHI, no secrets, no tokens in any log line
- Alerting: backend error rate > 1% → alert; DB connection failure → alert; authentication
  failure spike → alert; migration failure on deploy → alert
- On-call runbook: escalation path, who to contact, rollback procedure reference
- Log retention policy aligned with GDPR/DSG requirements from Milestone 8

**Go/no-go gate:** APM active; structured logging deployed with no PHI in logs; alerting
configured and tested; on-call runbook published; Blocker 12 resolved; proceed to Milestone 11.

---

## 15. Milestone 11 — Production PHI Launch

**Objective:** Admit real clinic staff and real patient data to the production system.

**This milestone requires ALL prior go/no-go gates (M1–M10) to be in GO state.**

**Pre-launch checklist:**

| Gate | Milestone | Resolves Blockers | Status |
|---|---|---|---|
| Decision Gate A | M1 Staging deployment | — | PENDING |
| Decision Gate B | M2 Staging smoke | #10 | PENDING |
| Decision Gate C | M3 Auth/session hardening | #1, #2 | PENDING |
| — | M4 Production domain and TLS | #5, #6 | PENDING |
| — | M5 Production secrets | #4 | PENDING |
| — | M6 Production database | #3 | PENDING |
| Decision Gate D | M7 Production Vapi | #7 | PENDING |
| Hard Gate | M8 Legal/GDPR/compliance | #11 | PENDING |
| — | M9 CI/CD pipeline | #9 | PENDING |
| — | M10 Production monitoring | #12 | PENDING |
| — | Architecture Checkpoint 13 | — | PENDING |

**Current status:** Production PHI launch is NO-GO.

Zero of 12 production blockers have been resolved by Sprint 13. Sprint 13 delivered planning
and documentation artifacts that enable execution. Execution begins in Sprint 14.

**Launch authority:** Architecture Checkpoint 13 is the formal go/no-go decision point. No
production PHI launch may occur without an Architecture Checkpoint sign-off confirming all
gates pass.

---

## 16. Explicit Deferrals

The following items are NOT in scope for any milestone in this plan:

| Deferred Item | Reason |
|---|---|
| Refresh token implementation | Deferred to Sprint 14+; 60-minute expiry accepted for initial production launch |
| Token blacklisting / session revocation | Deferred; httpOnly cookie + logout route is sufficient for initial launch |
| n8n production configuration | Deferred; optional; not required for Vapi appointment intake |
| Appointment workflow expansion (Reject, Assign, Archive) | Deferred; outside current scope |
| Calendar booking on Confirm | Deferred; no calendar integration built |
| Patient notification on Confirm | Deferred; no external channel notification built |
| Next.js middleware server-side auth guard | Deferred; client-side redirect accepted for initial launch |
| Content Security Policy (CSP) | Deferred; reduces (not eliminates) XSS risk; not required before initial launch |
| Fabel 5 / frontend UX sprint | Deferred; must wait until staging confirmed and auth hardened |
| Any deployment execution | No deployment in this module; planning only |
| Production PHI launch | Production PHI launch is NO-GO until all 12 blockers resolved |

---

## 17. Next Step — Architecture Checkpoint 13

**Architecture Checkpoint 13: Sprint 13 Go/No-Go Review**

This checkpoint reviews Sprint 13 deliverables and makes the formal go/no-go decision for
staging deployment execution and Sprint 14 planning.

**Sprint 13 deliverables under review:**
- Module 95: Staging topology plan (Railway + Vercel)
- Module 96: Staging environment variable matrix
- Module 97: Staging deployment dry-run checklist
- Module 98: Auth/session hardening implementation plan (httpOnly cookie)
- Module 99: This production deployment execution plan

**Checkpoint inputs:**
- Full test suite: 1892/1892 passed
- 12 production blockers: all OPEN; no resolutions in Sprint 13
- Staging deployment docs: complete and ready to execute in Sprint 14
- Auth hardening plan: ready to implement in Sprint 14

**Checkpoint decisions:**
- Staging deployment (Milestone 1): GO / NO-GO
- Sprint 14 auth/session hardening implementation: GO / NO-GO
- Production PHI launch: NO-GO (blocked by all 12 open blockers)

Architecture Checkpoint 13 must be completed before Sprint 14 execution begins.
