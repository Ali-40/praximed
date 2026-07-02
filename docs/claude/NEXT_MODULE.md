# Sprint 9 / Module 77 — Rerun Frontend Demo Data Browser Smoke Evidence

Status: pending Module 76 review.

## Context

Module 76 added two deterministic fake/local seed rows to `seed_local_data.py`:
- One appointment request (`55555555-5555-5555-5555-555555555555`)
- One notification (`66666666-6666-6666-6666-666666666666`)

The Module 75 browser smoke showed Appointments and Notifications in empty state.
Module 77 re-runs the smoke after the seed update to confirm all four sections
render list state.

## Scope

1. Follow `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` Steps 1–9.
2. Re-run `python backend/scripts/seed_local_data.py` (idempotent — safe to add new rows).
3. Log in at `http://localhost:3000` and verify all four dashboard sections:
   - **Appointments** — shows "Local Test Patient" (status: new)
   - **Patients** — shows "Local Test Patient" (status: active)
   - **Notifications** — shows "Local Test Notification" (priority: normal)
   - **Consultations** — shows "Local Test Consultation Session"
4. Update `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md`:
   - Add a Module 77 smoke row confirming list state for all four sections.
   - Date of re-smoke and verdict.
5. Update `docs/claude/CURRENT_STATE.md` with Module 76 completed and Module 77 entry.
6. Update `docs/claude/NEXT_MODULE.md` to the next sprint item.

## What not to do

- Do not add new backend routes or change existing routes.
- Do not change frontend code.
- Do not change seed UUIDs or existing clinic/user/patient/consultation rows.

## Acceptance

- All four dashboard sections show list state after re-seeding.
- `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` updated with Module 77 evidence.
- Full backend tests pass: `pytest -v backend/tests`
- Commit: `Sprint 9 / Module 77 — Rerun frontend demo data browser smoke evidence`
