# Sprint 11 / Module 88 — Real Vapi Tool Call Adapter

Status: pending Module 87 review.

## Context

Module 87 identified the shape gap between a real Vapi tool-call body and the current
`VapiAppointmentCaptureRequest` schema:

**Real Vapi tool-call body (nested):**
```json
{
  "message": {
    "type": "tool-calls",
    "toolCallList": [{ "function": { "name": "...", "arguments": {...} } }],
    "call": { "id": "...", "customer": { "number": "..." } }
  }
}
```

**Current schema (flat):**
```json
{ "clinic_ref": "...", "call_id": "...", "patient_name": "..." }
```

The current capture route only accepts the flat shape (used by the local harness).
A real Vapi assistant calling the tool will send the nested shape. An adapter is needed,
similar to `_adapt_vapi_payload` added for the webhook route in Module 56.

Mapping:
- `clinic_ref` → from `X-Vapi-Clinic-Id` header (machine auth context)
- `call_id` → from `message.call.id`
- `patient_name` → from `message.toolCallList[0].function.arguments.patient_name`
- `caller_phone` → from `message.call.customer.number`
- `reason`, `urgency_level` → from `function.arguments`

## Scope

### 1. Add `_adapt_vapi_tool_call_body` to the capture route

In `backend/app/api/routes/vapi_tools.py`, add a helper that:
- Detects nested `message.toolCallList` shape
- Extracts arguments, `call_id` from `message.call.id`, `caller_phone` from customer
- Passes `clinic_ref` from machine auth context (`machine_auth.clinic_id`)
- Returns a dict matching `VapiAppointmentCaptureRequest` fields
- Falls through unchanged if body is already flat (preserves local harness compatibility)

### 2. Wire the adapter in `vapi_capture_appointment_request`

Accept `Request` alongside the Pydantic body (as done in Module 56 for the webhook).
Or: change the route to accept `body: dict` and run adaptation before Pydantic validation.

### 3. Add tests

Extend `backend/tests/test_vapi_tool_routes.py`:
- Adapter maps nested payload to flat `VapiAppointmentCaptureRequest` fields
- Adapter leaves flat payload unchanged
- Missing `patient_name` in arguments → 422
- `call_id` resolved from `message.call.id`
- `clinic_ref` resolved from machine auth, not body

### 4. Run the inspector on any real captured payload

If a real Vapi payload has been captured manually:
```bash
python backend/scripts/inspect_vapi_tool_payload.py \
  --payload-file docs/integrations/local_payloads/vapi_real_tool_payload_captured.json
```

Compare against the adapter logic and adjust if the real shape differs from the sample.

### 5. Update docs

- `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` — mark shape gap RESOLVED
- `docs/claude/CURRENT_STATE.md` — record Module 88
- `docs/claude/NEXT_MODULE.md` — Module 89

## What not to do

- Do not use real patient data or real Vapi credentials
- Do not auto-confirm appointment requests in the adapter
- Do not change auth, JWT, machine auth, webhook signature, or seed data
- Do not break the existing flat-payload path (local harness must still work)

## Acceptance

- Nested Vapi tool-call body shape is handled by the capture route
- Flat local harness body shape continues to work
- All existing tests pass
- New adapter tests cover both shapes
- `inspect_vapi_tool_payload.py` reports COMPATIBLE on the captured payload
- Commit: `Sprint 11 / Module 88 — Real Vapi tool call adapter`
