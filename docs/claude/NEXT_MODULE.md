# Sprint 21 / Module 160 — Live Vapi Binding to One Staging Number

Status: pending.

## Context

Module 159 complete (Simple Clinic Settings):
- Einstellungen tab now editable: Praxisprofil, Öffnungszeiten, Sprachen, KI-Rezeption
- Praxisname, Arzt/Ärztin, Fachrichtung, Ort, Telefonnummer fields
- KI-Ton selector: Freundlich und ruhig / Kurz und direkt / Sehr formell
- KI-Vorschau live preview — no appointment auto-confirmation
- Language settings persisted via existing PATCH /clinics/{id}/language-settings
- No technical fields. No UUIDs. No Vapi config. No PHI.
- All existing contract tests green. Frontend build clean.
- Production PHI remains NO-GO.

## Goal

Connect one staging Vapi phone number to the existing German AI receptionist
so a real phone call to the staging number creates a callback request in the
Anfragen intake queue — ending the full demo loop.

The Vienna receptionist calls the number, speaks to the AI, hangs up, and the
request appears in /dashboard without Ali touching any technical settings.

Staging-only. No real patient data during tests. No production PHI. No
appointment auto-confirmation. No diagnosis/advice/triage.

## What Module 160 must produce

### 1. Vapi → PraxisMed call flow (staging only)

The existing Vapi webhook integration (`POST /webhooks/vapi/call-event`) should
already receive call events. Module 160 verifies and closes the loop:

- Staging Vapi number configured in tenant config for the demo clinic
- Vapi call event creates an appointment_request row in the DB
- source = "vapi", source_ref = call_id
- patient_phone captured from Vapi call metadata
- reason captured from transcript (if available) or empty
- status = "callback_needed"
- No PHI. No real patient data during staging tests.
- No recording URL stored. No transcript stored.
- production_phi_enabled = False

### 2. End-to-end staging test sequence

Ali's demo sequence:
1. Open `/dashboard` — empty or demo queue visible
2. Call the staging Vapi number from any phone
3. Speak a simple request: "Ich möchte einen Termin machen"
4. Hang up
5. Refresh `/dashboard` — new Anfrage visible with callback_needed status
6. Press "Rückruf" or "Als kontaktiert markieren"
7. Demo complete

No live production number. No real patients. No real clinic calls.

### 3. Checks before implementing

Before adding any new code:
- Verify the existing Vapi webhook route creates appointment_requests correctly
- Verify the demo clinic tenant config has a staging Vapi assistant_id
- Verify the VAPI_BINDING_METADATA table has a staging binding for the demo clinic
- If all three are satisfied: Module 160 may be purely docs + smoke evidence
- If not: add minimal backend wiring

### 4. Tests

`backend/tests/test_live_vapi_staging_call_loop_contract.py` (new — ≥10 tests)

Static evidence validation tests:
- Vapi webhook route exists
- Webhook route creates appointment_request with source=vapi
- No transcript stored in staging
- No recording URL stored
- No PHI in webhook payload processing
- production_phi_enabled = False in all created records
- Demo clinic has staging Vapi binding (or pending binding)
- No appointment auto-confirmation from Vapi call
- No diagnosis from Vapi transcript
- Frontend build passes

### 5. Docs updates

- docs/claude/CURRENT_STATE.md — Module 160 entry
- docs/claude/NEXT_MODULE.md — updated to Module 161

## Module 161 preview

Sprint 21 / Module 161 — Arabic/RTL Foundation

Module 161 should:
- Add RTL layout support for Arabic-language clinic UI
- Arabic first_message and system_prompt in Vapi config pack
- Right-to-left CSS for the dashboard shell
- Arabic-first language mode toggle
- No PHI. No real patient data. Production PHI remains NO-GO.

## Constraints

- Staging-only
- No real patient data
- No production PHI
- No appointment auto-confirmation
- No diagnosis/advice/triage
- No external LLM calls
- production_phi_enabled always False
- Frontend build must remain clean
- Full test suite must remain green
- Commit message:
  Sprint 21 / Module 160 — Live Vapi staging call loop
