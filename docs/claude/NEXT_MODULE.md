# Sprint 9 / Module 76 — Dashboard Empty-State and Local Demo Data Polish

## Context

The full browser smoke (Module 75) passed with verdict PASS. The Appointments and
Notifications sections showed empty state during the smoke because the seed script
does not create appointment requests or notifications. Before a demo, these sections
should show realistic (but still fake) data to demonstrate the full dashboard flow.

## Scope

1. Add one deterministic fake appointment request to `backend/scripts/seed_local_data.py`.
   - `id`: fixed UUID (e.g. `55555555-5555-5555-5555-555555555555`)
   - `clinic_id`: `11111111-1111-1111-1111-111111111111` (existing seed clinic)
   - `patient_id`: `33333333-3333-3333-3333-333333333333` (existing seed patient)
   - `patient_name_snapshot`: `"Local Test Patient"` (matches seeded patient)
   - `status`: `"pending"`
   - `urgency`: `"routine"`
   - Use `ON CONFLICT (id) DO UPDATE SET ... updated_at = now()` for idempotency

2. Add one deterministic fake notification to `backend/scripts/seed_local_data.py`.
   - `id`: fixed UUID (e.g. `66666666-6666-6666-6666-666666666666`)
   - `clinic_id`: `11111111-1111-1111-1111-111111111111`
   - `patient_id`: `33333333-3333-3333-3333-333333333333`
   - `title`: `"Local Test Notification"`
   - `priority`: `"normal"`
   - `notification_type`: `"appointment_reminder"`
   - Use `ON CONFLICT (id) DO UPDATE SET ... updated_at = now()` for idempotency

3. Update `main()` printout in the seed script to include the new IDs.

4. Keep all data clearly labeled fake/local only.

5. Add contract tests to `backend/tests/test_local_seed_contract.py` covering the new
   appointment request and notification seed rows (at minimum: UUID constants present,
   INSERT references the correct tables, no real data used).

6. Verify the dashboard renders list state (not empty state) for all four sections by
   re-running the smoke manually. Record the result.

## What not to do

- Do not add new backend routes or change existing routes.
- Do not change frontend code.
- Do not use real patient data or production credentials.
- Do not change the existing clinic, doctor user, patient, or consultation seed rows.

## Acceptance

- `seed_local_data.py` creates a fake appointment request and a fake notification.
- Script remains idempotent (safe to run multiple times).
- Contract tests pass: `pytest -v backend/tests/test_local_seed_contract.py`
- Full backend tests pass: `pytest -v backend/tests`
- Dashboard Appointments section shows list (not empty) after re-seed.
- Dashboard Notifications section shows list (not empty) after re-seed.
- Commit: `Sprint 9 / Module 76 — Dashboard empty-state and local demo data polish`
