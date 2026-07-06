# PraxisMed — Vapi Pseudonymized Logging

**Sprint 19 / Module 130**
**Date:** 2026-07-06
**Status:** Implemented — pseudonymization helpers available, audit log wired for Vapi capture

---

## 1. Rule: Vapi Payloads Must Never Be Logged Raw

Vapi webhook payloads and tool-call bodies may contain patient PII:
patient name, phone number, transcript content, reason for appointment, audio URLs.

**These must never appear verbatim in logs, audit records, or monitoring outputs.**

The PraxisMed pseudonymization pipeline replaces all sensitive values with deterministic
HMAC-SHA256 hash tokens before any log write. The original values are never returned,
never stored in log sinks, and never transmitted to monitoring services.

---

## 2. Sensitive Fields

The following field names are considered sensitive:

| Field | Treatment |
|---|---|
| `patient_name`, `name`, `full_name` | HMAC-SHA256 hex token |
| `phone`, `phone_number`, `mobile` | HMAC-SHA256 hex token |
| `email` | HMAC-SHA256 hex token |
| `transcript`, `raw_transcript`, `audio_transcript` | Redacted: `[TRANSCRIPT REDACTED]` |
| `recording_url`, `audio_url` | Redacted: `[TRANSCRIPT REDACTED]` |
| `reason` | HMAC-SHA256 hex token |
| `notes` | HMAC-SHA256 hex token |
| `message` | HMAC-SHA256 hex token |

---

## 3. Safe Operational Fields (Preserved Verbatim)

These fields are safe to log and are never pseudonymized:

| Field | Example |
|---|---|
| `clinic_id`, `clinic_ref` | UUID |
| `call_id` | Vapi-assigned call identifier |
| `source` | `"vapi"` |
| `status` | `"new"` / `"confirmed"` |
| `urgency_level` | `"normal"` / `"urgent"` |
| `action_required` | `true` / `false` |
| `ok` | `true` / `false` |
| `created_at`, `updated_at` | ISO 8601 timestamps |

---

## 4. Implementation

All helpers live in `backend/app/core/pseudonymization.py`:

```python
from backend.app.core.pseudonymization import (
    pseudonymize,                   # stable HMAC-SHA256 hex token for any value
    pseudonymize_phone,             # context-scoped token for phone numbers
    pseudonymize_name,              # context-scoped token for patient names
    pseudonymize_email,             # context-scoped token for email addresses
    stable_hash,                    # unscoped HMAC-SHA256 token
    redact_transcript,              # returns "[TRANSCRIPT REDACTED]" sentinel
    sanitize_for_log,               # recursively sanitize any dict/list/scalar
    sanitize_vapi_webhook_payload,  # sanitize a Vapi payload dict for safe logging
    assert_pseudonymization_ready,  # raises AssertionError if PSEUDONYMIZATION_PEPPER not set
)
```

### sanitize_vapi_webhook_payload

```python
raw_payload = {
    "call_id": "vapi-call-001",
    "clinic_ref": "1a5bbc75-...",
    "patient_name": "Demo Patient",      # ← sensitive
    "phone": "+436601234567",             # ← sensitive
    "reason": "Routine appointment",      # ← sensitive
    "urgency_level": "normal",            # ← safe
}

safe = sanitize_vapi_webhook_payload(raw_payload)
# safe = {
#     "call_id": "vapi-call-001",          # preserved
#     "clinic_ref": "1a5bbc75-...",        # preserved
#     "patient_name": "a3f7b2...(64 hex)", # HMAC token
#     "phone": "9c1e5d...(64 hex)",        # HMAC token
#     "reason": "f82a3c...(64 hex)",       # HMAC token
#     "urgency_level": "normal",           # preserved
# }
```

---

## 5. Vapi Audit Log Integration

The Vapi appointment capture route (`POST /vapi/tools/capture-appointment-request`)
writes an audit event with pseudonymized metadata:

```python
metadata={
    "route": "vapi_capture_appointment_request",
    "call_id": body.call_id,                           # safe — Vapi-assigned ID
    "patient_name_hash": pseudonymize_name(body.patient_name),   # HMAC token
    "caller_phone_hash": pseudonymize_phone(body.caller_phone),  # HMAC token
}
```

The appointment_request DB record itself retains full fidelity (patient_name, phone, etc.)
because those values are needed for the clinical workflow. Only the audit log metadata
is pseudonymized.

---

## 6. PSEUDONYMIZATION_PEPPER

The HMAC-SHA256 hash uses a secret pepper from the environment variable `PSEUDONYMIZATION_PEPPER`.

| Environment | Pepper |
|---|---|
| Local / staging | Staging fallback sentinel (not secret, not for production) |
| Production | `PSEUDONYMIZATION_PEPPER` env var — managed via Railway secrets |

**The pepper is never logged, never printed, never committed to code.**
Set it via Railway dashboard → Environment Variables.

In production, call `assert_pseudonymization_ready()` at startup to verify the pepper is set
before processing any PHI.

---

## 7. What This Does Not Provide

- **Full PHI redaction pipeline** — the DB appointment_request row still stores raw PII.
  Full redaction (C4) is a production hardening blocker.
- **Transcript ingestion** — recording/transcript ingestion is not yet enabled.
  The `redact_transcript()` helper is ready for when it is wired.
- **DSGVO/GDPR compliance** — this is a technical logging safeguard, not a compliance claim.
- **Irreversibility guarantee** — pseudonymized tokens are deterministic and could be
  reversed by an attacker who knows the pepper. Production PHI requires additional controls.

---

## 8. Safety Summary

| Constraint | Status |
|---|---|
| No raw patient_name in audit logs | **ENFORCED** — HMAC token in metadata |
| No raw phone in audit logs | **ENFORCED** — HMAC token in metadata |
| No raw transcript in logs | **ENFORCED** — redaction sentinel |
| No raw reason/message in logs | **ENFORCED** — HMAC token via sanitize_for_log |
| PSEUDONYMIZATION_PEPPER managed as secret | **CONFIRMED** — env var only |
| No secrets committed to code | **CONFIRMED** |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |
