# Sprint 19 / Module 143 — Live Vapi Assistant Config Preview Smoke Evidence

Status: pending implementation.

## Context

Module 142 complete:
- `frontend/app/developer-console/vapi-config/page.tsx` — Vapi config preview page
- `frontend/app/developer-console/page.tsx` — updated with Vapi config preview panel
- `frontend/lib/api.ts` — fetchVapiAssistantConfigPack + VapiAssistantConfigPack interface
- `backend/tests/test_admin_vapi_assistant_config_preview_ui_contract.py` — 73 tests, all pass
- `docs/architecture/ADMIN_VAPI_ASSISTANT_CONFIG_PREVIEW_UI.md`
- 4007/4007 backend tests pass
- Frontend build: PASS (9/9 pages)
- Commit: Sprint 19 / Module 142 — Admin Vapi assistant config preview UI

The Vapi assistant config preview UI is live on staging. Admin can load the
generated config pack for a provisioned clinic. No live smoke evidence exists
yet documenting that the UI actually works end-to-end against the staging backend.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Document real live staging evidence that the Vapi assistant config preview UI
works end-to-end: loading the config pack for a provisioned staging clinic and
verifying the German prompt, English fallback, required capture fields, tool
schema, and safety flags are visible and correct.

## What Module 143 must implement

### 1. Smoke evidence doc

`docs/runtime/LIVE_VAPI_ASSISTANT_CONFIG_PREVIEW_SMOKE_EVIDENCE.md` (new):

**Required sections:**
- Purpose
- Current Result: `PASS`
- Preconditions:
  - Admin session active (staging)
  - Clinic shell provisioned (use staging clinic_id 1a5bbc75-c1b0-4488-94aa-64b3f1c50056)
  - Frontend URL: https://praximed.vercel.app/developer-console/vapi-config
  - Module 142 commit deployed
- Live UI Evidence:
  - Opened page with staging clinic_id
  - Clicked "Load config pack"
  - Config pack loaded successfully (HTTP 200)
- German Prompt Evidence:
  - first_message_de visible
  - system_prompt_de visible with KI-Rezeption, keine Diagnose, Notruf 144
- English Fallback Evidence:
  - first_message_en visible
  - system_prompt_en visible with AI receptionist, no diagnosis, call 144
- Required Capture Fields Evidence:
  - patient_name, phone, reason, preferred_time, language_preference, urgency_level all listed
- Tool Schema Evidence:
  - JSON rendered in code block
  - capture_appointment_request tool visible
  - X-Vapi-Service-Name, X-Vapi-Clinic-Id, X-Vapi-Scopes header names visible
  - No secret values shown
- Safety Flags Evidence:
  - production_phi_enabled: false
  - recording_ingestion_enabled: false
  - transcript_ingestion_enabled: false
- Safety Boundaries:
  - No PHI displayed or entered
  - No Vapi credentials entered or shown
  - No sessionStorage or localStorage used
  - No live Vapi binding triggered
  - No production activation
- What This Proves:
  - GET /clinics/{id}/vapi-assistant-config-pack returns correct config pack
  - German-first prompt is complete and correct
  - English fallback prompt is complete and correct
  - Required capture fields all present
  - Tool schema renders correctly
  - All safety flags are false
  - Admin UI round-trip works end-to-end on staging
  - credentials: 'include' session auth works for this endpoint
- What This Does Not Prove:
  - Production readiness
  - DSGVO compliance
  - Vapi assistant actual binding
  - Bilingual audio testing
  - Security hardening
- Remaining Blockers: C3–C8 as per Module 138 arch doc

### 2. Tests

`backend/tests/test_live_vapi_assistant_config_preview_smoke_evidence_contract.py` (new):

Static tests verifying:
- Doc exists
- PASS result
- Module 143 referenced
- Frontend URL present
- Clinic ID referenced
- German-first prompt section: KI-Rezeption, keine Diagnose, Notruf 144
- English fallback: AI receptionist, no diagnosis, call 144
- Required capture fields: patient_name, phone, reason
- Tool schema: capture_appointment_request, X-Vapi-Service-Name
- Safety flags: production_phi_enabled=false, recording=false, transcript=false
- No PHI, no Vapi credentials, production PHI remains NO-GO
- What proves / what does not prove sections
- Remaining blockers C3–C8

### 3. Docs

- `docs/claude/CURRENT_STATE.md` — Module 143 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 144

## Constraints

- No production PHI activation
- No Vapi credentials shown or collected
- No live Vapi binding
- Production PHI remains NO-GO
- Full test suite must remain green
- Commit message:
  Sprint 19 / Module 143 — Live Vapi assistant config preview smoke evidence
