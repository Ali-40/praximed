# Sprint 3 / Module 37 — Apply Tenant Guards to Clinical PHI Routes

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–34: all committed.
- Sprint 3, Modules 35–36: all committed.

Do not modify completed modules unless absolutely required.

## Task scope
Apply AuthContext and tenant access dependencies to patient, consultation, and clinical workflow routes.

## Routes protected
- `/patients` — staff-level (owner, admin, doctor, staff)
- `/consultations` — clinical-level (owner, admin, doctor)
- `/clinical-workflows` — clinical-level (owner, admin, doctor)

## Acceptance criteria

- All updated tests pass.
- All previous tests still pass.
- No Vapi/n8n/availability/appointment-request/notification routes changed.
- No real database connection is used.
- Commit all changes only if tests pass.

## Commit message

`Sprint 3 / Module 37 — Apply tenant guards to clinical PHI routes`
