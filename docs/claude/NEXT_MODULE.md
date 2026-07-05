# Sprint 17 / Module 121 — Patient and Appointment Data Linking Foundation

Status: pending implementation.

## Context

Architecture Checkpoint 17 complete:
- Commercial acceleration mode active — clinic outreach starts immediately with fake-data demo
- Module 120B PASS: deployed browser auth/session smoke confirmed
- praximed_session httpOnly Secure SameSite=None cookie works in Vercel→Railway staging
- Full test suite: 2570/2570 passed
- Commit base: 38e9234

Production hardening blockers C3–C8 remain open (Modules 121–124 on hardening track).
Commercial MVP build track now runs in parallel with hardening track.

## Goal

Build the data model and repository layer that links `appointment_requests` to `patients`,
and introduces a new `appointments` table with full lifecycle states. This is the highest-
leverage technical step for commercial readiness — it directly enables appointment lifecycle
management, doctor notification, pre-appointment summaries, and consultation summary drafts
that pilot clinics will need.

## Scope

Backend only. No frontend changes. Full test suite must pass.

## What Module 121 must do

1. **Schema changes** — define a new `appointments` table (or extend `appointment_requests`)
   with lifecycle states: `new → scheduled → confirmed → completed → cancelled`

2. **Repository layer** — implement `appointment_repo.py` (or extend `appointment_request_repo.py`)
   with CRUD and state transition methods; link to `patients` via `patient_id` FK

3. **API routes** — add or update routes for the linked appointment/patient data

4. **Tests** — full test suite must pass; new module tests cover the schema, repo, and routes

## What not to do

- Do not generate, record, or commit any real secrets or credential values
- Do not deploy to production
- Do not change auth/session code (separate hardening track)
- Do not expose any existing secrets from Railway, Vercel, or any other service
- Do not use real patient data

## Reference docs

- `docs/architecture/ARCHITECTURE_CHECKPOINT_17_COMMERCIAL_MVP_OUTREACH_ACCELERATION.md`
  — commercial MVP feature map and priority order
- `backend/app/db/schema.sql` — current schema
- `backend/app/db/repositories/appointment_request_repo.py` — current appointment repo
- `backend/app/db/repositories/patient_repo.py` — patient repo

## Acceptance

- Schema updated with lifecycle states and patient linkage
- Repository methods implemented and tested
- API routes updated or added
- Full test suite passes
- Commit: `Sprint 17 / Module 121 — Patient and appointment data linking foundation`

---

## Parallel non-code task (runs alongside Module 121)

**Build first list of 50 private clinics in Vienna and start outreach immediately.**

Sources: Docfinder.at, WKO Ärzteliste, Google Maps, LinkedIn.
Format: clinic name / specialty / contact name / phone / email / Google Maps link / notes.
Target: 50 clinics identified; 10–15 first-contact messages or calls within 14 days.

---

## Upcoming (commercial MVP build track, post-Module 121)

- **Module 122** — Appointment lifecycle states and workflow
- **Module 123** — Doctor/reception notification (email or push)
- **Module 124** — Pre-appointment patient summary
- **Module 125** — Consultation summary draft generator
- **Module 126** — Follow-up and reminder workflow

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)

## Sprint 18

- **Fabel 5 premium UI/UX polish** — transform the functional dashboard into a
  premium, doctor-facing product; high priority for demo quality and sales conversion
