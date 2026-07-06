# Sprint 19 / Module 131 — Real Staging End-to-End Demo Execution Evidence

Status: pending implementation.

## Context

Module 130 complete:
- Backend data flow and storage map documented (Railway FastAPI + Railway PostgreSQL + Vercel)
- Staging end-to-end demo runbook created (9-step runbook with fake Vapi intake curl)
- Vapi German/English assistant setup documented (German-first, English fallback, safe boundaries)
- Staging clinic config updated: de/en language, clinic_display_name, specialty, feature flags
- 3151/3151 backend tests pass

## Goal

Execute the Module 130 runbook against the live Railway + Vercel staging environment and
document the real evidence that every step passes.

## What Module 131 must verify (against live staging)

1. Backend health liveness: GET /health returns {"status":"ok"}
2. Backend health readiness: GET /health/ready returns {"status":"ready"}
3. Vercel frontend loads at https://praximed.vercel.app
4. Login with staging doctor credentials — redirected to /dashboard
5. Dashboard shows "Dr. Med. Alexander Huber | Innere Medizin Wien" banner
6. Staging safety boundary visible (STAGING DEMO / no real patient data / Production PHI: NO-GO)
7. Fake Vapi intake curl succeeds: {"ok":true}
8. New appointment ("Demo Patient") appears in Incoming AI Intake Queue
9. View summary opens the Active Resolution Workspace with patient details
10. Confirm action changes status to confirmed
11. Patient Registry shows Demo Patient record
12. Notification appears for the intake event
13. Logout redirects to login
14. No real patient data observed
15. No secrets recorded

## Deliverables

- `docs/runtime/STAGING_E2E_DEMO_EXECUTION_EVIDENCE.md` (new)
- `backend/tests/test_staging_e2e_demo_execution_evidence_contract.py` (new)
- `docs/claude/CURRENT_STATE.md` and `docs/claude/NEXT_MODULE.md` updates

## Constraints

- Docs/static-tests only. No runtime code changes. No backend changes.
- No fabricated evidence — only document what is actually observed.
- No secrets. No real patient data. No production PHI.
- No production readiness claim.
