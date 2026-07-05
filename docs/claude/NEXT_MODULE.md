# Sprint 18 / Module 127 — Clinic Outreach Asset and 30-Day Pilot Offer Pack

Status: pending implementation.

## Context

Module 126B complete:
- Fabel 5 premium dashboard deployed and smoke-confirmed PASS on Vercel
- Dashboard shows premium header, staging demo badge, metric cards, appointment rows,
  View summary, notifications, and footer safety text
- All staging checks 1–17 confirmed PASS (Modules 112–126B)
- Full backend tests: 2828/2828 passed
- Commercial MVP + clinic outreach acceleration mode: ACTIVE
- Production PHI readiness: NO-GO

## Goal

Create practical, actionable outreach assets so the team can begin approaching
private clinics with a clear, honest, compelling offer. This module produces
text-based assets — no code changes, no backend changes, no new migrations.

The dashboard demo is ready. The outreach pack gives the team the words to use it.

## Scope

Docs only. No runtime code changes. No backend changes. No migrations. No secrets.
No real patient data. No production PHI. Do not mark production ready.

## What Module 127 must do

1. **30-day pilot offer document** — a one-page written offer for a free 30-day
   pilot with a private clinic. Must be honest: fake-data staging only, no real
   patient data until production hardening is complete, production PHI NO-GO.

2. **Demo script** — step-by-step walkthrough of the staging dashboard for a
   doctor/clinic manager demo call. Covers: login, dashboard overview, metric cards,
   appointment row, View summary, notification, safety boundaries.

3. **Clinic target list schema** — a simple schema/template for tracking outreach
   targets: clinic name, specialty, location, contact, outreach stage, notes.
   No real clinic data yet — just the schema.

4. **Email/phone/LinkedIn outreach scripts** — short, specific, honest message
   templates for each channel. Safe claims only (no real patient data claims, no
   production readiness claims).

5. **Objection handling guide** — top 5 objections from private clinic doctors
   ("Is it secure?", "Do you have other clients?", "What happens to patient data?",
   "Is it compliant?", "What does it cost?") with honest, non-misleading responses.

## Safe claims only

- May claim: functional demo, real AI voice intake, real-time appointment capture,
  doctor/staff review workflow, pre-appointment summary, staging demo available
- Must not claim: GDPR/HIPAA compliance (hardening incomplete), real patient data
  handling, production-ready, secure enough for live patient data now
- Must not mention: any real clinic name, any real patient, any revenue figures

## Allowed changes

- `docs/outreach/PILOT_OFFER.md` (new)
- `docs/outreach/DEMO_SCRIPT.md` (new)
- `docs/outreach/CLINIC_TARGET_LIST_SCHEMA.md` (new)
- `docs/outreach/OUTREACH_SCRIPTS.md` (new)
- `docs/outreach/OBJECTION_HANDLING.md` (new)
- `docs/claude/CURRENT_STATE.md` (updated)
- `docs/claude/NEXT_MODULE.md` (updated)

No tests required for this module (doc-only, no runtime code).

## Acceptance

- All 5 outreach asset docs created and honest
- Safe claims only — no false production readiness claims
- No real patient data in any doc
- No secrets in any doc
- Commit: `Sprint 18 / Module 127 — Clinic outreach asset and 30-day pilot offer pack`

---

## Upcoming (commercial MVP build track, post-Module 127)

- **Module 128** — Consultation summary draft generator
- **Module 129** — Patient timeline
- **Module 130** — Follow-up and reminder workflow

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)
