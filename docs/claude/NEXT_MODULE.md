# Sprint 11 / Module 87 — Real Vapi Appointment Tool Payload Smoke

Status: pending Module 86 review.

## Context

Module 86 proved the local Vapi intake loop end-to-end:
- `smoke_vapi_appointment_intake.py` → HTTP 200 → appointment row → dashboard → staff Confirm → "confirmed"
- Staff confirmation boundary maintained: AI does not auto-confirm

The local harness uses a hand-crafted JSON payload that matches `VapiAppointmentCaptureRequest`.
The remaining gap is whether a real Vapi assistant's tool-call payload will match this schema,
or whether an adapter is needed (similar to the `_adapt_vapi_payload` added for the webhook
in Module 56).

## Scope

### 1. Inspect real Vapi tool-call payload format

Investigate what Vapi sends when a tool call fires during a phone session:
- Tool call body shape (field names, nesting, types)
- Whether `clinic_ref`, `call_id`, `patient_name` match exactly or need mapping
- Whether Vapi wraps the body in a `message` envelope (as the webhook does)

Sources to inspect:
- Vapi documentation on tool call payloads
- `backend/app/schemas/vapi.py` — `VapiAppointmentCaptureRequest` field names
- `backend/app/api/routes/vapi_tools.py` — the capture route handler
- Module 56 notes in `docs/claude/CURRENT_STATE.md` — how webhook adapter was built

### 2. Compare against VapiAppointmentCaptureRequest schema

| VapiAppointmentCaptureRequest field | Required? | Real Vapi tool payload equivalent |
|---|---|---|
| `clinic_ref` | Yes | TBD |
| `call_id` | Yes | TBD |
| `patient_name` | Yes | TBD |
| `caller_phone` | No | TBD |
| `reason` | No | TBD |
| `urgency_level` | No | TBD |
| `raw_payload` | No | TBD |

### 3. Identify any adapter needed

If the real payload shape differs, plan a minimal field-mapping adapter in the capture route
(similar to `_adapt_vapi_payload` in the webhook route). If the schema matches exactly,
document that no adapter is needed.

### 4. Update docs

- `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` — record findings; mark real payload gap RESOLVED or document required adapter
- `docs/claude/CURRENT_STATE.md` — record Module 87
- `docs/claude/NEXT_MODULE.md` — Module 88 (adapter implementation if needed, or next workflow action)

## What not to do

- Do not use real patient data or real Vapi credentials for testing
- Do not auto-confirm appointment requests or create calendar events
- Do not modify auth, JWT, machine auth, or webhook signature
- Do not implement the adapter without inspecting the real payload first

## Acceptance

- Real Vapi tool-call payload shape documented
- Gap between real payload and `VapiAppointmentCaptureRequest` identified or ruled out
- If adapter needed: design documented; implementation scoped to Module 88
- If no adapter needed: documented explicitly
- No code changes required for this module (docs + inspection only)
- Commit: `Sprint 11 / Module 87 — Real Vapi appointment tool payload smoke`
