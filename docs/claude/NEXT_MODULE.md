# Sprint 8 / Module 71 — Frontend Consultation List Integration

Status: pending Module 70 review.

## Context

Module 70 wired the Notifications section of the dashboard to `GET /notifications`. The
pattern is now established for three live sections:
- `fetchAppointmentRequests(clinicId, token)` — Appointments section, Module 68
- `fetchPatients(clinicId, token)` — Patients section, Module 69
- `fetchNotifications(clinicId, token)` — Notifications section, Module 70

The same pattern applies to Consultations. The backend has `GET /consultations`
(requires Bearer JWT, clinical role — owner/admin/doctor only, Module 62).

## Scope

- Add a `fetchConsultations(clinicId, token)` helper to `frontend/lib/api.ts`.
- Wire the Consultations section of the dashboard to fetch `GET /consultations`.
- Show loading, error, empty, and list states (consultation status, created_at).
- Keep Appointments, Patients, and Notifications sections live and unchanged.
- Remove the Consultations placeholder card — the grid will be empty or removed.
- Add static contract tests confirming the consultation fetch is wired correctly.

## What not to do

- Do not add search or filtering UI.
- Do not add real consultation data to tests.
- Do not modify backend routes.
- Do not remove or change the Appointments, Patients, or Notifications sections.

## Acceptance

- Dashboard fetches consultations for the logged-in clinic and displays them.
- Loading and error states are handled gracefully.
- Full backend tests pass.
- Commit: `Sprint 8 / Module 71 — Frontend consultation list integration`
