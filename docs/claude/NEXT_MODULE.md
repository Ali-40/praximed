# Sprint 21 / Module 158 — One-Click Demo Flow

Status: pending.

## Context

Module 157 complete (Doctor-Facing Sales MVP Simplification):
- Existing /dashboard simplified into clinic-facing, German-first, UUID-hidden MVP.
- Heute summary bar: Neue Anfragen / Rückruf nötig / Dringend prüfen / Erledigt.
- Anfragen / Patienten / Einstellungen tabs.
- Human-readable request numbers (Anfrage #1, Anfrage #2).
- German status labels via getGermanStatusLabel.
- Rückruf and Als kontaktiert markieren actions.
- No visible UUIDs in clinic-facing UI.
- All existing contract tests green. Frontend build clean.
- Production PHI remains NO-GO.

## Goal

Add a "Create demo call" button to the existing /dashboard that instantly populates
the Anfragen queue with a realistic synthetic appointment request, so Ali can demo
the full intake-to-callback flow in a Vienna clinic without needing backend setup.

Staging-only synthetic data. No Vapi live call. No real patient data. No PHI.
No diagnosis. No medical advice. No triage scoring. Production PHI remains NO-GO.

Docs/tests only. No new backend domain complexity. No migration.

## What Module 158 must produce

### 1. Backend route (optional — inspect existing synthetic data endpoints first)

Check if a synthetic/demo-data creation endpoint already exists.
If it does, wire the frontend to it.
If it does not, add a safe staging-only POST endpoint:

`POST /clinics/{clinic_id}/demo/create-demo-request`

- Creates a synthetic appointment_request row
- patient_name: realistic Austrian name (e.g., "Mag. Klaus Hofer")
- reason: "Rücken­schmerzen seit 3 Tagen"
- status: new
- urgency_level: normal
- source: staging_demo
- production_phi_enabled: false
- synthetic_demo: true

Returns: `{ ok: true, request_id: "...", message: "Demo-Anfrage erstellt." }`

No real patient data. No PHI. No Vapi. No audio. No real call.

### 2. Frontend: "Demo-Anfrage erstellen" button

Add to /dashboard (Anfragen tab or Heute header):

Button: **"Demo-Anfrage erstellen"**
- Calls POST endpoint (or uses existing synthetic data API)
- Refreshes the Anfragen queue
- Shows a brief success message: "Demo-Anfrage wurde der Warteschlange hinzugefügt."
- Error copy: "Demo-Anfrage konnte nicht erstellt werden."
- Button disabled while in progress

### 3. Optional: one-click demo reset

If a demo reset endpoint exists or can be safely added:

Button: **"Demo zurücksetzen"**
- Clears all synthetic_demo=true requests for the clinic
- Refreshes the queue
- Staging-only. Protected behind staging-only guard.

If reset is complex, defer to Module 159.

### 4. Tests

`backend/tests/test_one_click_demo_flow_contract.py` (new — ≥15 tests)

Static evidence validation tests (no live API calls):
- Demo button exists in dashboard source
- Demo button label is in German
- Demo button wires to demo endpoint
- Demo success copy is German
- Demo error copy is German
- Demo data is synthetic (production_phi_enabled=false)
- No real patient names in demo request creation code
- No PHI in demo endpoint
- No diagnosis in demo endpoint
- No medical advice in demo endpoint
- No live Vapi call triggered
- No real patient data in demo flow
- Demo endpoint is staging-only (if added)
- Frontend build passes
- Existing tests still green

### 5. Docs updates

- docs/claude/CURRENT_STATE.md — Module 158 entry
- docs/claude/NEXT_MODULE.md — updated to Module 159

## Module 159 preview

Sprint 21 / Module 159 — Clinic Settings Editor

Module 159 should:
- Add editable clinic settings to the Einstellungen tab in /dashboard
- Doctor name, specialty, clinic name, language preference
- Read from existing clinic language settings endpoint
- Write via existing PATCH /clinics/{clinic_id}/language-settings
- No PHI fields
- No Vapi credential entry in clinic-facing UI (that stays in developer console)
- Production PHI remains NO-GO

## Constraints

- Staging-only synthetic data — no real patient data
- No PHI unlock
- No Vapi live call
- No diagnosis, no medical advice, no triage scoring
- production_phi_enabled=False in all demo data
- Frontend build must remain clean
- Full test suite must remain green
- Commit message:
  Sprint 21 / Module 158 — One-click demo flow
