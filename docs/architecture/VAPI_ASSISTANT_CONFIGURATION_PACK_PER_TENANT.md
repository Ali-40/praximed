# PraxisMed — Vapi Assistant Configuration Pack Per Tenant

**Sprint 19 / Module 141**
**Date:** 2026-07-06
**Status:** Implemented

---

## 1. Purpose

This document describes the per-tenant Vapi assistant configuration pack — a
structured, safe configuration object that specifies how the Vapi AI assistant
should behave for a given clinic. It is derived entirely from existing clinic
language settings and tenant config. No live Vapi binding occurs. No secrets
are stored or returned. No PHI. Production PHI remains NO-GO.

---

## 2. Route

```
GET /clinics/{clinic_id}/vapi-assistant-config-pack
```

| Property | Value |
|---|---|
| Auth | Required (`get_current_user` session cookie) |
| 200 | Returns `VapiAssistantConfigPack` JSON |
| 401 | No admin session |
| 403 | Insufficient permissions |
| 404 | Clinic not found |
| 500 | Unexpected server error |

---

## 3. Service Behaviour

`backend/app/services/vapi_assistant_config.build_vapi_assistant_config_pack(pool, clinic_id)`

1. Verify clinic exists in `clinics` table — raises `ClinicNotFoundError` if missing.
2. Load clinic language settings via `get_clinic_language_settings` (Module 138).
3. Load safe tenant config JSON file for display fields: `clinic_display_name`,
   `specialty`, `city`. No secrets are loaded.
4. Derive language mode from `vapi_assistant_language_mode`.
5. Build German system prompt and English system prompt from templates.
6. Build German and English first messages.
7. Include static tool schema targeting `POST /vapi/tools/capture-appointment-request`.
8. Include required capture fields, safety rules, escalation rules, forbidden claims.
9. Return config pack with `production_phi_enabled: false` always.

No Vapi API calls are made. No secrets are written or returned.

---

## 4. German-First Assistant

### Identity

> Du bist die KI-Rezeption von {clinic_display_name}, einer privaten Praxis in Wien.

### Tone

- Höflich und professionell
- Ruhig und klar
- Österreichischer Praxis-Kontext
- Keine übertriebene Marketing-Sprache

### Task

- Terminanfragen aufnehmen
- Name, Telefonnummer, Anliegen, gewünschte Zeit erfassen
- Sprache erkennen
- Anfrage an das Praxisteam weiterleiten

---

## 5. English Fallback

### Identity

> You are the AI receptionist for {clinic_display_name}, a private clinic in Vienna.

### Tone

- Polite and professional
- Calm and clear
- Clinic receptionist style
- No exaggerated marketing language

### Language Switching

- German-first: default to German, switch to English if caller speaks English.
- English-first: default to English, switch to German if caller speaks German.
- Bilingual auto: respond in the language the caller uses.

---

## 6. Required Capture Fields

The assistant must collect:

| Field | Description |
|---|---|
| `patient_name` | Full name of the patient |
| `phone` | Callback phone number |
| `reason` | Reason for the appointment request |
| `preferred_time` | Preferred appointment time or time range |
| `language_preference` | Language preference of the caller |
| `urgency_level` | Assessed urgency: `low`, `medium`, `high` |

---

## 7. Tool Schema

The assistant is configured with one tool:

```
name: capture_appointment_request
target: POST /vapi/tools/capture-appointment-request
```

Required fields: `patient_name`, `phone`, `reason`
Optional fields: `preferred_time`, `urgency_level`, `language_preference`, `clinic_ref`, `call_id`

Header names required by the Vapi runtime (values are never included):
- `X-Vapi-Service-Name`
- `X-Vapi-Clinic-Id`
- `X-Vapi-Scopes`

---

## 8. Safety Rules

All of the following are enforced by the prompt and tool schema:

- **No diagnosis.** The assistant never suggests what condition the caller may have.
- **No medical advice.** No treatment, medication, or procedure recommendations.
- **No appointment confirmation.** The assistant states the clinic team will review and confirm.
- **No treatment recommendations.** Only the doctor or clinic team confirms appointments.
- **Emergency escalation.** If the caller describes acute or life-threatening symptoms,
  the assistant instructs them to call **144** (Austria emergency number) or go to
  the nearest emergency department immediately.
- **Appointment capture only.** The assistant's sole task is to capture the request.
- **No PHI beyond captured fields.** Sensitive data is not repeated or stored beyond the request.
- **No secrets in responses.** API keys, webhook secrets, and credentials are never output.

---

## 9. Emergency Handling — Austria 144

In both German and English system prompts:

> **German:** Bei akuten Notfällen: Weise den Anrufer sofort an, den Notruf 144 zu wählen
> oder eine medizinische Notaufnahme aufzusuchen.

> **English:** For urgent or life-threatening emergencies in Austria, instruct the caller
> to call 144 immediately or go to the nearest emergency department.

The assistant does not perform triage. It directs callers to emergency services.

---

## 10. No Live Vapi Binding

This config pack is a **data object only**. It does not:

- Call any Vapi API endpoint.
- Store or read Vapi API keys.
- Create or modify Vapi assistant instances.
- Bind Vapi phone numbers.
- Process real call audio or transcripts.

Live Vapi binding is a future step (post C3–C8 hardening).

---

## 11. Safety Boundaries

| Constraint | Enforced by |
|---|---|
| No PHI | No patient data fields in schema or service |
| No secrets | No Vapi API key, webhook secret, or DATABASE_URL |
| No live Vapi call | Service makes no external HTTP requests |
| `production_phi_enabled: false` | Hardcoded False in service and schema |
| `recording_ingestion_enabled: false` | Default False; only True if tenant feature flag set |
| `transcript_ingestion_enabled: false` | Default False; only True if tenant feature flag set |
| Admin session required | `get_current_user` dependency on route |
| No diagnosis | Enforced in both system prompts and safety_rules list |
| No medical advice | Enforced in both system prompts and forbidden_claims list |

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

---

## 12. What Remains

| Item | Status |
|---|---|
| Frontend admin config preview UI (Module 142) | Next |
| Live Vapi credential binding | Pending (C3–C8 blockers) |
| Recording ingestion | Pending |
| Transcript storage | Pending |
| Bilingual assistant testing | Pending |
| Security / legal readiness (DSGVO) | Pending (C3–C8) |
| Production PHI activation | NO-GO — blocked on hardening checklist |
