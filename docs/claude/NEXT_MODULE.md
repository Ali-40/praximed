# Sprint 1 / Module 20 — Notification Repository

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
16. Module 19: notification schema contract

All are committed. Do not modify completed modules unless absolutely required.

## Task scope
Create the database repository layer for clinic_notifications.

## Purpose
PraxisMed needs a clean repository to create and manage internal notification records before adding SMS, push, email, or frontend notification delivery.

## Create or update only

1. `backend/app/db/repositories/notification_repo.py`
2. `backend/tests/test_notification_repo.py`
3. `docs/claude/CURRENT_STATE.md`
4. `docs/claude/NEXT_MODULE.md`

Do not create notification sender code yet.
Do not build SMS.
Do not build push.
Do not build email.
Do not build frontend.
Do not modify Vapi modules.
Do not modify appointment request modules.
Do not use a real database in tests.

## Repository requirements

### File: `backend/app/db/repositories/notification_repo.py`

### Custom exceptions
- `NotificationRepoError`
- `InvalidNotificationError`

### Allowed values
- channel: `internal`, `sms`, `push`, `email`, `webhook`
- notification_type: `urgent_call`, `human_handoff`, `callback_needed`, `appointment_request`, `cancellation`, `calendar_sync_failure`, `summary_ready`, `system`
- priority: `low`, `normal`, `high`, `urgent`, `emergency`
- status: `pending`, `sent`, `failed`, `read`, `cancelled`

### Public async functions

#### 1. `create_notification(pool, clinic_id, channel, notification_type, title, message, priority="normal", recipient_user_id=None, status="pending", related_resource_type=None, related_resource_id=None, scheduled_for=None, raw_payload=None)`

Behavior:
- Validate `clinic_id` is not empty.
- Validate `channel`.
- Validate `notification_type`.
- Validate `priority`.
- Validate `status`.
- Validate `title` is not empty.
- Validate `message` is not empty.
- Use parameterized SQL only.
- Insert into `clinic_notifications`.
- Return created row.

#### 2. `get_notification_by_id(pool, clinic_id, notification_id)`

Behavior:
- Return matching notification or None.
- Must filter by `clinic_id`.

#### 3. `list_notifications(pool, clinic_id, status=None, priority=None, notification_type=None, recipient_user_id=None, limit=50)`

Behavior:
- Return recent notifications for a clinic.
- Must filter by `clinic_id`.
- `limit` must be between 1 and 100.
- Optional filters for `status`, `priority`, `notification_type`, `recipient_user_id`.
- Validate filters if provided.

#### 4. `mark_notification_sent(pool, clinic_id, notification_id)`

Behavior:
- Set `status='sent'`.
- Set `sent_at=now()`.
- Return updated row.

#### 5. `mark_notification_failed(pool, clinic_id, notification_id, error_message)`

Behavior:
- Validate `error_message` is not empty.
- Set `status='failed'`.
- Set `error_message`.
- Return updated row.

#### 6. `mark_notification_read(pool, clinic_id, notification_id)`

Behavior:
- Set `status='read'`.
- Set `read_at=now()`.
- Return updated row.

#### 7. `cancel_notification(pool, clinic_id, notification_id)`

Behavior:
- Set `status='cancelled'`.
- Return updated row.

### Implementation rules
- Use async functions.
- Use asyncpg-style pool.
- Use `pool.fetchrow` and `pool.fetch`.
- Use parameterized SQL placeholders only.
- No direct database connection in tests.
- No external service calls.
- Keep repository small and readable.

## Tests required in `test_notification_repo.py`

1. `create_notification` calls `fetchrow`.
2. `create_notification` raises `InvalidNotificationError` for empty `clinic_id`.
3. `create_notification` raises `InvalidNotificationError` for empty `title`.
4. `create_notification` raises `InvalidNotificationError` for empty `message`.
5. `create_notification` validates invalid `channel`.
6. `create_notification` validates invalid `notification_type`.
7. `create_notification` validates invalid `priority`.
8. `create_notification` validates invalid `status`.
9. `get_notification_by_id` calls `fetchrow` and filters by `clinic_id`.
10. `list_notifications` calls `fetch`.
11. `list_notifications` validates `limit`.
12. `list_notifications` supports `status` filter.
13. `list_notifications` supports `priority` filter.
14. `list_notifications` supports `notification_type` filter.
15. `list_notifications` supports `recipient_user_id` filter.
16. `mark_notification_sent` calls `fetchrow`.
17. `mark_notification_failed` calls `fetchrow` and validates `error_message`.
18. `mark_notification_read` calls `fetchrow`.
19. `cancel_notification` calls `fetchrow`.
20. SQL uses parameterized placeholders, not string formatting.

## Run

```
pytest -v backend/tests/test_notification_repo.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 20 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Only `notification_repo.py`, its tests, and orchestration docs are changed.
- No sender code yet.
- No SMS/push/email yet.
- Commit all changes only if tests pass.

## Commit message

`Sprint 1 / Module 20 — Notification repository`
