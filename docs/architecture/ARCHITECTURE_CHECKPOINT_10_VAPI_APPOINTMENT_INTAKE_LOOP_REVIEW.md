# Architecture Checkpoint 10 — Vapi Appointment Intake Loop Review

**Date:** 2026-07-03
**Sprint:** Sprint 11 complete (Modules 81–89)
**Backend tests:** 1625/1625 passed
**Status:** Local/ngrok Vapi intake loop proven end-to-end. One evidence gap remains: direct real Vapi assistant call logs.

---

## 1. Current Status

Sprint 11 closed the full local appointment intake loop:
**Vapi/ngrok tool call → backend adapter → appointment request → staff dashboard → Confirm action → confirmed.**

The stack works locally and through an ngrok tunnel. The nested real Vapi tool-call body shape
is handled by an adapter. Staff confirmation is browser-confirmed. No auto-confirmation by AI
at any layer. The remaining open item before closing this loop completely is capturing direct
real Vapi assistant call logs from a live assistant — the local/ngrok path is proven but the
assistant-triggered path has not been captured with logs.

---

## 2. Sprint 11 Completed Work

| Module | Description | Key Outcome |
|---|---|---|
| 81 | Appointment Confirm UI — `confirmAppointmentRequest` helper + Confirm button on `status === 'new'` rows | Frontend can mutate appointment status via `PATCH`; 10 contract tests |
| 82 | Appointment workflow browser smoke | Staff login → Confirm → status "confirmed" → button gone; PASS in real browser |
| 83 | Vapi intake smoke harness; bug fix (`config_loader.get` → `config_loader.load`) | Harness + payload + 10 contract tests; `main.py` gap identified |
| 84 | `app.state.config_loader` wired in lifespan | HTTP 503 resolved; new HTTP 500 (UUID issue) found; 9 lifespan tests |
| 85 | UUID compatibility fix (regex → `uuid.UUID()` parser); DB-error fallback in `_load_db_config` | Live smoke returned HTTP 200; appointment created; 5 new config loader tests |
| 86 | Vapi intake to dashboard browser smoke evidence | Full local loop: harness → row in dashboard → staff Confirm; PASS |
| 87 | Real Vapi payload shape analysis; inspector script; sanitized sample | Shape gap identified (nested vs flat); 17 contract tests; inspector script |
| 88 | `adapt_vapi_tool_call_body` adapter; route changed to `request: Request` | Both flat and nested shapes handled; 14 new tests; 1625/1625 |
| 89 | ngrok/dashboard evidence; `vapi_real_tool_payload_captured.json` archived | HTTP 200 through ngrok; 4 rows in dashboard; Confirm passed; scope confirmed |

**Tests added in Sprint 11:** 65 new tests (1560 → 1625).

---

## 3. Proven Capabilities

### 3.1 Backend

| Capability | Evidence |
|---|---|
| `POST /vapi/tools/capture-appointment-request` accepts flat local harness shape | Module 85 live smoke — HTTP 200 |
| `POST /vapi/tools/capture-appointment-request` accepts nested Vapi tool-call shape | Module 89 ngrok curl — HTTP 200 |
| `adapt_vapi_tool_call_body` extracts `clinic_ref` from machine auth, not body | Module 88 unit tests (tests 23–31) |
| `adapt_vapi_tool_call_body` extracts `call_id` from `message.call.id` | Module 88 unit test 28 |
| `adapt_vapi_tool_call_body` extracts `caller_phone` from `message.call.customer.number` | Module 88 unit test 31 |
| `adapt_vapi_tool_call_body` passes flat payloads through unchanged | Module 88 unit test 23 |
| Arguments as JSON string are parsed safely | Module 88 unit test 26 |
| `source='vapi'` always set | Module 85 smoke; Module 89 response body |
| `status='new'` always set on creation | Module 85 smoke; Module 89 response body |
| `action_required=True` always set | Module 85 smoke; Module 89 response body |
| Machine auth scope `vapi:tool` required (singular) | Module 89 — confirmed in practice |
| `ClinicConfigLoader` wired in lifespan for runtime use | Module 84 |
| UUID validation accepts deterministic local seed UUIDs | Module 85 — `uuid.UUID()` parser |
| DB-error fallback in `_load_db_config` (tenants table absent) | Module 85 |

### 3.2 Frontend

| Capability | Evidence |
|---|---|
| JWT login → token stored → dashboard loads | Module 75 browser smoke |
| All four dashboard sections render live data | Module 77/80 browser smoke |
| Appointment rows display `patient_name`, `status` badge, `urgency_level` | Module 79/80 |
| Confirm button only shown on `status === 'new'` rows | Module 81/82 |
| Confirm in-flight: button disabled, label "Confirming…" | Module 82 browser smoke |
| After Confirm: status badge → "confirmed", button disappears | Module 82 + 86 + 89 |
| Vapi-created appointment rows appear in dashboard without seed script | Module 86 + 89 |
| Staff can confirm Vapi/ngrok-sourced rows | Module 86 + 89 |
| Other dashboard sections remain stable after Confirm | Module 82 + 86 + 89 |
| Logout clears session; auth guard redirects to /login | Module 75 |

### 3.3 Integration

| Capability | Evidence |
|---|---|
| ngrok tunnel routes nested Vapi-shape body to backend adapter | Module 89 |
| Adapter fires on nested shape; flat shape passes through | Module 88 unit tests + Module 89 curl |
| Staff confirmation boundary maintained throughout | All module browser smokes |
| No auto-confirmation at any layer (adapter, service, route) | Service docstring + code review + tests |

---

## 4. Accuracy Boundary

| Claim | Status |
|---|---|
| Local flat harness → HTTP 200 | PROVEN |
| Local/ngrok nested shape → HTTP 200 | PROVEN |
| Vapi-created rows visible in dashboard | PROVEN |
| Staff Confirm: status new → confirmed | PROVEN |
| No auto-confirmation by AI | PROVEN |
| Direct real Vapi assistant tool-call triggered and logged | **PENDING** |
| Live Vapi assistant configured to call the adapted endpoint | **PENDING** |
| Real Vapi payload shape matches the sanitized sample | **PENDING** |

**Interpretation:** The intake loop is proven correct for the local/ngrok path. A real live
Vapi assistant triggering the tool and returning 2xx is the last unproven claim. It is
directionally sound based on the shape evidence, but should be confirmed with logs before
any production-facing work.

---

## 5. Security Review

### 5.1 Machine Auth and Tenant Isolation

| Concern | Status |
|---|---|
| `clinic_ref` in adapter always from `X-Vapi-Clinic-Id` header | ENFORCED — `machine_clinic_id` is always the source; argument clinic_ref silently ignored |
| `require_vapi_tool_access` called after adaptation | ENFORCED — runs before service call |
| Machine auth scope `vapi:tool` required | CONFIRMED — `required_scope="vapi:tool"` in `get_machine_auth_context` dependency |
| Plural `vapi:tools` rejected | CONFIRMED — machine auth guard rejects wrong scope |
| Tenant separation via `clinic_id` | ENFORCED — all PHI routes check `clinic_id`; adapter cannot inject a foreign clinic |

### 5.2 Staff Confirmation Boundary

The no-auto-confirmation rule is enforced at three levels:

1. **Service level:** `vapi_appointment_capture.py` docstring and code — `status='new'`, `action_required=True` hardcoded; no code path confirms or books.
2. **Route level:** `vapi_capture_appointment_request` returns the service result verbatim; no status mutation.
3. **Frontend level:** Confirm button only appears for staff with a valid Bearer JWT; requires explicit click; `PATCH /appointment-requests/{id}/status` is a separate human-initiated request.

No AI action at any layer sets `status='confirmed'`.

### 5.3 Data Safety

| Concern | Status |
|---|---|
| Real patient data | NONE — all test data uses deterministic fake names/phones |
| Secrets in docs or logs | NONE — machine auth headers are local-dev values; not committed |
| Raw payload logging | NOT DONE — raw payload is stored in `raw_payload` column for audit trail only |
| `adapt_vapi_tool_call_body` logs raw body | NO — adapter stores in dict; no print/log call |
| JWT storage | `sessionStorage` — local-dev only; clearly labeled in code, docs, and UI footer |
| Password storage | bcrypt hash; no plaintext in DB or logs |
| Audit logging | Active — PHI mutations and machine routes logged via `audit_logger` |
| No secrets in tenant config JSON | ENFORCED per architecture rules |

### 5.4 No Regressions

Security setup from previous sprints (HMAC webhook verification, tenant guards, audit
logging, bcrypt passwords, CORS explicit origins) is unchanged in Sprint 11. All
security measures from Sprints 1–10 remain active.

---

## 6. Code Quality Review

### 6.1 `adapt_vapi_tool_call_body`

- Pure function — no side effects, no I/O
- Handles `arguments` as both `dict` and JSON string — safe fallback to `{}` on parse error
- `clinic_ref` always overwritten with `machine_clinic_id` — no way for a caller to inject a tenant
- Flat payloads returned by identity (`return raw_body`) — no mutation
- 9 unit tests cover all branches including the security boundary and edge cases
- 5 contract tests verify importability and sample payload mapping

### 6.2 Route Update

- `request: Request` pattern is consistent with `vapi_webhooks.py` (`_adapt_vapi_payload` Module 56)
- Pydantic validation runs after adaptation — validation errors surface as HTTP 422
- `require_vapi_tool_access` check runs after validation — consistent with other tool routes
- Audit log call unchanged — uses `body.call_id` from the validated `VapiAppointmentCaptureRequest`

### 6.3 Service

- No changes to `capture_vapi_appointment_request` logic in Sprint 11
- `status='new'`, `action_required=True`, `source='vapi'` hardcoded — cannot be overridden by caller
- Notification call wrapped in `try/except` — notification failure does not break the capture response

---

## 7. Remaining Gaps

| Gap | Priority | Detail |
|---|---|---|
| Direct real Vapi assistant call logs | HIGH (before production) | ngrok path proven; live assistant not yet confirmed with logs |
| Production Vapi assistant configuration | HIGH (before production) | Test assistant only; no production config or secrets |
| Production deployment | HIGH (before any real users) | Local-dev only; no HTTPS, CI/CD, or hosting config |
| JWT session storage | HIGH (before any real users) | `sessionStorage` is local-dev; httpOnly cookie path not built |
| Token refresh | MEDIUM | Expired JWT shows generic error; no auto-redirect |
| Calendar handoff on Confirm | MEDIUM | No calendar event created on Confirm; future module |
| Patient notification on Confirm | MEDIUM | Confirming does not notify patient; future module |
| Notification side effects from Vapi capture | LOW | `create_appointment_request_notification` called but not surfaced in smoke output |
| Reject / Assign / Callback / Archive appointment actions | MEDIUM | Only Confirm implemented |
| Patient detail page | LOW | No `/patients/[id]` drill-down |
| Consultation detail page | LOW | No `/consultations/[id]` drill-down |
| Notification mark-read UI | LOW | `POST /notifications/{id}/read` backend exists; no frontend trigger |
| Doctor-facing UI/UX polish | FUTURE | See frontend opportunity below |

---

## 8. Frontend Opportunity — Doctor-Facing UI Polish

The current dashboard is functional and has been browser-smoke confirmed through multiple
sprints. It is suitable for local demo purposes.

**Opportunity (noted by user in Module 89):**
Evaluate **Fabel 5 / Claude-related frontend generation tooling** for a dedicated frontend
UX sprint to make the doctor-facing dashboard more premium, user-friendly, and impressive.

Goals:
- Higher-quality visual design
- Better appointment workflow UI (richer row display, action feedback, status transitions)
- Improved navigation between sections
- Preserve all security, integration quality, and staff confirmation boundaries

**Timing:** After Architecture Checkpoint 10, in a dedicated frontend UX sprint. This is
a quality opportunity — not part of the integration verification work.

---

## 9. Recommendation

**Sprint 11 / Module 90 — Direct Real Vapi Assistant Tool-Call Log Capture**

### Why

The only remaining evidence gap before this integration loop can be considered
production-facing is direct proof that a real live Vapi assistant triggers the adapted
endpoint, receives a 2xx response, and the backend creates the appointment row. The
local/ngrok path is proven. This final evidence step closes the gap.

### What to do in Module 90

1. Set up a test Vapi assistant with `capture_appointment_request` configured as a server-URL tool.
2. Configure machine auth headers: `X-Vapi-Service-Name: vapi`, `X-Vapi-Clinic-Id: 11111111-…`, `X-Vapi-Scopes: vapi:tool`.
3. Start an ngrok tunnel; point the assistant server URL at `https://<ngrok>/vapi/tools/capture-appointment-request`.
4. Make a test phone call with fake patient data.
5. Capture the raw request body from ngrok inspector or Vapi call logs; sanitize all PII.
6. Confirm backend received the nested shape; returned 2xx.
7. Confirm appointment row appeared in dashboard with `source=vapi`, `status=new`.
8. Click Confirm on the row in the dashboard; verify status → confirmed.
9. Run inspector on the captured payload; confirm NEEDS ADAPTER verdict (adapter is already wired).
10. Archive sanitized payload as `vapi_real_tool_payload_captured_from_live_assistant.json`.
11. Document all evidence in `docs/runtime/VAPI_REAL_ASSISTANT_TOOL_CALL_SMOKE_RESULTS.md`.

### What not to do

- Do not use real patient names, phone numbers, or clinic credentials
- Do not commit any payload without full PII sanitization
- Do not change production code — no code changes unless a real blocker appears
- Do not claim production readiness in the docs

---

## 10. Sprint Summary (all sprints)

| Sprint | Scope | Modules | Tests at End |
|---|---|---|---|
| Sprint 1 | Backend API foundation | 1–23 | 545 |
| Sprint 2 | Clinical documentation engine | 24–34 | 908 |
| Sprint 3 | Clinical workflow API routes + access control | 35–40 | 1083 |
| Sprint 4 | Database migration + audit logging | 41–44 | 1193 |
| Sprint 5 | Local PostgreSQL + smoke test | 45–51 | 1312 |
| Sprint 6 | External integration compatibility | 52–58 | 1386 |
| Sprint 7 | Production auth and JWT wiring | 59–65 | 1461 |
| Sprint 8 | Frontend dashboard foundation | 66–71 | 1521 |
| Sprint 9 | Local runtime smoke, CORS, browser demo | 72–77 | 1547 |
| Sprint 10 | Dashboard demo polish | 78–80 | 1560 |
| Sprint 11 | Vapi appointment intake loop | 81–89 | 1625 |
