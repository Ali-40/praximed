# Fake Staging Clinic and User Provisioning Evidence — PraxisMed

**Date:** 2026-07-04
**Sprint:** Sprint 16 / Module 115
**Status:** PASS — fake staging clinic and doctor user provisioned in Railway PostgreSQL

---

## 1. Purpose

This document records the real evidence from provisioning the fake staging clinic and
doctor user in the Railway PostgreSQL staging database for PraxisMed fake-data staging.

**Accuracy policy:** No step is marked PASS without real evidence from the real Railway
PostgreSQL service. No evidence is fabricated. No secrets, passwords, bcrypt hashes, or
`DATABASE_URL` values appear in this document.

Staging uses fake/non-PHI data only. No real patient data. No production secrets.
No real clinic data. This is explicitly fake staging data.

---

## 2. Current Result

**Overall result: PASS**

A fake staging clinic row and a fake staging doctor user row were inserted into the
Railway PostgreSQL staging database using the Railway web service console. Both rows
were verified to exist with correct field values and `active` status. No real patient
data, no production secrets, and no local-dev UUIDs were used.

---

## 3. Evidence

### 3.1 Fake Staging Clinic

| Field | Value | Status |
|---|---|---|
| `id` (clinic UUID) | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` | **PASS** |
| `slug` | `staging-fake-clinic` | **PASS** |
| `name` | `Staging Fake Clinic` | **PASS** |
| `status` | `active` | **PASS** |
| `timezone` | `Europe/Vienna` | **PASS** |
| `locale` | `de-AT` | **PASS** |
| Not a local-dev UUID | Confirmed — not `11111111-1111-1111-1111-111111111111` | **PASS** |
| Fake/non-PHI data | Confirmed — no real clinic name, address, or contact data | **PASS** |

### 3.2 Fake Staging Doctor User

| Field | Value | Status |
|---|---|---|
| `id` (user UUID) | `5b63b514-7624-4e8e-9af0-71c153ba7b83` | **PASS** |
| `clinic_id` | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` (matches staging clinic) | **PASS** |
| `email` | `doctor.staging@praximed.test` | **PASS** |
| `full_name` | `Dr. Staging Test` | **PASS** |
| `role` | `doctor` | **PASS** |
| `status` | `active` | **PASS** |
| `password_hash` | bcrypt hash set — value not recorded in this document | **PASS** |
| Not a local-dev UUID | Confirmed — not `22222222-2222-2222-2222-222222222222` | **PASS** |
| Not local-dev email | Confirmed — not `doctor.local@praximed.test` | **PASS** |
| Fake/non-PHI data | Confirmed — no real doctor name, phone, or credentials | **PASS** |

### 3.3 Sanitized Verification Output

```
=== VERIFICATION ===
Clinic found: id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056 slug=staging-fake-clinic status=active
User found:   id=5b63b514-7624-4e8e-9af0-71c153ba7b83 email=doctor.staging@praximed.test role=doctor status=active
```

---

## 4. Safety Boundary

| Rule | Status |
|---|---|
| Password not recorded | CONFIRMED — plaintext staging password stored in password manager only; not in any document, log, or evidence record |
| Bcrypt hash not recorded | CONFIRMED — hash was used in the Railway run command only; not saved to any document |
| `DATABASE_URL` not recorded | CONFIRMED — connection string never appeared in any evidence; Railway injected it automatically |
| No real patient data | CONFIRMED — no patient rows inserted; no real names, phone numbers, DOBs, or medical records |
| Fake/non-PHI staging only | CONFIRMED — clinic and user rows contain explicitly fake identifiers only |
| Not local-dev-password | CONFIRMED — staging password was newly generated; not `local-dev-password` |
| Not local-dev UUIDs | CONFIRMED — clinic UUID and user UUID are randomly generated; not the deterministic local-dev UUIDs |
| Production PHI launch | **NO-GO** — Vercel frontend not deployed; CORS not wired; login smoke not executed; production PHI remains NO-GO |

---

## 5. What This Proves

- **Railway PostgreSQL has a fake staging clinic row** — `id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056`,
  `slug='staging-fake-clinic'`, `status='active'`; verified by Railway console SELECT
- **Railway PostgreSQL has a fake staging doctor user row** — `id=5b63b514-7624-4e8e-9af0-71c153ba7b83`,
  `email='doctor.staging@praximed.test'`, `role='doctor'`, `status='active'`; verified by Railway console SELECT
- **User is bound to the correct staging clinic** — `clinic_id` on the user row matches
  the staging clinic `id`; the foreign key relationship is satisfied
- **Both rows are in `active` status** — required for `POST /auth/login` to succeed
- **`password_hash` column is populated** — the `clinic_users.password_hash` column (added
  by migration `0002_password_hash`) is set on this user; the bcrypt hash was verified to
  be accepted by PostgreSQL without error
- **Staging fake login credentials exist privately** — the operator holds the staging
  password; a login attempt against `POST /auth/login` can now be made using:
  `clinic_id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056`, `email=doctor.staging@praximed.test`
- **Local-dev isolation confirmed** — no deterministic local-dev UUIDs (`11111111-...`,
  `22222222-...`) appear in the staging DB; local-dev password not reused

---

## 6. What This Does Not Prove

| Area | Status | Next Step |
|---|---|---|
| `POST /auth/login` returns JWT against staging backend | NOT PROVEN | Module 116 |
| JWT issuance works in staging (JWT_SECRET_KEY set) | NOT PROVEN | Module 116 |
| `GET /health/ready` returns 200 | NOT PROVEN | Module 116 |
| Vercel frontend deployed | NOT PROVEN | Module 117 |
| `NEXT_PUBLIC_API_BASE_URL` set in Vercel | NOT PROVEN | Module 117 |
| CORS wired (`FRONTEND_CORS_ORIGINS` = Vercel URL) | NOT PROVEN | Module 118 |
| Browser login via Vercel frontend works | NOT PROVEN | Module 118 |
| Dashboard loads after login | NOT PROVEN | Module 118 |
| Vapi test assistant pointed to staging | NOT PROVEN | Module 118 |
| Vapi test call creates appointment row | NOT PROVEN | Module 118 |
| n8n staging workflow configured | NOT PROVEN | Module 118 |
| Full staging smoke passed | NOT PROVEN | Module 119 |
| Production PHI readiness | NOT PROVEN | Production PHI launch remains NO-GO |

---

## 7. Next Verification — Module 116

**Sprint 16 / Module 116 — Backend Staging Login Smoke Evidence**

Now that the fake staging clinic and user exist in Railway PostgreSQL, the next step is
to verify that `POST /auth/login` against the Railway staging backend URL accepts the
fake credentials and returns a JWT.

**Manual step required:**

```
POST https://web-production-fd91d.up.railway.app/auth/login
Content-Type: application/json

{
  "clinic_id": "1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
  "email": "doctor.staging@praximed.test",
  "password": "<staging-password-from-password-manager>"
}
```

Expected response: HTTP 200 with `access_token` in response body.

**Evidence to capture (no secrets):**
- HTTP status code: expected `200`
- Presence of `access_token` field: confirmed (do not record token value)
- `token_type`: expected `bearer`
- `user.email`: expected `doctor.staging@praximed.test`
- `user.role`: expected `doctor`
- No `JWT_SECRET_KEY` or password visible in any log or response field
