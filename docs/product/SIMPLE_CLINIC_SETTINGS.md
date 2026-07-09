# Simple Clinic Settings

**Sprint 21 / Module 159**
**Date:** 2026-07-09
**Status:** Complete

---

## Purpose

After Module 158 made the demo instant with one-click synthetic data, the next
sales readiness step is personalization. The clinic must feel like *our practice*,
not a generic demo.

A receptionist opens **Einstellungen** and adjusts the clinic name, doctor name,
specialty, and AI receptionist tone — without seeing a single technical word.

---

## Why Simple Clinic Settings Matter for Sales

When Ali walks into a Vienna clinic and opens `/dashboard`, the demo uses a
generic staging name. Within 30 seconds, the receptionist asks: "Can we put our
name here?" If the answer is no (or requires a developer), the demo loses momentum.

Module 159 makes personalization instant and obvious.

---

## What Was Added

### Einstellungen Tab — Now Editable

The previously read-only settings placeholder is replaced with a full editable
settings form, divided into four plain-language sections:

### 1. Praxisprofil

| Field | Placeholder |
|---|---|
| Praxisname | Dr. Huber Praxis |
| Arzt / Ärztin | Dr. Med. Alexander Huber |
| Fachrichtung | Innere Medizin |
| Ort | Wien |
| Telefonnummer | +43 1 000 0000 |

### 2. Öffnungszeiten

Free-text field. Example: `Mo–Fr 08:00–17:00`

### 3. Sprachen

Checkboxes:
- Deutsch (default: checked)
- Englisch (default: checked)
- Arabisch — shown as "demnächst verfügbar" (preview/future, disabled)

Language selection is persisted via the existing
`PATCH /clinics/{clinic_id}/language-settings` endpoint. No new migration.

### 4. KI-Rezeption

Tone selector (radio buttons):

| Option | Description |
|---|---|
| Freundlich und ruhig | Warm, calm, welcoming |
| Kurz und direkt | Short and efficient |
| Sehr formell | Formal Austrian register |

**KI-Vorschau** (live preview card):

> "Guten Tag, hier ist die digitale Rezeption der Dr. Huber Praxis. Ich nehme
> gerne Ihre Terminanfrage auf — das Praxisteam meldet sich zur Bestätigung zurück."

The preview:
- Changes live when tone or clinic name changes
- Always says "Praxisteam meldet sich" — no appointment auto-confirmation
- Never mentions Vapi, API, webhook, FHIR, UUID
- Never promises medical advice or clinical decision

### Save Controls

- **Speichern** — saves language settings to backend, updates display name in header
- **Änderungen zurücksetzen** — resets form to current defaults

Success copy: **"Einstellungen gespeichert."**
Error copy: **"Einstellungen konnten nicht gespeichert werden."**

---

## No Technical Fields

The following are intentionally absent from the Einstellungen tab:

- No clinic_id or UUID
- No tenant_id
- No Vapi configuration
- No webhook URL
- No API keys or references
- No FHIR
- No JSON
- No token or secret
- No DATABASE_URL
- No JWT
- No proposal_id, template_id, patient_id

The Developer Console (`/developer-console`) remains the appropriate place for
all technical configuration. The clinic-facing dashboard is plain-language only.

---

## No Appointment Auto-Confirmation

The KI-Vorschau text is carefully worded:
- "das Praxisteam meldet sich zur Bestätigung zurück"
- "Kein automatischer Terminabschluss"

The AI receptionist never confirms appointments. That remains a staff decision.

---

## No Diagnosis / Advice / Triage

The settings UI contains no clinical decision logic:
- No diagnosis generation
- No medical advice
- No treatment recommendations
- No triage scoring

---

## Safety Boundaries (Unchanged)

All Module 157/158 safety boundaries remain in force:

- No real patient data
- No PHI
- `production_phi_enabled = False` throughout
- No live Vapi call
- No browser storage (no localStorage, no sessionStorage)
- Production PHI remains NO-GO

---

## Files Modified

- `frontend/app/dashboard/page.tsx` — Einstellungen tab replaced with editable form
- `backend/tests/test_simple_clinic_settings_sales_mvp_contract.py` — new, ≥15 tests
- `docs/product/SIMPLE_CLINIC_SETTINGS.md` — this file

---

## Acceptance Statement

> "Eine Rezeptionistin kann Einstellungen öffnen und die Demo anpassen,
> ohne ein einziges technisches Wort zu kennen."
>
> (A receptionist can open Einstellungen and understand/customize the demo
> without any technical word being spoken or shown.)

The `/dashboard` Einstellungen tab is now that product.
