# Sprint 21 / Module 164 — Simple Clinic Calendar Foundation

Status: pending.

## Context

Module 162 (outreach extension) complete (Sales Demo Polish and Outreach Readiness):
- Expanded CLINIC_OUTREACH_EXECUTION_PACK.md — phone script, follow-up after demo, 10 objections, pricing, calendar positioning, CTA options
- SALES_ONE_LINERS.md — 11 memorizable one-line pitches
- TOMORROW_FIRST_SALES_DAY_PLAN.md — exact first-sales-day schedule
- clinic_outreach_tracker_template.csv — ready-to-use spreadsheet
- 85 comprehensive contract tests. 5540 total. Frontend build clean. Production PHI remains NO-GO.
- Calendar positioned as next pilot workflow — not built yet, not promised as finished.

## Sprint 21 Sales-MVP Pivot — Paused until further notice

The following tracks remain paused:
- Arabic/RTL foundation
- Gulf/FHIR/pediatric expansion
- Smoke evidence docs
- Patient Story narrative
- Additional developer-console tooling
- Deeper anamnesis modules

## Why Calendar Now

After sales/demo readiness, the next actual product feature clinics will ask for is calendar:
clinics need to turn callback requests into actual scheduled appointments.

The current sales answer to calendar questions is:
"Im Pilot starten wir mit der Rückruf- und Anfrage-Übersicht. Der nächste Schritt ist ein
einfacher Kalender-Workflow: Anfrage prüfen, Termin vorschlagen, vom Praxisteam bestätigen.
Wir bauen das nicht als kompliziertes Buchungssystem, sondern passend zu Ihrem Praxisablauf."

Module 164 delivers that next step.

## Goal

Add a simple clinic calendar foundation — day view, staff-created appointments only,
no external calendar sync, no Google Calendar, no auto-confirmation.

## What Module 164 must produce

### 1. Backend: Appointments table and basic routes

New migration:
- `appointments` table: id, clinic_id, patient_name (optional), date, time, type, status, notes, created_by, created_at

Statuses: `proposed`, `confirmed`, `cancelled`, `completed`

Routes (new file `backend/app/api/routes/appointments.py`):
- `GET /clinics/{clinic_id}/appointments` — list appointments by date range
- `POST /clinics/{clinic_id}/appointments` — staff creates appointment
- `PATCH /clinics/{clinic_id}/appointments/{id}` — staff updates status or details
- No DELETE route
- Requires `get_current_user` auth
- Requires `enforce_phi_safeguard`
- No auto-confirmation
- No diagnosis, no medical advice, no triage
- No external calendar sync

### 2. Frontend: Calendar tab in /dashboard

Add "Kalender" tab to the existing Anfragen / Patienten / Einstellungen tab row.

Day view first:
- Shows appointments for selected day
- Staff can create a new appointment (name optional, date/time, type/Anliegen, notes)
- Staff can change status (proposed → confirmed → completed)
- No auto-confirmation

German labels only:
- Termin
- Vorgeschlagen / Bestätigt / Abgesagt / Erledigt
- Neuer Termin
- Kein Termin für diesen Tag

### 3. No external sync

- No Google Calendar
- No iCal export yet
- No patient-facing booking link
- No SMS/email confirmation automation

### 4. Tests

`backend/tests/test_simple_clinic_calendar_foundation_contract.py` (new — ≥20 tests)

Static evidence tests:
- Appointments migration file exists
- Appointments table has correct columns
- Routes file exists with correct endpoints
- No auto-confirmation in routes
- No diagnosis/medical advice in routes
- No DELETE route
- PHI safeguard in routes
- Frontend has Kalender tab
- Frontend has German appointment labels
- Frontend shows no auto-confirmation
- No external calendar URL
- No Google Calendar reference
- No iCal reference
- Safety boundaries intact

### 5. Docs updates

- docs/claude/CURRENT_STATE.md — Module 164 entry
- docs/claude/NEXT_MODULE.md — updated to Module 165

## Module 165 preview

Sprint 21 / Module 165 — Request-to-Appointment Path

Module 165 should:
- Allow staff to convert a callback request into a calendar appointment in one click
- "Termin erstellen" button on a Rückruf nötig request
- Pre-fills date/time/name from the request
- Staff confirms before saving
- No auto-confirmation
- No PHI unlock
- No external sync

## Constraints

- No real patient data
- No production PHI
- No external calendar sync
- No auto-confirmation
- No diagnosis/medical advice/triage
- No DELETE route
- Staff review required before confirmed status
- production_phi_enabled always False
- Frontend build must remain clean
- Full test suite must remain green
- Commit message:
  Sprint 21 / Module 164 — Simple clinic calendar foundation
