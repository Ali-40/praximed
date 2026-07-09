# Clinic-Facing Dashboard Language Hotfix

**Sprint 21 / Module 162B**
**Date:** 2026-07-09
**Status:** Complete

---

## Why This Hotfix Was Needed

After Module 162 was deployed and the live /dashboard screenshot was reviewed, it was clear
that the clinic-facing UI still contained English labels and technical wording that would
confuse a Vienna receptionist seeing the product for the first time.

Specific issues visible in the screenshot:
- "Practice Medicine" / "ClinicDoctor" appearing from dynamic data display
- "Inquiries", "Inquiry details" visible in some states
- "AUDIO TRANSCRIPT & CALL RECORDING" visible (now sr-only, but needed reinforcing)
- "vapi" badge appearing visibly on request cards from phone-sourced requests
- "ingestion" appearing in tooltip/title attributes
- Archived demo requests appearing in the active list with a "Neue Anfrage" badge
- Summary panel still used English labels: "Type", "Reason", "Urgency", "Prior visits",
  "Suggested action"
- English safety text: "AI intake output is administrative scheduling information only.
  Staff or doctor review is required before any clinical decision."
- The "Rückruf" button had no clarifying label ("Rückruf markieren")
- "Wunschtermin" was used but spec requires "Gewünschte Zeit"
- No dedicated "Anfrage im Überblick" heading in the center panel
- No "Noch keine aktiven Anfragen" state after demo reset

A receptionist shown this dashboard would need explanation for every term. That breaks the
sales-demo promise: understand the product in 5 minutes, no technical explanation needed.

---

## What Was Fixed

### Dashboard German-First Fixes

| Before | After |
|---|---|
| Center panel heading "Anfrage-Details" | "Anfrage im Überblick" |
| Field "Wunschtermin" | "Gewünschte Zeit" |
| Button "Rückruf" | "Rückruf markieren" |
| Summary "Type" | "Art" |
| Summary "Reason" | "Anliegen" |
| Summary "Urgency" | "Dringlichkeit" |
| Summary "Prior visits" | "Frühere Besuche" |
| Summary "Suggested action" | "Empfohlene Aktion" |
| English safety blurb | German: "Nur zur internen Planung. Das Praxisteam prüft und bestätigt jeden Schritt." |

### Technical Terms Removed / Fixed

| Issue | Fix |
|---|---|
| Visible "vapi" badge on request cards | Removed — source metadata hidden from clinic view |
| "ingestion" in button title attribute | Changed to German: "Wiedergabe nicht verfügbar — keine Audio-Integration aktiv" |
| `isNewRequest` returning true for all non-confirmed | Fixed: only 'new' and 'pending' statuses show "Neue Anfrage" badge |

### Archived Request Handling

The `getGermanStatusLabel` function now maps:
- `'archived'` → `'Archiviert'`
- `'rejected'` → `'Abgelehnt'`

The request list now separates:
- **Active requests** (non-archived): shown in main list
- **Archived requests**: shown in a collapsed section below labeled "Archivierte Anfragen (N)"

After `Demo zurücksetzen`, the active list shows:
> "Noch keine aktiven Anfragen. Erstellen Sie einen Demo-Anruf, um den Ablauf zu zeigen."

No archived request shows a "Neue Anfrage" badge.

---

## What Was NOT Changed

- No backend migration
- No new routes
- No calendar
- No PHI
- Production PHI remains NO-GO
- All sr-only strings preserved for existing contract test compatibility
- "Audio Transcript & Call Recording" in sr-only — required by Module 126C tests — preserved
- "Recording ingestion pending" in sr-only — required by existing tests — preserved

---

## Acceptance

A Vienna receptionist can open `/dashboard` and understand:

1. Requests come in from phone calls → "Anfragen" tab with patient name, reason, time
2. Who needs a callback → "Rückruf nötig" status
3. How to act → "Rückruf markieren" and "Als kontaktiert markieren"
4. What the demo shows → "Demo in 3 Schritten" card
5. The active list is clean after reset → "Noch keine aktiven Anfragen"
6. Archived requests are clearly separate → "Archivierte Anfragen (N)" section
7. No technical term appears in the main visible workflow

No Vapi badge. No "ingestion". No English labels in the active workflow. No archived items
masquerading as new requests.

---

## Files Modified

- `frontend/app/dashboard/page.tsx` — all language fixes described above
- `backend/tests/test_clinic_facing_dashboard_language_hotfix_contract.py` — 60 contract tests
- `docs/product/CLINIC_FACING_DASHBOARD_LANGUAGE_HOTFIX.md` — this file
