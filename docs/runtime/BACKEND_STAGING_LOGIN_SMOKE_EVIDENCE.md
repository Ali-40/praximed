# Backend Staging Login Smoke Evidence — PraxisMed

**Date:** 2026-07-04
**Sprint:** Sprint 16 / Module 116
**Status:** PASS — backend direct authentication smoke confirmed

---

## 1. Purpose

This document records the real evidence from the backend direct authentication smoke
against the PraxisMed Railway staging backend using the fake staging clinic and user
provisioned in Module 115.

**Accuracy policy:** No step is marked PASS without real evidence from the real Railway
staging backend. No evidence is fabricated. No passwords, JWT tokens, bcrypt hashes,
or `DATABASE_URL` values appear in this document.

Staging uses fake/non-PHI data only. No real patient data. No production secrets.

---

## 2. Current Result

**Overall result: PASS**

All three endpoints responded as expected. The Railway backend can reach Railway
PostgreSQL; the `JWT_SECRET_KEY` environment variable is set and functioning; and the
fake staging clinic and user credentials authenticate correctly against the staging DB.

---

## 3. Evidence

### 3.1 Backend Health

| Evidence Item | Value | Status |
|---|---|---|
| Backend URL | `https://web-production-fd91d.up.railway.app` | **PASS** |
| `GET /health` HTTP status | `200` | **PASS** |
| `GET /health` response body | `{"status":"ok","service":"PraxisMed API"}` | **PASS** |

### 3.2 Backend Readiness

| Evidence Item | Value | Status |
|---|---|---|
| `GET /health/ready` HTTP status | `200` | **PASS** |
| `GET /health/ready` response body | `{"status":"ready","checks":{"app":"ok"}}` | **PASS** |

### 3.3 Backend Login Smoke

| Evidence Item | Value | Status |
|---|---|---|
| Endpoint | `POST https://web-production-fd91d.up.railway.app/auth/login` | **PASS** |
| `clinic_id` used | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` | **PASS** |
| `email` used | `doctor.staging@praximed.test` | **PASS** |
| `password` used | Not recorded — held in developer password manager only | **PASS** |
| HTTP status | `200` | **PASS** |
| Response fields present | `access_token`, `expires_in_seconds`, `token_type`, `user` | **PASS** |
| `access_token` present | Confirmed — value REDACTED; not recorded in this document | **PASS** |
| `token_type` | `bearer` | **PASS** |
| `expires_in_seconds` | Present in response | **PASS** |
| `user` object present | Confirmed — contains `id`, `clinic_id`, `email`, `role` | **PASS** |
| No secrets in evidence | Confirmed — token value, password, bcrypt hash, DATABASE_URL not recorded | **PASS** |

---

## 4. Safety Boundary

| Rule | Status |
|---|---|
| Password not recorded | CONFIRMED — plaintext staging password held in developer password manager only |
| JWT token value not recorded | CONFIRMED — `access_token` value shown as REDACTED; not captured in any document |
| Bcrypt hash not recorded | CONFIRMED — not visible in login flow; not recorded |
| `DATABASE_URL` not recorded | CONFIRMED — connection string not visible in login flow; not recorded |
| No real patient data | CONFIRMED — login uses fake staging identifiers only; no real patient records involved |
| Fake/non-PHI staging only | CONFIRMED — all staging data is synthetic; no real clinic or patient PII |
| Production PHI launch | **NO-GO** — Vercel frontend not deployed; CORS not wired to a real frontend URL; browser dashboard smoke not executed |

---

## 5. What This Proves

- **Railway backend can reach Railway PostgreSQL** — `GET /health/ready` → 200 confirms
  the DB connection pool is established; the `asyncpg` pool is healthy
- **`JWT_SECRET_KEY` is set and functional in the Railway staging environment** — the
  login endpoint issued a token without returning 503; `MissingJWTSecretError` was not raised
- **Fake staging clinic and user credentials authenticate correctly** — `POST /auth/login`
  with `clinic_id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056` and `email=doctor.staging@praximed.test`
  returned HTTP 200; `verify_password()` accepted the staging bcrypt hash
- **Backend issues a bearer token in staging** — `token_type=bearer`; `access_token` field
  is present in the response; JWT issuance pipeline (bcrypt verify → `create_access_token`)
  works end-to-end in Railway
- **All three staging health endpoints are reachable via HTTPS** — `/health`, `/health/ready`,
  `/auth/login` all responded at `https://web-production-fd91d.up.railway.app`

---

## 6. What This Does Not Prove

| Area | Status | Next Step |
|---|---|---|
| Vercel frontend deployed | NOT PROVEN | Module 117 |
| `NEXT_PUBLIC_API_BASE_URL` set in Vercel | NOT PROVEN | Module 117 |
| Browser login works via Vercel frontend | NOT PROVEN | Module 118 |
| CORS wired to real Vercel URL | NOT PROVEN | Module 118 |
| Dashboard renders after browser login | NOT PROVEN | Module 118 |
| Vapi test assistant pointed to staging | NOT PROVEN | Module 118 |
| Vapi test call creates appointment row | NOT PROVEN | Module 118 |
| n8n staging workflow configured | NOT PROVEN | Module 118 |
| Full staging smoke passed | NOT PROVEN | Module 119 |
| Production PHI readiness | NOT PROVEN | Production PHI launch remains NO-GO |

---

## 7. Remaining Blockers

| # | Blocker | Level | Next Step |
|---|---|---|---|
| 1 | Vercel frontend not deployed | **HIGH** | Module 117 |
| 2 | `NEXT_PUBLIC_API_BASE_URL` not set in Vercel | **HIGH** | Module 117 |
| 3 | `FRONTEND_CORS_ORIGINS` not set to Vercel URL in Railway | **HIGH** | Module 118 |
| 4 | CORS preflight not verified from browser | **HIGH** | Module 118 |
| 5 | Browser login via Vercel frontend not tested | **HIGH** | Module 118 |
| 6 | Dashboard smoke not executed | **HIGH** | Module 118 |
| 7 | Vapi test assistant not pointed to staging URL | **HIGH** | Module 118 |
| 8 | n8n staging workflow not configured | LOW (optional for initial smoke) | Module 118 |
| 9 | Full staging smoke not executed | **HIGH** | Module 119 |

---

## 8. Next Step — Module 117

**Sprint 16 / Module 117 — Vercel Frontend Deployment and API Wiring**

Now that the Railway backend URL is confirmed and backend login smoke is PASS, the next
step is to deploy the Vercel frontend and wire `NEXT_PUBLIC_API_BASE_URL`.

1. Create a Vercel project from the `frontend/` directory of this repo
2. Set `NEXT_PUBLIC_API_BASE_URL=https://web-production-fd91d.up.railway.app`
3. Deploy and capture the Vercel frontend URL
4. After the Vercel URL is known, set `FRONTEND_CORS_ORIGINS` on Railway backend
   to the exact Vercel HTTPS URL (no wildcard)
5. Redeploy Railway backend after `FRONTEND_CORS_ORIGINS` is set

Follow `docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` for exact steps.

Evidence to capture (no secrets):
- Vercel project name
- Vercel frontend URL
- Vercel build status (Success)
- Deployed commit SHA
- `NEXT_PUBLIC_API_BASE_URL` variable name confirmed in Vercel (not value)
- `GET <vercel-url>/login` → page renders (no 404)
- `FRONTEND_CORS_ORIGINS` set to exact Vercel URL confirmed in Railway (variable name only)
