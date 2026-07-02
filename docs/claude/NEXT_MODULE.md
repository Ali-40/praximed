# Sprint 6 / Module 58 — Real n8n Tunnel Smoke Test Evidence

Status: pending manual n8n setup.

Follow the n8n test plan from `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` Section 7.

Steps:

1. Start the full local stack (Docker PostgreSQL, Alembic migrations, seed data, FastAPI).
2. Start ngrok to expose `http://127.0.0.1:8000`.
3. In n8n, create a test workflow with an HTTP Request node pointing at `https://<tunnel-base>/webhooks/n8n/calendar-sync`.
4. Add a Code node to compute HMAC-SHA256 over the request body and set `X-Signature` header.
5. Set machine auth headers: `X-N8N-Service-Name`, `X-N8N-Clinic-Id`, `X-N8N-Scopes`.
6. Trigger the workflow and inspect the response.

Record:

- HTTP response status.
- Whether n8n can produce HMAC-SHA256 via a Code node.
- Whether machine auth headers are correctly configured and accepted.
- Whether any payload or header adapter changes are needed.
- Full evidence in `docs/integrations/REAL_N8N_TUNNEL_SMOKE_RESULTS.md` (to be created).
