# Sprint 13 / Module 95 — Staging Deployment Target Selection and Topology Plan

Status: pending Architecture Checkpoint 12 review.

## Context

Architecture Checkpoint 12 concluded:
- Production PHI launch: NO-GO (12 unresolved blockers)
- Staging fake-data deployment prep: GO
- The integration loop is proven locally (Sprint 11)
- The full deployment documentation set is complete (Sprint 12)

Before executing any staging deployment, the team must choose a hosting platform and
define the exact topology for backend, frontend, database, domains, and secrets management.
This module makes that decision and documents the chosen architecture.

This module is docs-first. No deployment execution. No production secrets.

## Scope

### 1. Read and audit current state

Read:
- `docs/deployment/PRODUCTION_READINESS_INVENTORY.md`
- `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md`
- `docs/deployment/PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md`
- `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md`
- `backend/app/main.py` — startup requirements
- `frontend/next.config.js` — Next.js build config
- `docker-compose.postgres.yml` — current local DB setup

### 2. Create `docs/deployment/STAGING_TOPOLOGY_PLAN.md`

Sections:
1. **Purpose** — staging only; fake data; no PHI; no production launch
2. **Platform comparison** — compare 2–3 realistic options for backend hosting, frontend hosting, and managed PostgreSQL (e.g., Railway/Render/Fly.io + Vercel/Netlify + Supabase/Neon); include cost, simplicity, PostgreSQL support, env var injection, HTTPS
3. **Chosen topology** — decide one platform combination; document why
4. **Backend deployment target** — platform, runtime, port, process manager, HTTPS termination
5. **Frontend deployment target** — platform, build command, env var injection for `NEXT_PUBLIC_API_BASE_URL`
6. **Database target** — managed PostgreSQL service; connection string format; migration execution
7. **Staging domain placeholders** — staging backend URL; staging frontend URL; confirm these will differ from local and production
8. **Secrets injection method** — how secrets are set on the chosen platform (platform env vars UI, CLI, secret store)
9. **Vapi staging configuration** — staging Vapi test assistant pointing at staging HTTPS API URL
10. **Staging limitations** — fake data only; no real clinic; no PHI; no production Vapi assistant
11. **Next step** — Module 96: Staging Environment Variable Matrix

### 3. Static contract tests

Create `backend/tests/test_staging_topology_plan_contract.py`:
- Plan doc exists
- Mentions at least one hosting platform by name
- Mentions managed PostgreSQL
- Mentions HTTPS for staging
- Mentions `NEXT_PUBLIC_API_BASE_URL` staging value
- Mentions `FRONTEND_CORS_ORIGINS` staging value
- Mentions staging domain placeholders distinct from localhost and production
- Mentions secrets injection method
- Mentions Vapi staging configuration
- Mentions fake data only / no PHI
- Mentions no deployment execution in this module

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 95
- `docs/claude/NEXT_MODULE.md` — Module 96: Staging Environment Variable Matrix

## What not to do

- Do not execute any deployment
- Do not provision real infrastructure
- Do not add real production secrets or real domain names
- Do not change backend/frontend code
- Do not start the Fabel 5/UX sprint
- Do not implement httpOnly cookie auth yet

## Acceptance

- `docs/deployment/STAGING_TOPOLOGY_PLAN.md` created
- Contract tests pass
- Full test suite passes (1765/1765 minimum)
- Commit: `Sprint 13 / Module 95 — Staging deployment topology plan`
