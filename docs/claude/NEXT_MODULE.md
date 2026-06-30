# Sprint 1 / Module 19 — Notification Schema Contract

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
1. Module 1: config loader
2. Module 2: asyncpg pool
3. Module 3: PostgreSQL schema contract
4. Module 4: calendar repository
5. Module 5: availability engine
6. Module 6: calendar sync service
7. Module 7: FastAPI skeleton and health routes
8. Module 8: n8n calendar sync webhook route
9. Modules 9–10: availability schemas and API routes
10. Modules 11–12: Vapi prompt builder and tool routes
11. Modules 13–14: Vapi call logs and call event webhook
12. Module 15: appointment request schema contract
13. Module 16: appointment request repository
14. Module 17: appointment request API schemas and routes
15. Module 18: Vapi appointment capture integration

All are committed. Do not modify completed modules unless absolutely required.

## Task scope
Add the database schema contract for internal notifications.

## Purpose
PraxisMed needs a notification system so doctors/receptionists can be alerted about:

- urgent Vapi calls
- human handoff required
- callback needed
- new appointment request
- cancellation
- calendar sync failure
- consultation summary ready later

## Create or update only

1. `backend/app/db/schema.sql`
2. `backend/tests/test_schema_contract.py`
3. `docs/claude/CURRENT_STATE.md`
4. `docs/claude/NEXT_MODULE.md`

Do not create repository code yet.
Do not create notification sender code yet.
Do not build SMS.
Do not build push.
Do not build email.
Do not modify Vapi modules.
Do not modify appointment request modules.
Do not build frontend.
No real database connection during tests.

## Schema requirement

Add table: `clinic_notifications`

### Required columns

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PRIMARY KEY |
| clinic_id | UUID NOT NULL | REFERENCES clinics(id) ON DELETE CASCADE |
| recipient_user_id | UUID | REFERENCES clinic_users(id) ON DELETE SET NULL |
| channel | TEXT NOT NULL | |
| notification_type | TEXT NOT NULL | |
| priority | TEXT NOT NULL | DEFAULT 'normal' |
| title | TEXT NOT NULL | |
| message | TEXT NOT NULL | |
| status | TEXT NOT NULL | DEFAULT 'pending' |
| related_resource_type | TEXT | |
| related_resource_id | TEXT | |
| scheduled_for | TIMESTAMPTZ | |
| sent_at | TIMESTAMPTZ | |
| read_at | TIMESTAMPTZ | |
| error_message | TEXT | |
| raw_payload | JSONB | |
| created_at | TIMESTAMPTZ NOT NULL | DEFAULT now() |
| updated_at | TIMESTAMPTZ NOT NULL | DEFAULT now() |

### Constraints

- `CHECK (channel IN ('internal', 'sms', 'push', 'email', 'webhook'))`
- `CHECK (notification_type IN ('urgent_call', 'human_handoff', 'callback_needed', 'appointment_request', 'cancellation', 'calendar_sync_failure', 'summary_ready', 'system'))`
- `CHECK (priority IN ('low', 'normal', 'high', 'urgent', 'emergency'))`
- `CHECK (status IN ('pending', 'sent', 'failed', 'read', 'cancelled'))`

### Indexes

- `clinic_notifications(clinic_id, created_at)`
- `clinic_notifications(clinic_id, status)`
- `clinic_notifications(clinic_id, priority)`
- `clinic_notifications(clinic_id, notification_type)`
- `clinic_notifications(clinic_id, recipient_user_id)`
- `clinic_notifications(clinic_id, scheduled_for)`
- `clinic_notifications(clinic_id, related_resource_type, related_resource_id)`

## Update test_schema_contract.py to verify

1. `clinic_notifications` table exists.
2. All critical columns exist.
3. `clinic_id` references `clinics(id)`.
4. `recipient_user_id` references `clinic_users(id)`.
5. Channel check constraint exists.
6. Notification type check constraint exists.
7. Priority check constraint exists.
8. Status check constraint exists.
9. All required indexes exist.
10. Existing schema contract tests still pass.

## Run

```
pytest -v backend/tests/test_schema_contract.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 19 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Only schema contract and orchestration docs are changed.
- No repository code yet.
- No notification sender code yet.
- Commit all changes only if tests pass.

## Commit message

`Sprint 1 / Module 19 — Notification schema contract`
