# Auth/Session Deployed Browser Smoke Evidence — Sprint 17 / Module 120B

**Date:** 2026-07-05
**Sprint:** Sprint 17 / Module 120B
**Commit:** 95bfb64 (Module 120A — Cross-site staging cookie compatibility fix)
**Tests at commit:** 2549/2549 passed
**Result:** PASS

---

## 1. Purpose

Record the real deployed browser smoke for the auth/session hardening implemented in
Modules 120 and 120A. This confirms that the httpOnly cookie session model works in
the actual deployed staging environment (Vercel frontend + Railway backend, cross-site).

This document records outcomes only. No passwords, tokens, cookie values, or secrets
are recorded.

---

## 2. Current Result

**PASS**

The deployed browser auth/session hardening smoke passed in full. All login, session,
and logout flows work correctly with the httpOnly SameSite=None cookie model.

---

## 3. Evidence

### Environment

| Item | Value |
|---|---|
| Frontend URL | https://praximed.vercel.app |
| Backend URL | https://web-production-fd91d.up.railway.app |
| Staging type | Fake/non-PHI staging only |
| Commit under test | 95bfb64 |

### Browser smoke results

| Check | Result |
|---|---|
| Browser login with fake staging user | **PASS** |
| Dashboard load after login | **PASS** |
| Dashboard refresh keeps session (cookie survives page reload) | **PASS** |
| Appointments remain visible after refresh | **PASS** |
| Logout clears session (Logout button → POST /auth/logout) | **PASS** |
| /dashboard after logout blocks or redirects to /login | **PASS** |

---

## 4. Cookie/Session Context

The following session model is active in deployed staging:

| Attribute | Value |
|---|---|
| Cookie name | `praximed_session` |
| HttpOnly | Yes — not readable by JavaScript |
| Secure | Yes — transmitted over HTTPS only |
| SameSite | `None` — required for cross-site Vercel→Railway fetches |
| Frontend fetch mode | `credentials: include` on all API calls |
| Frontend token storage | None — no bearer-token storage dependency; no sessionStorage |
| Backend auth fallback | Bearer header accepted for machine/test compatibility |

`SameSite=None` is required because `praximed.vercel.app` (eTLD+1: `vercel.app`) and
`web-production-fd91d.up.railway.app` (eTLD+1: `railway.app`) are cross-site. Browsers
drop `SameSite=Lax` cookies on cross-site requests. `SESSION_COOKIE_SAMESITE` is left
unset in Railway (default `"none"` as of Module 120A).

---

## 5. Safety Boundary

| Constraint | Status |
|---|---|
| No password recorded | **CONFIRMED** |
| No token recorded | **CONFIRMED** |
| No cookie value recorded | **CONFIRMED** |
| No DATABASE_URL recorded | **CONFIRMED** |
| No secrets recorded (JWT_SECRET_KEY, VAPI_WEBHOOK_SECRET, etc.) | **CONFIRMED** |
| No real patient data | **CONFIRMED** |
| Fake/non-PHI staging only | **CONFIRMED** |
| No production PHI | **CONFIRMED** |

---

## 6. What This Proves

- Deployed browser auth works after cookie hardening (Modules 120 + 120A)
- The `praximed_session` httpOnly cookie is set correctly on login in the deployed environment
- `credentials: include` correctly sends the cookie from the Vercel frontend to the Railway backend
- Session survives page refresh (cookie persists across reloads within Max-Age window)
- Logout works end-to-end: Logout button → `POST /auth/logout` → cookie cleared → session ended
- Accessing `/dashboard` after logout redirects or blocks unauthenticated access
- The sessionStorage token dependency has been fully removed from the deployed frontend

---

## 7. What This Does Not Prove

The following remain **NOT PROVEN** or **PENDING** for production PHI use:

| Item | Status |
|---|---|
| Production PHI readiness | **NO-GO** — blockers C3–C8 from gap review remain open |
| Secrets rotation complete | **PENDING** — Module 121 — Secrets and Environment Hardening Review |
| PHI logging/redaction complete | **PENDING** — Module 122 |
| Tenant isolation audit complete | **PENDING** — Module 123 |
| Backup/restore runbook | **PENDING** — Module 124 |
| Monitoring/alerts/rate-limiting | **PENDING** — Module 125 |
| n8n staging workflow | **PENDING/DEFERRED** — Module 126 |
| Legal/compliance readiness | **NOT PROVEN** — no formal GDPR/HIPAA review completed |

---

## 8. Recommended Next Module

**Sprint 17 / Module 121 — Secrets and Environment Hardening Review**

Module 121 should inventory all backend and frontend environment variables, confirm
the staging/production secrets separation principle, and produce a production secrets
checklist. No secrets should be generated, committed, or deployed in that module.
