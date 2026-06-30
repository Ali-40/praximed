# Sprint 3 / Module 38 — Apply Tenant Guards to Appointment Requests and Notifications

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–34: all committed.
- Sprint 3, Modules 35–37: all committed.

Do not modify completed modules unless absolutely required.

## Task scope
Apply the existing AuthContext and tenant access dependencies to remaining human-facing PHI/internal clinic routes:

1. /appointment-requests
2. /notifications

## Routes protected
- `/appointment-requests` — staff-level (owner, admin, doctor, staff)
- `/notifications` — staff-level (owner, admin, doctor, staff)

## Acceptance criteria

- All updated tests pass.
- All previous tests still pass.
- No Vapi/n8n/availability routes changed.
- No real database connection is used.
- Commit all changes only if tests pass.

## Commit message

`Sprint 3 / Module 38 — Apply tenant guards to appointment and notification routes`
