# Architecture Checkpoint 01 — PraxisMed Backend Review
**Date:** 2026-06-30
**Scope:** Modules 1–23, Sprint 1 complete
**Purpose:** Review backend architecture before starting the Clinical Documentation Engine milestone.

---

## A) Current System Summary

### What PraxisMed Can Currently Do

PraxisMed's backend is a fully functional, multi-tenant medical clinic AI automation platform with the following live capabilities:

1. **Calendar availability checking** — given a clinic reference and a datetime range, the backend returns whether a slot is bookable (not blocked, within opening hours).
2. **Available slot suggestion** — suggest open appointment windows for a given date.
3. **Calendar sync from n8n** — receive, validate, and persist calendar block changes triggered by n8n workflows.
4. **Vapi phone agent support** — the AI phone receptionist can call the backend to check availability, suggest slots, and capture appointment requests during a live call.
5. **Call log persistence** — every Vapi call event (started, ended, transcript, handoff) is normalised and stored in `clinic_call_logs`.
6. **Appointment request capture** — structured appointment requests are created from Vapi calls with source tracking, patient details, preferred times, urgency, and action flags.
7. **Internal notification creation** — urgency-driven notifications are automatically generated for human-handoff events, urgent calls, and new appointment requests.
8. **Notification API** — clinic staff can list, view, mark-read, and cancel notification records via REST.

### Which Major Flows Are Already Implemented

| Flow | Status |
|---|---|
| n8n → calendar sync → DB | Complete |
| Availability check (API + Vapi tool) | Complete |
| Slot suggestion (API + Vapi tool) | Complete |
| Vapi call event → call log | Complete |
| Vapi phone call → appointment request | Complete |
| Appointment request → internal notification | Complete |
| Urgent/handoff call → internal notification | Complete |
| Notification CRUD API | Complete |

---

## B) Module Inventory

| # | Module Name | Key Files | Purpose | Tests |
|---|---|---|---|---|
| 1 | Secure clinic config loader | `core/config_loader.py` | Multi-tenant config with path traversal protection and cache | ✅ |
| 2 | asyncpg PostgreSQL pool | `db/pool.py` | Async connection pool lifecycle tied to FastAPI startup/shutdown | ✅ |
| 3 | PostgreSQL schema contract | `db/schema.sql`, `test_schema_contract.py` | Idempotent DDL for all tables; contract tested against raw SQL | 194/194 |
| 4 | Calendar repository | `db/repositories/calendar_repo.py` | SQL for calendar blocks and sync events | ✅ |
| 5 | Availability engine | `modules/calendar_sync/availability_engine.py` | `is_slot_bookable` and `suggest_available_slots` business logic | ✅ |
| 6 | Calendar sync service | `modules/calendar_sync/calendar_sync.py` | Normalises and persists n8n calendar payloads | ✅ |
| 7 | FastAPI skeleton + health routes | `main.py`, `routes/health.py` | App factory, lifespan, `/health`, `/health/ready` | ✅ |
| 8 | n8n calendar sync webhook | `routes/calendar_webhooks.py` | `POST /webhooks/n8n/calendar-sync` with secret verification | ✅ |
| 9–10 | Availability schemas + API routes | `schemas/availability.py`, `routes/availability.py` | `POST /calendar/availability/check` and `/suggest` | ✅ |
| 11–12 | Vapi prompt builder + tool routes | `modules/vapi/vapi_prompt_builder.py`, `routes/vapi_tools.py` | Vapi availability tools: check + suggest | ✅ |
| 13–14 | Vapi call logs + call event webhook | `db/repositories/call_repo.py`, `modules/vapi/vapi_event_handler.py`, `routes/vapi_webhooks.py` | Persist call events, `POST /webhooks/vapi/call-event` | ✅ |
| 15 | Appointment request schema contract | `db/schema.sql` (updated) | `appointment_requests` table with CHECK constraints and indexes | 194/194 |
| 16 | Appointment request repository | `db/repositories/appointment_request_repo.py` | CRUD for `appointment_requests` | 20/20 |
| 17 | Appointment request API | `schemas/appointment_requests.py`, `routes/appointment_requests.py` | 7 REST endpoints for appointment requests | 27/27 |
| 18 | Vapi appointment capture | `modules/vapi/vapi_appointment_capture.py` | Converts a Vapi call into a structured appointment request | 34/34 |
| 19 | Notification schema contract | `db/schema.sql` (updated) | `clinic_notifications` table with CHECK constraints and 7 indexes | 194/194 |
| 20 | Notification repository | `db/repositories/notification_repo.py` | CRUD + status transitions for `clinic_notifications` | 26/26 |
| 21 | Notification router service | `modules/notifications/notification_router.py` | Event-to-notification translation; 3 typed convenience helpers | 21/21 |
| 22 | Vapi notification integration | `vapi_event_handler.py` + `vapi_appointment_capture.py` (updated) | Auto-creates internal notifications on handoff/urgent calls and appointment capture | 42/42 |
| 23 | Notification API routes | `schemas/notifications.py`, `routes/notifications.py` | 5 REST endpoints for notification CRUD | 26/26 |

**Total tests as of Module 23: 545/545**

---

## C) Route Inventory

### Health
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe — always returns ok |
| GET | `/health/ready` | Readiness probe — future DB health checks |

### n8n Webhooks
| Method | Path | Description |
|---|---|---|
| POST | `/webhooks/n8n/calendar-sync` | Receive and persist calendar changes from n8n |

### Availability
| Method | Path | Description |
|---|---|---|
| POST | `/calendar/availability/check` | Is a specific slot bookable? |
| POST | `/calendar/availability/suggest` | Suggest available slots for a date |

### Vapi Tools
| Method | Path | Description |
|---|---|---|
| POST | `/vapi/tools/check-availability` | Vapi-facing slot check (German message) |
| POST | `/vapi/tools/suggest-slots` | Vapi-facing slot suggestion (German message) |
| POST | `/vapi/tools/capture-appointment-request` | Create appointment request from a Vapi call |

### Vapi Webhooks
| Method | Path | Description |
|---|---|---|
| POST | `/webhooks/vapi/call-event` | Receive and persist Vapi call events |

### Appointment Requests
| Method | Path | Description |
|---|---|---|
| POST | `/appointment-requests` | Create a new appointment request |
| GET | `/appointment-requests` | List requests (filters: status, action_required, limit) |
| GET | `/appointment-requests/{id}` | Fetch a single request |
| PATCH | `/appointment-requests/{id}/status` | Update status |
| PATCH | `/appointment-requests/{id}/assign` | Assign to a clinic user |
| POST | `/appointment-requests/{id}/callback-needed` | Mark as callback needed |
| POST | `/appointment-requests/{id}/archive` | Archive the request |

### Notifications
| Method | Path | Description |
|---|---|---|
| POST | `/notifications` | Create an internal notification record |
| GET | `/notifications` | List notifications (filters: status, priority, type, recipient, limit) |
| GET | `/notifications/{id}` | Fetch a single notification |
| POST | `/notifications/{id}/read` | Mark as read |
| POST | `/notifications/{id}/cancel` | Cancel a pending notification |

**Total routes: 22**

---

## D) Data Model Inventory

### `clinics`
Root tenant table. Every other table references this via `clinic_id`. Stores slug, name, status, config path, timezone, locale.

### `clinic_users`
Staff and admin users belonging to a clinic. Scoped to `clinic_id`. Unique on `(clinic_id, email)`. Used as FK target for assignment and notification recipient fields.

### `clinic_calendar_connections`
OAuth/API connections to external calendar providers (Google, Microsoft Bookings). One clinic may have multiple connections. Unique on `(clinic_id, provider, external_calendar_id)`.

### `clinic_calendar_blocks`
Busy periods the AI booking layer must respect. Sourced from calendar sync, manual entry, or vacation uploads. Indexed for time-range overlap queries. Has `CHECK (ends_at > starts_at)`.

### `clinic_calendar_sync_events`
Append-only log of sync operations triggered by n8n or webhooks. Consumed by dashboards and alerting pipelines.

### `clinic_call_logs`
One row per inbound/outbound phone call handled by the Vapi voice agent. Tracks call status, duration, transcript, summary, urgency, and action-required flags. Unique on `(clinic_id, provider, external_call_id)`.

### `appointment_requests`
Structured appointment requests captured by phone AI, WhatsApp, web forms, or clinic staff. Not a confirmed booking — always requires staff review. CHECK constraints on `status`, `urgency_level`, and `source`. FK to `clinic_users` for assignment.

### `clinic_notifications`
Internal notification records for alerting clinic staff about events. Supports multiple channels (`internal`, `sms`, `push`, `email`, `webhook`), typed notification kinds, priority levels, and status lifecycle. FK to `clinic_users` for recipient. 7 composite indexes for efficient dashboard queries.

### `audit_log`
Immutable compliance trail. Rows are never updated or deleted. `clinic_id` FK uses `ON DELETE SET NULL` to preserve log entries even if a clinic is removed.

---

## E) Dependency Map

```
Vapi phone call
    │
    ├──▶ POST /vapi/tools/check-availability
    │        └──▶ availability_engine.is_slot_bookable
    │                 └──▶ calendar_repo (reads clinic_calendar_blocks)
    │
    ├──▶ POST /vapi/tools/suggest-slots
    │        └──▶ availability_engine.suggest_available_slots
    │                 └──▶ calendar_repo (reads clinic_calendar_blocks)
    │
    └──▶ POST /vapi/tools/capture-appointment-request
             └──▶ vapi_appointment_capture
                      ├──▶ config_loader (load clinic_id from clinic_ref)
                      ├──▶ appointment_request_repo.create_appointment_request
                      │        └──▶ clinic_notifications (INSERT)
                      └──▶ notification_router.create_appointment_request_notification
                               └──▶ notification_repo.create_notification
                                        └──▶ clinic_notifications (INSERT)

Vapi webhook (call event)
    │
    └──▶ POST /webhooks/vapi/call-event
             └──▶ vapi_event_handler.process_vapi_call_event
                      ├──▶ call_repo.upsert_call_log
                      │        └──▶ clinic_call_logs (UPSERT)
                      └──▶ notification_router.create_urgent_call_notification  [if human_handoff or urgent]
                               └──▶ notification_repo.create_notification
                                        └──▶ clinic_notifications (INSERT)

n8n calendar sync
    │
    └──▶ POST /webhooks/n8n/calendar-sync
             └──▶ calendar_sync.process_calendar_sync_payload
                      └──▶ calendar_repo (UPSERT/DELETE blocks, INSERT sync event)

Appointment request API (direct)
    │
    └──▶ POST /appointment-requests
             └──▶ appointment_request_repo.create_appointment_request
                      └──▶ appointment_requests (INSERT)

Notification API (future dashboard)
    │
    ├──▶ GET  /notifications          → list for clinic
    ├──▶ GET  /notifications/{id}     → fetch single
    ├──▶ POST /notifications/{id}/read   → mark read
    └──▶ POST /notifications/{id}/cancel → cancel
```

---

## F) Risk Review

### 1. Tenant isolation risks
**Severity: High — must address before patient modules.**
- All repository functions accept `clinic_id` as a parameter and include it in WHERE clauses. However, there is no middleware-enforced tenant isolation. A caller that sends the wrong `clinic_id` will silently query another tenant's data.
- Patient data (PHI) arriving in Module 24+ makes this a compliance risk.
- **Recommendation:** Before patient modules, add a lightweight assertion layer that verifies `clinic_id` is present and non-empty in every repository call. Consider adding a tenant-scoping middleware once auth is added.

### 2. Duplicated validation risks
**Severity: Medium — can wait, but track.**
- Enum validation is duplicated across Pydantic schemas (`schemas/`) and repository layers (`db/repositories/`). Changes to allowed values (e.g., adding a new urgency level) must be applied in multiple places.
- Currently manageable with 4 repos and 4 schema files, but will grow quickly with patient/consultation modules.
- **Recommendation:** Centralise allowed-value constants into a `backend/app/core/enums.py` module that both Pydantic validators and repository guards import from.

### 3. Schema growth risks
**Severity: Medium.**
- `schema.sql` is a single monolithic file. At 260+ lines it is still readable, but patient, consultation, audio, and summary tables will add 100–200 more lines. There is no migration tool (Alembic or similar).
- **Recommendation:** Before Module 24, decide on a migration strategy. Options: keep idempotent DDL in `schema.sql` (acceptable for early dev), or introduce Alembic for tracked migrations.

### 4. Test quality risks
**Severity: Low-medium.**
- All 545 tests are pure unit tests against mocked pools. This is correct per project rules and ensures fast, deterministic CI. However, there are no integration tests against a real DB, which means constraint violations, index behavior, and FK cascades are not exercised.
- **Recommendation:** Plan one integration test layer (possibly Module 34 or a separate test sprint) before production deployment.

### 5. Error handling consistency
**Severity: Low.**
- Most routes follow the pattern: `InvalidXxxError` → 400, `None` result → 404, catch-all `Exception` → 500. However, the availability routes use a slightly different exception hierarchy (`ConfigNotFoundError`, `ConfigValidationError`) than the notification/appointment routes. The pattern is consistent within each domain but not globally.
- **Recommendation:** Document the error contract in `CLAUDE.md` or `PROJECT_CONTEXT.md` so future modules follow the same structure.

### 6. Missing audit log usage
**Severity: Medium.**
- The `audit_log` table exists and was planned for compliance tracking. As of Module 23, no code writes to it. Patient and consultation data (arriving in Sprint 2) are the primary audit trail targets.
- **Recommendation:** Before or alongside Module 24, create `audit_log_repo.py` with a `log_action` function. Call it from appointment request creation, notification creation, and future patient/consultation operations.

### 7. Missing authentication
**Severity: High — known and deferred intentionally.**
- No auth middleware exists. All routes are open. This is per the project roadmap (auth is Milestone 9). However, the notification and appointment request APIs now expose PHI-adjacent data.
- **Recommendation:** Document this gap clearly. When patient tables arrive (Module 24+), ensure all test fixtures do not assume auth will be added later without changes.

### 8. Missing real database integration tests
**Severity: Medium — known and deferred.**
- Per project architecture rules, unit tests must not use a real database. This is correct. But the schema contract tests only assert SQL text, not actual execution semantics.
- **Recommendation:** Before production deployment, add a Docker Compose test environment and at least one end-to-end smoke test per major table.

---

## G) Refactor Recommendations

### Must do before patient modules

| Item | Reason |
|---|---|
| Create `backend/app/core/enums.py` with shared enum constants | Avoids triple-duplication of allowed values when patient/consultation enums arrive. Prevents silent divergence between schema CHECK constraints, repo validation, and Pydantic validators. |
| Create `audit_log_repo.py` with `log_action` function | Patient and consultation records are the primary audit targets. Starting this now keeps the implementation consistent and avoids retrofitting later. |
| Add `clinic_id` non-empty assertion to all repo functions | Cheap to add, prevents silent cross-tenant queries — becomes a PHI risk with patient tables. |

### Can wait

| Item | Reason |
|---|---|
| Centralise error HTTP mapping | Patterns are consistent enough within domains. Standardise when introducing auth middleware. |
| Migration tooling (Alembic) | `schema.sql` is fine for dev. Introduce before staging/production deployment. |
| Real DB integration tests | Correct per project rules. Plan for a future test sprint. |

### Avoid for now

| Item | Reason |
|---|---|
| Breaking up `schema.sql` into per-table files | The idempotent single-file DDL pattern works well in dev; splitting creates ordering dependencies and adds complexity without benefit at this stage. |
| Refactoring availability routes to use notification system | There is no clear trigger for availability errors to produce notifications yet. Wait until a real use case is identified. |
| Adding auth middleware now | Milestone 9. Adding it early without a real auth provider would produce placeholder code that must be ripped out later. |

---

## H) Next Milestone Plan — Clinical Documentation Engine

Sprint 2 covers Modules 24–34.

### Module 24 — Patient Schema Contract
Add `patients` table to `schema.sql`. Schema-only, no repo code.
Fields: `id`, `clinic_id`, `full_name`, `date_of_birth`, `gender`, `phone`, `email`, `insurance_number`, `insurance_provider`, `notes`, `status`, timestamps.

### Module 25 — Patient Repository
`db/repositories/patient_repo.py`. CRUD functions: `create_patient`, `get_patient_by_id`, `list_patients`, `update_patient`, `archive_patient`. Parameterised SQL only. No real DB in tests.

### Module 26 — Patient API
`schemas/patients.py`, `routes/patients.py`. REST endpoints: create, list, get, update, archive. Register in `router.py`.

### Module 27 — Consultation Session Schema Contract
Add `consultation_sessions` table. Fields: `id`, `clinic_id`, `patient_id`, `doctor_user_id`, `session_date`, `session_type`, `status`, `audio_path`, `transcript_text`, `ai_summary_draft`, `doctor_approved_summary`, `approved_at`, `approved_by_user_id`, `raw_payload`, timestamps.

### Module 28 — Consultation Repository
`db/repositories/consultation_repo.py`. CRUD + status transitions. No real DB in tests.

### Module 29 — Consultation API
`schemas/consultations.py`, `routes/consultations.py`. REST endpoints: create, list, get, update status.

### Module 30 — Audio Upload Placeholder Service
`modules/consultations/audio_upload.py`. Accept file reference, validate format/size, store path. No real storage integration yet — return placeholder path. Stub only.

### Module 31 — Transcription Adapter Interface
`modules/consultations/transcription_adapter.py`. Define abstract interface and a mock adapter. Real provider (Whisper, AssemblyAI, etc.) plugged in later.

### Module 32 — Clinical Summary Draft Generator
`modules/consultations/summary_generator.py`. Takes transcript text, calls Claude API (or stub), returns structured draft summary. Doctor must approve before it is used.

### Module 33 — Doctor Review and Approval Workflow
Add review/approve/reject endpoints. `doctor_approved_summary` is only written when doctor explicitly approves. Audit log entry written on approval.

### Module 34 — Patient Timeline Report
`modules/consultations/timeline_report.py`. Aggregate all consultations for a patient into a chronological report. Returns structured dict; future PDF export attaches here.

---

## I) Recommended Next Module

**Sprint 2 / Module 24 — Patient Schema Contract**

See `NEXT_MODULE.md` for the placeholder.
