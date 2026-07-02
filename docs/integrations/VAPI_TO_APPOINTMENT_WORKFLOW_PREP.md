# Vapi to Appointment Workflow Integration Prep — PraxisMed Sprint 11

**Date:** 2026-07-02
**Sprint:** Sprint 11 (Module 82 prep)
**Status:** Planning — no code changes in this document

---

## 1. Purpose

This document prepares the next end-to-end integration loop for PraxisMed: a real or
simulated Vapi appointment capture creates an appointment request that appears live in
the clinic dashboard, where a staff member can then confirm it.

This is the core product loop: **AI intake → appointment request → staff review → confirmed**.

---

## 2. Target Flow

```
Vapi call event / tool request
        ↓
Backend: POST /webhooks/vapi/call-event
         or POST /vapi/tools/suggest-slots / check-availability
        ↓
Backend: appointment_requests INSERT (via vapi_appointment_capture module)
        ↓
Frontend: GET /appointment-requests?clinic_id=… (dashboard fetch on load)
        ↓
Staff: clicks Confirm → PATCH /appointment-requests/{id}/status
        ↓
Row status: new → confirmed
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

## 4. Unknowns to Verify Next

The following questions are unproven and block a confident end-to-end integration demo.

| Unknown | Why it matters |
|---|---|
| Does the current Vapi appointment capture route create `appointment_requests` rows from a real Vapi payload shape? | The backend adapter (Module 56) maps `message.type` → `event_type`, but the `vapi_appointment_capture` module may expect fields (`clinic_id`, `patient_name`, `reason`) that are not present in a real Vapi body |
| Does the real Vapi tool-call payload shape differ from the local fixture? | `POST /vapi/tools/suggest-slots` and `check-availability` use machine auth + scope checks; real Vapi may omit headers the local smoke fixture included |
| Does an appointment request appear in the dashboard without the manual seed? | Only the deterministic seed script has been used so far; no live appointment request has been created via Vapi and fetched from the dashboard |
| Is a notification created as expected when Vapi capture fires? | `vapi_appointment_capture` was spec'd to create a `clinic_notification`; this has not been verified against a real Vapi call |
| Does the audit log record the full Vapi integration path safely? | Audit logging for Vapi webhook and tool routes was added in Module 44; not yet verified with a real clinic_id |

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

## 6. Recommended Next Module

**Sprint 11 / Module 83 — Vapi Intake to Appointment Dashboard Smoke Harness**

Build a local/test harness or fixture-driven smoke path that proves a Vapi-like
appointment capture creates a dashboard-visible appointment request without using real
patient data or a live Vapi connection.

### Suggested approach

1. **Inspect `vapi_appointment_capture`** — read `backend/app/modules/vapi/vapi_appointment_capture.py`
   and the route that calls it to understand what fields it expects from the Vapi payload.

2. **Add a static contract test** that asserts the capture module reads `patient_name`,
   `reason`, and `clinic_id` from the adapted payload — and does not require real Vapi
   credentials or a live call.

3. **Add a local fixture smoke script** (optional, not committed as a pytest test):
   - Constructs a fake Vapi-shaped payload (using the same shape that Module 56 adapter produces)
   - Signs it with the local HMAC secret
   - POSTs to `POST /webhooks/vapi/call-event`
   - Verifies the HTTP 200 response
   - Queries `GET /appointment-requests?clinic_id=…` to confirm the new row appeared

4. **Verify end-to-end**:
   - New appointment request appears in dashboard without running seed script
   - Staff can click Confirm on the new row
   - Full loop proven without a real Vapi phone call

### What Module 83 should not do

- Use real patient data, real phone numbers, or real clinic credentials
- Modify Vapi configuration or n8n workflows
- Auto-confirm or auto-create calendar events
- Require a live Vapi connection or ngrok tunnel
