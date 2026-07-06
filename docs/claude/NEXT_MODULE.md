# Sprint 19 / Module 131 — Real Staging End-to-End Demo Execution Evidence

Status: pending implementation.

## Context

Module 130 complete (all parts):
- `backend/app/core/compliance.py` — production PHI circuit breaker:
  - `enforce_phi_safeguard()` wired to all PHI-processing routes
  - `assert_production_compliance_ready()` for startup pre-flight
  - Language env helpers: `get_default_clinic_language()`, `get_supported_clinic_languages()`
- `backend/app/core/pseudonymization.py` — HMAC-SHA256 PII pseudonymizer:
  - `sanitize_vapi_webhook_payload()`, `sanitize_for_log()`, `redact_transcript()`
  - Vapi audit log metadata uses pseudonymized patient_name and phone hashes
- PHI routes gated: appointment_requests, patients, consultations, clinical_workflows, Vapi capture
- Staging clinic config: staging_display + language_config sections
- docs: COMPLIANCE_READINESS_GATE.md, VAPI_PSEUDONYMIZED_LOGGING.md, VAPI_GERMAN_ENGLISH_ASSISTANT_SETUP.md
- 3253/3253 tests pass

## Goal

Execute the end-to-end demo runbook against the live Railway + Vercel staging environment
and document the real evidence that every step passes.

## What Module 131 must verify (against live staging)

1. Backend health liveness: GET /health → {"status":"ok"}
2. Backend health readiness: GET /health/ready → {"status":"ready"}
3. Vercel frontend loads at https://praximed.vercel.app
4. Login → redirected to /dashboard
5. Dashboard shows "Dr. Med. Alexander Huber | Innere Medizin Wien" banner
6. Staging safety boundary visible (STAGING DEMO / no real patient data / Production PHI: NO-GO)
7. Fake Vapi intake curl → {"ok":true}
8. "Demo Patient" appointment appears in Incoming AI Intake Queue
9. View summary opens Active Resolution Workspace with patient details
10. Confirm changes status to confirmed
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

- Docs/static tests only. No runtime code changes.
- No fabricated evidence — only document what is actually observed.
- No secrets. No real patient data. No production PHI.
- No production readiness claim.
