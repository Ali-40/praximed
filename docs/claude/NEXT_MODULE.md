# Sprint 11 / Module 81 — Appointment Request Workflow UI Foundation

Status: pending Architecture Checkpoint 09 review.

## Context

Architecture Checkpoint 09 identified the appointment request workflow as the
highest-priority next feature. Clinic staff can currently view appointment requests on
the dashboard but cannot action them. The backend already has:
- `PATCH /appointment-requests/{id}/status` — accepts `{"status": "confirmed"}` or
  `{"status": "rejected"}` with optional `action_required`
- `PATCH /appointment-requests/{id}/assign` — assigns to a user
- `POST /appointment-requests/{id}/callback-needed` — flags for callback
- `POST /appointment-requests/{id}/archive`

All routes require a Bearer JWT and enforce clinic-level tenant checks.

## Scope

Keep the scope small for the first iteration. Build one action only: **Confirm**.

1. Add a `confirmAppointmentRequest(requestId, clinicId, token)` helper to
   `frontend/lib/api.ts`:
   - Calls `PATCH /appointment-requests/{id}/status?clinic_id={clinicId}`
   - Body: `{"status": "confirmed", "action_required": false}`
   - Throws on non-2xx response

2. Add a Confirm button to each appointment request row in
   `frontend/app/dashboard/page.tsx`:
   - Only shown when `appt.status === 'new'` (no button for already-confirmed rows)
   - On click: calls `confirmAppointmentRequest`, then refreshes the appointments list
   - Shows a loading/disabled state while the request is in flight
   - Shows a generic error message if the call fails
   - On success: row status badge updates to "confirmed"

3. Create `backend/tests/test_frontend_appointment_workflow_contract.py`:
   - `confirmAppointmentRequest` defined in `lib/api.ts`
   - Uses `PATCH` method and `/appointment-requests/` endpoint
   - Uses Bearer token
   - Dashboard references `confirmAppointmentRequest`
   - Confirm button only shown for `status === 'new'`
   - No hardcoded tokens or real patient data

4. Manual browser verification:
   - Login and confirm the seeded appointment request shows a Confirm button.
   - Click Confirm — status badge updates to "confirmed" and button disappears.

## What not to do

- Do not add Reject, Assign, or Archive actions in this module (next modules).
- Do not add a modal or confirmation dialog — inline button only for now.
- Do not change backend routes, schemas, or migrations.
- Do not change auth or seed script.

## Acceptance

- Confirm button appears on appointment request rows with status "new".
- Clicking Confirm updates the row to status "confirmed".
- Button disabled while request is in flight.
- Generic error shown on failure.
- Contract tests pass: `pytest -v backend/tests/test_frontend_appointment_workflow_contract.py`
- Full backend tests pass: `pytest -v backend/tests`
- Commit: `Sprint 11 / Module 81 — Appointment request workflow UI foundation`
