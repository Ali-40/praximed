# Real n8n Tunnel Smoke Results — PraxisMed Sprint 6 / Module 58

## 1. Purpose

This document records the evidence from a real n8n tunnel smoke test session conducted in Sprint 6 / Module 58.

The goal was to confirm that a real n8n HTTP Request node can reach the local PraxisMed backend through a public tunnel, pass HMAC signature verification and machine auth, and receive a successful response from the calendar sync route.

---

## 2. Environment

| Component | Value |
|---|---|
| Local FastAPI | `http://127.0.0.1:8000` |
| Tunnel | ngrok forwarding to `http://127.0.0.1:8000` |
| Endpoint | `POST /webhooks/n8n/calendar-sync` |
| Local PostgreSQL | Docker (`docker-compose.postgres.yml`) |
| Seed data | Deterministic local UUIDs (see `seed_local_data.py`) |
| Secrets | Local test secrets only — no production secrets used |

---

## 3. n8n HTTP Request Node Config

| Setting | Value |
|---|---|
| Method | POST |
| URL | `https://<tunnel-base>/webhooks/n8n/calendar-sync` |
| Body type | Raw compact JSON |

Headers set in the HTTP Request node:

| Header | Value |
|---|---|
| `X-N8N-Service-Name` | `n8n` |
| `X-N8N-Clinic-Id` | `11111111-1111-1111-1111-111111111111` |
| `X-N8N-Scopes` | `calendar:sync` |
| `X-Signature` | `sha256=<hmac-sha256-hex-digest-of-raw-body>` |

The HMAC digest was computed over the exact raw compact JSON body sent by the HTTP Request node using `N8N_WEBHOOK_SECRET`.

---

## 4. Evidence

| Item | Result |
|---|---|
| Real n8n HTTP Request node reached ngrok | Confirmed |
| Real n8n request reached local backend | Confirmed |
| HTTP response status | Success |
| Machine auth headers accepted | Yes — `X-N8N-Service-Name`, `X-N8N-Clinic-Id`, `X-N8N-Scopes` |
| HMAC signature accepted | Yes — `X-Signature: sha256=...` over raw compact JSON body |

---

## 5. Failure and Fix

| Failure | Cause | Fix |
|---|---|---|
| HMAC digest mismatch | Signature was computed over a different body representation than the bytes actually sent by the HTTP Request node | Fixed by computing the HMAC over the exact raw compact JSON body that n8n sends and setting `X-Signature: sha256=<hex-digest>` |

**Key lesson**: The signature must be computed over the exact bytes the HTTP client sends on the wire. Any difference in whitespace, key ordering, or encoding between the body used to compute the signature and the body transmitted causes a digest mismatch.

---

## 6. What This Proves

- n8n can call PraxisMed endpoints through a public tunnel.
- n8n HTTP Request nodes support custom machine auth headers (`X-N8N-Service-Name`, `X-N8N-Clinic-Id`, `X-N8N-Scopes`).
- HMAC-SHA256 signature verification works when the signature is computed over the same raw bytes that are transmitted.
- The `X-Signature: sha256=<hex>` header format is accepted by the backend.
- The n8n machine auth alias headers added in Module 54 work correctly with a real n8n request.
- The calendar sync route (`POST /webhooks/n8n/calendar-sync`) is reachable and processes real payloads.

---

## 7. What Remains Unproven

- Production n8n workflow connected to real Google Calendar data.
- Real calendar event payloads (only local test payloads used).
- Production secrets and secret management.
- Production deployment (no real hostname, no TLS certificate beyond the ngrok-provided one).
- Frontend or dashboard integration.
- Real patient appointment flows triggered by calendar sync events.

---

## 8. Next Recommendation

**Architecture Checkpoint 05 — External Integration Review**

Status: pending.

Before continuing with new feature modules, review the external integration work completed in Sprint 6 (Modules 52–58):

- Provider header alias configs (Modules 53–54).
- Webhook signature alias configs (Module 53).
- Real Vapi tunnel smoke and payload adapter (Modules 55–57).
- Real n8n tunnel smoke (Module 58).

The checkpoint should document integration readiness, confirm the remaining gaps before production, and define the next sprint focus.
