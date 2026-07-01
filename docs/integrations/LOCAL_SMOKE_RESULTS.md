# Local Integration Smoke Results — PraxisMed

## A. Date / Context

- **After:** Sprint 5 / Module 50 — Local seed data and webhook smoke fixtures
- **Project path:** `/Users/aliabdeltawab/Documents/praximed`

---

## B. Environment Confirmed

| Component | Status |
|---|---|
| Docker PostgreSQL | Running on `localhost:5433` |
| Alembic migration | Applied (`alembic upgrade head` passed) |
| `seed_local_data.py` | Passed — 4 rows inserted |
| FastAPI server | Started from project root with `python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000` |
| `DATABASE_URL` | `postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local` |
| Webhook secrets | Local-only placeholder values (not production secrets) |

---

## C. Seeded Local IDs

| Resource | UUID |
|---|---|
| `clinic_id` | `11111111-1111-1111-1111-111111111111` |
| `doctor_user_id` | `22222222-2222-2222-2222-222222222222` |
| `patient_id` | `33333333-3333-3333-3333-333333333333` |
| `consultation_session_id` | `44444444-4444-4444-4444-444444444444` |

---

## D. Vapi Signed Webhook — Valid Request

**Endpoint:** `POST /webhooks/vapi/call-event`

**Payload file:** `docs/integrations/local_payloads/vapi_call_event.json`

```json
{
  "clinic_id": "11111111-1111-1111-1111-111111111111",
  "call_id": "local-test-call-1",
  "event_type": "call.ended",
  "action_required": false
}
```

**Required headers:**

```
X-Service-Name: vapi
X-Service-Clinic-Id: 11111111-1111-1111-1111-111111111111
X-Service-Scopes: vapi:webhook
X-Vapi-Signature: sha256=<valid HMAC computed by sign_webhook_payload.py>
```

**Expected result:** HTTP 200 — route processes payload and writes to DB

**Actual result:** HTTP 200 OK

**Response body:**
```json
{
  "ok": true,
  "clinic_id": "11111111-1111-1111-1111-111111111111",
  "event_type": "call.ended",
  "call_id": "local-test-call-1",
  "message": "Event 'call.ended' processed successfully.",
  "notification_created": false
}
```

---

## E. Vapi Bad Signature — Invalid Request

**Header sent:** `X-Vapi-Signature: sha256=wrong`

**Expected result:** HTTP 401 Unauthorized

**Actual result:** HTTP 401 Unauthorized

**Response body:**
```json
{
  "detail": "Webhook signature verification failed: digest mismatch."
}
```

---

## F. n8n Calendar Sync Signed Webhook — Valid Request

**Endpoint:** `POST /webhooks/n8n/calendar-sync`

**Payload file:** `docs/integrations/local_payloads/n8n_calendar_sync.json`

```json
{
  "clinic_id": "11111111-1111-1111-1111-111111111111",
  "provider": "google",
  "external_calendar_id": "local-test@group.calendar.google.com",
  "event_type": "connection_upsert"
}
```

**Required headers:**

```
X-Service-Name: n8n
X-Service-Clinic-Id: 11111111-1111-1111-1111-111111111111
X-Service-Scopes: calendar:sync
X-N8N-Signature: sha256=<valid HMAC computed by sign_webhook_payload.py>
```

**Expected result:** HTTP 200 — route processes payload and writes to DB

**Actual result:** HTTP 200 OK

**Response body:**
```json
{
  "ok": true,
  "event_type": "connection_upsert",
  "clinic_id": "11111111-1111-1111-1111-111111111111",
  "action": "connection_upserted",
  "message": "Calendar connection upserted for provider 'google', calendar 'local-test@group.calendar.google.com'."
}
```

---

## G. What This Proves

| Capability | Confirmed |
|---|---|
| Runtime DB pool startup from `DATABASE_URL` | ✓ |
| Real local PostgreSQL writes from route handlers | ✓ |
| Machine auth header validation (`X-Service-*`) | ✓ |
| HMAC-SHA256 webhook signature verification | ✓ |
| Signature rejection on mismatch (401) | ✓ |
| Route handlers process seeded UUID payloads correctly | ✓ |
| Audit logging does not break the response workflow | ✓ |
| Idempotent local seed data via `seed_local_data.py` | ✓ |

---

## H. What This Does Not Prove Yet

| Capability | Status |
|---|---|
| Real Vapi dashboard integration | Not done — local only |
| Real n8n workflow integration | Not done — local only |
| Public tunnel / webhook delivery (ngrok, etc.) | Not done |
| Production secrets management | Not done |
| Real OAuth / JWT user auth flow | Not done |
| Provider-native signature compatibility (Vapi's own signing format) | Unverified |
| n8n native signing mechanism vs. our HMAC convention | Unverified |
| Production security readiness review | Not done |

---

## I. Next Recommended Milestone

**Sprint 6 / Module 52 — External Integration Compatibility Plan for Vapi and n8n**

**Reason:**

Before configuring real Vapi or n8n dashboards, we need to document:

1. How Vapi delivers webhook payloads and signs them natively — does its signing format match our `X-Vapi-Signature: sha256=<digest>` convention?
2. How n8n delivers webhook payloads and whether it supports a signing header.
3. Whether an adapter layer or request transformer is needed between the provider and our routes.
4. What public tunnel setup (ngrok / Cloudflare Tunnel) is required for local webhook delivery testing.
5. Whether machine auth headers (`X-Service-*`) need to be injected by a gateway or supported natively by the providers.

This planning sprint ensures that when real dashboards are configured, the integration works on the first attempt rather than requiring emergency route changes.
