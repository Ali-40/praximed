# Sprint 11 / Module 90 — Direct Real Vapi Assistant Tool-Call Log Capture

Status: pending Architecture Checkpoint 10 review.

## Context

Architecture Checkpoint 10 reviewed the full Sprint 11 Vapi intake loop. One evidence
gap remains: the local/ngrok path is proven end-to-end, but direct real Vapi assistant
call logs have not been captured. The adapted endpoint is ready. The shape is understood.
Module 90 closes this gap with evidence from a real live Vapi test assistant.

## Scope

Docs and evidence only. No production code changes unless a real blocker appears.

### 1. Prerequisites

- A test Vapi assistant configured to call `capture_appointment_request` as a server-URL tool.
- ngrok tunnel exposing `http://127.0.0.1:8000`.
- Backend running with `DATABASE_URL`, `JWT_SECRET_KEY`, and machine auth env vars.
- Seed data fresh (`python backend/scripts/seed_local_data.py`).

**Test assistant only — never a production assistant with real patients.**

### 2. Vapi tool configuration (from Module 89)

| Field | Value |
|---|---|
| Method | `POST` |
| URL | `https://<ngrok-id>.ngrok-free.app/vapi/tools/capture-appointment-request` |
| `X-Vapi-Service-Name` | `vapi` |
| `X-Vapi-Clinic-Id` | `11111111-1111-1111-1111-111111111111` |
| `X-Vapi-Scopes` | `vapi:tool` (singular — not `vapi:tools`) |
| Function name | `capture_appointment_request` |
| `patient_name` | string, required |
| `reason` | string, optional |
| `urgency_level` | string enum `["normal", "urgent", "emergency"]`, optional |

Do NOT add `caller_phone` to parameters — it comes from `message.call.customer.number`.

### 3. Steps

1. Start stack: PostgreSQL, seed, backend, frontend, ngrok.
2. Configure test Vapi assistant with tool as above.
3. Make a test call: *"I'd like to book an appointment. My name is Local Real Vapi Caller. Fake test consultation only."*
4. Observe Vapi tool-call result in Vapi dashboard call logs.
5. Confirm backend received request (backend terminal or ngrok inspector).
6. Sanitize the captured payload — replace all patient names/phones with fake values.
7. Save sanitized payload as `docs/integrations/local_payloads/vapi_real_tool_payload_captured_from_live_assistant.json`.
8. Run inspector:
   ```bash
   python backend/scripts/inspect_vapi_tool_payload.py \
     --payload-file docs/integrations/local_payloads/vapi_real_tool_payload_captured_from_live_assistant.json
   ```
9. Note the argument keys present in the real payload — compare with adapter expectations.
10. Open `http://localhost:3000/login`, verify appointment row appeared with `source=vapi`, `status=new`.
11. Click Confirm; verify status → confirmed.

### 4. If argument keys differ from sample

If the real Vapi assistant sends `name` instead of `patient_name`, `phone` instead of
`caller_phone`, or any other alias:
- Add alias handling to `adapt_vapi_tool_call_body` in `vapi_appointment_capture.py`.
- Add unit tests for the alias keys.
- Re-run the live smoke to confirm the fix.
- This would be the only code change in Module 90.

### 5. Document results

Create `docs/runtime/VAPI_REAL_ASSISTANT_TOOL_CALL_SMOKE_RESULTS.md` with:
- Environment (ngrok URL sanitized, Vapi assistant name/ID sanitized)
- Steps completed
- Evidence table: Vapi call log status, HTTP status from backend, response body (sanitized), dashboard row, inspector verdict
- Accuracy statement: what is now proven vs what remains pending
- What this proves / what it does not prove

### 6. Update docs

- `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` — mark direct Vapi assistant logs RESOLVED
- `docs/claude/CURRENT_STATE.md` — record Module 90
- `docs/claude/NEXT_MODULE.md` — Architecture Checkpoint 11 or Sprint 12 placeholder

### 7. What not to do

- Do not use real patient data or real patient names
- Do not commit any payload with residual PII
- Do not auto-confirm appointment requests
- Do not change machine auth or webhook signature logic
- Do not claim production readiness in the docs

## Acceptance

- Real live Vapi assistant triggers `capture_appointment_request`
- Backend receives nested Vapi-shape body, adapter fires, HTTP 2xx returned
- Appointment row visible in dashboard with `source=vapi`, `status=new`
- Staff Confirm succeeds in browser
- Sanitized payload archived
- Inspector reports NEEDS ADAPTER (adapter already wired)
- If argument keys differ from sample, adapter adjusted and re-tested
- All existing tests pass (1625/1625 minimum)
- Commit: `Sprint 11 / Module 90 — Direct real Vapi assistant tool-call log capture`
