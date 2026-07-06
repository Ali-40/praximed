# Sprint 19 / Module 133 — Connect Onboarding Frontend to Backend Request API

Status: pending implementation.

## Context

Module 132 complete:
- `backend/app/db/schema.sql` — `clinic_onboarding_requests` table with full constraint suite
- `backend/migrations/versions/0004_clinic_onboarding_requests.py` — migration
- `backend/app/schemas/clinic_onboarding.py` — Pydantic schemas
- `backend/app/db/repositories/clinic_onboarding_repo.py` — repository
- `backend/app/api/routes/clinic_onboarding.py` — public POST + protected GET/PATCH routes
- `docs/architecture/CLINIC_ONBOARDING_BACKEND_FOUNDATION.md`
- 78/78 new tests pass; 3366/3366 total pass
- Commit: Sprint 19 / Module 132 — Real clinic onboarding backend foundation

The `/onboarding` page (`frontend/app/onboarding/page.tsx`) is currently a static
scaffold with 5 steps but no real form submission. The backend `POST /clinic-onboarding-requests`
endpoint now exists and accepts pilot requests.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Make the `/onboarding` page form functional: wire it to the backend API so that a doctor
can fill in their clinic details and submit a real pilot/onboarding request.

## What Module 133 must implement

### 1. Frontend onboarding form — wire step 5 to backend

`frontend/app/onboarding/page.tsx` (update):
- Replace the static "STAGING SCAFFOLD / NOT FUNCTIONAL" badge with a working form flow.
- Keep the 5-step structure but make it interactive:
  - Step 1 (Clinic Details): clinic_name, specialty, city, clinic_type (optional), website (optional)
  - Step 2 (Doctor / Admin Account): doctor_name, contact_email, contact_phone (optional)
  - Step 3 (Workflow Preferences): preferred_language selector (German / English fallback),
    workflow_notes (optional), estimated_call_volume (optional)
  - Step 4 (AI Intake Setup): wants_ai_phone_intake toggle, wants_dashboard toggle
  - Step 5 (Review & Pilot Activation): summary of entered data + consent checkboxes:
    - consent_pilot_contact = true (explicit checkbox)
    - acknowledges_no_phi = true (explicit checkbox with text: "I acknowledge this is a pilot
      onboarding request, not a production patient data system activation.")
    - Submit button → POST /clinic-onboarding-requests

### 2. Language selector (Step 3)

- Two options: "Deutsch (Standard)" and "English (Fallback)"
- Selecting "Deutsch" sets preferred_language=de, fallback_language=en
- German is the default pre-selected option
- Language preference is sent to the backend but does not configure Vapi automatically

### 3. Success state

After successful 201 response:
- Show a confirmation panel with doctor name and clinic name
- State: "Your pilot request has been submitted. PraxisMed will contact you at [email]."
- Status badge: "Submitted — awaiting review"
- Staging safety copy: "This is a pilot intake only. No production PHI is activated."
- No redirect — stay on page

### 4. Error handling

- 422 validation errors from the API → show field-level error messages
- Network error → show a generic retry message
- No secrets in error output

### 5. API client integration

Use the existing `frontend/lib/api.ts` client.

For the public POST route (no auth required):
```typescript
fetch(`${process.env.NEXT_PUBLIC_API_URL}/clinic-onboarding-requests`, {
  method: "POST",
  credentials: "include",   // keep for consistency; public route ignores cookie
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
})
```

### 6. Safety boundaries preserved

- No patient_name, date_of_birth, SVNR, or clinical data fields
- No Vapi API key or secret input
- No JWT in browser storage
- No diagnosis or medical advice copy
- production_phi_enabled never sent as true
- Staging demo badge preserved (can be re-framed as "Pilot Request Form — Staging")

### 7. Tests

- `backend/tests/test_clinic_onboarding_frontend_contract.py` (new): static tests verifying
  the updated onboarding page contains the required elements:
  - consent_pilot_contact checkbox
  - acknowledges_no_phi checkbox
  - preferred_language selector with de/en options
  - Success confirmation copy
  - No PHI fields (SVNR, date_of_birth, diagnosis)
  - No Vapi credential fields
  - No hardcoded JWT or sk- literals

### 8. Docs

- `docs/claude/CURRENT_STATE.md` — Module 133 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 134

## Constraints

- No PHI fields on the form
- No Vapi credential fields
- No production activation
- No automatic tenant creation
- No DSGVO-ready claim
- No secrets committed
- production_phi_enabled never sent as true
- Full test suite must remain green
