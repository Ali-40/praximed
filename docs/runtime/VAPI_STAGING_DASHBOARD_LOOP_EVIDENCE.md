# Vapi Staging Dashboard Loop Evidence — PraxisMed

**Date:** 2026-07-05
**Sprint:** Sprint 16 / Module 118B
**Status:** PASS

---

## 1. Purpose

This document records the real evidence that the PraxisMed Vapi staging dashboard loop
works end-to-end against live deployed staging services:

- Vapi tool call reaches the Railway backend
- Railway backend inserts a fake `appointment_requests` row with `status=new` and `action_required=True`
- Vercel dashboard displays the new row
- Staff Confirm updates the row to `status=confirmed` with no auto-confirmation

**Accuracy policy:** No step is marked PASS without real proof from real external staging
services. No evidence is fabricated.

Staging uses fake/non-PHI data only. Patient name used: "Test Patient". No real patient
data. No production PHI. No production secrets.

---

## 2. Current Result

**Overall result: PASS**

The full Vapi staging dashboard loop is confirmed against live deployed staging services:

- Vapi tool call received by Railway backend ✓
- Fake `appointment_requests` rows inserted ✓
- Vercel dashboard at `https://praximed.vercel.app/dashboard` displayed the rows ✓
- Staff Confirm updated rows to `status=confirmed` ✓
- No auto-confirmation observed ✓

---

## 3. Prerequisites (all PASS from prior modules)

| Prerequisite | Module | Status |
|---|---|---|
| Railway backend deployed and `/health` → 200 | Module 112 | **PASS** |
| Railway PostgreSQL migrated; 4 tables confirmed | Module 114 | **PASS** |
| Fake staging clinic provisioned (`id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056`) | Module 115 | **PASS** |
| Fake staging user provisioned (`doctor.staging@praximed.test`) | Module 115 | **PASS** |
| Backend login smoke PASS (`POST /auth/login` → 200, bearer token) | Module 116 | **PASS** |
| Vercel frontend deployed (`https://praximed.vercel.app`) | Module 117 | **PASS** |
| `FRONTEND_CORS_ORIGINS=https://praximed.vercel.app` set in Railway; no wildcard | Module 117 | **PASS** |
| Browser login and dashboard render PASS | Module 117 | **PASS** |
| Staging tenant config deployed for UUID `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` | Module 118A | **PASS** |

---

## 4. Vapi Configuration (Module 118B)

Previous blocker (Module 118A diagnostic):
- `X-Clinic-Ref` header was not a recognized alias — caused HTTP 401
- `X-Vapi-Service-Name` header was absent — caused HTTP 401
- Staging tenant config was missing — caused ConfigNotFoundError → HTTP 404

**Corrected configuration applied in Module 118B:**

| Field | Value |
|---|---|
| Server URL | `https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request` |
| Method | `POST` |
| `Content-Type` | `application/json` |
| `X-Vapi-Service-Name` | `vapi` |
| `X-Vapi-Clinic-Id` | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` |
| `X-Vapi-Scopes` | `vapi:tool` (singular — `vapi:tools` plural returns HTTP 403) |
| `X-Clinic-Ref` | **Removed** — not a recognized clinic ID alias |
| Vapi webhook secret | `VAPI_WEBHOOK_SECRET` env var name only — value not recorded |

---

## 5. Dashboard Evidence

**Dashboard URL:** `https://praximed.vercel.app/dashboard`

Browser logged in with fake staging credentials. No real patient data. Fake data only.

### First evidence capture

| Evidence | Value |
|---|---|
| Appointments count | 2 |
| Rows visible | 2 |
| Patient name | Test Patient |
| Row status | new |
| Row priority | normal |
| Confirm button | visible on each row |

### Second evidence capture (after staff Confirm on two rows)

| Evidence | Value |
|---|---|
| Appointments count | 3 |
| Rows visible | 3 |
| Patient name | Test Patient (all rows) |
| Row 1 status | confirmed |
| Row 2 status | confirmed |
| Row 3 status | new |
| Row priority | normal (all rows) |
| Confirm flow | worked in deployed Vercel dashboard |

Staff Confirm updated two rows to `status=confirmed`. One row remained `status=new`.
No auto-confirmation was observed — all `status=confirmed` transitions required explicit
staff action via the dashboard Confirm button.

---

## 6. Safety Constraints

| Constraint | Confirmed |
|---|---|
| Fake data only | Yes — patient name "Test Patient"; no real names, DOBs, phone numbers |
| No real patient data | Confirmed — no real patient data in any staging row or Vapi test call |
| No production PHI | Confirmed — staging is fake/non-PHI only; production PHI remains NO-GO |
| Password not recorded | Confirmed — staging user password not recorded anywhere |
| Token not recorded | Confirmed — JWT access_token value not recorded |
| DATABASE_URL not recorded | Confirmed — DATABASE_URL value not recorded |
| bcrypt hash not recorded | Confirmed — password_hash value not recorded |
| JWT secret not recorded | Confirmed — JWT_SECRET_KEY value not recorded |
| Webhook secret not recorded | Confirmed — `VAPI_WEBHOOK_SECRET` name only; value not recorded |
| Vapi secret not recorded | Confirmed — no Vapi API keys or secrets recorded |

---

## 7. What This Proves

- Vapi can reach the Railway backend staging endpoint over HTTPS with correct headers
- Railway backend can authenticate a Vapi machine tool call and insert fake `appointment_requests` rows
- Vercel dashboard can display those rows fetched from the Railway PostgreSQL DB
- Staff Confirm flow works in the deployed Vercel dashboard (status transitions to `confirmed`)
- No auto-confirmation occurs — `status=new` is the initial state; `status=confirmed` requires staff action
- The full Vapi-to-dashboard loop is functional in deployed staging with fake/non-PHI data

---

## 8. What This Does Not Prove

| Item | Status |
|---|---|
| n8n staging workflow configured and functional | NOT PROVEN — n8n staging PENDING/DEFERRED (Module 119) |
| Production PHI readiness | NOT PROVEN — production PHI remains NO-GO |
| Custom domain readiness | NOT PROVEN — staging uses Vercel and Railway default URLs |
| Production auth/session hardening (httpOnly cookie) | NOT PROVEN — sessionStorage JWT is fake-data staging only |
| Rollback path confirmed against live deployments | NOT PROVEN — documented in runbooks |
| Railway log stream sanitized (no secrets or PII) | NOT PROVEN — PENDING |
