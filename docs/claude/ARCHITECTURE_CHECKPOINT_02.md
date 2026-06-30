# Architecture Checkpoint 02 — Clinical Documentation Foundation Review
**Date:** 2026-06-30
**Scope:** Modules 24–34, Sprint 2 complete
**Purpose:** Review backend architecture after the Clinical Documentation Engine milestone before starting Sprint 3.

---

## A) Current System Summary

### What PraxisMed Can Currently Do After Modules 1–34

In addition to the Sprint 1 capabilities documented in Checkpoint 01, PraxisMed now has a complete **clinical documentation foundation**:

1. **Patient registry** — create, update, archive, and look up patients by internal ID or external EMR ID. Full-text search on name. Upsert by external ID for EMR sync.
2. **Consultation session lifecycle** — create sessions linked to a patient and optional doctor; transition through a defined status lifecycle (created → recording → audio_uploaded → transcribing → transcribed → draft_ready → approved / rejected / archived).
3. **Audio reference attachment** — validate file metadata (format, size), build sanitised storage paths, and attach the audio reference to a consultation session (placeholder — no real file I/O).
4. **Transcription adapter interface** — provider-agnostic interface for routing consultation audio to a transcription service (mock, openai, whisper, vapi, manual). Normalises provider output; saves transcript text to the consultation session.
5. **Clinical summary draft generation** — deterministic, regex-based extraction of structured markers from transcript text into a JSON draft summary. Never invents clinical content. Every draft is marked `doctor_review_required=True`, `no_diagnosis_generated=True`, `no_treatment_advice_generated=True`.
6. **Doctor review workflow** — validates draft summaries, builds review packages with explicit safety instructions, routes approve/reject decisions to the consultation repository. Never auto-approves AI output.
7. **Patient timeline report** — aggregates a patient's consultation history into a chronological report. Hides draft summaries by default. Normalised patient record does not expose notes or raw_payload. Includes safety flags on every report.

### Major Business Flows Implemented

| Flow | Status |
|---|---|
| Patient create / update / archive / search | Complete |
| Consultation session create + status lifecycle | Complete |
| Audio reference attach to consultation | Complete (placeholder path only) |
| Transcription adapter interface + mock adapter | Complete |
| Transcript save to consultation session | Complete |
| Clinical summary draft generation from transcript | Complete |
| Doctor review workflow (approve + reject) | Complete |
| Approved / rejected summary saved to consultation | Complete |
| Patient timeline report (chronological, drafts hidden) | Complete |

### Parts That Are Still Placeholder-Only

| Component | Status |
|---|---|
| Audio file I/O | Stub — builds path and attaches reference; no actual file read/write |
| Transcription provider | Mock adapter only; no real Whisper/OpenAI/AssemblyAI call |
| Clinical summary LLM | Deterministic marker extraction only; no AI/LLM call |
| File storage backend | No S3, GCS, or local storage integration |
| Real database | All tests use AsyncMock pools; no live PostgreSQL connection |
| Authentication | No auth middleware; all routes open |
| Audit log writes | `audit_log` table exists in schema; no code writes to it |

---

## B) Sprint 2 Module Inventory

| # | Module Name | Key Files | Purpose | Tests |
|---|---|---|---|---|
| 24 | Patient schema contract | `db/schema.sql` | `patients` table: 19 columns, 7 indexes, CHECK constraints on status and gender | 223/223 |
| 25 | Patient repository | `db/repositories/patient_repo.py` | create, upsert-by-external-id, get-by-id, get-by-external-id, list (ILIKE search), update (COALESCE), archive | 21/21 |
| 26 | Patient API routes | `schemas/patients.py`, `routes/patients.py` | 7 REST endpoints; `/by-external-id/{id}` declared before `/{id}` to prevent path collision | 34/34 |
| 27 | Consultation session schema contract | `db/schema.sql` | `consultation_sessions` table: 19 columns, 7 indexes, 3 CHECK constraints, 1 compound timing CHECK | 264/264 |
| 28 | Consultation session repository | `db/repositories/consultation_repo.py` | Full lifecycle: create, get, list, update-status, attach-audio, save-transcript, save-draft, approve, reject, archive | 32/32 |
| 29 | Consultation session API routes | `schemas/consultations.py`, `routes/consultations.py` | 10 REST endpoints covering full session lifecycle | 39/39 |
| 30 | Audio upload placeholder service | `modules/audio/audio_storage.py` | Metadata validation, filename sanitisation, path building, audio reference attachment | 23/23 |
| 31 | Transcription adapter interface | `modules/transcription/transcription_service.py` | `TranscriptionAdapter` Protocol; validate request/provider; normalise result; run adapter; save to consultation | 27/27 |
| 32 | Clinical summary draft generator | `modules/clinical_summary/summary_builder.py` | Deterministic marker extraction → structured JSON draft; safety flags; validate draft; save to consultation | 41/41 |
| 33 | Doctor review workflow | `modules/clinical_summary/review_workflow.py` | Validate draft for review; build review package; validate approved summary; approve/reject via repo | 33/33 |
| 34 | Patient timeline report service | `modules/patient_timeline/timeline_report.py` | Fetch patient + consultations; detect summary status; sort entries; build chronological report with safety flags | 43/43 |

**Total tests as of Module 34: 908/908**

---

## C) Clinical Documentation Flow Map

```
1. Patient Record
   └── patient_repo.create_patient / upsert_patient_by_external_id
           └── patients table (PostgreSQL)

2. Consultation Session Created
   └── consultation_repo.create_consultation_session
           └── consultation_sessions table
                   status = "created"
                   approval_status = "not_ready"

3. Audio Reference Attachment
   └── audio_storage.validate_audio_upload_metadata
           └── audio_storage.sanitize_audio_filename
                   └── audio_storage.build_consultation_audio_path
                           └── audio_storage.attach_audio_reference_to_consultation
                                   └── consultation_repo.attach_audio_to_session
                                           └── consultation_sessions.audio_file_path set
                                                   status → "audio_uploaded"

4. Transcription Adapter Interface
   └── transcription_service.validate_transcription_request
           └── transcription_service.validate_provider_name
                   └── transcription_service.run_transcription_adapter
                           └── TranscriptionAdapter.transcribe_audio_reference
                               (mock / openai / whisper / vapi / manual)
                                   └── transcription_service.normalize_transcription_result

5. Transcript Saved to Consultation
   └── transcription_service.transcribe_consultation_audio
           └── consultation_repo.save_transcript
                   └── consultation_sessions.transcript_text set
                           status → "transcribed"

6. Clinical Summary Draft Generated
   └── summary_builder.validate_summary_input
           └── summary_builder.parse_structured_transcript_markers
                   └── summary_builder.build_clinical_summary_draft
                           └── summary_builder.validate_clinical_summary_draft
                                   └── summary_builder.create_and_save_clinical_summary_draft
                                           └── consultation_repo.save_draft_summary
                                                   └── consultation_sessions.draft_summary set
                                                           status → "draft_ready"
                                                           approval_status → "pending_review"
                                                           doctor_review_required = True

7. Doctor Review Workflow
   └── review_workflow.validate_draft_ready_for_review
           └── review_workflow.build_review_package
                   └── [doctor reads draft, edits if needed, approves or rejects]

8a. Approved Summary Saved
   └── review_workflow.validate_approved_summary
           └── review_workflow.approve_summary_after_review
                   └── consultation_repo.approve_consultation_summary
                           └── consultation_sessions.approved_summary set
                                   status → "approved"
                                   approval_status → "approved"
                                   approved_by_user_id set
                                   approved_at = now()

8b. Rejected Summary Saved
   └── review_workflow.validate_rejection_reason
           └── review_workflow.reject_summary_after_review
                   └── consultation_repo.reject_consultation_summary
                           └── consultation_sessions.rejected_reason set
                                   status → "rejected"
                                   approval_status → "rejected"

9. Patient Timeline Report
   └── timeline_report.create_patient_timeline_report
           ├── patient_repo.get_patient_by_id → normalize_patient_record
           └── consultation_repo.list_consultation_sessions
                   └── timeline_report.build_timeline_entry (for each session)
                           ├── detect_summary_status
                           └── extract_summary_for_timeline (drafts hidden by default)
                   └── timeline_report.sort_timeline_entries (newest first)
                           └── timeline_report.build_patient_timeline_report
                                   └── report with safety flags returned
```

---

## D) Data Model Review

### `patients`
19 columns. Tenant-scoped via `clinic_id`. Unique on `(clinic_id, external_patient_id)` when set, enabling safe EMR upsert. CHECK constraint on `status` (active/inactive/archived) and `gender`. 7 indexes for name search (GIN trigram candidate), DOB, phone, email, external ID, and status. `notes` and `raw_payload` (JSONB) are intentionally excluded from the public timeline report output.

### `consultation_sessions`
19 columns. Tenant-scoped via `clinic_id`. Foreign keys to `patients` (ON DELETE CASCADE), `clinic_users` (doctor, approver — ON DELETE SET NULL). Dual JSONB columns: `draft_summary` (AI-generated, never final) and `approved_summary` (doctor-approved only). 3 CHECK constraints enforce valid values for `source`, `status`, and `approval_status`. 1 compound constraint: `approved_at IS NOT NULL` is required only when `approval_status = 'approved'`. 7 composite indexes for dashboard queries (patient, doctor, status, approval, approved_at, source).

### Approved vs. Draft Summary Separation
- `draft_summary` (JSONB) — set by `save_draft_summary`; always carries `doctor_review_required=True`, `no_diagnosis_generated=True`, `no_treatment_advice_generated=True`.
- `approved_summary` (JSONB) — set by `approve_consultation_summary` only when doctor explicitly approves; carries `doctor_approved=True`, `approved_by_user_id`, `source="doctor_review"`.
- `approval_status` CHECK constraint makes the state machine unambiguous: `not_ready → pending_review → approved / rejected`.
- The timeline service reads `approval_status` to distinguish the two; draft summaries are hidden from reports unless `include_drafts=True` is explicitly passed by the caller.

### Doctor Approval Representation
- `approved_by_user_id UUID` — FK to `clinic_users`; records which doctor approved.
- `approved_at TIMESTAMPTZ` — set by the repo at approval time using `now()`.
- `rejected_reason TEXT` — free-text explanation for rejection.
- The compound CHECK constraint `(approval_status = 'approved' AND approved_at IS NOT NULL) OR approval_status <> 'approved'` prevents approvals without a timestamp at the database level.

### clinic_users Relationship
- `consultation_sessions.doctor_user_id` → `clinic_users.id` (ON DELETE SET NULL) — tracks which doctor conducted the session.
- `consultation_sessions.approved_by_user_id` → `clinic_users.id` (ON DELETE SET NULL) — tracks which doctor approved the summary.
- No FK yet from `patients` to `clinic_users` (intentional — patients are not clinic users).

### What Should Not Be Stored in These Tables
- Raw audio binary data — audio is referenced by path only; binary storage belongs to a dedicated file service (S3/GCS).
- LLM prompts or model metadata — these belong in service layer constants, not the database.
- Authentication tokens or secrets — per project security rules, secrets stay out of tenant config and database rows.
- Patient notes and raw_payload in public API responses — the timeline report explicitly excludes both; this must be enforced in all future API endpoints that return patient records.

---

## E) API Inventory After Module 34

### Health
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/health/ready` | Readiness probe |

### n8n Webhooks
| Method | Path | Description |
|---|---|---|
| POST | `/webhooks/n8n/calendar-sync` | Calendar block sync from n8n |

### Availability
| Method | Path | Description |
|---|---|---|
| POST | `/calendar/availability/check` | Is a specific slot bookable? |
| POST | `/calendar/availability/suggest` | Suggest open slots |

### Vapi Tools
| Method | Path | Description |
|---|---|---|
| POST | `/vapi/tools/check-availability` | Vapi-facing slot check |
| POST | `/vapi/tools/suggest-slots` | Vapi-facing slot suggestion |
| POST | `/vapi/tools/capture-appointment-request` | Create appointment request from Vapi call |

### Vapi Webhooks
| Method | Path | Description |
|---|---|---|
| POST | `/webhooks/vapi/call-event` | Persist Vapi call event |

### Appointment Requests
| Method | Path | Description |
|---|---|---|
| POST | `/appointment-requests` | Create request |
| GET | `/appointment-requests` | List (filters: status, action_required, limit) |
| GET | `/appointment-requests/{id}` | Get single |
| PATCH | `/appointment-requests/{id}/status` | Update status |
| PATCH | `/appointment-requests/{id}/assign` | Assign to user |
| POST | `/appointment-requests/{id}/callback-needed` | Flag callback |
| POST | `/appointment-requests/{id}/archive` | Archive |

### Notifications
| Method | Path | Description |
|---|---|---|
| POST | `/notifications` | Create notification |
| GET | `/notifications` | List (filters: status, priority, type, recipient, limit) |
| GET | `/notifications/{id}` | Get single |
| POST | `/notifications/{id}/read` | Mark as read |
| POST | `/notifications/{id}/cancel` | Cancel |

### Patients
| Method | Path | Description |
|---|---|---|
| POST | `/patients` | Create patient |
| GET | `/patients` | List (filters: status, search, limit) |
| POST | `/patients/upsert-by-external-id` | Upsert by EMR external ID |
| GET | `/patients/by-external-id/{external_patient_id}` | Get by external ID |
| GET | `/patients/{patient_id}` | Get by internal ID |
| PATCH | `/patients/{patient_id}` | Update fields |
| POST | `/patients/{patient_id}/archive` | Archive |

### Consultations
| Method | Path | Description |
|---|---|---|
| POST | `/consultations` | Create session |
| GET | `/consultations` | List (filters: patient_id, doctor_user_id, status, approval_status, source, limit) |
| GET | `/consultations/{session_id}` | Get single |
| PATCH | `/consultations/{session_id}/status` | Update status |
| POST | `/consultations/{session_id}/audio` | Attach audio reference |
| POST | `/consultations/{session_id}/transcript` | Save transcript text |
| POST | `/consultations/{session_id}/draft-summary` | Save draft summary |
| POST | `/consultations/{session_id}/approve` | Doctor-approve summary |
| POST | `/consultations/{session_id}/reject` | Reject summary |
| POST | `/consultations/{session_id}/archive` | Archive session |

**Total routes: 44**

**Note:** The Sprint 2 service modules (audio_storage, transcription_service, summary_builder, review_workflow, timeline_report) are NOT yet wired to API routes. The consultation routes call `consultation_repo` directly; they do not invoke the service layer. This is the gap Module 35 must close.

---

## F) Safety Review

| Safety Concern | Status |
|---|---|
| Auto-diagnosis | Protected — summary_builder has no diagnosis key in output; validate_clinical_summary_draft rejects any draft containing a top-level `diagnosis` key; validate_draft_ready_for_review re-checks |
| Treatment advice generation | Protected — `no_treatment_advice_generated=True` is a required field in every draft; validation rejects drafts where this is False |
| AI draft treated as final | Protected — every draft carries `doctor_review_required=True`; approve endpoint requires explicit `approved_by_user_id`; DB CHECK constraint requires `approved_at` to be set |
| Draft summaries in timeline by default | Protected — `extract_summary_for_timeline` returns None for drafts unless `include_drafts=True`; default is False at all call sites |
| Missing doctor approval | Protected — `approval_status` CHECK constraint; `approved_at` NOT NULL constraint when approved; approve_consultation_summary requires non-empty `approved_by_user_id` |
| Storing audio binary in database | Protected — audio_storage.py builds a file path only; no binary data is stored in `consultation_sessions`; audio column is `audio_file_path TEXT` |
| Exposing patient notes/raw_payload in timeline | Protected — `normalize_patient_record` explicitly omits both keys; the returned dict is a whitelist of safe fields |

---

## G) Risk Review

### 1. Missing authentication — Severity: HIGH
No auth middleware exists. All 44 routes are open. Patient data (PHI) and consultation summaries are now accessible without credentials. Per project roadmap this is intentional until Milestone 9, but the risk surface has grown substantially since Checkpoint 01.
**Before external pilots:** implement at minimum a static API key check per clinic. Full OAuth/JWT can wait for Milestone 9.

### 2. Missing tenant auth enforcement — Severity: HIGH
`clinic_id` is passed in request bodies and URL paths, not derived from an authenticated session. A caller can query or mutate another tenant's patients and consultations by simply changing the `clinic_id` value. No middleware validates that the caller owns the `clinic_id` they submit.
**Before external pilots:** add a lightweight request-scoped tenant assertion. Even a hardcoded mapping of API key → allowed clinic_id would reduce the blast radius significantly.

### 3. Service layer not wired to API routes — Severity: MEDIUM
The Sprint 2 service modules (audio_storage, transcription_service, summary_builder, review_workflow, timeline_report) implement the full clinical workflow but are not called by any API route. The consultation routes (`consultations.py`) call `consultation_repo` directly and bypass all business logic, validation, and safety checks in the service layer. Until Module 35 wires these, the services cannot be exercised through the API.
**Before frontend:** Module 35 must expose clinical workflow API routes that delegate to the service modules.

### 4. No real database migration runner — Severity: MEDIUM
`schema.sql` is 437 lines and growing. It is applied idempotently via `IF NOT EXISTS` but there is no migration tool (Alembic, Flyway, etc.), no version tracking, and no rollback path. Adding a column to an existing table today would require a manual ALTER TABLE statement not tracked anywhere.
**Before staging/production:** introduce Alembic or a lightweight migration runner.

### 5. No real file storage — Severity: MEDIUM
`audio_storage.py` builds a sanitised storage path and attaches it to the consultation record, but no real file is written or read. A real consultation recording cannot be processed until a file storage backend (local disk, S3, GCS) is integrated.
**Before external pilots:** implement at minimum a local-disk storage adapter with an interface compatible with cloud storage.

### 6. No real transcription provider — Severity: MEDIUM
`transcription_service.py` defines a clean `TranscriptionAdapter` Protocol and a mock adapter. No real Whisper/OpenAI/AssemblyAI adapter exists. Audio cannot be converted to text.
**Before external pilots:** implement one real transcription adapter (Whisper via OpenAI API is the lowest-friction option).

### 7. No real LLM clinical summary adapter — Severity: MEDIUM
`summary_builder.py` uses regex-based deterministic marker extraction. It produces a useful structured draft when the transcript contains known markers, but produces only "missing information" entries for unstructured transcripts. Real consultation transcripts are conversational — they rarely use the exact marker format.
**Before external pilots:** implement a real LLM adapter (Claude API) that takes a raw transcript and returns a structured draft. The `build_clinical_summary_draft` function accepts a `source` parameter that can be set to a non-default generator — this is the extension point.

### 8. Audit log still unused — Severity: MEDIUM
The `audit_log` table was defined in Module 3 and remains empty. Patient creation, patient updates, consultation approvals, and rejections are all compliance-relevant actions with no immutable trail.
**Before external pilots:** create `audit_log_repo.py` with a `log_action` function. Call it at minimum on: patient create/archive, consultation approve, consultation reject.

### 9. Duplicated validation — Severity: LOW-MEDIUM
Enum values (status strings, source strings, approval_status values) are duplicated across: (a) `schema.sql` CHECK constraints, (b) repository `_assert_valid_*` helper functions, and (c) Pydantic validator literals in `schemas/`. The set is now large enough (7 repos, 6 schema files, 1 schema.sql) that a value change requires edits in 3 places.
**Before frontend:** centralise into `backend/app/core/enums.py`.

### 10. Growing test count — Severity: LOW
908 tests run in ~1.3 seconds — currently healthy. All are pure unit tests with mocked pools. As the codebase grows, test isolation, fixture reuse, and mock management will require more discipline. There are no shared fixtures across test files; each file re-implements `_make_pool`, `_fake_row`, etc.
**Can wait:** introduce a `conftest.py` with shared pool and row factories when test count crosses ~1200.

### 11. Route file growth — Severity: LOW
`consultations.py` (10 routes) and `patients.py` (7 routes) are large but still manageable. As clinical workflow routes (Module 35) and report routes are added, these files will grow further. No sub-routing is used.
**Can wait:** consider sub-routers (e.g., `consultations/workflow.py`) if any single route file exceeds 15 endpoints.

### 12. Privacy/compliance for medical data — Severity: HIGH (architectural concern)
`notes` and `raw_payload` in patient records contain unstructured free text that may include PHI. These are excluded from the timeline report but are returned by patient CRUD routes today. Without field-level access control or encryption, any caller with a valid clinic_id can read these fields.
**Before external pilots:** audit all API response models to confirm PHI-adjacent fields are explicitly opt-in, not opt-out.

---

## H) Refactor Recommendations

### Must do before external pilots

| Item | Reason |
|---|---|
| Implement static API key → clinic_id auth | PHI is now in the database. Open routes are unacceptable before any external party uses the system |
| Add tenant ownership assertion middleware | `clinic_id` from request body is not verified against the caller's identity — cross-tenant data access is trivially possible |
| Create `audit_log_repo.py` with `log_action` | Patient create/archive and consultation approve/reject are compliance-relevant; they need an immutable trail |
| Audit API response models for PHI leakage | `notes` and `raw_payload` are returned by patient routes today with no access control |

### Should do before frontend

| Item | Reason |
|---|---|
| Wire service modules to clinical workflow API routes (Module 35) | The frontend cannot use audio attach, transcription, summary generation, review, or timeline through the API yet |
| Centralise enum constants into `backend/app/core/enums.py` | Prevents divergence as more status values are added; affects schema, repos, and Pydantic simultaneously |
| Implement real transcription adapter | Placeholder is functional for testing but useless for actual consultation recording |
| Introduce Alembic or lightweight migration runner | Schema changes will be needed before frontend integration; manual ALTER TABLE is error-prone |

### Can wait

| Item | Reason |
|---|---|
| Shared test fixtures in `conftest.py` | 908 tests run in 1.3s; fixture duplication is a maintenance cost, not a correctness risk yet |
| Sub-routers for large route files | Route files are readable at current size; refactor when any file exceeds 15 endpoints |
| Real DB integration tests | Per project rules; plan for a separate test sprint before production |
| PDF/Excel export | Milestone 6 per roadmap; timeline service is the integration point when ready |

### Avoid for now

| Item | Reason |
|---|---|
| Real LLM integration in summary_builder | The marker-based approach is safe and testable; LLM integration belongs in a separate adapter module that wraps summary_builder, not inside it |
| Full OAuth/JWT auth middleware | Milestone 9; building it now without a real identity provider produces placeholder code that must be replaced |
| Breaking up `schema.sql` | Idempotent single-file DDL is correct for dev; splitting adds ordering dependencies with no benefit at this stage |
| Refactoring existing Sprint 1 or 2 modules | All 908 tests pass; refactoring stable code before external pilots is unnecessary churn |

---

## I) Next Milestone Options

| Option | Description | Assessment |
|---|---|---|
| Module 35 — Patient Timeline API Routes | Expose `create_patient_timeline_report` via REST | Ready to implement but narrow; only one endpoint |
| Module 35 — Clinical Workflow API Routes | Wire audio, transcription, summary, review, timeline to API routes | Highest value — closes the biggest gap between service layer and API surface |
| Module 35 — Auth + tenant access foundation | Static API key + clinic_id binding | Critical for safety but blocks nothing for internal development |
| Module 35 — Real database migration setup | Alembic or lightweight runner | Important before staging, not urgent for development |
| Module 35 — File storage integration | Local-disk adapter for audio | Required before real consultations; low complexity |
| Module 35 — Real transcription provider | OpenAI Whisper adapter | Required before real use; can be done in parallel with routes |
| Module 35 — Real LLM clinical summary adapter | Claude API summary generation | High value but requires prompt engineering discipline; do after routes are wired |

### Recommendation: Module 35 — Clinical Workflow API Routes

**Reason:** The service layer is complete (Modules 30–34) but not exposed through the API. The consultation routes (`POST /consultations/{id}/audio`, `/transcript`, `/draft-summary`, `/approve`, `/reject`) call the repository directly and bypass all business logic, safety validation, and workflow orchestration. Until this gap is closed:

- A frontend cannot safely use the clinical workflow.
- Audio attachment validation (format, size, path sanitisation) is not enforced at the API boundary.
- Transcript saving bypasses `transcription_service` normalisation.
- Draft summary generation is not callable via REST — a client must know to call the repo directly.
- Doctor approval bypasses `review_workflow` safety checks.
- The patient timeline endpoint does not exist.

Module 35 should update the existing consultation routes to delegate to the service modules and add the patient timeline route. This is the minimum viable step before any frontend or external integration work.

---

## J) Recommended Next Module

**Sprint 3 / Module 35 — Clinical Workflow API Routes**

See `NEXT_MODULE.md` for the placeholder.
