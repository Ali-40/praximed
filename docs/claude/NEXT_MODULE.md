# Sprint 19 / Module 139 — Admin Tenant Language Settings UI

Status: pending implementation.

## Context

Module 138 complete:
- `backend/app/schemas/clinic_language_settings.py` — ClinicLanguageSettingsRead + ClinicLanguageSettingsUpdate
- `backend/app/services/clinic_language_settings.py` — get/update with German-first defaults, locale↔lang mapping, JSON config file storage
- `backend/app/api/routes/clinic_language_settings.py` — GET/PATCH /clinics/{id}/language-settings (protected)
- `backend/app/services/tenant_provisioning.py` — updated to write language_config on clinic shell creation
- `backend/tests/test_tenant_language_settings_api_foundation.py` — 87 tests, all pass
- `docs/architecture/TENANT_LANGUAGE_SETTINGS_API_FOUNDATION.md`
- 3738/3738 backend tests pass
- No frontend changes
- Commit: Sprint 19 / Module 138 — Tenant language settings API foundation

The language settings API exists and is protected. There is no frontend UI to
read or update it — admin must currently use curl or an API tool.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Add a "Language Settings" panel to the internal developer/admin console so that
admin/staff can view and update clinic language settings for a provisioned clinic
directly from the browser UI.

## What Module 139 must implement

### 1. Frontend — language settings panel in `/developer-console`

`frontend/app/developer-console/page.tsx` (updated):
- Add a new ConsolePanel "Clinic Language Settings" (after the Pilot Request Review panel)
- Panel includes:
  - Input for clinic_id (text field)
  - "Load settings" button → GET /clinics/{id}/language-settings
  - Display: primary_language, fallback_language, supported_languages,
    default_patient_language, vapi_assistant_language_mode, clinic_ui_language, updated_at
  - Select dropdowns for updatable fields
  - "Update settings" button → PATCH /clinics/{id}/language-settings
  - Loading, success, error states
  - Safety copy: "Language settings do not activate production PHI."
  - No PHI fields
  - No Vapi credentials
  - No sessionStorage, no localStorage
  - credentials: 'include' on all fetches

### 2. api.ts helpers

`frontend/lib/api.ts` (updated):
- `getClinicLanguageSettings(clinicId: string)` → GET /clinics/{clinicId}/language-settings
- `updateClinicLanguageSettings(clinicId: string, update: object)` → PATCH /clinics/{clinicId}/language-settings
- Both: credentials: 'include'

### 3. Tests

`backend/tests/test_admin_tenant_language_settings_ui_contract.py` (new):
Static tests verifying:
- Developer console page has "Language Settings" or "language settings" text
- Panel has clinic_id input or field
- "Load settings" or equivalent trigger
- Shows primary_language, vapi_assistant_language_mode
- PATCH /clinics/ and /language-settings called
- credentials: 'include'
- Safety copy about no production PHI
- No sessionStorage, no localStorage
- No Vapi API key field
- api.ts has getClinicLanguageSettings
- api.ts has updateClinicLanguageSettings

### 4. Docs

- `docs/architecture/INTERNAL_ONBOARDING_REVIEW_CONSOLE.md` — update: Module 139 adds language settings panel
- `docs/claude/CURRENT_STATE.md` — Module 139 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 140

## Constraints

- No production PHI activation
- No Vapi credentials shown or collected
- No sessionStorage, no localStorage
- credentials: 'include' on all fetches
- German-first defaults displayed correctly
- Safety copy visible near update button
- Full test suite must remain green
- Frontend build must pass
- Commit message:
  Sprint 19 / Module 139 — Admin tenant language settings UI
