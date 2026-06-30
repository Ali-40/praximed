# Sprint 1 / Module 22 — Vapi Notification Integration

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
18. Module 21: notification router service

All are committed. Do not modify completed modules unless absolutely required.

## Task scope
Integrate the notification router into existing Vapi flows so important Vapi events create internal notification records.

## Purpose
PraxisMed should automatically create internal clinic notifications when:
1. Vapi call event requires human handoff or urgent attention.
2. Vapi appointment capture creates a new appointment request.

This module must not send SMS, push, email, or external webhooks yet.
It only creates internal notification records through the existing `notification_router` service.

## Create or update only

1. `backend/app/modules/vapi/vapi_event_handler.py`
2. `backend/app/modules/vapi/vapi_appointment_capture.py`
3. `backend/tests/test_vapi_event_handler.py`
4. `backend/tests/test_vapi_appointment_capture.py`
5. `docs/claude/CURRENT_STATE.md`
6. `docs/claude/NEXT_MODULE.md`

Do not create notification API routes yet.
Do not build SMS, push, email, or frontend.
Do not modify `notification_repo.py` or `notification_router.py` unless absolutely required.
Do not use a real database in tests.

## Integration requirements

### A) Update `vapi_event_handler.py`

In `process_vapi_call_event`:

**Existing behavior must remain** (normalize payload, upsert call log, return ok response).

**Add notification integration:**

- When `event_type == "human_handoff.required"`: call `notification_router.create_urgent_call_notification`
- When `event_type == "call.ended"` AND (`urgency_level in ["urgent", "emergency"]` OR `action_required` is true): call `create_urgent_call_notification`
- If notification creation fails, do not fail the call event processing — set `notification_created=False`
- Return dict includes `notification_created: bool`

### B) Update `vapi_appointment_capture.py`

In `capture_vapi_appointment_request`:

**Existing behavior must remain** (validate, load config, create appointment request, return ok + staff confirmation message).

**Add notification integration:**

- After `appointment_request_repo.create_appointment_request` succeeds, call `notification_router.create_appointment_request_notification`
- If notification fails: `notification_created=False`, but still return `ok=True`
- If notification succeeds: `notification_created=True`
- Do not create notification before appointment request creation succeeds
- Do not confirm or book the appointment

## Testing requirements

### Update `test_vapi_event_handler.py` — add 7 tests

1. `human_handoff.required` creates urgent call notification.
2. Urgent `call.ended` creates urgent call notification.
3. `action_required` `call.ended` creates urgent call notification.
4. Normal `call.ended` does not create notification.
5. Notification failure does not break successful call event processing.
6. Process result includes `notification_created=True` when created.
7. Process result includes `notification_created=False` when skipped or failed.

Existing tests must still pass.

### Update `test_vapi_appointment_capture.py` — add 10 tests

1. Creates appointment request notification after repository success.
2. Passes `request_id` to notification helper when available.
3. Passes `patient_name` to notification helper.
4. Passes `urgency_level` to notification helper.
5. Does not create notification if appointment request creation fails.
6. Notification failure does not break successful appointment request capture.
7. Response includes `notification_created=True` when created.
8. Response includes `notification_created=False` when notification fails.
9. Response message still says staff confirmation is required.
10. Response message does not say appointment is confirmed.

Mock `notification_router` functions in tests. No real database.

## Run

```
pytest -v backend/tests/test_vapi_event_handler.py
pytest -v backend/tests/test_vapi_appointment_capture.py
```

Then run all tests:

```
pytest -v backend/tests
```

## Acceptance criteria

- All Module 22 tests pass.
- All previous tests still pass.
- No real database connection is used.
- Human handoff / urgent Vapi events create notification records.
- Vapi appointment capture creates a notification record.
- Notification failures do not break the primary flow.
- No actual SMS/push/email sent.
- No notification API routes created.
- Commit all changes only if tests pass.

## Commit message

`Sprint 1 / Module 22 — Vapi notification integration`
