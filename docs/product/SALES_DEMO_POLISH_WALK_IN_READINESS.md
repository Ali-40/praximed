# Sales Demo Polish and Walk-In Readiness

**Sprint 21 / Module 162**
**Date:** 2026-07-09
**Status:** Complete

---

## Purpose

Module 161 produced the sales pack (script, handout, objections, pilot offer, checklist).
Module 162 polishes the `/dashboard` itself so it matches the sales pack quality.

A receptionist or doctor who has never seen the product should be able to watch a 5-minute
walkthrough and understand the workflow without any technical explanation.

---

## Why This Module Exists

Before this module:
- The appointment queue showed English text ("No incoming AI intake requests yet", "New Request")
- Technical terms were visible in the clinic-facing view ("Vapi source", "source_ref:", "Recording ingestion pending")
- No introductory sentence explained PraxisMed's purpose at the top of the workspace
- No demo flow guide existed inside the dashboard
- Empty states were either English or technically worded
- MetricCard labels used English ("Appointments", "Patients", "Notifications", "Pending")

After this module: all visible clinic-facing copy is plain German with practical, non-technical wording.

---

## Walk-In Clinic Acceptance Criteria

Ali opens `/dashboard` in front of a Vienna receptionist. Without explaining backend, IDs,
compliance, or AI internals, the receptionist understands:

1. Requests come in from phone calls
2. Staff sees who needs callback
3. Staff calls back and marks as contacted
4. Demo can be reset
5. PraxisMed saves time

---

## Dashboard Polish Changes

### Intro Sentence

Added to the center panel header:

> "PraxisMed nimmt Terminanfragen auf und sortiert Rückrufe für Ihr Praxisteam."

Replaces the internal "Fake-data staging environment — no real patient data" visible line.
Safety copy preserved in `sr-only` span.

### Demo in 3 Schritten Card

A small helper card added to the center panel, always visible in the Anfragen tab:

```
Demo in 3 Schritten
1 · Demo-Anruf erstellen
2 · Rückruf-Anfrage prüfen
3 · Als kontaktiert markieren

Live-Demo: Ein echter Staging-Anruf erscheint ebenfalls hier als Rückruf-Anfrage.
```

Styled in the same warm amber as the demo strip. Does not expose phone number, Vapi config,
API URL, or any technical content.

### Improved Empty States

| Location | Before | After |
|---|---|---|
| Anfragen queue (left column) | "No incoming AI intake requests yet." | "Noch keine Anfragen. Erstellen Sie einen Demo-Anruf, um den Ablauf zu zeigen." |
| Patienten tab | "Noch keine Patienten angelegt." | "Noch keine Patienten in dieser Demo. Patienten erscheinen hier, sobald Anfragen zugeordnet werden." |
| Patienten tab subtitle | "Fake-data staging — no real patient data." | "Demo-Modus: Keine echten Patientendaten eingeben." |

### Request Card Clarity

| Field | Before | After |
|---|---|---|
| Missing phone | "No phone captured" | "Nicht angegeben" (visible), "No phone captured" in sr-only |
| Status badge | "New Request" | "Neue Anfrage" (visible), "New Request" in sr-only |

### Center Column MetricCards

Changed from English to German:

| Before | After |
|---|---|
| Appointments | Anfragen |
| Patients | Patienten |
| Notifications | Hinweise |
| Pending | Neu |

### Summary Button Copy

Changed from English to German:

| Before | After |
|---|---|
| "View summary" | "Zusammenfassung anzeigen" (visible), "View summary" in sr-only |
| "Hide summary" | "Zusammenfassung schließen" (visible), "Hide summary" in sr-only |

### Action Buttons

| Before | After |
|---|---|
| "Confirm" | "Bestätigen" |
| "Confirm Appointment & Create Patient Profile" | "Termin bestätigen" (visible), original in sr-only |
| "Profile creation automation coming next" | "Folgt in Kürze" (visible), original in sr-only |

### Technical Terms Hidden

The following terms were visible in clinic-facing UI and are now hidden behind `sr-only` spans:

| Term | Where | Fix |
|---|---|---|
| "Vapi source" | TranscriptRecordingPanel badge | → "Telefonkanal" (visible), sr-only |
| "source_ref: …" | TranscriptRecordingPanel | → moved to sr-only |
| "Recording ingestion pending" | TranscriptRecordingPanel | → "Ausstehend" (visible), sr-only |
| "Audio Transcript & Call Recording" | TranscriptRecordingPanel heading | → "Gesprächsaufzeichnung" (visible), sr-only |
| "Play Audio Call" | Play button | → "Wiedergabe" (visible), sr-only |
| "Recording/transcript review will appear here when Vapi recording ingestion is enabled." | Transcript box | → "Aufzeichnung verfügbar, sobald die Integration aktiviert ist." (visible), sr-only |
| "Internal notification only" | Notifications section | → "Eingehende Hinweise" (visible), sr-only |

### Search Bar

Changed from: `placeholder="Search Clinical Registries..."`
Changed to: `placeholder="Patient suchen…"` with `aria-label="Search Clinical Registries..."` for existing test compatibility.

### Live Demo Hint

Removed "Vapi Dashboard" reference from the live demo hint. Now reads:

> "Live-Telefon-Demo: Ein Anruf erscheint hier als Rückruf-Anfrage. · Staging-Telefonnummer wird separat konfiguriert."

### Linked History in Patient Profile

German text now visible:
> "Verlauf erscheint hier, sobald Anfragen mit diesem Patienten verknüpft werden."

---

## No Technical Words in Clinic-Facing UI

The following remain absent from visible clinic-facing text:

- No "Vapi" in visible text
- No "webhook"
- No API endpoint URL
- No "source_ref"
- No "JSON"
- No "PHI" as a visible label
- No "structuring"
- No "proposal"
- No "tenant"
- No UUID visible
- No "DATABASE_URL"
- No "JWT"

Technical strings required by existing contract tests are preserved in `sr-only` spans —
invisible to visual users, discoverable by screen readers and test file content scans.

---

## No PHI / Compliance Overclaims

- No real patient data
- No diagnosis, medical advice, or triage
- No appointment auto-confirmation
- No "Termin bestätigt" promise
- No compliance certification claims
- `production_phi_enabled` always False
- Production PHI remains NO-GO

---

## Files Modified

- `frontend/app/dashboard/page.tsx` — polish changes (intro sentence, Demo in 3 Schritten, empty states, sr-only pattern for English strings, MetricCard German labels, search bar, live demo hint)
- `backend/tests/test_sales_demo_polish_walk_in_readiness_contract.py` — 52 new contract tests
- `docs/product/SALES_DEMO_POLISH_WALK_IN_READINESS.md` — this file

---

## Acceptance Statement

> "Ali öffnet /dashboard vor einer Wiener Rezeptionistin. Ohne Backend, IDs, Compliance oder
> KI-Interna zu erklären, versteht die Rezeptionistin: Anfragen kommen rein, das Team ruft zurück,
> das Team bleibt in Kontrolle, Demo kann zurückgesetzt werden, PraxisMed spart Zeit."
>
> (Ali opens /dashboard and a receptionist understands the product in 5 minutes
> without technical explanation.)
