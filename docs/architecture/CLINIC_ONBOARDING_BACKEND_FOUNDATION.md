# PraxisMed — Clinic Onboarding Backend Foundation

**Sprint 19 / Module 132**
**Date:** 2026-07-06
**Status:** Implemented — backend foundation complete, frontend wiring pending (Module 133)

---

## 1. Purpose

This document describes the backend data model and API for collecting pilot/onboarding
requests from doctors and private clinics. A clinic can submit a request to trial PraxisMed
as a pilot user with the AI phone receptionist and dashboard.

**No real tenant is created automatically.** A submitted request is stored in the
`clinic_onboarding_requests` table and reviewed by PraxisMed staff before any clinic
environment is provisioned.

**No patient PHI is accepted.** The onboarding form collects only clinic and contact details.
Production PHI processing remains **NO-GO** until all C3–C8 compliance hardening blockers
are resolved.

---

## 2. Database Table — `clinic_onboarding_requests`

A new table stores all pilot/onboarding requests submitted via the public form.

### Key columns

| Column | Type | Default | Purpose |
|---|---|---|---|
| `id` | UUID PK | `gen_random_uuid()` | Row identifier |
| `clinic_name` | TEXT NOT NULL | — | Clinic or practice name |
| `clinic_type` | TEXT NULL | — | e.g. Wahlarzt, Kassenarzt |
| `specialty` | TEXT NULL | — | Primary specialty (Innere Medizin, etc.) |
| `city` | TEXT NULL | — | Clinic city |
| `doctor_name` | TEXT NOT NULL | — | Submitting doctor |
| `contact_email` | TEXT NOT NULL | — | Contact email for follow-up |
| `contact_phone` | TEXT NULL | — | Optional contact phone |
| `preferred_language` | TEXT NOT NULL | `de` | Primary language: `de` or `en` |
| `fallback_language` | TEXT NOT NULL | `en` | Fallback: `de` or `en` |
| `supported_languages` | JSONB NOT NULL | `["de","en"]` | Languages supported by the clinic |
| `wants_ai_phone_intake` | BOOLEAN NOT NULL | `true` | Interest in AI receptionist |
| `wants_dashboard` | BOOLEAN NOT NULL | `true` | Interest in clinical dashboard |
| `wants_notifications` | BOOLEAN NOT NULL | `false` | Interest in SMS/push notifications |
| `pilot_interest_level` | TEXT NOT NULL | `new` | Lead temperature |
| `status` | TEXT NOT NULL | `submitted` | Review status |
| `source` | TEXT NOT NULL | `onboarding_page` | Origin of submission |
| `consent_pilot_contact` | BOOLEAN NOT NULL | `false` | Explicit consent to contact |
| `acknowledges_no_phi` | BOOLEAN NOT NULL | `false` | Acknowledges this is not PHI activation |
| `production_phi_enabled` | BOOLEAN NOT NULL | `false` | Always false — DB constraint enforced |
| `created_at` / `updated_at` | TIMESTAMPTZ | `now()` | Audit timestamps |

### DB constraints

- `status` must be one of: `submitted`, `reviewed`, `demo_booked`, `pilot_approved`, `rejected`, `archived`
- `preferred_language` must be one of: `de`, `en`
- `production_phi_enabled` must be `false` — a CHECK constraint enforces this at the DB level.
  Setting it to `true` is blocked by the database, the repository, and the Pydantic schema.

### Indexes

`contact_email`, `status`, `created_at`, `preferred_language`

---

## 3. Language Foundation — German-First, English Fallback

Austrian private clinics default to **German** as the primary interface and AI receptionist
language. English is available as a fallback for non-German-speaking patients.

- `preferred_language` defaults to `de`
- `fallback_language` defaults to `en`
- `supported_languages` defaults to `["de", "en"]`
- Allowed values: `de`, `en` — other languages are rejected with a validation error
- `preferred_language` must be present in `supported_languages`

This preference is **stored only** in Module 132. It does not automatically configure the
Vapi assistant or the clinic UI language. Language-specific Vapi assistant wiring is a future
module.

---

## 4. Public Onboarding Request Flow

```
Doctor fills out onboarding form (frontend)
    ↓
POST /clinic-onboarding-requests   (no auth required)
    ↓
Pydantic validation:
  - clinic_name required
  - doctor_name required
  - contact_email valid format
  - preferred_language in {de, en}
  - consent_pilot_contact must be true
  - acknowledges_no_phi must be true
    ↓
Repository: INSERT INTO clinic_onboarding_requests (status='submitted', production_phi_enabled=false)
    ↓
Response: 201 Created + request object (status=submitted, production_phi_enabled=false)
    ↓
PraxisMed staff reviews request (internal admin endpoint)
```

**What does not happen:**
- No clinic tenant record is created in `clinics`
- No `clinic_id` is assigned
- No Vapi credential is stored
- No `PRODUCTION_COMPLIANCE_UNLOCKED` is set
- No email is sent (Module 132 scope)
- No patient PHI is accepted or stored

---

## 5. Internal Review Flow

Protected endpoints (require existing `get_current_user` session auth):

| Endpoint | Purpose |
|---|---|
| `GET /clinic-onboarding-requests` | List all submissions (optionally filtered by status) |
| `GET /clinic-onboarding-requests/{id}` | View a single submission |
| `PATCH /clinic-onboarding-requests/{id}/status` | Update review status |

Status lifecycle:
```
submitted → reviewed → demo_booked → pilot_approved
                              ↘ rejected / archived
```

`pilot_approved` does **not** automatically create a production tenant. It is an internal
marker that a manual provisioning workflow may begin. Full tenant provisioning requires
a separate admin process outside this module.

---

## 6. API Endpoints Summary

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/clinic-onboarding-requests` | None (public) | Submit pilot request |
| `GET` | `/clinic-onboarding-requests` | session cookie | List requests |
| `GET` | `/clinic-onboarding-requests/{id}` | session cookie | Get single request |
| `PATCH` | `/clinic-onboarding-requests/{id}/status` | session cookie | Update status |

`enforce_phi_safeguard` is **not** applied — this endpoint does not process patient PHI.
Clinic contact details (email, phone) are clinic admin info, not patient PHI.

---

## 7. What This Does Not Provide

- **Frontend form wiring** — the `/onboarding` page remains a static scaffold. Module 133
  will connect it to `POST /clinic-onboarding-requests`.
- **Email notifications** — no email is sent on submission. Future module.
- **Automatic tenant provisioning** — no clinic is created automatically.
- **Vapi credential storage** — credentials are never accepted or stored.
- **DSGVO/Article 32 compliance** — not claimed. C3–C8 blockers remain open.
- **Production PHI processing** — `PRODUCTION_COMPLIANCE_UNLOCKED` was not set.

---

## 8. Safety Boundaries

| Constraint | Status |
|---|---|
| No patient PHI accepted | **ENFORCED** — no patient_name, DOB, diagnosis, or medical fields |
| No Vapi credentials accepted | **ENFORCED** — no credential fields in schema |
| No secrets committed | **CONFIRMED** |
| No automatic tenant creation | **CONFIRMED** — INSERT only in clinic_onboarding_requests |
| production_phi_enabled always false | **ENFORCED** — Pydantic + repo + DB CHECK constraint |
| consent_pilot_contact required | **ENFORCED** — validation error if false |
| acknowledges_no_phi required | **ENFORCED** — validation error if false |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |
| DSGVO/Article 32 compliance | **NOT CLAIMED** |

---

## 9. Migration

`backend/migrations/versions/0004_clinic_onboarding_requests.py`

- Revision: `0004_clinic_onboarding_requests`
- Down revision: `0003_patient_id_appt_requests`
- Idempotent: `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`
- Includes `downgrade()` that drops table and indexes

---

## 10. What Module 133 Will Do

Module 133 — Connect Onboarding Frontend to Backend Request API:
- Make the `/onboarding` form functional
- Wire step 5 "Review & Pilot Activation" to `POST /clinic-onboarding-requests`
- Include the German-first language selector with English fallback
- Show a success confirmation state after submission
- No PHI, no secrets, no automatic production activation
