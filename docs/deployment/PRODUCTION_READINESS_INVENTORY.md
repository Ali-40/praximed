# Production Readiness Inventory — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 12 / Module 91
**Author:** Architecture Checkpoint 11 direction
**Status:** Inventory only — not a deployment guide, not a go-live checklist

---

## 1. Purpose

This document is an inventory of every item that must be resolved, configured, or
decided before PraxisMed can be deployed to a production environment for real clinic
use. It is based on a code audit of the current codebase as of Sprint 12 / Module 91.

**What this document is:**
- A complete inventory of required environment variables and where they are consumed
- A list of infrastructure components that must be running in production
- A description of the current database migration strategy and what changes are needed
- An identification of secrets that must be rotated and injected securely
- A list of explicit production blockers that must be resolved before first deployment

**What this document is not:**
- A deployment guide (no step-by-step deployment commands)
- A go-live timeline or schedule
- A CI/CD pipeline specification
- A decision on which cloud provider or hosting platform to use
- A promise that the items listed can be resolved in any particular sprint

---

## 2. Required Environment Variables

All environment variables consumed by the backend at runtime. Frontend variables are
listed separately. Variables are read at startup or on first request — none have
default fallbacks that are safe for production.

### 2.1 Backend Environment Variables

| Variable | Used In | Purpose | Local Dev Value | Production Requirement |
|---|---|---|---|---|
| `DATABASE_URL` | `main.py` (lifespan startup), `backend/migrations/env.py` (Alembic) | asyncpg connection pool; Alembic migration target | `postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local` | Full PostgreSQL connection string for the production managed DB service |
| `JWT_SECRET_KEY` | `backend/app/core/jwt_tokens.py` | HMAC-SHA256 key for signing and verifying JWT tokens | `local-dev-jwt-secret-key-change-in-production` | High-entropy random secret (32+ bytes); rotated per environment |
| `VAPI_WEBHOOK_SECRET` | `backend/app/core/webhook_provider_config.py` | HMAC-SHA256 key for verifying `X-Vapi-Signature` on `/webhooks/vapi/*` | `local-vapi-secret-change-me` | Must match the secret configured in the Vapi dashboard for the production assistant |
| `N8N_WEBHOOK_SECRET` | `backend/app/core/webhook_provider_config.py` | HMAC-SHA256 key for verifying `X-N8N-Signature` on `/webhooks/n8n/*` | `local-n8n-secret-change-me` | Must match the secret configured in the n8n production workflow |
| `INTERNAL_WEBHOOK_SECRET` | `backend/app/core/webhook_provider_config.py` | HMAC-SHA256 key for internal webhook routes | `local-internal-secret-change-me` | High-entropy random secret; not shared with external services |
| `FRONTEND_CORS_ORIGINS` | `main.py` (`_cors_origins()`) | Comma-separated list of allowed CORS origins; defaults to `localhost:3000` and `127.0.0.1:3000` if unset | _(unset; defaults apply)_ | Must be set to the production frontend URL(s); wildcard origins are never used |
| `APP_ENV` | `.env.example` (documented) | Application environment label | `local` | `production` |
| `API_HOST` | `.env.example` (documented) | Backend bind host | `127.0.0.1` | `0.0.0.0` (behind reverse proxy) or platform-managed |
| `API_PORT` | `.env.example` (documented) | Backend bind port | `8000` | Platform-managed |

**Note on `MACHINE_SERVICE_SECRET`:** Machine auth in the current codebase (`backend/app/core/machine_auth.py`) is header-based trust (`X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes`) — no separate HMAC secret is used for machine headers. Webhook HMAC secrets (`VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`) are the relevant secrets for those routes. A dedicated machine-level auth secret is a future hardening item.

### 2.2 Frontend Environment Variables

| Variable | Used In | Purpose | Local Dev Value | Production Requirement |
|---|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `frontend/lib/api.ts` | Base URL for all API calls; falls back to `http://127.0.0.1:8000` if unset | _(unset; fallback applies)_ | Must be set to the production backend URL (e.g., `https://api.praxismed.example.com`); the `http://127.0.0.1:8000` fallback must never reach production |

### 2.3 Missing From `.env.example`

The following variables are consumed by the backend but not documented in `backend/.env.example`:

- `JWT_SECRET_KEY`
- `VAPI_WEBHOOK_SECRET`
- `N8N_WEBHOOK_SECRET`
- `INTERNAL_WEBHOOK_SECRET`
- `FRONTEND_CORS_ORIGINS`

And the following frontend variable is not documented:

- `NEXT_PUBLIC_API_BASE_URL`

These will be added to `.env.example` as part of this module (with placeholder values only).

---

## 3. Infrastructure Components

Every component that must be running and reachable in a production deployment.

| Component | Current State | Production Requirement |
|---|---|---|
| **Backend (FastAPI / uvicorn)** | Started manually with `python -m uvicorn backend.app.main:app --reload` | Deployed as a process (systemd, Docker container, or platform service); `--reload` flag removed; served behind reverse proxy |
| **Frontend (Next.js)** | Started with `npm run dev` (development server) | Built with `npm run build` and served with `next start` (or exported and served statically); development server must not be used in production |
| **PostgreSQL** | Local Docker container (`docker-compose.postgres.yml`, port 5433) | Managed DB service (e.g., AWS RDS, Supabase, Railway, Render Postgres); automatic backups enabled; connection pooling configured |
| **Reverse proxy / TLS termination** | Not configured; app serves plain HTTP | Nginx, Caddy, or cloud load balancer required; TLS (HTTPS) must terminate at the proxy; the FastAPI app itself does not handle TLS |
| **Domain / DNS** | Not configured; local only (`localhost:8000`, `localhost:3000`) | Production domain(s) for backend and frontend; DNS A/CNAME records pointing to the deployment host; TLS certificates provisioned |
| **Vapi (production assistant)** | Test assistant only; server URL points to ngrok (ephemeral) | Production Vapi assistant configured with stable HTTPS backend URL; production webhook secret set; machine auth headers set for production clinic IDs |
| **n8n (if used)** | Local-dev only; workflow URL is ngrok or not configured | Production n8n instance or cloud-hosted n8n; stable webhook URL; HMAC secret matches `N8N_WEBHOOK_SECRET` in production env |
| **Tenant config files** | Disk files in `backend/tenants/configs/{clinic_id}/clinic_config.json` | Strategy for production config storage needed (disk mount, object storage, or DB-backed config); current disk approach requires the files to be present on the production host |

---

## 4. Database Strategy

### 4.1 Migration State

Alembic manages all schema changes. Migrations run explicitly via `backend/scripts/run_migrations.py`.

Current migration history (as of Sprint 12 / Module 91):

| Revision | File | Description |
|---|---|---|
| _(root)_ | `0001_initial_schema.py` | Creates all initial tables: `clinic_call_logs`, `appointment_requests`, `patients`, `consultation_sessions`, `clinic_notifications`, `clinic_users`, `audit_log`, `tenants` |
| `0002_password_hash` | `0002_add_password_hash_to_clinic_users.py` | Adds `password_hash VARCHAR(255)` to `clinic_users` |

No automatic migration runs on startup — migrations must be applied explicitly before the app starts against a new DB.

### 4.2 Production Database Gaps

| Gap | Detail |
|---|---|
| **Managed DB service** | Local Docker container is not a production database; needs AWS RDS, Supabase, Railway, or equivalent with automatic backups |
| **Connection pooling** | asyncpg pool is created in-process; for production, an external pooler (PgBouncer, Supabase pooler, RDS Proxy) is recommended for large concurrency |
| **Backup strategy** | No backup configuration exists; managed DB service must enable point-in-time recovery |
| **Migration run before first deploy** | Before the first production deploy, `run_migrations.py` must be run against the production `DATABASE_URL` to create the schema |
| **Multi-tenant data isolation** | `clinic_id` filtering is enforced at the application layer — no row-level security at the DB layer; this is the current design and requires correct `clinic_id` usage on every query |

---

## 5. Secrets Handling Strategy

### 5.1 Current State

All secrets are set as shell environment variables in local development. No secrets
manager is in use. Placeholder values are used locally. No real secrets are committed
to version control.

### 5.2 What Must NEVER Be in Code or Version Control

- `DATABASE_URL` (contains database credentials)
- `JWT_SECRET_KEY`
- `VAPI_WEBHOOK_SECRET`
- `N8N_WEBHOOK_SECRET`
- `INTERNAL_WEBHOOK_SECRET`
- Any production clinic ID, patient data, or real API key

### 5.3 Production Injection Options (decision deferred to Module 92)

| Option | Description | Suitable For |
|---|---|---|
| Platform env vars | Set via Render, Railway, Fly.io, Heroku, or Vercel dashboard | Small deploys; no separate secret manager needed |
| `.env` file on host | Injected at deploy time; not committed to VCS | Self-hosted; must restrict file permissions |
| AWS Secrets Manager / GCP Secret Manager / HashiCorp Vault | Programmatic secret retrieval at startup | Production-grade; requires additional startup code |

The choice of injection method is a Sprint 12 / Module 92 decision. This document records the requirement; Module 92 will define the contract.

### 5.4 Secret Rotation

All local-dev values must be rotated before first production deployment:
- `JWT_SECRET_KEY` — generate 32+ random bytes; rotating invalidates all existing JWTs
- `VAPI_WEBHOOK_SECRET` — must match Vapi dashboard setting; rotate both simultaneously
- `N8N_WEBHOOK_SECRET` — must match n8n workflow setting; rotate both simultaneously
- `INTERNAL_WEBHOOK_SECRET` — internal only; rotate on any suspected exposure

---

## 6. CORS / Domain Strategy

### 6.1 Current CORS Configuration

CORS is configured in `backend/app/main.py` via `CORSMiddleware`:

```python
allow_origins=_cors_origins(),     # explicit list only, never wildcard
allow_credentials=True,
allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "PUT"],
allow_headers=["Content-Type", "Authorization"],
```

The `_cors_origins()` function reads `FRONTEND_CORS_ORIGINS` from env. If unset, it
returns `["http://localhost:3000", "http://127.0.0.1:3000"]`. Wildcard `*` is never
returned.

### 6.2 Production CORS Gaps

| Gap | Detail |
|---|---|
| `FRONTEND_CORS_ORIGINS` not set | Production frontend domain is unknown; must be set before deployment |
| No wildcard — correct | The no-wildcard policy is correct and must be preserved |
| Both backend and frontend domains must be known | CORS origin must exactly match the frontend scheme + domain + port as seen by the browser |

### 6.3 Production Domain Plan (deferred to Module 93)

- Backend URL (e.g., `https://api.praxismed.example.com`)
- Frontend URL (e.g., `https://app.praxismed.example.com`)
- `FRONTEND_CORS_ORIGINS` must be set to the production frontend URL(s)
- `NEXT_PUBLIC_API_BASE_URL` must be set to the production backend URL

Domain selection and registration are outside the scope of this inventory.

---

## 7. Auth Hardening Gaps

### 7.1 JWT Storage

The current implementation stores the JWT access token in `sessionStorage`:

```typescript
// frontend/lib/api.ts
const token = sessionStorage.getItem("access_token");
```

**Risk:** `sessionStorage` is accessible to JavaScript running in the same origin.
An XSS vulnerability would allow a malicious script to read the token and impersonate
the authenticated user.

**Target state:** httpOnly cookies, which are inaccessible to JavaScript and therefore
immune to token theft via XSS. This requires a backend change (set-cookie on login
response) and a frontend change (remove manual `Authorization` header injection;
let browser send cookie automatically).

**Current label:** Local-dev only. The `sessionStorage` approach is intentionally
labeled as local-dev in the UI footer and code comments.

### 7.2 Token Refresh

No token refresh endpoint exists. When a JWT expires, the user sees a generic API
error (401) with no auto-redirect to the login page.

**Risk:** Poor UX in production; staff sessions expire without a clear recovery path.

**Target state:** A `/auth/refresh` endpoint that issues a new access token from a
long-lived refresh token (stored in an httpOnly cookie). Frontend intercepts 401
responses and attempts refresh before redirecting.

### 7.3 Auth Hardening Priority

Both items (httpOnly cookie and token refresh) are deferred to Sprint 12 / Module 93
(Production CORS/Auth/Domain Plan). They must be resolved before a production deployment
serves real clinic staff.

---

## 8. Vapi Production Configuration

### 8.1 Current State

The Vapi integration is proven for the local/test environment:
- Test assistant configured in the Vapi dashboard (not production)
- Server URL pointed at an ngrok tunnel (`https://<id>.ngrok-free.app/...`)
- Machine auth headers set to local-dev clinic UUID

### 8.2 Production Gaps

| Gap | Detail |
|---|---|
| **Stable HTTPS URL** | ngrok is ephemeral; each restart generates a new URL. Production requires a stable HTTPS URL (e.g., `https://api.praxismed.example.com/vapi/tools/capture-appointment-request`) |
| **Production assistant** | Test assistant only; a production Vapi assistant must be created and configured separately |
| **Production machine auth headers** | Machine auth headers (`X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes`) in the Vapi assistant must use the production clinic UUID(s) — not the local `11111111-...` seed UUID |
| **Production webhook secret** | `VAPI_WEBHOOK_SECRET` on the backend must match the signing secret configured in the Vapi production assistant |
| **Scope** | `X-Vapi-Scopes: vapi:tool` (singular) — confirmed in testing; must be set correctly in production assistant configuration |

### 8.3 What Is Not Needed Now

No code changes are required for Vapi production support. The adapter
(`adapt_vapi_tool_call_body`) handles the nested tool-call shape. Only configuration
(URL, secrets, machine auth headers) changes are needed.

---

## 9. n8n Production Configuration

### 9.1 Current State

n8n integration is proven for local/test (Module 58). The webhook route
`POST /webhooks/n8n/calendar-sync` uses HMAC verification via `N8N_WEBHOOK_SECRET`.

### 9.2 Production Gaps

| Gap | Detail |
|---|---|
| **Stable webhook URL** | n8n workflow must point to the stable production backend URL |
| **Production n8n instance** | A cloud-hosted or self-hosted n8n instance with the production workflow configured |
| **HMAC secret** | `N8N_WEBHOOK_SECRET` on the backend must match the secret set in the n8n workflow's HTTP request node |
| **Machine auth headers in n8n** | n8n workflow must send `X-Service-Name: n8n`, `X-Service-Clinic-Id: <production-clinic-uuid>`, `X-Service-Scopes: calendar:sync` |

---

## 10. Health and Readiness

### 10.1 Current Health Route

`GET /health` returns:

```json
{"status": "ok"}
```

No DB check, no dependency check. Returns 200 as long as the FastAPI process is alive.

### 10.2 Production Readiness Probe Gaps

| Gap | Detail |
|---|---|
| **No DB health check** | The `/health` route does not verify DB connectivity; a process can be alive while the DB pool is broken (`app.state.db_pool is None`) |
| **No dependency checks** | No check for critical env vars, DB connection, or config loader state |
| **Suitable for liveness** | The current `/health` is a valid liveness probe (is the process responding?) |
| **Not suitable for readiness** | A readiness probe should confirm the DB pool is initialized and at least one connection can be acquired |

**Recommended addition** (deferred to Module 94 or the deployment runbook):
- `GET /health/ready` — checks `app.state.db_pool is not None` and acquires a test connection; returns 503 if either check fails

---

## 11. Production Deployment Blockers

The following items must be resolved before PraxisMed can serve real clinic data.
Items are listed in priority order. No item may be skipped.

| # | Blocker | Risk if Not Resolved |
|---|---|---|
| 1 | **All secrets rotated and injected via a non-VCS mechanism** | Local-dev secrets in production; any compromise exposes all clinics |
| 2 | **`FRONTEND_CORS_ORIGINS` set to production frontend URL** | Browser blocks all API calls from production frontend (CORS error) |
| 3 | **`NEXT_PUBLIC_API_BASE_URL` set to production backend URL** | Frontend falls back to `http://127.0.0.1:8000`; all API calls fail in production |
| 4 | **Production PostgreSQL (managed service) provisioned and migrations applied** | No persistent data; no DB connectivity |
| 5 | **HTTPS / TLS termination configured (reverse proxy or cloud LB)** | Backend serves plain HTTP; credentials and PHI transmitted unencrypted |
| 6 | **Production domain(s) registered and DNS configured** | Backend and frontend not reachable |
| 7 | **Frontend built with `npm run build` / `next start`** | Development server (`npm run dev`) must not serve production traffic |
| 8 | **JWT storage changed from `sessionStorage` to httpOnly cookie** | XSS-accessible token; real clinic staff credentials at risk |
| 9 | **Vapi production assistant configured with stable HTTPS URL and production secrets** | Vapi cannot call the production backend; appointment intake non-functional |
| 10 | **n8n production workflow configured with stable HTTPS URL and production secrets** | n8n cannot call the production backend; calendar sync non-functional |
| 11 | **Tenant config files present on production host** | `ClinicConfigLoader` fails for any clinic without a disk config file; Vapi intake returns 503 |
| 12 | **Token refresh endpoint or session expiry UX** | Expired sessions cause silent failures; staff cannot recover without a manual re-login |
| 13 | **Production readiness probe (`GET /health/ready`)** | Reverse proxy or orchestrator cannot distinguish a degraded app from a healthy one |

---

## 12. Not in Scope

The following items are explicitly not addressed in this inventory and are deferred
to later modules or future sprints:

- CI/CD pipeline (automated test runs, deployment automation)
- Doctor-facing UI/UX polish (Fabel 5 / Claude frontend tooling evaluation — confirmed deferred after Sprint 12)
- Appointment workflow expansion (Reject, Assign, Callback, Archive actions)
- Calendar handoff on Confirm (no calendar event is created today; this is future)
- Patient notification on Confirm
- Production Vapi assistant speech/prompt design
- Multi-region or high-availability database setup
- Log aggregation, APM, or observability stack
- GDPR / Austrian healthcare compliance audit
- Rate limiting or API abuse protection
- Patient-facing portal or booking interface
