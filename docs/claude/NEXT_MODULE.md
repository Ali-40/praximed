# Sprint 17 / Module 124 — Deployed Doctor Notification Smoke Evidence

Status: pending implementation.

## Context

Modules 121 and 121B complete:
- `appointment_requests.patient_id` FK implemented (migration 0003)
- Railway staging migration PASS; `patient_id` column/index confirmed
- Direct Vapi endpoint smoke with linked patient_id PASS

Modules 122 and 122B complete:
- `GET /appointment-requests/{id}/pre-appointment-summary` live
- `build_pre_appointment_summary` service: structured factual brief; no AI; no diagnosis
- 25 tests; full suite: 2689/2689 passed
- Deployed smoke PASS (Module 122B): doctor cookie auth → summary with `patient_type: returning`, `suggested_next_action: Review and confirm`, safety_note present

Module 123 complete:
- Internal `clinic_notifications` row created for every Vapi appointment capture
- Notification includes patient_name, reason, suggested_next_action ("Review and confirm")
- Notification scoped by clinic_id; references appointment_requests.id
- channel = "internal"; no external delivery
- No diagnosis, no medical advice
- 15 new tests; full suite: 2704/2704 passed

## Goal

Document real deployed staging evidence that Module 123 is live:
a new Vapi appointment request creates a notification row, and the
notification list endpoint returns it for authenticated staff/doctors.

## Scope

**Docs/static-tests only.** No runtime code changes. No new migrations. No secrets.
No real patient data. No production PHI. Do not mark production ready.

## What Module 124 must do

1. **Redeploy** — push/redeploy Module 123 to Railway staging.

2. **Create a fake Vapi appointment request** — call the Vapi capture endpoint
   with fake non-PHI data (e.g., patient name "Notification Smoke Patient",
   reason "annual check-up", fake call_id).

3. **Verify notification row exists** — query the notification list endpoint
   (`GET /notifications?clinic_id=...`) with doctor cookie auth; confirm the
   new `appointment_request` notification appears with status `pending`,
   `related_resource_type = "appointment_requests"`, and the correct
   `related_resource_id`.

4. **Verify notification content** — confirm the message includes the patient
   name; confirm no diagnosis or medical advice appears.

5. **Optional: dashboard notification count** — if the frontend notification
   badge/list already queries `/notifications`, confirm the count updates.

6. **Document evidence** — write evidence doc; no secrets, no real patient data.

7. **Update wiring/smoke docs** — mark doctor notification PASS in
   `STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` and
   `STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md`.

## What not to do

- Do not send real email or push notifications
- Do not expose notification content to unauthenticated callers
- Do not generate diagnosis or medical advice
- Do not auto-confirm the appointment
- Do not store any real patient data
- Do not generate, record, or commit any real secrets or credential values
- Do not deploy to production

## Safety constraints

- Fake/non-PHI data only in all tests and staging
- Production PHI readiness: NO-GO (C3–C8 hardening blockers still open)
- No real patient name, phone, DOB, or medical history in any file
- Doctor/staff approval remains required — no automated confirmation path
- No medical advice or diagnosis in notification body
- No secrets recorded in evidence docs

## Reference docs

- `docs/architecture/DOCTOR_NOTIFICATION_SYSTEM_FOUNDATION.md` — Module 123
- `docs/architecture/PRE_APPOINTMENT_SUMMARY_FOUNDATION.md` — Module 122 summary service
- `backend/app/modules/notifications/notification_router.py` — notification router
- `backend/app/api/routes/notifications.py` — notification API routes
- `backend/app/db/repositories/notification_repo.py` — notification repo

## Acceptance

- Railway redeployed with Module 123 changes
- Fake Vapi appointment request created in staging
- Notification row confirmed in Railway PostgreSQL via list endpoint
- Notification message includes patient name and reason
- No diagnosis or medical advice in notification content
- No secrets recorded
- Fake/non-PHI data only
- Production PHI readiness: NO-GO
- Commit: `Sprint 17 / Module 124 — Deployed doctor notification smoke evidence`

---

## Upcoming (commercial MVP build track, post-Module 124)

- **Module 125** — Consultation summary draft generator
- **Module 126** — Patient timeline
- **Module 127** — Follow-up and reminder workflow

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)

## Sprint 18

- **Fabel 5 premium UI/UX polish** — transform the functional dashboard into a
  premium, doctor-facing product; high priority for demo quality and sales conversion
