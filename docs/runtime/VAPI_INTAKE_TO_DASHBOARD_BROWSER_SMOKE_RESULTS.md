# Vapi Intake to Dashboard Browser Smoke Results — PraxisMed Sprint 11 / Module 86

**Date:** 2026-07-02
**Verdict:** PASS

---

## 1. Purpose

This document records evidence that the full local Vapi intake loop works end-to-end:
a simulated Vapi appointment capture creates an appointment request that appears in the
clinic dashboard, where a staff member can then confirm it.

This closes the core product loop for local demonstration:
**AI intake → appointment request (source: vapi) → staff review → confirmed.**

This builds on:
- `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_SMOKE_RESULTS.md` (Modules 84–85 — backend smoke)
- `docs/runtime/APPOINTMENT_WORKFLOW_BROWSER_SMOKE_RESULTS.md` (Module 82 — Confirm action)

---

## 2. Environment

| Component | Details |
|---|---|
| PostgreSQL | Local Docker container — `docker-compose.postgres.yml` (port 5433) |
| Backend | `uvicorn backend.app.main:app --reload --port 8000` on `http://127.0.0.1:8000` |
| Frontend | `npm run dev` on `http://localhost:3000` |
| JWT_SECRET_KEY | Local-dev value only — not committed; not used in production |
| CORS | `CORSMiddleware` allows `http://localhost:3000` and `http://127.0.0.1:3000` |
| Tunnel | None — no ngrok or external tunnel |
| Data | Fake/local only — no real patient data, no real Vapi credentials |
| Seed data | `backend/scripts/seed_local_data.py` (clinic `11111111-1111-1111-1111-111111111111`) |

---

## 3. Steps Completed

| Step | Action | Result |
|---|---|---|
| 1. Start PostgreSQL | `docker-compose -f docker-compose.postgres.yml up -d` | Container running, port 5433 healthy |
| 2. Start backend | `uvicorn backend.app.main:app --reload --port 8000` | Backend running; `app.state.config_loader` initialised |
| 3. Start frontend | `npm run dev` in `frontend/` | Next.js dev server on `http://localhost:3000` |
| 4. Run smoke harness | `python backend/scripts/smoke_vapi_appointment_intake.py` | HTTP 200 — appointment request created |
| 5. Browser login | Opened `http://localhost:3000`, filled login form with local-dev credentials | Redirect to `/dashboard` |
| 6. Dashboard load | Appointments section rendered | New Vapi-created row visible alongside seed row |
| 7. Verify new row | Checked row content | Source: vapi, patient: "Local Vapi Test Caller", status badge: "new", Confirm button visible |
| 8. Click Confirm | Clicked Confirm on the Vapi row | Button disabled; label changed to "Confirming…" while PATCH was in flight |
| 9. Observe result | PATCH completed | Status badge changed from "new" to "confirmed"; Confirm button disappeared |
| 10. Verify stability | Checked other dashboard sections | Patients (1), Notifications (1), Consultations (1) all remained stable |
| 11. Verify seed row | Checked seed appointment row | Seed row (`55555555-…`) unaffected — status unchanged |

---

## 4. Evidence

### Harness Output (smoke_vapi_appointment_intake.py)

```
HTTP status:  200
Response:
  "ok": true,
  "request": {
    "id": "509211a7-784e-4e45-90f1-d9af6f8d7981",
    "clinic_id": "11111111-1111-1111-1111-111111111111",
    "source": "vapi",
    "source_ref": "local-vapi-intake-call-1",
    "patient_name": "Local Vapi Test Caller",
    "status": "new",
    "urgency_level": "normal",
    "action_required": true
  }
```

### Vapi Appointment Row — Before Confirm

| Field | Observed value |
|---|---|
| Patient name | "Local Vapi Test Caller" |
| Source | "vapi" |
| Status badge | "new" (blue) |
| Urgency | "normal" |
| Confirm button | Visible and enabled |

### During Confirm (in-flight)

| Field | Observed value |
|---|---|
| Confirm button | Disabled — label showed "Confirming…" |
| Row | No layout shift; other content stable |

### Vapi Appointment Row — After Confirm

| Field | Observed value |
|---|---|
| Status badge | "confirmed" (green) |
| Confirm button | Gone — not rendered for confirmed rows |
| Error message | None — action succeeded without error |

### Other Dashboard Sections (stable throughout)

| Section | Stable? |
|---|---|
| Patients (1) | Yes — "Local Test Patient" unchanged |
| Notifications (1) | Yes — "Local Test Notification" unchanged |
| Consultations (1) | Yes — "Local Test Consultation Session" unchanged |
| Seed appointment (`55555555-…`) | Yes — status unchanged |

---

## 5. What This Proves

| Claim | Status |
|---|---|
| `smoke_vapi_appointment_intake.py` returns HTTP 200 | PROVEN |
| Appointment request created with `source=vapi` | PROVEN |
| Appointment request created with `status=new` — not auto-confirmed by AI | PROVEN |
| `action_required=true` — staff review required | PROVEN |
| Vapi-created row appears in dashboard without running the seed script | PROVEN |
| Confirm button visible on Vapi-created row | PROVEN |
| Clicking Confirm triggers `PATCH /appointment-requests/{id}/status` with Bearer JWT | PROVEN |
| Status badge updates from "new" to "confirmed" after Confirm | PROVEN |
| Confirm button disappears from confirmed rows | PROVEN |
| Other dashboard sections remain stable after Confirm | PROVEN |
| Staff confirmation boundary maintained — AI does not auto-confirm | PROVEN |
| Local Vapi-like intake loop is viable: intake → dashboard row → staff confirm | PROVEN |

---

## 6. What This Does Not Prove

| Gap | Detail |
|---|---|
| Real Vapi tool-call payload from a live assistant | Harness uses a local fake JSON payload — no live Vapi connection |
| Real Vapi credentials or production Vapi configuration | Not used; no secrets |
| Production deployment | Local-dev only — no production build, HTTPS, or CI/CD |
| Calendar event creation | No calendar integration on Confirm; future module |
| Staff scheduling logic | Confirmation changes status only; no calendar booking |
| Patient notification on Confirm | Not implemented; future module |
| Reject, Assign, Callback, or Archive actions | Only Confirm implemented (Module 81) |
| Token refresh or httpOnly cookie storage | JWT in sessionStorage — local-dev only |
| Real patient data handling | All data is deterministic fake (local-dev) |

---

## 7. Result

**PASS** — The local Vapi intake to dashboard confirmation loop works end-to-end:

1. `smoke_vapi_appointment_intake.py` sends a simulated Vapi capture → HTTP 200
2. Appointment request appears in dashboard with `source=vapi`, `status=new`
3. Staff clicks Confirm → status becomes "confirmed", button disappears
4. No auto-confirmation by AI; staff confirmation boundary maintained throughout

The core product loop — **AI intake → appointment request → staff review → confirmed** —
is now locally demonstrated without a real Vapi connection or ngrok tunnel.

---

## 8. Module 87 — Real Vapi Payload Prep

**Sprint 11 / Module 87** prepares inspection tooling for testing against a live Vapi
assistant tool-call payload. The local harness result above remains PASS and is unchanged.

Module 87 deliverables:
- Sanitized sample of the real Vapi tool-call body shape (`vapi_real_tool_payload_sample.json`)
- Inspector script (`inspect_vapi_tool_payload.py`) — structural summary, redacts patient values
- 17 static contract tests for sample, inspector, and prep docs
- Prep doc updated with shape gap analysis and manual capture steps

Shape gap identified: a real Vapi tool call nests arguments in
`message.toolCallList[0].function.arguments` while the current capture endpoint expects
flat fields at root level. An adapter will be needed (Module 88).
