# Architecture Checkpoint 12 — Production Readiness Review

**Date:** 2026-07-03
**Sprint:** Sprint 12 complete (Modules 91–94)
**Backend tests:** 1765/1765 passed
**Status:** Production readiness documentation complete. Production PHI launch: NO-GO. Staging fake-data deployment prep: GO.

---

## 1. Current Status

Sprint 12 produced the complete production readiness documentation set. No deployment was
executed. No real patient data was used. No runtime code was changed.

| Deliverable | Module | Status |
|---|---|---|
| Production Deployment Readiness Inventory | 91 | Complete — 13 deployment blockers documented |
| Environment and Secrets Contract | 92 | Complete — 4 tiers; all 8 env vars defined; rotation policy |
| Production CORS/Auth/Domain Plan | 93 | Complete — domain topology; sessionStorage risk; cookie migration path |
| Deployment Smoke Runbook | 94 | Complete — local/staging/production-like steps; failure triage; pass/fail checklist |

All documents live in `docs/deployment/`. No production deployment infrastructure exists yet.
No CI/CD pipeline. No staging environment. No production domain.

---

## 2. Sprint 12 Completed Work

| Module | Description | Key Output |
|---|---|---|
| 91 | Production Deployment Readiness Inventory | 13-blocker inventory; env var audit; infrastructure requirements |
| 92 | Environment and Secrets Contract | Canonical env var table; secret classification; rotation policy; 4 deployment tiers defined |
| 93 | Production CORS/Auth/Domain Plan | Domain topology with placeholders; CORS rules per tier; `sessionStorage` risk rated High; httpOnly cookie migration Options A/B/C documented |
| 94 | Deployment Smoke Runbook | 17-section runbook; 4 smoke tiers; exact local commands; failure triage table; pass/fail checklist; production launch gate |

**Tests added in Sprint 12:** 140 new tests (1625 → 1765). All static contract tests.

---

## 3. Proven Baseline (All Prior Sprints)

As of this checkpoint, the following capabilities are proven in the local/test environment:

### 3.1 Backend

| Capability | Status |
|---|---|
| FastAPI backend starts and serves on `http://127.0.0.1:8000` | PROVEN |
| `GET /health` and `GET /health/ready` return correct responses | PROVEN |
| JWT login (`POST /auth/login`) returns access token | PROVEN |
| JWT auth protects all PHI routes (`/patients`, `/consultations`, `/appointment-requests`, `/notifications`) | PROVEN |
| Machine auth protects Vapi/n8n routes (`/vapi/tools/*`, `/webhooks/*`, `/calendar/*`) | PROVEN |
| Tenant isolation — `clinic_id` enforced on all PHI queries | PROVEN |
| `adapt_vapi_tool_call_body` handles nested and flat Vapi tool-call shapes | PROVEN |
| `clinic_ref` always from machine auth header — patient payload cannot select tenant | PROVEN |
| Appointment request created: `source=vapi`, `status=new`, `action_required=True` | PROVEN |
| `PATCH /appointment-requests/{id}/status` transitions status on staff action | PROVEN |
| HMAC-SHA256 webhook signature verification (Vapi, n8n, internal) | PROVEN |
| Alembic migrations apply cleanly to local PostgreSQL | PROVEN |
| `ClinicConfigLoader` wired in lifespan; disk config + DB fallback | PROVEN |
| Audit logging on PHI mutations | PROVEN |
| bcrypt password hashing; no plaintext in DB | PROVEN |
| CORS with explicit origins; no wildcard | PROVEN |

### 3.2 Frontend

| Capability | Status |
|---|---|
| Next.js frontend starts and serves on `http://localhost:3000` | PROVEN |
| Login page renders; form submits to `POST /auth/login` | PROVEN |
| JWT stored in `sessionStorage`; Bearer token injected into all API calls | PROVEN (local-dev labeled) |
| Dashboard renders all four sections: appointments, patients, consultations, notifications | PROVEN |
| Appointment Confirm button works: status `new` → `confirmed`; button disappears | PROVEN |
| Logout clears `sessionStorage`; redirects to `/login` | PROVEN |
| Auth guard: unauthenticated `/dashboard` redirects to `/login` | PROVEN (client-side) |

### 3.3 Integration

| Capability | Status |
|---|---|
| Real Vapi test assistant → ngrok → adapter → appointment request → dashboard → staff Confirm | PROVEN (Module 90) |
| Nested Vapi tool-call shape handled by adapter | PROVEN (Module 88) |
| Staff confirmation boundary maintained: no auto-confirm at any layer | PROVEN (all smokes) |
| No calendar booking on Confirm | PROVEN (all smokes) |
| n8n calendar sync webhook: signed requests accepted; wrong signature rejected | PROVEN (Module 58) |
| Machine auth scope `vapi:tool` (singular) — `vapi:tools` plural rejected | CONFIRMED (Module 89) |

---

## 4. Production Readiness Assessment

### A. Ready Now (Local/Test)

- Full local integration loop (Vapi → backend → dashboard → staff Confirm)
- All backend tests pass (1765/1765)
- Local smoke runbook executable per `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md`
- All Sprint 12 deployment documentation complete

### B. Ready for Staging / Fake-Data Deployment Preparation

The following items are achievable in Sprint 13 without touching PHI:
- Choosing a staging deployment target (hosting platform)
- Provisioning an isolated staging database (managed PostgreSQL or equivalent)
- Configuring staging env vars (non-production secrets; isolated from local and prod)
- Defining stable staging HTTPS domains (placeholders can be finalized in Sprint 13)
- Configuring a Vapi test assistant against the staging API URL
- Running the smoke runbook with fake test data only

No real clinic data, no real patients, no production Vapi assistant required for staging prep.

### C. Not Ready for Production PHI Launch

The following blockers prevent production PHI launch. None are minor config items — each
requires explicit implementation or infrastructure work before real clinic staff data and
real patient data can be handled.

| Blocker | Risk Level | Notes |
|---|---|---|
| `sessionStorage` JWT — XSS-accessible | **High / PHI blocker** | `frontend/lib/auth.ts` explicitly labels this local-dev only; httpOnly cookie migration required |
| No httpOnly Secure SameSite cookie implementation | **High / PHI blocker** | Planned in Module 93; not yet built |
| No production managed PostgreSQL with backups | **Blocker** | Local Docker only; production PHI requires managed DB with PITR |
| No production secrets manager configured | **Blocker** | All secrets currently via shell exports / `.env` file |
| No stable production API/frontend HTTPS domains | **Blocker** | Placeholders only; no DNS, no TLS |
| No production CORS configuration applied | **Blocker** | `FRONTEND_CORS_ORIGINS` not set for production |
| No production Vapi assistant (test assistant only) | **Blocker** | Production assistant requires stable HTTPS URL and production secrets |
| No production n8n/calendar configuration | **Blocker** | Not configured beyond local testing |
| No CI/CD pipeline | **High** | No automated test runs on push; no deployment automation |
| No rollback verification | **High** | Rollback plan documented; not tested |
| No legal / GDPR / Austrian healthcare compliance review | **High / PHI blocker** | `raw_payload` column stores PHI; GDPR compliance not reviewed |
| No production monitoring / alerting | **Medium** | No APM, no structured logs, no on-call runbook |

---

## 5. Security Review

All security measures from Sprints 1–12 remain intact. No regressions introduced in Sprint 12.

### 5.1 What Is Enforced

| Concern | Status |
|---|---|
| JWT auth protects all PHI routes | ACTIVE — `get_current_user` dependency on all PHI routes |
| Machine auth protects Vapi/n8n-style routes | ACTIVE — `get_machine_auth_context` + `require_vapi_tool_access` |
| Tenant isolation — `clinic_id` enforced on all queries | ACTIVE — all PHI queries filter by `clinic_id` |
| `clinic_ref` in Vapi tool call always from machine auth header — patient payload cannot inject tenant | ACTIVE — `adapt_vapi_tool_call_body` enforces; argument `clinic_ref` silently ignored |
| Staff Confirm requires human JWT (Bearer token) | ACTIVE — `PATCH /appointment-requests/{id}/status` requires `get_current_user` |
| No auto-confirmation by AI at any layer | ACTIVE — service hardcodes `status='new'`, `action_required=True`; no code path confirms |
| No calendar booking on Confirm | ACTIVE — no calendar integration built |
| Password storage — bcrypt hash | ACTIVE — `password_hashing.py` |
| Audit logging on PHI mutations | ACTIVE — `audit_logger` on all mutation routes |
| HMAC signature verification on webhooks | ACTIVE — Modules 46–47 |
| CORS — explicit allowed origins only | ACTIVE — `_cors_origins()` never returns wildcard |
| No real secrets committed to version control | CONFIRMED throughout |
| No real patient data in tests or docs | CONFIRMED throughout |

### 5.2 Unresolved Production Security Risk

| Risk | Detail |
|---|---|
| `sessionStorage` JWT | XSS-accessible token; `auth.ts` explicitly labels this local-dev only; httpOnly Secure SameSite cookie migration required before production PHI |
| No token refresh | 60-minute expiry causes silent failures; no auto-redirect on expiry |
| No CSP header | Content-Security-Policy not yet deployed; reduces (but doesn't eliminate) XSS risk mitigation |
| Client-side auth guard only | Dashboard redirect to `/login` is JavaScript; server-side guard (Next.js middleware) not implemented |
| `raw_payload` PHI storage | Vapi tool-call body stored in DB for audit; access control and GDPR retention policy not reviewed |

---

## 6. Direction Options

### Option A — Staging Deployment Target Selection and Topology Plan (Recommended)

**What:** Choose a hosting platform (e.g., Railway, Render, Fly.io, Supabase + Vercel, or
a VPS); define the backend/frontend/DB/domain topology for staging; configure staging env
vars with isolated non-PHI secrets; point a Vapi test assistant at the staging API; run
the smoke runbook with fake data.

**Why first:** The integration loop is proven locally. Sprint 12 mapped every production
risk. The natural next step is to make the system accessible beyond the developer machine
using fake data. This validates the deployment assumptions and reveals any platform-specific
gaps before auth hardening or UI work begins.

**What it is not:** A production launch. Staging uses fake data, isolated secrets, and a
Vapi test assistant only. No real clinic staff, no real patients.

### Option B — Auth/Session Hardening (httpOnly Cookie Migration)

**What:** Implement the httpOnly Secure SameSite=Lax cookie migration from Module 93 Option B.
Backend adds `Set-Cookie` on login and reads cookie in the auth dependency. Frontend removes
manual `Authorization` header injection and uses `credentials: "include"`. Add `/auth/logout`
route and token expiry handling.

**Why defer slightly:** This is a prerequisite for production PHI launch but not for staging
with fake data. Doing the staging topology first means the auth migration can be smoke-tested
against a real staging environment rather than only locally.

**When:** Sprint 13 or 14; must complete before any real clinic staff access production.

### Option C — Doctor-Facing Frontend UX Sprint (Fabel 5 / Claude Frontend Tooling)

**What:** Evaluate Fabel 5 or Claude-related frontend generation tooling for a premium
doctor-facing dashboard redesign. Better cards, richer appointment workflow, improved typography.

**Why defer:** Staging deployment topology must be clear before a major UX investment, so
the redesign targets the correct domain structure and CORS assumptions. UI polish on a
`localhost`-only baseline is premature.

**When:** After staging deployment assumptions are established; likely Sprint 14 or 15.

### Option D — Appointment Workflow Expansion

**What:** Add Reject action (`status: "rejected"`), Assign to doctor, mark-handled flag,
appointment detail drawer, audit trail visibility.

**Why defer:** Existing routes support status transitions (Modules 17 + 64). This is high
value for clinic staff workflow completeness but not a prerequisite for staging deployment.
Best built after staging topology is clear so the expanded workflow targets the correct environment.

**When:** Sprint 14 or later.

---

## 7. Recommendation

**Sprint 13 — Staging Deployment Target Selection and Topology Plan**

Choose a staging deployment target and define the exact topology before writing code.
The smoke runbook exists; the env var contract exists; the CORS/auth plan exists. What's
missing is a concrete decision about where staging lives and what platform-specific steps
are needed to put the PraxisMed stack there.

Recommended Sprint 13 sequence:

| Module | Description |
|---|---|
| 95 | Staging Deployment Target Selection and Topology Plan — compare platform options; choose one; define backend/frontend/DB topology |
| 96 | Staging Environment Variable Matrix — map all env vars to staging values (with placeholders for real secrets); define secret injection method for chosen platform |
| 97 | Staging Deployment Dry-Run Checklist — step-by-step pre-deployment checklist for the chosen platform; no execution yet |
| 98 | Auth/Session Hardening Implementation Plan — detailed implementation plan for httpOnly cookie migration; scope/test plan; ready for execution in Sprint 14 |
| Checkpoint 13 | Staging Deployment Go/No-Go Review — decide if staging deployment can be executed; go/no-go for fake-data staging launch |

---

## 8. Explicit Deferrals

| Item | Deferred Until |
|---|---|
| Production PHI launch | All 12 blockers in Section 4.C resolved + legal/GDPR review |
| httpOnly cookie implementation | Module 98 plan; execution Sprint 14 |
| Fabel 5 / premium frontend UX sprint | After staging deployment topology confirmed |
| Appointment workflow expansion (Reject, Assign, Archive) | Sprint 14 or later; after staging topology clear |
| Token refresh endpoint | Sprint 14 or after auth migration |
| Calendar handoff on Confirm | Future module |
| Patient notification on Confirm | Future module |
| CI/CD pipeline | Sprint 14 or dedicated DevOps sprint |
| GDPR / Austrian healthcare compliance review | Before production PHI launch |
| Production monitoring / alerting | Before production PHI launch |

---

## 9. Final Go / No-Go

| Decision | Verdict | Rationale |
|---|---|---|
| **Production PHI launch** | **NO-GO** | 12 unresolved blockers; `sessionStorage` JWT is PHI-incompatible; no managed DB; no production secrets; no HTTPS domain |
| **Staging fake-data deployment prep** | **GO** | Integration loop proven; env contract complete; smoke runbook ready; fake data only; no PHI risk |
| **Auth/session hardening (httpOnly cookie)** | **PLAN NOW, IMPLEMENT SPRINT 14** | Prerequisite for production PHI; plan in Module 98; implement after staging topology confirmed |
| **Fabel 5 / frontend UX sprint** | **WAIT** | Deferred until staging topology clear |
| **Appointment workflow expansion** | **WAIT** | Deferred until staging topology clear |

---

## 10. Sprint Summary (All Sprints)

| Sprint | Scope | Modules | Tests at End |
|---|---|---|---|
| Sprint 1 | Backend API foundation | 1–23 | 545 |
| Sprint 2 | Clinical documentation engine | 24–34 | 908 |
| Sprint 3 | Clinical workflow API routes + access control | 35–40 | 1083 |
| Sprint 4 | Database migration + audit logging | 41–44 | 1193 |
| Sprint 5 | Local PostgreSQL + smoke test | 45–51 | 1312 |
| Sprint 6 | External integration compatibility | 52–58 | 1386 |
| Sprint 7 | Production auth and JWT wiring | 59–65 | 1461 |
| Sprint 8 | Frontend dashboard foundation | 66–71 | 1521 |
| Sprint 9 | Local runtime smoke, CORS, browser demo | 72–77 | 1547 |
| Sprint 10 | Dashboard demo polish | 78–80 | 1560 |
| Sprint 11 | Vapi appointment intake loop | 81–90 | 1625 |
| Sprint 12 | Production deployment readiness inventory | 91–94 | 1765 |
