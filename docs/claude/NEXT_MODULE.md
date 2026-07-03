# Sprint 13 / Module 98 — Auth/Session Hardening Implementation Plan

Status: pending Module 97 review.

## Context

Module 97 completed the staging deployment dry-run checklist. The Sprint 13 staging
documentation set is now complete:
- Module 95: Staging topology chosen (Railway + Vercel)
- Module 96: Staging environment variable matrix
- Module 97: Staging deployment dry-run checklist

The largest remaining production blocker is the `sessionStorage` JWT. The frontend
stores the JWT access token in `sessionStorage`, explicitly labeled "local-dev only"
in `frontend/lib/auth.ts`. This is acceptable for fake-data staging (no PHI) but
is PHI-incompatible for any production launch.

Module 98 produces a detailed **implementation plan** for httpOnly Secure SameSite
cookie auth migration. No implementation is performed in this module — plan only.
Execution is Sprint 14.

## Scope

### 1. Read and audit current state

Read:
- `frontend/lib/auth.ts` — current sessionStorage JWT implementation
- `frontend/lib/api.ts` — current manual Authorization header injection
- `frontend/app/login/page.tsx` — current login form
- `frontend/app/dashboard/page.tsx` — current auth guard
- `backend/app/api/routes/auth.py` — current login route
- `backend/app/api/dependencies/auth.py` — current JWT dependency
- `backend/app/core/jwt_tokens.py` — token creation and decode
- `docs/deployment/PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md` — Option B cookie migration path (Module 93)
- `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` — sessionStorage risk acknowledgment
- `docs/architecture/ARCHITECTURE_CHECKPOINT_12_PRODUCTION_READINESS_REVIEW.md` — production blockers

### 2. Create `docs/deployment/AUTH_SESSION_HARDENING_PLAN.md`

Sections:
1. **Purpose** — implementation plan only; no auth code changed in this module; production PHI blocker
2. **Current state assessment** — exact code locations for `storeToken`, `getToken`, `clearToken`, `sessionStorage`, `Authorization: Bearer`, auth guard
3. **Risk assessment** — XSS attack surface; 60-minute expiry window; no CSP; client-side guard only
4. **Migration target: httpOnly Secure SameSite cookie** — Option B from Module 93
5. **Backend changes required**
   - `POST /auth/login` response: add `Set-Cookie` header
   - New `POST /auth/logout` route: clear cookie
   - Auth dependency: read from `request.cookies` instead of `Authorization` header
   - Staging/production cookie attributes: `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`, `Domain=` policy
6. **Frontend changes required**
   - Remove `storeToken`, `getToken`, `clearToken` from `auth.ts`
   - Remove manual `Authorization: Bearer` header injection from `api.ts`
   - Add `credentials: "include"` to all fetch calls
   - Add `POST /auth/logout` call on logout
   - Server-side auth guard option (Next.js middleware)
7. **CORS changes required for cookie auth**
   - `allow_credentials=True` (already set)
   - `FRONTEND_CORS_ORIGINS` must be an exact origin (not wildcard) — already enforced
   - Cookie `Domain` attribute policy for staging vs production
8. **CSRF risk and mitigation** — SameSite=Lax protects cross-site POSTs; same-domain subdomains require care; no custom CSRF token needed for SameSite=Lax with same registrable domain
9. **Token expiry and refresh** — current 60-minute expiry; refresh token strategy (out of scope for this plan; defer)
10. **Test plan for the cookie migration** — unit tests for `Set-Cookie` on login; unit tests for cookie-based auth dependency; contract tests for logout route; frontend contract tests for credentials: include; regression tests for all PHI routes
11. **Implementation sequence** — order of changes; which parts are backend-first vs frontend-first; rollback point
12. **Staging dry-run with cookie auth** — after implementation, re-run staging smoke with cookie auth enabled
13. **Production gate** — cookie auth is a prerequisite for production PHI launch; completes one of the 12 Checkpoint 12 blockers
14. **What not to implement in this module** — no backend code change; no frontend code change; no cookie implementation; plan only
15. **Next step** — Sprint 14: implement httpOnly cookie auth (backend + frontend + tests)

### 3. Static contract tests

Create `backend/tests/test_auth_session_hardening_plan_contract.py`:
- Plan doc exists
- Mentions sessionStorage risk
- Mentions httpOnly
- Mentions Secure attribute
- Mentions SameSite
- Mentions Set-Cookie on login
- Mentions POST /auth/logout
- Mentions credentials: "include"
- Mentions removing Authorization header injection
- Mentions CORS credentials: true
- Mentions CSRF / SameSite=Lax mitigation
- Mentions no implementation in this module (plan only)
- Mentions production PHI blocker
- Mentions 60-minute expiry / no refresh (deferred)
- Mentions test plan for cookie migration
- Mentions Sprint 14 execution
- Mentions no real secrets in plan
- Confirms no obvious real secrets in doc

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 98
- `docs/claude/NEXT_MODULE.md` — Architecture Checkpoint 13: Staging Deployment Go/No-Go Review

## What not to do

- Do not implement httpOnly cookie auth in this module
- Do not modify `frontend/lib/auth.ts` or `frontend/app/`
- Do not modify `backend/app/api/routes/auth.py` or dependencies
- Do not execute staging deployment
- Do not start Fabel 5/UX sprint
- Do not expand appointment workflow

## Acceptance

- `docs/deployment/AUTH_SESSION_HARDENING_PLAN.md` created
- Contract tests pass
- Full test suite passes (1865/1865 minimum)
- Commit: `Sprint 13 / Module 98 — Auth session hardening implementation plan`
