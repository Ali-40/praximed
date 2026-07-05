# Sprint 18 / Module 129 — First 50 Vienna Clinic Targets Research

Status: pending implementation.

## Context

Module 128 complete:
- Outreach list tracker structure created with 50 empty rows ready to fill
- 9 outreach status stages defined; A/B/C fit scoring; 7 specialty priorities
- Daily execution rules: 10 clinics/day research, 5 contacts/day minimum
- Suggested public research sources listed (WKO, Google Maps, docfinder.at, etc.)
- Full backend tests: 2868/2868 passed

## Goal

Populate the first 50 rows of the clinic outreach tracker with real, publicly sourced
private clinic targets in Vienna. This gives Ali an immediately actionable outreach
list ready for first contact.

## Scope

Docs/business only. No runtime code. No scraping automation. No real patient data.
No secrets. No production PHI. Public information only.

## What Module 129 must do

1. **Research 50 private clinics in Vienna** — using public sources only:
   WKO, Google Maps, docfinder.at, herold.at, ärzteliste.at, clinic websites.

2. **Fill all 50 rows** in `docs/business/CLINIC_OUTREACH_LIST_TRACKER.md` with:
   - Clinic name (from public source)
   - Specialty
   - Website URL (from public listing)
   - Public email (from clinic website Impressum or contact page)
   - Public phone (from clinic website or directory)
   - Address (from public listing)
   - Doctor/Owner name (from clinic website "Team" or "Über uns" page)
   - Fit score (A/B/C)
   - Pain point guess
   - Contact method (email / phone / LinkedIn)
   - Outreach status: Not contacted
   - Source URL noted in Notes column

3. **Mark top 10 Week 1 priority clinics** — identify the 10 highest-fit (A-score)
   clinics and add "WEEK 1 PRIORITY" in their Notes field.

4. **Specialty distribution target for the 50:**
   - 12 private GPs (Allgemeinmedizin privat)
   - 8 dermatology (Dermatologie/Hautklinik privat)
   - 8 gynecology (Gynäkologie privat)
   - 6 orthopedics (Orthopädie privat)
   - 6 dentistry (Zahnarzt privat)
   - 6 aesthetics / private medicine
   - 4 physiotherapy / private rehab

## Constraints

- **Public information only** — clinic website, Google Maps, WKO, docfinder.at,
  herold.at, ärzteliste.at, clinic Impressum (legally required in Austria)
- No data brokers, no scrapers, no aggregated non-public data
- No real patient data in any field
- No secrets
- If a clinic's email is not publicly listed, leave Email blank and use phone/LinkedIn

## Allowed changes

- `docs/business/CLINIC_OUTREACH_LIST_TRACKER.md` (updated — 50 rows filled)
- `docs/claude/CURRENT_STATE.md` (updated)
- `docs/claude/NEXT_MODULE.md` (updated)

No tests required (data list only, no runtime code).

## Acceptance

- All 50 rows populated with real publicly sourced Vienna clinic data
- Fit scores assigned to all 50
- Top 10 Week 1 priorities marked
- All information traceable to a public source
- No real patient data; no secrets
- Commit: `Sprint 18 / Module 129 — First 50 Vienna clinic targets research`

---

## Upcoming (commercial MVP build track, post-Module 129)

- **Module 130** — First outreach batch execution (send first 10 emails)
- **Module 131** — Consultation summary draft generator
- **Module 132** — Patient timeline

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)
