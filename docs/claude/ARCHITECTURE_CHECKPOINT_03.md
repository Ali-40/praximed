# Architecture Checkpoint 03 — Access Control and Integration Route Review
**Date:** 2026-07-01
**Scope:** Modules 35–40, Sprint 3 complete
**Purpose:** Review access control layers, machine/human auth guards, integration route security, and readiness for real Vapi, n8n, database, and external AI integration. Identify risks before pilots begin.

---

## A) Current System Summary

### What PraxisMed Can Do After Modules 1–40

In addition to all Sprint 1 and Sprint 2 capabilities, PraxisMed now has a **complete access control layer** covering all route groups:

1. **Clinical workflow routes wired to service modules (Module 35)** — audio attachment, manual transcript entry, clinical summary draft generation, review package building, doctor approval and rejection, and patient timeline reports are now accessible through REST endpoints that delegate to the service layer rather than calling repositories directly.

2. **Header-based human auth context (Module 36)** — every request to human-facing routes carries `X-User-Id`, `X-Clinic-Id`, and `X-User-Role` headers. These are parsed into an `AuthContext` dataclass and validated before any route logic runs.

3. **Tenant guards on all PHI routes (Modules 37–38)** — patients, consultations, clinical workflows, appointment requests, and notifications all require `AuthContext`. `clinic_id` in the request body or path is validated against the caller's `X-Clinic-Id`. Staff-level and clinical-level role tiers are enforced per route group.

4. **Machine auth foundation (Module 39)** — a parallel `MachineAuthContext` dataclass handles machine-to-machine access using `X-Service-Name`, `X-Service-Clinic-Id`, and `X-Service-Scopes` headers. Service name, scope, and clinic_id are all validated independently.

5. **Machine guards on all integration routes (Module 40)** — availability, Vapi tool, Vapi webhook, and n8n calendar sync routes all require a valid `MachineAuthContext` with the correct service and scope before any business logic or database access occurs.

### Route Group Summary

| Route Group | Path Prefix | Count | Auth Type |
|---|---|---|---|
| Health | `/health` | 2 | None (intentional) |
| Availability | `/calendar/availability` | 2 | Machine (availability:read) |
| Vapi tools | `/vapi/tools` | 3 | Machine (vapi:tool) |
| Vapi webhooks | `/webhooks/vapi` | 1 | Machine (vapi:webhook) |
| n8n calendar sync | `/webhooks/n8n` | 1 | Machine (calendar:sync) |
| Appointment requests | `/appointment-requests` | 7 | Human (staff) |
| Notifications | `/notifications` | 5 | Human (staff) |
| Patients | `/patients` | 7 | Human (staff) |
| Consultations | `/consultations` | 10 | Human (clinical) |
| Clinical workflows | `/clinical-workflows` | 7 | Human (clinical) |

**Total routes: 45 human-addressable endpoints (2 unprotected health probes, 43 protected).**

### What Remains Placeholder-Only

| Component | Status |
|---|---|
| Auth verification | Header-trust only — no JWT signature, no HMAC, no DB membership check |
| Webhook signatures | String match for Vapi/n8n secrets; no HMAC-SHA256 |
| Audio file I/O | Path built and stored; no real file written or read |
| Transcription provider | Mock adapter only; no Whisper/OpenAI/AssemblyAI call |
| LLM clinical summary | Regex/marker extraction only; no AI API call |
| Real database | All 1083 tests use AsyncMock pools; no live PostgreSQL |
| Migration runner | `schema.sql` is idempotent DDL only; no Alembic or version tracking |
| Audit log writes | Table defined in `schema.sql`; no code writes to it |

---

## B) Sprint 3 Module Inventory

| # | Module Name | Key Files | Purpose | Tests |
|---|---|---|---|---|
| 35 | Clinical workflow API routes | `schemas/clinical_workflows.py`, `routes/clinical_workflows.py` | 7 endpoints at `/clinical-workflows/` prefix wiring audio, transcript, summary, review, approve, reject, timeline to service modules | 47/47 |
| 36 | Auth and tenant access foundation | `core/auth_context.py`, `api/dependencies/auth.py` | `AuthContext` dataclass; `build_auth_context_from_headers`; `ensure_same_clinic`; `ensure_role_allowed`; `require_staff_clinic_access`; `require_clinical_clinic_access` | 34/34 |
| 37 | Tenant guards on clinical PHI routes | `routes/patients.py`, `routes/consultations.py`, `routes/clinical_workflows.py` (all updated) | Applied `get_auth_context` + `require_*_clinic_access` to patients (staff), consultations (clinical), clinical workflows (clinical) | 17/17 |
| 38 | Tenant guards on appointment/notification routes | `routes/appointment_requests.py`, `routes/notifications.py` (both updated) | Applied staff-level tenant guards to all appointment request and notification endpoints | 12/12 |
| 39 | Machine access foundation | `core/machine_auth.py`, `api/dependencies/machine_auth.py` | `MachineAuthContext` dataclass; `build_machine_auth_context_from_headers`; scope/service/clinic validation; `require_vapi_tool_access`, `require_vapi_webhook_access`, `require_n8n_calendar_sync_access`, `require_availability_read_access` | 45/45 |
| 40 | Machine guards on integration routes | `routes/availability.py`, `routes/vapi_tools.py`, `routes/vapi_webhooks.py`, `routes/calendar_webhooks.py` (all updated) | Applied `get_machine_auth_context` + scoped `require_*_access` helpers to all machine-facing routes | 20/20 |

**Sprint 3 total new tests: 175. Full suite after Sprint 3: 1083/1083 passed.**

---

## C) Access Control Map

### Human AuthContext — Staff-Level Access
Roles allowed: `owner`, `admin`, `doctor`, `staff`
Headers required: `X-User-Id`, `X-Clinic-Id`, `X-User-Role`
Enforcement: `require_staff_clinic_access(requested_clinic_id=..., auth_context=auth)`

| Route Group | Endpoints |
|---|---|
| Patients | `POST /patients`, `GET /patients`, `POST /patients/upsert-by-external-id`, `GET /patients/by-external-id/{id}`, `GET /patients/{id}`, `PATCH /patients/{id}`, `POST /patients/{id}/archive` |
| Appointment requests | `POST /appointment-requests`, `GET /appointment-requests`, `GET /appointment-requests/{id}`, `PATCH /appointment-requests/{id}/status`, `PATCH /appointment-requests/{id}/assign`, `POST /appointment-requests/{id}/callback-needed`, `POST /appointment-requests/{id}/archive` |
| Notifications | `POST /notifications`, `GET /notifications`, `GET /notifications/{id}`, `POST /notifications/{id}/read`, `POST /notifications/{id}/cancel` |

### Human AuthContext — Clinical-Level Access
Roles allowed: `owner`, `admin`, `doctor`
Headers required: `X-User-Id`, `X-Clinic-Id`, `X-User-Role`
Enforcement: `require_clinical_clinic_access(requested_clinic_id=..., auth_context=auth)`

| Route Group | Endpoints |
|---|---|
| Consultations | `POST /consultations`, `GET /consultations`, `GET /consultations/{id}`, `PATCH /consultations/{id}/status`, `POST /consultations/{id}/audio`, `POST /consultations/{id}/transcript`, `POST /consultations/{id}/draft-summary`, `POST /consultations/{id}/approve`, `POST /consultations/{id}/reject`, `POST /consultations/{id}/archive` |
| Clinical workflows | `POST /clinical-workflows/consultations/{id}/audio-reference`, `POST /clinical-workflows/consultations/{id}/manual-transcript`, `POST /clinical-workflows/consultations/{id}/clinical-summary-draft`, `POST /clinical-workflows/consultations/{id}/review-package`, `POST /clinical-workflows/consultations/{id}/approve-summary`, `POST /clinical-workflows/consultations/{id}/reject-summary`, `GET /clinical-workflows/patients/{id}/timeline-report` |

### MachineAuthContext — Availability Read
Allowed services: `vapi`, `internal`, `system`, `dashboard`
Required scope: `availability:read`
Headers required: `X-Service-Name`, `X-Service-Clinic-Id`, `X-Service-Scopes`
Clinic_id source: `body.clinic_ref`

| Route | Enforcement helper |
|---|---|
| `POST /calendar/availability/check` | `require_availability_read_access` |
| `POST /calendar/availability/suggest` | `require_availability_read_access` |

### MachineAuthContext — Vapi Tool Access
Allowed services: `vapi`, `internal`, `system`
Required scope: `vapi:tool`
Clinic_id source: `body.clinic_ref`

| Route | Enforcement helper |
|---|---|
| `POST /vapi/tools/check-availability` | `require_vapi_tool_access` |
| `POST /vapi/tools/suggest-slots` | `require_vapi_tool_access` |
| `POST /vapi/tools/capture-appointment-request` | `require_vapi_tool_access` |

### MachineAuthContext — Vapi Webhook Access
Allowed services: `vapi`, `internal`, `system`
Required scope: `vapi:webhook`
Clinic_id source: `payload.get("clinic_id")` (Optional — None bypasses clinic check)

| Route | Enforcement helper |
|---|---|
| `POST /webhooks/vapi/call-event` | `require_vapi_webhook_access` |

### MachineAuthContext — Calendar Sync Access
Allowed services: `n8n`, `internal`, `system`
Required scope: `calendar:sync`
Clinic_id source: `payload.get("clinic_id")`

| Route | Enforcement helper |
|---|---|
| `POST /webhooks/n8n/calendar-sync` | `require_n8n_calendar_sync_access` |

### Intentionally Unprotected
| Route | Reason |
|---|---|
| `GET /health` | Liveness probe — must be accessible without credentials by load balancers and container orchestrators |
| `GET /health/ready` | Readiness probe — same reason |

---

## D) Safety and PHI Review

| Data Category | Route Surface | Protection Status |
|---|---|---|
| Patient identity (name, DOB, phone, email, insurance) | `/patients/*` | Protected: staff-level human auth + clinic_id check. Notes and raw_payload excluded from timeline report output. |
| Patient contact data | `/patients/*` | Protected: same as above. No API endpoint currently exposes notes or raw_payload in a stripped response — they are included in full CRUD responses. **Risk: field-level access control is not enforced on CRUD detail routes.** |
| Consultation transcripts | `/consultations/*`, `/clinical-workflows/*` | Protected: clinical-level human auth + clinic_id check. |
| Draft summaries | `/clinical-workflows/consultations/{id}/clinical-summary-draft` | Protected: always marked `doctor_review_required=True`, `no_diagnosis_generated=True`, `no_treatment_advice_generated=True`. Draft summaries hidden in timeline unless `include_drafts=True`. |
| Approved summaries | `/clinical-workflows/consultations/{id}/approve-summary` | Protected: only written when doctor explicitly approves with `approved_by_user_id`. DB compound CHECK prevents `approved_at` being null when status is `approved`. |
| Timeline reports | `/clinical-workflows/patients/{id}/timeline-report` | Protected: clinical-level auth; drafts hidden by default; `notes` and `raw_payload` excluded from patient record in report. |
| Appointment requests | `/appointment-requests/*` | Protected: staff-level human auth + clinic_id check. |
| Internal notifications | `/notifications/*` | Protected: staff-level human auth + clinic_id check. |
| Vapi call events | `/webhooks/vapi/call-event` | Protected: machine vapi:webhook scope required. Existing string-match secret check (`X-PraxisMed-Vapi-Secret`) preserved. No HMAC. |
| Calendar availability data | `/calendar/availability/*`, `/vapi/tools/*` | Protected: machine availability:read or vapi:tool scope required. |

**Safety invariants still holding from prior checkpoints:**
- No auto-diagnosis: `summary_builder` has no `diagnosis` key; `validate_clinical_summary_draft` rejects any draft that contains one.
- No auto-treatment advice: `no_treatment_advice_generated=True` is a required field on all drafts.
- No auto-confirmed appointments: `vapi_appointment_capture` creates `status='new'`, `action_required=True`; staff review is required.
- Availability checked before slots are offered: `vapi_tools` routes call `availability_engine` before returning a slot to the caller.

---

## E) Integration Readiness Review

### Real PostgreSQL Database

| Item | Status | Blockers |
|---|---|---|
| Schema DDL | Ready — idempotent `schema.sql` with all tables | No migration runner; manual `psql` apply only |
| asyncpg pool | Ready — lifecycle tied to FastAPI startup/shutdown | None |
| All repos | Ready — parameterised SQL, no ORM coupling | No real integration tests; constraint violations not exercised |
| Migration runner | Not ready | No Alembic; no version tracking; no rollback path |

**Verdict: Can connect to a local PostgreSQL instance today with `psql -f schema.sql`. Not ready for staged schema evolution.**

### Real Vapi Setup

| Item | Status | Blockers |
|---|---|---|
| Vapi tool routes | Ready structurally | Headers must be configured in Vapi assistant setup; currently no HMAC secret on tool calls |
| Vapi webhook route | Ready structurally | String-match secret only; no HMAC-SHA256 verification |
| Machine auth on Vapi routes | In place | Headers must be injected by real Vapi — Vapi does not natively add `X-Service-Name` etc.; a proxy or Vapi function-call configuration would need to set them |
| Call log persistence | Ready | Requires real PostgreSQL pool |
| Appointment capture | Ready | Requires real PostgreSQL pool + config loader with real clinic config files |

**Verdict: Not pilot-ready. Machine auth headers are internal conventions; real Vapi sends its own headers. Either configure Vapi to pass expected headers, introduce a thin proxy layer, or replace the header-trust model with HMAC verification before connecting real Vapi traffic.**

### Real n8n Setup

| Item | Status | Blockers |
|---|---|---|
| n8n calendar sync webhook | Ready structurally | Machine auth headers must be added to n8n HTTP request node; n8n does not auto-send them |
| Webhook secret | String-match in place | No HMAC; secret is in env var only |
| Calendar block persistence | Ready | Requires real PostgreSQL pool |

**Verdict: Similar situation to Vapi. n8n can be configured to send custom headers; the machine auth model is compatible but must be explicitly set up in each n8n workflow.**

### Real File Storage (Audio)

| Item | Status | Blockers |
|---|---|---|
| Audio path builder | Complete — sanitises filenames, prevents traversal | No real I/O |
| Audio attach to consultation | Complete | Writes path only; binary data goes nowhere |
| Storage backend | None | No S3, GCS, or local disk adapter |

**Verdict: Not ready. Implement a local-disk adapter (for dev) and an S3-compatible interface (for staging) before handling real consultation recordings.**

### Real Transcription Provider

| Item | Status | Blockers |
|---|---|---|
| `TranscriptionAdapter` Protocol | Complete | No real implementation |
| Mock adapter | Complete | For tests only |
| OpenAI Whisper / AssemblyAI adapter | Not implemented | Adapter interface is the extension point; real implementation is one module away |

**Verdict: One module away. The `TranscriptionAdapter` Protocol is clean; a real adapter just implements `transcribe_audio_reference`.**

### Real LLM Clinical Summary Provider

| Item | Status | Blockers |
|---|---|---|
| `summary_builder.py` | Regex/marker extraction | Works only if transcript uses exact structured markers |
| LLM adapter interface | Not defined | `build_clinical_summary_draft` accepts a `source` param — extension point exists |
| Claude API integration | Not implemented | Would require prompt design, safety validation, and explicit doctor-review flow |

**Verdict: Not ready for real conversational transcripts. The regex approach produces mostly "missing information" entries for natural speech. A real LLM adapter is needed before clinical summary generation is useful.**

### Frontend / Dashboard

| Item | Status | Blockers |
|---|---|---|
| API surface | Complete — 45 REST endpoints | No auth token mechanism usable by a browser; header-based auth is not browser-native |
| CORS policy | Not configured | FastAPI default; all origins accepted |
| Response models | Pydantic v2 — clean JSON | Some PHI-adjacent fields (patient notes, raw_payload) are returned by CRUD routes without field-level access control |
| Auth for browser clients | Not ready | Header-based auth requires custom browser logic; a JWT/session-cookie mechanism is needed for frontend use |

**Verdict: Not ready. The API is complete but frontend-incompatible auth is a blocker.**

---

## F) Remaining Risks

### Risk 1 — Header-Trust Auth Is an Internal Placeholder
**Severity: Critical before any external traffic**

Both `AuthContext` and `MachineAuthContext` are built entirely from HTTP headers. Any caller that sends the correct header values gains access. There is no JWT signature, no HMAC, no database membership lookup, and no session validation.

- A malicious caller can send `X-User-Role: doctor` and `X-Clinic-Id: any-clinic` to access clinical PHI routes.
- A malicious caller can send `X-Service-Name: vapi` and `X-Service-Scopes: vapi:tool` to call Vapi tool routes.

**Must address before any real pilot traffic reaches the system.**

### Risk 2 — No User-to-Clinic Database Membership Check
**Severity: High**

`clinic_id` in `AuthContext` is validated against `body.clinic_id` (same-clinic check), but the `clinic_id` itself is not verified against any database. There is no check that the user identified by `X-User-Id` actually belongs to the clinic identified by `X-Clinic-Id`. A caller that fabricates both headers passes all current guards.

**Must address before real user-facing deployment.**

### Risk 3 — No Webhook Signature Verification (HMAC)
**Severity: High before real Vapi/n8n traffic**

Both the Vapi webhook (`X-PraxisMed-Vapi-Secret`) and the n8n webhook (`X-PraxisMed-Webhook-Secret`) use simple string equality checks against an environment variable. This is better than nothing but is not HMAC-based.

Real Vapi and n8n both support configurable webhook signatures. Without HMAC verification, any caller that guesses or intercepts the secret string can send arbitrary webhook payloads.

**Must address before connecting real Vapi/n8n webhooks.**

### Risk 4 — Machine Auth Headers Are Internal Conventions
**Severity: High before Vapi/n8n integration**

`X-Service-Name`, `X-Service-Clinic-Id`, and `X-Service-Scopes` are internal header names not natively sent by Vapi or n8n. For real integration, either:
- A reverse proxy or API gateway injects these headers after validating HMAC.
- Vapi/n8n HTTP request nodes are explicitly configured to include them.
- The machine auth model is replaced by HMAC/JWT before pilot.

**Must define an integration strategy before connecting real external services.**

### Risk 5 — No Database Migration Runner
**Severity: High before staging/production**

`schema.sql` is 437+ lines of idempotent DDL. There is no Alembic, no migration history, no rollback path, and no schema version tracking. Adding a new column to an existing table requires a manual `ALTER TABLE` with no record of when or why it was applied.

**Must address before staging deployment.**

### Risk 6 — Audit Log Table Exists But Is Never Written
**Severity: Medium**

The `audit_log` table has existed since Module 3. As of Module 40, no code writes to it. Patient creation, patient archive, consultation approval, consultation rejection, and appointment request mutations are all compliance-relevant actions with no immutable trail.

**Should address before handling any real patient data.**

### Risk 7 — PHI in Full CRUD API Responses Without Field-Level Control
**Severity: Medium**

The `GET /patients/{id}` and `GET /patients` endpoints return the full patient record, including `notes` (free text) and `raw_payload` (JSONB). These fields are excluded from the timeline report but are included in direct patient CRUD responses. Any caller with valid staff auth can read all patient notes for their clinic with no additional access check.

**Should audit all response models before fronting with a dashboard.**

### Risk 8 — No Request Rate Limiting
**Severity: Medium**

No rate limiting middleware exists. Machine routes (availability check, Vapi tools) and human routes (patient list, consultation list) are all unbounded. A misconfigured Vapi assistant could flood the availability routes.

**Should add basic rate limiting before pilot traffic.**

### Risk 9 — No Secrets Management Review
**Severity: Medium**

Webhook secrets are read from environment variables. There is no secrets manager (Vault, AWS Secrets Manager, etc.), no secret rotation policy, and no audit of which secrets exist. Clinic config files store non-secret configuration only (per project rules), but the boundary between config and secret has not been formally audited.

**Should document and implement before production.**

### Risk 10 — No Real File Storage Security Model
**Severity: Medium**

Audio files will contain PHI (spoken consultations). The current path builder produces sanitised local paths, but there is no access control model for the storage layer — no signed URLs, no expiry, no tenant isolation at the storage level.

**Must define before real audio files are processed.**

### Risk 11 — No PHI Retention / Deletion Policy
**Severity: High for GDPR/DSGVO compliance**

Austrian private medical data is subject to GDPR and national health data regulations. There is no retention period enforcement, no patient data deletion workflow, and no right-to-erasure implementation. Consultation transcripts and summaries are stored indefinitely.

**Must define and implement before any real patient data is processed.**

### Risk 12 — No CORS or Frontend Security Configuration
**Severity: Medium before frontend**

FastAPI's default CORS policy accepts all origins. A dashboard frontend will require an explicit allowlist. Without it, any origin can make credentialed requests.

**Must configure before any frontend integration.**

### Risk 13 — No Production Logging or Observability Policy
**Severity: Low-Medium**

`logger.exception(...)` is used in route catch-all blocks, which is correct for error surfaces. However, there is no structured logging format, no correlation ID per request, no log redaction for PHI fields, and no aggregation target (no ELK, Datadog, Loki). PHI could appear in stack traces if exception messages include patient data.

**Should define before production.**

---

## G) Refactor Recommendations

### Must Do Before Real Pilot Traffic

| Item | Reason |
|---|---|
| Replace header-trust auth with HMAC or JWT for at least one path | Current model is completely bypassable by any caller. At minimum: verify Vapi HMAC signatures on webhook routes. Even a static API key → clinic_id mapping is significantly safer. |
| Add DB membership check to `get_auth_context` | `clinic_id` from header must be verified against `clinic_users` table. Without this, cross-tenant access is trivially possible. |
| Implement HMAC signature verification for Vapi and n8n webhooks | Replace string-equality secret check with `hmac.compare_digest(expected, provided)` on the full request body. |
| Define integration strategy for `X-Service-*` headers | Decide: proxy injection vs. explicit Vapi/n8n config vs. HMAC replacement. Document and implement before connecting real traffic. |
| Write PHI retention/deletion policy | Required for GDPR/DSGVO compliance before any real patient data is processed. |

### Should Do Before Frontend

| Item | Reason |
|---|---|
| Introduce Alembic or a lightweight migration runner | Schema changes without version tracking are unsafe for staging/production. |
| Create `audit_log_repo.py` and write to it | Patient creation, consultation approval/rejection are compliance-relevant; the table exists and should be used. |
| Audit all API response models for PHI leakage | Patient `notes` and `raw_payload` are currently returned in full CRUD responses; confirm this is intentional and document the policy. |
| Configure CORS allowlist | FastAPI default accepts all origins; this must be restricted before any browser client is used. |
| Add rate limiting middleware | At minimum for availability and Vapi tool routes that may be called in rapid succession during a phone call. |
| Centralise enum constants into `backend/app/core/enums.py` | Status strings, role strings, scope strings, and source strings are defined in three places each (schema CHECK, repo guards, Pydantic literals). Now 10+ repos and schema files are affected. |

### Can Wait

| Item | Reason |
|---|---|
| Shared `conftest.py` for test fixtures | 1083 tests run in ~1.6 seconds. Fixture duplication is a maintenance cost, not a correctness risk. Address when test count approaches 1500. |
| Real DB integration tests | Per project architecture rules. Plan for a separate test sprint before production. |
| Sub-routers for large route files | `consultations.py` (10 routes), `patients.py` (7 routes) are readable. Address if any file exceeds 15 endpoints. |
| Full OAuth2 / JWT middleware | Milestone 9 per roadmap. Building it now without a real identity provider produces placeholder code. |
| PDF export / Excel export | Milestone 6 per roadmap. Timeline report is the integration point when ready. |

### Avoid for Now

| Item | Reason |
|---|---|
| Real LLM integration inside `summary_builder.py` | The marker-extraction approach is safe and deterministic. LLM integration should be a separate adapter module that wraps the builder, not a change to the builder itself. |
| Breaking up `schema.sql` into per-table files | Single idempotent DDL file is correct for dev. Splitting creates ordering dependencies with no benefit at this stage. |
| Refactoring completed Sprint 1–2 modules | All 1083 tests pass. Touching stable code before pilots is unnecessary churn. |
| Adding WhatsApp routes now | Milestone 7 per roadmap. No business requirement yet. |

---

## H) Next Milestone Options

| Option | Description | Assessment |
|---|---|---|
| Module 41 — Database migration foundation | Alembic setup, initial migration from schema.sql | **Critical path**: every other real integration depends on a safe schema evolution story |
| Module 41 — Audit logging integration | `audit_log_repo.py` + write calls on key mutations | Important for compliance; low complexity; requires real DB first |
| Module 41 — Real auth / JWT foundation | JWT decode + DB membership check | Highest security value but requires real identity provider planning |
| Module 41 — Webhook HMAC signature verification | Replace string-equality secret with HMAC-SHA256 | Targeted security fix; can be done standalone; relatively small scope |
| Module 41 — Real PostgreSQL Docker / local integration | `docker-compose.yml` + `psql -f schema.sql` smoke test | Enables all other integration work; prerequisite for real integration tests |
| Module 41 — Vapi / n8n real setup | Connect real Vapi assistant to tool routes | Not safe until auth/webhook HMAC issues are resolved |
| Module 41 — File storage foundation | Local-disk + S3-interface adapter for audio | Blocks real consultations; medium complexity |
| Module 41 — Real transcription adapter | Whisper/OpenAI adapter implementing `TranscriptionAdapter` Protocol | Blocks real consultation recordings; interface is already clean |
| Module 41 — Frontend dashboard foundation | Next.js project scaffold + first page | Blocked by: CORS config, auth model suitable for browsers, PHI field audit |

### Why Database Migration Foundation Wins

Every other integration item on this list eventually requires changing the database schema. Without a migration runner:
- Adding a `deleted_at` column for soft-delete/retention compliance requires a manual ALTER TABLE with no record.
- Adding audit triggers, adding a webhook secrets table, adding user session tokens — all require schema changes.
- A staging deployment with real data cannot safely receive schema changes via manual SQL.

Alembic setup is a one-time foundation task with low code risk (no production logic changes), and it unblocks all subsequent integration work. It should be the first module of Sprint 4.

---

## I) Recommended Next Module

**Sprint 4 / Module 41 — Database Migration Foundation**

**Scope:**
- Install Alembic as a dev dependency.
- Configure `alembic.ini` and `env.py` to point to the PraxisMed database URL (from environment variable, not hardcoded).
- Generate an initial migration from the current `schema.sql` state — all tables as they exist today.
- Verify the migration is reversible (downgrade script either drops tables or is documented as irreversible with a safety comment).
- Add a `migrations/` directory alongside `backend/`.
- Write tests that verify: (a) the migration file parses without error, (b) Alembic's version tracking works against a real SQLite or in-memory PostgreSQL fixture.
- Do not remove or replace `schema.sql` — keep it as a reference. The migration is the new source of truth going forward.

**Rationale:**
This closes the largest infrastructure gap before any staging, pilot, or real integration work. It is low-risk (no production logic changes), prerequisite-free, and immediately enables all other integration-readiness items.

See `NEXT_MODULE.md` for the placeholder.
