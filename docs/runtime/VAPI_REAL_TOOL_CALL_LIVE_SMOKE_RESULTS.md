# Vapi/ngrok Appointment Intake Dashboard Evidence — PraxisMed Sprint 11 / Module 89

**Date:** 2026-07-03
**Verdict:** PASS — local/ngrok/dashboard path PASS; direct real Vapi assistant log evidence: PASS (Module 90)

---

## 1. Purpose

This document records evidence that the Vapi appointment intake loop works end-to-end
via the ngrok path: a nested Vapi-shaped tool-call body reaches the backend through an
ngrok tunnel, the adapter normalises it, an appointment request is created, it appears in
the staff dashboard, and staff can confirm it.

This builds on:
- `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_BROWSER_SMOKE_RESULTS.md` (Module 86 — local flat harness)
- `docs/runtime/VAPI_REAL_TOOL_PAYLOAD_ADAPTER_RESULTS.md` (Module 88 — adapter implementation)

**Accuracy note:** The evidence below reflects the local/ngrok intake path and
browser dashboard confirmation. Direct real Vapi assistant call logs were not captured
in this module. That exact evidence item is marked PENDING.

---

## 2. Environment

| Component | Details |
|---|---|
| PostgreSQL | Local Docker container — `docker-compose.postgres.yml` (port 5433) |
| Backend | `uvicorn backend.app.main:app --host 127.0.0.1 --port 8000` |
| Frontend | `npm run dev` (NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000) on `http://localhost:3000` |
| ngrok tunnel | `https://subsiding-visitor-family.ngrok-free.dev` |
| Tool endpoint | `POST https://subsiding-visitor-family.ngrok-free.dev/vapi/tools/capture-appointment-request` |
| Machine auth headers | `X-Vapi-Service-Name: vapi`, `X-Vapi-Clinic-Id: 11111111-…`, `X-Vapi-Scopes: vapi:tool` |
| Scope (confirmed) | `vapi:tool` — singular; `vapi:tools` plural is rejected with HTTP 403 |
| JWT_SECRET_KEY | Local-dev value only — not committed |
| Data | Fake/local only — no real patient data, no real Vapi credentials |
| Seed data | `backend/scripts/seed_local_data.py` |

---

## 3. Steps Completed

| Step | Action | Result |
|---|---|---|
| 1. Start PostgreSQL | `docker-compose -f docker-compose.postgres.yml up -d` | Container running, port 5433 healthy |
| 2. Seed data | `python backend/scripts/seed_local_data.py` | Seed clinic + user + base rows created |
| 3. Start backend | `uvicorn backend.app.main:app --host 127.0.0.1 --port 8000` | Backend running; `/health` returned `ok` |
| 4. Start frontend | `npm run dev` in `frontend/` | Next.js dev server on `http://localhost:3000` |
| 5. Start ngrok | `ngrok http 8000` | Tunnel `https://subsiding-visitor-family.ngrok-free.dev` live |
| 6. Verify tunnel | `curl` nested Vapi-shape POST through ngrok | HTTP 200 — appointment row created (`source=vapi`, `status=new`) |
| 7. Browser login | Opened `http://localhost:3000`, filled login form | Redirect to `/dashboard` |
| 8. Dashboard load | Appointments section rendered | 4 appointment rows visible after intake tests |
| 9. Verify rows | Checked row content | Included: "Local Ngrok Test Caller", "Local Vapi Test Caller" (×2), "Local Test Patient" |
| 10. Click Confirm | Clicked Confirm on the newest Vapi/ngrok-created row | Button disabled; label changed to "Confirming…" while PATCH in flight |
| 11. Observe result | PATCH completed | Status badge changed from "new" to "confirmed"; Confirm button disappeared |
| 12. Verify stability | Checked other dashboard sections | Patients, Notifications, Consultations all rendered; Logout visible; local-demo footer visible |

---

## 4. Evidence

### 4.1 Nested Vapi-shape via ngrok — HTTP 200

Request body shape (sanitized):
```json
{
  "message": {
    "type": "tool-calls",
    "toolCallList": [{
      "id": "toolu_ngrok_test_001",
      "function": {
        "name": "capture_appointment_request",
        "arguments": {
          "patient_name": "Local Ngrok Test Caller",
          "reason": "Ngrok connectivity test — fake patient",
          "urgency_level": "normal"
        }
      }
    }],
    "call": {
      "id": "ngrok-test-call-001",
      "customer": { "number": "+43000000099" }
    }
  }
}
```

Response (sanitized):
```
HTTP 200
{
  "ok": true,
  "source": "vapi",
  "status": "new",
  "action_required": true,
  "source_ref": "ngrok-test-call-001",
  "patient_phone": "+43000000099"
}
```

Adapter behaviour confirmed:
- `clinic_ref` resolved from `X-Vapi-Clinic-Id` machine auth header (not from body)
- `call_id` resolved from `message.call.id`
- `caller_phone` resolved from `message.call.customer.number`
- `patient_name` resolved from `function.arguments.patient_name`

### 4.2 Dashboard — Appointment Rows After Intake

| Row | Patient | Source | Status | Confirm button |
|---|---|---|---|---|
| Seed row | Local Test Patient | (seed) | (varies) | — |
| Intake row 1 | Local Vapi Test Caller | vapi | new → confirmed | Visible, then gone |
| Intake row 2 | Local Vapi Test Caller | vapi | new | Visible |
| Intake row 3 | Local Ngrok Test Caller | vapi | new | Visible |

### 4.3 After Confirm

| Field | Observed |
|---|---|
| Status badge | "confirmed" (green) |
| Confirm button | Disappeared — not rendered for confirmed rows |
| Error message | None |
| Other sections | Patients (1), Notifications (1), Consultations (1) — all stable |
| Logout | Visible |
| Local-demo footer | Visible |

### 4.4 Real Vapi Assistant Call Logs

**Status: PASS (Module 90)**

Direct real Vapi assistant call logs were captured in Module 90. The real test assistant
triggered `capture_appointment_request`, Vapi tool logs showed success, ngrok confirmed
the POST, and the dashboard row was confirmed by staff.

See: `docs/runtime/VAPI_DIRECT_ASSISTANT_TOOL_CALL_LOG_RESULTS.md`

---

## 5. Accuracy Statement

| Claim | Evidence status |
|---|---|
| Nested Vapi-shape through ngrok → HTTP 200 | PROVEN (curl test, Section 4.1) |
| Adapter extracts clinic_ref / call_id / caller_phone correctly | PROVEN (response body confirmed) |
| Appointment request created with source=vapi, status=new, action_required=true | PROVEN |
| Vapi/ngrok-created rows appear in staff dashboard | PROVEN (Section 4.2) |
| Staff Confirm action: status new → confirmed, button disappears | PROVEN (Section 4.3) |
| Other dashboard sections remain stable | PROVEN (Section 4.3) |
| No auto-confirmation by AI | PROVEN (status=new until staff clicks Confirm) |
| Real Vapi assistant call logs captured | **PASS** — Module 90 |

---

## 6. Security and Safety

| Constraint | Status |
|---|---|
| No real patient data | MAINTAINED — all names/phones are local fake values |
| No auto-confirmation | MAINTAINED — status=new until staff clicks Confirm |
| Staff confirmation boundary preserved | MAINTAINED — PATCH /appointment-requests/{id}/status requires staff Bearer JWT |
| No calendar booking on Confirm | MAINTAINED — future module |
| No secrets or raw payloads in docs | MAINTAINED — call_id and patient values are sanitized fakes |
| Clinic_ref always from machine auth | MAINTAINED — adapter enforces this |
| Machine auth scope | `vapi:tool` — singular required; plural rejected |

---

## 7. What This Proves

| Claim | Status |
|---|---|
| Nested Vapi-shape tool-call body is accepted by the adapted capture route | PROVEN |
| `adapt_vapi_tool_call_body` correctly normalises the nested shape | PROVEN |
| Appointment requests created via ngrok path appear in the staff dashboard | PROVEN |
| Staff can confirm Vapi-sourced appointment requests from the dashboard | PROVEN |
| AI-intake → appointment request → staff review → confirmed loop is viable locally | PROVEN |
| Machine auth scope `vapi:tool` (singular) is the correct header value | CONFIRMED |

---

## 8. What Remains

| Gap | Detail |
|---|---|
| Direct real Vapi assistant call logs | Not captured in this module — PENDING |
| Production deployment | Local-dev only |
| Production Vapi assistant configuration | Test assistant only; no production config |
| Production auth / httpOnly cookie session | JWT in sessionStorage — local-dev only |
| Calendar handoff on Confirm | No calendar event created — future module |
| Reject, Assign, Callback, Archive actions | Only Confirm implemented (Module 81) |
| Real patient data handling | All data is deterministic fake |
| Architecture Checkpoint 10 | Recommended next step |

---

## 9. Result

**PASS** — Local/ngrok/dashboard path end-to-end:

1. Nested Vapi-shape body sent through ngrok → HTTP 200
2. Adapter normalised shape: `clinic_ref` from machine auth, `call_id` from `message.call.id`
3. Appointment rows visible in dashboard with `source=vapi`, `status=new`
4. Staff clicked Confirm → status "confirmed", button disappeared
5. No auto-confirmation; no calendar booking; no real data; security boundaries maintained

**Real Vapi assistant log evidence: PENDING** — not captured in this module.
