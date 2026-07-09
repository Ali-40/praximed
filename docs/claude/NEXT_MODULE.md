# Sprint 21 / Module 159 — Clinic Settings Editor

Status: pending.

## Context

Module 158 complete (One-Click Demo Flow):
- POST /demo/sales-mvp/create-call — creates synthetic demo appointment request
- POST /demo/sales-mvp/reset — archives demo records
- Demo-Modus strip in /dashboard Anfragen tab
- "Demo-Anruf erstellen" and "Demo zurücksetzen" buttons
- German success/error copy
- Staging-only guard (HTTP 403 in production)
- All existing contract tests green. Frontend build clean.
- Production PHI remains NO-GO.

## Goal

Add editable clinic settings to the **Einstellungen** tab in `/dashboard`
so a doctor or receptionist can update their clinic name, doctor name,
specialty, and language preference — using the existing
`PATCH /clinics/{clinic_id}/language-settings` endpoint.

Currently the Einstellungen tab is read-only. Module 159 makes it editable.

No PHI fields. No Vapi credential entry in clinic-facing UI (that stays in
developer console). Production PHI remains NO-GO.

## What Module 159 must produce

### 1. Frontend: editable Einstellungen tab

Replace the read-only `<dl>` in the Einstellungen tab with an editable form:

Fields:
- **Praxisname** — read from `clinicDisplayName`, display only (no backend write)
- **Arzt/Ärztin** — doctor name, editable (if field available in language settings)
- **Fachrichtung** — specialty, editable (if field available)
- **Bevorzugte Sprache** — `primary_language` — dropdown: Deutsch, English
- **Fallback-Sprache** — `fallback_language` — dropdown

On load:
- Fetch `GET /clinics/{clinic_id}/language-settings` (existing endpoint, already in api.ts)
- Populate form fields from response

On save:
- PATCH `/clinics/{clinic_id}/language-settings` (existing endpoint)
- Show success: "Einstellungen gespeichert."
- Show error: "Einstellungen konnten nicht gespeichert werden."

No PHI fields. No Vapi credential fields. No UUID shown.

### 2. Optional: doctor name / specialty fields

Check if `clinic_language_settings` already has `doctor_name` and `specialty` columns.
- If yes: include in the editable form (PATCH)
- If no: skip for Module 159, defer to Module 160

### 3. Tests

`backend/tests/test_clinic_settings_editor_contract.py` (new — ≥10 tests)

Static evidence validation tests (no live API calls):
- Einstellungen tab has editable form fields
- Save button exists with German label
- Success copy is German
- Error copy is German
- No PHI fields in form
- No Vapi credential fields
- fetchClinicLanguageSettings is imported in dashboard
- updateClinicLanguageSettings is imported in dashboard
- Settings save handler exists
- Frontend build passes

### 4. Docs updates

- docs/claude/CURRENT_STATE.md — Module 159 entry
- docs/claude/NEXT_MODULE.md — updated to Module 160

## Module 160 preview

Sprint 21 / Module 160 — AI Receptionist Value Story

Module 160 should:
- Add a value story panel to the Einstellungen tab
- Show "Was PraxisMed für Sie tut": missed call capture → AI intake → Rückruf
- Demonstrate the full loop using the demo data from Module 158
- No Vapi live call. No real patient data. No PHI.
- Production PHI remains NO-GO.

## Constraints

- No PHI fields
- No Vapi credential entry in clinic-facing UI
- No UUIDs shown to clinic users
- Frontend build must remain clean
- Full test suite must remain green
- Commit message:
  Sprint 21 / Module 159 — Clinic settings editor
