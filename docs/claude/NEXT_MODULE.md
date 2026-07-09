# Sprint 21 / Module 163 — Clinic Outreach Execution Pack

Status: pending.

## Context

Module 162 complete (Sales Demo Polish and Walk-In Readiness):
- Intro sentence added: "PraxisMed nimmt Terminanfragen auf und sortiert Rückrufe für Ihr Praxisteam."
- "Demo in 3 Schritten" helper card added to center panel
- All visible English strings replaced with German (sr-only preserves for contract tests)
- Technical terms hidden: no Vapi, no webhook, no source_ref, no UUID visible
- 52 new contract tests. 5410 total. Frontend build clean. Production PHI remains NO-GO.

## Sprint 21 Sales-MVP Pivot — Paused until further notice

The following tracks remain paused:
- Arabic/RTL foundation
- Gulf/FHIR/pediatric expansion
- Smoke evidence docs
- Patient Story narrative
- Additional developer-console tooling
- Deeper anamnesis modules

## Goal

Produce exact outreach scripts that Ali can use to contact Vienna private clinics and book
a pilot walkthrough — email, WhatsApp, LinkedIn, walk-in cold approach.

The product is now demos-ready. The next conversion step is getting in the room.

## What Module 163 must produce

### 1. Cold Email Script

Short, direct email to a Vienna Wahlarzt or clinic manager.

Structure:
- Subject line: one clear value sentence
- Opening: one-line missed calls hook
- Value: 3 bullet points max (what PraxisMed does)
- CTA: "30-Minuten-Demo diese Woche?"
- No technical language
- No compliance claims
- No diagnosis/advice/triage

### 2. WhatsApp / SMS Script

Short follow-up message after cold email or cold call.

Structure:
- Under 5 sentences
- Direct value hook
- Simple yes/no CTA
- No technical language

### 3. LinkedIn Outreach Script

Connection request + follow-up message sequence for Vienna Wahlarzt community.

Structure:
- Connection request: 1 sentence
- Follow-up after connection: 3–4 sentences max
- CTA: "Demo?" or "5 Minuten diese Woche?"

### 4. Walk-In Cold Approach Script

For Ali to walk into a clinic without an appointment.

Structure:
- What to say to the receptionist first
- What to say to the doctor/manager if available
- Leave-behind: one-page handout
- Follow-up step: "Darf ich Ihnen einen Demo-Termin schicken?"

### 5. Follow-Up Sequence

3-touch follow-up sequence (Day 1, Day 3, Day 7):
- Day 1: Initial contact (email or WhatsApp)
- Day 3: Light follow-up with social proof hook
- Day 7: Final gentle nudge with pilot offer

### 6. Objection-Specific Quick Replies

Short replies for 5 common first-contact objections:
- "Kein Interesse"
- "Zu teuer"
- "Wir haben bereits eine Lösung"
- "Keine Zeit"
- "Schicken Sie uns eine E-Mail"

### 7. Tests

`backend/tests/test_clinic_outreach_execution_pack_contract.py` (new — ≥15 tests)

Static evidence tests:
- Cold email script exists
- WhatsApp script exists
- LinkedIn script exists
- Walk-in script exists
- Follow-up sequence exists
- All scripts mention missed calls / verpasste Anrufe
- All scripts mention 30-day pilot
- All scripts contain pilot CTA
- No compliance claims (no "DSGVO-zertifiziert", no "fully compliant")
- No technical language (no "API", no "webhook", no "UUID", no "FHIR")
- No diagnosis/medical advice claims
- No production readiness claims
- Safety wording: no real patient data
- No real names in scripts (generic placeholders only)

### 8. Docs updates

- docs/claude/CURRENT_STATE.md — Module 163 entry
- docs/claude/NEXT_MODULE.md — updated to Module 164

## Module 164 preview

Sprint 21 / Module 164 — First Pilot Clinic Activation Checklist

Module 164 should:
- Create a structured onboarding checklist for the first actual paying pilot clinic
- Staff welcome message template (German)
- First-week support guide
- How to handle transition from demo to live (when AVV is signed)
- What to set up on day 1 vs. day 7 vs. day 30
- No PHI. No automation beyond demo flow. Staff confirms everything.

## Constraints

- No real patient data
- No production PHI
- No new backend endpoints
- No new migrations
- No new developer-console tooling
- No Arabic/RTL, no FHIR, no Gulf expansion
- No compliance overclaims in outreach copy
- No technical language in clinic-facing or outreach copy
- production_phi_enabled always False
- Frontend build must remain clean
- Full test suite must remain green
- Commit message:
  Sprint 21 / Module 163 — Clinic outreach execution pack
