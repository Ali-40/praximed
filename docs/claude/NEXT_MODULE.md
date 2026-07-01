# Sprint 4 / Module 43 — Audit Route Integration

## Purpose

Module 42 created the audit logging foundation (repository + service layer).
Module 43 wires audit logging into the existing PHI-changing routes so that
compliance-relevant actions are recorded automatically.

No new tables. No schema changes. Route integration only.

## Scope

Wire `audit_logger.safe_record_audit_event` into:

1. Appointment request routes (create, status update)
2. Patient routes (create, update)
3. Consultation session routes (create, approve, reject)
4. Notification routes (create)

Use `safe_record_audit_event` — audit failure must never break the primary
business action.

## Files to create or update

1. `backend/app/api/routes/appointment_requests.py` (updated)
2. `backend/app/api/routes/patients.py` (updated)
3. `backend/app/api/routes/consultations.py` (updated)
4. `backend/app/api/routes/notifications.py` (updated)
5. `backend/tests/test_appointment_request_routes.py` (updated)
6. `backend/tests/test_patient_routes.py` (updated)
7. `backend/tests/test_consultation_routes.py` (updated)
8. `backend/tests/test_notification_routes.py` (updated)
9. `docs/claude/CURRENT_STATE.md`
10. `docs/claude/NEXT_MODULE.md`

## Do not modify

- `backend/app/db/schema.sql`
- `backend/migrations/`
- `backend/app/db/repositories/audit_repo.py`
- `backend/app/modules/audit/audit_logger.py`
- `backend/app/core/auth_context.py`
- `backend/app/core/machine_auth.py`

## Commit message

Sprint 4 / Module 43 — Audit route integration
