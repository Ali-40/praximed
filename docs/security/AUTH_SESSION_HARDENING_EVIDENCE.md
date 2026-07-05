# Auth/Session Hardening Evidence — Sprint 17 / Modules 120 + 120A

**Date:** 2026-07-05
**Sprint:** Sprint 17 / Module 120 + Module 120A
**Result:** IMPLEMENTATION COMPLETE — httpOnly Secure configurable-SameSite cookie session model

---

## 1. What Was Implemented

### Backend

| Change | File | Status |
|---|---|---|
| `POST /auth/login` sets `praximed_session` httpOnly Secure SameSite=Lax cookie | `backend/app/api/routes/auth.py` | **DONE** |
| JSON body still returned (transition window compatibility) | same | **DONE** |
| `POST /auth/logout` route added — clears cookie, returns 200 | `backend/app/api/routes/auth.py` | **DONE** |
| `GET /auth/me` route added — returns user_id, clinic_id, role | `backend/app/api/routes/auth.py` | **DONE** |
| `get_current_user` reads Bearer header first, falls back to cookie | `backend/app/api/dependencies/current_user.py` | **DONE** |

### Cookie Attributes

```
Set-Cookie: praximed_session=<JWT>; HttpOnly; Secure; SameSite=<value>; Path=/; Max-Age=3600
```

SameSite is controlled by the `SESSION_COOKIE_SAMESITE` environment variable:

| `SESSION_COOKIE_SAMESITE` | SameSite value | Use case |
|---|---|---|
| not set (default) | `None` | Cross-site staging — Vercel frontend + Railway backend |
| `none` | `None` | Same as default |
| `lax` | `Lax` | Same-site / custom-domain production deployment |
| `strict` | `Strict` | Most restrictive; tightly coupled same-origin setups |
| any other value | `None` | Falls back to cross-site-safe default |

**Deployed staging (Vercel→Railway):** `SESSION_COOKIE_SAMESITE` not set → `SameSite=None; Secure`

- `HttpOnly` — not readable by JavaScript; protects against XSS token theft
- `Secure` — transmitted over HTTPS only (required when SameSite=None)
- `SameSite=None` — required for cross-site `credentials: include` fetches from Vercel to Railway
- `Max-Age=3600` — matches the 60-minute JWT expiry

**Why SameSite=None is needed for staging:**
`praximed.vercel.app` and `web-production-fd91d.up.railway.app` have different eTLD+1
(`vercel.app` vs `railway.app`), making them cross-site. Browsers only send cookies on
cross-site requests when `SameSite=None; Secure` is set. `SameSite=Lax` would cause the
cookie to be silently dropped, breaking all authenticated API calls from the frontend.

### Frontend

| Change | File | Status |
|---|---|---|
| `credentials: "include"` added to all `fetch` calls via `apiFetch` | `frontend/lib/api.ts` | **DONE** |
| Bearer header injection removed from `apiFetch` and all data fetchers | `frontend/lib/api.ts` | **DONE** |
| `token` parameter removed from all data fetcher signatures | `frontend/lib/api.ts` | **DONE** |
| `sessionStorage` token storage removed | `frontend/lib/auth.ts` | **DONE** |
| `storeToken`, `getToken`, `clearToken`, `isAuthenticated`, `getClinicId` removed | `frontend/lib/auth.ts` | **DONE** |
| `loginUser` — unchanged in call signature; no longer returns token to caller | `frontend/lib/auth.ts` | **DONE** |
| `getMe()` added — calls `GET /auth/me` for session/identity check | `frontend/lib/auth.ts` | **DONE** |
| `logout()` added — calls `POST /auth/logout` to clear cookie | `frontend/lib/auth.ts` | **DONE** |
| Login page no longer calls `storeToken` | `frontend/app/login/page.tsx` | **DONE** |
| Dashboard uses `getMe()` for auth check and clinic_id resolution | `frontend/app/dashboard/page.tsx` | **DONE** |
| Dashboard `handleLogout` calls `logout()` then redirects | `frontend/app/dashboard/page.tsx` | **DONE** |
| Dashboard data fetchers called without token parameter | `frontend/app/dashboard/page.tsx` | **DONE** |

---

## 2. What Is Unchanged

| Item | Reason |
|---|---|
| Vapi machine auth (`get_machine_auth_context`) | Machine auth uses provider headers, not browser session |
| Webhook routes (`/vapi/tools/*`, `/webhooks/*`) | Machine endpoints; not affected by cookie migration |
| n8n routes | Same; machine auth only |
| `POST /auth/login` JSON response body | Retained for backward compat during transition window |
| Bearer header fallback in `get_current_user` | Retained for machine clients and backward compat |
| Frontend login form fields (clinic_id, email, password) | Unchanged |

---

## 3. Test Evidence

All tests pass locally. No real database. No real secrets. No real patient data.

| Test | Count | Status |
|---|---|---|
| Module 120 tests (`test_auth_session_hardening_module120.py`) | 17 | **PASS** |
| Module 120A tests (`test_auth_session_hardening_module120a.py`) | 16 | **PASS** |
| Existing login route tests (`test_auth_login_route.py`) | 10 | **PASS** |
| Existing current-user dependency tests (`test_current_user_dependency.py`) | 10 | **PASS** |
| Updated frontend contract tests | 7 updated | **PASS** |
| Full test suite | 2549 | **PASS** |

### Module 120 test coverage (cookie session model)

1. Login sets `praximed_session` cookie
2. Cookie is httpOnly
3. Cookie is Secure
4. Cookie has SameSite attribute
5. Default SameSite is `none` (cross-site staging)
6. Cookie has Max-Age (not session-only)
7. JSON body still returned (backward compat)
8. Logout returns HTTP 200
9. Logout returns `{"ok": true}`
10. Logout clears cookie (Max-Age=0)
11. Cookie auth accepted by `get_current_user`
12. No Bearer + no cookie → 401
13. Bearer header still works (backward compat)
14. Expired cookie token → 401
15. Invalid cookie token → 401
16. `GET /auth/me` resolves via cookie → 200 with user info
17. `GET /auth/me` unauthenticated → 401

### Module 120A test coverage (configurable SameSite)

1. Default (env not set) → SameSite=None
2. `SESSION_COOKIE_SAMESITE=none` → SameSite=None
3. `SESSION_COOKIE_SAMESITE=lax` → SameSite=Lax
4. `SESSION_COOKIE_SAMESITE=strict` → SameSite=Strict
5. Env var is case-insensitive (LAX accepted)
6. Mixed case (None) accepted
7. Unknown value falls back to SameSite=None
8. SameSite=None cookie is still HttpOnly
9. SameSite=None cookie is still Secure
10. SameSite=None cookie still carries Max-Age
11. SameSite=Lax cookie is still HttpOnly
12. SameSite=Lax cookie is still Secure
13. `_get_cookie_samesite()` returns "none" when env absent
14. `_get_cookie_samesite()` returns "lax" when SESSION_COOKIE_SAMESITE=lax
15. `_get_cookie_samesite()` returns "strict" when SESSION_COOKIE_SAMESITE=strict
16. `_get_cookie_samesite()` returns "none" for unrecognised values

---

## 4. What Remains Pending

This module closes critical blockers **C1** and **C2** from the production hardening gap review.

The following production-environment concerns remain PENDING (not part of this module):

| Item | Status |
|---|---|
| CSRF double-submit cookie or token for state-changing requests | PENDING — Module 120 MVP uses SameSite=Lax; full CSRF hardening deferred |
| `POST /auth/refresh` (token renewal before expiry) | PENDING — not implemented in this module |
| CSP headers restricting script sources | PENDING |
| Production deployment of cookie-based auth | PENDING — staging/local only |
| Production PHI readiness | **NO-GO** — blockers C3–C8 remain open |

---

## 5. Safety Constraints

| Constraint | Status |
|---|---|
| No secrets recorded (JWT_SECRET_KEY, VAPI_WEBHOOK_SECRET, DATABASE_URL, bcrypt hashes, tokens) | **CONFIRMED — no secrets recorded** |
| No passwords recorded | **CONFIRMED** |
| No tokens recorded | **CONFIRMED** |
| No real patient data | **CONFIRMED — fake/non-PHI staging only** |
| No production PHI | **CONFIRMED — production PHI NO-GO** |
| No production deployment in this module | **CONFIRMED — implementation only** |
