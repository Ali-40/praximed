# Sprint 19 / Module 131 — Compliance Gate Integration and PHI Safeguard Route Wiring

Status: pending implementation.

## Context

Module 130 (Compliance Readiness Gate and Language Foundation) complete:
- `backend/app/core/compliance.py` — production PHI circuit breaker:
  - `enforce_phi_safeguard()` async FastAPI dependency (HTTP 403 in production when locked)
  - `assert_production_compliance_ready()` for pre-flight startup checks
  - Language env helpers: `get_default_clinic_language()`, `get_supported_clinic_languages()`
- `backend/app/core/pseudonymization.py` — HMAC-SHA256 PII pseudonymizer for logs/audit
- `ClinicConfig` extended: `fallback_language`, `clinic_display_name`, `specialty`, `city`
- Frontend onboarding: German/English language foundation scaffold
- 3218/3218 tests pass

## Goal

Wire `enforce_phi_safeguard` as a FastAPI dependency on the PHI-processing routes,
add startup compliance assertions, and integrate `pseudonymize_*` into the Vapi
audit log path. Keep all existing tests green.

## What Module 131 must implement

1. Wire `enforce_phi_safeguard` onto PHI-sensitive routes:
   - `POST /vapi/tools/capture-appointment-request`
   - `GET /api/appointment-requests` and `/{id}` and `/{id}/summary`
   - `POST /api/appointment-requests/{id}/confirm`
   - `GET /api/patients`
   - Do NOT wire to `/health` or `/health/ready`

2. Add startup compliance assertion in `main.py` lifespan:
   - In local/staging: log a warning if PRODUCTION_COMPLIANCE_UNLOCKED is set (unexpected)
   - In production: call `assert_production_compliance_ready()` and crash fast if not ready
   - Do not break the app when DATABASE_URL is absent (existing behavior preserved)

3. Integrate `pseudonymize_phone` and `pseudonymize_name` into the Vapi audit log:
   - In `vapi_tools.py`, replace raw `call_id` / `patient_name` / `caller_phone` in audit
     metadata with their pseudonymized forms
   - Keep the appointment_request record itself unchanged (full fidelity in DB)
   - Only the audit log metadata gets pseudonymized tokens

4. Tests:
   - `backend/tests/test_compliance_gate_route_integration.py` (new)
     - enforce_phi_safeguard blocks the capture route in production when locked
     - enforce_phi_safeguard passes in staging
     - /health not blocked
     - /health/ready not blocked
   - `backend/tests/test_pseudonymization_audit_integration.py` (new)
     - audit metadata for Vapi capture contains pseudonymized tokens, not raw PII
     - pseudonymized tokens are hex strings of length 64

## Constraints

- No production unlock — ENVIRONMENT stays staging/local
- No real patient data
- No secrets committed
- Keep full test suite green
- Production PHI remains NO-GO
