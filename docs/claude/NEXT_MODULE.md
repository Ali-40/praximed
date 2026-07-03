# Sprint 12 / Module 94 — Deployment Smoke Runbook

Status: pending Module 93 commit.

## Context

Modules 91–93 produced:
- A production readiness inventory (13 deployment blockers)
- An environment and secrets contract (4 tiers; all env vars defined)
- A CORS/auth/domain plan (domain topology; sessionStorage risk; cookie migration path)

The remaining Sprint 12 step before Architecture Checkpoint 12 is a concrete runbook
that describes how to smoke-test a deployment once the blockers are resolved. This module
creates the runbook document. No deployment occurs in this module.

## Scope

### 1. Read and audit current state

Read:
- `docs/deployment/PRODUCTION_READINESS_INVENTORY.md` — 13 blockers
- `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` — env vars per tier
- `docs/deployment/PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md` — domain topology; CORS plan
- `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` — existing local runbook pattern
- `backend/scripts/` — what scripts exist (run_migrations.py, seed_local_data.py, db_smoke_test.py)
- `backend/app/api/routes/health.py` — current health endpoint

### 2. Create `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md`

Sections:
1. **Purpose** — when to use this runbook; what it does not cover
2. **Pre-smoke checklist** — verify all env vars set; domain live; HTTPS working; DB migrated
3. **Backend smoke steps** — start backend; hit `/health`; verify DB pool; check logs
4. **Frontend smoke steps** — build with `npm run build`; start with `next start`; load login page; verify NEXT_PUBLIC_API_BASE_URL
5. **Auth smoke** — log in with a test user; verify JWT returned; verify dashboard loads
6. **CORS smoke** — verify browser does not show CORS errors in console; verify preflight passes
7. **Vapi tool smoke** — trigger a test Vapi tool call to production URL; verify appointment row created; verify staff Confirm works
8. **n8n webhook smoke** — trigger a test n8n webhook; verify HMAC signature passes
9. **DB smoke** — verify migration version in alembic_version table; verify seed table absent; verify a real row can be written and read
10. **Secrets sanity check** — confirm no local placeholder values in production env; confirm no ngrok URLs
11. **Rollback steps** — what to do if smoke fails; how to take the backend offline without data loss
12. **Post-smoke sign-off** — what counts as pass; who signs off

### 3. Static contract tests

Create `backend/tests/test_deployment_smoke_runbook_contract.py`:
- Runbook doc exists
- Mentions pre-smoke checklist
- Mentions `/health` endpoint
- Mentions `npm run build`
- Mentions auth smoke / login
- Mentions CORS smoke
- Mentions Vapi tool smoke
- Mentions n8n webhook smoke
- Mentions DB migration check
- Mentions no local placeholder values in production
- Mentions no ngrok in production
- Mentions rollback steps
- Does not contain real secrets or real domain names with passwords

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 93 commit; record Module 94
- `docs/claude/NEXT_MODULE.md` — Architecture Checkpoint 12: Production Readiness Review

## What not to do

- Do not execute any deployment steps
- Do not create CI/CD pipeline files
- Do not change backend routes, auth, or CORS config
- Do not add real secrets or real domain names
- Do not start the Fabel 5 / UX sprint

## Acceptance

- `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` created
- Contract tests pass
- Full test suite passes (1729/1729 minimum)
- Commit: `Sprint 12 / Module 94 — Deployment smoke runbook`
