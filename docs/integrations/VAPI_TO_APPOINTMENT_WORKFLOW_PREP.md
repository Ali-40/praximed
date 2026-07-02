# Vapi to Appointment Workflow Integration Prep — PraxisMed Sprint 11

**Date:** 2026-07-02
**Sprint:** Sprint 11 (Module 86 complete — full local intake loop PASS)
**Status:** Local loop proven end-to-end. Next unknown: real Vapi tool-call payload from live assistant.

---

## 1. Purpose

This document prepares the next end-to-end integration loop for PraxisMed: a real or
simulated Vapi appointment capture creates an appointment request that appears live in
the clinic dashboard, where a staff member can then confirm it.

This is the core product loop: **AI intake → appointment request → staff review → confirmed**.

---

## 2. Target Flow

```
Vapi phone session ends → Vapi calls backend tool
        ↓
Backend: POST /vapi/tools/capture-appointment-request
  (machine auth: X-Vapi-Service-Name=vapi, X-Vapi-Scopes=vapi:tool)
  (body: clinic_ref, call_id, patient_name, reason, urgency_level)
        ↓
Backend: vapi_appointment_capture.capture_vapi_appointment_request()
  → ClinicConfigLoader.load(clinic_ref) → resolves clinic_id from config
  → appointment_requests INSERT (source=vapi, status=new, action_required=True)
  → clinic_notifications INSERT (via notification_router)
        ↓
Frontend: GET /appointment-requests?clinic_id=… (dashboard fetch on load)
        ↓
Staff: sees row with status=new, clicks Confirm
  → PATCH /appointment-requests/{id}/status {"status":"confirmed"}
        ↓
Row status: new → confirmed; Confirm button disappears
```

At the end of this loop, the dashboard shows a confirmed appointment request that
originated from a Vapi phone call — the full Vapi use case demonstrated.

---

## 3. Existing Proven Pieces

The following components have been individually proven and can be treated as reliable
building blocks for the integration loop.

| Piece | Where proven | Evidence |
|---|---|---|
| Real Vapi tunnel webhook → backend HTTP 200 | Module 57 | `docs/integrations/REAL_VAPI_TUNNEL_SMOKE_RESULTS.md` |
| Real n8n tunnel smoke passed | Module 58 | `docs/integrations/REAL_N8N_TUNNEL_SMOKE_RESULTS.md` |
| HMAC signature verification (Vapi and n8n) | Modules 46–47, 56–57 | `docs/integrations/LOCAL_SMOKE_RESULTS.md` |
| Machine auth (X-Vapi-* aliases accepted) | Modules 53–54 | `docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md` |
| Vapi payload adapter (`_adapt_vapi_payload`) | Module 56 | `backend/app/api/routes/vapi_webhooks.py` |
| Appointment request list in dashboard | Modules 68, 76, 77 | `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` |
| Appointment Confirm action in dashboard | Module 81 | `docs/runtime/APPOINTMENT_WORKFLOW_BROWSER_SMOKE_RESULTS.md` |
| JWT human auth (login → Bearer token → protected routes) | Modules 59–65, 67 | `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` |
| Audit logging on PHI mutations | Modules 42–44 | `docs/architecture/ARCHITECTURE_CHECKPOINT_04.md` |
| Tenant separation (clinic_id enforced) | Modules 37–38 | `docs/architecture/ARCHITECTURE_CHECKPOINT_03.md` |

---

## 4. Unknowns — Status After Module 86

| Unknown | Status |
|---|---|
| Does the capture route create `appointment_requests` rows from a Vapi-shaped payload? | **RESOLVED** — `POST /vapi/tools/capture-appointment-request` returns HTTP 200, creates row with `source=vapi`, `status=new`, `action_required=true`. |
| Does the real Vapi tool-call payload shape differ from the local fixture? | **RESOLVED (local)** — local fixture matches `VapiAppointmentCaptureRequest` schema. Real Vapi payload shape from a live assistant is the next unknown (Module 87). |
| Is `app.state.config_loader` initialized so the endpoint can resolve clinic config? | **RESOLVED** — Module 84 wires `ClinicConfigLoader(pool=app.state.db_pool)` in lifespan startup. |
| Does an appointment request appear in the dashboard without the manual seed? | **RESOLVED** — Module 86 browser smoke: Vapi-created row appeared in Appointments section without running seed script. |
| Can staff confirm a Vapi-sourced appointment request from the dashboard? | **RESOLVED** — Module 86: Confirm clicked on Vapi row → status "confirmed" → button disappeared. Staff confirmation boundary maintained. |
| Is a notification created when Vapi capture fires? | **PENDING** — `vapi_appointment_capture` calls `notification_router.create_appointment_request_notification`. Not surfaced in smoke output; can be confirmed via DB inspection. |
| Does the audit log record the integration path safely? | **PENDING** — audit logging is in place (Module 44); can be confirmed via DB audit log. |
| Does the nested Vapi-shape body reach the backend through ngrok and produce a dashboard row? | **RESOLVED** — Module 89: nested shape via ngrok → HTTP 200, rows appeared in dashboard, staff Confirm succeeded. |
| What is the exact required machine auth scope for the capture route? | **CONFIRMED** — `X-Vapi-Scopes: vapi:tool` (singular). `vapi:tools` (plural) is rejected with HTTP 403. |
| Are direct real Vapi assistant call logs captured? | **RESOLVED** — Module 90: real Vapi test assistant triggered `capture_appointment_request`; Vapi logs, ngrok POST, backend row creation, and staff Confirm all passed. See `docs/runtime/VAPI_DIRECT_ASSISTANT_TOOL_CALL_LOG_RESULTS.md`. |

---

## 5. Safety Constraints

The following constraints must be maintained throughout the integration loop work:

| Constraint | Enforcement |
|---|---|
| No real patient data | All test payloads must use `patient_name: "Local Test Patient"` (or equivalent fake) and the deterministic `clinic_id: 11111111-…` |
| Local fake clinic only | All requests must use the local seed clinic — `11111111-1111-1111-1111-111111111111` |
| Local secrets only | JWT_SECRET_KEY, VAPI_SIGNATURE_SECRET, and MACHINE_SERVICE_SECRET must be local-dev values; never committed |
| No auto calendar booking | The backend must not auto-create calendar events when an appointment request is confirmed — calendar booking remains a future manual staff step |
| No appointment confirmation by AI | The Confirm action requires a human (staff) click in the dashboard — AI must not trigger PATCH /appointment-requests/{id}/status |
| Staff confirmation required | Appointment request status transitions (`new → confirmed`) are staff-initiated only; AI captures requests, humans review and action them |

---

## 6. Module 83 Harness — What Was Built

**Sprint 11 / Module 83** built the smoke harness for the Vapi intake loop.

### Inspection findings

| Finding | Detail |
|---|---|
| Target endpoint | `POST /vapi/tools/capture-appointment-request` |
| Auth type | Machine auth only — `X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes: vapi:tool` |
| HMAC required | No — HMAC is only required for `POST /webhooks/vapi/call-event` |
| Bug found | `vapi_appointment_capture.py` called `config_loader.get()` and `config.clinic_id` — both wrong |
| Bug fixed | Changed to `config_loader.load()` and `config.tenant_id` to match `ClinicConfigLoader` API |
| Config gap | `main.py` does not initialize `app.state.config_loader` → endpoint returns HTTP 503 |
| Local clinic config | `backend/tenants/configs/11111111-1111-1111-1111-111111111111/clinic_config.json` exists on disk |

### Harness components

| File | Purpose |
|---|---|
| `docs/integrations/local_payloads/vapi_appointment_intake.json` | Fake Vapi capture payload with local clinic UUID and fake caller |
| `backend/scripts/smoke_vapi_appointment_intake.py` | Smoke script: sends POST with machine auth, prints result, handles 503 gracefully |
| `backend/tests/test_vapi_appointment_intake_harness_contract.py` | 10 static contract tests for payload, script, capture service fix, prep doc |

### Manual flow (once Module 84 wires config_loader)

```bash
# 1. Ensure seed data is fresh
python backend/scripts/seed_local_data.py

# 2. Start backend (with config_loader wired — Module 84 step)
uvicorn backend.app.main:app --reload --port 8000

# 3. Run the intake smoke
python backend/scripts/smoke_vapi_appointment_intake.py

# 4. Open dashboard and confirm
#    http://localhost:3000/dashboard → Appointments → Confirm
```

**This is LOCAL FAKE DATA ONLY.** Never use real patient data, real clinic IDs, or real secrets.

### What the harness does NOT do

- Does not auto-confirm appointment requests (staff action required)
- Does not create calendar events
- Does not require a real Vapi connection or ngrok tunnel
- Does not modify Vapi configuration or n8n workflows

---

## 7. Module 85 Smoke — Proven Command

```bash
# 1. Ensure seed data is fresh
python backend/scripts/seed_local_data.py

# 2. Start backend
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
export JWT_SECRET_KEY=local-dev-jwt-secret-key-change-in-production
uvicorn backend.app.main:app --reload --port 8000

# 3. Run the intake smoke (returns HTTP 200 after Module 85 fixes)
python backend/scripts/smoke_vapi_appointment_intake.py

# 4. Open dashboard and confirm (Module 86)
#    http://localhost:3000/dashboard → Appointments → new Vapi row → Confirm
```

**Result:** HTTP 200, appointment ID `509211a7-784e-4e45-90f1-d9af6f8d7981`, `status: new`, `source: vapi`.
**This is LOCAL FAKE DATA ONLY.** Never use real patient data, real clinic IDs, or real secrets.

## 8. Module 87 — Real Vapi Tool Payload Capture Plan

**Sprint 11 / Module 87** prepares the backend for testing against a real live Vapi
assistant tool-call payload.

### Shape gap identified (Module 87)

The current capture endpoint expects a **flat** body at the root level:
```json
{ "clinic_ref": "...", "call_id": "...", "patient_name": "..." }
```

A real Vapi server-URL tool-call sends a **nested** body:
```json
{
  "message": {
    "type": "tool-calls",
    "toolCallList": [{ "function": { "name": "...", "arguments": {...} } }],
    "call": { "id": "...", "customer": { "number": "..." } }
  }
}
```

Key differences:
- `clinic_ref` comes from `X-Vapi-Clinic-Id` header (machine auth), NOT in body
- `call_id` comes from `message.call.id`, NOT in arguments
- `patient_name` and other patient fields come from `function.arguments`

An adapter will be needed (similar to `_adapt_vapi_payload` in the webhook route, Module 56).

### Sample and inspector (Module 87 deliverables)

| File | Purpose |
|---|---|
| `docs/integrations/local_payloads/vapi_real_tool_payload_sample.json` | Sanitized fake sample of the real Vapi tool-call body shape |
| `backend/scripts/inspect_vapi_tool_payload.py` | Structural inspector — redacts patient values, detects shape, assesses compatibility |
| `backend/tests/test_vapi_real_tool_payload_prep_contract.py` | 17 static contract tests for sample, inspector, and prep docs |

### Manual real Vapi payload capture steps

1. Use a **test Vapi assistant only** — never a production assistant with real patients.
2. Configure the test assistant to call the `capture_appointment_request` tool with a fake patient.
3. Ask the assistant to book a fake appointment using a test phone call.
4. Capture the raw request body from backend access logs, ngrok inspector, or Vapi call logs.
5. Sanitize the captured payload — replace all patient names, phone numbers, transcript text
   with fake/local values. Remove any PII.
6. Save the sanitized payload as `docs/integrations/local_payloads/vapi_real_tool_payload_captured.json`.
7. Run the inspector:
   ```bash
   python backend/scripts/inspect_vapi_tool_payload.py \
     --payload-file docs/integrations/local_payloads/vapi_real_tool_payload_captured.json
   ```
8. Compare the shape against `VapiAppointmentCaptureRequest` schema.
9. If the shape matches the sample (nested `message.toolCallList`), implement an adapter.
10. **Staff confirmation boundary remains required** — no auto-confirm after any adapter changes.

### What not to do

- Never use real patient data, real patient names, or real phone numbers in any test payload
- Do not commit sanitized payloads with any residual PII
- Do not auto-confirm appointment requests in the adapter
- Do not modify machine auth or webhook signature verification

## 9. Module 88 — Adapter Implementation (COMPLETE)

**Sprint 11 / Module 88 — Real Vapi Tool Call Adapter** — COMPLETE (2026-07-02)

Shape gap RESOLVED. Adapter `adapt_vapi_tool_call_body` added to
`backend/app/modules/vapi/vapi_appointment_capture.py`.

What was done:
1. `adapt_vapi_tool_call_body(raw_body, machine_clinic_id)` added — detects nested shape and maps to flat fields.
2. `clinic_ref` always from `machine_clinic_id` (machine auth context) — patient-supplied clinic IDs ignored.
3. `call_id` from `message.call.id`, fallback to `toolCallList[0].id`.
4. `caller_phone` from `message.call.customer.number`.
5. Flat payloads (local harness) pass through unchanged.
6. Route changed from `body: VapiAppointmentCaptureRequest` → `request: Request`; adapter runs before Pydantic validation.
7. 14 new tests added — 9 adapter unit tests + 5 contract tests.
8. Full suite: 1625/1625 passed.

See: `docs/runtime/VAPI_REAL_TOOL_PAYLOAD_ADAPTER_RESULTS.md`

## 11. Future Frontend Opportunity — Doctor-Facing UI Polish

After Architecture Checkpoint 10, evaluate Fabel 5 / Claude-related frontend generation
tooling for a dedicated frontend UX sprint to make the doctor-facing dashboard more
premium, user-friendly, and impressive.

Goals:
- Higher-quality visual design for the clinic dashboard
- Better appointment workflow UI (richer row display, action feedback)
- Preserve all existing security, integration quality, and staff confirmation boundaries

This is a future quality opportunity — not part of Module 89 or the current intake loop work.

---

## 12. Integration Loop Status — Complete (Local/Test Environment)

As of Module 90, the full Vapi appointment intake loop is proven end-to-end for the
local/test environment:

| Layer | Status |
|---|---|
| Real Vapi assistant → tool call fired | PROVEN (Module 90) |
| ngrok → backend adapter → appointment created | PROVEN (Modules 88–90) |
| Appointment row visible in dashboard | PROVEN (Modules 86–90) |
| Staff Confirm → status confirmed → button gone | PROVEN (Modules 82–90) |
| Machine auth scope `vapi:tool` (singular) | CONFIRMED (Module 89) |
| No auto-confirmation at any layer | PROVEN throughout |

**Next focus options (Architecture Checkpoint 11):**
- A. Production deployment preparation (auth hardening, HTTPS, CI/CD)
- B. Appointment workflow expansion (Reject, Assign, Callback actions)
- C. Doctor-facing frontend UX sprint (evaluate Fabel 5 / Claude frontend tooling)

---

## 10. Recommended Next Module

**Sprint 11 / Module 89 — Real Vapi Live Tool-Call Smoke Evidence**

With the adapter in place, the next step is to confirm the nested shape works
with a real live Vapi assistant:

1. Set up a test Vapi assistant configured to call `capture_appointment_request` as a server-URL tool.
2. Start an ngrok tunnel to expose the local backend.
3. Make a test call with a fake patient name.
4. Confirm the backend receives the nested payload, adapter fires, HTTP 200 returned.
5. Confirm the appointment request appears in the dashboard with `source=vapi`, `status=new`.
6. Run the inspector on the captured payload and verify COMPATIBLE or adjust adapter.
7. Document smoke evidence.

Safety constraints (unchanged):
- Use a test Vapi assistant only — no production assistant with real patients.
- Use fake patient data only.
- Do not auto-confirm appointment requests.
- Do not commit real secrets.
