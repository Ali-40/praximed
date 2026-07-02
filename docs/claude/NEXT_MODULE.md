# Sprint 6 / Module 57 — Real Vapi Tunnel Retest Evidence

Status: pending Module 56 review.

Repeat the Vapi test plan from `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` Section 6 with the Module 56 payload adapter in place.

Verify that the real Vapi payload no longer causes HTTP 400 and that HTTP 200 is returned for both `assistant-started` and `end-of-call-report` events.

Record:

- HTTP response status from FastAPI for each real Vapi event type.
- Whether `clinic_id` was correctly resolved from machine auth headers.
- Whether `event_type` was correctly mapped from `message.type`.
- Whether any further schema or adapter changes are needed.
