# Direct Real Vapi Assistant Tool-Call Log Capture — PraxisMed Sprint 11 / Module 90

**Date:** 2026-07-03
**Verdict:** PASS

---

## 1. Purpose

This document records evidence that a real live Vapi test assistant successfully
triggered the `capture_appointment_request` server tool, the backend adapter handled
the nested tool-call shape, an appointment request was created, and staff confirmed
it from the dashboard.

This closes the last evidence gap identified in Architecture Checkpoint 10:
*direct real Vapi assistant call logs not yet captured.*

This builds on:
- `docs/runtime/VAPI_REAL_TOOL_CALL_LIVE_SMOKE_RESULTS.md` (Module 89 — ngrok/curl path)
- `docs/runtime/VAPI_REAL_TOOL_PAYLOAD_ADAPTER_RESULTS.md` (Module 88 — adapter implementation)

---

## 2. Environment

| Component | Details |
|---|---|
| Vapi assistant | Real test assistant — not a production assistant |
| Backend | `uvicorn backend.app.main:app --host 127.0.0.1 --port 8000` (local) |
| Frontend | `npm run dev` on `http://localhost:3000` (local) |
| ngrok tunnel | HTTPS tunnel forwarding to `http://127.0.0.1:8000` |
| Tool endpoint | `POST /vapi/tools/capture-appointment-request` |
| Machine auth headers | `X-Vapi-Service-Name: vapi`, `X-Vapi-Clinic-Id: 11111111-…`, `X-Vapi-Scopes: vapi:tool` |
| Scope (confirmed) | `vapi:tool` — singular |
| Data | Fake/local only — no real patient names, phones, or clinic credentials |

---

## 3. Steps Completed

| Step | Action | Result |
|---|---|---|
| 1. Stack running | Backend `/health`, frontend `http://localhost:3000`, ngrok tunnel active | All three up and responding |
| 2. Vapi tool configured | Test assistant `capture_appointment_request` tool pointing at ngrok URL with machine auth headers | Confirmed in Vapi dashboard |
| 3. Test call made | Called test assistant with fake appointment request prompt | Assistant processed the request |
| 4. Vapi tool call fired | Vapi assistant called `capture_appointment_request` server tool | Vapi call/tool logs showed successful tool execution |
| 5. ngrok observed | ngrok inspector showed `POST /vapi/tools/capture-appointment-request` | Successful status |
| 6. Backend received | Backend processed the nested Vapi tool-call body; adapter fired | Appointment request created |
| 7. Dashboard verified | Opened `http://localhost:3000`, logged in | Vapi-created row visible in Appointments section |
| 8. Staff Confirm | Clicked Confirm on the Vapi-created row | Button disabled; "Confirming…" while PATCH in flight |
| 9. Confirmation complete | PATCH completed | Status badge changed to "confirmed"; Confirm button disappeared |
| 10. Stability check | Checked other dashboard sections | Patients, Notifications, Consultations all stable; Logout visible |

---

## 4. Evidence

### 4.1 Vapi Assistant Tool Call

| Signal | Observed |
|---|---|
| Vapi call/tool logs | Successful tool execution — `capture_appointment_request` called |
| Tool name invoked | `capture_appointment_request` |
| Tool result | Success (2xx) — backend returned the capture response |
| Vapi tool configuration | `X-Vapi-Service-Name: vapi`, `X-Vapi-Clinic-Id: 11111111-…`, `X-Vapi-Scopes: vapi:tool` |

### 4.2 ngrok and Backend

| Signal | Observed |
|---|---|
| ngrok request | `POST /vapi/tools/capture-appointment-request` — successful status |
| Backend response | Appointment request created with `source=vapi`, `status=new`, `action_required=true` |
| Adapter fired | Nested `message.toolCallList` shape normalised by `adapt_vapi_tool_call_body` |
| `clinic_ref` | Resolved from `X-Vapi-Clinic-Id` machine auth header — not from body arguments |

### 4.3 Dashboard — Row Visible

| Field | Observed |
|---|---|
| Vapi-created row | Visible in Appointments section |
| Source | `vapi` |
| Status | `new` (staff-reviewable) |
| Action required | `true` |
| Confirm button | Visible and enabled |

### 4.4 Staff Confirmation

| Field | Observed |
|---|---|
| In-flight state | Confirm button disabled; label "Confirming…" |
| After Confirm | Status badge → "confirmed" (green) |
| Confirm button | Disappeared — not rendered for confirmed rows |
| Error | None |

### 4.5 Other Dashboard Sections (stable throughout)

| Section | Status |
|---|---|
| Patients | Rendered and stable |
| Notifications | Rendered and stable |
| Consultations | Rendered and stable |
| Logout | Visible |
| Local-demo footer | Visible |

---

## 5. Security and Safety

| Constraint | Status |
|---|---|
| Fake/local data only | MAINTAINED — no real patient names or phone numbers |
| `clinic_id` from machine auth header | MAINTAINED — `X-Vapi-Clinic-Id` enforced by adapter; patient-supplied clinic_ref in arguments ignored |
| No patient-controlled tenant selection | MAINTAINED — machine auth context always overrides |
| No raw payload or secrets documented | MAINTAINED — no call IDs, phone numbers, or transcripts in this doc |
| No auto-confirmation | MAINTAINED — status remained `new` until staff clicked Confirm |
| No calendar booking | MAINTAINED — Confirm updates status only; no calendar event created |
| Real test assistant only | MAINTAINED — no production assistant with real patients |

---

## 6. What This Proves

| Claim | Status |
|---|---|
| Real live Vapi test assistant triggers `capture_appointment_request` server tool | PROVEN |
| Nested Vapi tool-call body shape handled by `adapt_vapi_tool_call_body` adapter | PROVEN |
| Backend creates appointment request with `source=vapi`, `status=new`, `action_required=true` | PROVEN |
| Machine auth headers accepted from real Vapi assistant | PROVEN |
| `clinic_ref` resolved from machine auth — not from patient or assistant-supplied arguments | PROVEN |
| Appointment request appears in staff dashboard after real Vapi tool call | PROVEN |
| Staff confirmation boundary maintained — AI does not auto-confirm | PROVEN |
| Staff Confirm action succeeds: `new` → `confirmed`, button disappears | PROVEN |
| Full integration loop end-to-end: real Vapi assistant → ngrok → adapter → DB → dashboard → staff Confirm | PROVEN |

---

## 7. What Remains

| Gap | Detail |
|---|---|
| Production Vapi assistant configuration | Test assistant only; no production secrets or config |
| Production deployment | Local-dev only; no HTTPS, CI/CD, or hosting |
| Production auth/session storage | JWT in `sessionStorage` — local-dev only; httpOnly cookie path not built |
| Calendar handoff on Confirm | No calendar event created — future module |
| Patient notification on Confirm | Not implemented — future module |
| Reject / Assign / Callback / Archive actions | Only Confirm implemented |
| Doctor-facing UI/UX polish | Future sprint — Fabel 5 / Claude frontend tooling evaluation |
| Real patient data handling | All data is deterministic fake |

---

## 8. Result

**PASS** — Direct real Vapi assistant tool-call log capture:

1. Real Vapi test assistant called `capture_appointment_request` server tool
2. Vapi call logs and ngrok confirmed successful POST
3. Backend adapter handled nested shape; appointment request created
4. Row appeared in staff dashboard with `source=vapi`, `status=new`
5. Staff clicked Confirm → status "confirmed", button disappeared
6. No auto-confirmation; no calendar booking; no real data; security boundaries maintained

The local integration loop — **real Vapi assistant → ngrok → adapter → DB → dashboard → staff Confirm** — is now fully proven for the test environment.
