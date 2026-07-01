# Local Integration Runbook — PraxisMed

## A. Purpose

This runbook is for **local integration testing only**, before any real Vapi or n8n dashboard is configured.

It shows how to:
- Start local PostgreSQL and run Alembic migrations
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

---

## D. Required Local Environment Variables

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

## E. Start Backend Locally

```bash
# TODO: confirm exact uvicorn entry point once app startup is finalised
# Placeholder — replace with the actual command for this project:
# uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Wait until you see `Application startup complete` in the logs before sending requests.

---

## F. Machine Auth Headers

Every integration route requires machine auth headers in addition to the webhook signature.

### Vapi webhook (`POST /webhooks/vapi/call-event`)

| Header | Value |
|---|---|
| `X-Service-Name` | `vapi` |
| `X-Service-Clinic-Id` | `<clinic-uuid>` |
| `X-Service-Scopes` | `vapi:webhook` |
| `X-Vapi-Signature` | `sha256=<hmac-sha256-hex-digest>` |

### n8n calendar sync (`POST /webhooks/n8n/calendar-sync`)

| Header | Value |
|---|---|
| `X-Service-Name` | `n8n` |
| `X-Service-Clinic-Id` | `<clinic-uuid>` |
| `X-Service-Scopes` | `calendar:sync` |
| `X-N8N-Signature` | `sha256=<hmac-sha256-hex-digest>` |

---

## G. Signed Request Generation

Use the helper script to compute a webhook signature over a JSON payload:

```bash
# Sign an inline JSON string
python backend/scripts/sign_webhook_payload.py \
  --secret "$VAPI_WEBHOOK_SECRET" \
  --payload '{"clinic_id":"clinic-1","event_type":"call.started","call_id":"local-test-001"}'

# Sign a file
python backend/scripts/sign_webhook_payload.py \
  --secret "$N8N_WEBHOOK_SECRET" \
  --payload-file /tmp/calendar_payload.json

# Output plain hex digest (no sha256= prefix)
python backend/scripts/sign_webhook_payload.py \
  --secret "$VAPI_WEBHOOK_SECRET" \
  --payload '{"event":"test"}' \
  --prefix false
```

The script prints only the signature to stdout. It never logs the secret.

---

## H. Example Local curl Requests

### Vapi call event webhook

```bash
VAPI_PAYLOAD='{"clinic_id":"clinic-1","event_type":"call.started","call_id":"local-test-001"}'

VAPI_SIG=$(python backend/scripts/sign_webhook_payload.py \
  --secret "$VAPI_WEBHOOK_SECRET" \
  --payload "$VAPI_PAYLOAD")

curl -X POST http://127.0.0.1:8000/webhooks/vapi/call-event \
  -H "Content-Type: application/json" \
  -H "X-Service-Name: vapi" \
  -H "X-Service-Clinic-Id: clinic-1" \
  -H "X-Service-Scopes: vapi:webhook" \
  -H "X-Vapi-Signature: $VAPI_SIG" \
  -d "$VAPI_PAYLOAD"
```

### n8n calendar sync webhook

```bash
N8N_PAYLOAD='{"clinic_id":"clinic-1","provider":"google","external_calendar_id":"cal@example.com","event_type":"connection_upsert"}'

N8N_SIG=$(python backend/scripts/sign_webhook_payload.py \
  --secret "$N8N_WEBHOOK_SECRET" \
  --payload "$N8N_PAYLOAD")

curl -X POST http://127.0.0.1:8000/webhooks/n8n/calendar-sync \
  -H "Content-Type: application/json" \
  -H "X-Service-Name: n8n" \
  -H "X-Service-Clinic-Id: clinic-1" \
  -H "X-Service-Scopes: calendar:sync" \
  -H "X-N8N-Signature: $N8N_SIG" \
  -d "$N8N_PAYLOAD"
```

> **Note:** Use only safe fake local payloads. Do not include real patient data. Do not include real secrets in curl commands shown to others.

---

## I. Expected Results

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

## J. Stop Local PostgreSQL

```bash
docker compose -f docker-compose.postgres.yml down
```

> **WARNING:** Do not use `docker compose ... down -v` unless you intentionally want to delete the local database volume and all its data. The `-v` flag removes named volumes permanently.

---

## K. Real Vapi / n8n Setup Is Not Done Yet

This runbook covers **local testing only**.

Real Vapi dashboard configuration (webhook URL, signing secret) and real n8n workflow setup will be done in a later sprint once the local integration flow is confirmed stable.

Do not configure production Vapi or n8n endpoints until that sprint is reached.
