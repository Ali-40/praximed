# Sprint 1 / Module 23 — Notification API Routes

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
1–22 all committed. Do not modify completed modules unless absolutely required.

## Task scope
Create API schemas and FastAPI routes for internal clinic notifications.

## Purpose
PraxisMed needs API routes so the future receptionist/doctor dashboard can:
- list notifications
- view a specific notification
- mark notification as read
- cancel a pending notification
- manually create an internal notification if needed

This module does not send SMS, push, email, or external webhooks.

## Create or update only

1. `backend/app/schemas/notifications.py`
2. `backend/app/api/routes/notifications.py`
3. `backend/app/api/router.py`
4. `backend/tests/test_notification_schemas.py`
5. `backend/tests/test_notification_routes.py`
6. `docs/claude/CURRENT_STATE.md`
7. `docs/claude/NEXT_MODULE.md`

## Schema requirements

### `NotificationCreate`
- `clinic_id: str` — must not be empty
- `channel: str = "internal"` — one of: `internal`, `sms`, `push`, `email`, `webhook`
- `notification_type: str` — one of: `urgent_call`, `human_handoff`, `callback_needed`, `appointment_request`, `cancellation`, `calendar_sync_failure`, `summary_ready`, `system`
- `title: str` — must not be empty
- `message: str` — must not be empty
- `priority: str = "normal"` — one of: `low`, `normal`, `high`, `urgent`, `emergency`
- `recipient_user_id: str | None = None`
- `related_resource_type: str | None = None`
- `related_resource_id: str | None = None`
- `scheduled_for: datetime | None = None`
- `raw_payload: dict | None = None`

### `NotificationResponse`
- `ok: bool`
- `notification: dict | None = None`
- `message: str | None = None`

### `NotificationListResponse`
- `ok: bool`
- `notifications: list[dict]`
- `message: str | None = None`

## Routes requirements

### `POST /notifications`
Accept `NotificationCreate`, call `notification_repo.create_notification`, return `NotificationResponse`.

### `GET /notifications`
Query params: `clinic_id`, `status?`, `priority?`, `notification_type?`, `recipient_user_id?`, `limit=50`.
Call `notification_repo.list_notifications`, return `NotificationListResponse`.

### `GET /notifications/{notification_id}`
Query param: `clinic_id`. Call `notification_repo.get_notification_by_id`. 404 if None.

### `POST /notifications/{notification_id}/read`
Query param: `clinic_id`. Call `notification_repo.mark_notification_read`. 404 if None.

### `POST /notifications/{notification_id}/cancel`
Query param: `clinic_id`. Call `notification_repo.cancel_notification`. 404 if None.

### Error handling
- Missing `db_pool` → HTTP 503
- Invalid repo input → HTTP 400
- Not found → HTTP 404
- Unexpected error → HTTP 500

## Commit message

`Sprint 1 / Module 23 — Notification API routes`
