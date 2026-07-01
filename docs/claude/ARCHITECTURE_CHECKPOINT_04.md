# Architecture Checkpoint 04 — Migration, Audit, and Integration Safety Review
**Date:** 2026-07-01
**Scope:** Modules 41–44, Sprint 4 complete
**Purpose:** Review the database migration foundation, audit logging foundation and integration, and overall readiness for real external integrations before connecting real PostgreSQL, Vapi, n8n, file storage, transcription providers, or LLM services.

---

## A) Current System Summary

### What PraxisMed Can Do After Modules 1–44

In addition to all Sprint 1–3 capabilities, PraxisMed now has:

1. **Schema migration foundation (Module 41)** — Alembic is configured with an offline-only `env.py` that reads `DATABASE_URL` from the environment. A single baseline migration (`0001_initial_schema`) captures all 11 tables, 39 indexes, and all FK/CHECK/UNIQUE constraints as they existed at Sprint 3 completion. Static contract tests verify the migration file structure without connecting to any database.

2. **Audit logging foundation (Module 42)** — `audit_repo.py` provides parameterised SQL for inserting into and querying the `audit_log` table. `audit_logger.py` wraps it with typed event builders for human (`AuthContext`) and machine (`MachineAuthContext`) actors. `safe_record_audit_event` is a never-raising wrapper used in all routes.

3. **PHI mutation audit trail (Module 43)** — every write mutation on patients, consultations, clinical workflows, appointment requests, and notifications now emits a structured audit event via `safe_record_audit_event`. Read-only routes are intentionally not audited.

4. **Machine route audit trail (Module 44)** — Vapi webhook, n8n calendar sync webhook, and the Vapi appointment capture tool route now emit machine audit events with `actor_type="machine"`. The read-only availability routes (check-availability, suggest-slots, check-availability tool, suggest-slots tool) are explicitly not audited.

### Current Test Count

**1193/1193 passed** (1.76 seconds, all mocked, no real database)

### Route Groups

| Route Group | Path Prefix | Endpoints | Auth Type | Audit |
|---|---|---|---|---|
| Health | `/health` | 2 | None (intentional) | No |
| Availability | `/calendar/availability` | 2 | Machine (availability:read) | No — read-only |
| Vapi tools — availability | `/vapi/tools/check-availability`, `/vapi/tools/suggest-slots` | 2 | Machine (vapi:tool) | No — read-only |
| Vapi tools — capture | `/vapi/tools/capture-appointment-request` | 1 | Machine (vapi:tool) | Yes — machine event |
| Vapi webhooks | `/webhooks/vapi` | 1 | Machine (vapi:webhook) | Yes — machine event |
| n8n calendar sync | `/webhooks/n8n` | 1 | Machine (calendar:sync) | Yes — machine event |
| Appointment requests | `/appointment-requests` | 7 | Human (staff) | Yes — mutations only |
| Notifications | `/notifications` | 5 | Human (staff) | Yes — mutations only |
| Patients | `/patients` | 7 | Human (staff) | Yes — mutations only |
| Consultations | `/consultations` | 10 | Human (clinical) | Yes — mutations only |
| Clinical workflows | `/clinical-workflows` | 7 | Human (clinical) | Yes — saving actions only |

**Total: 45 endpoints (2 unprotected health probes, 43 protected)**

### Database Tables

11 tables in the Alembic baseline migration (in dependency order):

| Table | Purpose |
|---|---|
| `clinics` | Root tenant table |
| `clinic_users` | Staff/admin users per clinic |
| `clinic_calendar_connections` | External calendar provider OAuth/API connections |
| `clinic_calendar_blocks` | Busy periods the AI booking layer must respect |
| `clinic_calendar_sync_events` | Append-only log of n8n sync operations |
| `audit_log` | Immutable compliance trail — now written by Modules 43/44 |
| `clinic_call_logs` | Vapi call events: started, ended, transcript, handoff |
| `appointment_requests` | Structured appointment requests requiring staff review |
| `clinic_notifications` | Internal notification records for clinic staff |
| `patients` | Patient registry with EMR upsert support |
| `consultation_sessions` | Full consultation lifecycle with draft/approved summary separation |

### Access Control State

**Human access (AuthContext):**
- Built from `X-User-Id`, `X-Clinic-Id`, `X-User-Role` headers (header-trust only — no JWT)
- `clinic_id` in body validated against `AuthContext.clinic_id` (same-clinic check)
- Staff-level roles: `owner`, `admin`, `doctor`, `staff` — patients, appointment requests, notifications
- Clinical-level roles: `owner`, `admin`, `doctor` — consultations, clinical workflows

**Machine access (MachineAuthContext):**
- Built from `X-Service-Name`, `X-Service-Clinic-Id`, `X-Service-Scopes` headers (header-trust only)
- Service name validated against `ALLOWED_SERVICE_NAMES = {"vapi", "n8n", "internal", "system", "dashboard"}`
- Scope validated against `ALLOWED_SERVICE_SCOPES`
- `clinic_id` from body/payload validated against `MachineAuthContext.clinic_id`

**Both remain header-trust placeholders** — no JWT signature verification, no HMAC, no database membership lookup.

### Audit Logging State

- `audit_log` table has existed since Module 3 (schema.sql). It is now written by live code for the first time as of Modules 43–44.
- **Human events**: emitted via `build_user_audit_event(auth_context, ...)` which sets `actor_type="user"`, `actor_id=auth_context.user_id`, `clinic_id=auth_context.clinic_id`, and includes `role` in metadata.
- **Machine events**: emitted via `build_machine_audit_event(machine_context, ...)` which sets `actor_type="machine"`, `actor_id=machine_context.service_name`, resolves `clinic_id` from payload or machine context, and includes `scopes` in metadata.
- **`safe_record_audit_event`** never raises — audit failures are silently absorbed and cannot break primary workflows.
- `result`, `severity`, `ip_address`, `user_agent`, `request_id` have no dedicated columns; they are folded into the JSONB `metadata` field with `_` prefix (`_result`, `_severity`, etc.).
- Sensitive free text (patient notes, transcript text, message content, raw_payload) is never included in audit metadata.

---

## B) Sprint 4 Module Inventory

| # | Module Name | Commit | Key Files | Purpose | Tests |
|---|---|---|---|---|---|
| 41 | Database migration foundation | `2daf4fd` | `backend/alembic.ini`, `backend/migrations/env.py`, `backend/migrations/script.py.mako`, `backend/migrations/versions/0001_initial_schema.py`, `backend/tests/test_migration_contract.py` | Alembic scaffold + baseline migration capturing all 11 tables; static-only contract tests (20 tests using pathlib + ast, no real DB) | 20/20 |
| 42 | Audit logging foundation | `f085f83` | `backend/app/db/repositories/audit_repo.py`, `backend/app/modules/audit/__init__.py`, `backend/app/modules/audit/audit_logger.py`, `backend/tests/test_audit_repo.py`, `backend/tests/test_audit_logger.py` | `audit_repo` (3 async functions), `audit_logger` (5 functions including `safe_record_audit_event`); full test coverage without route integration | 42/42 (20 repo + 22 logger) |
| 43 | Audit logging integration for PHI mutations | `726710a` | `routes/patients.py`, `routes/consultations.py`, `routes/clinical_workflows.py`, `routes/appointment_requests.py`, `routes/notifications.py` (all updated); corresponding test files updated | Wired `build_user_audit_event + safe_record_audit_event` into all mutation routes across 5 human-facing route files; GET routes untouched | 30/30 new audit tests |
| 44 | Audit logging integration for machine routes | `005e43a` | `routes/vapi_webhooks.py`, `routes/calendar_webhooks.py`, `routes/vapi_tools.py` (all updated); `test_vapi_webhook_route.py`, `test_calendar_webhook_route.py`, `test_vapi_tool_routes.py` (all updated) | Wired `build_machine_audit_event + safe_record_audit_event` into 3 machine-facing mutation routes; read-only availability routes explicitly not audited | 18/18 new audit tests |

**Sprint 4 total new tests: 110. Full suite after Sprint 4: 1193/1193 passed.**

---

## C) Migration Foundation Review

### Alembic Scaffold

`backend/alembic.ini` points the script location to `backend/migrations/`. The `env.py` reads `DATABASE_URL` from the environment variable — it has no hardcoded connection string, no asyncpg import, and does not use SQLAlchemy models. It operates in **offline-only (static) mode**: `run_migrations_offline()` is implemented; `run_migrations_online()` uses a synchronous `psycopg2`-style `engine_from_config` but does not invoke real async connections in the current codebase. The `env.py` reads from `DATABASE_URL` only and raises `RuntimeError` if it is missing.

### Baseline Migration

`0001_initial_schema.py` wraps the entire `schema.sql` DDL inside a single `op.execute()` block in `upgrade()`. All 11 tables, 39 indexes, FK constraints, CHECK constraints, and UNIQUE constraints are reproduced. The `downgrade()` function drops all tables in reverse dependency order (consultation_sessions → patients → clinic_notifications → appointment_requests → clinic_call_logs → audit_log → clinic_calendar_sync_events → clinic_calendar_blocks → clinic_calendar_connections → clinic_users → clinics). `revision = "0001_initial_schema"`, `down_revision = None`.

### Relationship Between `schema.sql` and the Migration

`schema.sql` and the migration file exist **in parallel** and are currently kept in sync manually. `schema.sql` remains the canonical reference document for developers who want to read the full schema at a glance. The migration file is the operational source of truth for schema deployment. No mechanism enforces that the two remain consistent — this is a drift risk.

### What Is Static-Only So Far

- All 1193 tests use `AsyncMock` pools or plain `object()` sentinels. No test connects to a real PostgreSQL instance.
- The migration contract tests (`test_migration_contract.py`) use `pathlib.Path.read_text()` and `ast.parse()` only — they verify file structure, revision IDs, function names, and SQL content as text, not as executable SQL.
- Alembic has never been invoked against a real database. `alembic upgrade head` has not been run.
- The `audit_log` rows emitted by Modules 43/44 are validated by test-mocked pools; no real row has been inserted.

### What Is Still Missing Before Real Database Use

| Gap | Description |
|---|---|
| `alembic upgrade head` smoke test | The migration SQL has never been executed against a real PostgreSQL. Schema correctness (extension availability, constraint syntax, FK ordering) is unverified at runtime. |
| `DATABASE_URL` environment variable | No `.env` file, no Docker Compose service, no documented value for local development. |
| asyncio-compatible migration runner | `env.py` is written for synchronous Alembic invocation. If using asyncpg for the production pool, a sync migration pass (via `psycopg2` or `asyncpg` run-in-thread) must be confirmed to work. |
| Schema drift detection | No CI step compares `schema.sql` to the migration file for divergence. |
| Migration for future schema changes | Any change to the schema (e.g., adding a `deleted_at` column for GDPR soft-delete) requires a new migration file. No tooling or convention exists yet for this. |
| Real integration tests against PostgreSQL | Test suite is 100% mocked. Constraint violations, index semantics, JSONB operator behavior, and FK cascade behavior are unverified. |

### Drift Risk: `schema.sql` vs. Migration File

The primary risk is that a developer makes a quick fix to `schema.sql` (e.g., adds a column during debugging) without creating a corresponding migration. This silently diverges the two sources of truth. When a new environment is created from migrations alone, it will miss the manual change.

**Mitigation (recommended, not yet implemented):** A CI job that applies the migration to an in-memory PostgreSQL (via `pg_tmp` or Docker) and then dumps the resulting schema, comparing it to `schema.sql`. Until then, treat `schema.sql` as the readable reference and migration files as the operational truth.

---

## D) Audit Logging Review

### `audit_repo.py`

Three async functions operating on the `audit_log` table:

- `create_audit_log(pool, clinic_id, action, resource_type, ...)` — validates all inputs (actor_type, result, severity against frozenset allowlists); builds a merged JSONB metadata payload folding `_result`, `_severity`, `_ip_address`, `_user_agent`, `_request_id` as system keys alongside caller-supplied keys; inserts with 7 parameterised parameters (`$1`–`$7`); returns the full row as a dict.
- `get_audit_log_by_id(pool, clinic_id, audit_log_id)` — fetchrow filtered by clinic_id AND id.
- `list_audit_logs(pool, clinic_id, ...)` — dynamic WHERE clause with up to 7 optional filters; `result` and `severity` filtered via `metadata->>'_result'` and `metadata->>'_severity'` JSONB operators; `limit` clamped to 1–100.

No SQL string interpolation. All values parameterised.

### `audit_logger.py`

Five functions:

- `build_audit_event(clinic_id, action, resource_type, ...)` — validates and returns a dict. Stateless.
- `build_user_audit_event(auth_context, action, resource_type, ...)` — derives `actor_type="user"`, `actor_id=auth_context.user_id`, `clinic_id=auth_context.clinic_id`; includes `role` in metadata.
- `build_machine_audit_event(machine_context, action, resource_type, clinic_id=None, ...)` — derives `actor_type="machine"`, `actor_id=machine_context.service_name`; resolves clinic_id from explicit parameter or machine_context; raises `InvalidAuditLogInputError` if no clinic_id can be resolved; includes `scopes` in metadata.
- `record_audit_event(pool, event)` — calls `audit_repo.create_audit_log`; maps `InvalidAuditEventError` → `InvalidAuditLogInputError`, `AuditRepoError` → `AuditLoggerError`; returns `{"ok": True, "audit_log": ..., "message": "Audit event recorded."}`.
- `safe_record_audit_event(pool, event)` — wraps `record_audit_event`; catches ALL exceptions; returns `{"ok": False, ...}` on any failure. **Never raises.**

### Human Audit Events (Module 43)

| Route | Action | Resource Type | Severity | Notes |
|---|---|---|---|---|
| `POST /patients` | `patient.create` | `patients` | info | |
| `POST /patients/upsert-by-external-id` | `patient.upsert_by_external_id` | `patients` | info | |
| `PATCH /patients/{id}` | `patient.update` | `patients` | info | |
| `POST /patients/{id}/archive` | `patient.archive` | `patients` | info | |
| `POST /consultations` | `consultation.create` | `consultation_sessions` | info | |
| `PATCH /consultations/{id}/status` | `consultation.status_update` | `consultation_sessions` | info | |
| `POST /consultations/{id}/audio` | `consultation.audio_attach` | `consultation_sessions` | info | |
| `POST /consultations/{id}/transcript` | `consultation.transcript_save` | `consultation_sessions` | info | |
| `POST /consultations/{id}/draft-summary` | `consultation.draft_summary_save` | `consultation_sessions` | info | |
| `POST /consultations/{id}/approve` | `consultation.approve` | `consultation_sessions` | **critical** | Doctor approval is compliance-critical |
| `POST /consultations/{id}/reject` | `consultation.reject` | `consultation_sessions` | **critical** | |
| `POST /consultations/{id}/archive` | `consultation.archive` | `consultation_sessions` | info | |
| `POST /clinical-workflows/consultations/{id}/audio-reference` | `clinical_workflow.audio_reference_attach` | `consultation_sessions` | info | |
| `POST /clinical-workflows/consultations/{id}/manual-transcript` | `clinical_workflow.manual_transcript_save` | `consultation_sessions` | info | |
| `POST /clinical-workflows/consultations/{id}/clinical-summary-draft` | `clinical_workflow.draft_summary_create` | `consultation_sessions` | info | |
| `POST /clinical-workflows/consultations/{id}/approve-summary` | `clinical_workflow.summary_approve` | `consultation_sessions` | **critical** | |
| `POST /clinical-workflows/consultations/{id}/reject-summary` | `clinical_workflow.summary_reject` | `consultation_sessions` | **critical** | |
| `POST /appointment-requests` | `appointment_request.create` | `appointment_requests` | info | |
| `PATCH /appointment-requests/{id}/status` | `appointment_request.status_update` | `appointment_requests` | info | |
| `PATCH /appointment-requests/{id}/assign` | `appointment_request.assign` | `appointment_requests` | info | |
| `POST /appointment-requests/{id}/callback-needed` | `appointment_request.callback_needed` | `appointment_requests` | **warning** | Urgency signal |
| `POST /appointment-requests/{id}/archive` | `appointment_request.archive` | `appointment_requests` | info | |
| `POST /notifications` | `notification.create` | `clinic_notifications` | info | metadata includes channel; excludes message + raw_payload |
| `POST /notifications/{id}/read` | `notification.mark_read` | `clinic_notifications` | info | |
| `POST /notifications/{id}/cancel` | `notification.cancel` | `clinic_notifications` | info | |

**Read-only routes NOT audited (intentional):** GET /patients, GET /patients/{id}, GET /patients/by-external-id/{id}, GET /consultations, GET /consultations/{id}, GET /appointment-requests, GET /appointment-requests/{id}, GET /notifications, GET /notifications/{id}, `GET /clinical-workflows/patients/{id}/timeline-report`, `POST /clinical-workflows/consultations/{id}/review-package`.

### Machine Audit Events (Module 44)

| Route | Action | Resource Type | Actor ID | Severity | Notes |
|---|---|---|---|---|---|
| `POST /webhooks/vapi/call-event` | `vapi.call_event` | `clinic_call_logs` | `"vapi"` | warning if result.action_required else info | clinic_id from payload; resource_id from result.call_id |
| `POST /webhooks/n8n/calendar-sync` | `n8n.calendar_sync` | `calendar_sync` | `"n8n"` | info | clinic_id from payload; event_type in metadata |
| `POST /vapi/tools/capture-appointment-request` | `vapi.appointment_capture` | `appointment_requests` | `"vapi"` | **warning** | clinic_id from result; resource_id from result.request.id; call_id in metadata |

**Read-only routes NOT audited (intentional):** `POST /calendar/availability/check`, `POST /calendar/availability/suggest`, `POST /vapi/tools/check-availability`, `POST /vapi/tools/suggest-slots`.

### Safe Audit Behavior

`safe_record_audit_event` wraps `record_audit_event` in a try/except that catches `Exception` — the broadest possible catch. This means:
- A misconfigured pool (e.g., pool is `None` or a `MagicMock`) will cause an `AttributeError` inside `record_audit_event`, which is caught.
- A network partition to PostgreSQL will cause an asyncpg connection error, which is caught.
- An invalid event dict (missing clinic_id, invalid actor_type) will cause `InvalidAuditLogInputError`, which is caught.
- In all cases the route continues to its primary response normally.

**Risk:** Audit failures are silent. In production, audit events failing consistently (e.g., due to a broken DB connection) would go unnoticed unless the returned `{"ok": False, ...}` dict is monitored. A logging statement before the return in `safe_record_audit_event` would make failures observable without changing the never-raise contract.

### How Sensitive Free Text Is Excluded from Audit Metadata

Route-by-route exclusion:
- **Patients**: `notes`, `raw_payload` are never included in audit metadata.
- **Consultations**: `transcript_text`, `draft_summary`, `approved_summary`, `rejected_reason` are never included.
- **Clinical workflows**: no transcript or summary content in metadata.
- **Notifications**: `message` (free text) and `raw_payload` are explicitly excluded; only `channel` is included.
- **Machine routes**: only structural identifiers (event_type, call_id, route name) are included; no payload content.

---

## E) Access + Audit Map

```
Route Group: Patients
  Auth:       Human — staff-level (owner, admin, doctor, staff)
  Guard:      require_staff_clinic_access(clinic_id, auth_context)
  Mutations audited:
    POST /patients                      → patient.create          severity=info
    POST /patients/upsert-by-external-id → patient.upsert_by_external_id  severity=info
    PATCH /patients/{id}                → patient.update          severity=info
    POST /patients/{id}/archive         → patient.archive         severity=info
  Not audited (read-only):
    GET /patients
    GET /patients/{id}
    GET /patients/by-external-id/{id}

Route Group: Consultations
  Auth:       Human — clinical-level (owner, admin, doctor)
  Guard:      require_clinical_clinic_access(clinic_id, auth_context)
  Mutations audited:
    POST /consultations                      → consultation.create           severity=info
    PATCH /consultations/{id}/status         → consultation.status_update    severity=info
    POST /consultations/{id}/audio           → consultation.audio_attach     severity=info
    POST /consultations/{id}/transcript      → consultation.transcript_save  severity=info
    POST /consultations/{id}/draft-summary   → consultation.draft_summary_save severity=info
    POST /consultations/{id}/approve         → consultation.approve          severity=critical
    POST /consultations/{id}/reject          → consultation.reject           severity=critical
    POST /consultations/{id}/archive         → consultation.archive          severity=info
  Not audited (read-only):
    GET /consultations
    GET /consultations/{id}

Route Group: Clinical Workflows
  Auth:       Human — clinical-level (owner, admin, doctor)
  Guard:      require_clinical_clinic_access(session.clinic_id, auth_context)
  Mutations audited:
    POST /clinical-workflows/consultations/{id}/audio-reference          → clinical_workflow.audio_reference_attach severity=info
    POST /clinical-workflows/consultations/{id}/manual-transcript        → clinical_workflow.manual_transcript_save severity=info
    POST /clinical-workflows/consultations/{id}/clinical-summary-draft   → clinical_workflow.draft_summary_create   severity=info
    POST /clinical-workflows/consultations/{id}/approve-summary          → clinical_workflow.summary_approve        severity=critical
    POST /clinical-workflows/consultations/{id}/reject-summary           → clinical_workflow.summary_reject         severity=critical
  Not audited (read-only/package-build):
    POST /clinical-workflows/consultations/{id}/review-package  (pure in-memory, no pool)
    GET  /clinical-workflows/patients/{id}/timeline-report

Route Group: Appointment Requests
  Auth:       Human — staff-level
  Guard:      require_staff_clinic_access(clinic_id, auth_context)
  Mutations audited:
    POST /appointment-requests                        → appointment_request.create          severity=info
    PATCH /appointment-requests/{id}/status           → appointment_request.status_update   severity=info
    PATCH /appointment-requests/{id}/assign           → appointment_request.assign          severity=info
    POST /appointment-requests/{id}/callback-needed   → appointment_request.callback_needed severity=warning
    POST /appointment-requests/{id}/archive           → appointment_request.archive         severity=info
  Not audited (read-only):
    GET /appointment-requests
    GET /appointment-requests/{id}

Route Group: Notifications
  Auth:       Human — staff-level
  Guard:      require_staff_clinic_access(clinic_id, auth_context)
  Mutations audited:
    POST /notifications               → notification.create     severity=info
    POST /notifications/{id}/read     → notification.mark_read  severity=info
    POST /notifications/{id}/cancel   → notification.cancel     severity=info
  Not audited (read-only):
    GET /notifications
    GET /notifications/{id}

Route Group: Vapi Webhooks
  Auth:       Machine — vapi:webhook scope
  Guard:      require_vapi_webhook_access(clinic_id, machine_context)
  Audited:
    POST /webhooks/vapi/call-event    → vapi.call_event
                                         actor_type=machine, actor_id="vapi"
                                         resource_type=clinic_call_logs
                                         severity=warning if action_required else info

Route Group: n8n Calendar Sync
  Auth:       Machine — calendar:sync scope
  Guard:      require_n8n_calendar_sync_access(clinic_id, machine_context)
  Audited:
    POST /webhooks/n8n/calendar-sync  → n8n.calendar_sync
                                         actor_type=machine, actor_id="n8n"
                                         resource_type=calendar_sync
                                         severity=info

Route Group: Vapi Tools — Appointment Capture
  Auth:       Machine — vapi:tool scope
  Guard:      require_vapi_tool_access(clinic_ref, machine_context)
  Audited:
    POST /vapi/tools/capture-appointment-request → vapi.appointment_capture
                                                    actor_type=machine, actor_id="vapi"
                                                    resource_type=appointment_requests
                                                    severity=warning (always — captures require staff review)

Route Group: Vapi Tools — Availability (read-only)
  Auth:       Machine — vapi:tool scope
  Guard:      require_vapi_tool_access(clinic_ref, machine_context)
  NOT audited — read-only:
    POST /vapi/tools/check-availability
    POST /vapi/tools/suggest-slots

Route Group: Availability (read-only)
  Auth:       Machine — availability:read scope
  Guard:      require_availability_read_access(clinic_ref, machine_context)
  NOT audited — read-only:
    POST /calendar/availability/check
    POST /calendar/availability/suggest
```

---

## F) Safety Review

| Safety Concern | Status | Evidence |
|---|---|---|
| Auto-diagnosis | **Protected** | `summary_builder.validate_clinical_summary_draft` rejects any draft with a top-level `diagnosis` key. `no_diagnosis_generated=True` is required on every draft. |
| Treatment advice generation | **Protected** | `no_treatment_advice_generated=True` is a required draft field. `validate_clinical_summary_draft` rejects drafts where it is False. |
| AI draft treated as final | **Protected** | Every draft carries `doctor_review_required=True`. Approved summaries require explicit `approved_by_user_id`. DB CHECK constraint enforces `approved_at IS NOT NULL` when `approval_status = 'approved'`. |
| Draft summaries in timeline by default | **Protected** | `extract_summary_for_timeline` returns None for drafts unless `include_drafts=True`. Default is False at all call sites. |
| Missing doctor approval | **Protected** | `approval_status` CHECK constraint; `approved_at` NOT NULL when approved; `approve_consultation_summary` requires non-empty `approved_by_user_id`. Audited at `severity=critical`. |
| Appointment auto-confirmation by Vapi | **Protected** | `vapi_capture_appointment_request` creates `status='new'`, `action_required=True`. Response message explicitly states staff must review. The capture route is now audited as `severity=warning` to flag every Vapi-initiated capture for review. |
| Unauthenticated PHI access | **Protected (structurally)** | All PHI routes require `AuthContext`. Auth is header-trust (not signed), but unauthenticated requests (no headers) return 401. |
| Cross-tenant access via caller-supplied clinic_id | **Protected (structurally)** | `ensure_same_clinic` compares body clinic_id to `AuthContext.clinic_id`. However, both values originate from headers — there is no DB membership check. A caller supplying matching spoofed headers still passes. |
| Audit failure breaking primary workflows | **Protected** | `safe_record_audit_event` never raises. Audit failure is absorbed; primary response proceeds. Tested explicitly in audit failure tests per route. |
| Sensitive free text leaking into audit metadata | **Protected** | Patient notes, transcript text, draft/approved summaries, notification message content, and raw_payload fields are explicitly excluded from all audit metadata dicts. Only structural identifiers (resource IDs, event types, call IDs, channels) are included. |

---

## G) Integration Readiness Review

### Real PostgreSQL (Local Docker)

| Item | Status | Blockers |
|---|---|---|
| Schema DDL | Ready — baseline migration captures full schema | `alembic upgrade head` never executed; no Docker Compose config |
| asyncpg pool | Ready — lifecycle wired to FastAPI startup/shutdown | Requires `DATABASE_URL` in env |
| All repositories | Ready — parameterised SQL, no ORM | No real constraint or FK cascade exercised |
| Migration runner | Scaffold ready; never executed against real DB | Need `docker-compose.yml`, `DATABASE_URL`, smoke test |
| Alembic version tracking | Configured correctly | Untested against real PostgreSQL |
| Audit log writes | Code written; SQL correct | Untested against real DB; `_result`/`_severity` in JSONB requires no schema change |

**Verdict: One Docker Compose + `alembic upgrade head` command away from a working local database. This is the natural first step of Sprint 5.**

### Applying Migrations to a Real Database

| Item | Status |
|---|---|
| Migration file syntax | Valid Python + SQL — static tests pass |
| Table creation order | Correct: clinics first, consultation_sessions last |
| `IF NOT EXISTS` guards | Present on all CREATE TABLE statements |
| Extension `pgcrypto` | Required by `gen_random_uuid()` — must be available on target PostgreSQL |
| Downgrade script | Present — drops tables in correct reverse order |
| `alembic_version` table | Auto-managed by Alembic; not in `schema.sql` |

**Verdict: Ready for first run, but must be tested in a real local PostgreSQL before any staging deployment.**

### Vapi Dashboard Setup

| Item | Status | Blocker |
|---|---|---|
| Tool routes | Structurally ready | Machine auth headers (`X-Service-Name`, `X-Service-Clinic-Id`, `X-Service-Scopes`) not natively sent by Vapi; must be configured in function definitions |
| Webhook route | Structurally ready | String-match secret only; no HMAC-SHA256 |
| Call log persistence | Ready | Requires real PostgreSQL pool |
| Appointment capture | Ready | Requires real pool + config files |
| Machine auth strategy | Not defined | Real Vapi sends its own signature headers; `X-Service-*` convention must be explicitly injected or replaced |

**Verdict: Not pilot-ready. Machine auth header injection strategy must be defined before connecting real Vapi traffic.**

### n8n Workflow Setup

| Item | Status | Blocker |
|---|---|---|
| Calendar sync webhook | Structurally ready | Must configure n8n HTTP Request node to send `X-Service-Name: n8n`, `X-Service-Clinic-Id`, `X-Service-Scopes: calendar:sync` |
| Webhook secret | String-match env var in place | No HMAC |
| Calendar block persistence | Ready | Requires real PostgreSQL pool |

**Verdict: Closer to ready than Vapi — n8n HTTP Request nodes natively support custom headers. Still requires PostgreSQL and documented setup guide.**

### Webhook Signatures / HMAC

| Item | Status |
|---|---|
| Vapi webhook secret | String equality on `X-PraxisMed-Vapi-Secret` against `PRAXIMED_VAPI_WEBHOOK_SECRET` env var |
| n8n webhook secret | String equality on `X-PraxisMed-Webhook-Secret` against `PRAXIMED_N8N_WEBHOOK_SECRET` env var |
| HMAC-SHA256 | Not implemented on either route |

**Verdict: Current implementation is better than no validation, but HMAC verification (signing the full request body) must be added before any production traffic. Real Vapi supports HMAC webhook signatures; this should be the first security hardening step for webhook routes.**

### Real File Storage

Audio files contain PHI (spoken consultations). Current state: path builder produces sanitised local paths; no real file I/O exists. No S3, GCS, or local disk adapter. No access control model at the storage layer (no signed URLs, no expiry, no tenant isolation).

**Verdict: Not ready. Must implement a local-disk adapter first (dev), then an S3-compatible interface (staging) before handling real consultation recordings.**

### Real Transcription Provider

`TranscriptionAdapter` Protocol is clean. Mock adapter exists. No real Whisper/OpenAI/AssemblyAI adapter. The interface is the extension point: one module implements `transcribe_audio_reference`.

**Verdict: One module away. Interface is clean; implementation is straightforward.**

### Real LLM Clinical Summary Provider

`summary_builder.py` uses regex/marker extraction. Works only when transcript uses exact structured markers. Real consultation transcripts are conversational — they rarely match markers. The `source` parameter is the extension point for an LLM adapter.

**Verdict: Not ready for real transcripts. A Claude API adapter wrapping `summary_builder` is needed. Requires careful prompt design and safety validation to preserve `no_diagnosis_generated=True` invariant.**

### Frontend / Dashboard

45 REST endpoints are complete. Auth model is not browser-compatible (custom headers, not cookies or JWT Bearer tokens). CORS policy is FastAPI default (all origins). No response field-level access control. Patient `notes` and `raw_payload` are returned by full CRUD routes.

**Verdict: Not ready. Auth model, CORS configuration, and PHI field audit are all prerequisites before any frontend integration.**

### Real Auth / JWT / OAuth

`AuthContext` and `MachineAuthContext` are built from header values with no signature verification. JWT decode, database membership check, and token refresh are all unimplemented.

**Verdict: Milestone 9 per roadmap. Placeholder model is acceptable for internal development. Must be replaced before any external party or real patient interacts with the system.**

---

## H) Remaining Risks Before External Pilot

Ranked by severity:

### Risk 1 — Header-Trust Auth Is a Bypass-Ready Placeholder
**Severity: Critical before any external traffic**

Both `AuthContext` and `MachineAuthContext` are constructed entirely from HTTP headers. Any caller that sends the correct header values gains full access, including to PHI routes. No JWT signature, no HMAC, no database membership lookup. Audit trail now exists, but it can be trivially forged by spoofing headers.

**Must fix before any external pilot.**

### Risk 2 — No User-to-Clinic Database Membership Check
**Severity: High**

`ensure_same_clinic` checks that body `clinic_id == AuthContext.clinic_id`, but `AuthContext.clinic_id` itself comes from a header. A caller that fabricates both `X-User-Id` and `X-Clinic-Id` passes all current guards. There is no check that the user actually belongs to the clinic in the `clinic_users` table.

**Must fix before real user-facing deployment.**

### Risk 3 — No Webhook Signature Verification (HMAC)
**Severity: High before real Vapi/n8n traffic**

Both webhook routes use string equality on a static secret. This is better than nothing but is not HMAC-based. Real Vapi supports HMAC signatures on the full request body; without verification, any caller who guesses or intercepts the string secret can send arbitrary webhook payloads that will be processed and audited as legitimate.

**Must fix before connecting real Vapi/n8n webhooks.**

### Risk 4 — Machine Auth Headers Are Internal Conventions
**Severity: High before Vapi/n8n integration**

`X-Service-Name`, `X-Service-Clinic-Id`, and `X-Service-Scopes` are not natively sent by Vapi or n8n. Integrating real services requires either: (a) configuring each service to send these headers in HTTP requests, (b) a reverse proxy or API gateway that injects them after HMAC verification, or (c) replacing the machine auth model with HMAC/JWT before pilot. No integration strategy has been defined or documented.

**Must define before connecting real traffic.**

### Risk 5 — Migration Never Executed Against Real PostgreSQL
**Severity: High before staging**

`alembic upgrade head` has never been run. The migration SQL is structurally correct and statically tested, but runtime correctness (pgcrypto extension availability, FK constraint ordering, asyncpg compatibility with `op.execute()`) is unverified. A failed migration against a staging database with real data would require manual recovery.

**Must smoke-test locally before any staging deployment.**

### Risk 6 — PHI Retention and Deletion Policy Absent
**Severity: High for GDPR/DSGVO compliance**

Austrian private medical data is subject to GDPR and national health data regulations. There is no retention period enforcement, no patient data deletion workflow, no right-to-erasure implementation. Consultation transcripts, approved summaries, and patient records are stored indefinitely. Audit logs use `ON DELETE SET NULL` for clinic_id (log entry preserved even if clinic is deleted), which may conflict with right-to-erasure.

**Must define and implement before any real patient data is processed.**

### Risk 7 — Audit Failures Are Silent
**Severity: Medium**

`safe_record_audit_event` absorbs all exceptions without logging. In production, repeated audit failures (e.g., database pool exhaustion, wrong credentials) would go unnoticed. Compliance-critical events (consultation.approve, clinical_workflow.summary_approve) might fail to record without anyone knowing.

**Should add a `logger.warning(...)` inside `safe_record_audit_event` before production.**

### Risk 8 — No PHI Field-Level Access Control in CRUD Responses
**Severity: Medium**

`GET /patients/{id}` and `GET /patients` return full patient records including `notes` (free text) and `raw_payload` (JSONB). These are excluded from the timeline report but not from direct CRUD responses. Any caller with valid staff-level auth can read all patient notes for their clinic.

**Should audit all response models before fronting with a dashboard.**

### Risk 9 — No Request Rate Limiting
**Severity: Medium**

No rate limiting middleware exists. Vapi availability tools and appointment capture can be called in rapid succession during a phone call. A misconfigured Vapi assistant could flood these routes. The audit log would grow proportionally.

**Should add before pilot traffic.**

### Risk 10 — No Secrets Management Review
**Severity: Medium**

Webhook secrets are read from environment variables. No secrets manager, no rotation policy, no audit of which secrets exist. The boundary between configuration and secrets in clinic config files has not been formally reviewed.

**Should document and implement before production.**

### Risk 11 — No Real File Storage Security Model
**Severity: Medium**

Audio storage builds sanitised paths but no real file is written. When real files are added, there will be no signed URL expiry, no tenant isolation at the storage layer, and no access control model for the binary content.

**Must define before real consultation recordings are processed.**

### Risk 12 — No CORS or Frontend Security Configuration
**Severity: Medium before frontend**

FastAPI default CORS accepts all origins. A dashboard frontend requires an explicit allowlist. Without it, any origin can make credentialed requests.

**Must configure before any browser client integration.**

### Risk 13 — No Production Logging or Observability Policy
**Severity: Low-Medium**

`logger.exception(...)` is used correctly in route catch-all blocks. However, there is no structured logging format, no per-request correlation ID, no PHI field redaction policy in log messages, and no aggregation target. PHI could appear in stack traces if exception messages include patient data.

**Should define before production.**

---

## I) Refactor Recommendations

### Must Do Before Real Pilot

| Item | Reason |
|---|---|
| Replace header-trust auth with HMAC or JWT on at least one path | Current model is trivially bypassable. Minimum: HMAC on Vapi/n8n webhook routes. Even a static per-clinic API key is significantly safer than open headers. |
| Add DB membership check to `get_auth_context` | `clinic_id` from header must be validated against `clinic_users` table. Without this, cross-tenant access by fabricated headers is possible. |
| Implement HMAC signature verification for Vapi/n8n webhooks | Replace string-equality check with `hmac.compare_digest(expected_hmac, computed_hmac)` over the full request body. |
| Define and document machine auth header injection strategy | Decide: proxy injection, Vapi/n8n explicit config, or HMAC replacement. Before connecting any real external service. |
| Write PHI retention/deletion policy | Required for GDPR/DSGVO compliance before any real patient data enters the system. |
| Add `logger.warning(...)` in `safe_record_audit_event` on failure | Silent audit failures are a compliance risk. A single log line makes them observable without changing the never-raise contract. |

### Should Do Before Frontend

| Item | Reason |
|---|---|
| Audit all API response models for PHI leakage | `notes` and `raw_payload` returned in full CRUD responses; confirm policy and document it. |
| Configure CORS allowlist in `main.py` | FastAPI default accepts all origins. |
| Add rate limiting middleware | Availability and Vapi tool routes can be called many times per phone call. |
| Centralise enum constants into `backend/app/core/enums.py` | Status strings, role strings, scope strings, and source strings are duplicated across schema, repos, and Pydantic schemas. |
| Run `alembic upgrade head` against local Docker PostgreSQL | Validates migration correctness before staging deployment. |

### Can Wait

| Item | Reason |
|---|---|
| Shared `conftest.py` for test fixtures | 1193 tests run in 1.76 seconds. Fixture duplication is a maintenance cost, not a correctness risk. Address when count approaches 1500. |
| Real DB integration tests | Per project architecture rules. Plan for a separate test sprint before production. |
| Sub-routers for large route files | `consultations.py` (10 routes) is readable. Address if any file exceeds 15 endpoints. |
| Full OAuth2/JWT middleware | Milestone 9 per roadmap. Building now without a real identity provider produces placeholder code. |
| PDF/Excel export | Milestone 6 per roadmap. Timeline service is the integration point when ready. |

### Avoid for Now

| Item | Reason |
|---|---|
| Real LLM integration inside `summary_builder.py` | The marker-extraction approach is safe and deterministic. A real LLM adapter should be a separate module wrapping the builder, not a change to the builder itself. |
| Breaking up `schema.sql` into per-table files | Single idempotent DDL is correct for dev. Splitting creates ordering dependencies with no benefit. |
| Refactoring completed Sprint 1–4 modules | All 1193 tests pass. Touching stable code before pilots is unnecessary churn. |
| Adding WhatsApp routes now | Milestone 7 per roadmap. No business requirement yet. |

---

## J) Next Milestone Options

| Option | Assessment |
|---|---|
| **Module 45 — Local PostgreSQL Docker + Migration Runner Smoke Test** | **Highest priority.** Every other real integration (Vapi, n8n, file storage, transcription, auth) depends on a working database. Low code risk, closes the largest remaining infrastructure gap. |
| Module 45 — Webhook Signature Verification Foundation | Important security fix. Can be done before or after DB setup. Does not require real PostgreSQL. |
| Module 45 — Real Auth/JWT Foundation | High security value but requires identity provider planning (no real auth server exists yet). Premature without a defined provider. |
| Module 45 — User-to-Clinic Membership Enforcement | Important but depends on real DB — can't be tested without PostgreSQL. |
| Module 45 — Secrets Management Review | Documentation + environment setup. Prerequisite for any real deployment but no code changes needed now. |
| Module 45 — Vapi/n8n Real Setup Guide | Documentation only. Blocked by: no real DB, no HMAC, no defined machine auth strategy. |
| Module 45 — File Storage Foundation | Needed for real consultations. Lower priority than DB. |
| Module 45 — Real Transcription Provider Adapter | Interface is clean, implementation is straightforward. Blocked by real DB and real file storage. |
| Module 45 — Frontend Dashboard Foundation | Blocked by: CORS, auth model, PHI field audit, no browser-compatible auth mechanism. |

### Why Local PostgreSQL + Migration Runner Wins

Every integration work item on this list eventually requires the database:
- Webhook HMAC verification writes nothing to the DB, but the audit events it validates depend on a real pool.
- User-to-clinic membership enforcement requires querying `clinic_users`.
- File storage integration writes audio file references to `consultation_sessions`.
- Real transcription writes transcript text to `consultation_sessions`.
- Frontend integration requires all routes to function end-to-end against real data.

`alembic upgrade head` against a real local PostgreSQL is a 30-minute setup task that validates the migration, confirms pgcrypto availability, and provides the foundation for every subsequent integration. It is low-risk (no production logic changes) and has no blockers other than Docker being available locally.

---

## K) Recommended Next Module

**Sprint 5 / Module 45 — Local PostgreSQL Docker + Migration Runner Smoke Test**

**Scope (do not implement yet — this is the documented plan):**
- Create `docker-compose.yml` (or `docker-compose.dev.yml`) with a `postgres:16` service configured for the PraxisMed database.
- Document the `DATABASE_URL` format in a `.env.example` file.
- Run `alembic upgrade head` against the local Docker PostgreSQL instance.
- Confirm: all 11 tables created, `pgcrypto` available, `alembic_version` table populated, downgrade/upgrade round-trip works.
- Write a minimal smoke test script (not a pytest test) that connects via asyncpg, inserts a clinic row, and reads it back — confirming the pool lifecycle and parameterised SQL work against a real database.
- Do not remove or replace `schema.sql`.
- Do not modify any existing test.
- Commit: `Sprint 5 / Module 45 — Local PostgreSQL Docker + migration runner smoke test`

**Rationale:**
Before real Vapi/n8n, external AI providers, or frontend work, the backend should prove it can initialize a real local PostgreSQL database using the migration foundation built in Sprint 4. This validates schema deployment without jumping straight into production integrations.

See `NEXT_MODULE.md` for the placeholder.
