# PraxisMed — Admin Provision Clinic Shell UI

**Sprint 19 / Module 136**
**Date:** 2026-07-06
**Status:** Implemented

---

## 1. Purpose

This document describes the internal admin UI that allows PraxisMed staff to
trigger clinic shell provisioning directly from the onboarding review console,
without needing curl or an API tool.

The button calls the backend provisioning endpoint introduced in Module 135.
It is a UI convenience layer only — all safety enforcement remains in the
backend service.

---

## 2. What Module 136 Adds

| Component | Change |
|---|---|
| `frontend/app/developer-console/onboarding-requests/page.tsx` | "Clinic Shell Provisioning" section with button, safety copy, success/error states |
| `frontend/lib/api.ts` | `provisionClinicShell(requestId)` helper |
| `backend/tests/test_admin_provision_clinic_shell_ui_contract.py` | 90 static contract tests |

---

## 3. Page Changes

### 3.1 New State

```typescript
type ProvisionState = 'idle' | 'provisioning' | 'provisioned' | 'error'

interface ProvisionResult {
  ok: boolean
  clinic_id: string
  clinic_name: string
  clinic_slug: string
  preferred_language: string
  production_phi_enabled: boolean   // always false
  message: string
  already_provisioned: boolean
}
```

State variables: `provisionState`, `provisionResult`, `provisionError`.
All three reset to `idle`/`null`/`null` when a new request is selected.

### 3.2 handleProvision

```
POST /clinic-onboarding-requests/{id}/provision-clinic-shell
credentials: 'include'
```

Error mapping:

| HTTP status | UI message |
|---|---|
| 401 / 403 | "Admin session required." |
| 409 | "Request must be pilot_approved before provisioning." |
| Other error | "Provisioning failed. Please retry or check backend logs." |
| Network error | "Provisioning failed. Please retry or check backend logs." |

### 3.3 Button Rules

- Button label: **Provision Clinic Shell**
- Enabled only when `selected.status === 'pilot_approved'`
- Disabled with `opacity: 0.5` and `cursor: not-allowed` when status ≠ `pilot_approved`
- Disabled during provisioning to prevent double-click
- Loading label: **Provisioning…**
- Helper text when disabled: "Set status to pilot_approved before provisioning."

### 3.4 Success State

When `provisionState === 'provisioned'`:

- If `already_provisioned`: "Already provisioned. clinic_id: `<id>`"
- If newly provisioned: "Clinic shell provisioned. Production PHI remains disabled."
  - Displays: `clinic_id`, `clinic_name`, `clinic_slug`, `preferred_language`

### 3.5 Safety Copy (always visible near button)

> Provisioning does not activate production PHI. It creates a pilot clinic
> shell only — no Vapi credentials are bound, no patient records are created,
> and no production PHI is enabled. **Production PHI remains NO-GO.**

---

## 4. api.ts Helper

```typescript
export async function provisionClinicShell(
  requestId: string,
): Promise<ClinicShellProvisionResult>
```

Calls `POST /clinic-onboarding-requests/{requestId}/provision-clinic-shell`
via `apiFetch` (which always sets `credentials: 'include'`).
Throws on non-2xx responses.

---

## 5. Safety Constraints

| Constraint | Status |
|---|---|
| No production PHI activation | **ENFORCED** — backend service never sets production_phi_enabled |
| No Vapi credentials shown or collected | **ENFORCED** — no credential fields in page or api helper |
| No patient records created | **ENFORCED** — backend service has no patient INSERT |
| Button requires explicit click | **ENFORCED** — no automatic provisioning on status change |
| Button disabled when status ≠ pilot_approved | **ENFORCED** — frontend gate + backend 409 guard |
| No sessionStorage / localStorage | **ENFORCED** — no storage calls anywhere in page |
| Auth required | **ENFORCED** — credentials: 'include'; backend requires get_current_user |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |

---

## 6. Relation to Module 135

Module 135 created the backend provisioning service and route. Module 136
adds the frontend button that calls it. No backend changes were required for
Module 136.

See `docs/architecture/TENANT_PROVISIONING_BACKEND_FOUNDATION.md` for the
full backend specification.
