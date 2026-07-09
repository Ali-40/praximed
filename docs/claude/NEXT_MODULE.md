# Sprint 21 / Module 162 — Sales Demo Polish and Walk-In Readiness

Status: pending.

## Context

Module 161 complete (Five-Minute Clinic Demo Script and Sales Pack):
- FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md — 5-minute script, receptionist + doctor talk tracks
- THIRTY_DAY_PILOT_OFFER.md — pilot structure, €390 setup, €290–€490/month anchor
- ONE_PAGE_CLINIC_HANDOUT.md — print-ready handout, no technical language
- OBJECTION_HANDLING.md — 10 objections, honest answers, no overclaims
- DEMO_DAY_CHECKLIST.md — before/during/after checklist
- 71 new contract tests. 5358 total. Production PHI remains NO-GO.

## Sprint 21 Sales-MVP Pivot — Paused until further notice

The following tracks remain paused:
- Arabic/RTL foundation
- Gulf/FHIR/pediatric expansion
- Smoke evidence docs
- Patient Story narrative
- Additional developer-console tooling
- Deeper anamnesis modules

## Goal

Inspect /dashboard from a sales perspective and smooth any rough edges that
could cost momentum during a clinic walkthrough.

This is a polish pass — no new infrastructure, no new features, no migrations.
Only changes that make the sales demo cleaner, faster to understand, and
more convincing on first impression.

## What Module 162 must inspect and fix

### 1. Empty-state check

When Ali first opens /dashboard with no demo calls in the queue, the Anfragen
tab may show an empty state. This could look broken or unimpressive.

Module 162 should:
- Verify the empty state has a clean, non-technical German message
- If the empty state shows technical copy or nothing, replace with:
  "Noch keine Anfragen. Klicken Sie auf 'Demo-Anruf erstellen' um den Demo-Modus zu starten."
- Do not auto-populate without user action

### 2. Button copy review

Review these buttons for clarity:
- "Demo-Anruf erstellen" — check it is prominent and obvious
- "Demo zurücksetzen" — check it is labeled clearly and is secondary (not primary)
- "Rückruf" — check it is clear (short enough, action-oriented)
- "Als kontaktiert markieren" — check it reads naturally

If any button copy is confusing for a non-technical receptionist, improve it.

### 3. Heute summary bar

Verify the Heute summary bar shows meaningful numbers in demo mode:
- After "Demo-Anruf erstellen": "Heute" bar should reflect the new request
- If numbers are always zero even after demo creation, fix the count logic

### 4. No visible technical terms

Scan /dashboard for any remaining technical words visible in the default view:
- No UUID visible
- No "staging" in visible UI text (only in hidden safety comments)
- No "webhook", "API", "Vapi", "FHIR", "token", "JWT" in visible text
- No "production_phi_enabled" visible
- No error messages containing technical details

### 5. Einstellungen tab first impression

Check the Einstellungen tab opens to a welcoming default state:
- Praxisname field has a sensible placeholder (not empty or UUID)
- KI-Vorschau is visible without scrolling (or close to top)
- No technical labels visible

### 6. Tests

`backend/tests/test_sales_demo_polish_walk_in_readiness_contract.py` (new — ≥10 tests)

Static contract tests:
- Dashboard has no visible UUID in default view
- Dashboard has no "staging" in visible German text
- Dashboard has no "webhook" in visible text
- Dashboard has no "JWT" or "token" in visible text
- Anfragen tab has empty-state text in German
- Demo strip is yellow/warning-colored (not default gray)
- Heute summary bar exists
- Einstellungen tab has Praxisname placeholder
- KI-Vorschau is present in Einstellungen tab
- No technical error messages containing endpoint URLs in visible text

### 7. Docs updates

- docs/claude/CURRENT_STATE.md — Module 162 entry
- docs/claude/NEXT_MODULE.md — updated to Module 163

## Module 163 preview

Sprint 21 / Module 163 — First Pilot Clinic Onboarding Script

Module 163 should:
- Create a structured onboarding checklist for the first actual paying pilot clinic
- Staff welcome message template
- First-week support guide
- How to handle the transition from demo to live (when AVV is signed)
- No PHI. No automation. Staff confirms everything.

## Constraints

- No real patient data
- No production PHI
- No new backend endpoints
- No new migrations
- No Arabic/RTL, no FHIR, no Gulf expansion
- No compliance overclaims
- No technical language in clinic-facing copy
- production_phi_enabled always False
- Frontend build must remain clean
- Full test suite must remain green
- Commit message:
  Sprint 21 / Module 162 — Sales demo polish and walk-in readiness
