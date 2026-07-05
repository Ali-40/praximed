# Sprint 17 / Module 125 — Dashboard Notification and Summary UI Foundation

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
- Deployed smoke PASS (Module 122B)

Modules 123, 123A, and 124 complete:
- Internal `clinic_notifications` row created for every Vapi appointment capture
- UUID→str blocker fixed (Module 123A)
- Deployed smoke PASS (Module 124): notification_count=1; clinic-scoped; linked to appointment request
- Dashboard notification UI not yet wired

## Goal

Surface the internal notification foundation and pre-appointment summary in the
existing dashboard UI. The current dashboard has Notifications and Appointments
sections — wire them to the live backend endpoints so clinic staff and doctors see
notification alerts and per-appointment summaries without building a new UI from scratch.

This module prepares the UI for the Fabel 5 premium polish sprint (Sprint 18).

## Scope

Frontend + (minor backend if needed) + tests + docs.
Fake-data staging only. No real patient data. No production PHI. No secrets.
No external phone/email/SMS/WhatsApp delivery.
Do not mark production ready.

## What Module 125 must do

1. **Notifications section** — the dashboard Notifications section should display
   the list of `clinic_notifications` from `GET /notifications?clinic_id=...`.
   Show: title, message (truncated), status, created_at.
   Highlight `status=pending` rows.

2. **Pre-appointment summary link** — each appointment row in the Appointments section
   should have a "View Summary" button or link that fetches and displays the
   `GET /appointment-requests/{id}/pre-appointment-summary` for that row.
   Summary display: patient_name, reason, suggested_next_action, safety_note.
   No diagnosis, no medical advice in display.

3. **Simple, functional UI** — not premium yet; Sprint 18 (Fabel 5) handles polish.
   The goal is data wired and visible, not visual perfection.

4. **Fake data only** — all staging data is non-PHI. No real patient names.

5. **Tests** — frontend component/integration tests if framework supports it.
   Backend tests for any new API changes (should be minimal — endpoints exist).

## What not to do

- Do not build push/email/SMS/WhatsApp notification delivery
- Do not add diagnosis or medical advice to notification or summary display
- Do not auto-confirm the appointment from the summary view
- Do not store any real patient data
- Do not generate, record, or commit any real secrets or credential values
- Do not deploy to production

## Safety constraints

- Fake/non-PHI data only in all tests and staging
- Production PHI readiness: NO-GO (C3–C8 hardening blockers still open)
- No real patient name, phone, DOB, or medical history in any file
- Doctor/staff approval remains required — no automated confirmation path
- No medical advice or diagnosis in notification body or summary display
- No secrets recorded in any evidence

## Reference docs

- `docs/architecture/DOCTOR_NOTIFICATION_SYSTEM_FOUNDATION.md` — Module 123/123A
- `docs/architecture/PRE_APPOINTMENT_SUMMARY_FOUNDATION.md` — Module 122
- `backend/app/api/routes/notifications.py` — `GET /notifications?clinic_id=...`
- `backend/app/api/routes/appointment_requests.py` — `GET /{id}/pre-appointment-summary`
- `frontend/` — existing dashboard UI

## Acceptance

- Dashboard Notifications section displays `clinic_notifications` rows from live API
- Dashboard Appointments section has per-row "View Summary" that fetches pre-appointment summary
- No diagnosis or medical advice displayed
- Safety note present in summary display
- Existing Vapi/dashboard/Confirm/notification flow remains compatible
- Fake data only; production PHI NO-GO
- Full tests pass
- Commit: `Sprint 17 / Module 125 — Dashboard notification and summary UI foundation`

---

## Upcoming (commercial MVP build track, post-Module 125)

- **Module 126** — Consultation summary draft generator
- **Module 127** — Patient timeline
- **Module 128** — Follow-up and reminder workflow

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)

## Sprint 18

- **Fabel 5 premium UI/UX polish** — transform the functional dashboard into a
  premium, doctor-facing product; high priority for demo quality and sales conversion
