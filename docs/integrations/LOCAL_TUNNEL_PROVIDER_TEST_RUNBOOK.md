# Local Tunnel Provider Test Runbook — PraxisMed

## 1. Purpose

This runbook prepares for **controlled real-provider testing** after local integration smoke success.

It covers:

- Starting the full local stack (PostgreSQL, FastAPI, seeded data).
- Exposing the local server through a public tunnel.
- Sending real or real-like requests from Vapi and n8n to the local backend.
- Capturing evidence of what actually happens.

This is not a production setup guide. It is a safe, isolated, reversible test procedure.

---

## 2. Current Proven Local State

The following capabilities have been confirmed working locally before any tunnel test:

| Capability | Status |
|---|---|
| Local PostgreSQL (Docker) | Confirmed |
| Alembic migrations | Confirmed |
| Local seed data (4 deterministic UUIDs) | Confirmed |
| FastAPI runtime DB pool startup | Confirmed |
| HMAC-SHA256 webhook signature verification | Confirmed |
| Machine auth header validation (X-Service-*) | Confirmed |
| Provider alias headers for webhook signatures | Confirmed |
| Provider alias headers for machine auth | Confirmed |
| Vapi alias smoke (X-Vapi-* headers) | **HTTP 200 OK** |
| n8n alias smoke (X-N8N-* headers) | **HTTP 200 OK** |
| Bad signature rejection | **HTTP 401** |

The full local stack is stable. This runbook moves to the next step: real external provider connectivity.

---

## 3. Safety Rules

Follow these rules without exception during all tunnel tests:

- **No real patient data.** Use only seeded deterministic UUIDs from `seed_local_data.py`.
- **No production secrets.** Use only local placeholder secrets (`local-vapi-secret-change-me`, etc.).
- **No disabling auth or signatures.** Do not comment out or bypass HMAC verification or machine auth headers to make a test pass faster. Investigate the root cause instead.
- **No production URLs.** Do not point real Vapi or n8n production workflows at this tunnel.
- **Rotate local test secrets after testing.** If a real signing secret was configured in a Vapi/n8n dashboard, rotate or delete it after the test session.
- **Stop the tunnel after testing.** A running tunnel with a known URL is an open door. Close it when done.

---

## 4. Local Startup Checklist

Run these steps in order before starting the tunnel.

### Step 1 — Start local PostgreSQL

```bash
docker compose -f docker-compose.postgres.yml up -d
docker compose -f docker-compose.postgres.yml ps
```

Expected: container status `Up`.

### Step 2 — Export environment variables

```bash
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
export VAPI_WEBHOOK_SECRET=local-vapi-secret-change-me
export N8N_WEBHOOK_SECRET=local-n8n-secret-change-me
export INTERNAL_WEBHOOK_SECRET=local-internal-secret-change-me
```

> **Do not use real production secrets here.** These are local placeholder values only.

### Step 3 — Run Alembic migrations

```bash
python backend/scripts/run_migrations.py
```

### Step 4 — Seed local test data

```bash
python backend/scripts/seed_local_data.py
```

Expected: no errors. The script is idempotent — safe to run multiple times.

Seeded UUIDs:

| Resource | UUID |
|---|---|
| Clinic | `11111111-1111-1111-1111-111111111111` |
| Doctor user | `22222222-2222-2222-2222-222222222222` |
| Patient | `33333333-3333-3333-3333-333333333333` |
| Consultation session | `44444444-4444-4444-4444-444444444444` |

### Step 5 — Start FastAPI

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Wait for `Application startup complete` before continuing.

If port 8000 is already in use, an existing backend is likely running. Stop it first (`Ctrl+C` in its terminal) before starting a new one to avoid address conflicts.

---

## 5. Tunnel Plan

Use **ngrok** (or an equivalent such as Cloudflare Tunnel) to expose the local FastAPI server to the internet.

### Start ngrok

```bash
ngrok http 8000
```

ngrok prints a public HTTPS URL such as `https://abc123.ngrok-free.app`. This is the **tunnel base URL** for this session.

### Endpoint paths

| Route | Full tunnel URL |
|---|---|
| Vapi webhook | `https://<tunnel-base>/webhooks/vapi/call-event` |
| n8n calendar sync | `https://<tunnel-base>/webhooks/n8n/calendar-sync` |

### Notes on vapi listen

Vapi provides a `vapi listen` CLI command that can forward Vapi events locally for debugging. This may be useful for inspecting the exact payload Vapi sends, but it does not replace a public tunnel for receiving actual dashboard webhooks. A public tunnel is still required if Vapi needs to POST to an endpoint that your machine is hosting.

---

## 6. Vapi Real Test Plan

### Configuration

1. In the Vapi dashboard, create a **test assistant** (not production).
2. Set the server/webhook URL to:
   ```
   https://<tunnel-base>/webhooks/vapi/call-event
   ```
3. Configure Vapi to send the following headers on webhook delivery:

   | Header | Value |
   |---|---|
   | `X-Vapi-Service-Name` | `vapi` |
   | `X-Vapi-Clinic-Id` | `11111111-1111-1111-1111-111111111111` |
   | `X-Vapi-Scopes` | `vapi:webhook` |
   | `X-Vapi-Hmac-Sha256` or `X-Signature` | `<hmac-sha256 digest of payload>` |

   Use whichever signature header Vapi supports natively. Both `X-Vapi-Hmac-Sha256` and `X-Signature` are accepted by the backend.

4. Configure the HMAC secret in the Vapi dashboard to match `VAPI_WEBHOOK_SECRET` set in your shell.

### Verification steps

1. Trigger a test call event from the Vapi dashboard.
2. **Expected:** FastAPI returns **HTTP 200** and logs the event.
3. Change the signing secret in the Vapi dashboard to something wrong.
4. **Expected:** FastAPI returns **HTTP 401** — `digest mismatch`.
5. Restore the correct secret.

### What to record

- Exact request headers received (check ngrok's web inspector at `http://127.0.0.1:4040`).
- Exact request body received.
- HTTP response status from FastAPI.
- Any route or auth errors in the FastAPI logs.
- Whether any code change is needed to accommodate Vapi's actual payload shape.

---

## 7. n8n Real Test Plan

### Configuration

1. In n8n, create a **test workflow** (not production).
2. Add an **HTTP Request node** pointed at:
   ```
   https://<tunnel-base>/webhooks/n8n/calendar-sync
   ```
3. Configure the HTTP Request node to send the following headers:

   | Header | Value |
   |---|---|
   | `X-N8N-Service-Name` | `n8n` |
   | `X-N8N-Clinic-Id` | `11111111-1111-1111-1111-111111111111` |
   | `X-N8N-Scopes` | `calendar:sync` |
   | `X-Signature` or `X-N8N-Signature` | `<hmac-sha256 digest>` |

4. If n8n cannot produce HMAC-SHA256 natively, add a **Code node** before the HTTP Request node to compute the digest:

   ```js
   const crypto = require('crypto');
   const secret = $env.N8N_WEBHOOK_SECRET;  // store in n8n credentials
   const body = JSON.stringify($json);
   const digest = 'sha256=' + crypto.createHmac('sha256', secret).update(body).digest('hex');
   return [{ json: { ...$json, _signature: digest } }];
   ```

   Then use `{{ $json._signature }}` as the header value.

### Verification steps

1. Activate the test workflow and trigger it.
2. **Expected:** FastAPI returns **HTTP 200**.
3. Remove or corrupt the signature header in the workflow.
4. **Expected:** FastAPI returns **HTTP 401**.
5. Restore the correct signature.

### Important notes

- n8n uses **separate URLs** for test and production webhook triggers. Do not mix them.
- Use the test URL (`/webhook-test/`) during workflow development, and the production URL (`/webhook/`) only after finalising the workflow.
- Store all secrets in n8n Credentials, not in hard-coded node values.

---

## 8. Evidence Template

Complete this table after each real provider test session. Keep one row per test attempt.

| Provider | Tunnel URL used | Endpoint | Key request headers | Response status | Response body (summary) | Issues found | Code change needed |
|---|---|---|---|---|---|---|---|
| Vapi | `https://…` | `/webhooks/vapi/call-event` | X-Vapi-Service-Name, X-Vapi-Clinic-Id, X-Vapi-Scopes, X-Vapi-Hmac-Sha256 | 200 | `{"ok": true, ...}` | None | No |
| Vapi (bad sig) | `https://…` | `/webhooks/vapi/call-event` | X-Vapi-Signature: wrong | 401 | `{"detail": "digest mismatch"}` | None | No |
| n8n | `https://…` | `/webhooks/n8n/calendar-sync` | X-N8N-Service-Name, X-N8N-Clinic-Id, X-N8N-Scopes, X-Signature | — | — | — | — |

Copy and extend this table as needed. Store completed evidence files in `docs/integrations/` with a date prefix (e.g., `2026-07-15_tunnel_smoke_evidence.md`).

---

## 9. Stop and Cleanup

After each test session:

### Stop ngrok

Press `Ctrl+C` in the ngrok terminal, or close the ngrok process. Verify the public URL is no longer accessible.

### Stop FastAPI

Press `Ctrl+C` in the uvicorn terminal.

### Stop PostgreSQL (optional)

```bash
docker compose -f docker-compose.postgres.yml down
```

> **WARNING:** Do not use `-v`. The `-v` flag deletes the local database volume permanently.

### Unset local secrets (optional)

```bash
unset VAPI_WEBHOOK_SECRET
unset N8N_WEBHOOK_SECRET
unset INTERNAL_WEBHOOK_SECRET
unset DATABASE_URL
```

### Rotate provider-side secrets

If you configured a real signing secret in the Vapi or n8n dashboard for this test session, delete or rotate it after you are done. Do not leave test secrets active in provider dashboards.

---

## 10. Observed Real Vapi Tunnel Result (Module 55 session)

The following was confirmed during a real Vapi tunnel test session:

- Real Vapi reached ngrok and the backend.
- HMAC auth passed after configuring:
  - Signature Header: `x-signature`
  - Include Timestamp: OFF
  - Payload Format: `{body}`
  - Encoding: Hex
- Machine auth headers that worked:
  - `X-Vapi-Service-Name: vapi`
  - `X-Vapi-Clinic-Id: 11111111-1111-1111-1111-111111111111`
  - `X-Vapi-Scopes: vapi:webhook`
- Backend returned **HTTP 400**: `{"detail":"Missing required field: 'clinic_id'"}`
  - **Root cause**: Real Vapi server payloads use `{"message": {"type": "assistant-started", ...}}` — they do not include `clinic_id`, `call_id`, or `event_type` at the root.
  - **Fixed in Module 56**: The route now adapts real Vapi payloads — resolving `clinic_id` from machine auth, `event_type` from `message.type`, and `call_id` from `message.call.id` or `X-Call-Id` header.

---

## 11. Next Module Recommendation

**Sprint 6 / Module 57 — Real Vapi Tunnel Retest Evidence**

Status: pending Module 56 review.

Repeat the Vapi test plan from Section 6 with the adapter in place. Verify that the real Vapi payload no longer causes HTTP 400 and that HTTP 200 is returned for both `assistant-started` and `end-of-call-report` events.
