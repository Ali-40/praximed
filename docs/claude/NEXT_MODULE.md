# Sprint 17 / Module 122 — Pre-Appointment Summary Foundation

Status: pending implementation.

## Context

Module 121 complete:
- `appointment_requests.patient_id` FK implemented (migration 0003)
- `find_or_create_patient_from_vapi` live in patient_repo
- Vapi capture links every new appointment request to a patient row
- Tenant isolation tested; second-call reuse tested; no real patient data
- Full test suite: 2611/2611 passed
- Commercial acceleration mode active — clinic outreach in parallel

## Goal

Generate a safe, structured pre-appointment brief from the linked patient + appointment
request data. This gives the doctor or reception team a compact summary before the
appointment is confirmed, reducing the time spent on intake calls.

## Scope

Backend only. No frontend changes in this module. Full test suite must pass.

## What Module 122 must do

1. **Repository layer** — query the linked `patients` + `appointment_requests` data
   for a given `appointment_request_id` and `clinic_id`

2. **Summary service** — produce a structured plain-text or JSON brief containing:
   - Patient: name, date of birth (age), phone
   - Request: reason, urgency_level, preferred_starts_at / preferred_ends_at
   - Status: current appointment request status
   - Source: vapi / staff

3. **API route** — `GET /appointment-requests/{request_id}/summary` (staff-facing;
   requires authentication; returns the pre-appointment brief)

4. **Tests** — full test suite must pass; new module tests cover the service and route

## What not to do

- Do not generate diagnosis, prognosis, or medical advice of any kind
- Do not call any external AI API (Claude, GPT, etc.) — this module is structured data only
- Do not auto-confirm the appointment
- Do not store any real patient data
- Do not expose the summary to unauthenticated callers
- Do not implement doctor push notifications yet (Module 123)
- Do not generate, record, or commit any real secrets or credential values
- Do not deploy to production
- Do not change auth/session code (separate hardening track)

## Safety constraints

- Fake/non-PHI data only in all tests and staging
- Production PHI readiness: NO-GO (C3–C8 hardening blockers still open)
- No real patient name, phone, DOB, or medical history in any file
- Doctor/staff approval remains required — no automated confirmation path

## Reference docs

- `docs/architecture/PATIENT_APPOINTMENT_DATA_LINKING_FOUNDATION.md` — Module 121 schema and linking behavior
- `backend/app/db/schema.sql` — current schema (patients + appointment_requests + patient_id FK)
- `backend/app/db/repositories/patient_repo.py` — patient repo including find_or_create_patient_from_vapi
- `backend/app/db/repositories/appointment_request_repo.py` — appointment request repo

## Acceptance

- Pre-appointment summary service implemented and tested
- Route returns structured brief for a valid appointment_request_id
- Unauthorized access returns 401
- No medical advice / no diagnosis generated
- Full test suite passes
- Commit: `Sprint 17 / Module 122 — Pre-appointment summary foundation`

---

## Parallel non-code task (runs alongside Module 122)

**Build first list of 50 private clinics in Vienna and start outreach immediately.**

Sources: Docfinder.at, WKO Ärzteliste, Google Maps, LinkedIn.
Format: clinic name / specialty / contact name / phone / email / Google Maps link / notes.
Target: 50 clinics identified; 10–15 first-contact messages or calls within 14 days.

---

## Upcoming (commercial MVP build track, post-Module 122)

- **Module 123** — Doctor/reception notification (email or push)
- **Module 124** — Consultation summary draft generator
- **Module 125** — Patient timeline
- **Module 126** — Follow-up and reminder workflow

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)

## Sprint 18

- **Fabel 5 premium UI/UX polish** — transform the functional dashboard into a
  premium, doctor-facing product; high priority for demo quality and sales conversion
