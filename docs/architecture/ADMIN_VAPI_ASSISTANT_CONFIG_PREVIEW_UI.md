# PraxisMed — Admin Vapi Assistant Config Preview UI

**Sprint 19 / Module 142**
**Date:** 2026-07-06
**Status:** Implemented

---

## 1. Purpose

This document describes the internal admin UI for previewing the generated Vapi
assistant configuration pack per clinic. The page allows admin or staff to
inspect the German/English prompts, required capture fields, tool schema, safety
rules, forbidden claims, and readiness flags before any live Vapi binding occurs.

Read-only preview only. No live Vapi API calls. No Vapi credentials stored or
transmitted. No PHI. No secrets. Production PHI remains NO-GO.

---

## 2. Route

```
/developer-console/vapi-config   (Next.js page, admin-only console)
```

Entry point: a "Vapi Assistant Config Preview" panel on `/developer-console`
links to this page via "Preview Vapi config →".

---

## 3. Backend Endpoint Used

```
GET /clinics/{clinic_id}/vapi-assistant-config-pack
```

Provided by Module 141. Requires admin session cookie (`credentials: 'include'`).
Returns `VapiAssistantConfigPack` JSON. No live Vapi binding. No secrets in response.

| HTTP | Status | Meaning |
|---|---|---|
| GET | 200 | Returns VapiAssistantConfigPack JSON |
| GET | 401 | No session — admin login required |
| GET | 403 | Session present but not admin |
| GET | 404 | clinic_id not found |

---

## 4. Clinic ID Input

Admin enters a provisioned clinic UUID and clicks "Load config pack". An example
staging clinic_id (`1a5bbc75-c1b0-4488-94aa-64b3f1c50056`) is shown as a hint.
No sessionStorage or localStorage is used. No Vapi API key, webhook secret,
DATABASE_URL, or JWT secret is ever requested or shown.

---

## 5. German-First Prompt Preview

Section B of the display shows:
- `first_message_de` — the German greeting the assistant says when a call starts
- `system_prompt_de` — the full German system prompt rendered in a monospace block

The prompt includes:
- "Du bist die KI-Rezeption von {clinic_display_name}, einer privaten Praxis in Wien."
- Keine Diagnose / keine medizinische Beratung / keine Terminbestätigung
- Notruf 144 escalation instruction

---

## 6. English Fallback Prompt Preview

Section C of the display shows:
- `first_message_en` — the English greeting
- `system_prompt_en` — the full English system prompt

The prompt includes:
- "You are the AI receptionist for {clinic_display_name}, a private clinic in Vienna."
- No diagnosis / no medical advice / no appointment confirmation promise
- Call 144 escalation instruction

---

## 7. Required Capture Fields

Section D lists all fields the assistant must collect:
- `patient_name`
- `phone`
- `reason`
- `preferred_time`
- `language_preference`
- `urgency_level`

---

## 8. Tool Schema Display

Section E shows the full `tool_schema` JSON in a monospace code block. Includes:
- Tool name: `capture_appointment_request`
- Target endpoint: `POST /vapi/tools/capture-appointment-request`
- Required header **names** only (values are never shown):
  - `X-Vapi-Service-Name`
  - `X-Vapi-Clinic-Id`
  - `X-Vapi-Scopes`

Secret values are never displayed or requested.

---

## 9. Safety Rules

Section F lists all safety rules and escalation rules from the config pack:
- No diagnosis
- No medical advice
- No treatment recommendations
- No appointment confirmation promise
- Staff/doctor confirms everything
- Emergency escalation to 144 in Austria

---

## 10. Forbidden Claims

Section G lists all forbidden claims:
- Do not claim confirmed appointment
- Do not claim medical diagnosis
- Do not claim treatment advice
- Do not claim production PHI readiness

---

## 11. Readiness Flags

Section H shows the three safety flags:
- `production_phi_enabled` — always `false`
- `recording_ingestion_enabled` — `false` by default
- `transcript_ingestion_enabled` — `false` by default

All flags are displayed in colour: `false` in green, `true` in red. All must be
`false` before any live Vapi binding should occur.

---

## 12. No Live Vapi Binding

The page makes a single GET request to the backend to fetch the config pack.
It does not:
- Call any Vapi API endpoint.
- Store or read Vapi API keys.
- Create or modify Vapi assistant instances.
- Bind Vapi phone numbers.
- Submit any credentials.

---

## 13. api.ts Helper

`frontend/lib/api.ts` exports:

```typescript
interface VapiAssistantConfigPack {
  clinic_id: string
  clinic_display_name: string
  specialty: string
  city: string
  primary_language: string
  fallback_language: string
  supported_languages: string[]
  vapi_assistant_language_mode: string
  assistant_name: string
  voice_locale_recommendation: string
  first_message_de: string
  first_message_en: string
  system_prompt_de: string
  system_prompt_en: string
  tool_schema: Record<string, unknown>
  required_capture_fields: string[]
  safety_rules: string[]
  escalation_rules: string[]
  forbidden_claims: string[]
  production_phi_enabled: boolean
  recording_ingestion_enabled: boolean
  transcript_ingestion_enabled: boolean
  generated_at: string | null
}

fetchVapiAssistantConfigPack(clinicId: string): Promise<VapiAssistantConfigPack>
```

Uses `credentials: 'include'` via `apiFetch`. No sessionStorage. No localStorage.

---

## 14. Safety Boundaries

| Constraint | Enforced by |
|---|---|
| No PHI fields | No patient data shown |
| No Vapi credentials | No Vapi API key or webhook secret shown or requested |
| No sessionStorage | React state only |
| No localStorage | React state only |
| No live Vapi call | Page makes no external requests beyond the backend GET |
| `production_phi_enabled: false` | Hardcoded in backend service; shown read-only |
| Admin session required | `get_current_user` dependency on backend route |
| No secrets | No DATABASE_URL, JWT secret, or Vapi credential fields |

Safety copy on page:
> "Preview only. No Vapi credentials are stored or transmitted.
> No PHI. No secrets. No live Vapi binding. No production activation.
> Production PHI remains NO-GO."

---

## 15. What Remains

| Item | Status |
|---|---|
| Live smoke evidence (Module 143) | Next |
| Vapi credential binding | Pending (C3–C8 blockers) |
| Actual Vapi assistant provisioning | Pending |
| Recording ingestion | Pending |
| Transcript storage | Pending |
| Bilingual assistant testing | Pending |
| Security / legal readiness (DSGVO) | Pending (C3–C8) |
| Production PHI activation | NO-GO — blocked on hardening checklist |

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.
