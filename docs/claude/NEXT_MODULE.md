# Sprint 19 / Module 142 — Admin Vapi Assistant Config Preview UI

Status: pending implementation.

## Context

Module 141 complete:
- `backend/app/schemas/vapi_assistant_config.py` — VapiAssistantConfigPack schema
- `backend/app/services/vapi_assistant_config.py` — build_vapi_assistant_config_pack service
- `backend/app/api/routes/vapi_assistant_config.py` — GET /clinics/{id}/vapi-assistant-config-pack
- `backend/app/api/router.py` — vapi_assistant_config router registered
- `backend/tests/test_vapi_assistant_config_pack_per_tenant.py` — 81 tests, all pass
- `docs/architecture/VAPI_ASSISTANT_CONFIGURATION_PACK_PER_TENANT.md`
- 3934/3934 backend tests pass
- No frontend changes
- Commit: Sprint 19 / Module 141 — Vapi assistant configuration pack per tenant

The Vapi assistant configuration pack can be generated per clinic via a protected
backend route. There is no frontend UI to preview it — admin must currently use
curl or an API tool to fetch the config pack.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Add an internal admin UI page that fetches and displays the Vapi assistant
configuration pack for a provisioned clinic. The page allows admin to review
the German/English prompts, required capture fields, tool schema, and safety
rules before any live Vapi binding happens.

## What Module 142 must implement

### 1. Frontend — Vapi config preview page

`frontend/app/developer-console/vapi-config/page.tsx` (new):

- Admin internal page under developer console.
- Clinic ID text input + "Load config" button.
- GET /clinics/{id}/vapi-assistant-config-pack with `credentials: 'include'`.
- Display sections:
  - Language mode: primary_language, fallback_language, vapi_assistant_language_mode
  - German prompt: system_prompt_de (code block / pre-wrap)
  - English prompt: system_prompt_en (code block / pre-wrap)
  - First messages: first_message_de, first_message_en
  - Required capture fields: list
  - Tool schema: JSON display (target endpoint, required fields)
  - Safety rules: list
  - Forbidden claims: list
  - Safety flags: production_phi_enabled, recording_ingestion_enabled, transcript_ingestion_enabled
  - Generated at timestamp
- Safety copy: "This is a read-only preview. No Vapi binding occurs."
  "No PHI. No secrets. No Vapi credentials."
  "Production PHI remains NO-GO."
- Error states: 401/403 → "Admin session required.", 404 → "Clinic not found or no access."
- No sessionStorage, no localStorage.
- credentials: 'include' on all fetches.
- ADMIN / STAGING badge.

### 2. Developer console nav

`frontend/app/developer-console/page.tsx` (updated):

- Add new panel "Vapi Assistant Config Preview" (after Tenant Language Settings panel).
- Link: "Preview Vapi config →" → `/developer-console/vapi-config`.
- Safety copy: "Read-only preview. No live Vapi binding. No secrets."

### 3. api.ts helper

`frontend/lib/api.ts` (updated):

- `fetchVapiAssistantConfigPack(clinicId: string): Promise<VapiAssistantConfigPack>`
  - GET /clinics/{clinicId}/vapi-assistant-config-pack
  - credentials: 'include'
- `VapiAssistantConfigPack` interface with all fields from the schema.

### 4. Tests

`backend/tests/test_admin_vapi_config_preview_ui_contract.py` (new):

Static contract tests verifying:
- Page file exists
- Page has "Vapi" in title / header
- Page has clinic ID input
- Page has "Load config" button or equivalent
- Page calls /vapi-assistant-config-pack endpoint
- Page shows system_prompt_de
- Page shows system_prompt_en
- Page shows required_capture_fields
- Page shows safety_rules
- Page shows production_phi_enabled
- Page uses credentials: 'include'
- Page has "No Vapi binding" safety copy
- Page has "No PHI" copy
- Page has NO-GO copy
- Page has Admin session required error state
- Page handles 401/403/404
- No sessionStorage, no localStorage
- No Vapi API key field
- No webhook secret field
- Developer console links to /developer-console/vapi-config
- api.ts has fetchVapiAssistantConfigPack
- api.ts has VapiAssistantConfigPack interface
- api.ts no sessionStorage, no localStorage

### 5. Docs

- `docs/architecture/ADMIN_VAPI_CONFIG_PREVIEW_UI.md` (new)
- `docs/claude/CURRENT_STATE.md` — Module 142 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 143

## Constraints

- Read-only UI — no write operations to Vapi
- No live Vapi API calls
- No PHI in response or display
- No secrets shown or collected
- No sessionStorage, no localStorage
- credentials: 'include' on all fetches
- Production PHI remains NO-GO
- Full test suite must remain green
- Frontend build must pass
- Commit message:
  Sprint 19 / Module 142 — Admin Vapi assistant config preview UI
