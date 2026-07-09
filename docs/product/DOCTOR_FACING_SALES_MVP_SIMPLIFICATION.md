# Doctor-Facing Sales MVP Simplification

**Sprint 21 / Module 157**
**Date:** 2026-07-09
**Status:** Complete

---

## Why We Pivoted

After Sprint 20 (Modules 151–156), PraxisMed had a technically sound platform:
consent recording, AI structuring, staff review/merge, and a longitudinal patient
timeline. But none of it was visible to a clinic without navigating developer tools,
understanding UUIDs, or knowing what a "structuring run" is.

The product pivot: make PraxisMed understandable to a Vienna doctor or receptionist
in 5 minutes, without changing the backend architecture or unlocking PHI.

---

## Target Buyer / User

**Austrian private clinic** (Wahlarzt / Privatordination):
- Doctor: wants fewer missed calls, less phone chaos
- Receptionist: needs a clear callback queue, not a technical dashboard
- Location: Vienna (Wien), Austria
- Language: German-first

**5-minute demo goal:**
Ali walks into a clinic, opens `/dashboard`, and in 5 minutes a receptionist
understands the product without a single technical word being spoken.

---

## What Changed in /dashboard

The existing `/dashboard` was simplified in-place. No parallel dashboard was created.
All existing backend APIs, data attributes, and contract tests remain intact.

### Before (Module 156 era)
- Heading: "Incoming AI Intake Queue"
- Heading: "Active Resolution Workspace"
- Heading: "Patient Registry"
- UUID visible in workspace header (`selectedAppt.id`)
- UUID visible in patient list row (`patient.id`)
- UUID visible in patient profile (`selectedPatient.id`)
- Raw status codes shown as-is ("new", "callback_needed")
- No tab structure — all columns always visible
- English-only labels

### After (Module 157)
- Visible heading: **"Anfragen"** (sr-only keeps "Incoming AI Intake Queue" for tests)
- Visible heading: **"Anfrage-Details"** (sr-only keeps "Active Resolution Workspace")
- Visible heading: **"Patientenregister"** (sr-only keeps "Patient Registry")
- UUID replaced with **"Anfrage #1"**, **"Anfrage #2"** etc. in clinic-facing UI
- No UUID shown in patient list or patient profile
- Status labels mapped to readable German (see below)
- **3-tab structure**: Anfragen / Patienten / Einstellungen
- German-first labels throughout clinic-facing UI

---

## Today Summary (Heute)

A `Heute` summary bar appears above the tab navigation with 4 count cards:

| Card | Label | Status mapping |
|------|-------|----------------|
| 1 | **Neue Anfragen** | status: new, pending |
| 2 | **Rückruf nötig** | status: callback_needed |
| 3 | **Dringend prüfen** | urgency: urgent, emergency, high |
| 4 | **Erledigt** | status: confirmed, closed |

Counts are derived from the existing appointment request data — no new API calls,
no new backend logic, no AI triage scoring.

---

## Requests / Patients / Settings Tabs

### Anfragen (default)
- Full 3-column workspace (existing layout preserved)
- Incoming AI intake queue on the left (now labelled "Anfragen")
- Anfrage details in the center
- Patient registry on the right
- "Rückruf" button on each request card
- "Als kontaktiert markieren" in the detail workspace

### Patienten
- Simplified patient list — sequential numbering (1, 2, 3…), no UUIDs
- German status labels
- Phone number shown if available
- Friendly empty state

### Einstellungen
- Read-only clinic information placeholder (clinic name, language, environment)
- No technical fields
- Full settings management is planned for Module 159

---

## Readable German Status Labels

A `getGermanStatusLabel()` helper maps raw API status codes to clinic-facing labels:

| Raw status | German label |
|---|---|
| new | Neue Anfrage |
| pending | Neue Anfrage |
| callback_needed | Rückruf nötig |
| contacted | Kontaktiert |
| confirmed | Bestätigt |
| active | Aktiv |
| approved | Genehmigt |
| urgent | Dringend |
| emergency | Notfall |
| closed | Erledigt |
| cancelled | Abgesagt |
| unknown | status (raw) |

---

## Callback Workflow

Two new staff actions are available in the dashboard:

1. **Rückruf** (button on each request card)
   - Calls `updateAppointmentRequestStatus(id, clinicId, 'callback_needed')`
   - Sets appointment request to `callback_needed` status
   - Refreshes the list

2. **Als kontaktiert markieren** (in request detail workspace)
   - Calls `updateAppointmentRequestStatus(id, clinicId, 'contacted')`
   - Sets appointment request to `contacted` status
   - Refreshes the list

Both actions use PATCH `/appointment-requests/{id}/status?clinic_id=` — the same
endpoint already used by `confirmAppointmentRequest`. No new backend routes needed.

---

## Human-Readable Request Numbers

UUIDs are hidden from all clinic-facing UI.

Request display uses list-index-based numbering:
- **"Anfrage #1"** — first request in the list
- **"Anfrage #2"** — second request
- etc.

The UUID remains in:
- API payloads (sent to backend for all PATCH/GET calls)
- React `key` props (internal rendering, not visible)
- Developer Console (technical team tool, untouched)
- Backend logs and audit trail

---

## UUIDs Hidden from Clinic-Facing UI

The following are no longer shown as visible text in `/dashboard`:

- `selectedAppt.id` → replaced with `getReadableRequestNumber(index)`
- `patient.id` → removed from patient list rows
- `selectedPatient.id` → removed from patient profile card

The following remain allowed internally:
- UUID in `key={appt.id}` React props (hidden, functional)
- UUID in API calls via `encodeURIComponent(id)` (hidden, sent to backend)
- UUID in Developer Console (intentionally technical)

---

## What Is Intentionally Paused

The following modules are deprioritized in favour of sales readiness:

- **Module 157 (original)** — Live longitudinal timeline smoke evidence
- **Module 158 (original)** — Patient Story pre-visit narrative
- FHIR / Gulf / Arabic / pediatric-specific modules
- Further anamnesis depth
- New developer-console tools
- Intake form builder UI
- Advanced patient timeline UI
- Vapi credential binding production flow

These remain in the backlog. The foundation is built. They are not deleted.

---

## Trust Story

PraxisMed is built properly underneath:

- Every patient answer is covered by a consent event (Module 151)
- AI never auto-approves anything — every structured proposal requires staff review (Module 154)
- Approved history is separated from unverified proposals at the schema level (Module 156)
- No diagnosis, no medical advice, no triage scoring — anywhere in the system
- No external LLM calls in the structuring pipeline
- `production_phi_enabled = false` enforced at DB, service, route, schema, and frontend level
- No PHI ever stored in staging

The clinic-facing UI is simple. The foundation underneath is sound.

---

## Developer Console Remains Technical

`/developer-console` is unchanged. It remains a technical admin tool:

- Tenant provisioning
- Clinic ID scope injection
- Vapi machine credential binding
- Patient history review queue
- Longitudinal patient timeline (developer view)
- Environment checklist
- Safety guardrails

UUIDs, internal IDs, and technical labels remain visible in the developer console.
It is explicitly not clinic-facing.

---

## Safety Boundaries (Unchanged)

All Module 156-era safety boundaries remain in force:

- No diagnosis. No medical advice. No treatment recommendations. No triage scoring.
- No external LLM calls.
- No auto-approval. No auto-merge.
- `production_phi_enabled = false` throughout.
- No real patient data — synthetic/fake staging only.
- Production PHI remains NO-GO.
- `extraction_confidence` is extraction confidence only — not a medical judgment.

---

## Files Modified

- `frontend/app/dashboard/page.tsx` — simplified, German-first, tabbed, UUID-hidden
- `frontend/lib/api.ts` — added `updateAppointmentRequestStatus`
- `backend/tests/test_doctor_facing_sales_mvp_dashboard_contract.py` — new, ≥45 tests
- `docs/product/DOCTOR_FACING_SALES_MVP_SIMPLIFICATION.md` — this file

---

## Acceptance Statement

> "Ali can walk into a Vienna clinic and in 5 minutes a receptionist understands
> the product without a single technical word being spoken."

The `/dashboard` is now that product.

---

## What Remains

- **Module 158** — One-click demo flow (synthetic data, demo reset button)
- Module 159 — Clinic settings editor (language, doctor name, specialty)
- Module 160 — AI receptionist value story (call capture demo with synthetic Vapi call)
- Arabic/RTL foundation
- Gulf readiness architecture review
- Production readiness / security / legal gates
