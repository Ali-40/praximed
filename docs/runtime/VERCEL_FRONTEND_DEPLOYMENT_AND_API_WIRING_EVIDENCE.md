# Vercel Frontend Deployment and API Wiring Evidence — PraxisMed

**Date:** 2026-07-04
**Sprint:** Sprint 16 / Module 117
**Status:** PASS — Vercel frontend deployed; CORS wired; browser login and dashboard confirmed

---

## 1. Purpose

This document records the real evidence from deploying the PraxisMed Next.js frontend
to Vercel, wiring `NEXT_PUBLIC_API_BASE_URL` to the Railway backend, setting
`FRONTEND_CORS_ORIGINS` on the Railway backend, and confirming browser login and
dashboard load in deployed staging.

**Accuracy policy:** No step is marked PASS without real evidence from real deployed
services. No evidence is fabricated. No passwords, JWT tokens, bcrypt hashes,
`DATABASE_URL`, `JWT_SECRET_KEY`, or webhook secrets appear in this document.

Staging uses fake/non-PHI data only. No real patient data. No production secrets.

---

## 2. Current Result

**Overall result: PASS**

The Vercel frontend is deployed and reachable at `https://praximed.vercel.app`. The
Railway backend URL is wired via `NEXT_PUBLIC_API_BASE_URL`. `FRONTEND_CORS_ORIGINS`
is set to the exact Vercel URL on the Railway backend (no wildcard). Browser login
with the fake staging doctor succeeded. The dashboard loaded with all four sections
visible (Appointments, Patients, Notifications, Consultations — all showing zero rows,
which is the expected state before any Vapi test calls).

---

## 3. Evidence

### 3.1 Vercel Frontend Deployment

| Evidence Item | Value | Status |
|---|---|---|
| Vercel project deployed | Confirmed | **PASS** |
| Vercel frontend URL | `https://praximed.vercel.app` | **PASS** |
| Vercel deployment status | Ready | **PASS** |
| Frontend directory | `frontend/` (repo root → Vercel root = `frontend`) | **PASS** |
| `GET https://praximed.vercel.app/login` | Login page visible in browser | **PASS** |

### 3.2 API Base URL Wiring

| Evidence Item | Value | Status |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` set in Vercel | Confirmed (variable name only; value = Railway backend HTTPS URL) | **PASS** |
| Railway backend URL pointed to | `https://web-production-fd91d.up.railway.app` | **PASS** |

### 3.3 CORS Wiring

| Evidence Item | Value | Status |
|---|---|---|
| `FRONTEND_CORS_ORIGINS` set on Railway backend | `https://praximed.vercel.app` (exact URL; no wildcard) | **PASS** |
| Railway backend redeployed after CORS update | Confirmed | **PASS** |
| `GET /health` after Railway redeploy | HTTP 200 — `{"status":"ok","service":"PraxisMed API"}` | **PASS** |
| `GET /health/ready` after Railway redeploy | HTTP 200 | **PASS** |

### 3.4 Browser Login Smoke

| Evidence Item | Value | Status |
|---|---|---|
| `clinic_id` used | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` | **PASS** |
| `email` used | `doctor.staging@praximed.test` | **PASS** |
| `password` | Not recorded — held in developer password manager only | **PASS** |
| Browser login HTTP status | `200` | **PASS** |
| JWT token | Present in response — value not recorded | **PASS** |
| Browser login succeeded | Confirmed — login form accepted credentials | **PASS** |

### 3.5 Dashboard Load

| Evidence Item | Value | Status |
|---|---|---|
| Dashboard URL | `https://praximed.vercel.app/dashboard` | **PASS** |
| Dashboard loaded | Confirmed | **PASS** |
| Header | `PraxisMed / Clinic Dashboard` | **PASS** |
| Logout button | Visible | **PASS** |
| Clinic Overview section | Visible | **PASS** |
| Appointments card | Visible — count 0; "No appointment requests found." | **PASS** |
| Patients card | Visible — count 0; "No patients found." | **PASS** |
| Notifications card | Visible — count 0; "No notifications found." | **PASS** |
| Consultations card | Visible — count 0; "No consultations found." | **PASS** |
| Zero-row state | Expected — no Vapi test calls made yet; empty state is correct | **PASS** |
| Footer content | Local demo / fake development data wording — confirmed no real data | **PASS** |

---

## 4. Login Evidence Summary

| Field | Value |
|---|---|
| `clinic_id` | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` |
| `email` | `doctor.staging@praximed.test` |
| `password` | Not recorded |
| `access_token` | Not recorded (present in response; value REDACTED) |

---

## 5. Safety Boundary

| Rule | Status |
|---|---|
| Password not recorded | CONFIRMED — plaintext staging password held in developer password manager only |
| JWT token not recorded | CONFIRMED — token value was present in login response but not captured in any document |
| Bcrypt hash not recorded | CONFIRMED — not visible in any frontend or network evidence |
| `DATABASE_URL` not recorded | CONFIRMED — not visible in any frontend evidence |
| `JWT_SECRET_KEY` not recorded | CONFIRMED — not visible in any frontend evidence |
| Webhook secrets not recorded | CONFIRMED — `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `INTERNAL_WEBHOOK_SECRET` not visible or recorded |
| `FRONTEND_CORS_ORIGINS` — no wildcard | CONFIRMED — set to exact URL `https://praximed.vercel.app`; no `*` |
| No real patient data | CONFIRMED — all dashboard sections showed zero rows with empty-state messaging |
| Fake/non-PHI staging only | CONFIRMED — dashboard footer explicitly notes fake/local demo data; no real patient PII |
| Production PHI launch | **NO-GO** — Vapi staging test call not yet executed; full staging smoke loop not complete |

---

## 6. What This Proves

- **Vercel frontend deploys correctly from the `frontend/` directory** — Next.js 14.2.3
  build succeeded; no `output: 'standalone'` or `vercel.json` needed
- **Frontend can reach the Railway backend** — `NEXT_PUBLIC_API_BASE_URL` is correctly
  baked into the Vercel build; `POST /auth/login` was reachable from the browser
- **CORS allows the real Vercel origin** — browser login succeeded without a CORS error;
  `FRONTEND_CORS_ORIGINS=https://praximed.vercel.app` (no wildcard) is accepted by the
  backend `_cors_origins()` implementation
- **Browser login works with the fake staging doctor credentials** — JWT was issued;
  browser navigation to `/dashboard` succeeded
- **Dashboard loads and renders all four sections** — Appointments, Patients, Notifications,
  and Consultations all rendered with correct zero-row empty states
- **No auto-confirmed appointments** — Appointments card shows 0 rows; no `status=confirmed`
  row was automatically created; the no-auto-confirm constraint is intact

---

## 7. What This Does Not Prove

| Area | Status | Next Step |
|---|---|---|
| Vapi test assistant pointed to Railway staging URL | NOT PROVEN | Module 118 |
| Vapi test call creates appointment row in staging DB | NOT PROVEN | Module 118 |
| New appointment row appears in deployed dashboard | NOT PROVEN | Module 118 |
| Staff Confirm flow works in deployed dashboard | NOT PROVEN | Module 118 |
| n8n staging workflow configured | NOT PROVEN | Module 118 |
| Full staging smoke loop complete | NOT PROVEN | Module 118 |
| Production PHI readiness | NOT PROVEN | Production PHI launch remains NO-GO |

---

## 8. Next Verification — Module 118

**Sprint 16 / Module 118 — Vapi Staging Dashboard Loop Evidence**

Now that the full frontend/backend stack is deployed and browser login works, the final
staging smoke step is to verify the Vapi appointment intake loop end-to-end:

1. Configure the Vapi test assistant to point to the Railway backend:
   - Server URL: `https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request`
   - Header `X-Vapi-Scopes: vapi:tool` (singular — plural returns HTTP 403)
   - Header `X-Clinic-Ref: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056`
   - `VAPI_WEBHOOK_SECRET` must match the Railway backend env var (set in Railway; not recorded here)
2. Trigger a fake Vapi test call with synthetic caller data (no real phone numbers or PII)
3. Confirm the tool call returns HTTP 200
4. Confirm a new `appointment_requests` row appears in the Vercel dashboard with `status=new`
5. Confirm `action_required=True` on the new row (no auto-confirmation)
6. Test the staff Confirm button in the deployed dashboard (if UI supports it)
7. Confirm row updates to `status=confirmed` only after explicit staff action

Evidence to capture (no secrets):
- Vapi tool call HTTP status: expected 200
- Dashboard row count: expected 1 (new appointment)
- Row `status`: expected `new`
- Row `action_required`: expected `True`
- Staff Confirm result: `status=confirmed` after staff action
- Confirmation: no auto-confirmation observed
- Confirmation: no real patient PII in the Vapi test call data
