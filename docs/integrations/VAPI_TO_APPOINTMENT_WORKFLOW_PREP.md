# Vapi to Appointment Workflow Integration Prep — PraxisMed Sprint 11

**Date:** 2026-07-02
**Sprint:** Sprint 11 (Module 85 complete — smoke PASS, HTTP 200)
**Status:** Backend intake proven. Remaining: browser confirm loop (Module 86).

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

## 4. Unknowns — Status After Module 85

| Unknown | Status |
|---|---|
| Does the capture route create `appointment_requests` rows from a Vapi-shaped payload? | **RESOLVED** — `POST /vapi/tools/capture-appointment-request` returns HTTP 200 and creates a row. Module 83 fixed capture service bugs; Module 84 wired config_loader; Module 85 fixed UUID validation and DB-error fallback. |
| Does the real Vapi tool-call payload shape differ from the local fixture? | **RESOLVED** — tool endpoint uses `VapiAppointmentCaptureRequest` (structured body). Local fixture matches the schema. |
| Is `app.state.config_loader` initialized so the endpoint can resolve clinic config? | **RESOLVED** — Module 84 wires `ClinicConfigLoader(pool=app.state.db_pool)` in lifespan startup. |
| Does an appointment request appear in the dashboard without the manual seed? | **PENDING** — intake smoke returns HTTP 200, row created in DB. Browser dashboard confirmation is Module 86. |
| Is a notification created when Vapi capture fires? | **PENDING** — `vapi_appointment_capture` calls `notification_router.create_appointment_request_notification`; not verified in smoke output. Will be confirmed in Module 86 browser check. |
| Does the audit log record the integration path safely? | **PENDING** — audit logging is in place (Module 44); will be confirmed in Module 86 browser check. |

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

## 8. Recommended Next Module

**Sprint 11 / Module 86 — Vapi Intake to Dashboard Browser Smoke Evidence**

With the backend intake proven, the remaining step is the browser confirm loop:

1. Open `http://localhost:3000/dashboard`.
2. Confirm the new Vapi-created row appears in the Appointments section (distinct from the seed row).
3. Click Confirm — status updates to "confirmed".
4. Document evidence in `docs/runtime/VAPI_INTAKE_DASHBOARD_SMOKE_RESULTS.md`.

### What Module 86 should not do

- Use real patient data, real clinic credentials, or live Vapi
- Auto-confirm appointment requests or create calendar events
- Require ngrok or an external tunnel
- Modify backend routes, auth, or seed data
