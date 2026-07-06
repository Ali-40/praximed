# Sprint 19 / Module 141 — Vapi Assistant Configuration Pack Per Tenant

Status: pending implementation.

## Context

Module 140 complete:
- `docs/runtime/LIVE_TENANT_LANGUAGE_SETTINGS_SMOKE_EVIDENCE.md` — PASS
- `backend/tests/test_live_tenant_language_settings_smoke_evidence_contract.py` — 48 tests, all pass
- 3853/3853 backend tests pass
- No frontend changes
- Commit: Sprint 19 / Module 140 — Live tenant language settings smoke evidence

Language settings are live and verified end-to-end on staging. Admin can now
load and update German-first language configuration per clinic. The
`vapi_assistant_language_mode` field stores the intended assistant language
behaviour — but no Vapi-specific prompt pack or per-tenant assistant config
has been generated from it yet.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Create a per-tenant Vapi assistant configuration pack — a structured, static
configuration object that describes how the Vapi assistant should behave for a
given clinic based on that clinic's language settings. This is a data/doc layer
only — no live Vapi credential binding, no API calls to Vapi's platform.

## What Module 141 must implement

### 1. Vapi assistant config service

`backend/app/services/vapi_assistant_config.py` (new):

- Function: `get_vapi_assistant_config(pool, clinic_id) -> dict`
  - Reads clinic language settings (via `get_clinic_language_settings`)
  - Reads clinic config (name, specialty, etc.)
  - Returns a structured config dict:
    ```python
    {
        "clinic_id": str,
        "clinic_name": str,
        "language_mode": str,          # german_first | english_first | bilingual_auto
        "primary_language": str,       # de | en
        "fallback_language": str,      # en | de
        "greeting_language": str,      # de | en (same as primary_language)
        "assistant_persona": str,      # "Praxisassistentin" (de) | "Practice assistant" (en)
        "appointment_capture_only": bool,   # always True
        "no_diagnosis": bool,               # always True
        "no_medical_advice": bool,          # always True
        "production_phi_enabled": bool,     # always False
        "prompt_language_instruction": str, # human-readable instruction for prompt builder
    }
    ```
- `prompt_language_instruction` examples:
  - german_first: "Führe das Gespräch auf Deutsch. Wechsle zu Englisch wenn der Anrufer auf Englisch spricht."
  - english_first: "Conduct the conversation in English. Switch to German if the caller speaks German."
  - bilingual_auto: "Respond in the language the caller uses. Support German and English."

### 2. Schema

`backend/app/schemas/vapi_assistant_config.py` (new):

```python
class VapiAssistantConfig(BaseModel):
    clinic_id: str
    clinic_name: str
    language_mode: str        # german_first | english_first | bilingual_auto
    primary_language: str
    fallback_language: str
    greeting_language: str
    assistant_persona: str
    appointment_capture_only: bool
    no_diagnosis: bool
    no_medical_advice: bool
    production_phi_enabled: bool
    prompt_language_instruction: str
```

### 3. Route

`backend/app/api/routes/vapi_assistant_config.py` (new):

```
GET /clinics/{clinic_id}/vapi-assistant-config
```

- Protected: `get_current_user`
- Returns `VapiAssistantConfig` JSON
- 404 on missing clinic
- No Vapi credentials in response
- No PHI in response
- No secrets in response

Register in `backend/app/api/router.py`.

### 4. Tests

`backend/tests/test_vapi_assistant_config.py` (new):

Static + async tests:
- Schema: all fields present, appointment_capture_only=True, no_diagnosis=True,
  no_medical_advice=True, production_phi_enabled=False always
- Service: german_first → prompt in German, english_first → prompt in English,
  bilingual_auto → bilingual instruction, correct persona per language
- Route: GET requires auth, 404 on missing clinic, 200 returns correct fields,
  no PHI/Vapi credentials/secrets in response

### 5. Docs

- `docs/architecture/VAPI_ASSISTANT_CONFIG_PACK.md` (new):
  - Purpose, route, response fields, language mode instructions,
    safety constraints (appointment_capture_only, no_diagnosis, no_medical_advice,
    production_phi_enabled=False), what it does not do (no live Vapi binding),
    remaining work
- `docs/claude/CURRENT_STATE.md` — Module 141 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 142

## Constraints

- No live Vapi credential binding (no calls to Vapi API)
- No PHI in response
- No secrets in response
- appointment_capture_only always True
- no_diagnosis always True
- no_medical_advice always True
- production_phi_enabled always False
- credentials: 'include' on all frontend fetches (if any)
- German-first defaults
- Full test suite must remain green
- Commit message:
  Sprint 19 / Module 141 — Vapi assistant configuration pack per tenant
