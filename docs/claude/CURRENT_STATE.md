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

- Sprint 2 / Module 24 — Patient schema contract
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
- Commit: 9e66dbd
- Full backend tests: 545/545 passed
- Sprint 1 complete (Modules 1–23)
- Sprint 2 started: Clinical Documentation Engine (Modules 24–34)

22. Module 24 — Patient schema contract
   - Commit: bdbed09
   - `backend/app/db/schema.sql` — added `patients` table
   - `backend/tests/test_schema_contract.py` — extended to 223 tests
   - Schema tests: 223/223 passed
   - Full backend tests: 574/574 passed

23. Module 25 — Patient repository
   - Commit: 0f84ad3 / docs: fe1d438
   - `backend/app/db/repositories/patient_repo.py`
   - `backend/tests/test_patient_repo.py`
   - Module 25 tests: 21/21 passed
   - Full backend tests: 595/595 passed

24. Module 26 — Patient API routes
   - Commit: b902dba / docs: b8c1515
   - `backend/app/schemas/patients.py`
   - `backend/app/api/routes/patients.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_patient_schemas.py`
   - `backend/tests/test_patient_routes.py`
   - Module 26 tests: 34/34 passed
   - Full backend tests: 629/629 passed

25. Module 27 — Consultation session schema contract
   - Commit: 8cfe4a9 / docs: 4bbd514
   - `backend/app/db/schema.sql` — added `consultation_sessions` table
   - `backend/tests/test_schema_contract.py` — extended to 264 tests
   - Schema tests: 264/264 passed
   - Full backend tests: 670/670 passed

26. Module 28 — Consultation session repository
   - Commit: 45988e0 / docs: 364cc1a
   - `backend/app/db/repositories/consultation_repo.py`
   - `backend/tests/test_consultation_repo.py`
   - Module 28 tests: 32/32 passed
   - Full backend tests: 702/702 passed

27. Module 29 — Consultation session API routes
   - Commit: e832a91 / docs: 82895fa
   - `backend/app/schemas/consultations.py`
   - `backend/app/api/routes/consultations.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_consultation_schemas.py`
   - `backend/tests/test_consultation_routes.py`
   - Module 29 tests: 39/39 passed
   - Full backend tests: 741/741 passed

28. Module 30 — Audio upload placeholder service
   - Commit: 1ccc797 / docs: 2b31c13
   - `backend/app/modules/audio/__init__.py`
   - `backend/app/modules/audio/audio_storage.py`
   - `backend/tests/test_audio_storage.py`
   - Module 30 tests: 23/23 passed
   - Full backend tests: 764/764 passed

29. Module 31 — Transcription adapter interface
   - Commit: 9aa2cb7 / docs: 13d2fdf
   - `backend/app/modules/transcription/__init__.py`
   - `backend/app/modules/transcription/transcription_service.py`
   - `backend/tests/test_transcription_service.py`
   - Module 31 tests: 27/27 passed
   - Full backend tests: 791/791 passed

30. Module 32 — Clinical summary draft generator
   - Commit: a1a6498 / docs: c879f4b
   - `backend/app/modules/clinical_summary/__init__.py`
   - `backend/app/modules/clinical_summary/summary_builder.py`
   - `backend/tests/test_clinical_summary_builder.py`
   - Module 32 tests: 41/41 passed
   - Full backend tests: 832/832 passed

31. Module 33 — Doctor review workflow
   - Commit: 6cd62c2 / docs: cc165f0
   - `backend/app/modules/clinical_summary/review_workflow.py`
   - `backend/tests/test_review_workflow.py`
   - Module 33 tests: 33/33 passed
   - Full backend tests: 865/865 passed

32. Module 34 — Patient timeline report service
   - Commit: 827c2da / docs: cf8c097
   - `backend/app/modules/patient_timeline/__init__.py`
   - `backend/app/modules/patient_timeline/timeline_report.py`
   - `backend/tests/test_patient_timeline_report.py`
   - Module 34 tests: 43/43 passed
   - Full backend tests: 908/908 passed

## Architecture checkpoint

- Architecture Checkpoint 02 created: `docs/claude/ARCHITECTURE_CHECKPOINT_02.md`
- Commit: 7e478c5 / follow-up docs: 2855d2f
- Full backend tests: 908/908 passed
- Sprint 2 complete (Modules 24–34)
- Sprint 3 started: Clinical Workflow API Routes (Module 35+)

33. Module 35 — Clinical workflow API routes
   - Commit: 9c36593 / docs: aa05911
   - `backend/app/schemas/clinical_workflows.py`
   - `backend/app/api/routes/clinical_workflows.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_clinical_workflow_schemas.py`
   - `backend/tests/test_clinical_workflow_routes.py`
   - Module 35 tests: 47/47 passed (18 schema + 29 routes)
   - Full backend tests: 955/955 passed

34. Module 36 — Auth and tenant access foundation
   - Commit: 711ddfb / docs: 6ecd5ed
   - `backend/app/core/auth_context.py`
   - `backend/app/api/dependencies/__init__.py`
   - `backend/app/api/dependencies/auth.py`
   - `backend/tests/test_auth_context.py`
   - `backend/tests/test_auth_dependencies.py`
   - Module 36 tests: 34/34 passed (23 context + 11 dependencies)
   - Full backend tests: 989/989 passed

35. Module 37 — Apply tenant guards to clinical PHI routes
   - Commit: 5211f7c
   - `backend/app/api/routes/patients.py` (updated)
   - `backend/app/api/routes/consultations.py` (updated)
   - `backend/app/api/routes/clinical_workflows.py` (updated)
   - `backend/tests/test_patient_routes.py` (updated)
   - `backend/tests/test_consultation_routes.py` (updated)
   - `backend/tests/test_clinical_workflow_routes.py` (updated)
   - Module 37 tests: 17/17 new passed (5 patient + 6 consultation + 6 clinical_workflows)
   - Full backend tests: 1006/1006 passed

36. Module 38 — Apply tenant guards to appointment and notification routes
   - Commit: 251e82d
   - `backend/app/api/routes/appointment_requests.py` (updated)
   - `backend/app/api/routes/notifications.py` (updated)
   - `backend/tests/test_appointment_request_routes.py` (updated)
   - `backend/tests/test_notification_routes.py` (updated)
   - Module 38 tests: 12/12 new passed (6 appointment_requests + 6 notifications)
   - Full backend tests: 1018/1018 passed

37. Module 39 — Machine access foundation
   - Commit: fb9d31d
   - `backend/app/core/machine_auth.py` (new)
   - `backend/app/api/dependencies/machine_auth.py` (new)
   - `backend/tests/test_machine_auth.py` (new)
   - `backend/tests/test_machine_auth_dependencies.py` (new)
   - Module 39 tests: 45/45 passed (30 core + 15 dependencies)
   - Full backend tests: 1063/1063 passed

38. Module 40 — Apply machine guards to integration routes
   - Commit: 1c21ee5
   - `backend/app/api/routes/availability.py` (updated)
   - `backend/app/api/routes/vapi_tools.py` (updated)
   - `backend/app/api/routes/vapi_webhooks.py` (updated)
   - `backend/app/api/routes/calendar_webhooks.py` (updated)
   - `backend/tests/test_availability_routes.py` (updated)
   - `backend/tests/test_vapi_tool_routes.py` (updated)
   - `backend/tests/test_vapi_webhook_route.py` (updated)
   - `backend/tests/test_calendar_webhook_route.py` (updated)
   - Module 40 tests: 20/20 passed (5 availability + 5 vapi_tools + 5 vapi_webhook + 5 calendar_webhook)
   - Full backend tests: 1083/1083 passed

## Architecture checkpoint

- Architecture Checkpoint 03 created: `docs/claude/ARCHITECTURE_CHECKPOINT_03.md`
- Commit: 8169ee4
- Scope: Modules 35–40, Sprint 3 complete
- Focus: access control map, human/machine auth guards, integration readiness, remaining risks before pilot
- Full backend tests: 1083/1083 passed
- Sprint 3 complete (Modules 35–40)
- Sprint 4 started: Database Migration Foundation (Module 41)

39. Module 41 — Database migration foundation
   - Commit: 2daf4fd
   - `backend/alembic.ini` (new)
   - `backend/migrations/env.py` (new)
   - `backend/migrations/script.py.mako` (new)
   - `backend/migrations/versions/0001_initial_schema.py` (new)
   - `backend/tests/test_migration_contract.py` (new)
   - Migration tests: 20/20 passed
   - Full backend tests: 1103/1103 passed

40. Module 42 — Audit logging foundation
   - Commit: f085f83
   - `backend/app/db/repositories/audit_repo.py` (new)
   - `backend/app/modules/audit/__init__.py` (new)
   - `backend/app/modules/audit/audit_logger.py` (new)
   - `backend/tests/test_audit_repo.py` (new)
   - `backend/tests/test_audit_logger.py` (new)
   - Module 42 tests: 42/42 passed (20 repo + 22 logger)
   - Full backend tests: 1145/1145 passed

41. Module 43 — Audit logging integration for PHI mutations
   - Commit: 726710a
   - `backend/app/api/routes/patients.py` (updated)
   - `backend/app/api/routes/consultations.py` (updated)
   - `backend/app/api/routes/clinical_workflows.py` (updated)
   - `backend/app/api/routes/appointment_requests.py` (updated)
   - `backend/app/api/routes/notifications.py` (updated)
   - `backend/tests/test_patient_routes.py` (updated)
   - `backend/tests/test_consultation_routes.py` (updated)
   - `backend/tests/test_clinical_workflow_routes.py` (updated)
   - `backend/tests/test_appointment_request_routes.py` (updated)
   - `backend/tests/test_notification_routes.py` (updated)
   - Module 43 tests: 30/30 new audit tests passed
   - Full backend tests: 1175/1175 passed

42. Module 44 — Audit logging integration for machine routes
   - Commit: 005e43a
   - `backend/app/api/routes/vapi_webhooks.py` (updated)
   - `backend/app/api/routes/calendar_webhooks.py` (updated)
   - `backend/app/api/routes/vapi_tools.py` (updated)
   - `backend/tests/test_vapi_webhook_route.py` (updated)
   - `backend/tests/test_calendar_webhook_route.py` (updated)
   - `backend/tests/test_vapi_tool_routes.py` (updated)
   - Module 44 tests: 18/18 new tests passed
   - Full backend tests: 1193/1193 passed

## Architecture checkpoint

- Architecture Checkpoint 04 created: `docs/claude/ARCHITECTURE_CHECKPOINT_04.md`
- Commit: 9fba526
- Scope: Modules 41–44, Sprint 4 complete
- Focus: migration foundation, audit logging foundation, PHI/machine audit integration, integration readiness, remaining risks before pilot
- Full backend tests: 1193/1193 passed
- Sprint 4 complete (Modules 41–44)
- Sprint 5 started: Local PostgreSQL Docker + Migration Runner Smoke Test (Module 45)

43. Module 45 — Local PostgreSQL Docker and migration smoke test
   - Commit: 5566653
   - `docker-compose.postgres.yml` (new)
   - `backend/.env.example` (new)
   - `backend/scripts/__init__.py` (new)
   - `backend/scripts/run_migrations.py` (new)
   - `backend/scripts/db_smoke_test.py` (new)
   - `backend/tests/test_local_db_setup_contract.py` (new)
   - Module 45 tests: 24/24 passed
   - Full backend tests: 1217/1217 passed
   - Manual local PostgreSQL smoke flow passed: Docker started, migration applied, key tables confirmed

44. Module 46 — Webhook signature verification foundation
   - Commit: 41d0a46
   - Docs commit: c2c2dc8
   - `backend/app/core/webhook_signature.py` (new)
   - `backend/app/api/dependencies/webhook_signature.py` (new)
   - `backend/tests/test_webhook_signature.py` (new)
   - `backend/tests/test_webhook_signature_dependencies.py` (new)
   - Module 46 tests: 33/33 passed (23 core + 10 dependencies)
   - Full backend tests: 1250/1250 passed

45. Module 47 — Apply webhook signature enforcement
   - Commit: c161c16
   - Docs commit: 718046f
   - `backend/app/api/routes/vapi_webhooks.py` (updated)
   - `backend/app/api/routes/calendar_webhooks.py` (updated)
   - `backend/tests/test_vapi_webhook_route.py` (updated)
   - `backend/tests/test_calendar_webhook_route.py` (updated)
   - Module 47 tests: 12 new signature enforcement tests passed
   - Full backend tests: 1256/1256 passed

46. Module 48 — Local integration runbook and signed webhook helper
   - Commit: 60f61fa
   - Docs commit: d6a3e3b
   - `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` (new)
   - `backend/scripts/sign_webhook_payload.py` (new)
   - `backend/tests/test_signed_webhook_helper_contract.py` (new)
   - Module 48 tests: 25/25 passed
   - Full backend tests: 1281/1281 passed
   - Manual signed webhook curl reached backend but returned 503: runtime DB pool startup was missing

47. Module 49 — Local runtime database pool startup
   - Commit: b6cb614
   - `backend/app/main.py` (updated — lifespan handler added)
   - `backend/tests/test_app_lifespan_db_pool.py` (new)
   - Module 49 tests: 9/9 passed
   - Full backend tests: 1290/1290 passed

## Next module
Sprint 5 / Module 50 — TBD.
