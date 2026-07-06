# PraxisMed — Tenant Language Settings API Foundation

**Sprint 19 / Module 138**
**Date:** 2026-07-06
**Status:** Implemented

---

## 1. Purpose

This document describes the backend foundation for reading and updating clinic
language settings. Language settings control the clinic's AI assistant language,
patient/caller language fallback, and UI defaults.

German-first is the default for Austrian clinics. English fallback is supported.
No PHI. No Vapi credentials. No secrets. Production PHI remains NO-GO.

---

## 2. Routes

```
GET  /clinics/{clinic_id}/language-settings
PATCH /clinics/{clinic_id}/language-settings
```

| Property | Value |
|---|---|
| Auth | Required (`get_current_user` session cookie or Bearer) |
| GET `200` | Returns current language settings (German-first defaults if unconfigured) |
| GET `404` | Clinic not found |
| PATCH `200` | Returns updated language settings |
| PATCH `400` | primary_language not in supported_languages |
| PATCH `404` | Clinic not found |
| PATCH `422` | Invalid field value (unsupported language code or vapi mode) |

---

## 3. Schema

### ClinicLanguageSettingsRead (response)

| Field | Type | Default |
|---|---|---|
| `ok` | bool | `true` |
| `clinic_id` | str | — |
| `primary_language` | str | `"de"` |
| `fallback_language` | str | `"en"` |
| `supported_languages` | list[str] | `["de", "en"]` |
| `default_patient_language` | str | `"de"` |
| `vapi_assistant_language_mode` | str | `"german_first"` |
| `clinic_ui_language` | str | `"de"` |
| `updated_at` | str \| null | — |

### ClinicLanguageSettingsUpdate (request body — all fields optional)

| Field | Allowed values |
|---|---|
| `primary_language` | `de`, `en` |
| `fallback_language` | `de`, `en` |
| `supported_languages` | non-empty list of `de`/`en` |
| `default_patient_language` | `de`, `en` |
| `vapi_assistant_language_mode` | `german_first`, `english_first`, `bilingual_auto` |
| `clinic_ui_language` | `de`, `en` |

---

## 4. German-First Default

For Austrian clinics, the German-first default is applied when no explicit
language settings are stored:

```python
GERMAN_FIRST_DEFAULTS = {
    "primary_language":             "de",
    "fallback_language":            "en",
    "supported_languages":          ["de", "en"],
    "default_patient_language":     "de",
    "vapi_assistant_language_mode": "german_first",
    "clinic_ui_language":           "de",
}
```

If a clinic has `locale = 'de-AT'` in the database but no JSON config file,
all settings are derived from this default. No migration is required.

---

## 5. English Fallback

English is the default fallback language for all Austrian clinics:

- `fallback_language = "en"` by default
- `supported_languages = ["de", "en"]` by default
- `vapi_assistant_language_mode` can be set to `english_first` or `bilingual_auto`
  to support English-first or bilingual caller experiences

---

## 6. Vapi Assistant Language Mode

`vapi_assistant_language_mode` controls how the Vapi voice assistant selects
its response language:

| Mode | Description |
|---|---|
| `german_first` | Always attempt German; fall back to English if caller responds in English |
| `english_first` | Always attempt English; fall back to German |
| `bilingual_auto` | Detect caller language automatically and respond in-kind |

This field is stored in the tenant JSON config file. It does not bind any
Vapi credentials — it is a configuration intent marker only.

---

## 7. Clinic UI Language

`clinic_ui_language` controls the default language of the clinic-facing UI
(dashboard, notifications, admin console). Defaults to `"de"` for Austrian clinics.

---

## 8. Storage Approach

No new database migration is required. Language settings are stored in two places:

| Storage | Field(s) |
|---|---|
| `clinics.locale` (DB) | `primary_language` (via locale mapping: `de-AT` ↔ `de`) |
| `backend/tenants/configs/{clinic_id}/clinic_config.json` | All language fields under `language_config` key |

On `GET`: `clinics.locale` is read from the database; the JSON config file
is read if present. JSON file values take precedence over locale-derived values.

On `PATCH`: `clinics.locale` is updated in the database; the full language
settings are written to the JSON config file (created if absent).

The JSON config file also updates the top-level `language` and `fallback_language`
keys for compatibility with the existing `ClinicConfig` loader.

---

## 9. Locale Mapping

| `primary_language` | `clinics.locale` |
|---|---|
| `de` | `de-AT` |
| `en` | `en-US` |

| `clinics.locale` | `primary_language` |
|---|---|
| `de-AT` | `de` |
| `de-DE` | `de` |
| `en-US` | `en` |
| `en-GB` | `en` |

---

## 10. Tenant Provisioning Integration

When `provision_clinic_shell_from_onboarding_request` creates a new clinic shell,
it now also writes a `language_config` JSON file deriving from the onboarding
request's language preferences:

| Onboarding request field | language_config field |
|---|---|
| `preferred_language` | `primary_language`, `default_patient_language`, `clinic_ui_language` |
| `fallback_language` | `fallback_language` |
| `supported_languages` | `supported_languages` |
| — | `vapi_assistant_language_mode = "german_first"` (if `preferred_language = "de"`) |

The file write is best-effort — if it fails, the audit log retains the full
language preference record and the `clinics.locale` column remains authoritative.

---

## 11. Safety Constraints

| Constraint | Status |
|---|---|
| No PHI stored or returned | **ENFORCED** — no patient_name, diagnosis, or PHI fields |
| No Vapi credentials | **ENFORCED** — vapi_assistant_language_mode is a config intent, not a credential |
| No secrets | **ENFORCED** — no API keys, tokens, or passwords in any field |
| Auth required for both endpoints | **ENFORCED** — `get_current_user` dependency |
| Invalid language codes rejected | **ENFORCED** — Pydantic validators at schema layer |
| Empty supported_languages rejected | **ENFORCED** — Pydantic validator |
| primary_language must be in supported_languages | **ENFORCED** — model_validator + service guard |
| German-first default preserved | **ENFORCED** — GERMAN_FIRST_DEFAULTS applied when no config |
| No automatic language change on status update | **ENFORCED** — no hook or trigger |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |

---

## 12. What Remains

| Item | Status |
|---|---|
| Frontend admin language settings UI | **Planned — Module 139** |
| Vapi assistant config binding | **Future — requires Vapi API integration** |
| Real bilingual assistant testing | **Future — requires Vapi testing environment** |
| Multilingual Vapi prompt templates | **Future** |
| More language codes (fr, tr, etc.) | **Future — currently de/en only** |
| Legal / security readiness | **NO-GO — C3–C8 blockers open** |
| DSGVO compliance claim | **NO-GO — C8 legal review required** |
