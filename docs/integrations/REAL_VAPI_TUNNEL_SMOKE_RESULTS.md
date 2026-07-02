# Real Vapi Tunnel Smoke Results — PraxisMed Sprint 6 / Module 57

## 1. Purpose

This document records the evidence from a real Vapi tunnel smoke test session conducted after Module 56 (real Vapi payload compatibility adapter).

The goal was to confirm that a real Vapi dashboard webhook delivery reaches the local PraxisMed backend end-to-end, passes HMAC and machine auth, and returns HTTP 200.

---

## 2. Environment

| Component | Value |
|---|---|
| Local FastAPI | `http://127.0.0.1:8000` |
| Tunnel | ngrok forwarding to `http://127.0.0.1:8000` |
| Endpoint | `POST /webhooks/vapi/call-event` |
| Local PostgreSQL | Docker (`docker-compose.postgres.yml`) |
| Seed data | Deterministic local UUIDs (see `seed_local_data.py`) |
| Secrets | Local test secrets only — no production secrets used |

---

## 3. Vapi Dashboard Config Summary

| Setting | Value |
|---|---|
| Server URL | `https://<tunnel-base>/webhooks/vapi/call-event` |
| Credential name | PraxisMed Local HMAC Test |
| Signature Header | `x-signature` |
| Payload Format | `{body}` |
| Include Timestamp | Off |
| Encoding | Hex |

Custom headers configured in Vapi dashboard:

| Header | Value |
|---|---|
| `X-Vapi-Service-Name` | `vapi` |
| `X-Vapi-Clinic-Id` | `11111111-1111-1111-1111-111111111111` |
| `X-Vapi-Scopes` | `vapi:webhook` |

---

## 4. Evidence

| Item | Result |
|---|---|
| Real Vapi request reached ngrok | Confirmed |
| Real Vapi request reached local backend | Confirmed |
| Latest HTTP status | **200 OK** |
| Payload root structure | `message` object (real Vapi server shape) |
| Observed `message.type` | `end-of-call-report` |
| HMAC signature accepted | Yes — `x-signature` over `{body}` |
| Machine auth headers accepted | Yes — `X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes` |

---

## 5. Previous Failures and Fixes

| Failure | Cause | Fix |
|---|---|---|
| HTTP 401 `digest mismatch` | Vapi signing a different payload representation (not raw body) | Set Vapi credential Payload Format to `{body}` |
| HTTP 502 Bad Gateway | ngrok upstream pointed at wrong port | Corrected ngrok upstream to `http://127.0.0.1:8000` |
| HTTP 400 `Missing required field: 'clinic_id'` | Real Vapi payload does not include `clinic_id` at root | Fixed by Module 56 adapter — `clinic_id` resolved from machine auth context |

---

## 6. What This Proves

- The ngrok tunnel successfully exposes the local FastAPI server to the internet.
- Vapi dashboard webhook delivery reaches the local backend.
- HMAC-SHA256 verification works with `x-signature` header, `{body}` payload format, and hex encoding.
- Machine auth header aliases (`X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes`) are accepted.
- The Module 56 real Vapi payload adapter correctly resolves missing root fields from machine auth context and maps `message.type` to internal event types.
- End-to-end: real Vapi webhook → ngrok → FastAPI → HMAC check → machine auth → payload adapter → event handler → HTTP 200 OK.

---

## 7. What This Does Not Prove

- Production deployment readiness (no real hostname, no TLS certificate, no production secrets).
- Real patient data handling (only deterministic seed UUIDs used).
- Phone-number production workflow (no live phone call tested).
- Frontend or dashboard integration.
- Real appointment confirmation or scheduling.
- n8n calendar sync (separate test session required).

---

## 8. Next Recommendation

**Sprint 6 / Module 58 — Real n8n Tunnel Smoke Test Evidence**

Status: pending manual n8n setup.

Repeat the n8n test plan from `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` Section 7 using a real n8n workflow. Configure the HTTP Request node to point at the tunnel URL, compute HMAC in a Code node, and set the required machine auth headers. Record the HTTP response and any payload or header changes needed.
