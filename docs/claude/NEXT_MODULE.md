# Sprint 19 / Module 145 — Vapi Binding Metadata Backend Foundation

Status: pending implementation.

## Context

Module 144 complete:
- `docs/architecture/VAPI_CREDENTIAL_BINDING_SECRET_BOUNDARY.md` — hard secret boundary defined
- `backend/tests/test_vapi_credential_binding_secret_boundary_contract.py` — 41 tests, all pass
- 4115/4115 backend tests pass
- No frontend changes. No migration. No live Vapi API calls. No secrets stored.
- Commit: Sprint 19 / Module 144 — Vapi credential binding design and secret boundary

The secret boundary is now documented and enforced by contract tests. The
`clinic_vapi_bindings` table design is finalised (reference names only, no secret
values). The readiness gate (C3–C8, Article 28/32) remains open.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Create the `clinic_vapi_bindings` database migration, repository layer, and
protected internal backend routes for storing Vapi binding metadata. No live Vapi
API calls. No actual secrets stored — only reference names (api_key_secret_ref,
webhook_secret_ref). No PHI. All safety flags hardcoded False.

## What Module 145 must implement

### 1. Migration

`backend/migrations/versions/XXXX_clinic_vapi_bindings.py` (new):

```sql
CREATE TABLE IF NOT EXISTS clinic_vapi_bindings (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    assistant_id            TEXT,
    phone_number_id         TEXT,
    vapi_project_id         TEXT,
    api_key_secret_ref      TEXT        NOT NULL,
    webhook_secret_ref      TEXT        NOT NULL,
    assistant_config_version TEXT,
    language_mode           TEXT        NOT NULL DEFAULT 'german_first',
    status                  TEXT        NOT NULL DEFAULT 'draft',
    created_by_user_id      UUID,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_clinic_vapi_bindings_clinic_id
    ON clinic_vapi_bindings(clinic_id);
```

### 2. Repository

`backend/app/db/repositories/vapi_binding_repo.py` (new):

```python
async def create_vapi_binding(pool, clinic_id, api_key_secret_ref, webhook_secret_ref,
                               language_mode, created_by_user_id) -> dict
async def get_vapi_binding(pool, clinic_id) -> dict | None
async def update_vapi_binding_status(pool, clinic_id, status, actor_user_id) -> dict
async def set_vapi_assistant_ids(pool, clinic_id, assistant_id, phone_number_id,
                                  vapi_project_id, assistant_config_version) -> dict
```

Rules:
- `api_key_secret_ref` and `webhook_secret_ref` are stored as-is — never resolved
  or logged
- No VAPI_API_KEY, no VAPI_WEBHOOK_SECRET actual values stored or returned
- All functions raise `ClinicNotFoundError` for unknown clinic_id

### 3. Schemas

`backend/app/schemas/vapi_binding.py` (new):

```python
class ClinicVapiBindingCreate(BaseModel):
    clinic_id: str
    api_key_secret_ref: str        # reference name only, e.g. VAPI_API_KEY_CLINIC_abc
    webhook_secret_ref: str        # reference name only
    language_mode: str = "german_first"

class ClinicVapiBindingRead(BaseModel):
    id: str
    clinic_id: str
    assistant_id: str | None
    phone_number_id: str | None
    vapi_project_id: str | None
    api_key_secret_ref: str        # reference name only — not the secret value
    webhook_secret_ref: str        # reference name only
    assistant_config_version: str | None
    language_mode: str
    status: str                    # draft / configured / disabled / revoked
    created_by_user_id: str | None
    created_at: str
    updated_at: str
    production_phi_enabled: bool = False   # always False

class ClinicVapiBindingStatus(BaseModel):
    clinic_id: str
    is_bound: bool
    status: str | None
    assistant_id: str | None
    phone_number_id: str | None
    api_key_secret_ref: str | None  # masked label only
    webhook_secret_ref: str | None  # masked label only
    production_phi_enabled: bool = False
    binding_blocked_reason: str | None
```

Note: No VAPI_API_KEY value in any schema. `production_phi_enabled` always False.

### 4. Routes (internal/admin only)

`backend/app/api/routes/vapi_binding.py` (new):

```python
router = APIRouter(prefix="/internal/clinics", tags=["vapi-binding"])

# POST /internal/clinics/{clinic_id}/vapi-binding
# Creates binding metadata record. Requires admin auth. No live Vapi call.

# GET /internal/clinics/{clinic_id}/vapi-binding
# Returns binding metadata (reference names only). Requires admin auth.

# PATCH /internal/clinics/{clinic_id}/vapi-binding/status
# Updates binding status (draft/configured/disabled/revoked). Requires admin auth.
```

All routes:
- Require `get_current_user` with role="admin"
- Return 404 for unknown clinic_id
- Never return or accept actual secret values
- Create audit log entries for all mutations

### 5. Tests

`backend/tests/test_vapi_binding_repo.py` (new):
- create_vapi_binding: stores reference names, not secrets
- get_vapi_binding: returns dict or None
- update_vapi_binding_status: valid status transitions
- ClinicNotFoundError for unknown clinic
- No VAPI_API_KEY value in any stored row
- production_phi_enabled always False in schema

`backend/tests/test_vapi_binding_routes.py` (new):
- POST creates binding — 201, returns ClinicVapiBindingRead
- GET returns binding — 200
- PATCH updates status — 200
- 401 for unauthenticated
- 403 for non-admin
- 404 for unknown clinic
- No secret values in any response body
- production_phi_enabled=False in all responses

`backend/tests/test_vapi_binding_contract.py` (new — static):
- Schema has ClinicVapiBindingCreate, ClinicVapiBindingRead, ClinicVapiBindingStatus
- Schema has api_key_secret_ref, webhook_secret_ref
- Schema has production_phi_enabled always False
- Schema has no VAPI_API_KEY value field
- Schema has binding_blocked_reason
- Routes file has /internal prefix (admin-only)
- Routes file has no VAPI_API_KEY resolution
- Routes file has audit log call

### 6. Docs

- `docs/claude/CURRENT_STATE.md` — Module 145 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 146

## Constraints

- No live Vapi API calls
- No VAPI_API_KEY resolved, stored, or returned anywhere
- No secrets in logs, tests, or docs
- No browser secret input
- production_phi_enabled remains False in all schemas and responses
- Full test suite must remain green
- Migration uses next available version number
- Commit message:
  Sprint 19 / Module 145 — Vapi binding metadata backend foundation
