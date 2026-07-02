# Sprint 11 / Module 82 — Appointment Workflow Browser Smoke Evidence

Status: pending Module 81 commit.

## Context

Module 81 added a **Confirm** button to appointment request rows with `status === 'new'`.
The button calls `PATCH /appointment-requests/{id}/status` and refreshes the appointments
list on success. This module records browser evidence that the Confirm action works
end-to-end in a real browser against the local backend.

## Scope

Docs-only. No production code changes.

1. Run the local stack:
   - `python backend/scripts/seed_local_data.py` — upsert seed rows (idempotent)
   - `uvicorn backend.app.main:app --reload --port 8000`
   - `cd frontend && npm run dev`

2. Perform the smoke in a browser:
   - Login with local-dev credentials → `/dashboard`
   - Confirm the seeded appointment request row shows a **Confirm** button (status: new)
   - Click Confirm — observe button goes to "Confirming…" (disabled) while in-flight
   - Observe row status badge updates to "confirmed" and button disappears
   - Confirm no error message is shown

3. Create `docs/runtime/FRONTEND_APPOINTMENT_WORKFLOW_SMOKE_RESULTS.md`:
   - Date, sprint, verdict
   - Environment table (same as Module 80 smoke)
   - Steps completed table
   - Evidence: what was observed at each step
   - What this proves
   - What remains (Reject, Assign, Callback, Archive not yet built)
   - Recommended next step

4. Update `docs/claude/CURRENT_STATE.md` — record Module 82
5. Update `docs/claude/NEXT_MODULE.md` — Sprint 11 / Module 83 — Reject Action

## Acceptance

- Browser smoke evidence document created.
- Confirm flow proven end-to-end: button visible → click → status updates → button gone.
- `docs/claude/CURRENT_STATE.md` updated.
- `docs/claude/NEXT_MODULE.md` updated.
- Commit: `Sprint 11 / Module 82 — Appointment workflow browser smoke evidence`
