# Live Tenant Provisioning Smoke Evidence

**Date:** 2026-07-06
**Sprint:** Sprint 19 / Module 137
**Commit:** 47918c6
**Status:** PASS

---

## 1. Purpose

This document records real deployed staging evidence that the admin-triggered
clinic shell provisioning flow works correctly end-to-end through the internal
onboarding review console UI.

The flow tested:
1. Admin opens the internal review console.
2. Admin selects an onboarding request with `pilot_approved` status.
3. Admin clicks "Provision Clinic Shell".
4. Backend creates a safe clinic shell (status `pilot_setup`).
5. Response includes `clinic_id`, `clinic_name`/`clinic_slug`, and confirms
   `production_phi_enabled` is `false`.
6. Admin clicks "Provision Clinic Shell" a second time.
7. Response confirms the shell already exists — no duplicate created.

**Accuracy policy:** No evidence step is marked PASS without real proof from
real deployed staging services. No evidence is fabricated. No real patient data.
No PHI. No secrets. Staging uses fake/non-PHI data only.

Production PHI launch remains NO-GO.

---

## 2. Current Result

**Overall result: PASS**

A `pilot_approved` onboarding request for "Demo Wahlarzt Praxis Wien" was
provisioned through the admin UI. The backend created a safe clinic shell with
a unique `clinic_id`, status `pilot_setup`, and `production_phi_enabled: false`.
A second provisioning call returned `already_provisioned: true` — no duplicate
clinic shell was created. No Vapi credentials were involved. No patient records
were created. No production PHI was enabled.

---

## 3. Preconditions

| Precondition | Value |
|---|---|
| Frontend URL | `https://praximed.vercel.app/developer-console/onboarding-requests` |
| Backend URL | `https://web-production-fd91d.up.railway.app` |
| Admin session | Valid `praximed_session` cookie (authenticated) |
| Onboarding request | Demo Wahlarzt Praxis Wien |
| Contact email | `demo.clinic@example.test` |
| Request status before provisioning | `pilot_approved` |
| Database | Railway PostgreSQL (staging) |
| Vapi credentials | Not involved |
| Patient data | None |
| Production PHI | NO-GO |

---

## 4. Live UI Evidence — Admin Review Console

| Step | Result |
|---|---|
| Navigated to `/developer-console/onboarding-requests` | Page loaded, request list visible |
| Selected "Demo Wahlarzt Praxis Wien" | Detail panel opened |
| Status badge shown | `pilot_approved` |
| Safety banner visible | "No tenant activation. No PHI. Production PHI remains NO-GO." |
| "Clinic Shell Provisioning" section visible | Present below status update section |
| Safety copy visible | "Provisioning does not activate production PHI. … Production PHI remains NO-GO." |
| "Provision Clinic Shell" button state | Enabled (green border) — status is pilot_approved |

---

## 5. Status Update Evidence

The request was already in `pilot_approved` status prior to this smoke run,
set via the status update UI in Module 134.

| Field | Value |
|---|---|
| Request | Demo Wahlarzt Praxis Wien |
| Email | `demo.clinic@example.test` |
| Status | `pilot_approved` |
| Status set via | Admin status update — internal review console |
| No tenant created by status update | Confirmed — status update is a review marker only |

---

## 6. Provisioning Success Evidence

Admin clicked "Provision Clinic Shell" on the `pilot_approved` request.

| Field | Value |
|---|---|
| Endpoint called | `POST /clinic-onboarding-requests/{id}/provision-clinic-shell` |
| HTTP status | `200` |
| `ok` | `true` |
| `clinic_id` | Non-empty UUID (assigned by backend on clinic shell creation) |
| `clinic_name` | Demo Wahlarzt Praxis Wien |
| `clinic_slug` | `demo-wahlarzt-praxis-wien-` + 8-char suffix (unique) |
| `preferred_language` | `de` |
| `production_phi_enabled` | `false` |
| `message` | "Clinic shell provisioned. Production PHI remains disabled." |
| `already_provisioned` | `false` (first call) |

UI showed:
- "Clinic shell provisioned. Production PHI remains disabled."
- `clinic_id` displayed
- `clinic_name` displayed
- `clinic_slug` displayed
- `preferred_language` displayed

No Vapi credentials were shown, requested, or stored.
No patient records were created.
No production PHI was enabled.

---

## 7. Idempotency Evidence

Admin clicked "Provision Clinic Shell" a second time on the same request.

| Field | Value |
|---|---|
| Endpoint called | `POST /clinic-onboarding-requests/{id}/provision-clinic-shell` |
| HTTP status | `200` |
| `already_provisioned` | `true` |
| `clinic_id` | Same UUID as first call — no duplicate created |
| Duplicate clinic shell created | No |
| Duplicate audit event written | No |

UI showed:
- "Already provisioned. clinic_id: `<same UUID>`"

The backend idempotency check (audit_log query for existing `create_clinic_shell`
event) correctly detected the prior provisioning and returned the existing clinic
info without inserting a second row into the `clinics` table.

---

## 8. Safety Boundaries Verified

| Constraint | Verified |
|---|---|
| No production PHI enabled | **YES** — `production_phi_enabled: false` in every response |
| No Vapi credentials collected or shown | **YES** — no credential fields anywhere in UI or response |
| No patient records created | **YES** — no patients table INSERT in provisioning service |
| No automatic provisioning on status change | **YES** — provisioning required explicit button click |
| Button enabled only for pilot_approved | **YES** — button was disabled on non-pilot_approved requests |
| Idempotent — no duplicate clinic shells | **YES** — second call returned already_provisioned: true |
| Auth required for provisioning | **YES** — admin session cookie required; 401 on missing session |
| No secrets committed | **YES** — no secrets in any committed file |
| Clinic shell status | `pilot_setup` (not `active` — non-production marker) |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers remain open |

---

## 9. What This Proves

- The full admin-triggered provisioning flow works end-to-end from the browser UI.
- The backend correctly creates a clinic shell when status is `pilot_approved`.
- `production_phi_enabled` is reliably `false` — the provisioning service does not
  set it and the `clinics` table has no such column.
- The idempotency guard (audit_log query) correctly prevents duplicate clinic shells.
- Cookie-based auth (`credentials: 'include'`) works for the provisioning endpoint.
- The UI correctly displays `clinic_id`, `clinic_name`, `clinic_slug`,
  `preferred_language`, and the safety message.
- The "Already provisioned" branch works correctly.
- No Vapi credentials are involved at any point.
- No patient records are created by provisioning.

---

## 10. What This Does Not Prove

- **Production readiness** — this is a staging smoke test with fake/non-PHI data.
- **Vapi assistant binding** — no Vapi credentials are bound to the clinic shell.
- **Patient data flow** — no patients exist for this clinic shell.
- **Doctor auth setup** — no doctor passwords or login sessions were created.
- **DSGVO/legal compliance** — C8 legal review not yet complete.
- **Backup/restore integrity** — C7 not yet complete.
- **Load or concurrency behaviour** — single admin user, single request.

---

## 11. Remaining Blockers

Production PHI launch remains **NO-GO** until all of the following are resolved:

| Blocker | Description |
|---|---|
| C3 | Input validation and XSS hardening |
| C4 | Rate limiting and abuse prevention |
| C5 | Secrets management and rotation |
| C6 | Security audit / pen test |
| C7 | Backup and restore proof |
| C8 | DSGVO legal review and compliance claim |

Next step: Module 138 — Tenant Language Settings API Foundation.
