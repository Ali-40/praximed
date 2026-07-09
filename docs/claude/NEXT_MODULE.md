# Sprint 21 / Module 164 — First Pilot Clinic Activation Checklist

Status: pending.

## Context

Module 163 complete (Clinic Outreach Execution Pack):
- Cold email, WhatsApp/SMS, LinkedIn, walk-in cold approach scripts
- 3-touch follow-up sequence (Day 1, Day 3, Day 7)
- Objection-specific quick replies for 5 common first-contact objections
- 45 contract tests. 5455 total. Frontend build clean. Production PHI remains NO-GO.

## Sprint 21 Sales-MVP Pivot — Paused until further notice

The following tracks remain paused:
- Arabic/RTL foundation
- Gulf/FHIR/pediatric expansion
- Smoke evidence docs
- Patient Story narrative
- Additional developer-console tooling
- Deeper anamnesis modules

## Goal

Create a structured onboarding checklist for the first actual paying pilot clinic —
everything Ali needs to do when a clinic says "yes" to the 30-day pilot.

This module bridges the gap between "demo accepted" and "pilot live."

## What Module 164 must produce

### 1. First Pilot Clinic Activation Checklist

A structured Markdown doc: `docs/sales/FIRST_PILOT_CLINIC_ACTIVATION_CHECKLIST.md`

Structure:
- Pre-activation (before Day 1): what Ali does before the clinic starts
- Day 1 — Onboarding: what happens on the first day
- Day 7 — First check-in: review with clinic staff
- Day 30 — Pilot review: decision point (continue / adjust / end)
- What Ali sets up vs. what the clinic does
- When to escalate (staff confusion, tech issue, no calls coming in)
- No PHI. No automation beyond demo flow. Staff confirms everything.

### 2. Staff Welcome Message Template (German)

Short welcome message Ali sends to the clinic staff on Day 1.

Structure:
- Under 8 sentences
- Explains what PraxisMed does in plain German
- What staff sees in the dashboard
- Who to contact if something is unclear
- No technical language

### 3. First-Week Support Guide

A short guide for Ali: how to support the first pilot clinic in week 1.

Structure:
- Daily check-in rhythm (how often to follow up)
- What to look for (calls coming in, staff using dashboard)
- What to do if no calls appear after Day 3
- How to handle a staff question about a patient call
- When to involve the doctor vs. reception staff

### 4. Demo-to-Live Transition Guide

What changes when AVV is signed and the clinic moves from demo to live.

Structure:
- Demo vs. live differences (staging phone vs. real phone)
- What Ali sets up on Day 1 of live mode
- Staff briefing template (what to tell the team)
- Data boundary reminder: no real patient data during demo phase

### 5. Tests

`backend/tests/test_first_pilot_clinic_activation_checklist_contract.py` (new — ≥15 tests)

Static evidence tests:
- Activation checklist file exists
- Checklist has Day 1 section
- Checklist has Day 7 section
- Checklist has Day 30 section
- Checklist mentions staff confirmation requirement
- Staff welcome message template exists in doc
- First-week support guide exists in doc
- Demo-to-live transition guide exists in doc
- No compliance certification claims
- No technical language (no API names, protocol names)
- No PHI claims
- No clinical or medical claims
- No automatic appointment confirmation promise
- Pilot offer is time-bounded (30 days)
- Safety boundaries section exists

### 6. Docs updates

- docs/claude/CURRENT_STATE.md — Module 164 entry
- docs/claude/NEXT_MODULE.md — updated to Module 165

## Module 165 preview

Sprint 21 / Module 165 — Pilot Metrics and Feedback Collection

Module 165 should:
- Create a simple feedback template Ali uses after 7 days with the pilot clinic
- Define 3–5 metrics to track during the pilot (calls answered, callbacks completed, staff satisfaction)
- Post-pilot summary template (what worked, what to improve)
- Simple one-page pilot report Ali can share with the clinic after 30 days
- No PHI. No automated data collection. Staff fills in manually.

## Constraints

- No real patient data
- No production PHI
- No new backend endpoints
- No new migrations
- No new developer-console tooling
- No Arabic/RTL, no FHIR, no Gulf expansion
- No compliance overclaims in any copy
- No technical language in clinic-facing or outreach copy
- production_phi_enabled always False
- Frontend build must remain clean
- Full test suite must remain green
- Commit message:
  Sprint 21 / Module 164 — First pilot clinic activation checklist
