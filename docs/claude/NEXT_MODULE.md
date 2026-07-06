# Sprint 19 / Module 140 — Live Tenant Language Settings Smoke Evidence

Status: pending implementation.

## Context

Module 139 complete:
- `frontend/app/developer-console/language-settings/page.tsx` — language settings admin page
- `frontend/app/developer-console/page.tsx` — updated with language settings panel
- `frontend/lib/api.ts` — fetchClinicLanguageSettings + updateClinicLanguageSettings helpers
- `backend/tests/test_admin_tenant_language_settings_ui_contract.py` — 67 tests, all pass
- `docs/architecture/ADMIN_TENANT_LANGUAGE_SETTINGS_UI.md`
- 3805/3805 backend tests pass
- Frontend build: PASS (10/10 pages)
- Commit: Sprint 19 / Module 139 — Admin tenant language settings UI

The language settings UI exists and is live on staging. Admin can now load and
update clinic language settings from the browser. No live smoke evidence exists yet
documenting that the UI actually works end-to-end against the staging backend.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Document real live staging evidence that the language settings admin UI works
end-to-end: loading German-first defaults for a provisioned clinic, updating a
field, and observing the change reflected on reload.

## What Module 140 must implement

### 1. Smoke evidence doc

`docs/runtime/LIVE_TENANT_LANGUAGE_SETTINGS_SMOKE_EVIDENCE.md` (new):

**Required sections:**
- Purpose
- Current Result: `PASS` or `PARTIAL` (if full round-trip not yet testable from staging)
- Preconditions:
  - Admin session active (staging)
  - Clinic shell provisioned (use the Demo Wahlarzt Praxis Wien clinic_id from Module 137)
  - Frontend URL: https://praximed.vercel.app/developer-console/language-settings
  - Module 139 commit deployed
- Live UI Evidence:
  - Loaded page with clinic_id
  - German-first defaults displayed (primary_language=de, fallback_language=en,
    supported_languages=["de","en"], vapi_assistant_language_mode=german_first,
    clinic_ui_language=de)
  - updated_at value shown
- Update Evidence:
  - Changed a field (e.g. clinic_ui_language de → en)
  - Clicked "Save language settings"
  - "Language settings saved" confirmed
  - Reloaded page — updated value persisted
- Safety Boundaries:
  - No PHI collected or displayed
  - No Vapi credentials entered or stored
  - No sessionStorage or localStorage used
  - production_phi_enabled remained false
  - No production activation
- What This Proves:
  - GET /clinics/{id}/language-settings returns correct German-first defaults
  - PATCH /clinics/{id}/language-settings persists partial updates
  - Admin UI round-trip works end-to-end on staging
  - credentials: 'include' session auth works for this endpoint
- What This Does Not Prove:
  - Production readiness
  - DSGVO compliance
  - Vapi assistant binding
- Remaining Blockers: C3–C8 as per Module 138 arch doc

### 2. Tests

`backend/tests/test_live_tenant_language_settings_smoke_evidence_contract.py` (new):

Static tests verifying:
- Doc exists
- PASS or PARTIAL result stated
- Module 140 referenced
- Frontend URL present
- Clinic ID referenced
- German-first defaults mentioned (primary_language=de, german_first, fallback_language)
- Load and update evidence sections present
- "Language settings saved" confirmed
- Safety: no PHI, no Vapi credentials, production_phi_enabled=false, NO-GO
- What proves / what does not prove sections present
- Remaining blockers (C3–C8) referenced

### 3. Docs

- `docs/claude/CURRENT_STATE.md` — Module 140 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 141

## Constraints

- No production PHI activation
- No Vapi credentials shown or collected
- No sessionStorage, no localStorage
- Production PHI remains NO-GO
- Full test suite must remain green
- Frontend build must pass
- Commit message:
  Sprint 19 / Module 140 — Live tenant language settings smoke evidence
