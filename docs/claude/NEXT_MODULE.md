# Sprint 19 / Module 137 — Live Tenant Provisioning Smoke Evidence

Status: pending implementation.

## Context

Module 136 complete:
- `frontend/app/developer-console/onboarding-requests/page.tsx` — "Clinic Shell Provisioning" panel with button, safety copy, success/error states
- `frontend/lib/api.ts` — `provisionClinicShell(requestId)` helper
- `backend/tests/test_admin_provision_clinic_shell_ui_contract.py` — 90 tests, all pass
- `docs/architecture/ADMIN_PROVISION_CLINIC_SHELL_UI.md`
- Full backend test suite and frontend build pass
- Commit: Sprint 19 / Module 136 — Admin provision clinic shell UI

The provisioning button exists and the backend service is ready. What we have
not yet verified is that the full end-to-end flow works in a staging environment:
submit → approve → provision → clinic row visible in DB.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Capture structured evidence that the full pilot onboarding → provisioning
flow works end-to-end in a staging (non-production) environment.

## What Module 137 must implement

### 1. Smoke test script

`backend/scripts/smoke_provision.py` (new):
- Submit a clinic onboarding request via POST /clinic-onboarding-requests
- Fetch the request via GET /clinic-onboarding-requests/{id}
- Update status to pilot_approved via PATCH /clinic-onboarding-requests/{id}/status
- Provision the clinic shell via POST /clinic-onboarding-requests/{id}/provision-clinic-shell
- Print structured result: clinic_id, clinic_slug, clinic_name, preferred_language,
  production_phi_enabled (must be false), already_provisioned, message
- Print a PASS / FAIL summary
- Assert: production_phi_enabled is false
- Assert: clinic_id is a non-empty string
- Assert: message contains "Production PHI remains disabled"
- Idempotency check: call provision again, assert already_provisioned=true
- Accepts BASE_URL as env var or CLI arg (default http://127.0.0.1:8000)
- No hardcoded credentials, no secrets committed
- Requires ADMIN_SESSION_COOKIE env var for authenticated calls

### 2. Tests

`backend/tests/test_live_provisioning_smoke_contract.py` (new):
Static tests verifying:
- Script file exists at backend/scripts/smoke_provision.py
- Script calls POST /clinic-onboarding-requests
- Script calls /provision-clinic-shell
- Script asserts production_phi_enabled is false
- Script asserts already_provisioned=true on second call
- Script has PASS/FAIL output
- No hardcoded DATABASE_URL, no hardcoded passwords, no hardcoded secrets
- Script reads BASE_URL from env or CLI
- Script reads ADMIN_SESSION_COOKIE from env

### 3. Docs

- `docs/architecture/LIVE_PROVISIONING_SMOKE_EVIDENCE.md` — document the smoke
  script, how to run it, and what constitutes a PASS
- `docs/claude/CURRENT_STATE.md` — Module 137 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 138

## Constraints

- No production PHI activation
- No Vapi credentials collected or committed
- ADMIN_SESSION_COOKIE must be read from env, never hardcoded
- BASE_URL must be configurable
- production_phi_enabled must be asserted false in smoke script
- Full test suite must remain green
- Frontend build must pass
- Commit message:
  Sprint 19 / Module 137 — Live tenant provisioning smoke evidence
