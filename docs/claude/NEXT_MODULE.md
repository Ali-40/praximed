# Sprint 8 / Module 69 — Frontend Patient List Integration

Status: pending Module 68 review.

## Context

Module 68 wired the Appointments section of the dashboard to `GET /appointment-requests`
using the stored JWT. The pattern is established:
- `fetchAppointmentRequests(clinicId, token)` in `lib/api.ts`
- `getClinicId()` decodes `clinic_id` from the stored JWT payload
- Dashboard `useEffect` fetches after auth check
- Loading / error / empty / list states rendered

The same pattern applies to Patients. The backend already has `GET /patients`
(requires Bearer JWT, Module 61).

## Scope

- Add a `fetchPatients(clinicId, token)` helper to `frontend/lib/api.ts`.
- Wire the Patients section of the dashboard to fetch `GET /patients`.
- Show loading, error, empty, and list states (patient name, status, created_at).
- Keep Notifications and Consultations as placeholders.
- Add static contract tests confirming the patient fetch is wired correctly.

## What not to do

- Do not fetch notifications or consultations yet.
- Do not add search or filtering UI.
- Do not add real patient data to tests.
- Do not modify backend routes.
- Do not remove the Appointments section wired in Module 68.

## Acceptance

- Dashboard fetches patients for the logged-in clinic and displays them.
- Loading and error states are handled gracefully.
- Full backend tests pass.
- Commit: `Sprint 8 / Module 69 — Frontend patient list integration`
