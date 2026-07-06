# Sprint 18 / Module 127 — Clinic Outreach Asset & 30-Day Pilot Offer Pack

Status: pending implementation.

## Context

Module 126D complete:
- Fabel 5 premium 3-panel clinical interface deployed smoke evidence documented
- /dashboard: Incoming AI Intake Queue / Active Resolution Workspace / Patient Registry
- Dynamic doctor/clinic banner: "Dr. Med. Alexander Huber | Innere Medizin Wien" via tenantDisplay
- Audio Transcript & Call Recording placeholder with Vapi ingestion message
- /onboarding: 5-step pilot wizard, Review & Pilot Activation (plain text, no HTML entity leak)
- /developer-console: dark admin command theme, isolated from clinical UI, directly accessible
- All safety boundaries enforced: STAGING DEMO / fake data / no real patient data / Production PHI: NO-GO
- 3107/3107 backend tests pass

## Staging Demo Asset State

The premium Fabel 5 dashboard is live and demo-ready on Vercel staging.
It demonstrates:
- Professional 3-panel clinical workspace with deep navy / teal palette
- AI intake queue workflow with patient card, summary, and confirm flow
- Dynamic tenant identity banner (doctor name / specialty / clinic)
- Safety boundaries clearly visible — no real patient data risk during demos
- No login credentials or real patient data needed to understand the product value

## Production Hardening Track (Parallel — C3–C8)

All production hardening blockers remain open. No production PHI launch until resolved:
- C3 — Secrets hardening
- C4 — PHI logging/redaction hardening
- C5 — Tenant isolation verification
- C6 — Audit trail hardening
- C7 — Backup/restore runbook
- C8 — Legal / DSGVO review

## Goal

Build a clinic outreach asset pack for Austrian private clinic pilot outreach.

## What Module 127 must deliver

1. Outreach one-pager template (Austrian private clinic audience, German/English)
2. 30-day pilot offer framing (scope, terms, what the clinic gets)
3. First 50 Vienna clinic targets shortlist (specialty, contact entry points)
4. Demo script: how to show the staging dashboard in a 5-minute clinic walkthrough
5. Pitch safety framing: staging only / fake data / production PHI: NO-GO communicated to prospects

## Constraints

- No real patient data
- No production PHI claim
- No secrets
- Outreach materials must be honest about staging/pilot status
- No production readiness claim before C3–C8 resolved
