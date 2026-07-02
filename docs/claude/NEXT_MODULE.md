# Sprint 11 / Module 83 — Vapi Intake to Appointment Dashboard Smoke Harness

Status: pending Module 82 review.

## Context

Module 82 proved the full local staff workflow loop: login → Confirm appointment request
→ status "confirmed" → button disappears. The next gap is proving that the AI intake
path (Vapi call event) creates a dashboard-visible appointment request without relying
on the manual seed script.

The backend already has:
- `POST /webhooks/vapi/call-event` — Vapi webhook endpoint with HMAC + machine auth
- `vapi_appointment_capture` module — creates appointment requests from Vapi payloads
- `appointment_requests` table — stores captured requests
- `GET /appointment-requests` — frontend fetches this on dashboard load

The unknowns (documented in `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md`):
- Whether the current capture module extracts `patient_name`, `reason`, and `clinic_id`
  from the adapted Vapi payload shape (Module 56's adapter output)
- Whether a real or simulated Vapi call produces a dashboard-visible row without the seed

## Scope

### 1. Inspect the Vapi capture module

Read `backend/app/modules/vapi/vapi_appointment_capture.py` and the webhook route
`backend/app/api/routes/vapi_webhooks.py` to understand:
- What payload fields the capture module expects
- Whether `clinic_id` and `patient_name` are available after Module 56's adapter runs
- Whether an `appointment_requests` row is created on `call.ended` events

### 2. Add static contract tests if gaps exist

Create or update contract tests to assert:
- The capture module reads `patient_name` (or a suitable field) from the adapted payload
- The capture module uses `clinic_id` from the machine auth context, not from the raw Vapi body
- No real credentials or patient data appear in the contract

Place new tests in `backend/tests/test_vapi_appointment_capture_contract.py` (or extend
`backend/tests/test_vapi_appointment_capture.py` if appropriate).

### 3. Add a local fixture smoke script (optional, for manual verification only)

If the contract inspection reveals the flow should work:
- Write `backend/scripts/smoke_vapi_appointment_capture.py` (not a pytest file)
- It should construct a fake Vapi-shaped payload matching Module 56's adapter input
- Sign with the local HMAC secret
- POST to `http://127.0.0.1:8000/webhooks/vapi/call-event`
- Print the HTTP status and response
- Query `GET /appointment-requests?clinic_id=…` to confirm the new row appears

This script is for manual local use only — it must not be a pytest test (no real DB in tests rule).

### 4. Update docs

- `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` — update "Unknowns" section
  with findings from the inspection
- `docs/claude/CURRENT_STATE.md` — record Module 83
- `docs/claude/NEXT_MODULE.md` — Sprint 11 / Module 84 — Reject Action

## What not to do

- Do not modify Vapi configuration, n8n workflows, or production webhook routes.
- Do not use real patient data, real phone numbers, or real clinic credentials.
- Do not auto-confirm appointment requests or auto-create calendar events.
- Do not add a live Vapi connection — the fixture smoke uses a constructed local payload only.
- Do not change the seed script or remove any existing seed rows.

## Acceptance

- Contract inspection complete — findings documented.
- Any gaps in the capture path covered by static contract tests.
- Smoke script written (if capture path is viable) or gaps documented (if not).
- `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` updated with findings.
- Full backend tests pass: `pytest -v backend/tests`
- Commit: `Sprint 11 / Module 83 — Vapi intake to appointment dashboard smoke harness`
