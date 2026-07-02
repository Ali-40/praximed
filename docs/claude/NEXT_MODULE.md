# Sprint 11 / Module 89 — Real Vapi Live Tool-Call Smoke Evidence

Status: pending Module 88 review.

## Context

Module 88 added `adapt_vapi_tool_call_body` to the capture route so the endpoint now
accepts both the flat local harness shape and the real Vapi nested tool-call shape
(`message.toolCallList`). The flat harness smoke (Module 85) remains PASS. The nested
shape is verified only by unit tests — no live Vapi assistant has yet called the
adapted endpoint.

Module 89 closes this gap by running a real Vapi assistant tool call through an ngrok
tunnel to the local backend and confirming the full end-to-end flow works.

## Scope

### 1. Prerequisites

- A test Vapi assistant configured to call `capture_appointment_request` as a server-URL tool.
- An ngrok tunnel exposing `http://127.0.0.1:8000`.
- Backend running with `DATABASE_URL`, `JWT_SECRET_KEY`, and machine auth env vars set.
- Seed data fresh (`python backend/scripts/seed_local_data.py`).

**CRITICAL**: Use a test Vapi assistant only. Never use a production assistant with real patients.

### 2. Run the live smoke

1. Start PostgreSQL: `docker-compose -f docker-compose.postgres.yml up -d`
2. Run seed: `python backend/scripts/seed_local_data.py`
3. Start backend: `uvicorn backend.app.main:app --reload --port 8000`
4. Start ngrok: `ngrok http 8000`
5. Configure test Vapi assistant server URL to `https://<ngrok-id>.ngrok.io/vapi/tools/capture-appointment-request`
6. Configure machine auth headers in Vapi: `X-Vapi-Service-Name: vapi`, `X-Vapi-Clinic-Id: 11111111-1111-1111-1111-111111111111`, `X-Vapi-Scopes: vapi:tool`
7. Make a test call with fake patient: "I would like to book an appointment for Local Vapi Live Caller"
8. Confirm backend returns HTTP 200 in ngrok inspector or backend logs
9. Confirm appointment request appears in dashboard with `source=vapi`, `status=new`
10. Capture the raw payload from ngrok inspector, sanitize it (remove all PII), save as `docs/integrations/local_payloads/vapi_real_tool_payload_captured.json`
11. Run inspector: `python backend/scripts/inspect_vapi_tool_payload.py --payload-file docs/integrations/local_payloads/vapi_real_tool_payload_captured.json`
12. Confirm verdict is COMPATIBLE (or adjust adapter if argument key names differ from sample)

### 3. Document results

Create `docs/runtime/VAPI_REAL_TOOL_PAYLOAD_LIVE_SMOKE_RESULTS.md` with:
- Environment (ngrok URL, backend version, Vapi assistant name/ID — sanitized)
- Steps completed
- Evidence table: HTTP status, response body, dashboard row, inspector verdict
- What this proves / what it does not prove
- Any adapter adjustments needed

### 4. Update docs

- `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` — mark live smoke COMPLETE
- `docs/claude/CURRENT_STATE.md` — record Module 89
- `docs/claude/NEXT_MODULE.md` — Module 90

### 5. Update adapter if needed

If the real captured payload uses different argument key names (e.g. `name` instead of
`patient_name`, `phone` instead of `caller_phone`):
- Add aliasing logic in `adapt_vapi_tool_call_body`
- Add tests for the alias keys
- Re-run live smoke to confirm

## What not to do

- Do not use real patient data or real patient names
- Do not commit the captured payload without sanitizing PII first
- Do not use a production Vapi assistant
- Do not auto-confirm appointment requests in the adapter
- Do not change machine auth, HMAC, or JWT logic
- Do not break the flat harness path (local smoke must still pass)

## Acceptance

- Live Vapi assistant → ngrok → backend → HTTP 200
- Appointment request created with `source=vapi`, `status=new`, `action_required=true`
- Appointment request visible in dashboard
- Inspector reports COMPATIBLE on captured payload (or adapter adjusted and re-tested)
- All existing tests pass
- Commit: `Sprint 11 / Module 89 — Real Vapi live tool-call smoke evidence`
