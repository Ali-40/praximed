# Sprint 19 / Module 144 — Vapi Credential Binding Design and Secret Boundary

Status: pending implementation.

## Context

Module 143 complete:
- `docs/runtime/LIVE_VAPI_ASSISTANT_CONFIG_PREVIEW_SMOKE_EVIDENCE.md` — PASS
- `backend/tests/test_live_vapi_assistant_config_preview_smoke_evidence_contract.py` — 67 tests, all pass
- 4074/4074 backend tests pass
- No frontend changes
- Commit: Sprint 19 / Module 143 — Live Vapi assistant config preview smoke evidence

The Vapi assistant configuration pack can be generated and previewed per clinic.
The German/English prompts, capture tool schema, safety rules, and readiness flags
all work end-to-end on staging. However, no mechanism exists yet to bind real Vapi
credentials to a clinic — no VAPI_API_KEY, no Vapi phone number binding, no
real assistant creation on Vapi's platform.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Design the safe backend-only credential binding structure for Vapi. This module
is architecture + design only: no live Vapi API calls yet, no secrets in docs or
tests, no browser secret input, no environment variable exposure. The output is a
clear, safe architecture doc and accompanying contract tests.

## What Module 144 must implement

### 1. Architecture doc

`docs/architecture/VAPI_CREDENTIAL_BINDING_DESIGN.md` (new):

**Required sections:**
- Purpose: what Vapi credential binding achieves (linking a clinic to a Vapi assistant)
- Secret boundary: where secrets live (environment variables only, never in browser/DB/logs)
- Credential types:
  - `VAPI_API_KEY` — Vapi account API key (environment variable, never in browser)
  - Vapi phone number ID — which phone number the assistant answers
  - Vapi assistant ID — the created/configured assistant's ID on Vapi platform
- Binding flow (design only — not implemented):
  1. Admin triggers binding via backend admin endpoint (NOT browser form)
  2. Backend reads VAPI_API_KEY from environment
  3. Backend calls Vapi API to create or update assistant with config pack
  4. Backend stores only the returned vapi_assistant_id and vapi_phone_number_id
     in the clinics table or a new vapi_binding table (non-secret references)
  5. No VAPI_API_KEY stored in DB
  6. Audit log entry created
- DB design (proposed, no migration yet):
  - New table `clinic_vapi_bindings` (to be created in a future migration):
    - clinic_id (FK)
    - vapi_assistant_id (non-secret, public reference)
    - vapi_phone_number_id (non-secret, public reference)
    - bound_at (timestamp)
    - bound_by (actor user_id)
    - is_active (bool)
  - No API key columns — VAPI_API_KEY stays in environment
- Safety constraints:
  - VAPI_API_KEY never written to DB
  - VAPI_API_KEY never returned from any API endpoint
  - VAPI_API_KEY never logged
  - VAPI_API_KEY never shown in browser
  - production_phi_enabled remains False until explicit hardening sign-off
  - No live Vapi calls until C3–C8 are resolved
- What remains before binding can be activated:
  - C3 — Secrets hardening complete
  - C4 — PHI logging/redaction hardening complete
  - C5 — Tenant isolation verified
  - C6 — Audit trail hardened
  - C7 — Backup/restore runbook complete
  - C8 — Legal / DSGVO review complete
  - VAPI_API_KEY set in Railway environment
  - Vapi phone number provisioned
  - production_phi_enabled: false remains enforced

### 2. Schema (design-only, no migration)

`backend/app/schemas/vapi_binding.py` (new):

```python
class ClinicVapiBindingRead(BaseModel):
    clinic_id: str
    vapi_assistant_id: str        # non-secret public reference
    vapi_phone_number_id: str     # non-secret public reference
    bound_at: str
    bound_by: str | None
    is_active: bool
    production_phi_enabled: bool  # always False

class ClinicVapiBindingStatus(BaseModel):
    clinic_id: str
    is_bound: bool
    vapi_assistant_id: str | None
    vapi_phone_number_id: str | None
    production_phi_enabled: bool  # always False
    binding_blocked_reason: str | None  # e.g. "C3-C8 hardening not complete"
```

Note: No VAPI_API_KEY field in any schema. Schema is design documentation — no
backend migration runs in this module.

### 3. Tests

`backend/tests/test_vapi_credential_binding_design.py` (new):

Static tests verifying:
- Arch doc exists
- Arch doc mentions VAPI_API_KEY is environment-variable only
- Arch doc mentions no VAPI_API_KEY in DB
- Arch doc mentions no VAPI_API_KEY in browser
- Arch doc mentions no VAPI_API_KEY in logs
- Arch doc mentions vapi_assistant_id (non-secret reference)
- Arch doc mentions vapi_phone_number_id (non-secret reference)
- Arch doc mentions audit log
- Arch doc mentions production_phi_enabled remains False
- Arch doc mentions C3–C8 blockers
- Arch doc mentions no live Vapi calls until blockers resolved
- Schema has ClinicVapiBindingRead
- Schema has ClinicVapiBindingStatus
- Schema production_phi_enabled: always False
- Schema no VAPI_API_KEY field
- Schema has binding_blocked_reason

### 4. Docs

- `docs/claude/CURRENT_STATE.md` — Module 144 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 145

## Constraints

- No live Vapi API calls
- No VAPI_API_KEY in any doc, test, or source file (except as a label referencing the env var name)
- No secrets in logs
- No browser secret input
- production_phi_enabled remains False in all schemas
- Full test suite must remain green
- No migration runs
- Commit message:
  Sprint 19 / Module 144 — Vapi credential binding design and secret boundary
