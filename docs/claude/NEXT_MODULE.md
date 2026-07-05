# Sprint 17 / Module 120 — Auth/Session Hardening Implementation Plan

Status: pending implementation of httpOnly Secure SameSite cookie session model.

## Context

Module 119 complete:
- Production hardening gap review created: `docs/architecture/PRODUCTION_HARDENING_GAP_REVIEW.md`
- Critical blockers C1–C8 identified; Module 120 is the first critical to close
- Fake-data staging core: PASS
- Production PHI readiness: NO-GO (auth/session hardening is the first blocking gap)
- Full test suite: 2516/2516 passed
- Commit: Sprint 17 / Module 119

## Goal

Implement the httpOnly Secure SameSite cookie session model (Option B from
`docs/deployment/PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md` Section 6) to replace the
`sessionStorage` JWT token storage that is flagged in the code as local-dev only.

## Scope

Implementation only. No secrets. No production deployment. No real patient data.

## What Module 120 must do

### Backend changes

1. `POST /auth/login` — set httpOnly Secure SameSite=Lax cookie instead of (or
   in addition to) returning the token in the JSON body during a migration window:
   ```
   Set-Cookie: praximed_session=<JWT>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
   ```

2. `get_current_user` dependency — read JWT from cookie (`praximed_session`) in
   addition to (or instead of) `Authorization: Bearer` header:
   - File: `backend/app/api/dependencies/current_user.py`
   - Try `Authorization` header first (backward compat); fall back to cookie

3. New `POST /auth/logout` route:
   - Clear the `praximed_session` cookie (`Max-Age=0`)
   - Return HTTP 200

4. (Optional for MVP) `POST /auth/refresh` — issue a new cookie from expiry check

### Frontend changes

5. `frontend/lib/api.ts` — add `credentials: "include"` to all `fetch` calls;
   remove `Authorization: Bearer` header injection (or leave it for transition)

6. `frontend/lib/auth.ts` — replace `storeToken`/`getToken`/`clearToken`/`isAuthenticated`
   with a `/auth/me` call or cookie-presence approach

7. `frontend/app/login/page.tsx` — update logout to call `POST /auth/logout`

### Tests

8. Update existing auth/route tests for cookie-based auth
9. Add new tests: logout clears cookie; unauthenticated cookie request → 401

## What not to do

- Do not implement httpOnly cookie in production — staging and local only
- Do not record secrets
- Do not deploy to production
- Do not change machine auth (Vapi/n8n endpoints are unaffected — they use machine
  auth headers, not browser session)
- Do not change CORS implementation beyond adding `credentials: "include"` support

## Reference docs

- `docs/deployment/PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md` — Option B cookie migration
  (Section 6); CSRF strategy (Section 6.4); backend/frontend change tables
- `docs/security/AUTH_SESSION_HARDENING_IMPLEMENTATION_PLAN.md` — existing plan
- `backend/app/api/routes/auth.py` — current login route
- `backend/app/api/dependencies/current_user.py` — current JWT dependency
- `frontend/lib/auth.ts` — sessionStorage functions to replace
- `frontend/lib/api.ts` — Bearer header injection to update

## Acceptance

- `POST /auth/login` sets httpOnly Secure SameSite cookie
- `get_current_user` reads from cookie (with Bearer header fallback)
- `POST /auth/logout` clears cookie; returns 200
- Frontend uses `credentials: "include"` instead of injecting Authorization header
- Existing PHI route tests pass
- New tests: logout clears cookie; cookie auth accepted; missing cookie → 401
- Full test suite passes
- Commit: `Sprint 17 / Module 120 — Auth/session hardening implementation`
