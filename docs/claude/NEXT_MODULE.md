# Sprint 12 / Module 91 — Production Deployment Readiness Inventory

Status: pending Architecture Checkpoint 11 review.

## Context

Architecture Checkpoint 11 chose production deployment readiness as the next sprint
direction. The full local/test Vapi intake loop is proven (Sprint 11). Before expanding
features or redesigning the UI, the project needs an inventory of all deployment
blockers, required secrets, infrastructure components, and operational risks.

This module is docs-first. No code changes unless only static contract tests or docs
require it.

## Scope

### 1. Read and audit current state

Read:
- `backend/app/main.py` — env vars consumed at startup
- `backend/.env.example` — current documented env vars
- `backend/alembic.ini` — migration config
- `backend/migrations/versions/` — migration history
- `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` — current local runbook
- `docs/architecture/ARCHITECTURE_CHECKPOINT_11_POST_VAPI_DIRECTION_REVIEW.md` — secrets/gaps list

### 2. Create `docs/deployment/PRODUCTION_READINESS_INVENTORY.md`

Sections:
1. **Purpose** — what this document is and is not
2. **Required environment variables** — complete list with description, where used, current local-dev value, production requirement
3. **Infrastructure components** — what must be running in production: backend, frontend, PostgreSQL, Vapi (production config), n8n (if used), reverse proxy, domain/TLS
4. **Database strategy** — migration plan, managed DB service, connection pooling, backup
5. **Secrets handling strategy** — how secrets are injected (env file vs secrets manager vs platform), what must NEVER be in code
6. **CORS/domain strategy** — production frontend URL, backend URL, CORS policy for production
7. **Auth hardening gaps** — JWT sessionStorage → httpOnly cookie path, token refresh
8. **Vapi production configuration** — stable URL (not ngrok), machine auth headers for production
9. **n8n production configuration** — stable URL, HMAC setup
10. **Health and readiness** — current `/health` route, what a production readiness probe needs
11. **Production deployment blockers** — explicit list of items that must be resolved before first real deployment
12. **Not in scope** — what this inventory does not address

### 3. Update `.env.example`

Add any missing env vars discovered during the audit. Do not add real values — use placeholder descriptions only.

### 4. Static contract tests

Create `backend/tests/test_production_readiness_inventory_contract.py`:
- Inventory doc exists
- `.env.example` exists and contains key env var names
- No real secrets in `.env.example` (no passwords, tokens, or keys that look real)
- Inventory mentions all required env vars from `main.py`
- Inventory mentions PostgreSQL, JWT, CORS, Vapi

### 5. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 91
- `docs/claude/NEXT_MODULE.md` — Module 92: Environment and Secrets Contract

## What not to do

- Do not commit real credentials, passwords, or tokens
- Do not make infrastructure decisions in code — only document them
- Do not build production deployment infrastructure in this module
- Do not change backend routes, auth logic, or migration files
- Do not claim a production deployment timeline

## Acceptance

- `docs/deployment/PRODUCTION_READINESS_INVENTORY.md` created
- `.env.example` updated with any missing env vars
- Contract tests pass
- Full test suite passes (1625/1625 minimum)
- Commit: `Sprint 12 / Module 91 — Production deployment readiness inventory`
