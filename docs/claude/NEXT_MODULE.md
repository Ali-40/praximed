# Sprint 19 / Module 138 — Tenant Language Settings API Foundation

Status: pending implementation.

## Context

Module 137 complete:
- `docs/runtime/LIVE_TENANT_PROVISIONING_SMOKE_EVIDENCE.md` — PASS; clinic shell provisioned from UI; idempotency verified
- `backend/tests/test_live_tenant_provisioning_smoke_evidence_contract.py` — 39 tests, all pass
- 3651/3651 backend tests pass
- No frontend changes
- Commit: Sprint 19 / Module 137 — Live tenant provisioning smoke evidence

A clinic shell now exists in staging (status=`pilot_setup`). The next step is
to allow admin/staff to read and update the clinic's language settings —
German-first by default, English fallback — via a protected API.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Add a backend API foundation for reading and updating tenant language settings
for a provisioned clinic shell.

Language settings are stored in the existing `clinics` table (`locale` column).
The API must expose a clear, simple structure and enforce German-first defaults.

## What Module 138 must implement

### 1. Backend — language settings service

`backend/app/services/language_settings.py` (new):
- `get_language_settings(pool, clinic_id)` → dict with `preferred_language`, `fallback_language`, `supported_languages`, `locale`
- `update_language_settings(pool, clinic_id, preferred_language, fallback_language, supported_languages)` → updated dict
- German-first default: `preferred_language=de`, `fallback_language=en`, `supported_languages=["de","en"]`
- `locale` derived from `preferred_language`: `de` → `de-AT`, `en` → `en-US`
- Validates `preferred_language` is in `supported_languages`
- No Vapi credentials accepted or stored
- No patient data
- No production PHI

### 2. Backend — language settings route

`backend/app/api/routes/language_settings.py` (new):
- `GET /clinics/{clinic_id}/language-settings` — read current language settings
  - Protected: requires `get_current_user`
  - Returns: `{ ok, clinic_id, preferred_language, fallback_language, supported_languages, locale }`
- `PATCH /clinics/{clinic_id}/language-settings` — update language settings
  - Protected: requires `get_current_user`
  - Body: `{ preferred_language, fallback_language?, supported_languages? }`
  - Returns: same shape as GET
  - 404 if clinic not found
  - 400 if preferred_language not in supported_languages

### 3. Backend — schemas

`backend/app/schemas/language_settings.py` (new):
- `LanguageSettingsResponse`: `ok`, `clinic_id`, `preferred_language`, `fallback_language`, `supported_languages`, `locale`
- `LanguageSettingsUpdate`: `preferred_language`, `fallback_language` (optional), `supported_languages` (optional)

### 4. Tests

`backend/tests/test_tenant_language_settings_api_foundation.py` (new):
- Static: service/route/schema files exist, no Vapi, no patient data, no PHI, auth required
- Service: get returns correct fields, de→de-AT locale mapping, en→en-US, default language
- Service: update sets locale from preferred_language, validates preferred in supported
- Route: unauth→401, GET→200+fields, PATCH→200+updated, 404 on missing, 400 on invalid language
- No sessionStorage, no localStorage in any frontend file (not applicable to backend, skip)
- Arch doc: exists, mentions German-first, no PHI, no Vapi

### 5. Docs

- `docs/architecture/TENANT_LANGUAGE_SETTINGS_API.md` — new
- `docs/claude/CURRENT_STATE.md` — Module 138 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 139

## Constraints

- No production PHI activation
- No Vapi credentials accepted or stored
- German-first default enforced
- `preferred_language` must be in `supported_languages`
- Auth required for all language settings endpoints
- Full test suite must remain green
- Frontend build must pass (no frontend changes expected)
- Commit message:
  Sprint 19 / Module 138 — Tenant language settings API foundation
