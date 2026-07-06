# PraxisMed — Vapi Binding Metadata Backend Foundation

**Sprint 19 / Module 145**
**Date:** 2026-07-06
**Status:** Backend foundation only — no live Vapi API calls. No Vapi credentials stored. No PHI.

---

## 1. Purpose

This module creates the database table, repository layer, service, and protected
internal API routes for storing Vapi binding metadata per clinic. The binding
record holds only secret reference names (labels pointing to environment
variables) — never the actual secret values.

No live Vapi API calls are made. No VAPI_API_KEY is resolved, stored, or
returned. No Vapi assistant is created or modified. Production PHI remains NO-GO.

---

## 2. Table — clinic_vapi_bindings

Migration: `0005_clinic_vapi_bindings`

```sql
CREATE TABLE clinic_vapi_bindings (
    id                       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id                UUID        NOT NULL REFERENCES clinics(id),
    assistant_id             TEXT,
    phone_number_id          TEXT,
    vapi_project_id          TEXT,
    api_key_secret_ref       TEXT        NOT NULL,
    webhook_secret_ref       TEXT        NOT NULL,
    assistant_config_version TEXT,
    language_mode            TEXT        NOT NULL DEFAULT 'german_first',
    status                   TEXT        NOT NULL DEFAULT 'draft',
    created_by_user_id       UUID,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT clinic_vapi_bindings_status_check CHECK (
        status IN ('draft', 'configured', 'disabled', 'revoked')
    ),
    CONSTRAINT clinic_vapi_bindings_language_mode_check CHECK (
        language_mode IN ('german_first', 'english_first', 'bilingual_auto')
    )
);
```

### Column notes

| Column | Notes |
|---|---|
| `api_key_secret_ref` | Reference name only — e.g. `VAPI_API_KEY_REF_CLINIC_DEMO`. Never the secret value. |
| `webhook_secret_ref` | Reference name only — e.g. `VAPI_WEBHOOK_SECRET_REF_CLINIC_DEMO`. Never the secret value. |
| `assistant_id` | Non-secret public reference returned by Vapi after assistant creation (future). |
| `phone_number_id` | Non-secret public reference (future). |
| `status` | `draft` / `configured` / `disabled` / `revoked` |

**No PHI. No patient data. No transcript. No recording URL. No Vapi secret value.**

---

## 3. Secret Reference Rule

Only **reference names** may be stored — never actual secret values.

### Allowed reference name format

```
VAPI_API_KEY_REF_CLINIC_DEMO
VAPI_WEBHOOK_SECRET_REF_CLINIC_DEMO
```

Reference names are uppercase alphanumeric + underscore strings (e.g.
`^[A-Z][A-Z0-9_]{2,99}$`). They are labels pointing to environment variables
managed in Railway, Vercel, or a future secret manager.

### Rejected values (validation rejects these at schema level)

| Pattern | Reason |
|---|---|
| `sk-...` | OpenAI-style API key prefix |
| `vapi_live_...` | Vapi live credential prefix |
| Any lowercase or mixed-case token | Reference names must be uppercase |
| Empty strings | Not allowed |

The schema validator `_validate_secret_ref` enforces the regex pattern and
rejects known secret-looking prefixes.

---

## 4. Protected Routes

All routes require an authenticated session (`get_current_user` dependency).
No public access.

| Method | Path | Description |
|---|---|---|
| `POST` | `/clinics/{clinic_id}/vapi-bindings` | Create binding metadata record |
| `GET` | `/clinics/{clinic_id}/vapi-bindings` | Get latest binding for clinic |
| `PATCH` | `/clinic-vapi-bindings/{binding_id}/status` | Update binding status |

### Response rules

- Responses return `api_key_secret_ref` and `webhook_secret_ref` as reference names only.
- Responses never return actual VAPI_API_KEY or VAPI_WEBHOOK_SECRET values.
- `production_phi_enabled` is always `false` in every response.

---

## 5. Service Layer

`backend/app/services/clinic_vapi_binding.py`

```python
async def create_vapi_binding_metadata(pool, payload, actor_user) -> dict
    # 1. Verify clinic exists
    # 2. Create repo row with reference names only
    # 3. Log binding_id, clinic_id, language_mode, actor — never log secret values
    # 4. Return row with production_phi_enabled=False

async def get_vapi_binding_metadata(pool, clinic_id, actor_user) -> dict | None
    # 1. Verify clinic exists
    # 2. Return latest binding row or None
    # 3. production_phi_enabled=False always

async def update_vapi_binding_status(pool, binding_id, status, actor_user) -> dict
    # 1. Update status column
    # 2. Log binding_id, new status, actor
    # 3. production_phi_enabled=False always
```

### Service rules

- No VAPI_API_KEY resolved at any point.
- No live Vapi API call ever made.
- Secret values never logged — only reference names, binding IDs, and status.
- `production_phi_enabled` is injected as `False` before returning any row.

---

## 6. Repository Layer

`backend/app/db/repositories/clinic_vapi_binding_repo.py`

```python
async def create_clinic_vapi_binding(pool, clinic_id, api_key_secret_ref, webhook_secret_ref, ...) -> dict
async def get_clinic_vapi_binding_by_id(pool, binding_id) -> dict | None
async def get_clinic_vapi_binding_by_clinic_id(pool, clinic_id) -> dict | None
async def list_clinic_vapi_bindings(pool, status=None, limit=50) -> list[dict]
async def update_clinic_vapi_binding_status(pool, binding_id, status) -> dict | None
async def disable_or_revoke_clinic_vapi_binding(pool, binding_id, revoke=False) -> dict | None
```

All SQL is parameterised. No actual secret values accepted, stored, or returned.

---

## 7. Audit Behaviour

- All binding creation events are logged at INFO level with: `binding_id`, `clinic_id`,
  `language_mode`, `actor_user_id`.
- Status update events are logged with: `binding_id`, `new_status`, `actor_user_id`.
- Secret reference names (labels) may appear in logs.
- Actual secret values must **never** appear in any log line.

---

## 8. No Live Vapi API Calls

This module makes no live Vapi API calls. No VAPI_API_KEY is read, resolved, used,
or stored. No Vapi assistant is created. No Vapi phone number is bound.

The service layer contains no HTTP client imports (no `httpx`, no `aiohttp`, no
`requests`). Live Vapi provisioning is deferred until the readiness gate (C3–C8
and Article 28/32) is cleared.

---

## 9. No PHI

No PHI is stored, processed, or transmitted in any artifact of this module.
No patient data. No transcript. No recording URL. No patient name, phone,
or appointment reason.

`production_phi_enabled` is always `False` at the service and route layer.

---

## 10. Environment Variables Only

Actual secret values are managed via secure environment variables (Railway,
Vercel, or a future secret manager). The environment variable names may appear
in reference labels. Their values must never appear in:

- Database rows
- API responses
- Application logs
- Architecture docs
- Tests

---

## 11. What Remains

| Item | Status |
|---|---|
| Railway migration 0005 — run on staging | Next step |
| Admin frontend UI for binding metadata refs | Module 146 |
| Secret manager / environment resolver service | Pending |
| Live Vapi provisioning client (HTTP to api.vapi.ai) | Pending — blocked on C3–C8 |
| Recording ingestion pipeline | Pending |
| Transcript storage with pseudonymisation | Pending |
| C3–C8 security/legal hardening | Open |
| Article 28 AVV with Vapi | Pending |
| Article 32 technical and organisational measures | Pending |
| Production PHI activation | NO-GO — blocked on full hardening checklist |
