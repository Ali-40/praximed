# Sprint 21 / Module 161 — Arabic/RTL Foundation

Status: pending.

## Context

Module 160 complete (Live Vapi Staging Call Loop):
- data-live-demo-hint span added to dashboard demo strip (plain German, no technical content)
- Existing POST /vapi/tools/capture-appointment-request verified — handles full call flow
- German AI receptionist script: greeting, data collection (Name/Telefon/Anliegen/Zeit), "Praxisteam meldet sich zur Bestätigung zurück", emergency 144 routing
- Vapi Dashboard checklist: header names only (values from environment, never in docs)
- No transcript storage. No recording URL storage. No auto-confirmation. No diagnosis. No PHI.
- 54+ new contract tests. Frontend build clean. Production PHI remains NO-GO.

## Goal

Add RTL layout support and Arabic-language configuration so a Vienna clinic with Arabic-speaking
patients can switch the AI receptionist to Arabic-first mode.

## What Module 161 must produce

### 1. RTL CSS layout

- `dir="rtl"` support in dashboard shell for Arabic mode
- Right-to-left CSS for the main layout columns and text
- No layout breakage in default German (LTR) mode
- Toggle in Einstellungen tab under Sprachen: "Arabisch (Vorschau)" → enables RTL when selected as primary

### 2. Arabic first_message and system_prompt

- Arabic greeting added to the Vapi config pack for the demo clinic
- Arabic-language assistant greets in Arabic, collects the same fields (name, phone, reason, preferred time)
- Emergency routing: "في حالة الطوارئ اتصل بـ 144 فوراً"
- "Das Praxisteam meldet sich" equivalent in Arabic: "سيتواصل معك فريق العيادة للتأكيد"
- No appointment auto-confirmation. No diagnosis. No medical advice. No triage.

### 3. Arabic-first language mode toggle

- When Arabic is selected as primary language in Einstellungen → Sprachen:
  - KI-Vorschau preview shows Arabic greeting
  - Dashboard subtitle switches to Arabic "مرحباً بك في العيادة الرقمية"
  - Layout applies RTL

### 4. Tests

`backend/tests/test_arabic_rtl_foundation_contract.py` (new — ≥15 tests)

Static evidence tests:
- Dashboard CSS includes dir="rtl" or rtl layout class when Arabic active
- Arabic greeting exists in Vapi config or Einstellungen preview
- Arabic emergency routing "144" in Arabic text
- "Arabisch" option exists in Sprachen section
- No appointment auto-confirmation in Arabic path
- No diagnosis in Arabic assistant config
- No PHI. production_phi_enabled = False
- LTR layout not broken for German mode
- Frontend build passes

### 5. Docs updates

- docs/claude/CURRENT_STATE.md — Module 161 entry
- docs/claude/NEXT_MODULE.md — updated to Module 162

## Module 162 preview

Sprint 21 / Module 162 — Five-Minute Clinic Demo Script and Sales Pack

Module 162 should:
- Create a structured 5-minute demo script for Ali to use in Vienna clinic visits
- Printable one-page "demo card" with step-by-step flow
- Talking points for each dashboard section (Anfragen, Patienten, Einstellungen)
- Objection handling notes (GDPR, data security, pricing, accuracy)
- No patient data. No PHI. No technical content visible.

## Constraints

- No real patient data
- No production PHI
- No appointment auto-confirmation
- No diagnosis/advice/triage
- No external LLM calls
- production_phi_enabled always False
- Frontend build must remain clean
- Full test suite must remain green
- Commit message:
  Sprint 21 / Module 161 — Arabic/RTL foundation
