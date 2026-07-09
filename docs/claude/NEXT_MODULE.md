# Sprint 21 / Module 161 — Five-Minute Clinic Demo Script and Sales Pack

Status: pending.

## Context

Module 160 complete (Live Vapi Staging Call Loop — commit 5cb8671):
- data-live-demo-hint added to dashboard demo strip
- Existing POST /vapi/tools/capture-appointment-request verified — no backend changes needed
- German AI receptionist script documented
- 52 new contract tests. 5287 total. Frontend build clean. Production PHI remains NO-GO.

## Sprint 21 Sales-MVP Pivot — Paused until further notice

The following tracks are paused and must NOT be included in upcoming modules:
- Arabic/RTL foundation
- Gulf/FHIR/pediatric expansion
- Smoke evidence docs
- Patient Story narrative
- Additional developer-console tooling
- Deeper anamnesis modules

The sole focus of Sprint 21 remaining modules is closing a Vienna pilot sale.

## Goal

Produce a practical sales pack that Ali can use in a Vienna clinic visit today:
a 5-minute demo script, receptionist talk track, doctor talk track, 30-day pilot offer,
simple pricing anchor, and objection handling — all in plain German, no technical language.

## What Module 161 must produce

### 1. Five-Minute Demo Script

A structured, time-boxed walkthrough of /dashboard for a receptionist + doctor audience.

Sections:
- **00:00 – 00:30** — Opening hook (missed calls problem)
- **00:30 – 02:00** — Live Anfragen queue walkthrough
- **02:00 – 03:00** — Live phone demo moment
- **03:00 – 04:00** — Einstellungen personalization
- **04:00 – 05:00** — Pilot offer close

Each section: what to say, what to show, what to listen for.

### 2. Receptionist Talk Track

Focus: staff time, missed calls, no new software to learn, simple callback workflow.

Key messages:
- "Das System nimmt Anrufe entgegen, wenn Sie beschäftigt sind."
- "Sie sehen alle Anfragen auf einem Blick und rufen zurück, wenn Sie Zeit haben."
- "Kein Termin wird automatisch bestätigt — Sie haben immer die Kontrolle."

### 3. Doctor Talk Track

Focus: fewer interruptions, no missed new patients, simple overview, pilot framing.

Key messages:
- "Neue Patienten gehen nicht verloren, auch wenn das Telefon nicht abgenommen wird."
- "Sie sehen den Überblick — Ihr Team kümmert sich um die Details."
- "Wir testen das 30 Tage — ohne Risiko."

### 4. Live Phone Demo Moment (script)

Script for the moment Ali calls the staging number in the room:

> "Ich rufe jetzt die Staging-Nummer an. Das KI-System antwortet auf Deutsch,
> nimmt die Terminanfrage auf — und in wenigen Sekunden sehen Sie die Anfrage
> hier in der Warteschlange als 'Rückruf nötig'."

After call appears:
> "Das war ein echter Anruf. Keine echten Patientendaten — das ist unser
> Demo-System. Aber genau so funktioniert es im echten Betrieb."

### 5. 30-Day Pilot Offer

Simple, low-commitment framing:

- 30-Tage-Pilotprogramm
- Setup in einem Nachmittag
- Kein Vertrag, keine Mindestlaufzeit für den Pilot
- Wir konfigurieren alles — die Praxis tut nichts Technisches

### 6. Simple Pricing Anchor

One clear line. No tiers, no feature matrix. One number that sounds reasonable
relative to one missed new patient per month.

### 7. Objection Handling

Common objections with short, honest responses:

| Einwand | Antwort |
|---|---|
| "Was ist mit Datenschutz?" | Demo-Modus: keine echten Patientendaten. Pilotdaten bleiben in Österreich. |
| "Macht das KI Diagnosen?" | Nein. Das System nimmt nur Terminanfragen auf. Ihr Team entscheidet alles. |
| "Wir haben schon ein Telefonsystem." | Ergänzung, kein Ersatz. Anrufe außerhalb der Öffnungszeiten fallen nicht mehr weg. |
| "Zu teuer." | Wie viele neue Patienten verlieren Sie pro Monat durch verpasste Anrufe? |
| "Wir sind noch nicht bereit." | Pilot: 30 Tage, kein Risiko. Wir richten alles ein. |

### 8. Safety wording (required in script)

Every copy of the demo script must include:

- "Demo/Staging only — keine echten Patientendaten"
- "Kein automatischer Terminabschluss — das Praxisteam bestätigt jeden Termin"
- "Keine Diagnose, keine medizinische Beratung"
- "Das Personal bestätigt jeden Termin vor der Buchung"

### 9. Tests

`backend/tests/test_five_minute_demo_script_sales_pack_contract.py` (new — ≥15 tests)

Static evidence tests:
- Sales pack doc exists
- Doc mentions receptionist talk track
- Doc mentions doctor talk track
- Doc mentions 30-day pilot
- Doc mentions live phone demo moment
- Doc mentions "Rückruf nötig"
- Doc includes staging safety wording ("keine echten Patientendaten")
- Doc states no automatic appointment confirmation
- Doc states no diagnosis
- Doc states no medical advice
- Doc does not make compliance overclaims (no "DSGVO-zertifiziert", no "HIPAA")
- Doc does not make production readiness claims
- Doc does not mention UUID, API, webhook, DATABASE_URL, JWT
- Objection handling section present
- Pricing anchor section present

### 10. Docs updates

- docs/claude/CURRENT_STATE.md — Module 161 entry
- docs/claude/NEXT_MODULE.md — updated to Module 162

## Module 162 preview

Sprint 21 / Module 162 — Demo Polish: Instant Visual Impact

Module 162 should:
- Ensure /dashboard opens to an already-populated demo queue (one demo call visible by default)
- "Heute" summary bar shows non-zero numbers on first load
- No empty-state placeholder on the sales demo day
- No new patient data. No PHI. Staging only.

## Constraints

- No real patient data
- No production PHI
- No appointment auto-confirmation
- No diagnosis/advice/triage
- No compliance overclaims
- No production readiness claims
- No technical language in sales copy
- No Arabic/RTL, no FHIR, no Gulf expansion
- production_phi_enabled always False
- Frontend build must remain clean
- Full test suite must remain green
- Commit message:
  Sprint 21 / Module 161 — Five-minute clinic demo script and sales pack
