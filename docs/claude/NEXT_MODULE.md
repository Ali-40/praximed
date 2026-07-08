# Sprint 20 / Module 150 — Anamnesis Template Engine

Status: pending implementation.

## Context

Module 149 complete:
- `backend/migrations/versions/0007_patient_history_data_model.py` — 7 FHIR-aligned history tables
- `backend/app/schemas/patient_history.py` — all 7 create/read schemas + status update
- `backend/app/db/repositories/patient_history_repo.py` — CRUD, no DELETE
- `backend/app/services/patient_history.py` — consent gate on every write
- `backend/app/api/routes/patient_history.py` — 5 protected routes, no DELETE
- `backend/app/api/router.py` (updated) — patient_history router registered
- `backend/tests/test_patient_history_data_model_foundation.py` — 113 tests
- `docs/architecture/PATIENT_HISTORY_DATA_MODEL_FOUNDATION.md`
- consent_event_id required on every history row
- Append-only/versioned. Staff/doctor review required.
- production_phi_enabled always False.
- No real patient PHI. No diagnosis. No medical advice. No triage.
- Production PHI remains NO-GO.

Sprint 20 is in progress. The data model foundation is in place. The next step is
the anamnesis template engine: clinic-configurable questionnaire templates that drive
the structured intake flow.

## Goal

Create a clinic-configurable anamnesis questionnaire template engine. Templates define
which questions are shown during patient intake, in what order, and in what language.
Templates are stored per clinic and per specialty. Rendering is structure-only —
no AI involvement, no diagnosis, no medical scoring. de/en/ar-ready labels.

Synthetic staging only. No real patient data. No PHI unlock. Production PHI remains NO-GO.

## What Module 150 must implement

### 1. Database Migration

`backend/migrations/versions/0008_anamnesis_templates.py` (new):
Revision: `0008_anamnesis_templates`
Down revision: `0007_patient_history_data_model`

Table: `anamnesis_templates`
- id UUID primary key
- clinic_id UUID NOT NULL references clinics(id)
- template_name TEXT NOT NULL
- specialty TEXT NOT NULL DEFAULT 'general'
- language_code TEXT NOT NULL DEFAULT 'de' (de/en/ar)
- version INTEGER NOT NULL DEFAULT 1
- sections JSONB NOT NULL DEFAULT '[]'::jsonb
- red_flag_keywords JSONB NOT NULL DEFAULT '[]'::jsonb
- status TEXT NOT NULL DEFAULT 'draft' (draft/active/archived)
- created_by_user_id UUID
- production_phi_enabled BOOLEAN NOT NULL DEFAULT false
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
- CONSTRAINT anamnesis_templates_phi_check CHECK (production_phi_enabled = false)
- CONSTRAINT anamnesis_templates_status_check CHECK (status IN ('draft','active','archived'))
- CONSTRAINT anamnesis_templates_language_check CHECK (language_code IN ('de','en','ar'))
- UNIQUE(clinic_id, template_name, language_code, version)

Indexes: clinic_id, specialty, language_code, status.

### 2. Sections and Questions Schema

sections is a JSONB array of section objects:
```json
[
  {
    "section_id": "chief_complaint",
    "label_de": "Hauptbeschwerde",
    "label_en": "Chief Complaint",
    "label_ar": "الشكوى الرئيسية",
    "order": 1,
    "questions": [
      {
        "question_id": "q1",
        "label_de": "Was ist Ihr Hauptproblem?",
        "label_en": "What is your main concern?",
        "label_ar": "ما هي شكواك الرئيسية؟",
        "answer_type": "text",
        "required": true,
        "maps_to_history_type": "conditions",
        "maps_to_field": "condition_text"
      }
    ]
  }
]
```

answer_type: text / boolean / select / multiselect / date

red_flag_keywords: list of strings to escalate to staff (no triage scoring).

Specialty templates required:
- general (GP)
- dermatology
- pediatrics

Each specialty includes relevant section/question structure for de/en/ar.

### 3. Schemas

`backend/app/schemas/anamnesis_template.py` (new):
- TemplateQuestion
- TemplateSection
- AnamnesisTemplateCreate
- AnamnesisTemplateRead
- AnamnesisTemplateUpdate
- AnamnesisTemplateResponse

Validation:
- clinic_id required
- template_name not empty
- sections must be a valid list
- red_flag_keywords: strings only, no medical scoring
- language_code: de/en/ar
- status: draft/active/archived
- production_phi_enabled always False
- reject forbidden metadata

### 4. Repository

`backend/app/db/repositories/anamnesis_template_repo.py` (new):
- create_template
- get_template_by_id
- list_templates_for_clinic(clinic_id, specialty=None, language_code=None, status=None)
- get_active_template(clinic_id, specialty, language_code)
- update_template_status
- update_template_sections

### 5. Service

`backend/app/services/anamnesis_template.py` (new):
- create_anamnesis_template
- get_anamnesis_template
- list_clinic_templates
- activate_template
- render_template_for_intake(clinic_id, specialty, language_code) — returns ordered sections/questions

render_template_for_intake must NOT generate diagnosis, triage, or medical advice.
Red flag keywords are surfaced as a plain list for staff escalation — no scoring.

### 6. Routes

`backend/app/api/routes/anamnesis_templates.py` (new):
- POST /clinics/{clinic_id}/anamnesis-templates (201, auth)
- GET /clinics/{clinic_id}/anamnesis-templates (200, auth)
- GET /anamnesis-templates/{template_id} (200, auth)
- PATCH /anamnesis-templates/{template_id}/status (200, auth)
- GET /clinics/{clinic_id}/anamnesis-templates/render?specialty=general&language=de (200, auth)

No DELETE. production_phi_enabled=False always.

### 7. Seed Templates

`backend/scripts/seed_anamnesis_templates.py` (new):
Seed 3 specialty templates (general/dermatology/pediatrics) × 3 languages (de/en/ar)
= 9 templates for staging clinic.

### 8. Tests

`backend/tests/test_anamnesis_template_engine.py` (new — ≥60 tests):
- Migration: table, all columns, all CHECK constraints, UNIQUE constraint
- Schemas: create/read/update, required field validation, language/status enum validation,
  forbidden metadata rejection, sections structure
- Repo: create, list, get, activate, render
- Service: create, list, get active, render for intake (sections ordered, labels correct)
- Routes: all endpoints require auth, no DELETE, render returns ordered sections
- Red flag: keywords surface without scoring (no triage, no medical advice)
- Forbidden: no diagnosis, no triage_score, no medical_advice, no DATABASE_URL, no secrets
- Seed script: seed function callable, creates templates for staging clinic

### 9. Architecture doc

`docs/architecture/ANAMNESIS_TEMPLATE_ENGINE.md` (new):
- Purpose: configurable intake questionnaire engine
- Template structure: sections → questions → labels (de/en/ar) → answer_type → history_type mapping
- Specialty templates: GP, dermatology, pediatrics
- Red flag escalation: keyword list surfaced to staff, no automated scoring
- de/en/ar support
- Rendering is structure-only, no AI
- No diagnosis. No triage. No medical advice.
- Synthetic staging only. Production PHI remains NO-GO.

### 10. Docs

- `docs/claude/CURRENT_STATE.md` — Module 150 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 151 — Intake Link Flow

## Constraints

- No AI involvement in this module
- No diagnosis, no triage scoring, no medical advice
- Red flag keywords surface to staff only — no automated escalation decisions
- de/en/ar labels required on all questions
- production_phi_enabled always False
- All SQL parameterised
- Tenant isolation
- No DELETE
- Full test suite must remain green
- Commit message:
  Sprint 20 / Module 150 — Anamnesis template engine
