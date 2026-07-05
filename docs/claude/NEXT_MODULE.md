# Sprint 17 / Module 123 — Doctor Notification System Foundation

Status: pending implementation.

## Context

Modules 121 and 121B complete:
- `appointment_requests.patient_id` FK implemented (migration 0003)
- Railway staging migration PASS; `patient_id` column/index confirmed
- Direct Vapi endpoint smoke with linked patient_id PASS

Module 122 complete:
- `GET /appointment-requests/{id}/pre-appointment-summary` live
- `build_pre_appointment_summary` service: structured factual brief; no AI; no diagnosis
- 25 tests; full suite: 2665/2665 passed
- Commercial acceleration mode active — clinic outreach in parallel

## Goal

Build the foundation for notifying doctors and clinic reception when a new
appointment request arrives or requires action. Initial scope: a safe internal
notification record (the same `clinic_notifications` table already in the schema),
later extended to email/push delivery.

## Scope

Backend only. No frontend changes in this module. Full test suite must pass.

## What Module 123 must do

1. **Notification creation** — when a new appointment_request is created via Vapi
   capture, create a `clinic_notifications` row for the clinic's doctors/staff.
   Include a brief summary (patient name, reason, suggested action) as the
   notification body.

2. **Notification type** — use `notification_type = "appointment_request"` (or a
   new type if it doesn't exist); link `related_resource_id` to the
   `appointment_requests.id`.

3. **Pre-appointment summary integration** — the notification body should reference
   the pre-appointment summary fields (patient_name, reason, suggested_next_action)
   without repeating the full summary.

4. **Recipient targeting** — notification should target clinic staff (broadcast to
   all active staff/doctors in the clinic, or use a configurable role targeting).

5. **Tests** — full test suite must pass; new module tests cover notification creation
   and content fields.

## What not to do

- Do not send real email or push notifications yet (delivery is a later module)
- Do not expose notification content to unauthenticated callers
- Do not generate diagnosis or medical advice in notification bodies
- Do not auto-confirm the appointment
- Do not store any real patient data
- Do not generate, record, or commit any real secrets or credential values
- Do not deploy to production
- Do not change auth/session code (separate hardening track)

## Safety constraints

- Fake/non-PHI data only in all tests and staging
- Production PHI readiness: NO-GO (C3–C8 hardening blockers still open)
- No real patient name, phone, DOB, or medical history in any file
- Doctor/staff approval remains required — no automated confirmation path
- No medical advice or diagnosis in notification body

## Reference docs

- `docs/architecture/PRE_APPOINTMENT_SUMMARY_FOUNDATION.md` — Module 122 summary service
- `docs/architecture/PATIENT_APPOINTMENT_DATA_LINKING_FOUNDATION.md` — Module 121 linking
- `backend/app/db/repositories/notification_repo.py` — existing notification repo
- `backend/app/modules/notifications/notification_router.py` — existing notification router
- `backend/app/db/schema.sql` — `clinic_notifications` table definition

## Acceptance

- Notification created when Vapi appointment request is captured
- Notification body includes patient name, reason, and suggested next action
- Notification is scoped by clinic_id (tenant isolation)
- No diagnosis or medical advice in notification content
- Existing Vapi/dashboard/Confirm flow remains compatible
- Full test suite passes
- Commit: `Sprint 17 / Module 123 — Doctor notification system foundation`

---

## Parallel non-code task (runs alongside Module 123)

**Build first list of 50 private clinics in Vienna and start outreach immediately.**

Sources: Docfinder.at, WKO Ärzteliste, Google Maps, LinkedIn.
Format: clinic name / specialty / contact name / phone / email / Google Maps link / notes.
Target: 50 clinics identified; 10–15 first-contact messages or calls within 14 days.

---

## Upcoming (commercial MVP build track, post-Module 123)

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
