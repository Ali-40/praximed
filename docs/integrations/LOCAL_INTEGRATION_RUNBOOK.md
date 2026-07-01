# Local Integration Runbook — PraxisMed

## A. Purpose

This runbook is for **local integration testing only**, before any real Vapi or n8n dashboard is configured.

It shows how to:
- Start local PostgreSQL and run Alembic migrations
- Seed local fake test data (deterministic UUIDs)
- Run the FastAPI backend locally
- Generate HMAC-SHA256 signed webhook headers
- Send signed test requests to the Vapi and n8n webhook routes

Real Vapi and real n8n integration is **not done yet** — that comes in a later sprint.

---

## B. Prerequisites

- Docker Desktop running
- Python environment active (the same environment used for `pytest`)
- Project folder: `/Users/aliabdeltawab/Documents/praximed`

---

## C. Start Local PostgreSQL

### 1. Start the database container

```bash
cd /Users/aliabdeltawab/Documents/praximed
docker compose -f docker-compose.postgres.yml up -d
```

### 2. Verify it is running

```bash
docker compose -f docker-compose.postgres.yml ps
```

### 3. Export the database URL

```bash
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
```

### 4. Run Alembic migrations

```bash
python backend/scripts/run_migrations.py
```

### 5. Smoke-test the schema

```bash
python backend/scripts/db_smoke_test.py
```

Expected output: no errors and exit code 0.

### 6. Seed local test data

```bash
python backend/scripts/seed_local_data.py
```

This inserts deterministic fake-only rows into the local database using the fixed UUIDs below.
**Seed data is not production data.** It is safe to run multiple times — the script is idempotent.

---

## D. Deterministic Local Test UUIDs

These UUIDs are hard-coded in the seed script and used in all local smoke payloads:

| Resource | UUID |
|---|---|
| Clinic | `11111111-1111-1111-1111-111111111111` |
| Doctor user | `22222222-2222-2222-2222-222222222222` |
| Patient | `33333333-3333-3333-3333-333333333333` |
| Consultation session | `44444444-4444-4444-4444-444444444444` |

---

## E. Required Local Environment Variables

Set these in your shell before starting the backend. **Use local placeholder values only.**

```bash
export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local

export VAPI_WEBHOOK_SECRET=local-vapi-secret-change-me
export N8N_WEBHOOK_SECRET=local-n8n-secret-change-me
export INTERNAL_WEBHOOK_SECRET=local-internal-secret-change-me
```

> **WARNING — local secrets only**
>
> The values above are placeholder secrets for local development.
> **Never commit real production secrets to version control.**
> Real production secrets belong in a deployment secret manager (e.g., AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault) and will be configured in a later sprint.

---

## F. Start Backend Locally

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Wait until you see `Application startup complete` in the logs before sending requests.

---

## G. Machine Auth Headers

Every integration route requires machine auth headers in addition to the webhook signature.

### Vapi webhook (`POST /webhooks/vapi/call-event`)

| Header | Value |
|---|---|
| `X-Service-Name` | `vapi` |
| `X-Service-Clinic-Id` | `11111111-1111-1111-1111-111111111111` |
| `X-Service-Scopes` | `vapi:webhook` |
| `X-Vapi-Signature` | `sha256=<hmac-sha256-hex-digest>` |

### n8n calendar sync (`POST /webhooks/n8n/calendar-sync`)

| Header | Value |
|---|---|
| `X-Service-Name` | `n8n` |
| `X-Service-Clinic-Id` | `11111111-1111-1111-1111-111111111111` |
| `X-Service-Scopes` | `calendar:sync` |
| `X-N8N-Signature` | `sha256=<hmac-sha256-hex-digest>` |

---

## H. Signed Request Generation

Use the helper script to compute a webhook signature over a JSON payload:

```bash
# Sign an inline JSON string
python backend/scripts/sign_webhook_payload.py \
  --secret "$VAPI_WEBHOOK_SECRET" \
  --payload '{"clinic_id":"11111111-1111-1111-1111-111111111111","call_id":"local-test-call-1","event_type":"call.ended","action_required":false}'

# Sign a payload fixture file
python backend/scripts/sign_webhook_payload.py \
  --secret "$VAPI_WEBHOOK_SECRET" \
  --payload-file docs/integrations/local_payloads/vapi_call_event.json

python backend/scripts/sign_webhook_payload.py \
  --secret "$N8N_WEBHOOK_SECRET" \
  --payload-file docs/integrations/local_payloads/n8n_calendar_sync.json

# Output plain hex digest (no sha256= prefix)
python backend/scripts/sign_webhook_payload.py \
  --secret "$VAPI_WEBHOOK_SECRET" \
  --payload-file docs/integrations/local_payloads/vapi_call_event.json \
  --prefix false
```

The script prints only the signature to stdout. It never logs the secret.

---

## I. Example Local curl Requests

### Vapi call event webhook (using payload file)

```bash
VAPI_SIG=$(python backend/scripts/sign_webhook_payload.py \
  --secret "$VAPI_WEBHOOK_SECRET" \
  --payload-file docs/integrations/local_payloads/vapi_call_event.json)

curl -X POST http://127.0.0.1:8000/webhooks/vapi/call-event \
  -H "Content-Type: application/json" \
  -H "X-Service-Name: vapi" \
  -H "X-Service-Clinic-Id: 11111111-1111-1111-1111-111111111111" \
  -H "X-Service-Scopes: vapi:webhook" \
  -H "X-Vapi-Signature: $VAPI_SIG" \
  -d @docs/integrations/local_payloads/vapi_call_event.json
```

### n8n calendar sync webhook (using payload file)

```bash
N8N_SIG=$(python backend/scripts/sign_webhook_payload.py \
  --secret "$N8N_WEBHOOK_SECRET" \
  --payload-file docs/integrations/local_payloads/n8n_calendar_sync.json)

curl -X POST http://127.0.0.1:8000/webhooks/n8n/calendar-sync \
  -H "Content-Type: application/json" \
  -H "X-Service-Name: n8n" \
  -H "X-Service-Clinic-Id: 11111111-1111-1111-1111-111111111111" \
  -H "X-Service-Scopes: calendar:sync" \
  -H "X-N8N-Signature: $N8N_SIG" \
  -d @docs/integrations/local_payloads/n8n_calendar_sync.json
```

> **Note:** All payloads use deterministic local UUIDs from the seed script.
> They contain no real patient data and no real clinic data.

---

## J. Expected Results

| Condition | HTTP Status |
|---|---|
| Valid machine headers + valid HMAC signature | 200 — route processes |
| Missing signature header | 401 |
| Wrong/invalid signature | 401 |
| Signature env var not set | 503 |
| Wrong clinic_id in machine header | 403 |
| Wrong service name | 401 |
| Missing required scope | 403 |

---

## K. Stop Local PostgreSQL

```bash
docker compose -f docker-compose.postgres.yml down
```

> **WARNING:** Do not use `docker compose ... down -v` unless you intentionally want to delete the local database volume and all its data. The `-v` flag removes named volumes permanently.

---

## L. Confirmed Local Smoke Result

The full local smoke test passed after Module 50. See:
[`docs/integrations/LOCAL_SMOKE_RESULTS.md`](LOCAL_SMOKE_RESULTS.md)

**Summary of confirmed results:**

- `seed_local_data.py` — seeded 4 deterministic UUID rows successfully
- `POST /webhooks/vapi/call-event` with valid HMAC + valid machine auth → **HTTP 200 OK**
- `POST /webhooks/vapi/call-event` with bad signature (`sha256=wrong`) → **HTTP 401 Unauthorized**
- `POST /webhooks/n8n/calendar-sync` with valid HMAC + valid machine auth → **HTTP 200 OK**

The local signed Vapi and n8n webhook tests passed with seeded UUID data.
Real DB writes, HMAC signature verification, and machine auth all work end-to-end in the local environment.

---

## M. Real Vapi / n8n Setup Is Not Done Yet

This runbook covers **local testing only**.

Real Vapi dashboard configuration (webhook URL, signing secret) and real n8n workflow setup will be done in a later sprint once the local integration flow is confirmed stable.

Do not configure production Vapi or n8n endpoints until that sprint is reached.
