# Vapi Real Tool Call Adapter — PraxisMed Sprint 11 / Module 88

**Date:** 2026-07-02
**Verdict:** IMPLEMENTED — local flat harness remains PASS; live Vapi nested shape now supported

---

## 1. Purpose

This document records what was built in Module 88 to handle the shape gap identified in
Module 87: the current capture route expected a flat body, while a real Vapi server-URL
tool-call sends a nested `message.toolCallList` body.

---

## 2. Shape Gap Recap (Module 87)

| Shape | Source | Example |
|---|---|---|
| Flat (local harness) | `smoke_vapi_appointment_intake.py` | `{"clinic_ref": "...", "call_id": "...", "patient_name": "..."}` |
| Nested (real Vapi) | Live Vapi assistant server-URL call | `{"message": {"toolCallList": [...], "call": {...}}}` |

Key mapping for nested shape:
- `clinic_ref` → from `X-Vapi-Clinic-Id` machine auth header (NOT from body arguments)
- `call_id` → from `message.call.id`, fallback to `toolCallList[0].id`
- `caller_phone` → from `message.call.customer.number`
- `patient_name`, `reason`, `urgency_level` → from `function.arguments`

---

## 3. What Was Built

### 3.1 `adapt_vapi_tool_call_body` — `vapi_appointment_capture.py`

Added between the internal helpers and the public API section.

Behaviour:
- If `raw_body` has no `message.toolCallList` key → returned **unchanged** (flat passthrough)
- If `message.toolCallList` is present → adapted to flat `VapiAppointmentCaptureRequest` fields
- `arguments` can be a `dict` or JSON string — both handled safely
- `clinic_ref` is **always** `machine_clinic_id` — patient-supplied clinic IDs in arguments are silently ignored
- `raw_payload` is set to the full raw body for audit trail storage
- Raw payload is never logged

### 3.2 Route update — `vapi_tools.py`

`vapi_capture_appointment_request` signature changed from:
```python
body: VapiAppointmentCaptureRequest
```
to:
```python
request: Request
```

Route body now:
1. Parses raw JSON (`await request.json()`)
2. Runs `adapt_vapi_tool_call_body(raw, machine_auth.clinic_id)`
3. Validates with `VapiAppointmentCaptureRequest(**adapted)` — returns HTTP 422 on failure
4. Proceeds to `require_vapi_tool_access` and service call unchanged

---

## 4. Security Boundaries Maintained

| Constraint | Status |
|---|---|
| `clinic_ref` always from machine auth, never from nested arguments | ENFORCED in adapter |
| Appointment request created with `status=new`, `action_required=True` | UNCHANGED |
| No auto-confirmation by AI | UNCHANGED |
| Raw payload not logged | ENFORCED — only stored in `raw_payload` column for audit |
| Machine auth headers required (`X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes: vapi:tool`) | UNCHANGED |
| HMAC not required for tool route (only for webhook route) | UNCHANGED |

---

## 5. Tests Added

### `backend/tests/test_vapi_appointment_capture.py` — 9 new tests

| # | Test | What it verifies |
|---|---|---|
| 23 | `test_adapter_passes_flat_payload_through` | Flat body returned unchanged (identity) |
| 24 | `test_adapter_extracts_patient_name_from_nested` | `patient_name` from `function.arguments` |
| 25 | `test_adapter_extracts_reason_from_nested` | `reason` from `function.arguments` |
| 26 | `test_adapter_parses_json_string_arguments` | `arguments` as JSON string parsed correctly |
| 27 | `test_adapter_uses_machine_clinic_id_not_argument_clinic` | Patient-supplied `clinic_ref` ignored |
| 28 | `test_adapter_call_id_from_message_call` | `call_id` from `message.call.id` |
| 29 | `test_adapter_call_id_fallback_to_tool_id` | `call_id` from `toolCallList[0].id` when `call` absent |
| 30 | `test_adapter_missing_patient_name_returns_empty` | Empty string when `patient_name` absent (Pydantic rejects) |
| 31 | `test_adapter_caller_phone_from_customer_number` | `caller_phone` from `message.call.customer.number` |

### `backend/tests/test_vapi_real_tool_payload_prep_contract.py` — 5 new tests

| # | Test | What it verifies |
|---|---|---|
| 18 | `test_adapter_function_exists_in_capture_module` | `adapt_vapi_tool_call_body` defined in module |
| 19 | `test_adapter_accepts_machine_clinic_id_param` | Security param present |
| 20 | `test_adapter_does_not_trust_clinic_ref_from_arguments` | `machine_clinic_id` used |
| 21 | `test_adapter_maps_sample_payload_to_flat_fields` | Sample JSON maps to correct flat fields |
| 22 | `test_adapter_flat_payload_unchanged` | Flat payload identity preserved |

---

## 6. Test Run Results

```
1625 passed (full suite, including 14 new Module 88 tests)
```

Previous count: 1611. Increase: 14 (9 adapter unit tests + 5 contract tests).

---

## 7. Manual Smoke Status

| Shape | Status |
|---|---|
| Flat (local harness) | PASS — `smoke_vapi_appointment_intake.py` returns HTTP 200 (proven Module 85) |
| Nested (real Vapi live) | PENDING — live Vapi assistant test not yet run; adapter logic verified by unit tests |

Live Vapi nested shape smoke is the recommended next step (Module 89).

---

## 8. Inspector Compatibility

Run against the sample payload:

```bash
python backend/scripts/inspect_vapi_tool_payload.py \
  --payload-file docs/integrations/local_payloads/vapi_real_tool_payload_sample.json
```

Expected verdict: **NEEDS ADAPTER** — the adapter is now in place.

If a real captured payload is available:

```bash
python backend/scripts/inspect_vapi_tool_payload.py \
  --payload-file docs/integrations/local_payloads/vapi_real_tool_payload_captured.json
```

Compare argument keys against what the adapter extracts. If the real payload uses different
argument key names (e.g. `name` instead of `patient_name`), add aliasing logic to the adapter.

---

## 9. What This Does Not Prove

| Gap | Detail |
|---|---|
| Live Vapi assistant calling the capture endpoint | Not yet run — no real Vapi assistant or ngrok tunnel in this module |
| Production deployment | Local-dev only |
| Calendar event creation on Confirm | Not implemented — future module |
| Real patient data | All test data is deterministic fake (local-dev only) |

---

## 10. Module 89 — ngrok/Dashboard Evidence

**Sprint 11 / Module 89** confirms the adapter remains compatible with the tested
ngrok/Vapi-like intake path. Evidence:

- Nested Vapi-shape POST through ngrok → HTTP 200 — adapter fired correctly
- `clinic_ref` from `X-Vapi-Clinic-Id` header, `call_id` from `message.call.id`,
  `caller_phone` from `message.call.customer.number` — all resolved correctly
- Appointment rows created via ngrok path appeared in staff dashboard
- Staff Confirm action succeeded — status new → confirmed
- Machine auth scope confirmed: `X-Vapi-Scopes: vapi:tool` (singular)

Direct real Vapi assistant call logs: **PENDING** — not captured in Module 89.

See: `docs/runtime/VAPI_REAL_TOOL_CALL_LIVE_SMOKE_RESULTS.md`
