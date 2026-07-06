# PraxisMed — Vapi Credential Binding Design and Secret Boundary

**Sprint 19 / Module 144**
**Date:** 2026-07-06
**Status:** Design only — no live Vapi API calls. No migration yet. No secrets stored.

---

## 1. Purpose

This document defines the hard secret boundary for future Vapi credential binding
in PraxisMed. It establishes where Vapi secrets may and may not exist, documents
the proposed `clinic_vapi_bindings` data model (reference names only — no secret
values), and lists the readiness gate that must be cleared before any live Vapi
API call can occur.

No live Vapi API calls are made in this module. No Vapi credentials are stored.
No PHI. Production PHI remains NO-GO.

---

## 2. Hard Secret Boundary

### 2.1 What counts as a secret

- `VAPI_API_KEY` — Vapi account or project API key
- `VAPI_WEBHOOK_SECRET` — Vapi webhook signing secret
- `INTERNAL_WEBHOOK_SECRET` — PraxisMed internal webhook secret
- `N8N_WEBHOOK_SECRET` — n8n automation webhook secret
- `JWT_SECRET_KEY` — session signing key
- `DATABASE_URL` — database connection string
- Assistant provider API keys
- Machine credentials
- Any token, bearer, or signing value that grants platform access

### 2.2 Forbidden storage locations

Secrets must **never** appear in:

| Location | Status |
|---|---|
| Browser / frontend form fields | FORBIDDEN |
| Database text columns | FORBIDDEN |
| Tenant JSON config files | FORBIDDEN |
| Architecture docs | FORBIDDEN |
| Tests or test fixtures | FORBIDDEN |
| Log lines (application or audit) | FORBIDDEN |
| Audit `raw_payload` columns | FORBIDDEN |
| Screenshots or evidence docs | FORBIDDEN |
| Version control (committed files) | FORBIDDEN |

### 2.3 Allowed future storage

Only the **reference name** of a secret may be stored — never the secret value.

```
api_key_secret_ref = "VAPI_API_KEY_CLINIC_<clinic_slug>"
webhook_secret_ref = "VAPI_WEBHOOK_SECRET_CLINIC_<clinic_slug>"
```

The reference name is a label pointing to the secret in a secure environment
variable or a future managed secret store. The actual secret value is never
written to the database, never logged, and never returned from any API endpoint.

### 2.4 Environment variables only

All secrets are managed via secure environment variables (Railway, Vercel, or a
future secret manager). The environment variable name may appear in docs as a
label. The value must never appear anywhere.

Example labels (not values):

```
VAPI_API_KEY           — Vapi account/project API key
VAPI_WEBHOOK_SECRET    — Vapi webhook signing secret
```

---

## 3. Proposed clinic_vapi_bindings Table

This table will be created in a future migration. It stores only non-secret
binding metadata — reference names, not secret values.

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
```

### Column constraints

| Column | Notes |
|---|---|
| `api_key_secret_ref` | Reference name only — e.g. `VAPI_API_KEY_CLINIC_abc`. No actual secret value. |
| `webhook_secret_ref` | Reference name only. No actual secret value. |
| `assistant_id` | Non-secret public reference returned by Vapi after assistant creation. |
| `phone_number_id` | Non-secret public reference to the Vapi phone number. |
| `status` | `draft` / `configured` / `disabled` / `revoked` |

**No PHI. No patient data. No transcript. No recording URL. No Vapi secret value.**

### Allowed status values

| Status | Meaning |
|---|---|
| `draft` | Binding metadata stored but not yet active |
| `configured` | Binding configured and ready for activation gate |
| `disabled` | Temporarily inactive |
| `revoked` | Permanently revoked — must not be reactivated |

---

## 4. Future Service Design

`backend/app/services/vapi_credential_binding.py` (future module):

```python
async def create_vapi_binding_metadata(pool, clinic_id, api_key_secret_ref, webhook_secret_ref, ...) -> dict
async def get_vapi_binding_metadata(pool, clinic_id) -> dict
async def disable_vapi_binding(pool, clinic_id, actor_user_id) -> dict

def resolve_secret_reference(ref_name: str) -> str
    # Reads secret value from environment at runtime.
    # Must never log the value. Returns value only in memory.

def validate_no_secret_value(value: str) -> None
    # Raises ValueError if value looks like an actual secret
    # (e.g. matches patterns common to API keys, bearer tokens).
    # This is a defence against accidental secret leakage.
```

### Service rules

- Service accepts **reference names** only in stored fields — never raw secret values.
- `validate_no_secret_value` rejects inputs that look like real credentials before persisting.
- `resolve_secret_reference` reads from environment at call time — value never stored, never logged.
- All binding actions create an audit log entry.
- No live Vapi API call is made until the readiness gate (Section 6) is cleared.

---

## 5. Frontend Rules

The Developer Console must **never** contain form fields for:

- Vapi API key input
- Webhook secret input
- JWT secret input
- DATABASE_URL input
- Any secret value input

The frontend may later display (read-only, reference only):

- Binding `status`
- `assistant_id` (non-secret public reference)
- `phone_number_id` (non-secret public reference)
- `api_key_secret_ref` as a masked label (e.g. `VAPI_API_KEY_***`)
- `webhook_secret_ref` as a masked label

No browser secret input under any circumstance.

---

## 6. Logging Rules

- Binding metadata (reference names, status, timestamps) may be logged.
- Actual secret values must **never** be logged — not in application logs, not in audit logs.
- `resolve_secret_reference` must log only that a secret was accessed, not the value.
- The pseudonymization pipeline (Module 130) remains required for all Vapi call payloads.
- Audit `raw_payload` columns must never contain secret values.

---

## 7. Readiness Gate — Before Any Live Vapi Call

The following blockers must all be resolved before any live Vapi API call or
production credential binding:

| Blocker | Status |
|---|---|
| C3 — Secrets hardening and rotation review | Open |
| C4 — PHI logging and redaction hardening | Open |
| C5 — Tenant isolation assurance | Open |
| C6 — Audit trail and compliance coverage | Open |
| C7 — Backup and restore runbook complete | Open |
| C8 — Incident response and rollback plan | Open |

### Austrian / EU legal gate

| Requirement | Status |
|---|---|
| Article 28 AVV (Auftragsverarbeitungsvertrag) with Vapi | Pending |
| Article 32 technical and organisational security measures | Pending |
| Datenschutzbehörde-sensitive process documentation | Pending |
| DSGVO-compliant data processing agreement | Pending |

**Do not set `PRODUCTION_COMPLIANCE_UNLOCKED=true` until all C3–C8 items and
legal requirements are satisfied.**

Production PHI remains NO-GO until this gate is cleared.

---

## 8. No Live Vapi API Calls

This module makes no live Vapi API calls. No VAPI_API_KEY is read, used, or
stored. No Vapi assistant is created or modified. No Vapi phone number is bound.

Live Vapi provisioning is deferred until the readiness gate (Section 7) is cleared.

---

## 9. No PHI

No PHI is stored, processed, or transmitted in any artifact of this module.
No patient data. No transcript. No recording URL. No patient name, phone,
or appointment reason.

---

## 10. What Remains

| Item | Status |
|---|---|
| `clinic_vapi_bindings` migration (Module 145) | Next |
| Secure secret reference resolver service | Pending |
| Admin binding UI — reference labels only, no secret input | Pending |
| Live Vapi provisioning client | Pending (blocked on C3–C8 + Article 28/32) |
| Production hardening (C3–C8) | Open |
| Legal / DSGVO / Article 28 / Article 32 review | Open |
| Production PHI activation | NO-GO — blocked on full hardening checklist |
