# Sprint 12 / Module 93 — Production CORS/Auth/Domain Plan

Status: pending Module 92 commit.

## Context

Module 92 defined the full environment and secrets contract across all four deployment
tiers. Module 91 identified 13 production deployment blockers. Two of the highest-risk
blockers relate to auth and CORS:

- Blocker 3: `FRONTEND_CORS_ORIGINS` not set → production frontend blocked by CORS
- Blocker 8: JWT in `sessionStorage` → XSS-accessible token; clinic staff credentials at risk

This module defines the production domain topology, CORS policy, and auth hardening path.
It is a planning and documentation module. No implementation unless a missing doc-only
correction is needed.

## Scope

### 1. Read and audit current state

Read:
- `backend/app/main.py` — CORS configuration (`_cors_origins`, CORSMiddleware)
- `backend/app/api/routes/auth.py` — login response; how token is returned
- `frontend/lib/auth.ts` — how token is stored and used
- `frontend/lib/api.ts` — how Bearer token is injected into requests
- `frontend/app/login/` — login page; token handling
- `docs/deployment/PRODUCTION_READINESS_INVENTORY.md` — blockers 3, 8, 9, 10
- `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` — CORS/domain contract (Section I)

### 2. Create `docs/deployment/PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md`

Sections:
1. **Purpose** — planning doc only; no implementation
2. **Domain topology** — production backend URL, frontend URL, how they relate
3. **CORS policy for production** — what `FRONTEND_CORS_ORIGINS` must be set to;
   why wildcard is forbidden; how to handle multiple environments
4. **Current auth mechanism** — how JWT is issued (login response), stored
   (sessionStorage), and sent (Authorization: Bearer header)
5. **sessionStorage risk assessment** — why sessionStorage is XSS-vulnerable;
   what the actual attack surface is in the current frontend; severity rating
6. **httpOnly cookie migration path** — what changes are needed in backend (set-cookie
   on login) and frontend (remove manual Authorization header); complexity estimate;
   blockers; what must be decided before implementation
7. **MVP risk decision options** — three options:
   A. Block production until httpOnly cookie path is implemented
   B. Deploy with sessionStorage + XSS hardening (Content-Security-Policy header, no
      inline scripts); accept residual risk; document explicitly
   C. Hybrid: deploy behind a VPN or IP allowlist so only clinic staff can reach the
      frontend; reduces but does not eliminate XSS risk
8. **Token expiry and refresh** — current 60-minute token expiry; no refresh; what
   happens on expiry; options (extend expiry vs. add refresh endpoint)
9. **NEXT_PUBLIC_API_BASE_URL configuration** — how to set for production; must not
   default to localhost
10. **Backend URL requirements** — stable HTTPS, not ngrok; what reverse proxy or
    platform service is needed
11. **Pre-CORS/auth checklist** — items that must be resolved before Module 94
    (deployment runbook)
12. **Not in scope** — no httpOnly cookie implementation, no CI/CD, no Fabel 5

### 3. Static contract tests

Create `backend/tests/test_production_cors_auth_domain_plan_contract.py`:
- Plan doc exists
- Plan mentions sessionStorage risk
- Plan mentions httpOnly cookie path
- Plan mentions wildcard CORS prohibition
- Plan mentions stable HTTPS production URL
- Plan mentions NEXT_PUBLIC_API_BASE_URL
- Plan mentions FRONTEND_CORS_ORIGINS production value
- Plan mentions MVP risk decision options
- Plan mentions no implementation in this module

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 92 commit and Module 93
- `docs/claude/NEXT_MODULE.md` — Module 94: Deployment Smoke Runbook

## What not to do

- Do not implement httpOnly cookie auth
- Do not modify JWT signing, login route, or token handling
- Do not change CORS configuration in main.py
- Do not register a production domain
- Do not deploy
- Do not add real secrets

## Acceptance

- `docs/deployment/PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md` created
- Contract tests pass
- Full test suite passes (1697/1697 minimum)
- Commit: `Sprint 12 / Module 93 — Production CORS/auth/domain plan`
