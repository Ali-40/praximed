# Sprint 10 / Module 78 — Dashboard Demo Polish and Patient Display Fix

Status: pending Architecture Checkpoint 08 review.

## Context

Architecture Checkpoint 08 identified the patient name fallback (`"—"`) as the
highest-priority visible defect before a stakeholder demo. The backend `patients` table
stores `full_name` as a single field; the frontend `Patient` TypeScript interface only
exposes `first_name` and `last_name`, so the display expression
`[patient.first_name, patient.last_name].filter(Boolean).join(' ')` produces `"—"`.

## Scope

1. Add `full_name` to the `Patient` interface in `frontend/lib/api.ts`:
   ```ts
   interface Patient {
     id: string
     full_name: string        // added — backend returns this as a single field
     first_name?: string
     last_name?: string
     status: string
   }
   ```

2. Update the patient row display in `frontend/app/dashboard/page.tsx`:
   - Current: `[patient.first_name, patient.last_name].filter(Boolean).join(' ') || '—'`
   - Updated: `patient.full_name || [patient.first_name, patient.last_name].filter(Boolean).join(' ') || '—'`
   - This is backwards-compatible: uses `full_name` if present, falls back to split fields.

3. Update `backend/tests/test_frontend_patient_list_contract.py`:
   - Add a test confirming `full_name` is referenced in `frontend/lib/api.ts`.
   - Add a test confirming the patient row display uses `full_name`.

4. Manual browser verification:
   - Re-seed: `python backend/scripts/seed_local_data.py`
   - Login at `http://localhost:3000`
   - Patients section shows "Local Test Patient" (not `"—"`).

## What not to do

- Do not change the backend patients API response shape.
- Do not add new dashboard sections or features.
- Do not implement token refresh, httpOnly cookies, or any auth changes.
- Do not add create/edit flows.

## Acceptance

- Patients section shows "Local Test Patient" (not `"—"`) after re-seed and login.
- `full_name` field added to `Patient` interface in `lib/api.ts`.
- Patient row display uses `full_name` in `dashboard/page.tsx`.
- Contract tests confirm both changes.
- Full backend tests pass: `pytest -v backend/tests`
- Commit: `Sprint 10 / Module 78 — Dashboard demo polish and patient display fix`
