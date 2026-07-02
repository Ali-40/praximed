# Sprint 10 / Module 79 — Dashboard Visual Polish Pass

Status: pending Module 78 review.

## Context

Module 78 fixed the patient name display issue — the highest-priority visible defect
identified in Architecture Checkpoint 08. The local demo now shows readable patient
names. The next step is a broader visual polish pass to make the dashboard look
credible before a stakeholder demo.

## Scope

Docs-only scoping required first. Before implementing, inspect the current dashboard
and decide what visual changes are worth doing in one focused pass. Target:

1. **Section headers with row counts** — show e.g. "Appointments (1)" so the demo
   communicates how many items exist at a glance.
2. **Status badge consistency** — review badge styling across all four sections
   to ensure colours are consistent and readable.
3. **Empty state copy** — confirm the empty state messages are friendly and not
   generic error-looking ("No appointment requests found." → acceptable; very
   terse messages may need softening).
4. **Loading state copy** — confirm loading messages are consistent.
5. Optional: Add a thin section divider or icon to each section header.

## What not to do

- Do not add new API calls or backend routes.
- Do not implement create/edit forms.
- Do not implement appointment request workflow actions (approve/reject).
- Do not change auth or token storage.
- Do not install new npm packages.

## Acceptance

- Dashboard looks visually coherent in a live browser demo.
- All four sections still render loading → list state after seed.
- Patient row displays "Local Test Patient" (Module 78 fix preserved).
- Full backend contract tests pass: `pytest -v backend/tests`
- Commit: `Sprint 10 / Module 79 — Dashboard visual polish pass`
