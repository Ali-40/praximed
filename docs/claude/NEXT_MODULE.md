# Sprint 18 / Module 126B — Deployed Fabel 5 Dashboard UI/UX Smoke Evidence

Status: pending implementation.

## Context

Module 126 complete:
- Fabel 5 premium dashboard UI/UX polish implemented
- Sticky header with brand + staging demo badge + logout
- 4-card metrics row: Appointments, Patients, Notifications, Pending confirmations
- Appointments as primary full-width section
- Two-column responsive grid: Patients + Notifications side by side
- Pending notifications with brand-blue left border accent
- Summary panel: blue-50 elevated card, labeled fields, suggested action in brand blue
- Safety note rendered below a rule in muted text
- All existing functionality preserved (Confirm, View summary, login/session/logout)
- Full backend tests: 2801/2801 passed

## Goal

Document real deployed browser evidence that the Fabel 5 premium dashboard UI is
live on Vercel and all key interactions work correctly in the deployed environment.

## Scope

Docs/static-tests only. No runtime code changes. No new migrations. No secrets.
No real patient data. No production PHI. Do not mark production ready.

## What Module 126B must do

1. Push/deploy the Module 126 frontend to Vercel (developer action).
2. Verify the premium dashboard loads in browser.
3. Verify metric cards are visible.
4. Verify appointment rows with View summary / Hide summary work.
5. Verify summary panel opens and closes inline.
6. Verify Confirm button works for status=new rows.
7. Verify logout works.
8. Verify staging demo badge is visible.
9. Document all evidence in a new runtime evidence doc.
10. Add static contract tests for the evidence doc.
11. Update staging wiring and smoke execution docs.

## Allowed changes

- `docs/runtime/FABEL5_PREMIUM_DASHBOARD_DEPLOYED_SMOKE_EVIDENCE.md` (new)
- `backend/tests/test_fabel5_premium_dashboard_deployed_smoke_evidence_contract.py` (new)
- `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` (updated)
- `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` (updated)
- `docs/claude/CURRENT_STATE.md` (updated)
- `docs/claude/NEXT_MODULE.md` (updated)

## Safety constraints

- Fake/non-PHI data only in all tests and staging
- Production PHI readiness: NO-GO (C3–C8 hardening blockers still open)
- No real patient name, phone, DOB, or medical history in any file
- Doctor/staff approval remains required — no automated confirmation path
- No medical advice or diagnosis in notification body or summary display
- No secrets recorded in any evidence

## Reference docs

- `docs/architecture/FABEL_5_PREMIUM_DASHBOARD_UI_UX_POLISH.md` — Module 126
- `docs/runtime/DASHBOARD_NOTIFICATION_AND_SUMMARY_UI_DEPLOYED_SMOKE_EVIDENCE.md` — Module 125B
- `frontend/app/dashboard/page.tsx` — current dashboard (Module 126)

## Acceptance

- Deployed Fabel 5 premium dashboard smoke documented as PASS
- Metric cards visible
- View summary / Hide summary confirmed in browser
- Confirm flow confirmed
- Logout confirmed
- Staging demo badge visible
- Full tests pass
- Commit: `Sprint 18 / Module 126B — Deployed Fabel 5 dashboard UI smoke evidence`

---

## Upcoming (commercial MVP build track, post-Module 126B)

- **Module 127** — Consultation summary draft generator
- **Module 128** — Patient timeline
- **Module 129** — Follow-up and reminder workflow

## Upcoming (production hardening track, parallel)

- **Module 121 (hardening)** — Secrets and environment hardening review (C3)
- **Module 122 (hardening)** — PHI logging/redaction and audit hardening (C4, C6)
- **Module 123 (hardening)** — Tenant isolation and access-control verification (C5)
- **Module 124 (hardening)** — Backup/restore and rollback runbook (C7, C8)
