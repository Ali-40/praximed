# Sprint 20 / Module 157 — Live Longitudinal Timeline Smoke Evidence

Status: pending.

## Context

Module 156 complete (Longitudinal Timeline and Delta View Foundation):
- Timeline aggregates appointment requests, intake submissions, consent events,
  structuring runs, unverified proposals, and approved patient_history_* entries.
- Delta view shows items changed since last visit anchor (latest appointment_request).
- Approved history and unverified proposals are clearly separated.
- No diagnosis. No medical advice. No triage scoring. No treatment recommendations.
- No external LLM. No new writes. No PHI.
- 5067/5067 backend tests passing. Frontend build clean.
- Production PHI remains NO-GO.

## Goal

Deploy Module 156 to staging and document live evidence that the timeline view works
for a staging patient with synthetic intake/review/merge data.
Load timeline, verify approved history appears, verify unverified proposal separation,
verify delta view, and document all safety boundaries.

Docs/static-tests only. No new backend code. No frontend changes. No migration.

## What Module 157 must produce

### 1. Evidence document

`docs/runtime/LIVE_LONGITUDINAL_TIMELINE_SMOKE_EVIDENCE.md` (new)

Sections:
1. Purpose
2. Current result: PASS
3. Live route tested
4. Clinic ID and patient ID used
5. Timeline endpoint evidence
6. Approved history items visible
7. Unverified proposal items visible (labeled separately)
8. Consent event visible
9. Intake submission visible
10. Appointment event visible
11. Structuring run visible
12. Delta since last visit evidence
13. changed_since_last_visit anchor confirmed
14. no_prior_visit_anchor behavior documented (if tested)
15. production_phi_enabled false evidence
16. Extraction confidence label evidence
17. Safety boundaries
18. What this proves
19. What this does not prove
20. Remaining blockers

### 2. Tests

`backend/tests/test_live_longitudinal_timeline_smoke_evidence_contract.py` (new — ≥20 tests)

Static evidence validation tests (no live API calls):
- Evidence doc exists
- Result is PASS
- Mentions Module 157
- Mentions timeline route
- Mentions staging clinic_id
- Mentions approved history
- Mentions unverified proposal
- Mentions changed_since_last_visit or no_prior_visit_anchor
- Mentions delta since last visit
- Mentions consent_event
- Mentions intake_submission
- Mentions appointment_request
- Mentions structuring_run
- Mentions production_phi_enabled false
- Mentions extraction confidence labeled correctly
- Mentions no auto-approval
- Mentions no diagnosis
- Mentions no medical advice
- Mentions no treatment recommendations
- Mentions no triage scoring
- Mentions no real patient data
- Mentions no PHI
- Mentions Production PHI remains NO-GO
- Mentions remaining blockers
- No DATABASE_URL, no JWT_SECRET, no sk- keys
- No real patient names
- No diagnosis generation claim
- No production readiness claim

### 3. Docs updates

- docs/claude/CURRENT_STATE.md — Module 157 entry
- docs/claude/NEXT_MODULE.md — updated to Module 158

## Module 158 preview

Sprint 20 / Module 158 — Patient Story Pre-Visit Narrative Foundation

Module 158 should:
- add a pre-visit narrative generator that summarizes the approved patient timeline
  into a structured (non-medical-interpretation) summary for the doctor before a visit
- approved structured data only — no unverified proposals in narrative
- no diagnosis, no medical advice, no treatment recommendations
- local template-based narrative generation (no external LLM)
- production PHI remains NO-GO

## Constraints

- No new backend code — docs/tests only
- All evidence must be synthetic staging — no real PHI
- No diagnosis, no medical advice, no triage scoring in evidence
- production_phi_enabled=False confirmed in all documented responses
- Full test suite must remain green
- Frontend build must remain clean
- Commit message:
  Sprint 20 / Module 157 — Live longitudinal timeline smoke evidence
