# Sprint 18 / Module 130 — First 10 Vienna Clinic Targets Manual Entry

Status: pending implementation.

## Context

Module 129 complete:
- Full research workflow prepared for manually sourcing 50 Vienna private clinic targets
- 7 public research sources listed (Google Maps, Impressum, Herold, DocFinder, WKO, etc.)
- 7 specialty targets with German search terms
- Data quality rules: source URL required, no guessing, no scraping, public-only
- First batch execution steps: research 10 → contact 5 → 3-business-day follow-up
- Next action checklist ready
- Full backend tests: 2893/2893 passed

## Goal

Manually research and enter the first 10 real, publicly sourced private clinic targets
in Vienna into the tracker. Then prepare the first 5 outreach sends.

All entries must be sourced from public pages — no fabrication, no scraping automation.

## Scope

Docs/business only. No runtime code. No scraping. No fake data. Public information only.
No real patient data. No secrets. No production PHI.

## What Module 130 must do

1. **Research first 10 clinics** using the workflow defined in Module 129:
   - Open Google Maps, DocFinder, Herold, or clinic websites
   - Fill rows 1–10 in `docs/business/CLINIC_OUTREACH_LIST_TRACKER.md`
   - Every row must have a source URL in Notes
   - Assign fit score A/B/C to each

2. **Identify top 5** by fit score for first outreach

3. **Draft first 5 personalised outreach messages** — using Module 127 scripts as
   a base, personalise slightly for each clinic's specialty and name

4. **Log outreach status** — update tracker: Email sent / Called, Last contacted,
   Next follow-up (+3 business days)

## Constraints

- No fabricated clinic names, emails, phones, or doctor names
- No scraping automation
- No real patient data
- No secrets
- Source URL required for every entry

## Allowed changes

- `docs/business/CLINIC_OUTREACH_LIST_TRACKER.md` (updated — rows 1–10 filled)
- `docs/business/FIRST_10_OUTREACH_DRAFTS.md` (new — 5 personalised outreach messages)
- `docs/claude/CURRENT_STATE.md` (updated)
- `docs/claude/NEXT_MODULE.md` (updated)

No tests required (data list + outreach drafts, no runtime code).

## Acceptance

- Rows 1–10 in the tracker filled with real publicly sourced Vienna clinic data
- Source URL present in Notes for every row
- Fit scores assigned to all 10
- Top 5 identified
- 5 personalised outreach drafts prepared
- No fabricated data; no scraping; no patient data; no secrets
- Commit: `Sprint 18 / Module 130 — First 10 Vienna clinic targets manual entry`

---

## Upcoming (commercial MVP build track, post-Module 130)

- **Module 131** — First outreach batch sent (log actual send evidence)
- **Module 132** — Consultation summary draft generator (product feature)
- **Module 133** — Patient timeline (product feature)

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)
