# Sprint 19 / Module 135 — Tenant Provisioning Backend Foundation

Status: pending implementation.

## Context

Module 134 complete:
- `frontend/app/developer-console/onboarding-requests/page.tsx` — internal review console
- `frontend/app/developer-console/page.tsx` — updated with "Pilot Request Review" panel and link
- `frontend/lib/api.ts` — fetchClinicOnboardingRequests, updateClinicOnboardingRequestStatus added
- `backend/tests/test_internal_onboarding_review_console_contract.py` — 48 tests, all pass
- `docs/architecture/INTERNAL_ONBOARDING_REVIEW_CONSOLE.md`
- Frontend build: ✓ clean (9/9 pages)
- 3450/3450 backend tests pass
- Commit: Sprint 19 / Module 134 — Internal clinic onboarding review console

The onboarding review console allows staff to move a request to `pilot_approved`, but
there is no backend provisioning mechanism — tenant creation requires a separate manual
process. Module 135 lays the foundational backend for future tenant provisioning.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Build the backend foundation for clinic tenant provisioning — database table, migration,
Pydantic schemas, repository, and protected admin API routes. No tenant is created
automatically from any onboarding request status change.

## What Module 135 must implement

### 1. Database — `tenants` table

`backend/app/db/schema.sql` (updated):
- New table `tenants`:
  - `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
  - `clinic_name` TEXT NOT NULL
  - `clinic_id` TEXT UNIQUE NOT NULL  — short slug for URL/scope scoping
  - `onboarding_request_id` UUID REFERENCES clinic_onboarding_requests(id)
  - `specialty` TEXT
  - `city` TEXT
  - `preferred_language` TEXT NOT NULL DEFAULT 'de' CHECK (... IN ('de','en'))
  - `fallback_language` TEXT NOT NULL DEFAULT 'en'
  - `supported_languages` JSONB NOT NULL DEFAULT '["de","en"]'
  - `status` TEXT NOT NULL DEFAULT 'provisioning' CHECK (... IN ('provisioning','active','suspended','archived'))
  - `production_phi_enabled` BOOLEAN NOT NULL DEFAULT false CHECK (production_phi_enabled = false)
  - `vapi_assistant_id` TEXT  — nullable; set later via separate secure admin process
  - `vapi_phone_number_id` TEXT  — nullable
  - `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
  - `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
  - `created_by` TEXT  — admin username who provisioned
- Indexes: clinic_id (UNIQUE), status, onboarding_request_id

### 2. Migration

`backend/migrations/versions/0005_tenants.py`:
- `revision = "0005_tenants"`
- `down_revision = "0004_clinic_onboarding_requests"`
- `upgrade()`: CREATE TABLE IF NOT EXISTS tenants + indexes
- `downgrade()`: DROP TABLE IF EXISTS tenants (+ DROP indexes)

### 3. Pydantic schemas

`backend/app/schemas/tenant.py` (new):
- `TenantCreate`: clinic_name, clinic_id (slug), specialty, city, preferred_language, onboarding_request_id (optional)
  - Validates clinic_id: alphanumeric + hyphens, 3–64 chars, lowercase
  - Validates preferred_language in {de, en}
  - production_phi_enabled is NOT accepted from input — always false
  - vapi_assistant_id / vapi_phone_number_id are NOT accepted from input
- `TenantResponse`: ok, tenant: dict
- `TenantListResponse`: ok, tenants: list[dict], total: int

### 4. Repository

`backend/app/db/repositories/tenant_repo.py` (new):
- `create_tenant(pool, data: dict) -> dict`
  - Hardcodes `production_phi_enabled = false` in INSERT
  - Returns the created row
- `get_tenant_by_id(pool, tenant_id: UUID) -> dict | None`
- `get_tenant_by_clinic_id(pool, clinic_id: str) -> dict | None`
- `list_tenants(pool, status: str | None, limit: int) -> list[dict]`
- `update_tenant_status(pool, tenant_id: UUID, status: str) -> dict`

### 5. API routes

`backend/app/api/routes/tenants.py` (new):
```python
router = APIRouter(prefix="/tenants", tags=["tenants"])
# All routes require get_current_user — no public endpoint

@router.post("", status_code=201)   # protected admin
@router.get("")                      # protected
@router.get("/{tenant_id}")          # protected
@router.patch("/{tenant_id}/status") # protected
```
- `POST /tenants` does NOT automatically link from onboarding approval
- Safety copy in response: "Tenant created in provisioning state. Vapi credentials and production PHI activation require a separate secure process."
- `production_phi_enabled` is never returned as `true` — DB constraint enforces this

### 6. Router wiring

`backend/app/api/router.py` (updated):
- `from backend.app.api.routes import tenants`
- `api_router.include_router(tenants.router)`

### 7. Tests

`backend/tests/test_tenant_provisioning_backend_foundation.py` (new):
- Schema SQL contract: tenants table, columns, CHECK constraints, indexes
- Migration: file exists, correct revision and down_revision
- Pydantic schemas: valid create, invalid clinic_id formats, production_phi_enabled rejected
- Repository: AsyncMock pool, create/get/list/update_status (all 4 operations)
- API routes: TestClient + dependency_overrides, POST/GET/PATCH
- Safety: production_phi_enabled always false in inserts and responses
- No automatic provisioning from onboarding request status

### 8. Docs

- `docs/architecture/TENANT_PROVISIONING_BACKEND_FOUNDATION.md` (new)
- `docs/claude/CURRENT_STATE.md` — Module 135 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 136

## Constraints

- `production_phi_enabled` must always be `false` — DB CHECK constraint + repo hardcode
- `vapi_assistant_id` and `vapi_phone_number_id` are NOT accepted via API — set via secure deploy-time process only
- No automatic tenant creation from onboarding request approval
- No PHI in tenant provisioning data (tenant = clinic config, not patient records)
- No secrets displayed or collected in any route response
- Full test suite must remain green
- Frontend build must pass (no frontend changes in this module)
