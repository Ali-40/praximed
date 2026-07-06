# PraxisMed — Onboarding Frontend to Backend Connection

**Sprint 19 / Module 133**
**Date:** 2026-07-06
**Status:** Implemented — /onboarding is now a real controlled form

---

## 1. Purpose

This document describes how the `/onboarding` page submits real clinic pilot/onboarding
requests to the `POST /clinic-onboarding-requests` backend endpoint introduced in Module 132.

The form collects clinic details, doctor/admin contact, workflow preferences, and consent
acknowledgements. No patient PHI is accepted. No automatic tenant is created. No production
PHI is activated.

---

## 2. What Changed (Module 133)

Before Module 133, `/onboarding` was a static scaffold — all buttons were disabled and no
data was submitted anywhere. In Module 133:

- The page is a real React controlled form (`useState`-based)
- Submits to `POST /clinic-onboarding-requests` (public, no auth required)
- German-first language selector is interactive
- Consent checkboxes are required before submission
- Success state shows confirmation and request ID
- Error state shows a safe error message (no stack traces)
- Safety copy is preserved: no PHI, no secrets, no production activation

---

## 3. Form Fields

### Required
| Field | Type | Default |
|---|---|---|
| `clinic_name` | text | — |
| `doctor_name` | text | — |
| `contact_email` | email | — |
| `consent_pilot_contact` | checkbox | false |
| `acknowledges_no_phi` | checkbox | false |

### Optional
| Field | Type | Default |
|---|---|---|
| `clinic_type` | text | — |
| `specialty` | text | — |
| `city` | text | Wien |
| `address` | text | — |
| `website` | url | — |
| `contact_phone` | tel | — |
| `estimated_call_volume` | text | — |
| `current_booking_system` | text | — |
| `workflow_notes` | textarea | — |
| `wants_ai_phone_intake` | checkbox | true |
| `wants_dashboard` | checkbox | true |
| `wants_notifications` | checkbox | false |

### Server-controlled (never sent from form)
- `status` — always `submitted` on create (server sets this)
- `production_phi_enabled` — always `false` (DB constraint, not accepted from client)
- Vapi credentials — never collected here

---

## 4. Language Configuration

Austrian private clinics default to **German-first** (`preferred_language=de`),
with English as the fallback (`fallback_language=en`).

The language selector shows two interactive option cards:
- **Deutsch** — Primary, Austrian clinic default
- **English (Fallback)** — English fallback for non-German speakers

Helper text: "Deutsch zuerst / Englisch als Fallback — Default for Austrian clinics: German-first"

`supported_languages` is always sent as `["de","en"]`.

Language preference is stored by the backend but does **not** automatically configure
the Vapi assistant or clinic UI language — that wiring is a future module.

---

## 5. Submission Flow

```
User fills form → clicks "Submit Pilot Access Request"
    ↓
fetch(`${API_BASE_URL}/clinic-onboarding-requests`, {
  method: 'POST',
  credentials: 'include',  // cookie-based session consistency
  body: JSON.stringify(payload)
})
    ↓
201 Created → success state: "Pilot request submitted" + request ID
    ↓
422 / 4xx → error state: safe validation message, no stack traces
    ↓
Network error → "A network error occurred. Please check your connection."
```

**What does not happen:**
- No automatic tenant creation
- No Vapi credential storage
- No `production_phi_enabled = true`
- No patient PHI accepted
- No `sessionStorage` or `localStorage` used
- No redirect on success (user stays on page)

---

## 6. Consent Requirements

Both checkboxes are required (`required` HTML attribute + backend validation):

1. **consent_pilot_contact** — "I agree to be contacted by PraxisMed about this pilot request."
2. **acknowledges_no_phi** — "I acknowledge this is a pilot onboarding request, not a production
   patient data system activation."

If either is false, the backend returns HTTP 422 and the form shows a validation error.

---

## 7. Safety Boundaries

| Constraint | Status |
|---|---|
| No patient data collected | **ENFORCED** — no patient_name, DOB, SVNR, diagnosis fields |
| No Vapi credentials collected | **ENFORCED** — no credential input fields |
| No sessionStorage / localStorage | **CONFIRMED** — cookies only |
| No production_phi_enabled in payload | **CONFIRMED** — not sent |
| No status in payload (server-controlled) | **CONFIRMED** |
| consent_pilot_contact required | **ENFORCED** — HTML required + backend validation |
| acknowledges_no_phi required | **ENFORCED** — HTML required + backend validation |
| Safety copy visible | **CONFIRMED** — Do not enter patient data; Pilot activation does not enable production PHI processing |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |

---

## 8. What Module 134 Will Do

Module 134 — Internal Clinic Onboarding Review Console:
- Admin/staff view to list and review submitted onboarding requests
- Status update workflow (submitted → reviewed → demo_booked → pilot_approved / rejected)
- No automatic tenant provisioning
- Protected by existing session auth
