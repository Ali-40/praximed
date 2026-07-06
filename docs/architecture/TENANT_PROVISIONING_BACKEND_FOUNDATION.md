# PraxisMed — Tenant Provisioning Backend Foundation

**Sprint 19 / Module 135**
**Date:** 2026-07-06
**Status:** Implemented

---

## 1. Purpose

This document describes the backend foundation that allows PraxisMed staff to
create a safe clinic shell from an approved onboarding request.

A clinic shell is a minimal, non-production-ready tenant record in the `clinics`
table. It enables pilot setup without enabling production PHI processing,
storing Vapi credentials, or creating patient records.

---

## 2. Provisioning Preconditions

Provisioning is only allowed when **all** of the following are true:

| Condition | Enforced by |
|---|---|
| Onboarding request exists | Service raises `ProvisioningNotFoundError` if missing |
| Request status is `pilot_approved` | Service raises `ProvisioningBlockedError` otherwise |
| Caller has authenticated session | Route requires `get_current_user` dependency |

Provisioning is **NOT** triggered automatically:
- Not by the public `POST /clinic-onboarding-requests` endpoint
- Not by any status change (including `pilot_approved`)
- Only by an explicit `POST /clinic-onboarding-requests/{id}/provision-clinic-shell` call from an authenticated user

---

## 3. Route

```
POST /clinic-onboarding-requests/{request_id}/provision-clinic-shell
```

| Property | Value |
|---|---|
| Auth | Required (`get_current_user` session cookie or Bearer) |
| `404` | Request not found |
| `409` | Request not in `pilot_approved` status |
| `200` | Already provisioned (idempotent — returns existing clinic info) |
| `200` | New provisioning successful |

Response fields:
- `ok` — always `true`
- `onboarding_request_id`
- `clinic_id`
- `clinic_name`
- `clinic_slug`
- `preferred_language`
- `fallback_language`
- `supported_languages`
- `production_phi_enabled` — always `false`
- `message` — "Clinic shell provisioned. Production PHI remains disabled."
- `already_provisioned` — `true` if already provisioned, `false` if newly created

---

## 4. Service

`backend/app/services/tenant_provisioning.py`

**`provision_clinic_shell_from_onboarding_request(pool, request_id, actor_user_id=None)`**

Steps:
1. Load onboarding request by ID.
2. Guard: status must be `pilot_approved`.
3. Idempotency check: query `audit_log` for existing `create_clinic_shell` event.
4. Create clinic shell in `clinics` table (status=`pilot_setup`).
5. Write audit event to `audit_log`.
6. Return safe provisioning result.

---

## 5. Clinic Shell Creation

The existing `clinics` table is used — no new migration was required.

```sql
INSERT INTO clinics (slug, name, status, locale, timezone)
VALUES ($1, $2, 'pilot_setup', $3, 'Europe/Vienna')
RETURNING *
```

| clinics column | Source |
|---|---|
| `slug` | Slugified `clinic_name` + 8-char UUID suffix (unique) |
| `name` | `clinic_name` from onboarding request |
| `status` | `'pilot_setup'` — not `'active'`, signals non-production state |
| `locale` | Mapped from `preferred_language`: `de` → `de-AT`, `en` → `en-US` |
| `timezone` | `Europe/Vienna` (Austrian clinic default) |

**`production_phi_enabled` is NOT a column in the `clinics` table.**
PHI activation is never stored in the clinic shell. Production PHI activation
requires a separate, guarded, multi-step compliance process (C3–C8 blockers).

---

## 6. Language Preservation

Language configuration from the onboarding request is preserved in:

| Target | Value |
|---|---|
| `clinics.locale` | `de-AT` (for `preferred_language=de`) or `en-US` |
| Provisioning result | `preferred_language`, `fallback_language`, `supported_languages` |
| `audit_log.metadata` | Full language config stored for traceability |

`supported_languages` from the onboarding request may arrive as a JSONB-parsed
list or a raw JSON string (asyncpg codec variation) — both are handled.

Default (if missing): `preferred_language=de`, `fallback_language=en`, `supported_languages=["de","en"]`.

---

## 7. Audit Event

Provisioning is recorded in the existing `audit_log` table — no new table was created.

```sql
-- Written on successful provisioning:
INSERT INTO audit_log (
    clinic_id, actor_type, actor_id, action, resource_type, resource_id, metadata
) VALUES (
    <new_clinic_id>,
    'user' | 'system',
    <actor_user_id>,
    'create_clinic_shell',
    'clinic_onboarding_request',
    <onboarding_request_id>,
    <metadata_jsonb>
)
```

`metadata` includes: `clinic_id`, `onboarding_request_id`, `clinic_name`, `clinic_slug`,
`preferred_language`, `fallback_language`, `supported_languages`, `production_phi_enabled: false`,
`message`, `_result: success`, `_severity: info`.

---

## 8. Idempotency

Before creating a new clinic, the service queries `audit_log` for an existing
`create_clinic_shell` event for the same `onboarding_request_id`:

```sql
SELECT metadata FROM audit_log
WHERE resource_type = 'clinic_onboarding_request'
  AND resource_id   = $1
  AND action        = 'create_clinic_shell'
  AND metadata->>'_result' = 'success'
ORDER BY created_at DESC LIMIT 1
```

If found, the existing clinic info is returned immediately — no duplicate clinic
is inserted and no second audit event is written.

---

## 9. Safety Boundaries

| Constraint | Status |
|---|---|
| No automatic provisioning from public submit | **ENFORCED** — provision endpoint is separate and protected |
| No automatic provisioning from status change | **ENFORCED** — no trigger or hook |
| No production PHI activation | **ENFORCED** — `production_phi_enabled` not in clinics table |
| No Vapi credentials accepted or stored | **ENFORCED** — not accepted as input, not inserted anywhere |
| No patients created | **ENFORCED** — no INSERT INTO patients in service |
| No doctor passwords generated | **ENFORCED** — no password hash in clinic shell |
| Auth required for provisioning | **ENFORCED** — `get_current_user` dependency |
| Audit trail written | **ENFORCED** — `audit_log` INSERT on every new provisioning |
| Idempotent | **ENFORCED** — idempotency check prevents duplicate clinic creation |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |

---

## 10. What Remains

The following are NOT yet implemented and require future modules:

- **Frontend admin button** — "Provision clinic shell" button in the review console (Module 136)
- **Tenant language settings API** — live configuration of Vapi assistant language
- **Vapi credential binding** — secure deploy-time process, not an API endpoint
- **External notification config** — email/SMS for new clinic staff
- **Legal / security readiness** — C3–C8 compliance blockers must be resolved
- **Backup / restore proof** — Module C7
- **DSGVO compliance claim** — Module C8 (legal review required)
