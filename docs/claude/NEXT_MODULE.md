# Sprint 20 / Module 152 — Live Patient Intake Link Smoke Evidence

Status: pending implementation.

## Context

Module 151 complete:
- `backend/migrations/versions/0009_patient_intake_links.py` — patient_intake_links + patient_intake_submissions
- `backend/app/schemas/patient_intake_link.py` — Pydantic schemas, PHI/demo guards
- `backend/app/services/intake_token.py` — generate_intake_token, hash_intake_token, token_prefix
- `backend/app/db/repositories/patient_intake_link_repo.py` — CRUD, no raw token stored
- `backend/app/services/patient_intake_link.py` — create, public load, submit, revoke; consent event on submit
- `backend/app/api/routes/patient_intake_links.py` — 4 admin + 2 public routes, no DELETE
- `backend/app/api/router.py` (updated) — patient_intake_links router registered
- `backend/app/db/schema.sql` (updated) — both tables
- `frontend/app/intake/[token]/page.tsx` — mobile-first consent-first questionnaire
- `frontend/app/developer-console/intake-links/page.tsx` — admin link management
- `frontend/lib/api.ts` (updated) — all intake helpers
- `backend/tests/test_patient_intake_link_flow_foundation.py` — 113 tests
- `docs/architecture/PATIENT_INTAKE_LINK_FLOW_FOUNDATION.md`
- Raw token never stored. token_hash stored. intake_url shown once.
- Consent step required before questionnaire.
- Answers stored as synthetic intake submissions only.
- No patient history writes. No AI structuring. No diagnosis. No triage.
- production_phi_enabled always False. Production PHI remains NO-GO.

Sprint 20 data layer is now complete:
- Consent ledger (Module 148)
- Patient history data model (Module 149)
- Anamnesis template engine (Module 150)
- Patient intake link flow (Module 151)

## Goal

Deploy Module 151 to the staging environment and produce live smoke evidence
that the full intake link flow works end-to-end with synthetic/demo data only.

## What Module 152 must do

### 1. Deploy and migrate

- Deploy Module 151 backend to Railway (or staging target).
- Run migration 0009_patient_intake_links.
- Confirm both tables exist: patient_intake_links, patient_intake_submissions.
- Confirm no prior migration state broken.

### 2. Seed demo templates if needed

- If demo_gp_basic_history is not seeded:
  - Call POST /anamnesis-templates/seed-demo with admin session.
  - Confirm 3 templates returned.
  - Note template ID of demo_gp_basic_history for next step.

### 3. Create demo intake link

- Call POST /clinics/{staging_clinic_id}/patient-intake-links:
  - template_id = demo_gp_basic_history UUID
  - language = de
  - purpose = patient_history_collection
  - expires_at = now + 72 hours
- Confirm HTTP 201.
- Capture intake_url from response (raw token, shown once).
- Confirm token_prefix appears in response.
- Confirm production_phi_enabled = false.

### 4. Open public intake page

- Navigate to /intake/{raw_token} in browser.
- Confirm demo staging notice appears.
- Confirm consent step renders before questionnaire.
- Confirm language selector shows de / en / ar.

### 5. Complete consent-first questionnaire

- Check consent checkbox.
- Click "Continue to questionnaire".
- Confirm questionnaire renders with sections from demo_gp_basic_history.
- Fill in one or two optional fields with synthetic placeholder answers:
  - known_allergies: "Keine (Demo)"
  - current_medications: "Keine (Demo)"
- Skip remaining questions.
- Click "Submit intake".
- Confirm success message: "Intake submitted for staff review."

### 6. Verify submission stored

- Call GET /clinics/{staging_clinic_id}/patient-intake-submissions with admin session.
- Confirm 1 submission returned.
- Confirm status = submitted.
- Confirm consent_event_id is present.
- Confirm answers JSON contains the synthetic placeholder answers.
- Confirm production_phi_enabled = false.
- Confirm synthetic_demo = true.

### 7. Verify consent event created

- Check that consent_events table has a new row with:
  - channel = intake_link
  - purpose = patient_history_collection
  - granted = true
  - production_phi_enabled = false

### 8. Verify no patient history write

- Confirm patient_history_allergies has no new rows for this submission.
- Confirm no other patient_history_* tables were written.

### 9. Verify no PHI / no real data

- Confirm no real patient identifiers in answers.
- Confirm synthetic_demo = true on all rows.
- Confirm production_phi_enabled = false everywhere.

### 10. Evidence documentation

Create: `docs/smoke/MODULE_152_INTAKE_LINK_SMOKE_EVIDENCE.md`

Must include:
- Date and staging environment
- Clinic ID used (staging demo UUID)
- Template ID used
- token_prefix captured (not raw token)
- HTTP response codes at each step
- Submission ID returned
- Consent event ID returned
- Screenshots or curl output (redacted of raw token)
- Confirmation: no history write occurred
- Confirmation: no PHI / no real data
- Production PHI remains NO-GO

### 11. Docs

- `docs/claude/CURRENT_STATE.md` — Module 152 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 153 (AI Structuring Service Foundation or Arabic RTL Foundation)

## Constraints

- Synthetic/fake staging only
- No real patient data
- No PHI
- No raw token in docs or smoke evidence
- No diagnosis, no triage, no medical advice
- No history writes during this smoke run
- Commit message:
  Sprint 20 / Module 152 — Live patient intake link smoke evidence
