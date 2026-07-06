# PraxisMed — Admin Tenant Language Settings UI

**Sprint 19 / Module 139**
**Date:** 2026-07-06
**Status:** Implemented

---

## 1. Purpose

This document describes the internal admin UI for reading and updating tenant
(clinic) language settings. The UI lives inside the developer/admin console and
allows admin or staff to view and change the language configuration for a
provisioned clinic shell directly from the browser.

German-first is the default for Austrian clinics (Wahlärzte). English fallback
is supported. No PHI. No Vapi credentials. No secrets. No production activation.
Production PHI remains NO-GO.

---

## 2. Route

```
/developer-console/language-settings   (Next.js page, admin-only console)
```

Entry point: a "Tenant Language Settings" panel on `/developer-console` links
to this page via "Configure language settings →".

---

## 3. Backend Endpoints Used

```
GET   /clinics/{clinic_id}/language-settings
PATCH /clinics/{clinic_id}/language-settings
```

Both require an admin session cookie (`credentials: 'include'`). Partial update
— only provided fields are changed. Provided by Module 138.

| HTTP | Status | Meaning |
|---|---|---|
| GET | 200 | Returns ClinicLanguageSettings JSON |
| GET | 401 | No session — admin login required |
| GET | 403 | Session present but not admin |
| GET | 404 | clinic_id not found |
| PATCH | 200 | Settings updated; returns new ClinicLanguageSettings |
| PATCH | 400 | Validation error (e.g. primary_language not in supported_languages) |
| PATCH | 401 | No session |
| PATCH | 403 | Not admin |
| PATCH | 404 | Clinic not found |
| PATCH | 422 | Invalid language code or vapi mode |

---

## 4. Clinic ID Input

The page opens with a Clinic ID text field. The admin enters a provisioned
clinic UUID and clicks "Load settings". No clinic ID is hard-coded.
No sessionStorage or localStorage is used. The clinic ID is held in React state
only for the lifetime of the page.

---

## 5. Language Settings Form

After loading, the following fields are displayed and editable via select
dropdowns and checkboxes:

| Field | Type | German-first default | Allowed values |
|---|---|---|---|
| `primary_language` | select | `de` | `de`, `en` |
| `fallback_language` | select | `en` | `de`, `en` |
| `supported_languages` | checkboxes | `["de", "en"]` | `de` (Deutsch), `en` (English) |
| `default_patient_language` | select | `de` | `de`, `en` |
| `vapi_assistant_language_mode` | select | `german_first` | `german_first`, `english_first`, `bilingual_auto` |
| `clinic_ui_language` | select | `de` | `de`, `en` |

The UI label "German-first is recommended for Austrian Wahlärzte." is shown
near the form to reinforce the German-first default.

The Vapi assistant language mode note reads: "This controls future Vapi
assistant configuration. It does not bind Vapi credentials yet."

---

## 6. Load and Save Behaviour

### Load

1. Admin enters a clinic UUID and clicks "Load settings".
2. Frontend sends `GET /clinics/{clinicId}/language-settings` with
   `credentials: 'include'`.
3. On 200: form is populated with current settings. `updated_at` is displayed.
4. On 401/403: "Admin session required. Please log in first."
5. On 404: "Clinic not found or no access."
6. On other error: generic error message.

### Save

1. Admin edits one or more fields and clicks "Save language settings".
2. Frontend sends `PATCH /clinics/{clinicId}/language-settings` with only the
   changed fields in the JSON body. `credentials: 'include'`.
3. On 200: "Language settings saved" is shown. Form updated with response.
4. On 401/403: auth error message.
5. On 404: clinic not found message.
6. On 400: "Unsupported language configuration."
7. On other error: "Could not save language settings."

---

## 7. api.ts Helpers

`frontend/lib/api.ts` exports:

```typescript
interface ClinicLanguageSettings {
  ok: boolean
  clinic_id: string
  primary_language: string
  fallback_language: string
  supported_languages: string[]
  default_patient_language: string
  vapi_assistant_language_mode: string
  clinic_ui_language: string
  updated_at: string | null
}

interface ClinicLanguageSettingsUpdatePayload {
  primary_language?: string
  fallback_language?: string
  supported_languages?: string[]
  default_patient_language?: string
  vapi_assistant_language_mode?: string
  clinic_ui_language?: string
}

fetchClinicLanguageSettings(clinicId: string): Promise<ClinicLanguageSettings>
updateClinicLanguageSettings(clinicId: string, payload: ClinicLanguageSettingsUpdatePayload): Promise<ClinicLanguageSettings>
```

Both use `credentials: 'include'` via `apiFetch`. No sessionStorage.
No localStorage. No Vapi API key. No webhook secret. No DATABASE_URL.

---

## 8. Safety Boundaries

| Constraint | Enforced by |
|---|---|
| No PHI fields | Page contains no patient data fields |
| No Vapi credentials | No Vapi API key or webhook secret field |
| No sessionStorage | React state only |
| No localStorage | React state only |
| No production activation | This UI sets language config only |
| production_phi_enabled never set | Not a field in this page |
| credentials: 'include' | All fetches via apiFetch |
| Admin session required | Backend get_current_user dependency |

Safety copy visible on the page:

> "No PHI. No secrets. No Vapi credentials."
> "Language settings do not enable production PHI, Vapi credentials, or patient-data processing."
> "Production PHI remains NO-GO."

---

## 9. Developer Console Nav

`/developer-console/page.tsx` includes a "Tenant Language Settings" panel with:
- Description: language controls clinic UI language, patient language fallback,
  future Vapi assistant language mode
- Link: "Configure language settings →" → `/developer-console/language-settings`

---

## 10. What Remains

| Item | Status |
|---|---|
| Live smoke evidence (Module 140) | Pending |
| Vapi assistant config binding | Pending (C3–C8 blockers) |
| Bilingual assistant testing | Pending |
| External notifications | Pending |
| Security / legal readiness (DSGVO) | Pending (C3–C8) |
| Production PHI activation | NO-GO — blocked on hardening checklist |

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.
