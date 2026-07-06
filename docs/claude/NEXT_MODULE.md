# Sprint 19 / Module 136 — Admin Provision Clinic Shell UI

Status: pending implementation.

## Context

Module 135 complete:
- `backend/app/services/tenant_provisioning.py` — safe clinic shell provisioning service
- `backend/app/api/routes/clinic_onboarding.py` — POST /clinic-onboarding-requests/{id}/provision-clinic-shell
- `backend/tests/test_tenant_provisioning_backend_foundation.py` — 47 tests, all pass
- `docs/architecture/TENANT_PROVISIONING_BACKEND_FOUNDATION.md`
- 3541/3541 backend tests pass
- No frontend changes (build remains clean at 9/9 pages)
- Commit: Sprint 19 / Module 135 — Tenant provisioning backend foundation

The backend provisioning endpoint exists and is protected. There is no frontend
UI to trigger it — admin must currently use curl or an API tool to provision.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Add a "Provision clinic shell" button to the internal onboarding review console
so that admin/staff can trigger clinic shell provisioning for pilot_approved requests
directly from the UI.

## What Module 136 must implement

### 1. Frontend — provision button in `/developer-console/onboarding-requests`

`frontend/app/developer-console/onboarding-requests/page.tsx` (updated):
- In the detail panel, below the status update section:
  - Show "Provision clinic shell" button ONLY when selected.status === 'pilot_approved'
  - Button calls POST /clinic-onboarding-requests/{id}/provision-clinic-shell
  - `credentials: 'include'`
  - Loading state: "Provisioning…"
  - Success state: show clinic_id, clinic_name, clinic_slug, preferred_language
  - Success message: "Clinic shell provisioned. Production PHI remains disabled."
  - Error state: safe error message, no stack traces
  - If already_provisioned=true: show "Already provisioned. clinic_id: …"
  - Safety copy visible: "Provisioning does not activate production PHI."
  - Button is disabled when status is not pilot_approved
  - Button is disabled during provisioning (prevent double-click)
- `ProvisionState` = 'idle' | 'provisioning' | 'provisioned' | 'error'
- No sessionStorage, no localStorage
- No Vapi credentials displayed or collected
- No patient data

### 2. api.ts helper

`frontend/lib/api.ts` (updated):
- `provisionClinicShell(requestId: string)` → POST /clinic-onboarding-requests/{requestId}/provision-clinic-shell
  - credentials: 'include'
  - Returns: { ok, clinic_id, clinic_name, clinic_slug, preferred_language, production_phi_enabled, message, already_provisioned }

### 3. Tests

`backend/tests/test_admin_provision_clinic_shell_ui_contract.py` (new):
Static tests verifying:
- Review console page has "Provision" button or text
- Button enabled only for pilot_approved (or conditional render)
- Calls POST /clinic-onboarding-requests/ and /provision-clinic-shell
- credentials: 'include'
- Shows clinic_id on success
- Shows "Production PHI remains disabled" or "does not activate production PHI"
- Shows safe error state
- No sessionStorage, no localStorage
- No Vapi credentials shown
- api.ts has provisionClinicShell
- api.ts calls /provision-clinic-shell

### 4. Docs

- `docs/architecture/INTERNAL_ONBOARDING_REVIEW_CONSOLE.md` — update: Module 136 adds provision button
- `docs/claude/CURRENT_STATE.md` — Module 136 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 137

## Constraints

- No production PHI activation
- No Vapi credentials collected or displayed
- No automatic provisioning (button must be clicked explicitly)
- Button visible only when status = pilot_approved
- Safety copy must be visible near the button
- Full test suite must remain green
- Frontend build must pass
- Commit message:
  Sprint 19 / Module 136 — Admin provision clinic shell UI
