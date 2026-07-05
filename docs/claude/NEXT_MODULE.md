# Sprint 17 / Module 121 — Secrets and Environment Hardening Review
<!-- Module 120A complete: SameSite configurable; default "none" for cross-site staging. -->

Status: pending implementation of production secrets rotation and environment hardening review.

## Context

Module 120 complete:
- httpOnly Secure SameSite=Lax cookie session model implemented
- `POST /auth/login` sets `praximed_session` cookie
- `POST /auth/logout` clears cookie
- `GET /auth/me` returns current user via cookie or Bearer
- Frontend uses `credentials: "include"`; sessionStorage removed
- Critical blockers C1 and C2 from PRODUCTION_HARDENING_GAP_REVIEW.md closed
- Full test suite: 2532/2532 passed
- Commit: Sprint 17 / Module 120

## Goal

Perform a production secrets and environment hardening review. Document the current
state of all secrets and environment variables, define what production secrets need
to be generated and managed separately from staging, and produce a concrete checklist
for production secrets rotation.

## Scope

Documentation and plan only (like Module 119). No actual secrets generated, stored,
or committed. No production deployment.

## What Module 121 must do

1. Inventory all environment variables used by the backend and frontend:
   - `JWT_SECRET_KEY`
   - `DATABASE_URL`
   - `VAPI_WEBHOOK_SECRET`
   - `N8N_WEBHOOK_SECRET`
   - `INTERNAL_WEBHOOK_SECRET`
   - `FRONTEND_CORS_ORIGINS`
   - `NEXT_PUBLIC_API_BASE_URL`
   - Any others found in the codebase

2. For each variable: document where it is used, who generates it, what format/length
   it should be in production, and what the rotation strategy should be.

3. Confirm the staging/production separation principle: staging secrets must never be
   used in production; production secrets must be independently generated.

4. Produce a production secrets checklist document:
   `docs/security/PRODUCTION_SECRETS_CHECKLIST.md`

5. Add static contract tests verifying the checklist doc exists and records the
   required items.

## What not to do

- Do not generate, record, or commit any real secrets
- Do not deploy to production
- Do not change any runtime code
- Do not expose any existing secrets from Railway, Vercel, or any other service

## Reference docs

- `docs/architecture/PRODUCTION_HARDENING_GAP_REVIEW.md` — C3: Production secrets
  rotation and review
- `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` — existing secrets contract
- `backend/app/core/config.py` (or similar) — where env vars are loaded

## Acceptance

- `docs/security/PRODUCTION_SECRETS_CHECKLIST.md` created
- All required env vars inventoried
- Staging/production separation principle documented
- Rotation strategy outlined for each secret
- Static contract tests pass
- Full test suite passes
- Commit: `Sprint 17 / Module 121 — Secrets and environment hardening review`
