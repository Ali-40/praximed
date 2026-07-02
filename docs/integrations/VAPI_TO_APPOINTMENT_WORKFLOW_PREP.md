# Vapi to Appointment Workflow Integration Prep — PraxisMed Sprint 11

**Date:** 2026-07-02
**Sprint:** Sprint 11 (Module 83 harness built)
**Status:** Harness created — config_loader wiring pending (Module 84)

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

## 4. Unknowns — Status After Module 83 Inspection

| Unknown | Status after Module 83 |
|---|---|
| Does the capture route create `appointment_requests` rows from a Vapi-shaped payload? | **RESOLVED** — the dedicated tool endpoint `POST /vapi/tools/capture-appointment-request` accepts the payload directly. Bug fixed: `config_loader.get`→`load`, `config.clinic_id`→`tenant_id`. |
| Does the real Vapi tool-call payload shape differ from the local fixture? | **RESOLVED** — the tool endpoint uses `VapiAppointmentCaptureRequest` (structured body), not the webhook's raw Vapi message shape. Local fixture matches the schema. |
| Does an appointment request appear in the dashboard without the manual seed? | **PENDING** — blocked by config_loader not wired in `main.py`. Once Module 84 wires it, `smoke_vapi_appointment_intake.py` will create a live row. |
| Is a notification created when Vapi capture fires? | **PENDING** — `vapi_appointment_capture` does call `notification_router.create_appointment_request_notification`; will be verified in Module 84 smoke. |
| Does the audit log record the integration path safely? | **PENDING** — audit logging for the tool route is in place (Module 44); will be confirmed in Module 84 smoke. |

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

## 7. Recommended Next Module

**Sprint 11 / Module 84 — Vapi Intake to Dashboard Browser Smoke**

Wire `app.state.config_loader` in `main.py` so the capture endpoint can resolve
the clinic config, then run `smoke_vapi_appointment_intake.py` against the live local
backend and document evidence that:

1. `POST /vapi/tools/capture-appointment-request` returns HTTP 200.
2. An `appointment_requests` row with `status=new` is created.
3. The row appears in the dashboard without running the seed script.
4. Staff can click Confirm and see the status update to "confirmed".

Config loader wiring (the missing step):

```python
# In backend/app/main.py lifespan startup:
from backend.app.core.config_loader import ClinicConfigLoader
app.state.config_loader = ClinicConfigLoader(pool=pool)
```

### What Module 84 should not do

- Use real patient data, real clinic credentials, or live Vapi
- Auto-confirm appointment requests or create calendar events
- Require ngrok or an external tunnel
