# Sprint 12 / Module 92 — Environment and Secrets Contract

Status: pending Module 91 commit.

## Context

Module 91 produced the production readiness inventory. The inventory identified 7 backend
env vars and 1 frontend env var that must be set for production. It documented 13 explicit
deployment blockers. Before writing a deployment runbook (Module 94), the project needs a
concrete contract for how secrets are structured, named, validated, and injected.

This module is docs-first and contract-tests-first. No code changes unless a missing
startup validation is discovered and is a single, safe, additive change.

## Scope

### 1. Read and audit current state

Read:
- `backend/.env.example` — updated in Module 91
- `docs/deployment/PRODUCTION_READINESS_INVENTORY.md` — env vars table (Section 2)
- `backend/app/core/jwt_tokens.py` — JWT_SECRET_KEY consumption
- `backend/app/core/webhook_provider_config.py` — VAPI/N8N/INTERNAL secret consumption
- `backend/app/main.py` — DATABASE_URL and FRONTEND_CORS_ORIGINS consumption
- `frontend/lib/api.ts` — NEXT_PUBLIC_API_BASE_URL consumption

### 2. Create `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md`

Sections:
1. **Purpose** — what this contract is and is not
2. **Canonical env var list** — complete table: name, required/optional, default,
   where consumed, what breaks if absent, production requirement
3. **Secret classification** — which vars are secrets (must not appear in logs, must
   be rotated), which are configuration (safe to log)
4. **Injection method options** — platform env vars, `.env` file on host, secrets
   manager; trade-offs for each
5. **`.env.example` policy** — what `.env.example` is for, what values are allowed,
   what must never appear
6. **Startup validation gaps** — what the backend currently does when a required secret
   is absent (returns 503 for DATABASE_URL; returns 401/503 for missing webhook secret;
   no validation at startup for JWT_SECRET_KEY being empty)
7. **Recommended startup guard** — a startup warning if JWT_SECRET_KEY or webhook
   secrets are absent or equal to a known placeholder value (log warning only; do not
   crash on startup)
8. **Secret rotation procedure** — when and how each secret should be rotated,
   downstream effects
9. **What not to do** — explicit list of anti-patterns

### 3. Static contract tests

Create `backend/tests/test_environment_secrets_contract.py`:
- Contract doc exists
- `.env.example` policy section exists in contract doc
- Contract mentions all 8 env vars (7 backend + 1 frontend)
- Contract classifies DATABASE_URL and JWT_SECRET_KEY as secrets
- Contract mentions startup validation / startup guard
- Contract mentions secret rotation

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 92
- `docs/claude/NEXT_MODULE.md` — Module 93: Production CORS/Auth/Domain Plan

## What not to do

- Do not add production secrets to any file
- Do not change auth logic, JWT signing, or webhook verification
- Do not add a startup crash (hard fail) for missing secrets — only a log warning
- Do not deploy anything
- Do not define which cloud provider or platform to use

## Acceptance

- `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` created
- Contract tests pass
- Full test suite passes (1654/1654 minimum)
- Commit: `Sprint 12 / Module 92 — Environment and secrets contract`
