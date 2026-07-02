# Sprint 8 / Module 70 — Frontend Notifications Integration

Status: pending Module 69 review.

## Context

Module 69 wired the Patients section of the dashboard to `GET /patients`. The
pattern is now established for both live sections:
- `fetchAppointmentRequests(clinicId, token)` — Appointments section, Module 68
- `fetchPatients(clinicId, token)` — Patients section, Module 69

The same pattern applies to Notifications. The backend has `GET /notifications`
(requires Bearer JWT, Module 65).

## Scope

- Add a `fetchNotifications(clinicId, token)` helper to `frontend/lib/api.ts`.
- Wire the Notifications section of the dashboard to fetch `GET /notifications`.
- Show loading, error, empty, and list states (notification message, severity, created_at).
- Keep Consultations as a placeholder.
- Keep Appointments and Patients sections live and unchanged.
- Add static contract tests confirming the notification fetch is wired correctly.

## What not to do

- Do not fetch consultations yet.
- Do not add search or filtering UI.
- Do not add real notification data to tests.
- Do not modify backend routes.
- Do not remove or change the Appointments or Patients sections.

## Acceptance

- Dashboard fetches notifications for the logged-in clinic and displays them.
- Loading and error states are handled gracefully.
- Full backend tests pass.
- Commit: `Sprint 8 / Module 70 — Frontend notifications integration`
