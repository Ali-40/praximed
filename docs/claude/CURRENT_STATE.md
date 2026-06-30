# PraxisMed — Current State

## Completed and committed modules

1. Module 1 — Secure clinic config loader
   - `backend/app/core/config_loader.py`
   - Secure tenant config loading
   - Path traversal/symlink protections
   - Clinic config cache

2. Module 2 — asyncpg PostgreSQL pool
   - `backend/app/db/pool.py`

3. Module 3 — PostgreSQL schema contract
   - `backend/app/db/schema.sql`
   - schema contract tests

4. Module 4 — Calendar repository layer
   - `backend/app/db/repositories/calendar_repo.py`

5. Module 5 — Availability engine
   - `backend/app/modules/calendar_sync/availability_engine.py`

6. Module 6 — Calendar sync service
   - `backend/app/modules/calendar_sync/calendar_sync.py`

7. Module 7 — FastAPI skeleton and health routes
   - `backend/app/main.py`
   - health routes

8. Module 8 — n8n calendar sync webhook route
   - `POST /webhooks/n8n/calendar-sync`

9. Modules 9–10 — Availability schemas and API routes
   - `POST /calendar/availability/check`
   - `POST /calendar/availability/suggest`

10. Modules 11–12 — Vapi prompt builder and Vapi tool routes
   - Vapi prompt builder
   - `POST /vapi/tools/check-availability`
   - `POST /vapi/tools/suggest-slots`

11. Modules 13–14 — Vapi call logs and call event webhook
   - `clinic_call_logs`
   - call repository
   - Vapi call event handler
   - `POST /webhooks/vapi/call-event`

12. Claude orchestration docs created
   - `docs/claude/PROJECT_CONTEXT.md`
   - `docs/claude/ROADMAP.md`
   - `docs/claude/CURRENT_STATE.md`
   - `docs/claude/NEXT_MODULE.md`

13. Module 15 — Appointment request schema contract
   - Commit: 2a71deb
   - `backend/app/db/schema.sql` — added `appointment_requests` table
   - `backend/tests/test_schema_contract.py` — extended to 158 tests
   - Schema tests: 158/158 passed
   - Full backend tests: 349/349 passed

14. Module 16 — Appointment request repository
   - Commit: d7707c2
   - `backend/app/db/repositories/appointment_request_repo.py`
   - `backend/tests/test_appointment_request_repo.py`
   - Module 16 tests: 20/20 passed
   - Full backend tests: 369/369 passed

15. Module 17 — Appointment request API schemas and routes
   - Commit: be1a346
   - `backend/app/schemas/appointment_requests.py`
   - `backend/app/api/routes/appointment_requests.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_appointment_request_schemas.py`
   - `backend/tests/test_appointment_request_routes.py`
   - Module 17 tests: 27/27 passed
   - Full backend tests: 396/396 passed

## Latest git log expected

- Sprint 1 / Module 23 — Notification API routes
- Sprint 1 / Module 22 — Vapi notification integration
- Sprint 1 / Module 21 — Notification router service
- Sprint 1 / Module 20 — Notification repository
- Sprint 1 / Module 19 — Notification schema contract
- Sprint 1 / Module 18 — Vapi appointment capture integration
- Populate Claude orchestration docs for Module 18
- Sprint 1 / Module 17 — Appointment request API routes
- Populate Claude orchestration docs for Module 17
- Sprint 1 / Module 16 — Appointment request repository
- Populate Claude orchestration docs for Module 16
- Sprint 1 / Module 15 — Appointment request schema contract
- Populate Claude orchestration docs for Module 15
- Add Claude orchestration docs
- Sprint 1 / Modules 13–14 — Vapi call logs and call event webhook
- Sprint 1 / Modules 11–12 — Vapi prompt builder and tool routes
- Sprint 1 / Modules 9–10 — Availability schemas and API routes
- Sprint 1 / Module 8 — n8n Calendar Sync Webhook Route
- Sprint 1 Module 7: FastAPI skeleton and health routes
- Sprint 1 Module 6: calendar sync service
- Sprint 1 Module 5: availability engine
- Sprint 1 Module 4: calendar repository layer
- Sprint 1 Module 3: PostgreSQL schema contract
- Sprint 1 Module 2: asyncpg connection pool
- Sprint 1 Module 1: secure clinic config loader

16. Module 18 — Vapi appointment capture integration
   - Commit: 9231a6b
   - `backend/app/modules/vapi/vapi_appointment_capture.py`
   - `backend/app/schemas/vapi.py` (updated)
   - `backend/app/api/routes/vapi_tools.py` (updated)
   - `backend/tests/test_vapi_appointment_capture.py`
   - `backend/tests/test_vapi_tool_routes.py` (updated)
   - Module 18 tests: 34/34 passed
   - Full backend tests: 419/419 passed

17. Module 19 — Notification schema contract
   - Commit: 8814c0b
   - `backend/app/db/schema.sql` — added `clinic_notifications` table
   - `backend/tests/test_schema_contract.py` — extended to 194 tests
   - Schema tests: 194/194 passed
   - Full backend tests: 455/455 passed

18. Module 20 — Notification repository
   - Commit: 6c37a74
   - `backend/app/db/repositories/notification_repo.py`
   - `backend/tests/test_notification_repo.py`
   - Module 20 tests: 26/26 passed
   - Full backend tests: 481/481 passed

19. Module 21 — Notification router service
   - Commit: c0d4bd4
   - `backend/app/modules/notifications/__init__.py`
   - `backend/app/modules/notifications/notification_router.py`
   - `backend/tests/test_notification_router.py`
   - Module 21 tests: 21/21 passed
   - Full backend tests: 502/502 passed

20. Module 22 — Vapi notification integration
   - Commit: 2e6d53f
   - `backend/app/modules/vapi/vapi_event_handler.py` (updated)
   - `backend/app/modules/vapi/vapi_appointment_capture.py` (updated)
   - `backend/tests/test_vapi_event_handler.py` (updated)
   - `backend/tests/test_vapi_appointment_capture.py` (updated)
   - Module 22 tests: 42/42 passed
   - Full backend tests: 519/519 passed

21. Module 23 — Notification API routes
   - Commit: 085cafa
   - `backend/app/schemas/notifications.py`
   - `backend/app/api/routes/notifications.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_notification_schemas.py`
   - `backend/tests/test_notification_routes.py`
   - Module 23 tests: 26/26 passed
   - Full backend tests: 545/545 passed

## Architecture checkpoint

- Architecture Checkpoint 01 created: `docs/claude/ARCHITECTURE_CHECKPOINT_01.md`
- Sprint 1 complete (Modules 1–23)
- Sprint 2 scope defined: Clinical Documentation Engine (Modules 24–34)

## Next module
Sprint 2 / Module 24 — Patient Schema Contract.
