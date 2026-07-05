# Sprint 18 / Module 126 — Fabel 5 Premium Dashboard UI/UX Polish

Status: pending implementation.

## Context

Module 125 complete:
- Dashboard Notifications section displays `clinic_notifications` rows (title, message truncated, status badge, priority badge; pending rows highlighted)
- Dashboard Appointments section has per-row "View summary" / "Hide summary" toggle with inline summary panel (patient_name, patient_type, reason, urgency_level, previous_request_count, suggested_next_action, safety_note)
- No diagnosis; no medical advice; Confirm button unchanged; cookie-based auth intact
- Full backend tests: 2754/2754 passed

## Goal

Transform the functional PraxisMed dashboard into a premium, doctor-facing product.
This is the Fabel 5 sprint — high priority for demo quality and sales conversion.

The current dashboard is functional but visually minimal. Sprint 18 is the premium polish
pass that makes the UI look like a real clinical product.

## Scope

Frontend only + visual/UX improvements. No backend code changes. No new APIs.
No real patient data. No production PHI. No secrets. Do not mark production ready.

## What Module 126 must do

1. **Visual design system** — replace CSS variable stubs with a real premium design:
   typography scale, consistent spacing, professional color palette (not flat gray/white),
   subtle shadows, refined borders.

2. **Header and navigation** — premium header with clinic branding, user role indicator,
   notification bell with count badge.

3. **Appointments section** — card-based rows instead of flat list; status chip colors
   more distinct; "View summary" inline panel styled as an elevated card with clear
   section labels; Confirm button more prominent.

4. **Notifications section** — distinct "pending" row treatment (accent left border or
   icon badge); message line styled as secondary text; clear empty state.

5. **Patients and Consultations sections** — same card-based row treatment for visual
   consistency.

6. **Loading and error states** — skeleton loaders instead of text-only loading strings;
   styled error banners.

7. **Responsive layout** — ensure the 900px max-width container looks correct on tablet.

## What not to do

- Do not add new API endpoints
- Do not add push/email/SMS/WhatsApp delivery
- Do not add diagnosis or medical advice to any display
- Do not store any real patient data
- Do not generate, record, or commit any real secrets or credential values
- Do not deploy to production

## Safety constraints

- Fake/non-PHI data only in all tests and staging
- Production PHI readiness: NO-GO (C3–C8 hardening blockers still open)
- No real patient name, phone, DOB, or medical history in any file
- Doctor/staff approval remains required — no automated confirmation path
- No medical advice or diagnosis in any display
- No secrets recorded in any evidence

## Reference docs

- `frontend/app/dashboard/page.tsx` — current dashboard (Module 125)
- `frontend/lib/api.ts` — API helpers
- `docs/architecture/DASHBOARD_NOTIFICATION_AND_SUMMARY_UI_FOUNDATION.md` — Module 125

## Acceptance

- Dashboard visually looks like a premium clinical product
- All four sections (Appointments, Patients, Notifications, Consultations) use consistent premium card/row styling
- Notifications pending rows have a clear visual accent
- Summary panel renders with elevated card style and labeled fields
- Loading states use skeleton loaders
- Error states are styled banners, not plain text
- Confirm button is prominent and accessible
- All existing functionality intact (Confirm, View summary, Logout)
- Full tests pass
- Commit: `Sprint 18 / Module 126 — Fabel 5 premium dashboard UI/UX polish`

---

## Upcoming (commercial MVP build track, post-Module 126)

- **Module 127** — Consultation summary draft generator
- **Module 128** — Patient timeline
- **Module 129** — Follow-up and reminder workflow

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)
