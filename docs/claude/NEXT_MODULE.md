# Sprint 10 / Module 80 — Local Demo Retest After Visual Polish

Status: pending Module 79 review.

## Context

Module 79 made several visual changes to the dashboard:
- Header now shows "Clinic Dashboard" subtitle.
- Page heading changed to "Clinic Overview".
- Each section heading shows a row-count pill when data is loaded.
- Status/priority badges use shared BADGE_STYLES helper and CSS token colours.
- Local-demo footer label added.

A manual browser smoke should confirm these changes render correctly and that all
four dashboard sections still load list state after re-seeding.

## Scope

Docs only. No code changes.

1. Run the local stack:
   - `python backend/scripts/seed_local_data.py` (idempotent re-seed)
   - `uvicorn backend.app.main:app --reload --port 8000`
   - `npm run dev` in `frontend/`
2. Login at `http://localhost:3000` with local-dev credentials.
3. Verify the updated dashboard:
   - Header shows "PraxisMed" + "Clinic Dashboard" subtitle.
   - Page heading shows "Clinic Overview".
   - All four sections show row-count pills (1 appointment, 1 patient, 1 notification, 1 consultation).
   - Patient row shows "Local Test Patient" (not `"—"`).
   - Status badges are colour-coded correctly.
   - Footer label "Local demo — all data is fake…" visible.
4. Create or update `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` with Module 80 evidence.
5. Update `docs/claude/CURRENT_STATE.md` with Module 79 completed and Module 80 entry.
6. Update `docs/claude/NEXT_MODULE.md` to Sprint 10 / Module 81 or Architecture Checkpoint 09.

## What not to do

- Do not change frontend code.
- Do not change backend routes, schemas, or migrations.
- Do not change seed script or test files.

## Acceptance

- All four sections render list state with count pills.
- Patient row shows "Local Test Patient".
- "Clinic Dashboard" subtitle visible in header.
- "Clinic Overview" heading visible.
- Local-demo footer label visible.
- Full backend tests pass: `pytest -v backend/tests`
- Commit: `Sprint 10 / Module 80 — Local demo retest after visual polish`
