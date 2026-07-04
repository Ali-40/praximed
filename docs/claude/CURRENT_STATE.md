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
   - Docs commit: 1fa34d1
   - `backend/app/main.py` (updated — lifespan handler added)
   - `backend/tests/test_app_lifespan_db_pool.py` (new)
   - Module 49 tests: 9/9 passed
   - Full backend tests: 1290/1290 passed
   - Manual signed webhook curl passed signature/auth layer; good signature reached DB logic; bad signature returned 401
   - Current local gap: seed data and valid UUID smoke payloads

48. Module 50 — Local seed data and webhook smoke fixtures
   - Commit: dd8df3b
   - Docs commit: 0f178f9
   - `backend/scripts/seed_local_data.py` (new)
   - `docs/integrations/local_payloads/vapi_call_event.json` (new)
   - `docs/integrations/local_payloads/n8n_calendar_sync.json` (new)
   - `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` (updated)
   - `backend/tests/test_local_seed_contract.py` (new)
   - Module 50 tests: 22/22 passed
   - Full backend tests: 1312/1312 passed
   - Manual local signed Vapi webhook: HTTP 200 OK
   - Manual bad Vapi signature: HTTP 401 Unauthorized
   - Manual local signed n8n webhook: HTTP 200 OK
   - Local integration smoke checkpoint created

49. Module 51 — Local integration smoke result checkpoint
   - Commit: 2872c99
   - Docs commit: ced433c
   - `docs/integrations/LOCAL_SMOKE_RESULTS.md` (new)
   - `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` (updated — Section L added)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 52 placeholder)
   - No production code changes
   - Full backend tests: 1312/1312 passed
   - Local signed Vapi webhook smoke test passed with HTTP 200
   - Bad Vapi signature returned HTTP 401
   - Local signed n8n calendar sync webhook smoke test passed with HTTP 200

## Architecture checkpoint

- Sprint 5 complete (Modules 45–51)
- Sprint 6 started: External Integration Compatibility (Module 52+)

50. Module 52 — External integration compatibility plan
   - Commit: f50c94c
   - Docs commit: 39c472e
   - `docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md` (new)
   - `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` (updated — Section M rewritten)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 53 placeholder)
   - No production code changes
   - Full backend tests: 1312/1312 passed

51. Module 53 — Provider header compatibility config
   - Commit: 3b1937e
   - Docs commit: 1bc2ea9
   - `backend/app/core/webhook_provider_config.py` (new)
   - `backend/app/api/dependencies/webhook_signature.py` (updated)
   - `backend/tests/test_webhook_provider_config.py` (new — 21 tests)
   - `backend/tests/test_webhook_signature_dependencies.py` (updated — 5 new alias tests)
   - `docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md` (updated — Section L added)
   - Module 53 tests: 36/36 passed (21 config + 15 dependency)
   - Full backend tests: 1338/1338 passed
   - Signature dependencies now accept controlled provider-specific header aliases while keeping HMAC verification required

52. Module 54 — Provider machine header compatibility config
   - Commit: 79220ca
   - `backend/app/core/machine_provider_config.py` (new)
   - `backend/app/api/dependencies/machine_auth.py` (updated — alias-aware extraction)
   - `backend/tests/test_machine_provider_config.py` (new — 24 tests)
   - `backend/tests/test_machine_auth_dependencies.py` (updated — 18 new alias tests)
   - `docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md` (updated — Section M added)
   - Module 54 tests: 42 new tests passed (24 config + 18 alias dependency)
   - Full backend tests: 1380/1380 passed
   - Machine auth accepts provider-specific aliases for service_name, clinic_id, scopes
   - Original X-Service-* headers remain fully supported
   - Conflicting duplicate aliases rejected with HTTP 401
   - Required scope and tenant/clinic enforcement unchanged

53. Module 55 — Local tunnel real provider test runbook
   - Commit: 708952a
   - Docs commit: 7afb929
   - `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` (new)
   - `docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md` (updated — Section N added)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 56 placeholder)
   - No production code changes
   - Full backend tests: 1380/1380 passed
   - Real Vapi tunnel test result: HMAC and machine auth passed; backend returned HTTP 400 due to payload shape mismatch (clinic_id absent in real Vapi body)
   - Real Vapi payload shape: {"message": {"type": "assistant-started", ...}} — no clinic_id/call_id/event_type at root

54. Module 56 — Real Vapi payload compatibility adapter
   - Commit: 53b6ddb
   - Docs commit: 57f37f8
   - `backend/app/api/routes/vapi_webhooks.py` (updated — _adapt_vapi_payload, request: Request added)
   - `backend/tests/test_vapi_webhook_route.py` (updated — 6 new adapter tests, 30 total)
   - `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` (updated — Section 10 real result, Section 11 next module)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 57 placeholder)
   - Module 56 tests: 6 new tests passed (30 total in file)
   - Full backend tests: 1386/1386 passed
   - Route now accepts both local payload shape and real Vapi server shape
   - clinic_id resolved from machine auth when absent in body
   - event_type mapped from message.type (assistant-started → call.started, end-of-call-report → call.ended)
   - call_id resolved from message.call.id → message.callId → X-Call-Id header → fallback
   - HMAC and machine auth enforcement unchanged
   - Real Vapi tunnel retest after Module 56: HTTP 200 OK confirmed

55. Module 57 — Real Vapi tunnel smoke evidence
   - Commit: 9733710
   - Docs commit: 1903c54
   - `docs/integrations/REAL_VAPI_TUNNEL_SMOKE_RESULTS.md` (new)
   - `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` (updated — Section 11 Vapi smoke passed, Section 12 next module)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 58 placeholder)
   - No production code changes
   - Full backend tests: 1386/1386 passed
   - Real Vapi → ngrok → FastAPI end-to-end confirmed: HTTP 200 OK
   - HMAC via x-signature / {body} / hex accepted
   - Machine auth via X-Vapi-* aliases accepted
   - Payload adapter resolved clinic_id and event_type from real Vapi body

56. Module 58 — Real n8n tunnel smoke evidence
   - Commit: f70041f
   - Docs commit: a9d0d79
   - `docs/integrations/REAL_N8N_TUNNEL_SMOKE_RESULTS.md` (new)
   - `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` (updated — Section 12 n8n smoke passed, Section 13 next recommendation)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Architecture Checkpoint 05 placeholder)
   - No production code changes
   - Full backend tests: 1386/1386 passed
   - Real n8n → ngrok → FastAPI end-to-end confirmed: success
   - HMAC via X-Signature: sha256=... over raw compact JSON body accepted
   - Machine auth via X-N8N-* aliases accepted
   - Key fix: HMAC must be computed over the exact raw bytes transmitted by n8n

## Architecture checkpoint

- Architecture Checkpoint 05 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_05_EXTERNAL_INTEGRATION_REVIEW.md`
- Commit: 3a5a76d
- Docs commit: 1c71f66
- Full backend tests: 1386/1386 passed
- Sprint 6 complete (Modules 52–58)
- Sprint 7 started: Production Auth and User Session Foundation (Module 59+)

57. Module 59 — Production auth and user session foundation
   - Commit: 97db66d
   - `backend/app/db/schema.sql` (updated — password_hash added to clinic_users)
   - `backend/migrations/versions/0002_add_password_hash_to_clinic_users.py` (new)
   - `backend/app/core/password_hashing.py` (new — bcrypt hash/verify)
   - `backend/app/core/jwt_tokens.py` (new — JWT create/decode, MissingJWTSecretError, ExpiredJWTError)
   - `backend/app/db/repositories/user_repo.py` (new — get_user_by_email, get_user_by_id, create_user)
   - `backend/app/api/dependencies/current_user.py` (new — Bearer JWT → AuthContext, not yet wired to routes)
   - `backend/tests/test_password_hashing.py` (new — 12 tests)
   - `backend/tests/test_jwt_tokens.py` (new — 12 tests)
   - `backend/tests/test_user_repository.py` (new — 14 tests)
   - `backend/tests/test_current_user_dependency.py` (new — 10 tests)
   - Module 59 tests: 51/51 passed (12 hashing + 12 JWT + 14 repo + 10 dep + 3 migration contract)
   - Full backend tests: 1437/1437 passed
   - No plaintext passwords stored or tested
   - No real secrets committed
   - No real DB in tests
   - Existing PHI route behavior unchanged — current_user dep not yet wired

58. Module 60 — Login endpoint and auth wiring plan
   - Commit: a7866ae
   - `backend/app/schemas/auth.py` (new — LoginRequest, LoginUserInfo, LoginResponse)
   - `backend/app/api/routes/auth.py` (new — POST /auth/login)
   - `backend/app/api/router.py` (updated — auth router registered)
   - `docs/security/AUTH_WIRING_PLAN.md` (new — future PHI route wiring order)
   - `backend/tests/test_auth_login_route.py` (new — 10 tests)
   - Module 60 tests: 10/10 passed
   - Full backend tests: 1447/1447 passed
   - POST /auth/login returns 200 + JWT on correct credentials
   - Wrong password or unknown email → 401 "Invalid credentials" (no user enumeration)
   - Inactive account → 401 "Account is not active"
   - Missing password_hash → 401
   - Missing JWT_SECRET_KEY → 503
   - password_hash never returned or logged
   - Email normalized to lowercase before lookup
   - Existing PHI routes unchanged — current_user dep not yet wired

59. Module 61 — Wire JWT auth to patient routes
   - Commit: f6afa45
   - `backend/app/api/routes/patients.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context))
   - `backend/tests/test_patient_routes.py` (updated — fixtures override get_current_user; 7 new JWT auth tests)
   - `backend/tests/test_clinical_workflow_routes.py` (updated — cross-route smoke test assertion updated)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /patients marked wired ✓)
   - Module 61 tests: 36/36 patient route tests passed (7 new JWT enforcement tests)
   - Full backend tests: 1451/1451 passed
   - Patient routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Tenant/role checks (require_staff_clinic_access) unchanged — same clinic only, viewer denied
   - Other PHI routes (consultations, clinical-workflows, appointments, notifications) unchanged

60. Module 62 — Wire JWT auth to consultation routes
   - Commit: 0773bfa
   - `backend/app/api/routes/consultations.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context))
   - `backend/tests/test_consultation_routes.py` (updated — fixtures override get_current_user; 9 new JWT auth tests)
   - `backend/tests/test_clinical_workflow_routes.py` (updated — test_consultations_route_still_works assertion updated to != 404)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /consultations marked wired ✓)
   - Module 62 tests: 38/38 consultation route tests passed (9 new JWT enforcement tests)
   - Full backend tests: 1454/1454 passed
   - Consultation routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Clinical role guard (require_clinical_clinic_access) unchanged — staff and viewer denied, doctor/owner/admin allowed
   - Other PHI routes (clinical-workflows, appointments, notifications) unchanged

61. Module 63 — Wire JWT auth to clinical workflow routes
   - Commit: 79e75b6
   - `backend/app/api/routes/clinical_workflows.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context) across all 7 routes)
   - `backend/tests/test_clinical_workflow_routes.py` (updated — fixtures override get_current_user; 9 new JWT auth tests replacing 6 old header-based tests)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /clinical-workflows marked wired ✓)
   - Module 63 tests: 46/46 clinical workflow tests passed (9 new JWT enforcement tests)
   - Full backend tests: 1457/1457 passed
   - Clinical workflow routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Clinical role guard (require_clinical_clinic_access) unchanged — staff and viewer denied, doctor/owner/admin allowed
   - No cross-route test files required updating (consultation/clinical-workflow smoke tests already used != 404 assertions)
   - Other PHI routes (appointments, notifications) unchanged

62. Module 64 — Wire JWT auth to appointment request routes
   - Commit: 3bacac0
   - Docs commit: a04a452
   - `backend/app/api/routes/appointment_requests.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context) across all 7 routes)
   - `backend/tests/test_appointment_request_routes.py` (updated — fixtures override get_current_user; 8 new JWT auth tests replacing 6 old header-based tests)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /appointment-requests marked wired ✓)
   - Module 64 tests: 29/29 appointment request route tests passed (8 new JWT enforcement tests)
   - Full backend tests: 1459/1459 passed
   - Appointment request routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Staff-level role guard (require_staff_clinic_access) unchanged — viewer denied, staff/doctor/owner/admin allowed
   - No cross-route test files required updating (all appointment smoke tests already used != 404 assertions)

63. Module 65 — Wire JWT auth to notification routes
   - Commit: 4b36a66
   - Docs commit: 5faa0ed
   - `backend/app/api/routes/notifications.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context) across all 5 routes)
   - `backend/tests/test_notification_routes.py` (updated — fixtures override get_current_user; 8 new JWT auth tests replacing 6 old header-based tests)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /notifications marked wired ✓; Sprint 7 PHI JWT wiring complete)
   - Module 65 tests: 30/30 notification route tests passed (8 new JWT enforcement tests)
   - Full backend tests: 1461/1461 passed
   - Notification routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Staff-level role guard (require_staff_clinic_access) unchanged — viewer denied, staff/doctor/owner/admin allowed
   - All PHI route JWT wiring complete: /patients, /consultations, /clinical-workflows, /appointment-requests, /notifications
   - Machine routes (Vapi, n8n, availability, webhooks) unchanged

## Architecture checkpoint

- Architecture Checkpoint 06 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_06_HUMAN_AUTH_WIRING_REVIEW.md`
- Commit: 6b64de9
- Full backend tests: 1461/1461 passed
- Sprint 7 complete (Modules 59–65)
- Sprint 8 started: Frontend Dashboard Foundation (Module 66+)

64. Module 66 — Frontend dashboard foundation
   - Commit: 201d504
   - `frontend/package.json` (new — Next.js 14, React 18, TypeScript 5)
   - `frontend/tsconfig.json` (new)
   - `frontend/next.config.js` (new)
   - `frontend/app/layout.tsx` (new — root layout with PraxisMed metadata)
   - `frontend/app/page.tsx` (new — redirects to /login)
   - `frontend/app/globals.css` (new — minimal design tokens and reset)
   - `frontend/app/login/page.tsx` (new — email/password form UI scaffold)
   - `frontend/app/dashboard/page.tsx` (new — placeholder cards for Patients, Appointments, Notifications, Consultations)
   - `frontend/lib/api.ts` (new — apiFetch helper with NEXT_PUBLIC_API_BASE_URL and localhost fallback)
   - `frontend/lib/auth.ts` (new — loginUser, storeToken, getToken, clearToken, isAuthenticated; sessionStorage local-dev only)
   - `frontend/README.md` (new — local startup instructions)
   - `backend/tests/test_frontend_dashboard_foundation_contract.py` (new — 10 static contract tests)
   - Module 66 contract tests: 10/10 passed
   - Full backend tests: 1471/1471 passed
   - No backend routes modified
   - No real patient data; no hardcoded secrets
   - Login flow wired to backend in Module 67

65. Module 67 — Frontend login flow integration
   - Commit: eafe918
   - `frontend/app/login/page.tsx` (updated — 'use client'; onSubmit wired to loginUser; storeToken on success; router.push('/dashboard'); generic error display)
   - `frontend/app/dashboard/page.tsx` (updated — 'use client'; useEffect auth guard redirects to /login if no token; Logout button calls clearToken + router.push('/login'))
   - `frontend/README.md` (updated — login flow section: Clinic ID + email + password, local test instructions)
   - `backend/tests/test_frontend_login_flow_contract.py` (new — 10 static contract tests)
   - Module 67 contract tests: 10/10 passed
   - Full backend tests: 1481/1481 passed
   - No backend routes modified
   - Generic error on login failure — does not reveal email vs password mismatch
   - Section data fetching wired in Module 68

66. Module 68 — Frontend appointment requests dashboard integration
   - Commit: e106dcf
   - `frontend/lib/api.ts` (updated — AppointmentRequest type + fetchAppointmentRequests helper with Bearer token)
   - `frontend/lib/auth.ts` (updated — getClinicId() decodes clinic_id from stored JWT payload via atob)
   - `frontend/app/dashboard/page.tsx` (updated — Appointments section wired to fetchAppointmentRequests; loading/error/empty/list states; Patients/Notifications/Consultations remain as placeholders)
   - `frontend/README.md` (updated — dashboard data section: appointment fetch, Bearer token, states)
   - `backend/tests/test_frontend_appointment_requests_contract.py` (new — 10 static contract tests)
   - Module 68 contract tests: 10/10 passed
   - Full backend tests: 1491/1491 passed
   - No backend routes modified
   - clinic_id decoded from JWT payload client-side (no extra library)
   - No hardcoded tokens or real patient data

67. Module 69 — Frontend patient list integration
   - Commit: 6890f8e
   - `frontend/lib/api.ts` (updated — Patient type + fetchPatients helper)
   - `frontend/app/dashboard/page.tsx` (updated — Patients section wired to fetchPatients; loading/error/empty/list states; Appointments section unchanged; Notifications/Consultations remain as placeholders)
   - `frontend/README.md` (updated — patients section: fetchPatients, Bearer token, states)
   - `backend/tests/test_frontend_patient_list_contract.py` (new — 10 static contract tests)
   - Module 69 contract tests: 10/10 passed
   - Full backend tests: 1501/1501 passed
   - No backend routes modified
   - Patient row displays full name (first + last) and status badge (green for active)
   - No hardcoded tokens or real patient data

68. Module 70 — Frontend notifications integration
   - Commit: 07b7ad2
   - `frontend/lib/api.ts` (updated — Notification type + fetchNotifications helper)
   - `frontend/app/dashboard/page.tsx` (updated — Notifications section wired to fetchNotifications; loading/error/empty/list states; Appointments and Patients unchanged; Consultations remains as placeholder)
   - `frontend/README.md` (updated — notifications section: fetchNotifications, Bearer token, states)
   - `backend/tests/test_frontend_notifications_contract.py` (new — 10 static contract tests)
   - Module 70 contract tests: 10/10 passed
   - Full backend tests: 1511/1511 passed
   - No backend routes modified
   - Notification row displays title, priority badge (red for urgent/emergency), and notification_type
   - No hardcoded tokens or real patient data

69. Module 71 — Frontend consultation list integration
   - Commit: 6a4cff5
   - `frontend/lib/api.ts` (updated — ConsultationSession type + fetchConsultations helper)
   - `frontend/app/dashboard/page.tsx` (updated — Consultations section wired to fetchConsultations; loading/error/empty/list states; placeholder grid removed; all four sections live)
   - `frontend/README.md` (updated — consultations section: fetchConsultations, Bearer token, states)
   - `backend/tests/test_frontend_consultations_contract.py` (new — 10 static contract tests)
   - Module 71 contract tests: 10/10 passed
   - Full backend tests: 1521/1521 passed
   - No backend routes modified
   - Consultation row displays title, approval status badge (green for approved), and source
   - Consultations placeholder card removed; all four dashboard sections now live
   - No hardcoded tokens or real patient data

## Architecture checkpoint

- Architecture Checkpoint 07 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_07_FRONTEND_DASHBOARD_REVIEW.md`
- Commit: b36a4a9
- Full backend tests: 1521/1521 passed
- Sprint 8 complete (Modules 66–71)
- Sprint 9 started: Frontend Local Runtime Smoke (Module 72+)

70. Module 72 — Frontend local runtime smoke and seed login
   - Commit: 82d7856
   - `backend/scripts/seed_local_data.py` (updated — LOCAL_LOGIN_EMAIL + LOCAL_LOGIN_PASSWORD_LABEL constants; hash_password imported; password_hash included in clinic_users INSERT; ON CONFLICT updates email + password_hash; main() prints email/password label but NOT hash)
   - `backend/tests/test_local_seed_contract.py` (updated — 6 new tests 23–28: password_hash reference, hash_password usage, local login email, email constant value, password label, no print of raw hash)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (new — 9-step local browser smoke runbook: PostgreSQL, migrations, seed, backend, frontend, login, dashboard verification, logout, known limitations)
   - `frontend/README.md` (updated — local browser smoke quick-start and link to runbook)
   - Module 72 contract tests: 28/28 passed (6 new + 22 existing)
   - Full backend tests: 1527/1527 passed
   - No backend routes modified
   - Local login credentials: doctor.local@praximed.test / local-dev-password (fake/local only)
   - password_hash never printed; hash_password called at runtime inside async function

71. Module 73 — Fix frontend runtime smoke blockers
   - Commit: 746d77e
   - Runtime blockers found during manual smoke (Module 72):
     1. Alembic revision ID `0002_add_password_hash_to_clinic_users` (42 chars) exceeded `alembic_version VARCHAR(32)` — migration failed
     2. `seed_local_data.py` raised `ModuleNotFoundError: No module named 'backend'` when run directly — missing sys.path safety
     3. Backend failed to start with `[Errno 48] Address already in use` — runbook needed port-conflict guidance
   - `backend/migrations/versions/0002_add_password_hash_to_clinic_users.py` (updated — revision shortened to `0002_password_hash`, 16 chars)
   - `backend/scripts/seed_local_data.py` (updated — `_PROJECT_ROOT` sys.path insertion at top for direct execution; hash_password import preserved)
   - `backend/tests/test_migration_contract.py` (updated — 3 new tests 21–23: all revision IDs ≤32 chars, 0002 file exists, 0002 revision value correct)
   - `backend/tests/test_local_seed_contract.py` (updated — 1 new test 29: sys.path project-root safety present)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — blocker table added, port-conflict stop instructions, no-ngrok note, JWT_SECRET_KEY required note)
   - Module 73 new tests: 4 new tests (3 migration + 1 seed); all 52 seed+migration tests pass
   - Full backend tests: 1531/1531 passed
   - No backend routes modified; no frontend code changed

72. Module 74 — Fix frontend browser login runtime issue (CORS)
   - Commit: 04cba09
   - CORS blocker found during manual smoke (Module 73):
     - curl `POST /auth/login` returned HTTP 200 (backend auth works)
     - Browser login showed "Sign-in failed" — root cause: `OPTIONS /auth/login → 405 Method Not Allowed`
     - FastAPI had no CORS middleware; browser preflight was rejected before reaching the auth route
   - `backend/app/main.py` (updated — `CORSMiddleware` added; defaults to `http://localhost:3000` and `http://127.0.0.1:3000`; `FRONTEND_CORS_ORIGINS` env override; explicit origins only, no wildcard)
   - `backend/tests/test_cors_contract.py` (new — 8 CORS contract tests)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — CORS blocker row added; backend CORS note in Step 4)
   - `frontend/README.md` (updated — backend CORS local-dev note)
   - Module 74 CORS tests: 8/8 passed
   - Full backend tests: 1539/1539 passed
   - No auth routes or frontend code modified

73. Module 75 — Frontend browser smoke evidence
   - Commit: c5f9d4a
   - `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` (new — full smoke evidence: environment, steps, curl/browser/CORS/logout evidence, what this proves, what it does not prove, future language note, recommended Module 76)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — smoke PASS note added at top, link to results doc)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 76 spec: dashboard demo data polish)
   - No production code changes
   - Full backend tests: 1539/1539 passed
   - Browser smoke verdict: PASS (2026-07-02)
   - login → dashboard → logout flow confirmed in real browser
   - CORS preflight (OPTIONS /auth/login) → HTTP 200 confirmed
   - All four dashboard sections rendered (Appointments empty, Patients seeded, Notifications empty, Consultations seeded)
   - Logout cleared sessionStorage token; auth guard redirected back to /login

74. Module 76 — Dashboard empty-state and local demo data polish
   - Commit: 4f263b5
   - `backend/scripts/seed_local_data.py` (updated — LOCAL_APPOINTMENT_REQUEST_ID + LOCAL_NOTIFICATION_ID constants; INSERT into appointment_requests and clinic_notifications; ON CONFLICT upserts; main() prints both new IDs)
   - `backend/tests/test_local_seed_contract.py` (updated — 8 new tests 30–37: appointment request ID, notification ID, UUID validity, table INSERT references, constant usage count, ON CONFLICT count)
   - `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` (updated — Section 9 rewritten to Module 76 demo data note)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — Module 76 update line at top; demo data note; Step 3 expected output updated; Step 8 all four sections show list state)
   - `frontend/README.md` (updated — seed row table for all four dashboard sections; status updated to Module 76)
   - Module 76 new tests: 8 new (37 total in file); all 37 passed
   - Full backend tests: 1547/1547 passed
   - No backend routes modified; no frontend code changed
   - Seed script creates: clinic, doctor user, patient, consultation session, appointment request (55555555), notification (66666666)
   - All four dashboard sections now show list state after re-seeding

75. Module 77 — Rerun frontend demo data browser smoke evidence
   - Commit: 1253b84
   - `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (new — full demo data smoke evidence: environment, steps, seed output, all four sections list state, what this proves, known patient name display issue, what this does not prove, Architecture Checkpoint 08 recommended)
   - `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` (updated — Section 10 added: Module 77 PASS confirmation with section-by-section table, known issue note)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — Module 77 update line; demo data smoke PASS note; link to new results doc; updated demo data note with name display caveat)
   - `docs/claude/NEXT_MODULE.md` (updated — Architecture Checkpoint 08 spec)
   - No production code changes
   - Full backend tests: 1547/1547 passed
   - Demo data browser smoke verdict: PASS (2026-07-02)
   - All four dashboard sections rendered list state after re-seeding
   - Known minor issue: patient row shows `"—"` for name (full_name vs first_name/last_name field mismatch — cosmetic, not blocking)

## Architecture checkpoint

- Architecture Checkpoint 08 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_08_LOCAL_DEMO_READINESS_REVIEW.md`
- Commit: cdc2ee1
- Full backend tests: 1547/1547 passed (re-confirmed at start of Module 78)
- Sprint 9 complete (Modules 72–77)
- Local full-stack demo confirmed viable: login → all four dashboard sections list state → logout
- Known issue noted: patient row name displayed as `"—"` — resolved in Module 78
- Sprint 10 started: Dashboard Demo Polish (Module 78+)

76. Module 78 — Dashboard demo polish and patient display fix
   - Commit: bc3e9e2
   - `frontend/lib/api.ts` (updated — `full_name: string | null` added to `Patient` interface as primary field; `first_name` and `last_name` kept for defensive compatibility)
   - `frontend/app/dashboard/page.tsx` (updated — patient name display expression changed from `|| '—'` to `patient.full_name || join(first+last) || 'Unnamed patient'`)
   - `backend/tests/test_frontend_patient_list_contract.py` (updated — 3 new tests 11–13: full_name in Patient interface, patient.full_name in display, 'Unnamed patient' fallback not '—')
   - `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (updated — §6 known issue marked resolved in Module 78)
   - `docs/architecture/ARCHITECTURE_CHECKPOINT_08_LOCAL_DEMO_READINESS_REVIEW.md` (updated — §4.1 patient name issue marked fixed in Module 78)
   - Module 78 new tests: 3 new (13 total in patient list contract file); all 13 passed
   - Full backend tests: 1550/1550 passed
   - No backend routes or schema modified
   - Patient row now displays "Local Test Patient" after re-seeding (not `"—"`)
   - Fallback for missing name data is `'Unnamed patient'` (not `'—'`)

77. Module 79 — Dashboard visual polish pass
   - Commit: 32e9781
   - `frontend/app/dashboard/page.tsx` (updated — "Clinic Dashboard" subtitle in header; "Clinic Overview" page heading; per-section row count pills; shared BADGE_STYLES helper + badgeStyle() function; cardStyle/rowStyle/badgePillStyle constants; local-demo footer label; all four data fetch calls unchanged)
   - `frontend/app/globals.css` (updated — badge colour token variables: --badge-blue-bg/text, --badge-green-bg/text, --badge-red-bg/text, --badge-neutral-bg/text)
   - `backend/tests/test_frontend_dashboard_visual_polish_contract.py` (new — 10 static contract tests: PraxisMed brand, logout button, all four sections, clinical heading, all loading/error/empty states, badge styling, no hardcoded credentials/data)
   - `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (updated — Module 79 note added)
   - Module 79 new tests: 10 new; all 10 passed
   - Full backend tests: 1560/1560 passed
   - No backend routes, API helpers, or auth modified
   - No data fetching behavior changed
   - Dashboard improvements: clinic context, count pills, consistent badge colours, demo label

78. Module 80 — Local demo retest after visual polish
   - Commit: (docs only — no code commit; see sprint commit below)
   - `docs/runtime/FRONTEND_POLISHED_DEMO_BROWSER_SMOKE_RESULTS.md` (new — full polished demo smoke evidence: header, count pills, patient name fix confirmed, badge colours, footer label, what this proves, what remains, Architecture Checkpoint 09 recommended)
   - `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (updated — Module 80 PASS note added, links to polished smoke results doc)
   - No production code changes
   - Full backend tests: 1560/1560 passed
   - Polished browser smoke verdict: PASS (2026-07-02)
   - All four sections show count pills (1) and correct row content
   - Patient row shows "Local Test Patient" — Module 78 fix confirmed
   - "Clinic Dashboard" subtitle and "Clinic Overview" heading confirmed
   - Local-demo footer label confirmed visible

## Architecture checkpoint

- Architecture Checkpoint 09 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_09_POLISHED_LOCAL_DEMO_REVIEW.md`
- Full backend tests: 1560/1560 passed
- Sprint 10 complete (Modules 78–80): patient display fix, visual polish, polished smoke
- Local demo confirmed presentable: "Clinic Overview" dashboard, count pills, correct patient names, badge colours, local-demo footer
- No security regressions in Sprint 10
- Recommended: Sprint 11 / Module 81 — Appointment Request Workflow UI Foundation
- Reason: appointment requests are the core Vapi output; clinic staff need Confirm/Reject actions to complete the loop
- Sprint 11 started: Appointment Request Workflow UI (Module 81+)

79. Module 81 — Appointment request workflow UI foundation
   - Commit: acda04c
   - `frontend/lib/api.ts` (updated — `confirmAppointmentRequest(requestId, clinicId, token)` helper: PATCH /appointment-requests/{id}/status?clinic_id=..., body {"status":"confirmed","action_required":false}, throws on non-2xx)
   - `frontend/app/dashboard/page.tsx` (updated — `confirmAppointmentRequest` imported; `confirmingIds: Set<string>` and `apptActionError` state added; `handleConfirm()` async handler; Confirm button on rows with status === 'new'; button disabled + "Confirming…" while in-flight; generic error on failure; refetches appointments on success)
   - `backend/tests/test_frontend_appointment_workflow_contract.py` (new — 10 static contract tests: helper defined, PATCH method, correct endpoint, Bearer token via apiFetch, dashboard imports helper, button gated on status==='new', disabled state, action error state, refetch on success, no hardcoded credentials)
   - `docs/runtime/FRONTEND_POLISHED_DEMO_BROWSER_SMOKE_RESULTS.md` (updated — Module 81 note added)
   - `frontend/README.md` (updated — Confirm action section)
   - Module 81 new tests: 10 new (1570 total); all 10 passed
   - Full backend tests: 1570/1570 passed
   - No backend routes or schema modified
   - Confirm button only shown on status === 'new' rows; disappears after successful confirmation
   - Action error is generic — does not expose backend error detail

80. Module 82 — Appointment workflow browser smoke evidence and integration loop prep
   - Commit: (see below)
   - `docs/runtime/APPOINTMENT_WORKFLOW_BROWSER_SMOKE_RESULTS.md` (new — full smoke evidence: Confirm button visible on new row, in-flight disabled state observed, status badge updated to confirmed, button disappeared, all other sections stable, verdict PASS)
   - `docs/runtime/FRONTEND_POLISHED_DEMO_BROWSER_SMOKE_RESULTS.md` (updated — Module 82 PASS note added)
   - `docs/architecture/ARCHITECTURE_CHECKPOINT_09_POLISHED_LOCAL_DEMO_REVIEW.md` (updated — §3b Sprint 11 follow-up added; §4.1 updated to reflect Confirm action delivered, remaining actions not yet built)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (new — integration prep: target flow, proven pieces, unknowns, safety constraints, recommended Module 83)
   - No production code changes
   - Full backend tests: 1570/1570 passed
   - Browser smoke verdict: PASS (2026-07-02)
   - Appointment Confirm workflow proven end-to-end: login → Confirm → status "confirmed" → button gone → dashboard stable
   - Next integration target: Vapi intake → appointment request → dashboard confirm loop

81. Module 83 — Vapi intake to appointment dashboard smoke harness
   - Commit: (see below)
   - **Inspection findings**: target endpoint is `POST /vapi/tools/capture-appointment-request` (machine auth, no HMAC); bug found: `config_loader.get()` / `config.clinic_id` should be `config_loader.load()` / `config.tenant_id`; `main.py` does not wire `app.state.config_loader` (pending Module 84)
   - `backend/app/modules/vapi/vapi_appointment_capture.py` (bug fix — `config_loader.get` → `config_loader.load`; `config.clinic_id` → `config.tenant_id`)
   - `backend/tests/test_vapi_appointment_capture.py` (updated — `loader.get` → `loader.load`; `cfg.clinic_id` → `cfg.tenant_id` in `_make_config`; all 23 tests still pass)
   - `docs/integrations/local_payloads/vapi_appointment_intake.json` (new — fake Vapi capture payload: clinic_ref, call_id, patient_name, reason, urgency_level)
   - `backend/scripts/smoke_vapi_appointment_intake.py` (new — sends POST with X-Vapi-* machine auth, prints result, handles 503 with config_loader guidance, exits non-zero on failure)
   - `backend/tests/test_vapi_appointment_intake_harness_contract.py` (new — 10 static contract tests: payload valid, local clinic UUID, required fields, no real data, script exists, API_BASE_URL fallback, machine auth headers, no secret printing, non-zero exit, prep doc references harness)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — target flow corrected; Unknowns table updated; Module 83 harness section with inspection findings, harness components, manual flow commands, Module 84 next steps)
   - `docs/runtime/APPOINTMENT_WORKFLOW_BROWSER_SMOKE_RESULTS.md` (updated — Module 83 note added)
   - Module 83 new tests: 10 harness contract tests; all 10 passed
   - Module 82 full test re-confirmation (timed out previously): 1570/1570 passed
   - Full backend tests: 1580/1580 passed
   - No frontend code changed
   - No backend routes, auth, schema, or seed data modified
   - Bug fix is covered by existing 23 capture tests (all still pass)

## Architecture checkpoint

- Architecture Checkpoint 09 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_09_POLISHED_LOCAL_DEMO_REVIEW.md`
- Updated in Module 82: §3b follow-up added (Modules 81–82 outcomes); §4.1 Confirm action marked delivered
- Sprint 11 in progress (Modules 81–84 complete)

82. Module 84 — Vapi intake harness runtime wiring and smoke evidence
   - Commit: 0959ccc
   - `backend/app/main.py` (updated — `ClinicConfigLoader` imported; `app.state.config_loader = ClinicConfigLoader(pool=app.state.db_pool)` in lifespan startup; `app.state.config_loader = None` in lifespan shutdown)
   - `backend/tests/test_app_lifespan_config_loader.py` (new — 9 lifespan config_loader tests)
   - Module 84 new tests: 9/9 passed
   - Full backend tests: 1589/1589 passed
   - Smoke result: HTTP 503 → resolved; new HTTP 500 — seed UUID `11111111-1111-1111-1111-111111111111` failed `_assert_valid_uuid()` variant byte check `[89ab]`

83. Module 85 — Config loader UUID compatibility and Vapi intake smoke completion
   - Commit: fd6ac74
   - `backend/app/core/config_loader.py` (updated — replaced `_UUID_RE` regex with `uuid.UUID()` parser; added DB-error fallback in `_load_db_config`; updated docstrings)
   - `backend/tests/test_config_loader.py` (updated — 5 new tests: accepts deterministic local UUID, accepts RFC 4122 UUID unchanged, rejects brace-wrapped UUID, rejects unhyphenated UUID, DB error falls back to disk)
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_SMOKE_RESULTS.md` (updated — verdict PASS; smoke evidence recorded)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — UUID blocker RESOLVED; smoke command and result recorded)
   - Module 85 new tests: 5/5 passed (28 total in config_loader test file)
   - Full backend tests: 1594/1594 passed
   - Live smoke: HTTP 200 — appointment ID `509211a7-784e-4e45-90f1-d9af6f8d7981`, `status: new`, `source: vapi`, `action_required: true`

84. Module 86 — Vapi intake to dashboard browser smoke evidence
   - Commit: 4c31a9f
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_BROWSER_SMOKE_RESULTS.md` (new — full browser smoke evidence: harness output, row verification, Confirm action, verdict PASS)
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_SMOKE_RESULTS.md` (updated — Module 86 browser confirm note added)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — all local unknowns RESOLVED; next unknown is real Vapi payload from live assistant; Module 87 recommended)
   - No production code changes
   - Full backend tests: 1594/1594 passed
   - Browser smoke verdict: PASS (2026-07-02)
   - Vapi-created row appeared in dashboard without seed script
   - Staff Confirm: status "new" → "confirmed"; button disappeared

85. Module 87 — Real Vapi appointment tool payload smoke prep
   - Commit: (see git log)
   - `docs/integrations/local_payloads/vapi_real_tool_payload_sample.json` (new — sanitized fake sample of real Vapi tool-call body shape with nested message.toolCallList)
   - `backend/scripts/inspect_vapi_tool_payload.py` (new — structural inspector: redacts patient values, detects flat vs nested shape, assesses compatibility with VapiAppointmentCaptureRequest)
   - `backend/tests/test_vapi_real_tool_payload_prep_contract.py` (new — 17 static contract tests for sample, inspector, prep docs)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — shape gap analysis; real Vapi payload capture plan; Module 88 adapter recommended)
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_BROWSER_SMOKE_RESULTS.md` (updated — Module 87 prep note added)
   - No production code changes
   - Full backend tests: 1611/1611 passed
   - Shape gap identified: real Vapi tool call nests arguments in `message.toolCallList[0].function.arguments`; current capture endpoint expects flat root-level fields; adapter needed (Module 88)
   - Inspector correctly redacts patient values; verdicts NEEDS ADAPTER (nested) and COMPATIBLE (flat)

86. Module 88 — Real Vapi tool call adapter
   - Commit: 479d509
   - `backend/app/modules/vapi/vapi_appointment_capture.py` (updated — `adapt_vapi_tool_call_body` function added; `import json` added)
   - `backend/app/api/routes/vapi_tools.py` (updated — route changed from `body: VapiAppointmentCaptureRequest` to `request: Request`; adapter wired before Pydantic validation; `Request`, `PydanticValidationError`, `adapt_vapi_tool_call_body` imported)
   - `backend/tests/test_vapi_appointment_capture.py` (updated — 9 new adapter tests 23–31; `adapt_vapi_tool_call_body` imported)
   - `backend/tests/test_vapi_real_tool_payload_prep_contract.py` (updated — 5 new contract tests 18–22 for adapter importability and sample payload mapping)
   - `docs/runtime/VAPI_REAL_TOOL_PAYLOAD_ADAPTER_RESULTS.md` (new — adapter design, security boundaries, test results, smoke status)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — shape gap marked RESOLVED; adapter complete; Module 89 recommended)
   - Module 88 new tests: 14/14 passed (9 unit + 5 contract)
   - Full backend tests: 1625/1625 passed
   - Flat (local harness) shape passes through adapter unchanged — existing smoke and tests unaffected
   - Nested (real Vapi) shape normalized: clinic_ref from machine auth, call_id from message.call.id, patient fields from function.arguments
   - Security boundary enforced: patient-supplied clinic_ref in arguments silently ignored; machine_clinic_id always used

87. Module 89 — Vapi/ngrok appointment intake dashboard evidence
   - Commit: 514206e
   - `docs/runtime/VAPI_REAL_TOOL_CALL_LIVE_SMOKE_RESULTS.md` (new — full evidence: ngrok intake, dashboard rows, staff Confirm, accuracy statement, what's proven vs pending)
   - `docs/runtime/VAPI_REAL_TOOL_PAYLOAD_ADAPTER_RESULTS.md` (updated — Module 89 ngrok/dashboard evidence note)
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_BROWSER_SMOKE_RESULTS.md` (updated — Module 89 dashboard confirmation note)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — unknowns table updated; scope `vapi:tool` confirmed; frontend opportunity note added)
   - `docs/integrations/local_payloads/vapi_real_tool_payload_captured.json` (new — sanitized captured payload from ngrok smoke)
   - No production code changes
   - Full backend tests: 1625/1625 passed (unchanged)
   - Evidence: nested Vapi-shape through ngrok → HTTP 200; 4 appointment rows in dashboard; staff Confirm succeeded; status new → confirmed; button disappeared; other sections stable
   - Machine auth scope confirmed: `X-Vapi-Scopes: vapi:tool` (singular)
   - Direct real Vapi assistant call logs: PENDING — not captured in this module

88. Module 90 — Direct real Vapi assistant tool-call log capture
   - Commit: 5155d65
   - `docs/runtime/VAPI_DIRECT_ASSISTANT_TOOL_CALL_LOG_RESULTS.md` (new — full evidence: real Vapi test assistant tool call, ngrok POST, backend row creation, dashboard Confirm, verdict PASS)
   - `docs/runtime/VAPI_REAL_TOOL_CALL_LIVE_SMOKE_RESULTS.md` (updated — direct assistant log evidence upgraded from PENDING to PASS)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — direct Vapi assistant logs marked RESOLVED; integration loop status section added; next focus options listed)
   - `docs/architecture/ARCHITECTURE_CHECKPOINT_10_VAPI_APPOINTMENT_INTAKE_LOOP_REVIEW.md` (updated — status updated; post-checkpoint Module 90 note; pending claims marked PASS)
   - No production code changes
   - Full backend tests: 1625/1625 passed (unchanged)
   - Evidence: real Vapi test assistant fired `capture_appointment_request`; Vapi tool logs success; ngrok POST confirmed; backend created row; dashboard row confirmed by staff; no real data; no auto-confirmation

89. Module 91 — Production Deployment Readiness Inventory
   - Commit: 2f373b5
   - `docs/deployment/PRODUCTION_READINESS_INVENTORY.md` (new — 12-section inventory: purpose, required env vars, infrastructure components, DB strategy, secrets handling, CORS/domain strategy, auth hardening gaps, Vapi production config, n8n production config, health and readiness, production blockers, not in scope)
   - `backend/.env.example` (updated — added JWT_SECRET_KEY, VAPI_WEBHOOK_SECRET, N8N_WEBHOOK_SECRET, INTERNAL_WEBHOOK_SECRET, FRONTEND_CORS_ORIGINS with placeholder values)
   - `backend/tests/test_production_readiness_inventory_contract.py` (new — 29 static contract tests: inventory exists, .env.example completeness, no real secrets, all required env vars covered, critical components mentioned)
   - No production code changes
   - Full backend tests: 1654/1654 passed
   - Env var audit: 7 backend vars + 1 frontend var documented; 5 were missing from .env.example and added
   - Production blockers: 13 explicit blockers documented before first real deployment

90. Module 92 — Environment and Secrets Contract
   - Commit: 6679453
   - `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` (new — 14-section contract: purpose, environment tiers, backend env var contract table, frontend env var contract, secret generation rules, rotation policy, storage rules, env file rules, CORS/domain contract, Vapi/n8n production contract, database contract, logging/secrets safety, pre-deployment checklist, non-goals)
   - `frontend/.env.example` (new — documents NEXT_PUBLIC_API_BASE_URL with localhost placeholder; no backend secrets)
   - `backend/tests/test_environment_and_secrets_contract.py` (new — 43 static contract tests: contract doc coverage, backend/frontend .env.example completeness, no real secrets, security rules, Vapi/n8n requirements)
   - No production code changes; no runtime behavior changes
   - Full backend tests: 1697/1697 passed
   - Four deployment tiers documented: local, test/CI, staging, production
   - Secret classification: DATABASE_URL, JWT_SECRET_KEY, all webhook secrets, POSTGRES_PASSWORD classified as secrets
   - Rotation policy: all 5 secrets with when-to-rotate, impact, and coordination notes
   - Logging safety: PHI and secret values that must never appear in logs enumerated

91. Module 93 — Production CORS/Auth/Domain Plan
   - Commit: 9d087f5
   - `docs/deployment/PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md` (new — 13-section plan: purpose, current local state, production domain topology, CORS policy per tier, sessionStorage JWT risk assessment, httpOnly Secure SameSite cookie migration path with options A/B/C, domain/auth interaction, Vapi/n8n server-to-server domain plan, security headers plan, env var mapping per tier, implementation sequence, risks and decisions table, go/no-go verdict)
   - `backend/tests/test_production_cors_auth_domain_plan_contract.py` (new — 32 static contract tests)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1729/1729 passed
   - sessionStorage JWT risk rated High (XSS-accessible; blocker for real PHI production)
   - httpOnly Secure SameSite=Lax cookie migration recommended before production PHI; implementation deferred to Module 95+
   - Machine auth headers (Vapi/n8n) are server-to-server; not browser CORS — correctly excluded from allow_headers
   - Go/no-go: Not ready for production launch; 6 blockers remain; ready to proceed to deployment smoke runbook

92. Module 94 — Deployment Smoke Runbook
   - Commit: 2674688
   - `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` (new — 17-section runbook: purpose, scope, prerequisites, 4 smoke tiers, local smoke steps with exact commands, staging smoke steps with placeholders, production-like pre-traffic smoke, Vapi smoke, n8n smoke, CORS smoke, auth/session smoke with PHI note, DB/migration smoke, logging safety, failure triage table with 14 scenarios, pass/fail checklist, production launch gate, appendix of local commands)
   - `backend/tests/test_deployment_smoke_runbook_contract.py` (new — 36 static contract tests)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1765/1765 passed
   - Covers local/staging/production-like tiers; Vapi, n8n, CORS, auth, DB, frontend, backend, logging
   - Production launch gate explicitly states smoke runbook alone does not approve launch; Architecture Checkpoint 12 required

## Architecture checkpoints

- Architecture Checkpoint 10 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_10_VAPI_APPOINTMENT_INTAKE_LOOP_REVIEW.md`
  - Updated post-checkpoint (Module 90): all pending evidence gaps closed
- Architecture Checkpoint 11 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_11_POST_VAPI_DIRECTION_REVIEW.md`
  - Reviews Sprint 11 outcomes; decides next sprint direction
  - Recommendation: Sprint 12 — Production Deployment Readiness Inventory
  - Defers: Fabel 5/frontend UX sprint (after deployment blockers mapped); appointment workflow expansion (after production risks known)
- Architecture Checkpoint 12 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_12_PRODUCTION_READINESS_REVIEW.md`
  - Production PHI launch: NO-GO (12 unresolved blockers)
  - Staging/fake-data deployment prep: GO
  - Auth/session hardening (httpOnly cookie): plan in Module 98; implement Sprint 14
  - Fabel 5/frontend UX sprint: deferred until staging topology confirmed
  - Appointment workflow expansion: deferred
  - Next direction: Sprint 13 — Staging Deployment Target Selection and Topology Plan
- Full backend tests: 1765/1765 passed
- Sprint 11 complete (Modules 81–90); Sprint 12 complete (Modules 91–94); Sprint 13 starting

93. Module 95 — Staging Deployment Target Selection and Topology Plan
   - Commit: 3102ab7
   - `docs/deployment/STAGING_DEPLOYMENT_TOPOLOGY_PLAN.md` (new — 15-section plan: purpose, context from Checkpoint 12, pre-existing baseline, platform comparison table with 5 options scored, chosen topology Railway+Vercel with rationale, architecture diagram, environment variable mapping table, staging domain placeholders, CORS constraint, DB strategy with isolated fake clinic UUID, migration gate, Vapi staging configuration, n8n staging strategy, sessionStorage JWT note, risk/mitigation table, staging limitations, Module 96 next step)
   - `backend/tests/test_staging_deployment_topology_plan_contract.py` (new — 33 static contract tests: plan exists, platforms compared Railway/Render/Fly.io/Vercel, managed PostgreSQL, chosen topology with rationale, fake/non-PHI data only, PHI no-go, HTTPS staging URLs, no ngrok in staging, no wildcard CORS, FRONTEND_CORS_ORIGINS, NEXT_PUBLIC_API_BASE_URL, Vapi endpoint vapi:tool singular, n8n strategy, isolated staging DB, migrations, secrets injection method, sessionStorage acceptable for fake-data staging only, no deployment executed, Module 96 mention, no real secrets)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1798/1798 passed
   - Chosen topology: Railway (Backend + PostgreSQL) + Vercel (Frontend)
   - Staging domains: https://staging-api.up.railway.app (backend), https://staging-app.vercel.app (frontend)
   - FRONTEND_CORS_ORIGINS: https://staging-app.vercel.app (exact; no wildcard)
   - sessionStorage JWT: acceptable for fake-data staging; not PHI-safe for production
   - Vapi test assistant points at Railway stable URL (replaces ngrok)
   - DATABASE_URL auto-injected by Railway PostgreSQL add-on
   - No seed_local_data.py in staging; staging-specific fake clinic UUID required

94. Module 96 — Staging Environment Variable Matrix
   - Commit: 5761683
   - `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` (new — 15-section matrix: purpose, environment boundary with 3-tier isolation rules, staging components table, full backend env var matrix with Railway injection details, frontend env var matrix, PostgreSQL staging matrix, Vapi staging matrix with machine auth headers, n8n staging matrix, domain/CORS variable mapping, secret generation rules, staging env setup checklist, validation checklist, 13-scenario failure matrix, production separation statements, Module 97 next step)
   - `backend/tests/test_staging_environment_variable_matrix_contract.py` (new — 34 static contract tests: matrix exists, Railway backend/PostgreSQL/Vercel covered, fake/non-PHI staging, PHI no-go, all 6 backend secrets, POSTGRES_DB/USER/PASSWORD, NEXT_PUBLIC_API_BASE_URL, vapi:tool singular, staging fake clinic UUID placeholder, no ngrok, no wildcard CORS, HTTPS only, no local-dev secrets, no production secrets, Railway/Vercel secret storage, migrations, n8n staging, no real patient data, no deployment in module, Module 97 mention, no real secrets in doc)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1832/1832 passed
   - DATABASE_URL: auto-injected by Railway PostgreSQL add-on; never set manually
   - JWT_SECRET_KEY / VAPI_WEBHOOK_SECRET / N8N_WEBHOOK_SECRET / INTERNAL_WEBHOOK_SECRET: set via Railway dashboard; high-entropy per-staging values
   - FRONTEND_CORS_ORIGINS: set via Railway dashboard to exact Vercel staging origin
   - NEXT_PUBLIC_API_BASE_URL: set via Vercel dashboard; build-time public var; not a secret
   - sessionStorage JWT: acceptable for fake-data staging only; httpOnly cookie required for production PHI (Module 98)
   - Staging fake clinic UUID: distinct from local 11111111-... UUID; assigned at DB provisioning time

95. Module 97 — Staging Deployment Dry-Run Checklist
   - Commit: 5f7122d
   - `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` (new — 19-section dry-run checklist: purpose, preconditions, target topology, repository readiness, Railway backend setup, Railway PostgreSQL, Vercel frontend, domain/CORS, env var checklist, migration gate, auth/dashboard, Vapi staging, n8n staging, smoke execution order, evidence capture, failure stop rules, rollback, go/no-go, Module 98 next step)
   - `backend/tests/test_staging_deployment_dry_run_checklist_contract.py` (new — 33 static contract tests: checklist exists, Railway/Vercel/PostgreSQL covered, fake/non-PHI data, PHI no-go, no deployment in module, no ngrok, no wildcard CORS, HTTPS, DATABASE_URL/JWT_SECRET_KEY/FRONTEND_CORS_ORIGINS/NEXT_PUBLIC_API_BASE_URL, migrations, Vapi vapi:tool singular/no auto-confirm/staff Confirm, n8n staging, no real patient data, no secrets in logs, rollback, evidence capture, failure stop rules, sessionStorage JWT fake-data-only/not PHI-safe, Module 98 mention, no real secrets in doc)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1865/1865 passed
   - Smoke execution order: 13-step sequence from health check to rollback readiness
   - Failure stop rules: 14 conditions that must halt the staging deployment attempt
   - Evidence capture: per-smoke checklist of command, status, screenshot, log snippet, commit SHA, timestamp, pass/fail
   - Go/no-go: staging GO when all checklists signed off; production PHI NO-GO; Fabel 5/UX sprint WAIT; Module 98 auth plan next

## Architecture checkpoints

- Architecture Checkpoint 10 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_10_VAPI_APPOINTMENT_INTAKE_LOOP_REVIEW.md`
  - Updated post-checkpoint (Module 90): all pending evidence gaps closed
- Architecture Checkpoint 11 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_11_POST_VAPI_DIRECTION_REVIEW.md`
  - Reviews Sprint 11 outcomes; decides next sprint direction
  - Recommendation: Sprint 12 — Production Deployment Readiness Inventory
  - Defers: Fabel 5/frontend UX sprint (after deployment blockers mapped); appointment workflow expansion (after production risks known)
- Architecture Checkpoint 12 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_12_PRODUCTION_READINESS_REVIEW.md`
  - Production PHI launch: NO-GO (12 unresolved blockers)
  - Staging/fake-data deployment prep: GO
  - Auth/session hardening (httpOnly cookie): plan in Module 98; implement Sprint 14
  - Fabel 5/frontend UX sprint: deferred until staging topology confirmed
  - Appointment workflow expansion: deferred
  - Next direction: Sprint 13 — Staging Deployment Target Selection and Topology Plan
96. Module 98 — Auth/Session Hardening Implementation Plan
   - Commit: (see git log)
   - `docs/security/AUTH_SESSION_HARDENING_IMPLEMENTATION_PLAN.md` (new — 15-section implementation plan: current auth architecture with exact code locations, production target architecture, cookie strategy with SameSite tier matrix, access token lifecycle, refresh token lifecycle (deferred), CSRF protection per-tier, logout flow with target backend route, browser behavior per scenario, backend changes (auth.py login cookie, logout route, get_current_user cookie read + Bearer fallback), frontend changes (auth.ts/api.ts/login/dashboard), testing strategy, rollback strategy, 13-step migration sequence, 10-scenario risk matrix, final recommendation + Sprint 14 scope)
   - `backend/tests/test_auth_session_hardening_plan_contract.py` (new — 27 static contract tests: plan exists, sessionStorage risk, XSS, HttpOnly, Secure, SameSite, Set-Cookie on login, POST /auth/logout, delete_cookie on logout, credentials: include, remove Authorization header, CSRF, SameSite=Lax CSRF protection, allow_credentials, get_current_user reads cookie, Bearer fallback, clinic_id from login body, staging cross-domain SameSite=None risk, refresh deferred, PHI blocker, testing strategy, planning only, Sprint 14, no real secrets)
   - No production code changes; no runtime behavior changed; no auth code modified
   - Full backend tests: 1892/1892 passed
   - Key finding: staging (Railway + Vercel) requires SameSite=None; Secure for cookie auth (cross-domain); production on same registrable domain uses SameSite=Lax
   - clinic_id resolution: after cookie migration, frontend reads clinic_id from login JSON response body (user.clinic_id); stores in localStorage
   - Bearer header fallback: keep in get_current_user during migration window; remove after full rollout
   - Refresh tokens: deferred to Sprint 14 or later; 60-min expiry accepted for initial production launch
   - Sprint 14 scope: implement cookie login/logout/get_current_user + frontend auth.ts/api.ts/pages update

   - Refresh tokens: deferred to Sprint 14 or later; 60-min expiry accepted for initial production launch
   - Sprint 14 scope: implement cookie login/logout/get_current_user + frontend auth.ts/api.ts/pages update

97. Module 99 — Production Deployment Execution Plan
   - Commit: (see git log)
   - `docs/deployment/PRODUCTION_DEPLOYMENT_EXECUTION_PLAN.md` (new — 17-section execution plan: purpose, current status (what is complete / what is NOT done), 12 production blockers tracker with Sprint 13 progress and open/resolved status, milestone sequence table (M1–M11 with go/no-go gates and sprint estimates), M1 staging deployment (Module 97 checklist + failure stop rules + rollback + Decision Gate A), M2 staging smoke (13-step smoke order + evidence capture + session storage note + Decision Gate B), M3 auth/session hardening (httpOnly cookie + SameSite=None for staging + clinic_id from login body + smoke re-run + Decision Gate C), M4 production domain and TLS (HTTPS domains + DNS + no ngrok), M5 production secrets provisioning (4 secrets + high-entropy + no placeholders), M6 production database (managed PostgreSQL + PITR + migration gate + isolation), M7 production Vapi assistant (dedicated production assistant + vapi:tool singular + no ngrok + Decision Gate D), M8 legal/GDPR/compliance review (hard gate; raw_payload PHI policy; Austrian DSG; data processor agreements), M9 CI/CD pipeline (GitHub Actions + Railway/Vercel hooks + manual approval for production), M10 production monitoring (APM + structured logs + alerting + on-call runbook), M11 production PHI launch (pre-launch checklist; all M1–M10 gates required; current status NO-GO), explicit deferrals table, Architecture Checkpoint 13 as next step)
   - `backend/tests/test_production_deployment_execution_plan_contract.py` (new — 54 static contract tests: plan exists, non-empty, staging deployment/Railway/Vercel/HTTPS/no-ngrok, staging smoke/smoke-runbook/evidence capture, auth hardening/httpOnly/SameSite/SameSite=None staging cross-domain/Sprint 14 implementation, production domain and TLS/DNS/no-ngrok, production secrets/JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/no-placeholder, production database/managed PostgreSQL/backups+PITR/migration gate, production Vapi/vapi:tool singular/no auto-confirm, legal/GDPR/Austrian healthcare/raw_payload PHI/hard gate, CI/CD/automated test gate/no secrets in CI logs, production monitoring/APM/alerting/structured logs, go/no-go gates/gate at each milestone/decision gates, PHI launch blocked/all gates must pass/12 open blockers, no deployment in module/planning document only, Architecture Checkpoint 13/checkpoint go/no-go/Sprint 13 deliverables under review, stop rules/rollback, no real API keys/no real DB password)
   - No deployment executed; no production secrets; no runtime code changes; no auth implementation
   - Full backend tests: 1946/1946 passed

- Full backend tests: 1946/1946 passed
- Sprint 11 complete (Modules 81–90); Sprint 12 complete (Modules 91–94); Sprint 13 complete (Modules 95–99)

## Architecture checkpoint

- Architecture Checkpoint 13 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_13_STAGING_DEPLOYMENT_GO_NO_GO_REVIEW.md`
- Commit: (see git log)
- Full backend tests: 1946/1946 passed
- Sprint 13 complete (Modules 95–99)
- Key decisions:
  - Fake-data staging deployment attempt: **GO**
  - Actual staging deployment attempt: **GO** — proceed in Sprint 14 per Module 97 checklist
  - Production PHI launch: **NO-GO** — all 12 blockers remain open
  - Auth/session hardening (httpOnly cookie): **GO** for Sprint 14; implement after M1/M2 evidence; before production PHI
  - SameSite=None required for Railway+Vercel staging (cross-domain); SameSite=Lax for production (same registrable domain)
  - Fabel 5/UX sprint: **DEFERRED** — wait until staging confirmed and auth hardened
  - Appointment workflow expansion: **DEFERRED**
- Recommended Sprint 14 sequence: Module 100 (config file inventory) → 101 (Railway prep) → 102 (Vercel prep) → 103 (DB/migration strategy) → 104 (smoke execution evidence) → Checkpoint 14

98. Module 100 — Staging Deployment Config File Inventory
   - Commit: (see git log)
   - `docs/deployment/STAGING_DEPLOYMENT_CONFIG_FILE_INVENTORY.md` (new — 13-section inventory: purpose, current repo layout (actual paths; missing files noted in tree diagram), Railway backend requirements table (requirements.txt MISSING/BLOCKER; Procfile MISSING/BLOCKER; runtime.txt MISSING; start command; app import path backend.app.main:app; $PORT/0.0.0.0 binding; health route; env vars; migration command; no DB-ready retry gap), Railway PostgreSQL inventory (managed add-on; DATABASE_URL auto-injection; migration target; seed_local_data.py must NOT run in staging; staging seed gap for Module 103), Vercel frontend requirements table (root directory=frontend/; package.json/build command; NEXT_PUBLIC_API_BASE_URL; no backend secrets in frontend env; frontend/.gitignore MISSING), cross-platform URL/domain inventory (FRONTEND_CORS_ORIGINS; no wildcard; no ngrok; HTTPS; SameSite cross-domain complication), migration/seed command inventory (run_migrations.py usable; seed_local_data.py local-only; smoke/sign scripts noted), Vapi/n8n inventory (capture-appointment-request; vapi:tool singular; no CORS dependency), required config files summary (existing/local-only/missing/not-needed), blockers table (12 items: requirements.txt BLOCKER; Procfile BLOCKER; Python version HIGH; staging seed HIGH; .gitignore gaps MEDIUM; no DB-ready retry MEDIUM; no Vapi test assistant HIGH; staging URLs unknown MEDIUM), recommended next actions (Module 101/102/103/104), non-goals)
   - `backend/tests/test_staging_deployment_config_file_inventory_contract.py` (new — 41 static contract tests: inventory exists, Railway backend/uvicorn/import path/PORT/health/requirements.txt missing/Procfile/python version/Nixpacks, Railway PostgreSQL/DATABASE_URL injection/migrations/seed gap/seed_local_data must not run/no DB-ready retry, Vercel frontend/root directory/package.json build/NEXT_PUBLIC_API_BASE_URL/no backend secrets/frontend gitignore missing, FRONTEND_CORS_ORIGINS/no wildcard/no ngrok/HTTPS/SameSite cross-domain, Vapi endpoint/vapi:tool singular/n8n staging, sessionStorage JWT fake-data acceptable/PHI blocker, fake/non-PHI staging/production PHI no-go, no deployment in module, Module 101/Railway prep, no real secrets)
   - Key findings: requirements.txt MISSING (BLOCKER); Procfile/railway.toml MISSING (BLOCKER); runtime.txt MISSING (HIGH); frontend/.gitignore MISSING (MEDIUM); backend uses PyJWT + bcrypt directly (not python-jose/passlib); no DB-ready retry in run_migrations.py; seed_local_data.py local-only; vercel.json not needed; next.config.js needs no output setting for Vercel
   - No deployment executed; no production secrets; no runtime code changes
   - Full backend tests: 1987/1987 passed

   - Commit: 3312049

99. Module 101 — Railway Backend Deployment Prep
   - Commit: (see git log)
   - `backend/requirements.txt` (new — 7 pinned runtime deps: fastapi==0.138.2, uvicorn[standard]==0.49.0, asyncpg==0.31.0, alembic==1.18.5, pydantic==2.13.4, PyJWT==2.4.0, bcrypt==3.2.0; no python-jose/passlib/httpx/pytest; Python 3.11; test deps excluded)
   - `runtime.txt` (new — `python-3.11`; pins Python version for Railway Nixpacks)
   - `Procfile` (new — `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`; migrations NOT in web command; migration is manual predeploy step)
   - `.gitignore` (updated — added backend/.env, frontend/.env.local, frontend/.next/, frontend/next-env.d.ts, frontend/node_modules/, frontend/package-lock.json)
   - `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` (new — 12-section prep doc: purpose, selected Railway approach/Nixpacks/Procfile, config files created in M101, required Railway env vars table (DATABASE_URL auto-injected; JWT_SECRET_KEY/VAPI/N8N/INTERNAL secrets; FRONTEND_CORS_ORIGINS; APP_ENV), Railway PostgreSQL binding, migration strategy (manual run via Railway "Run Command" or railway.toml preDeployCommand; NOT in Procfile web command; run_migrations.py notes including no retry loop), health check routes, log safety rules, Vapi integration (capture-appointment-request; vapi:tool; no ngrok; no auto-confirm; staff Confirm required), CORS/domain safety (no wildcard; HTTPS; no ngrok), blockers remaining before actual deploy (10 items), non-goals)
   - `backend/tests/test_railway_backend_deployment_prep_contract.py` (new — 37 static contract tests: requirements.txt exists/fastapi/uvicorn/asyncpg/alembic/pydantic/PyJWT/bcrypt/no secrets; runtime.txt exists/python-3.11; Procfile exists/backend.app.main/0.0.0.0/$PORT/web process/uvicorn; prep doc exists/Railway backend/fake-non-PHI/no deployment/DATABASE_URL/JWT_SECRET_KEY/FRONTEND_CORS_ORIGINS/health/migration/Vapi endpoint/vapi:tool/no ngrok/no wildcard/HTTPS/staff Confirm/PORT binding/blockers remaining/no real secrets)
   - No deployment executed; no production secrets; no runtime behavior changed; migrations NOT in Procfile (manual predeploy step)
   - Full backend tests: 2024/2024 passed

- Full backend tests: 2024/2024 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 in progress (Modules 100–101 complete)

100. Module 102 — Vercel Frontend Deployment Prep
   - Commit: (see git log)
   - `docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md` (new — 13-section prep doc: purpose (no deployment; fake/non-PHI; no Fabel 5), current frontend inventory (Next.js 14.2.3; App Router; package.json scripts; api.ts/auth.ts paths; login/dashboard routes; root .gitignore coverage from Module 101; no standalone frontend .gitignore needed; no vercel.json needed), recommended Vercel project settings (root=frontend; Next.js auto-detect; npm install; npm run build; no vercel.json; no output:standalone), Vercel env vars (only NEXT_PUBLIC_API_BASE_URL; no backend secrets table; failure mode if unset; no JWT_SECRET_KEY/DATABASE_URL/webhook secrets in frontend), frontend/backend URL contract (CORS bootstrap sequence: Railway→Vercel URL→FRONTEND_CORS_ORIGINS→restart→verify preflight; no wildcard; no ngrok; HTTPS; exact origin), auth/session staging caveat (sessionStorage JWT fake-data-only; XSS risk acceptable for staging; PHI blocker; httpOnly Secure SameSite=None when cookie auth implemented; SameSite cross-domain complication), build verification plan (npm run build not run in this module; previously verified Module 77), Vercel routing expectations (/login; /dashboard; client-side auth guard only), staging smoke expectations (9 steps), rollback plan, blockers before actual Vercel deploy (8 items), non-goals, recommended next Module 103)
   - `backend/tests/test_vercel_frontend_deployment_prep_contract.py` (new — 26 static contract tests: doc exists/non-empty; mentions Vercel+frontend/root directory/Next.js/npm run build/npm run dev; NEXT_PUBLIC_API_BASE_URL/no backend secrets/no DATABASE_URL/no JWT_SECRET_KEY; Railway staging API URL/FRONTEND_CORS_ORIGINS exact origin/no wildcard CORS/no ngrok/HTTPS; /login//dashboard routes; sessionStorage JWT fake-data-only/httpOnly cookie migration; fake/non-PHI staging only/no deployment executed/no Fabel 5 UX; rollback/Module 103 staging DB migration and seed; no real API keys)
   - No deployment executed; no production secrets; no runtime code changes; no frontend code changes; no auth/session implementation; no CORS changes; no npm install
   - Full backend tests: 2050/2050 passed

- Full backend tests: 2050/2050 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 in progress (Modules 100–102 complete)

101. Module 103 — Staging DB Migration and Seed Strategy
   - Commit: (see git log)
   - `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md` (new — 17-section strategy doc: purpose (planning only; no DB mutation; fake/non-PHI; production PHI no-go), current DB/migration inventory (alembic.ini at backend/alembic.ini; migrations/versions/0001_initial_schema.py + 0002_add_password_hash_to_clinic_users.py; run_migrations.py behavior; no DB-ready retry gap; seed_local_data.py local-only; db_smoke_test.py usable; docker-compose.postgres.yml local-only; backend/.env.example shows placeholder secrets), staging database target (Railway managed PostgreSQL; DATABASE_URL auto-injected; separate from local and production; fake/non-PHI only; pgcrypto supported), migration execution strategy (migrations must run before backend traffic; recommended command python backend/scripts/run_migrations.py; wait for Railway "Running" status; stop if non-zero; do not put in Procfile; capture sanitized output; alembic upgrade head is idempotent; expected final revision 0002_password_hash; 11 tables after head), migration readiness gaps (no DB-ready retry; no migration status verify step; no preDeployCommand created; future improvement documented), fake staging tenant/user strategy (staging-fake-clinic UUID placeholder; slug staging-fake-clinic; doctor.staging@praximed.test; must not use local-dev UUIDs 11111111-... or 22222222-...; must not reuse local-dev-password; staging Vapi test assistant must use staging clinic UUID), local seed script assessment (seed_local_data.py must not run against staging; hardcoded local UUIDs; local email; local-dev-password hash; local-only output labels; seeds patients and consultation_sessions not needed for smoke), recommended staging provisioning approach (Option A recommended: manual one-time SQL insert via Railway shell; Option B: future seed_staging_fake_data.py; Option C: Railway one-time Python command; no automatic production seed), password hashing for staging (hash_password() method documented; never commit plaintext; never reuse local-dev-password; high entropy; staging-only), required staging data for smoke (minimum: clinic row + clinic_user row; optional: appointment_request/patient/notification/consultation; smoke passes with empty tables after login), Vapi/n8n DB interaction (vapi:tool singular; staging clinic UUID in X-Clinic-Ref; status=new action_required=True hardcoded; no auto-confirm; staff Confirm only; n8n staging workflow; no production calendar), backup/rollback strategy (Railway PITR on paid plans; alembic downgrade; staging data is all fake; reset by drop+recreate if needed), evidence capture (command/timestamp/commit SHA/environment/sanitized output/revision/DB smoke test/staging clinic UUID/email; no secrets/PII), failure stop rules (14 rules: wrong DATABASE_URL target; migration failure; credentials in logs; real patient data; seed script targets wrong DB; production DB touched; duplicate clinic/user; auto-confirmed appointment; n8n to production calendar; real phone in Vapi), open blockers (12 items: Railway PostgreSQL not provisioned; DATABASE_URL unavailable; staging UUIDs not generated; staging password not created; secrets not set; migration not run; Vapi test assistant not configured; smoke not executed), non-goals, recommended next Module 104)
   - `backend/tests/test_staging_db_migration_seed_strategy_contract.py` (new — 27 static contract tests: doc exists/non-empty; Railway PostgreSQL; fake/non-PHI staging only; production PHI no-go; no DB mutation in module; alembic; run_migrations.py; python backend/scripts/run_migrations.py command; DATABASE_URL; migrations before backend traffic; migrations not in Procfile; backup/snapshot; rollback; seed_local_data.py local-only; staging fake clinic id placeholder; fake staging user; no real patient data; no production DB; Vapi creates appointment_request; status=new/action_required; staff Confirm/no auto-confirm; n8n staging workflow; evidence capture; failure stop rules; Module 104; no real secrets)
   - Key findings: seed_local_data.py must not run against staging (hardcoded local UUIDs + local-dev-password); run_migrations.py has no DB-ready retry (manual timing required); Option A (manual SQL via Railway shell) is the recommended first-smoke provisioning approach; staging fake clinic/user UUIDs must be newly generated; bcrypt hash generation documented safely
   - No DB mutation executed; no deployment; no production secrets; no runtime code changes
   - Full backend tests: 2077/2077 passed

- Full backend tests: 2077/2077 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 in progress (Modules 100–103 complete)

102. Module 104 — Staging Smoke Execution Evidence
   - Commit: (see git log)
   - `docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md` (new — 10-section results doc with result BLOCKED/PENDING: purpose (accuracy policy; no fabricated evidence; fake/non-PHI; production PHI no-go), current result (BLOCKED/PENDING — Railway backend/PostgreSQL/Vercel frontend not yet created; this is an accurate status not a failure), preconditions checked (all external: Railway backend/PostgreSQL/Vercel/staging URLs/env vars/fake tenant+user/migrations/Vapi/n8n — all MISSING or UNKNOWN; all repo-side items — all READY), smoke checklist (19 steps: /health, /health/ready, DB connection, migrations, fake tenant/user in DB, frontend loads, /login renders, CORS preflight, login, dashboard, appointments, Vapi test call, Vapi row in dashboard, staff Confirm, no auto-confirm, n8n NOT ENABLED, logs sanitized, rollback — all PENDING), evidence table (13 rows; all "Not available yet"), blockers preventing smoke (15 items: Railway/Vercel/PostgreSQL not created; staging URLs unknown; JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/N8N_WEBHOOK_SECRET/INTERNAL_WEBHOOK_SECRET/FRONTEND_CORS_ORIGINS/NEXT_PUBLIC_API_BASE_URL not set; staging clinic/user/password not created; migrations not run; Vapi test assistant not configured; n8n deferred), what is ready repo-side (18 items: requirements.txt/Procfile/runtime.txt/.gitignore/run_migrations.py/db_smoke_test.py/migration files/prep docs/2077 tests all READY), what must happen before real smoke (18 ordered steps from Railway service creation through evidence capture), safety constraints (10 rules: fake/non-PHI; no real patients; no production secrets; no production DB; no local-dev password; no ngrok; no wildcard CORS; no auto-confirm; staff Confirm required; sessionStorage JWT acceptable for staging), recommended next Architecture Checkpoint 14)
   - `backend/tests/test_staging_smoke_execution_results_contract.py` (new — 26 static contract tests: doc exists/non-empty; PASS/BLOCKED/PENDING accuracy boundary; no fabricated evidence; Railway backend/PostgreSQL; Vercel frontend; staging API/frontend HTTPS URLs; /health; migrations; /login; CORS; fake staging user; Vapi test assistant; vapi:tool scope; n8n staging workflow; staff Confirm/no auto-confirm; no real patient data; no production secrets; no ngrok; no wildcard CORS; evidence required/available; blockers; Architecture Checkpoint 14; no real secrets)
   - Key findings: no staging services exist; smoke result is BLOCKED/PENDING (accurate, not a failure); repo is fully ready for deployment; all 15 external blockers documented; 18-step ordered provisioning sequence documented
   - No deployment executed; no smoke fabricated; no production secrets; no runtime code changes
   - Full backend tests: 2103/2103 passed

- Full backend tests: 2103/2103 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104)

## Architecture checkpoint

- Architecture Checkpoint 14 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_14_STAGING_DEPLOYMENT_REVIEW.md`
- Commit: (see git log)
- Full backend tests: 2103/2103 passed
- Sprint 14 complete (Modules 100–104)
- Key decisions:
  - Actual fake-data staging service creation: **GO** — repo is fully ready; no further planning modules needed before Railway/Vercel service creation
  - Production PHI launch: **NO-GO** — 12 production blockers open; staging smoke not yet executed; auth hardening not yet implemented
  - Auth/session hardening (httpOnly cookie): **GO — after staging smoke evidence** — Module 98 plan complete; implement after M1/M2 staging evidence; SameSite=None required for Railway+Vercel cross-domain staging
  - Fabel 5/UX sprint: **DEFERRED** — wait until staging confirmed and auth hardened
  - Appointment workflow expansion: **DEFERRED**
- Repo-side readiness: 24 items confirmed READY; no runtime changes required before service creation
- External blockers: 18 items require manual developer action (Railway/Vercel service creation)
- Recommended Sprint 15 sequence: Module 105 (Railway backend runbook) → 106 (PostgreSQL provisioning/migration evidence) → 107 (Vercel frontend runbook) → 108 (staging environment wiring evidence) → 109 (staging smoke PASS/BLOCKED evidence) → Checkpoint 15

103. Module 105 — Railway Backend Service Creation Runbook
   - Commit: (see git log)
   - `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` (new — 15-section human-executable runbook: purpose (developer-executed; no Claude deployment; fake/non-PHI; no production launch), current repo readiness (Procfile/runtime.txt/backend/requirements.txt/health endpoint/migration runner all READY; 2103 tests), preconditions (Railway account; GitHub access; secrets generated with openssl rand -hex 32; no production secrets), Railway project/service creation steps (GitHub repo connection; Nixpacks Python detection; Procfile start command confirmation; service naming), backend service settings (root=repo root; start command `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`; health check path /health; Python 3.11; branch=master; auto-deploy recommendation; why --host 0.0.0.0 required; why $PORT required; why backend.app.main:app is the correct import path), required Railway env vars (DATABASE_URL auto-injected; JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/N8N_WEBHOOK_SECRET/INTERNAL_WEBHOOK_SECRET via openssl rand -hex 32; FRONTEND_CORS_ORIGINS placeholder until Vercel URL known; APP_ENV=staging; failure mode for each), DATABASE_URL binding note (auto-injected by Railway PostgreSQL add-on; never use local Docker or production URL), first deploy expectations (Nixpacks build; process start; lifespan startup; /health 200; /health/ready 503 until DB; DB routes 503 expected; CORS localhost default), migration command (not in Procfile; run via Railway "Run Command" after Module 106; python backend/scripts/run_migrations.py; stop if non-zero), health check verification (curl command; expected JSON; 200 vs 503 before DB), evidence to capture (11 items: service name/URL/branch/commit SHA/build status/Python version/start command/env var names/DATABASE_URL status/GET /health result/log snippet; no secret values), failure triage (12 rows: ModuleNotFoundError/missing dep/Python mismatch/127.0.0.1 binding/PORT binding/500/503 health/CORS/migration failures), stop rules (6 rules: production secrets requested; wrong DATABASE_URL; real patient data; secrets in logs; code change required; /health fails after config fix), non-goals (Module 106/107/108/109/auth/Fabel 5), recommended next Module 106)
   - `backend/tests/test_railway_backend_service_creation_runbook_contract.py` (new — 32 static contract tests: runbook exists/non-empty; Railway backend service; fake/non-PHI; no Claude deployment; service name; GitHub repo; root directory; Procfile; start command; backend.app.main:app; 0.0.0.0; $PORT; runtime.txt; python-3.11; backend/requirements.txt; /health; DATABASE_URL; JWT_SECRET_KEY; VAPI_WEBHOOK_SECRET; N8N_WEBHOOK_SECRET; INTERNAL_WEBHOOK_SECRET; FRONTEND_CORS_ORIGINS; openssl rand; no local Docker DATABASE_URL; no production DATABASE_URL; migration command; evidence capture; failure triage; stop rules; Module 106 PostgreSQL; no real secrets)
   - No deployment executed; no real secrets; no runtime code changes
   - Full backend tests: 2135/2135 passed

- Full backend tests: 2135/2135 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 in progress (Module 105 complete)

104. Module 106 — Railway PostgreSQL Provisioning and Migration Evidence
   - Commit: (see git log)
   - `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` (new — 15-section human-executable provisioning and migration runbook: purpose (developer-executed; no Claude deployment; fake/non-PHI; no production DB), current status (runbook/migration scripts READY; Railway PostgreSQL PENDING), preconditions (Module 105 backend must exist; /health must be 200; data safety checks), Railway PostgreSQL creation steps (Railway dashboard add Plugin; PostgreSQL; name; confirm private DATABASE_URL available; do not paste value), DATABASE_URL wiring (Variable reference injection into backend service; redeploy; /health/ready verification; safety rules: no localhost; no production), migration execution (python backend/scripts/run_migrations.py via Railway "Run Command"; wait for "Running" status; stop if non-zero; do not print DATABASE_URL; idempotent), migration verification (db_smoke_test.py; expected 4-table output; alembic current optional), health/readiness expectations (before/after DATABASE_URL injection; before/after migration; expected 200 at each stage), staging fake data provisioning (seed_local_data.py must not run; generate UUIDs; generate bcrypt hash; provisioning SQL with ON CONFLICT; verification queries), evidence to capture (14 items: project/service names; commit SHA; DATABASE_URL injection confirmed; migration command/timestamp/exit status/sanitized output; final revision; db smoke test; /health/ready 200; staging clinic UUID; user email; no secrets), failure triage (11 rows: DATABASE_URL missing/wrong/production; /health/ready 503; migration fails on DATABASE_URL/connection refused/alembic.ini not found/ModuleNotFoundError/SSL; db_smoke_test fails; provisioning duplicate key; credentials in logs), stop rules (8 rules: wrong DATABASE_URL; secrets in logs; migration targets wrong DB; real patient data; migration non-zero; production DB touched; project/service ambiguity), non-goals (Module 107/108/109/auth/production), recommended next Module 107)
   - `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` (new — 6-section evidence doc: purpose (accuracy policy; no fabricated evidence; BLOCKED/PENDING), current result (BLOCKED/PENDING — Railway PostgreSQL not yet provisioned), preconditions available/missing (all external missing; repo-side all READY), migration evidence table (14 rows; all "Not available yet"; all PENDING), blockers (8 items: PostgreSQL not provisioned; DATABASE_URL missing; not Running; migration not run; db_smoke_test not run; staging clinic/user not provisioned; /health/ready not 200), next evidence needed)
   - `backend/tests/test_railway_postgresql_migration_runbook_contract.py` (new — 25 static contract tests: runbook exists/non-empty; evidence doc exists/non-empty; Railway PostgreSQL; add-on/plugin; fake/non-PHI; no production DB; no real patient data; DATABASE_URL; DATABASE_URL auto-injected; no local Docker DATABASE_URL; no production DATABASE_URL; python backend/scripts/run_migrations.py; migrations not in Procfile; sanitized evidence; no secrets; seed_local_data.py local-only; PASS/BLOCKED/PENDING/FAIL states; stop rules; failure triage; evidence BLOCKED/PENDING; Module 107 Vercel; no real secrets in runbook/evidence)
   - Result: BLOCKED/PENDING (accurate; Railway PostgreSQL not yet provisioned; no fabricated evidence)
   - No deployment executed; no DB mutation; no real secrets; no runtime code changes
   - Full backend tests: 2160/2160 passed

- Full backend tests: 2160/2160 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 in progress (Modules 105–106 complete)

105. Module 107 — Vercel Frontend Project Creation Runbook
   - Commit: (see git log)
   - `docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` (new — 14-section human-executable runbook: purpose (developer-executed; no Claude deployment; fake/non-PHI; no production launch; no Fabel 5), current repo readiness (frontend/package.json build/start/dev/lint scripts; next.config.js no output:standalone; .env.example NEXT_PUBLIC_API_BASE_URL; Next.js 14.2.3; no vercel.json needed; 2160 tests), preconditions (Vercel account; GitHub access; Railway backend HTTPS URL from Module 105/106), Vercel project creation steps (import GitHub repo; framework auto-detect Next.js; root directory = `frontend` — CRITICAL; service naming), build settings (Next.js auto-detect; npm install; npm run build; output .next managed by Vercel; no vercel.json; no output:standalone), required env vars (NEXT_PUBLIC_API_BASE_URL only; public build-time; baked into browser bundle; not a secret; redeploy required after change; set before first build; forbidden backend secrets: DATABASE_URL/JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/N8N_WEBHOOK_SECRET/INTERNAL_WEBHOOK_SECRET/POSTGRES_PASSWORD), frontend/backend URL wiring (3-step sequence: deploy Railway → get Railway URL → set NEXT_PUBLIC_API_BASE_URL in Vercel → deploy Vercel → get Vercel URL → set FRONTEND_CORS_ORIGINS on Railway; no wildcard CORS; HTTPS; no ngrok), first deploy expectations (Next.js 14.2.3 build; CORS errors acceptable at this stage; partial deploy valid; /login page renders), browser smoke checklist (8 checks: page loads; /login renders; login form exists; no console errors; API calls fail with CORS until Module 108; /health reachable; no secrets in browser; no production data), evidence to capture (14 items: Vercel project name/URL/root directory/env var name confirmed/build status/commit SHA/build log snippet/login page render/no backend secrets confirmed/FRONTEND_CORS_ORIGINS dependency noted/no real patient data/no production secrets/Module 108 readiness; no secret values), failure triage (10 rows: wrong root directory/no package.json found/TypeScript error/env var missing/API points to localhost/CORS fails before FRONTEND_CORS_ORIGINS/env var changed but not redeployed/domain not recognized/build timeout/500 on login page), stop rules (7 rules: backend secrets in Vercel env; wrong NEXT_PUBLIC_API_BASE_URL; production data; build fails without obvious config fix; secrets in build logs; root directory not frontend; ngrok URLs), result states (PASS/BLOCKED/PENDING/FAIL; current: BLOCKED/PENDING), non-goals (CORS update on Railway/Vapi config/full smoke/auth hardening/Fabel 5/appointment workflow), recommended next Module 108)
   - `docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md` (new — 6-section evidence doc: purpose (accuracy policy; no fabricated evidence; BLOCKED/PENDING), current result (BLOCKED/PENDING — Vercel project not yet created), preconditions available/missing (all external missing; repo-side all READY), deployment evidence table (14 rows; all "Not available yet"; all PENDING), blockers (8 items: Railway backend URL unknown; Railway PostgreSQL pending; Vercel project not created; NEXT_PUBLIC_API_BASE_URL not set; first deploy not triggered; Vercel URL not assigned; FRONTEND_CORS_ORIGINS pending), next evidence needed)
   - `backend/tests/test_vercel_frontend_project_creation_runbook_contract.py` (new — 28 static contract tests: runbook exists/non-empty; evidence doc exists/non-empty; Vercel frontend project; no Claude deployment; fake/non-PHI staging; no production launch; root directory frontend; critical/required/must; Next.js auto-detect; npm run build; NEXT_PUBLIC_API_BASE_URL; Railway backend HTTPS URL; public build-time variable not a secret; no backend secrets in Vercel env; DATABASE_URL forbidden in Vercel; JWT_SECRET_KEY forbidden in Vercel; FRONTEND_CORS_ORIGINS dependency; CORS dependency on Vercel URL; evidence capture; no secrets in evidence; stop rules; PASS/BLOCKED/PENDING/FAIL states; Module 108; evidence BLOCKED/PENDING; no real secrets in runbook/evidence)
   - Result: BLOCKED/PENDING (accurate; Vercel project not yet created; no fabricated evidence)
   - No deployment executed; no real secrets; no runtime code changes; no npm install
   - Full backend tests: 2188/2188 passed

- Full backend tests: 2188/2188 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 in progress (Modules 105–107 complete)

106. Module 108 — Staging Environment Wiring Evidence
   - Commit: (see git log)
   - `docs/deployment/STAGING_ENVIRONMENT_WIRING_RUNBOOK.md` (new — 13-section human-executable wiring guide: purpose (developer-executed; no Claude deployment; fake/non-PHI; no production launch; no fabricated success), wiring map (Railway PostgreSQL→backend DATABASE_URL; Railway backend URL→Vercel NEXT_PUBLIC_API_BASE_URL; Vercel URL→Railway FRONTEND_CORS_ORIGINS; Railway URL→Vapi tool endpoint; Railway URL→n8n staging endpoint; browser traffic Vercel→Railway; machine traffic Vapi/n8n→Railway), required external URLs (Railway backend placeholder; Vercel frontend placeholder; Vapi tool endpoint; n8n staging endpoint; HTTPS only; no ngrok), required env var wiring (Railway backend: DATABASE_URL auto-injected/JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/N8N_WEBHOOK_SECRET/INTERNAL_WEBHOOK_SECRET/FRONTEND_CORS_ORIGINS exact Vercel URL no wildcard no trailing slash; Vercel frontend: NEXT_PUBLIC_API_BASE_URL Railway HTTPS URL public build-time; Vapi: server URL/X-Vapi-Service-Name/X-Vapi-Clinic-Id/X-Vapi-Scopes=vapi:tool singular/signing secret matches Railway; n8n: staging endpoint/HMAC matches N8N_WEBHOOK_SECRET), wiring order (15 ordered steps from Railway creation through full smoke), validation checks (12 checks: /health/200; /health/ready/200; alembic current; db_smoke_test; Vercel /login; CORS preflight; fake login; dashboard; Vapi test call; Vapi row in dashboard; Staff Confirm/no auto-confirm; n8n), common wiring failures (11 rows: NEXT_PUBLIC_API_BASE_URL wrong/localhost; CORS origin mismatch/trailing slash/wrong subdomain; DATABASE_URL missing; Vapi 403 scope plural; Vapi 401 secret mismatch; n8n 401 HMAC mismatch; fake user missing; migrations not run; Railway redeploy needed; Vercel redeploy needed for env var change), safety rules (10 rules: no real patients; no production secrets; no production DB; no local-dev password; no ngrok; no wildcard CORS; Vapi test assistant only; staff Confirm required; no auto-confirm; sessionStorage JWT fake-data-only), evidence to capture (24 evidence items across all 5 components; no secret values; no DATABASE_URL strings; no passwords), stop rules (8 rules: backend secrets in Vercel env; wildcard CORS; production secrets; real patient data; local-dev password; ngrok; auto-confirmation; secrets in evidence), result states (PASS/BLOCKED/PENDING/FAIL; current: BLOCKED/PENDING), non-goals (Module 105/106/107/109/auth/n8n production/production launch/Fabel 5), recommended next Module 109)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` (new — 7-section evidence doc: purpose (accuracy policy; no fabricated evidence; BLOCKED/PENDING), current result (BLOCKED/PENDING — no wiring evidence provided), preconditions available/missing (all external missing; repo-side all READY including Procfile/runtime.txt/migrations/scripts/frontend/runbooks/2188 tests), wiring evidence table (27 rows; all "Not available yet"; all PENDING covering Railway URL/health/ready/env var names/DATABASE_URL injected/migrations/alembic current/db_smoke_test/staging clinic UUID/user email/Vercel URL/NEXT_PUBLIC_API_BASE_URL/build status/commit SHA/login loads/FRONTEND_CORS_ORIGINS set/no wildcard/CORS preflight/fake login/dashboard/Vapi URL/Vapi scope singular/Vapi row/status=new/Staff Confirm/n8n/no secrets), blockers (14 items: HIGH/MEDIUM/LOW), what is repo-ready (16 items confirmed READY), next evidence needed (11 ordered steps))
   - `backend/tests/test_staging_environment_wiring_evidence_contract.py` (new — 49 static contract tests: runbook exists/non-empty; evidence doc exists/non-empty; staging environment wiring; fake/non-PHI; no Claude deployment; Railway backend/PostgreSQL; Vercel frontend; DATABASE_URL; FRONTEND_CORS_ORIGINS; NEXT_PUBLIC_API_BASE_URL; Vapi endpoint; vapi:tool scope; n8n staging; /health; /login; CORS; migrations; fake staging user; staff Confirm/no auto-confirm; no real patient data; no production secrets; no ngrok; no wildcard CORS; PASS/BLOCKED/PENDING; BLOCKED/PENDING in evidence; no fabricated success; Module 109 staging smoke; no real secrets in runbook/evidence)
   - Result: BLOCKED/PENDING (accurate; no staging wiring evidence provided; no fabricated success)
   - No deployment executed; no real secrets; no runtime code changes
   - Full backend tests: 2237/2237 passed

- Full backend tests: 2237/2237 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 in progress (Modules 105–108 complete)

107. Module 109 — Staging Smoke Execution PASS/BLOCKED Evidence
   - Commit: (see git log)
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` (new — 10-section smoke evidence doc: purpose (final Sprint 15 smoke evidence; fake/non-PHI; no fabricated evidence; accuracy policy), current result (BLOCKED/PENDING — Railway/Vercel/PostgreSQL/Vapi staging services or evidence not available yet), evidence status summary (17-row table: Railway backend URL/health/PostgreSQL/migrations/fake clinic+user/Vercel URL/login/CORS browser call/dashboard login/dashboard protected route/appointment Confirm/Vapi test assistant call/Vapi-created row/staff Confirm Vapi row/n8n staging NOT ENABLED DEFERRED/logs sanitized/rollback path — all "Not available yet"/"PENDING"), smoke checklist status (15 checks with PENDING/NOT ENABLED/DEFERRED; each has expected pass signal and blocker; all PENDING because no staging services), repo-side readiness (17 items all READY: Procfile/runtime.txt/requirements/run_migrations.py/db_smoke_test.py/migration files/frontend build/next.config.js/.env.example/CORS impl/all 4 Sprint 15 runbooks/DB migration strategy/smoke runbook/2237 tests), external blockers (14 items HIGH/MEDIUM/LOW — all same external blockers as Module 108), PASS criteria (16 explicit pass requirements: /health 200/migrations exit 0/alembic current head/fake clinic row/fake user row/Vercel /login loads/CORS preflight passes no wildcard/fake login JWT/dashboard renders/Vapi test call 200/Vapi row in DB/staff Confirm PATCH/no auto-confirm/n8n PASS or NOT ENABLED/logs no secrets/rollback path documented), safety constraints (12 rules: fake/non-PHI/no production secrets/no production DB/no real patients/no local-dev password/no ngrok/no wildcard CORS/HTTPS only/Vapi test assistant only/no auto-confirm/staff Confirm required/sessionStorage JWT fake-data-only risk), next human actions (12 ordered steps from Railway service creation through Checkpoint 15), recommended next Architecture Checkpoint 15)
   - `backend/tests/test_staging_smoke_execution_pass_blocked_evidence_contract.py` (new — 29 static contract tests: evidence doc exists/non-empty; PASS/BLOCKED/PENDING; no fabricated evidence; Railway backend/PostgreSQL; Vercel frontend; /health; DATABASE_URL; migrations; fake staging clinic/user; /login; CORS; dashboard; appointment Confirm; Vapi test assistant; Vapi-created appointment row; status=new/action_required; staff Confirm/no auto-confirm; n8n staging NOT ENABLED/DEFERRED; logs sanitized; rollback; no real patient data; no production secrets; no ngrok; no wildcard CORS; sessionStorage JWT fake-data-only risk; Architecture Checkpoint 15; no real secrets in doc)
   - Result: BLOCKED/PENDING (accurate; no staging smoke evidence provided; no fabricated success)
   - No deployment executed; no real secrets; no runtime code changes
   - Full backend tests: 2266/2266 passed

- Full backend tests: 2266/2266 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 complete (Modules 105–109 all complete)

## Architecture checkpoint

- Architecture Checkpoint 15 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_15_STAGING_DEPLOYMENT_EVIDENCE_REVIEW.md`
- Commit: (see git log)
- Full backend tests: 2266/2266 passed
- Sprint 15 complete (Modules 105–109)
- Key decisions:
  - More planning before manual setup: **NO** — Sprint 15 produced the complete runbook set; no further docs needed
  - Manual Railway backend service creation: **GO** — repo fully ready; runbook complete; this is the exact next step
  - Railway PostgreSQL creation: **GO** — after Railway backend URL confirmed (Module 106 runbook)
  - Vercel frontend creation: **GO** — after Railway backend URL confirmed (Module 107 runbook)
  - Staging smoke execution: **GO** — after wiring complete (Module 108/109 runbooks)
  - Production PHI launch: **NO-GO** — staging smoke evidence not captured; 12 production blockers open; auth hardening not implemented
  - Auth/session hardening (httpOnly cookie): **GO — after staging smoke PASS** — Module 98 plan complete; implement after smoke evidence
  - Fabel 5/UX sprint: **DEFER** — wait until staging confirmed and auth hardened
  - Appointment workflow expansion: **DEFER**
- Repo-side readiness: 19 items confirmed READY; no code changes or planning docs needed before manual service creation
- External blockers: 15 items require manual developer action (Railway/Vercel/Vapi service creation)
- First manual action: follow `RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` to create Railway project and backend service
- Evidence to capture after Railway backend creation: 16 items (service URL; commit SHA; build status; env var names; /health response; no secret values)
- Safety rules documented: no real patients; no production secrets; no local-dev password; no ngrok; no wildcard CORS; stop if secrets in logs
- Recommended Sprint 16 sequence: Module 110 (Railway backend evidence) → 111 (PostgreSQL evidence) → 112 (Vercel evidence) → 113 (wiring + smoke evidence) → Checkpoint 16

## Next module
Sprint 16 / Module 110 — Railway Backend Root Requirements Fix and Evidence Retest.

108. Module 110 — Railway Backend Root Requirements Fix
   - Commit: (see git log)
   - Real Railway deploy attempted: **FAILED** — `ModuleNotFoundError: No module named 'backend'`
   - Root cause: Railway root directory was set to `backend/`; start command `backend.app.main:app` resolves from inside `backend/` where the `backend` package does not exist; this is a Railway monorepo/root configuration issue
   - Fix:
     - `requirements.txt` (repo root, new) — one-line Nixpacks bridge: `-r backend/requirements.txt`; Nixpacks detects Python from this file at repo root; no duplicate pins
     - `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` — corrected root directory row (blank = repo root; NOT `backend/`); added Section 5.4 explaining exactly why `root=backend` causes `ModuleNotFoundError`; updated Step 4.2 to explain root `requirements.txt` bridge; updated failure triage with exact real error and fix
     - `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` — updated build system row; added Section 3.0 for root `requirements.txt` bridge with explicit `do not set root to backend` warning
   - `backend/tests/test_railway_backend_root_requirements_contract.py` (new — 16 static contract tests: root requirements.txt exists/references backend; Procfile exists/backend.app.main/0.0.0.0/$PORT; runtime.txt exists/python-3.11; runbook mentions repo root/warns not to set root to backend/ModuleNotFoundError No module named backend/root requirements bridge/no secrets/fake non-PHI staging; prep doc mentions repo root/ModuleNotFoundError)
   - No runtime app logic changed; no auth changes; no DB schema changes; no real secrets
   - Full backend tests: 2282/2282 passed

- Full backend tests: 2282/2282 passed
- Sprint 15 complete; Sprint 16 in progress (Module 110 config fix complete)
- Railway backend redeploy required: push `requirements.txt` to Railway; set root directory to blank (repo root) in Railway service settings; redeploy

109. Module 111 — Railway Root Requirements Direct Dependency Fix
   - Commit: (see git log)
   - Railway build retest failed: root `requirements.txt` used `-r backend/requirements.txt`; Railway/Railpack cannot resolve nested includes during install cache step
   - Fix: `requirements.txt` (repo root) — replaced `-r backend/requirements.txt` with direct pinned dependency list (fastapi/uvicorn/asyncpg/alembic/pydantic/PyJWT/bcrypt); matches `backend/requirements.txt` exactly; no nested includes
   - `backend/requirements.txt` unchanged (remains source reference)
   - `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` — Step 4.2 updated: direct dependencies explanation; explicit "do not use -r backend/requirements.txt" note with real Railway build failure reason
   - `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` — Section 3.0 updated: flat direct dependency list; real failure reason documented
   - `backend/tests/test_railway_root_requirements_direct_dependencies_contract.py` (new — 22 tests: root req exists/no nested include; fastapi/uvicorn/asyncpg/alembic/pydantic/PyJWT/bcrypt in root req; backend/requirements.txt exists; Procfile exists/backend.app.main; runtime.txt/python-3.11; runbook repo root/not backend root/direct deps/Railpack cannot resolve nested/no secrets/fake non-PHI; prep doc repo root/direct or flat deps)
   - `backend/tests/test_railway_backend_root_requirements_contract.py` — updated: replaced stale `test_root_requirements_references_backend_requirements` with `test_root_requirements_contains_fastapi` (reflects direct-dep approach)
   - No runtime app logic changed; no auth changes; no DB schema changes; no real secrets
   - Full backend tests: 2304/2304 passed

- Full backend tests: 2304/2304 passed
- Sprint 16 in progress (Modules 110–111 complete)

110. Module 112 — Railway Backend Service Creation Evidence
   - Commit: (see git log)
   - Real evidence provided by user: Railway backend active; `/health` → 200
   - `docs/runtime/RAILWAY_BACKEND_SERVICE_CREATION_EVIDENCE.md` (new — 8-section evidence doc: purpose (accuracy policy; fake/non-PHI; no production secrets), current result (PASS), evidence table (14 rows: service active PASS/URL https://web-production-fd91d.up.railway.app PASS/commit 081121b PASS/health endpoint PASS/GET /health 200 PASS/response body {"status":"ok","service":"PraxisMed API"} PASS/root requirements.txt direct deps PASS/Procfile start command PASS/root directory repo root PASS/Python 3.11 PASS/backend imports PASS/DATABASE_URL PENDING/FRONTEND_CORS_ORIGINS PENDING/health/ready 503 PENDING), what this proves (Railway builds; direct deps work; Procfile works; imports from repo root work; HTTPS URL serves backend), what this does not prove (PostgreSQL/migrations/login/dashboard/Vapi/Vercel/production PHI), safety boundary (fake/non-PHI only; Railway environment label may say "production" — PraxisMed status is fake-data staging; no real patients; no production secrets; production PHI NO-GO), remaining blockers (12 items: PostgreSQL not provisioned; DATABASE_URL not wired; migrations not run; fake clinic/user not provisioned; Vercel not deployed; NEXT_PUBLIC_API_BASE_URL not set; FRONTEND_CORS_ORIGINS not set; CORS not verified; fake login not tested; Vapi not pointed to staging; n8n not configured; full smoke not run), recommended next Module 113)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` updated: Railway backend URL row → PASS (`https://web-production-fd91d.up.railway.app`); /health response → PASS; /health/ready → PENDING
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` updated: evidence summary row 1 (Railway backend service) → PASS with URL + commit; smoke checklist check 1 (backend /health) → PASS; overall remains BLOCKED/PENDING
   - `backend/tests/test_railway_backend_service_creation_evidence_contract.py` (new — 20 static contract tests: evidence doc exists/non-empty; PASS; Railway service active; URL web-production-fd91d; /health; status ok response; commit 081121b; root requirements direct deps; Procfile/start command; repo root imports; fake non-PHI staging; no real patient data; production PHI not proven/NO-GO; PostgreSQL/DATABASE_URL PENDING; migrations PENDING; Vercel PENDING; Vapi PENDING; Module 113; no real secrets)
   - No runtime code changed; no secrets recorded; no real patient data
   - Full backend tests: 2324/2324 passed

- Full backend tests: 2324/2324 passed
- Sprint 16 in progress (Modules 110–112 complete)
- Railway backend URL confirmed: https://web-production-fd91d.up.railway.app
- Next: Module 113 — Railway PostgreSQL provisioning and migration

111. Module 113 — Railway Migration psycopg2 Dependency Fix
   - Commit: (see git log)
   - Real Railway migration attempted: **FAILED** — `ModuleNotFoundError: No module named 'psycopg2'`
   - Root cause: `psycopg2-binary` was missing from `requirements.txt`; SQLAlchemy/Alembic requires a synchronous PostgreSQL driver (`psycopg2`) for migrations even when `asyncpg` (async driver) is installed for runtime DB access; both drivers must coexist
   - Fix:
     - `requirements.txt` (repo root) — added `psycopg2-binary==2.9.9` after `asyncpg==0.31.0`; now contains 8 direct deps
     - `backend/requirements.txt` — added `psycopg2-binary==2.9.9` after `asyncpg==0.31.0`; kept in sync with root
     - `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` — added Section 6.1a "PostgreSQL Driver Requirements" (driver table: asyncpg = async runtime; psycopg2-binary = sync for Alembic; both required); added failure triage row for `ModuleNotFoundError: No module named 'psycopg2'`
     - `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` — updated current result: PostgreSQL Online PASS; DATABASE_URL wired PASS; migration failed `ModuleNotFoundError: No module named 'psycopg2'`; fix applied Module 113; evidence table updated with PASS rows for PostgreSQL status and DATABASE_URL injection
   - `backend/tests/test_railway_migration_psycopg2_dependency_contract.py` (new — 14 static contract tests: root requirements.txt exists/has psycopg2-binary/still has asyncpg; backend requirements.txt exists/has psycopg2-binary/still has asyncpg; migration runbook exists/mentions psycopg2-binary/mentions asyncpg/mentions ModuleNotFoundError/mentions run_migrations script; migration evidence doc exists/records psycopg2 failure/no secrets policy)
   - No runtime app logic changed; no auth changes; no DB schema changes; no real secrets
   - Full backend tests: 2338/2338 passed

- Full backend tests: 2338/2338 passed
- Sprint 16 in progress (Modules 110–113 complete)
- psycopg2-binary==2.9.9 now in both requirements files; Railway redeploy + migration rerun required
- Next: Module 114 — Railway PostgreSQL Migration Retest Evidence

112. Module 114 — Railway PostgreSQL Migration Retest Evidence
   - Commit: (see git log)
   - Real evidence provided by user: Railway backend `/health` → 200; `run_migrations.py` exit 0; `db_smoke_test.py` → 4 tables PASS
   - Sanitized migration output confirms both revisions applied: `0001_initial_schema` and `0002_password_hash`
   - Sanitized DB smoke output: SELECT 1 passed; clinics/patients/consultation_sessions/audit_log all confirmed
   - `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` — updated to PASS: migration failure history (Module 113 attempt + fix + Module 114 retest PASS); full evidence table (18 rows; PostgreSQL/DATABASE_URL/migration command/exit 0/0001/0002/db_smoke/4 tables/health all PASS; fake clinic/user/health-ready PENDING); sanitized migration output section; sanitized DB smoke output section; what this proves (PostgreSQL reachable; both drivers functional; migrations applied; 4 tables confirmed); what this does not prove (fake clinic/user/Vercel/CORS/Vapi/n8n/production PHI all PENDING); safety boundary; remaining blockers (11 items); recommended next Module 115
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — PostgreSQL status PASS; DATABASE_URL wired PASS; migrations PASS; db_smoke PASS; fake clinic/user/Vercel/CORS/Vapi/n8n remain PENDING; resolved blockers 1–5 noted
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — evidence summary table: PostgreSQL PASS; migrations PASS; smoke checklist check 3 (migrations applied) PASS; check 2 (health/ready) still PENDING (fake user not provisioned); overall BLOCKED/PENDING
   - `backend/tests/test_railway_postgresql_migration_retest_evidence_contract.py` (new — 22 static contract tests: evidence doc exists/non-empty; PASS; Railway PostgreSQL; DATABASE_URL wired name-only; run_migrations.py; 0001_initial_schema; 0002_password_hash; db_smoke_test.py; SELECT 1 passed; clinics/patients/consultation_sessions/audit_log tables; /health still PASS; no secrets; no real patient data; fake/non-PHI; fake clinic/user still PENDING; Vercel PENDING; Vapi PENDING; Module 115)
   - No runtime code changed; no secrets recorded; no real patient data
   - Full backend tests: 2360/2360 passed

- Full backend tests: 2360/2360 passed
- Sprint 16 in progress (Modules 110–114 complete)
- Railway PostgreSQL migration PASS; fake staging clinic/user still PENDING
- Next: Module 115 — Fake Staging Clinic and User Provisioning Evidence

113. Module 115 — Fake Staging Clinic and User Provisioning Evidence
   - Commit: (see git log)
   - Real evidence provided by user: fake staging clinic and doctor user provisioned in Railway PostgreSQL via Railway console
   - Staging clinic: `id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056` `slug=staging-fake-clinic` `status=active`
   - Staging user: `id=5b63b514-7624-4e8e-9af0-71c153ba7b83` `email=doctor.staging@praximed.test` `role=doctor` `status=active`
   - Password not recorded; bcrypt hash not recorded; DATABASE_URL not recorded; no real patient data; not local-dev-password; not local-dev UUIDs
   - `docs/runtime/FAKE_STAGING_CLINIC_USER_PROVISIONING_EVIDENCE.md` (new — 7-section evidence doc: purpose (accuracy policy; fake/non-PHI; no production secrets), current result (PASS), evidence (clinic table: id/slug/name/status/timezone/locale all PASS; user table: id/clinic_id/email/full_name/role/status/password_hash all PASS; sanitized verification output from Railway console), safety boundary (password/hash/DATABASE_URL not recorded; no real patient data; fake/non-PHI; not local-dev-password; not local-dev UUIDs; production PHI NO-GO), what this proves (Railway PostgreSQL has both rows; user bound to clinic; active status on both; password_hash column populated; credentials held privately; local-dev isolation confirmed), what this does not prove (login/JWT/health-ready/Vercel/CORS/dashboard/Vapi/n8n/production PHI all NOT PROVEN), next verification Module 116 with exact request template)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — fake staging clinic PASS (id/slug/status); fake staging user PASS (id/email/role/status); blockers 6+7 resolved; Vercel/CORS/Vapi/n8n remain PENDING
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — evidence summary row (fake staging clinic/user) PASS with real IDs; smoke checklist check 2 (health/ready) updated blocker note (not yet tested); check 6 (fake login) updated (not yet tested against staging backend); overall BLOCKED/PENDING
   - `backend/tests/test_fake_staging_clinic_user_provisioning_evidence_contract.py` (new — 19 static contract tests: evidence doc exists/PASS/fake staging clinic/staging-fake-clinic slug/clinic UUID/user email/user UUID/role doctor/status active/password not recorded/hash not recorded/DATABASE_URL not recorded/no real patient data/fake non-PHI/not local-dev-password/login endpoint pending/Vercel pending/Vapi pending/Module 116)
   - No runtime code changed; no secrets recorded; no real patient data
   - Full backend tests: 2379/2379 passed

- Full backend tests: 2379/2379 passed
- Sprint 16 in progress (Modules 110–115 complete)
- Fake staging clinic/user PASS; backend login smoke still PENDING
- Next: Module 116 — Backend Staging Login Smoke Evidence

114. Module 116 — Backend Staging Login Smoke Evidence
   - Commit: (see git log)
   - Real evidence provided by user: `GET /health` → 200; `GET /health/ready` → 200; `POST /auth/login` → 200
   - `GET /health/ready` response: `{"status":"ready","checks":{"app":"ok"}}` — DB pool healthy; JWT_SECRET_KEY set
   - `POST /auth/login` response: HTTP 200; `access_token` present (REDACTED); `token_type=bearer`; `expires_in_seconds` present; `user` object present; password not recorded; token value not recorded
   - `docs/runtime/BACKEND_STAGING_LOGIN_SMOKE_EVIDENCE.md` (new — 8-section evidence doc: purpose (accuracy policy; no secrets), current result (PASS), evidence (health/ready/login tables with all PASS; token REDACTED), safety boundary (password/token/hash/DATABASE_URL not recorded; no real patient data; fake/non-PHI; production PHI NO-GO), what this proves (backend reaches PostgreSQL; JWT_SECRET_KEY set; fake credentials authenticate; bearer token issued; all HTTPS endpoints reachable), what this does not prove (Vercel/CORS/browser login/dashboard/Vapi/n8n/production PHI all NOT PROVEN), remaining blockers (9 items), next step Module 117)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — health/ready PASS; direct login smoke PASS; Vercel/CORS/browser dashboard/Vapi/n8n remain PENDING
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — smoke checklist check 2 (health/ready) PASS; check 6 (fake login — direct backend) PASS; Vercel/browser/dashboard/Vapi/n8n remain PENDING; overall BLOCKED/PENDING
   - `backend/tests/test_backend_staging_login_smoke_evidence_contract.py` (new — 21 static contract tests: evidence doc exists/PASS; /health; /health/ready; /auth/login; status 200; staging email; clinic UUID; access_token present; token REDACTED; bearer; password not recorded; hash not recorded; DATABASE_URL not recorded; no real patient data; fake non-PHI; Vercel pending; CORS pending; browser dashboard pending; Vapi pending; Module 117)
   - No runtime code changed; no secrets recorded; no real patient data
   - Full backend tests: 2400/2400 passed

- Full backend tests: 2400/2400 passed
- Sprint 16 in progress (Modules 110–116 complete)
- Backend direct login smoke PASS; Vercel frontend deployment still PENDING
- Next: Module 117 — Vercel Frontend Deployment and API Wiring
