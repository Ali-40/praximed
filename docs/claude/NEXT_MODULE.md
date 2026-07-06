# Sprint 19 / Module 146 — Admin Vapi Binding Metadata UI

Status: pending implementation.

## Context

Module 145 complete:
- `backend/migrations/versions/0005_clinic_vapi_bindings.py` — migration for clinic_vapi_bindings table
- `backend/app/schemas/clinic_vapi_binding.py` — validates secret reference names; rejects actual secrets
- `backend/app/db/repositories/clinic_vapi_binding_repo.py` — async CRUD, parameterised SQL
- `backend/app/services/clinic_vapi_binding.py` — orchestration; no live Vapi calls; production_phi_enabled=False
- `backend/app/api/routes/clinic_vapi_bindings.py` — protected routes: POST/GET/PATCH
- `backend/app/api/router.py` — clinic_vapi_bindings wired
- `backend/tests/test_vapi_binding_metadata_backend_foundation.py` — 55 tests, all pass
- `docs/architecture/VAPI_BINDING_METADATA_BACKEND_FOUNDATION.md` — arch doc
- 4170/4170 backend tests pass
- Commit: Sprint 19 / Module 145 — Vapi binding metadata backend foundation

The clinic_vapi_bindings table and protected backend routes now exist.
Secret reference names are validated and stored; actual secret values are rejected.
No live Vapi API calls. production_phi_enabled is always False.
The C3–C8 readiness gate and Article 28/32 review remain open.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Add an admin UI panel in the developer console for creating and viewing Vapi binding
metadata records. The UI must enforce the same secret boundary as the backend: only
reference names accepted, no actual secret values entered, no live Vapi calls triggered,
no PHI.

## What Module 146 must implement

### 1. Frontend page

`frontend/app/developer-console/vapi-bindings/page.tsx` (new):

```
- LoadState: idle/loading/loaded/auth_error/not_found/error
- SubmitState: idle/submitting/submitted/error
- Clinic ID input + "Load binding" button
  → GET /clinics/{id}/vapi-bindings, credentials:'include'
  → Display existing binding if found: status badge, api_key_secret_ref label, webhook_secret_ref label,
    language_mode, created_at
  → "No Vapi binding found for this clinic." if 404

- Create binding form (only if no binding loaded, or new binding button):
  Fields: api_key_secret_ref (text, placeholder "VAPI_API_KEY_REF_CLINIC_XXX"),
          webhook_secret_ref (text, placeholder "VAPI_WEBHOOK_SECRET_REF_CLINIC_XXX"),
          language_mode (select: german_first/english_first/bilingual_auto)
  POST /clinics/{id}/vapi-bindings, credentials:'include'
  On success: show binding id, status=draft, production_phi_enabled=false
  On 422: "Secret reference names only — no actual API key values."

- Status update: select new status (draft/configured/disabled/revoked) + "Update status" button
  PATCH /clinic-vapi-bindings/{binding_id}/status, credentials:'include'

- Safety copy:
  "Reference names only. Never enter VAPI_API_KEY or webhook secret values here."
  "No live Vapi binding is made. production_phi_enabled remains false."
  "Production PHI remains NO-GO."

- Error states: 401/403 → "Admin session required."
- No sessionStorage, no localStorage
- No Vapi API key input field that accepts actual key values
- No webhook secret value field
```

### 2. Developer console link

`frontend/app/developer-console/page.tsx` (updated):
- Add "Vapi Binding Metadata" panel with link to /developer-console/vapi-bindings

### 3. api.ts helpers

`frontend/lib/api.ts` (updated):
```typescript
interface ClinicVapiBinding {
  id: string;
  clinic_id: string;
  api_key_secret_ref: string;
  webhook_secret_ref: string;
  language_mode: string;
  status: string;
  assistant_id: string | null;
  phone_number_id: string | null;
  production_phi_enabled: false;
  created_at: string;
  updated_at: string;
}

fetchClinicVapiBinding(clinicId: string): GET /clinics/{id}/vapi-bindings
createClinicVapiBinding(clinicId, apiKeyRef, webhookRef, languageMode): POST /clinics/{id}/vapi-bindings
updateClinicVapiBindingStatus(bindingId, status): PATCH /clinic-vapi-bindings/{id}/status
```

### 4. Tests

`backend/tests/test_admin_vapi_binding_metadata_ui_contract.py` (new — ≥50 static tests):
- Page file exists
- Safety copy: "Reference names only", "No live Vapi binding", "Production PHI remains NO-GO"
- Clinic ID input, Load binding button
- GET /vapi-bindings endpoint reference, credentials:include
- Create form fields: api_key_secret_ref, webhook_secret_ref, language_mode
- Placeholder guidance: VAPI_API_KEY_REF_CLINIC_XXX, VAPI_WEBHOOK_SECRET_REF_CLINIC_XXX
- POST /vapi-bindings endpoint reference
- Status update: draft/configured/disabled/revoked; PATCH endpoint
- Success states: binding id, status=draft, production_phi_enabled=false
- Error states: 401/403/422 handled
- Forbidden: no actual VAPI_API_KEY field, no webhook_secret value field, no sessionStorage
- api.ts: all three helpers defined, correct endpoints, credentials:include
- Developer console: links to /developer-console/vapi-bindings

### 5. Arch doc

`docs/architecture/ADMIN_VAPI_BINDING_METADATA_UI.md` (new):
- Purpose: admin panel for creating/viewing binding metadata records
- Secret boundary: reference names only; no actual secret values in UI
- No live Vapi API calls; no PHI; production_phi_enabled always false
- What this enables: operator can register secret reference labels without exposing secrets to browser

### 6. Docs

- `docs/claude/CURRENT_STATE.md` — Module 146 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 147

## Constraints

- No live Vapi API calls
- No actual VAPI_API_KEY, VAPI_WEBHOOK_SECRET values in any UI field
- No secrets in logs, tests, or docs
- No PHI. No patient data.
- production_phi_enabled remains False in all responses and UI
- No sessionStorage, no localStorage
- Full test suite must remain green
- Frontend build: PASS (all pages)
- Commit message:
  Sprint 19 / Module 146 — Admin Vapi binding metadata UI
