# Sprint 18 / Module 128 — Clinic Outreach List Builder and First 50 Targets

Status: pending implementation.

## Context

Module 127 complete:
- Full outreach and 30-day pilot offer pack created (`docs/business/CLINIC_OUTREACH_30_DAY_PILOT_PACK.md`)
- English + German email scripts, phone script, WhatsApp/LinkedIn message, demo script
- 30-day pilot: free, no setup fee, €299–€499/month after pilot
- 50-clinic outreach list schema defined
- Objection handling guide ready
- Immediate outreach can begin
- Production PHI readiness: NO-GO
- Full backend tests: 2853/2853 passed

## Goal

Build a structured first-50 clinic outreach list as a practical working document.
The list is a tracking tool for real clinic contacts — not scraped, not automated,
built manually from public sources.

## Scope

Docs only. No runtime code changes. No scraping automation. No secrets.
No real patient data. No production PHI. Do not mark production ready.

## What Module 128 must do

1. **First 50 clinic outreach list** — a table (or CSV-format doc) with the first
   50 private clinic targets in Austria (AT), Germany (DE), or Switzerland (CH),
   populated from public sources (clinic websites, Google Maps listings, medical
   directories). Fields per the schema in Module 127 Section 7.

2. **Priority scoring** — score each clinic 1–5 on fit (specialty match, city size,
   likely call volume).

3. **Outreach status tracking** — starting status: `not_started` for all 50.

4. **Week 1 shortlist** — mark the top 10 highest-fit clinics for Week 1 outreach.

## Constraints

- Public information only — clinic name, specialty, city, public phone, public email,
  website URL from clinic's own website or public directories
- No data from data brokers, scrapers, or aggregated private datasets
- No real patient data
- No secrets
- No DSGVO-restricted personal data beyond what clinics publish publicly

## Allowed changes

- `docs/business/CLINIC_OUTREACH_LIST_FIRST_50.md` (new)
- `docs/claude/CURRENT_STATE.md` (updated)
- `docs/claude/NEXT_MODULE.md` (updated)

No tests required for this module (data list doc, no runtime code).

## Acceptance

- First 50 clinic targets listed with all schema fields
- Priority scores assigned
- Week 1 shortlist (top 10) identified
- All information is publicly sourced
- No real patient data; no secrets
- Commit: `Sprint 18 / Module 128 — Clinic outreach list builder and first 50 targets`

---

## Upcoming (commercial MVP build track, post-Module 128)

- **Module 129** — Consultation summary draft generator
- **Module 130** — Patient timeline
- **Module 131** — Follow-up and reminder workflow

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)
