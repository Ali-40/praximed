# PraxisMed — Internal Clinic Onboarding Review Console

**Sprint 19 / Module 134**
**Date:** 2026-07-06
**Status:** Implemented

---

## 1. Purpose

This document describes the internal admin review console that allows PraxisMed staff
to view and process submitted clinic pilot/onboarding requests.

The console is a protected internal page — not visible to clinic staff or public users.
No tenant is provisioned automatically by any action in this console. Production PHI
remains NO-GO until all C3–C8 compliance hardening blockers are resolved.

---

## 2. URL and Access

| Property | Value |
|---|---|
| Route | `/developer-console/onboarding-requests` |
| Auth | Session cookie (`get_current_user`) |
| Unauthenticated | HTTP 401/403 → "Admin session required. Please log in first." |
| Theme | Dark developer-console (INK `#0B132B`, PANEL `#111C3D`, ACCENT `#008080`) |

The developer console main page (`/developer-console`) links directly to this page
via a "Review onboarding requests →" link inside the "Pilot Request Review" panel.

---

## 3. Backend API Usage

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/clinic-onboarding-requests` | List all submitted onboarding requests |
| `PATCH` | `/clinic-onboarding-requests/{id}/status` | Update review status |

Both endpoints require an active session cookie. Credentials are sent via
`credentials: 'include'` on all `fetch` calls. No `sessionStorage` or `localStorage`
is used. No secrets are displayed or collected.

---

## 4. Status Workflow

Allowed status transitions (manual, no automation):

```
submitted → reviewed → demo_booked → pilot_approved
                                    → rejected
                    → archived
```

| Status | Badge colour |
|---|---|
| submitted | WARN (`#FFB703`) |
| reviewed | ACCENT (`#008080`) |
| demo_booked | ACCENT (`#008080`) |
| pilot_approved | GREEN (`#4ADE80`) |
| rejected | DANGER (`#E63946`) |
| archived | MUTED (`#93A0B8`) |

Status updates are internal review markers only. They do **not** trigger tenant
provisioning, Vapi assistant configuration, or any downstream automation.

---

## 5. UI Layout

Two-panel layout (flex, responsive):

**Left panel — Request list:**
- Requests are listed with `clinic_name`, `status` badge, `doctor_name`, `contact_email`, and language badge.
- Clicking a row selects it and populates the detail panel.
- Empty state: "No onboarding requests submitted yet."

**Right panel — Request detail:**
- Sections: Clinic, Doctor / Admin, Language, Workflow, Safety, Operational.
- Fields displayed: `clinic_name`, `clinic_type`, `specialty`, `city`, `address`,
  `website`, `doctor_name`, `contact_email`, `contact_phone`, `preferred_language`,
  `fallback_language`, `supported_languages`, `estimated_call_volume`,
  `current_booking_system`, `workflow_notes`, `wants_ai_phone_intake`, `wants_dashboard`,
  `wants_notifications`, `consent_pilot_contact`, `acknowledges_no_phi`,
  `production_phi_enabled` (always false), `id`, `source`, `pilot_interest_level`,
  `created_at`, `updated_at`.
- Status update dropdown + "Update status" button → PATCH endpoint.

---

## 6. api.ts Helpers

Two exported helpers were added to `frontend/lib/api.ts`:

```typescript
// Fetches GET /clinic-onboarding-requests — returns the requests array
fetchClinicOnboardingRequests(): Promise<ClinicOnboardingRequest[]>

// PATCH /clinic-onboarding-requests/{requestId}/status
updateClinicOnboardingRequestStatus(requestId: string, status: string): Promise<void>
```

Both use the shared `apiFetch` helper which automatically applies
`credentials: 'include'`.

---

## 7. Safety Boundaries

| Constraint | Status |
|---|---|
| No automatic tenant creation | **ENFORCED** — status changes are markers only |
| No PHI displayed | **ENFORCED** — onboarding requests contain clinic/doctor info only |
| No secrets displayed or collected | **CONFIRMED** |
| No sessionStorage / localStorage | **CONFIRMED** — cookies only |
| production_phi_enabled always false | **ENFORCED** — DB CHECK constraint |
| Auth-protected page | **ENFORCED** — 401/403 → "Admin session required" |
| Safety banner visible | **CONFIRMED** — "No tenant activation. No PHI. Production PHI remains NO-GO." |
| Activation warning in detail | **CONFIRMED** — "Approving a request does not create a tenant or unlock production PHI." |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |

---

## 8. Module 134A — Crash Fix

**Problem found:** Live smoke test at `https://praximed.vercel.app/developer-console/onboarding-requests`
confirmed the request list loaded (GET `/clinic-onboarding-requests` worked), but clicking any
request triggered a client-side exception that crashed the page.

**Root cause:** The detail panel called `.join()` directly on `supported_languages` after a
`?? []` guard. Because asyncpg returns JSONB columns as raw JSON strings by default (not
parsed arrays), `supported_languages` arrived as the string `'["de","en"]'`. Strings in
JavaScript do not have a `.join()` method → `TypeError: value.join is not a function`.

Secondary risks (also fixed): date fields called `toLocaleString()` without null guard;
boolean fields (`wants_ai_phone_intake`, consent flags, etc.) were typed non-nullable but
could arrive as `null` or `undefined`; optional text fields (`pilot_interest_level`, `source`)
were typed as `string` but could be `null`.

**Fix (Module 134A):**

Four defensive rendering helpers were added to the page:

| Helper | Guards against |
|---|---|
| `safeText(value, fallback='—')` | null, undefined, empty string |
| `safeDate(value)` | null, undefined, invalid date strings |
| `safeBoolean(value)` | null, undefined → `null` (renders as "—") |
| `safeLanguages(value)` | array, JSON string, null/undefined |

`safeLanguages` specifically: if value is an array, joins it; if it's a JSON string, parses
then joins; if null/undefined, returns `'de, en'`.

`BoolRow` updated: `boolean | null` signature, renders null as "—", true as "Yes", false as "No".

`OnboardingRequest` interface updated: `supported_languages: string[] | string | null`,
all boolean fields `boolean | null`, `created_at`/`updated_at` `string | null`,
`pilot_interest_level`/`source` `string | null`.

No backend changes. No PHI. No secrets. No tenant activation changed.

---

## 9. What Module 135 Will Do

Module 135 — Tenant Provisioning Backend Foundation:
- Database table, schema, and Alembic migration for `tenants`
- Pydantic schemas for tenant creation
- Repository layer (`tenant_repo.py`)
- Protected admin API routes (POST /tenants, GET /tenants, GET /tenants/{id})
- No automatic provisioning from onboarding request approval
- No PHI activation
- Full test coverage
