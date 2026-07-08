# Anamnesis Template Engine Foundation

**Sprint 20 / Module 150 — 2026-07-08**

## Purpose

Clinic-configurable questionnaire templates for consent-first patient intake.
Templates define multilingual question sets (de/en/ar) per specialty.
Staff surface escalation keywords — no medical scoring, no diagnosis.

## Safety boundaries

- No patient answers stored (templates only, no intake responses)
- No patient history writes
- No AI structuring, no triage scoring, no diagnosis, no medical advice
- No treatment recommendations
- `production_phi_enabled` always `False` — enforced by DB CHECK, service, and route layers
- `synthetic_demo = True` on all seeded templates
- No DELETE route — templates are draft → active → archived only
- Production PHI remains NO-GO

## Database

**Table:** `anamnesis_templates` (migration `0008_anamnesis_templates`)

- `clinic_id IS NULL` — global/demo template available to all clinics
- `clinic_id SET` — clinic-specific override; takes precedence over global
- Partial unique indexes ensure one version per (template_key, version) per scope
- `production_phi_enabled = false` enforced by `anamnesis_templates_phi_check` CHECK constraint
- Status enum: `draft | active | archived`
- Status transitions: draft → active → archived (no reverse, no delete)

## Template JSON schema contract

```
template_schema: {
  sections: [
    {
      section_key: string,
      title: { de: string, en?: string, ar?: string },
      description?: { de?: string, en?: string, ar?: string },
      questions: [
        {
          question_key: string,
          history_target: "allergies" | "medications" | "conditions" | "procedures"
                        | "immunizations" | "family-history" | "social-history"
                        | "appointment-context" | "none",
          type: "text" | "textarea" | "single_select" | "multi_select"
              | "yes_no" | "date" | "number",
          label: { de: string, en?: string, ar?: string },
          help_text?: { de?: string, en?: string, ar?: string },
          required: bool,
          skip_allowed: bool,           # always true for demo templates
          maps_to_fhir?: string,
          options?: [{ value: string, label: { de: string, ... } }]
        }
      ]
    }
  ]
}
```

Forbidden schema keys (validated at create time): `score`, `risk_score`, `triage_score`,
`diagnosis_score`, `medical_advice`, `treatment_recommendation`, `sk-`, `vapi_live`,
`jwt`, `password`, `secret`, `DATABASE_URL`.

## Seeded demo templates

| Template key | Specialty | Sections | Escalation keywords |
|---|---|---|---|
| `demo_gp_basic_history` | general_practice | allergies, medications, procedures, family_history, social_history | de + en |
| `demo_dermatology_basic_history` | dermatology | reason_context, allergies, medications, prior_treatments | none |
| `demo_pediatrics_since_birth` | pediatrics | immunizations, allergies, medications, family_history, milestones_observation | none |

All demo templates: `synthetic_demo=True`, `status=active`, primary_language=de, supported=de/en/ar.

## API routes (all require authenticated session)

| Method | Path | Purpose |
|---|---|---|
| POST | `/clinics/{clinic_id}/anamnesis-templates` | Create template for clinic |
| GET | `/clinics/{clinic_id}/anamnesis-templates` | List templates (with specialty/status/limit filters) |
| GET | `/anamnesis-templates/{template_id}` | Fetch single template by UUID |
| PATCH | `/anamnesis-templates/{template_id}/status` | Activate or archive template |
| POST | `/anamnesis-templates/seed-demo` | Seed the 3 global demo templates |

No DELETE route. No public access. No patient answers in any route.

## File map

| File | Role |
|---|---|
| `backend/migrations/versions/0008_anamnesis_templates.py` | Migration |
| `backend/app/db/schema.sql` | Reference DDL |
| `backend/app/schemas/anamnesis_template.py` | Pydantic validators |
| `backend/app/db/repositories/anamnesis_template_repo.py` | Async SQL repo |
| `backend/app/services/anamnesis_template_engine.py` | Business logic + demo data |
| `backend/app/api/routes/anamnesis_templates.py` | FastAPI routes |
| `backend/tests/test_anamnesis_template_engine_foundation.py` | ≥60 tests |

## Next module

Module 151 — Patient Intake Link Flow Foundation
