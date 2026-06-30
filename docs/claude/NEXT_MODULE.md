# Sprint 1 / Module 21 — Notification Router Service

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
17. Module 20: notification repository

All are committed. Do not modify completed modules unless absolutely required.

## Task scope
Create the internal notification routing service.

## Purpose
PraxisMed needs a service that converts important system events into clinic notification records using the existing notification repository.

This module does not send SMS, push, email, or webhooks yet.
It only decides notification content/priority/channel and creates records in `clinic_notifications`.

## Create or update only

1. `backend/app/modules/notifications/__init__.py`
2. `backend/app/modules/notifications/notification_router.py`
3. `backend/tests/test_notification_router.py`
4. `docs/claude/CURRENT_STATE.md`
5. `docs/claude/NEXT_MODULE.md`

Do not create notification sender code yet.
Do not build SMS.
Do not build push.
Do not build email.
Do not build frontend.
Do not modify Vapi modules.
Do not modify appointment request modules.
Do not create FastAPI routes.
Do not use a real database in tests.

## Module requirements

### File: `backend/app/modules/notifications/notification_router.py`

### Custom exceptions
- `NotificationRouterError`
- `InvalidNotificationEventError`

### Supported notification types
`urgent_call`, `human_handoff`, `callback_needed`, `appointment_request`, `cancellation`, `calendar_sync_failure`, `summary_ready`, `system`

### Allowed channels
`internal`, `sms`, `push`, `email`, `webhook`

### Allowed priorities
`low`, `normal`, `high`, `urgent`, `emergency`

### Public functions

#### 1. `infer_priority(notification_type, urgency_level=None) -> str`

- If `urgency_level` is provided and valid (`low`, `normal`, `urgent`, `emergency`), map it directly.
- If `urgency_level` is not provided, use type defaults:
  - `urgent_call` → `urgent`
  - `human_handoff` → `urgent`
  - `callback_needed` → `high`
  - `appointment_request` → `normal`
  - `cancellation` → `high`
  - `calendar_sync_failure` → `high`
  - `summary_ready` → `normal`
  - `system` → `normal`
- Invalid `notification_type` raises `InvalidNotificationEventError`.
- Invalid `urgency_level` raises `InvalidNotificationEventError`.

#### 2. `build_notification_event(clinic_id, notification_type, title, message, channel="internal", priority=None, urgency_level=None, recipient_user_id=None, related_resource_type=None, related_resource_id=None, scheduled_for=None, raw_payload=None) -> dict`

- Validate `clinic_id` not empty.
- Validate `notification_type`.
- Validate `title` not empty.
- Validate `message` not empty.
- Validate `channel`.
- If `priority` is None, call `infer_priority`.
- If `priority` is provided, validate it.
- Return normalized event dict with all fields.

#### 3. `route_notification_event(pool, event: dict) -> dict`

- Validate/normalize event using `build_notification_event`.
- Call `notification_repo.create_notification` with normalized values.
- Return `{ok: True, notification: ..., message: "..."}`.

#### 4. `create_urgent_call_notification(pool, clinic_id, call_id, caller_phone=None, urgency_level="urgent", recipient_user_id=None, raw_payload=None) -> dict`

- Creates internal `urgent_call` notification.
- `related_resource_type = "clinic_call_logs"`, `related_resource_id = call_id`.
- Message includes `caller_phone` if provided.

#### 5. `create_appointment_request_notification(pool, clinic_id, request_id, patient_name, urgency_level="normal", recipient_user_id=None, raw_payload=None) -> dict`

- Creates internal `appointment_request` notification.
- `related_resource_type = "appointment_requests"`, `related_resource_id = request_id`.
- Message includes `patient_name`.

#### 6. `create_calendar_sync_failure_notification(pool, clinic_id, message, recipient_user_id=None, raw_payload=None) -> dict`

- Creates internal `calendar_sync_failure` notification with priority `high`.
- `related_resource_type = "calendar_sync"`.

## Tests required in `test_notification_router.py`

1. `infer_priority` returns `urgent` for `urgent_call`.
2. `infer_priority` returns `high` for `callback_needed`.
3. `infer_priority` uses `urgency_level` override.
4. `infer_priority` raises for invalid `notification_type`.
5. `infer_priority` raises for invalid `urgency_level`.
6. `build_notification_event` returns normalized event.
7. `build_notification_event` defaults channel to `internal`.
8. `build_notification_event` infers priority when `priority` is None.
9. `build_notification_event` validates empty `clinic_id`.
10. `build_notification_event` validates empty `title`.
11. `build_notification_event` validates empty `message`.
12. `build_notification_event` validates invalid `channel`.
13. `build_notification_event` validates invalid `priority`.
14. `route_notification_event` calls `notification_repo.create_notification`.
15. `route_notification_event` passes normalized values to `create_notification`.
16. `create_urgent_call_notification` creates `urgent_call` with `related_resource_type=clinic_call_logs`.
17. `create_urgent_call_notification` includes `caller_phone` in message if provided.
18. `create_appointment_request_notification` creates `appointment_request` with `related_resource_type=appointment_requests`.
19. `create_appointment_request_notification` includes `patient_name` in message.
20. `create_calendar_sync_failure_notification` creates `calendar_sync_failure` with high priority.
21. Repository error is handled or propagated cleanly.

## Run

```
pytest -v backend/tests/test_notification_router.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 21 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Only `notification_router.py`, its tests, `__init__.py`, and orchestration docs are changed.
- No sender code yet.
- No SMS/push/email yet.
- No FastAPI routes yet.
- Commit all changes only if tests pass.

## Commit message

`Sprint 1 / Module 21 — Notification router service`
