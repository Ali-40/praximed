# Environment and Secrets Contract — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 12 / Module 92
**Status:** Contract only — no production deployment, no auth refactor, no cookie migration

---

## A. Purpose

This document defines the canonical environment variable contract for PraxisMed across
all deployment tiers. It specifies which variables are required, what kind of values they
hold, who owns them, and how they must be stored and rotated.

**What this document is:**
- The single source of truth for every env var the backend and frontend consume
- A classification of which vars are secrets vs. configuration
- Storage and rotation policy for all secrets
- Logging safety rules for secrets and PHI

**What this document is not:**
- A deployment guide (no step-by-step deploy commands)
- A go-live checklist (that is Module 94)
- An auth refactor plan (httpOnly cookie path is Module 93)
- A CI/CD pipeline specification
- A cloud provider or hosting platform decision

No real secrets are in this document. No production deployment occurs in this module.

---

## B. Environment Tiers

PraxisMed targets four deployment tiers. Each tier has different expectations for
secrets type, external exposure, and data sensitivity.

### B.1 Local (Developer Workstation)

| Property | Value |
|---|---|
| **Purpose** | Development and manual testing |
| **Data type** | Fake/seed data only; deterministic UUIDs; no real patients |
| **Secrets type** | Placeholder values; local dev secrets; must never match staging/production |
| **External exposure** | None; all services run on `localhost`; ngrok allowed for Vapi/n8n testing only |
| **Vapi usage** | Test Vapi assistant only; ngrok tunnel as server URL |
| **n8n usage** | Local or ngrok-tunneled n8n workflow |
| **Database** | Local Docker PostgreSQL (`docker-compose.postgres.yml`, port 5433) |
| **Backend URL** | `http://127.0.0.1:8000` |
| **Frontend URL** | `http://localhost:3000` |
| **Secrets storage** | Shell exports or untracked `backend/.env` file |

### B.2 Test / CI

| Property | Value |
|---|---|
| **Purpose** | Automated test runs (pytest); static contract verification |
| **Data type** | No real data; in-memory or mocked dependencies; no real DB calls |
| **Secrets type** | CI secret store (e.g., GitHub Actions secrets); placeholder values for non-secret config vars |
| **External exposure** | None; tests are isolated; no external service calls |
| **Vapi usage** | Not used; all Vapi paths are mocked or tested via static contracts |
| **n8n usage** | Not used |
| **Database** | Not used in unit/contract tests; no external DB calls |
| **Backend URL** | N/A (tests run in-process via FastAPI TestClient) |
| **Frontend URL** | N/A |
| **Secrets storage** | CI secret store; never in `.env.example` |

### B.3 Staging

| Property | Value |
|---|---|
| **Purpose** | Pre-production validation; stakeholder demo; QA testing |
| **Data type** | Synthetic test data only; no real patient records |
| **Secrets type** | High-entropy secrets; distinct from local and production; never reused |
| **External exposure** | HTTPS only; accessible to authorized testers; not public-facing |
| **Vapi usage** | Staging Vapi assistant; stable HTTPS backend URL (not ngrok) |
| **n8n usage** | Staging n8n workflow; stable HTTPS URL |
| **Database** | Managed PostgreSQL (not Docker); separate from production DB |
| **Backend URL** | `https://api-staging.praxismed.example.com` (or equivalent stable HTTPS URL) |
| **Frontend URL** | `https://app-staging.praxismed.example.com` |
| **Secrets storage** | Deployment platform secret manager or platform env vars |

### B.4 Production

| Property | Value |
|---|---|
| **Purpose** | Real clinic use; real staff; real patient intake |
| **Data type** | Real PHI; real clinic data; GDPR-applicable |
| **Secrets type** | High-entropy production secrets; independent of all other tiers; rotated per policy |
| **External exposure** | HTTPS only; domain-restricted CORS; no wildcard origins |
| **Vapi usage** | Production Vapi assistant; stable HTTPS backend URL |
| **n8n usage** | Production n8n workflow; stable HTTPS URL |
| **Database** | Managed PostgreSQL with backups and point-in-time recovery |
| **Backend URL** | `https://api.praxismed.example.com` (or equivalent) |
| **Frontend URL** | `https://app.praxismed.example.com` (or equivalent) |
| **Secrets storage** | Platform secret manager (AWS Secrets Manager, GCP Secret Manager, Vault, or platform env vars injected at deploy time) |

---

## C. Backend Environment Variable Contract

All variables consumed by the FastAPI backend at startup or on first request.

### C.1 Complete Table

| Variable | Local | Test/CI | Staging | Production | Secret? | Failure Mode if Absent |
|---|---|---|---|---|---|---|
| `DATABASE_URL` | Required | Not required (no real DB) | Required | Required | Yes | App starts; DB-backed routes return HTTP 503 until set |
| `JWT_SECRET_KEY` | Required | Required (placeholder ok) | Required | Required | Yes | `MissingJWTSecretError` raised on first JWT operation; login returns 500 |
| `VAPI_WEBHOOK_SECRET` | Required | Not required | Required | Required | Yes | `MissingWebhookSecretError` on first Vapi webhook call; returns HTTP 503 |
| `N8N_WEBHOOK_SECRET` | Required | Not required | Required | Required | Yes | `MissingWebhookSecretError` on first n8n webhook call; returns HTTP 503 |
| `INTERNAL_WEBHOOK_SECRET` | Required | Not required | Required | Required | Yes | `MissingWebhookSecretError` on first internal webhook call; returns HTTP 503 |
| `FRONTEND_CORS_ORIGINS` | Optional | Not required | Required | Required | No | Defaults to `http://localhost:3000,http://127.0.0.1:3000`; production frontend blocked by CORS if not set |
| `POSTGRES_DB` | Required (Docker) | Not required | Required (DB provisioning) | Required (DB provisioning) | No | Docker Compose fails; app unaffected if `DATABASE_URL` is set directly |
| `POSTGRES_USER` | Required (Docker) | Not required | Required (DB provisioning) | Required (DB provisioning) | No | As above |
| `POSTGRES_PASSWORD` | Required (Docker) | Not required | Required (DB provisioning) | Required (DB provisioning) | Yes | As above |
| `APP_ENV` | Optional | Optional | Optional | Optional | No | No failure; informational only |
| `API_HOST` | Optional | Optional | Optional | Optional | No | No failure; used only by startup scripts |
| `API_PORT` | Optional | Optional | Optional | Optional | No | No failure; used only by startup scripts |

### C.2 Variable Descriptions

**`DATABASE_URL`**
- **Format:** `postgresql://<user>:<password>@<host>:<port>/<dbname>`
- **Consumed by:** `backend/app/main.py` (lifespan startup pool creation), `backend/migrations/env.py` (Alembic)
- **Owner:** Database administrator / deployment platform
- **Local example:** `postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local`
- **Production requirement:** Full connection string for the managed PostgreSQL service; must not be the local Docker URL
- **Rotation:** Rotate DB password → update `DATABASE_URL` → redeploy; causes brief downtime if pool is not gracefully cycled

**`JWT_SECRET_KEY`**
- **Format:** Arbitrary string; minimum 32 characters of high entropy recommended
- **Consumed by:** `backend/app/core/jwt_tokens.py` (`_get_jwt_secret()`) — all login and token-verify operations
- **Owner:** Platform secret manager / deployment operator
- **Local placeholder:** `local-dev-jwt-secret-key-change-in-production`
- **Production requirement:** High-entropy random value; never the local placeholder
- **Rotation:** Rotating invalidates all active sessions; all logged-in users must re-authenticate

**`VAPI_WEBHOOK_SECRET`**
- **Format:** Arbitrary string; high entropy recommended
- **Consumed by:** `backend/app/core/webhook_signature.py` — HMAC-SHA256 verification on `POST /webhooks/vapi/*`
- **Owner:** Shared between PraxisMed backend and Vapi dashboard
- **Local placeholder:** `local-vapi-secret-change-me`
- **Production requirement:** Must match the HMAC signing secret configured in the Vapi production assistant webhook settings
- **Rotation:** Requires simultaneous update in Vapi dashboard and backend; brief window of 401 errors during rollover

**`N8N_WEBHOOK_SECRET`**
- **Format:** Arbitrary string; high entropy recommended
- **Consumed by:** `backend/app/core/webhook_signature.py` — HMAC-SHA256 verification on `POST /webhooks/n8n/*`
- **Owner:** Shared between PraxisMed backend and n8n workflow
- **Local placeholder:** `local-n8n-secret-change-me`
- **Production requirement:** Must match the secret in the n8n HTTP request node's header signing configuration
- **Rotation:** Requires simultaneous update in n8n workflow and backend

**`INTERNAL_WEBHOOK_SECRET`**
- **Format:** Arbitrary string; high entropy recommended
- **Consumed by:** `backend/app/core/webhook_signature.py` — HMAC-SHA256 verification on `POST /webhooks/internal/*`
- **Owner:** PraxisMed internal services only; not shared with Vapi or n8n
- **Local placeholder:** `local-internal-secret-change-me`
- **Rotation:** Internal only; no external service coordination required

**`FRONTEND_CORS_ORIGINS`**
- **Format:** Comma-separated list of origin strings, e.g. `https://app.praxismed.example.com`
- **Consumed by:** `backend/app/main.py` (`_cors_origins()`) — FastAPI CORSMiddleware
- **Owner:** Deployment operator; must match the actual frontend URL
- **Local value:** Not set; defaults apply (`http://localhost:3000`, `http://127.0.0.1:3000`)
- **Production requirement:** Set to the production frontend HTTPS URL(s); wildcard `*` is never used and never returned
- **Rotation:** Config change only; no secrets involved

**`POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD`**
- **Purpose:** Docker Compose DB provisioning variables (not consumed by the app directly; `DATABASE_URL` is the app-facing var)
- **Local value:** `praxismed_local`, `praxismed`, `praxismed_local_password`
- **Production requirement:** Managed DB service credentials; `POSTGRES_PASSWORD` is a secret

---

## D. Frontend Environment Variable Contract

Variables consumed by the Next.js frontend at build time or runtime.

| Variable | Classification | Local Value | Staging Value | Production Value | Failure Mode |
|---|---|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Public (exposed to browser) | `http://127.0.0.1:8000` (fallback default in code) | `https://api-staging.praxismed.example.com` | `https://api.praxismed.example.com` | Fallback to `http://127.0.0.1:8000`; all API calls fail silently in non-local environments |

**`NEXT_PUBLIC_API_BASE_URL`**
- **Format:** Full HTTPS URL with no trailing slash
- **Consumed by:** `frontend/lib/api.ts` — prefixed to every API call path
- **Classification:** Public (`NEXT_PUBLIC_` prefix exposes value to the browser); **not a secret**
- **Local:** Not required (falls back to `http://127.0.0.1:8000`); set in `frontend/.env.local`
- **Production:** Must be set to the production backend HTTPS URL in the frontend build environment or platform; the `http://127.0.0.1:8000` fallback must never reach production

---

## E. Secret Generation Rules

The following rules apply to all secrets at every tier except local development.

1. **High entropy:** Each secret must be generated from a cryptographically secure random
   source. Minimum 32 bytes of entropy. Example (openssl):
   ```
   openssl rand -hex 32
   ```

2. **Independent values:** Each secret (`JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`,
   `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET`) must be a unique value. No reuse
   across secrets or across tiers.

3. **No local-dev values in staging/production:** The placeholder values in
   `.env.example` (e.g. `local-dev-jwt-secret-key-change-in-production`) must never
   appear in staging or production environments.

4. **No secrets in git, docs, logs, or screenshots:** Secrets must never be committed
   to version control, pasted in documentation, included in log output, or captured in
   screenshots or screen recordings shared outside the team.

5. **Rotation without code change:** The value of every secret must be changeable by
   updating the env var and redeploying, with no code change required. No secret is
   hardcoded in source.

6. **Separate DB passwords per tier:** The `POSTGRES_PASSWORD` in `DATABASE_URL` must
   differ across local, staging, and production environments.

---

## F. Rotation Policy

| Secret | When to Rotate | Impact | Coordination Needed |
|---|---|---|---|
| `JWT_SECRET_KEY` | On suspected exposure; minimum every 6–12 months in production; on every environment rebuild | All active sessions invalidated; all users must re-login | None (self-contained); announce brief forced re-login to clinic staff |
| `VAPI_WEBHOOK_SECRET` | On suspected exposure; when rotating Vapi assistant configuration; minimum annually | Vapi webhook calls fail (HTTP 401) until both sides updated | Must update Vapi dashboard webhook signing secret simultaneously with backend env var |
| `N8N_WEBHOOK_SECRET` | On suspected exposure; when rotating n8n workflow configuration; minimum annually | n8n webhook calls fail (HTTP 401) until both sides updated | Must update n8n workflow HTTP header configuration simultaneously |
| `INTERNAL_WEBHOOK_SECRET` | On suspected exposure; minimum annually | Internal webhook calls fail (HTTP 401) | No external coordination; PraxisMed internal only |
| `POSTGRES_PASSWORD` (in `DATABASE_URL`) | On suspected exposure; when replacing DB instance; minimum annually | DB connections fail until pool is recycled with new URL | Update managed DB service password → update `DATABASE_URL` → redeploy; may require brief downtime |

**Rollback risk:** Rotating a shared secret (Vapi, n8n) without updating both sides
simultaneously causes a brief window of 401 errors. Coordinate the update sequence:
update the backend env var first (or simultaneously with the external service), verify,
then complete the rollover.

---

## G. Storage Rules

| Tier | Where Secrets Live | What Must Never Happen |
|---|---|---|
| **Local** | Untracked `backend/.env` file (not committed) or shell exports | Do not commit `.env` files; do not export secrets in shell history files |
| **Test / CI** | CI secret store (e.g., GitHub Actions Secrets, GitLab CI Variables) | Never inline secret values in `.yml` workflow files |
| **Staging** | Deployment platform secret manager or platform environment variables | Never set staging secrets in `backend/.env.example` |
| **Production** | Platform secret manager (AWS Secrets Manager, GCP Secret Manager, Vault, or platform env vars injected at deploy time) | Never set production secrets in source code, docs, or `.env.example` |

**Rule:** `backend/.env.example` contains placeholder values only. It documents the
variable names and formats. It must never contain real secrets for any environment.

---

## H. Environment File Rules

| File | Status | Contents |
|---|---|---|
| `backend/.env.example` | Committed to git | Placeholder values only; all backend env var names documented |
| `backend/.env` | Untracked (git-ignored) | Real local-dev values; created by developer from `.env.example` |
| `frontend/.env.example` | Committed to git | Placeholder values only; `NEXT_PUBLIC_API_BASE_URL` documented |
| `frontend/.env.local` | Untracked (Next.js-ignored by default) | Real local-dev value for `NEXT_PUBLIC_API_BASE_URL` if needed |

**Rule:** Frontend `NEXT_PUBLIC_*` variables are not secrets — they are exposed to the
browser at runtime. Backend secrets (`JWT_SECRET_KEY`, webhook secrets, `DATABASE_URL`)
must never appear in frontend env files or be passed to the frontend build.

---

## I. CORS / Domain Contract

| Tier | `FRONTEND_CORS_ORIGINS` Value | Rule |
|---|---|---|
| **Local** | _(not set)_ → defaults to `http://localhost:3000,http://127.0.0.1:3000` | Only localhost origins; no ngrok origin in CORS |
| **Test / CI** | Not applicable | CORS middleware not tested in unit tests |
| **Staging** | `https://app-staging.praxismed.example.com` | Explicit HTTPS staging origin only |
| **Production** | `https://app.praxismed.example.com` | Explicit HTTPS production origin only |

**Hard rules:**
- Wildcard `*` is never used in `FRONTEND_CORS_ORIGINS`. The `_cors_origins()` function
  in `main.py` never returns a wildcard regardless of env var value.
- ngrok URLs must never be set as production CORS origins. ngrok is allowed only as a
  local testing tunnel for Vapi/n8n end-to-end smoke tests.
- The production backend URL must be served over HTTPS. Plain HTTP is never acceptable
  for production traffic.

---

## J. Vapi / n8n Production Contract

### J.1 What Is Allowed in Local / Test

- ngrok tunnel as the Vapi server URL for local smoke testing
- Test Vapi assistant (not production)
- Local seed clinic UUID (`11111111-1111-1111-1111-111111111111`)
- Placeholder machine auth secrets

### J.2 Production Requirements

**Vapi:**

| Requirement | Value |
|---|---|
| Server URL | Stable HTTPS URL — `https://api.praxismed.example.com/vapi/tools/capture-appointment-request` (no ngrok) |
| Machine auth header `X-Vapi-Service-Name` | `vapi` |
| Machine auth header `X-Vapi-Clinic-Id` | Production clinic UUID (not the local `11111111-...` seed UUID) |
| Machine auth header `X-Vapi-Scopes` | `vapi:tool` (singular — `vapi:tools` plural is rejected with HTTP 403) |
| Webhook secret | `VAPI_WEBHOOK_SECRET` must match the Vapi production assistant signing secret |

**n8n:**

| Requirement | Value |
|---|---|
| Webhook URL | Stable HTTPS URL — `https://api.praxismed.example.com/webhooks/n8n/calendar-sync` (no ngrok) |
| Machine auth header `X-Service-Name` | `n8n` |
| Machine auth header `X-Service-Clinic-Id` | Production clinic UUID |
| Machine auth header `X-Service-Scopes` | `calendar:sync` |
| Webhook secret | `N8N_WEBHOOK_SECRET` must match the n8n workflow signing secret |

### J.3 Clinic ID Security Rule

The `clinic_id` used to identify the tenant in every Vapi tool call must come from the
machine auth header (`X-Vapi-Clinic-Id`), not from patient-supplied arguments. The
`adapt_vapi_tool_call_body` adapter enforces this: any `clinic_ref` in the Vapi tool
call arguments is silently ignored; the machine auth header is always the authoritative
source. This rule must be maintained in all future adapter changes.

---

## K. Database Contract

| Tier | Database | Notes |
|---|---|---|
| **Local** | Docker PostgreSQL 16 (`docker-compose.postgres.yml`, port 5433) | Ephemeral; data lost when volume removed |
| **Test / CI** | No real DB; contract and unit tests use mocks / no DB calls | Never configure a real DB in CI for unit/contract tests |
| **Staging** | Managed PostgreSQL (RDS, Supabase, Railway, or equivalent) | Separate from production; regular backups |
| **Production** | Managed PostgreSQL with automated backups, point-in-time recovery | Credentials in secret manager; no direct access from app code except via `DATABASE_URL` |

**Rules:**
- Alembic migrations must be applied explicitly before first app traffic against any
  DB instance. `run_migrations.py` must be run as a pre-deploy step.
- No seed data (`seed_local_data.py`) or demo users in staging or production databases.
- The local `11111111-...` deterministic UUID must never appear in a production database
  as a real clinic identifier.
- Connection pooling (PgBouncer or managed pooler) is recommended for production
  workloads with concurrent requests.

---

## L. Logging / Secrets Safety

The following items must never appear in application logs, error messages, or audit records:

| What | Why |
|---|---|
| Raw values of `JWT_SECRET_KEY`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET` | Secret exposure via log aggregation |
| Full `Authorization: Bearer <token>` header values | JWT token theft via logs |
| Full `DATABASE_URL` value (contains password) | DB credential exposure |
| Raw Vapi/n8n tool call bodies with patient names, phone numbers, or transcript text | PHI exposure in logs |
| Raw `patient_name`, `caller_phone`, `date_of_birth` from any API request before validation | PHI in logs |

**What is allowed in logs:**
- `clinic_id` (not PHI; a tenant identifier)
- `call_id` (non-identifiable session reference)
- HTTP method and path (no query params that contain PHI)
- HTTP status codes
- Timing and duration
- Error type (not error detail containing raw secrets or PHI)
- Audit log entries per `audit_logger` policy (PHI policy must be reviewed before production)

**Current state:** The `adapt_vapi_tool_call_body` adapter does not log the raw body.
The `raw_payload` field is stored in the DB `raw_payload` column for audit purposes —
this column must be treated as PHI-containing and access-controlled accordingly.

---

## M. Pre-Deployment Checklist

Before the first production deployment, confirm each item:

- [ ] All required env vars set via secret manager or platform env (not `.env.example`)
- [ ] No placeholder / local-dev secret values in staging or production env
- [ ] `FRONTEND_CORS_ORIGINS` set to production HTTPS frontend URL
- [ ] `NEXT_PUBLIC_API_BASE_URL` set to production HTTPS backend URL
- [ ] Stable HTTPS domain provisioned and TLS certificates configured
- [ ] Production PostgreSQL provisioned; `DATABASE_URL` points to it
- [ ] Alembic migrations applied against production DB before first deploy
- [ ] No seed data or local UUIDs in production DB
- [ ] `npm run build` + `next start` used for frontend (not `npm run dev`)
- [ ] Vapi production assistant configured with stable HTTPS backend URL
- [ ] Vapi machine auth headers set with production clinic UUID (not `11111111-...`)
- [ ] n8n production workflow configured with stable HTTPS backend URL
- [ ] All secrets rotated from local-dev placeholder values
- [ ] No ngrok URLs in any production env var
- [ ] Backend served behind HTTPS reverse proxy
- [ ] Token storage decision documented (sessionStorage → httpOnly cookie path, Module 93)

---

## N. Explicit Non-Goals

The following are explicitly out of scope for this module:

- No production deployment
- No auth refactor (httpOnly cookie migration is Module 93)
- No Fabel 5 / frontend UX sprint
- No appointment workflow expansion (Reject, Assign, Archive actions)
- No CI/CD pipeline definition
- No cloud provider or hosting platform selection
- No GDPR / healthcare compliance audit
- No rate limiting or abuse protection configuration
- No calendar handoff or patient notification implementation
