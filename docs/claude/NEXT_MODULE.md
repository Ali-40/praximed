# Sprint 20 / Module 151 — Patient Intake Link Flow Foundation

Status: pending implementation.

## Context

Module 150 complete:
- `backend/migrations/versions/0008_anamnesis_templates.py` — anamnesis_templates table
- `backend/app/schemas/anamnesis_template.py` — Pydantic schemas with forbidden pattern checks
- `backend/app/db/repositories/anamnesis_template_repo.py` — CRUD, no DELETE
- `backend/app/services/anamnesis_template_engine.py` — 3 demo templates (GP, Dermatology, Pediatrics)
- `backend/app/api/routes/anamnesis_templates.py` — 5 protected routes, no DELETE
- `backend/app/api/router.py` (updated) — anamnesis_templates router registered
- `backend/app/db/schema.sql` (updated) — anamnesis_templates DDL
- `backend/tests/test_anamnesis_template_engine_foundation.py` — ≥60 tests
- `docs/architecture/ANAMNESIS_TEMPLATE_ENGINE_FOUNDATION.md`
- Templates: global (clinic_id IS NULL) and clinic-specific overrides
- Status lifecycle: draft → active → archived
- No patient answers stored. No history writes. No AI. No diagnosis. No triage.
- production_phi_enabled always False. Production PHI remains NO-GO.

Sprint 20 data layer is in place:
- Consent ledger (consent_events, Module 148)
- Patient history data model — 7 FHIR-aligned tables (Module 149)
- Anamnesis template engine (Module 150)

The next step is the intake link flow: generating short-lived, clinic-scoped intake
URLs that patients can follow to answer their anamnesis template before an appointment.

## Goal

Create the backend foundation for the patient intake link flow. Generate a time-limited,
clinic-scoped intake session token that links to a specific anamnesis template.
Track session state (not-started / in-progress / completed / expired).

No patient answers stored in this module. No history writes. No AI.
Synthetic/fake staging only. No real patient PHI. Production PHI remains NO-GO.

## What Module 151 must implement

### 1. Database Migration

`backend/migrations/versions/0009_intake_link_sessions.py` (new):
Revision: `0009_intake_link_sessions`
Down revision: `0008_anamnesis_templates`

Table: `intake_link_sessions`
- id UUID primary key
- clinic_id UUID NOT NULL references clinics(id)
- patient_id UUID references patients(id)
- template_id UUID NOT NULL references anamnesis_templates(id)
- session_token TEXT NOT NULL UNIQUE
- status TEXT NOT NULL DEFAULT 'not_started' (not_started/in_progress/completed/expired)
- expires_at TIMESTAMPTZ NOT NULL
- started_at TIMESTAMPTZ
- completed_at TIMESTAMPTZ
- consent_event_id UUID references consent_events(id)
- synthetic_demo BOOLEAN NOT NULL DEFAULT true
- production_phi_enabled BOOLEAN NOT NULL DEFAULT false
- created_by_user_id UUID
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
- CONSTRAINT intake_link_phi_check CHECK (production_phi_enabled = false)
- CONSTRAINT intake_link_status_check CHECK (status IN ('not_started','in_progress','completed','expired'))

Indexes: clinic_id, patient_id, template_id, session_token, status, expires_at.

### 2. Schemas

`backend/app/schemas/intake_link.py` (new):
- IntakeLinkCreate
- IntakeLinkRead
- IntakeLinkStatusUpdate (in_progress / completed / expired)
- IntakeLinkResponse
- IntakeLinkListResponse

Validation:
- template_id required and valid UUID
- expires_at must be in the future
- production_phi_enabled always False
- synthetic_demo always True
- No patient answers in schema

### 3. Repository

`backend/app/db/repositories/intake_link_repo.py` (new):
- create_intake_link_session
- get_intake_link_session_by_id
- get_intake_link_session_by_token
- list_intake_link_sessions_for_clinic(clinic_id, status=None)
- update_intake_link_status
- expire_stale_sessions (mark sessions past expires_at as expired)

No DELETE. Parameterised SQL. Tenant-scoped.

### 4. Service

`backend/app/services/intake_link.py` (new):
- generate_session_token: secrets.token_urlsafe(32) — no patient data in token
- create_intake_link(clinic_id, template_id, patient_id=None, ttl_hours=48)
- get_intake_link(session_id)
- resolve_intake_link_by_token(token) — returns session + template for rendering
- advance_session_status(session_id, new_status)
- expire_stale_sessions(clinic_id)

No AI. No diagnosis. No medical advice. Token must not encode patient data.

### 5. Routes

`backend/app/api/routes/intake_links.py` (new):
- POST /clinics/{clinic_id}/intake-links (201, auth) — create intake link session
- GET /clinics/{clinic_id}/intake-links (200, auth) — list sessions
- GET /intake-links/{session_id} (200, auth) — get session by UUID
- GET /intake-links/resolve/{token} (200, auth) — resolve by token
- PATCH /intake-links/{session_id}/status (200, auth) — advance status

No DELETE. No public access. No patient answers.

### 6. Tests

`backend/tests/test_intake_link_flow_foundation.py` (new — ≥60 tests):
- Migration: table, all columns, all CHECK constraints, UNIQUE on session_token, downgrade
- Schema SQL: intake_link_sessions table present
- Pydantic: create/read/status-update, future expires_at required, phi always false
- Repo: create, get by id, get by token, list, update status, expire stale
- Service: generate_token is urlsafe, create returns session, resolve by token, expire stale
- Routes: all require auth, no DELETE, 404 for missing, 400 for expired
- PHI invariant: production_phi_enabled=False in all responses
- Forbidden: no patient answers in any schema, no diagnosis, no medical advice

### 7. Architecture doc

`docs/architecture/INTAKE_LINK_FLOW_FOUNDATION.md` (new)

### 8. Docs

- `docs/claude/CURRENT_STATE.md` — Module 151 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 152

## Constraints

- No patient answers stored in this module
- No AI involvement
- No diagnosis, no triage scoring, no medical advice
- session_token must not encode patient data
- production_phi_enabled always False
- All SQL parameterised
- Tenant isolation
- No DELETE
- Full test suite must remain green
- Commit message:
  Sprint 20 / Module 151 — Patient intake link flow foundation
