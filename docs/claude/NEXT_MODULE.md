# Sprint 17 / Module 121 — Secrets and Environment Hardening Review

Status: pending implementation of production secrets inventory and rotation checklist.

## Context

Module 120B complete:
- Deployed browser smoke PASS after Module 120 + 120A auth/session hardening
- praximed_session httpOnly Secure SameSite=None cookie works in Vercel→Railway staging
- Browser login / dashboard / session refresh / logout / post-logout block all PASS
- Full test suite: 2570/2570 passed
- Commit: Sprint 17 / Module 120B

Remaining critical blockers from PRODUCTION_HARDENING_GAP_REVIEW.md:
- C3: Production secrets rotation and review → **Module 121** (this module)
- C4/C6: PHI logging/redaction and audit hardening → Module 122
- C5: Tenant isolation and access-control verification → Module 123
- C7/C8: Backup/restore and rollback runbook → Module 124

## Goal

Perform a production secrets and environment hardening review. Inventory every
environment variable used by the backend and frontend, document the staging/production
separation principle, and produce a concrete production secrets checklist.

## Scope

Documentation and static tests only. No runtime code changes. No secrets generated,
stored, committed, or deployed. No production deployment.

## What Module 121 must do

1. Inventory all environment variables:
   **Backend (Railway):**
   - `JWT_SECRET_KEY`
   - `DATABASE_URL`
   - `VAPI_WEBHOOK_SECRET`
   - `N8N_WEBHOOK_SECRET`
   - `INTERNAL_WEBHOOK_SECRET`
   - `FRONTEND_CORS_ORIGINS`
   - `SESSION_COOKIE_SAMESITE`

   **Frontend (Vercel):**
   - `NEXT_PUBLIC_API_BASE_URL`

2. For each variable: document where it is used in the codebase, who generates it,
   what format/length is required for production, and what the rotation strategy is.

3. Confirm the staging/production separation principle:
   - Staging secrets must never be used in production.
   - Production secrets must be independently generated.
   - No cross-environment credential reuse.

4. Produce a production secrets checklist:
   `docs/security/PRODUCTION_SECRETS_CHECKLIST.md`

5. Add static contract tests verifying the checklist doc exists and records all
   required items.

## What not to do

- Do not generate, record, or commit any real secrets or credential values
- Do not deploy to production
- Do not change any runtime code
- Do not expose any existing secrets from Railway, Vercel, or any other service

## Reference docs

- `docs/architecture/PRODUCTION_HARDENING_GAP_REVIEW.md` — C3 blocker
- `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` — existing secrets contract
- `backend/app/core/jwt_tokens.py` — JWT_SECRET_KEY usage
- `backend/app/core/webhook_signature.py` — webhook secret usage
- `backend/app/main.py` — app startup / env loading

## Acceptance

- `docs/security/PRODUCTION_SECRETS_CHECKLIST.md` created
- All env vars inventoried with usage, format, and rotation notes
- Staging/production separation principle documented
- Static contract tests pass
- Full test suite passes
- Commit: `Sprint 17 / Module 121 — Secrets and environment hardening review`

---

## Upcoming (post-critical hardening)

**Sprint 18 — UI/UX Fabel 5 Premium Demo Polish**

After critical blockers C1–C8 are closed (Modules 120–124), the next sprint will
focus on premium doctor-facing UI polish using Fabel 5 or equivalent tooling.
This is deferred until the security hardening track is complete.
