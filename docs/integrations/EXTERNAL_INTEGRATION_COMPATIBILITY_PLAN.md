# External Integration Compatibility Plan — PraxisMed

## A. Purpose

This plan prepares for real Vapi and n8n dashboard setup after local integration smoke success (Sprint 5 / Module 50–51).

The local backend integration layer is confirmed working:

- Local PostgreSQL, Alembic migrations, and seed data work.
- Runtime `asyncpg` pool startup works.
- Machine auth header validation (`X-Service-*`) works.
- HMAC-SHA256 webhook signature verification works.
- Signed Vapi and n8n webhooks return HTTP 200 with valid credentials.
- Invalid signatures return HTTP 401.

Before configuring real Vapi or n8n dashboards, this document identifies where the real external services may differ from our local convention, and what must be resolved before the first real webhook attempt.

---

## B. Current Local Backend Contract

### Vapi webhook

| Item | Value |
|---|---|
| Endpoint | `POST /webhooks/vapi/call-event` |
| `X-Service-Name` header | `vapi` |
| `X-Service-Clinic-Id` header | `<clinic UUID>` |
| `X-Service-Scopes` header | `vapi:webhook` |
| `X-Vapi-Signature` header | `sha256=<hmac-sha256-hex-digest>` |
| Env secret | `VAPI_WEBHOOK_SECRET` |
| Signature target | Raw request body bytes |

### n8n webhook

| Item | Value |
|---|---|
| Endpoint | `POST /webhooks/n8n/calendar-sync` |
| `X-Service-Name` header | `n8n` |
| `X-Service-Clinic-Id` header | `<clinic UUID>` |
| `X-Service-Scopes` header | `calendar:sync` |
| `X-N8N-Signature` header | `sha256=<hmac-sha256-hex-digest>` |
| Env secret | `N8N_WEBHOOK_SECRET` |
| Signature target | Raw request body bytes |

Both routes reject requests with missing or invalid signatures with HTTP 401.
Both routes reject requests with wrong machine headers with HTTP 401/403.
Both routes return HTTP 503 if the corresponding secret env var is not set.

---

## C. Current Local Proof

| Test | Result |
|---|---|
| Valid signed Vapi webhook (`POST /webhooks/vapi/call-event`) | HTTP 200 OK |
| Bad Vapi signature (`sha256=wrong`) | HTTP 401 Unauthorized |
| Valid signed n8n webhook (`POST /webhooks/n8n/calendar-sync`) | HTTP 200 OK |
| Local PostgreSQL with seeded UUID data | Working |
| asyncpg DB pool runtime startup | Working |
| Idempotent seed script | Working |

All results documented in `docs/integrations/LOCAL_SMOKE_RESULTS.md`.

---

## D. Vapi Compatibility Questions

Before configuring a real Vapi assistant or server, the following must be verified:

1. **HMAC signing** — Can Vapi send HMAC-SHA256 signatures on webhook requests? What version of signing does Vapi support natively?
2. **Signature header name** — What exact header name does Vapi use when sending webhooks? Does it match `X-Vapi-Signature` exactly, or does Vapi use a different header such as `x-vapi-secret` or a custom configurable header?
3. **Signature format** — Does Vapi's signature use `sha256=<hex>` format, or plain hex, or another format?
4. **Payload signed** — What does Vapi sign — the raw request body, or a subset of fields? Does Vapi include a timestamp in the signed content?
5. **Replay protection** — Does Vapi send timestamp or nonce headers to prevent replay attacks?
6. **Custom tool headers** — For Vapi custom tool calls (`POST /vapi/tools/*`), can Vapi include custom headers such as `X-Service-Name`, `X-Service-Clinic-Id`, `X-Service-Scopes`?
7. **Server webhook headers** — For Vapi server webhooks (`POST /webhooks/vapi/call-event`), can all required machine auth headers be configured in the Vapi dashboard?
8. **Tool vs webhook auth** — Do Vapi tool calls and Vapi server webhooks use the same credential mechanism, or are they configured separately?
9. **Request body shape** — Does Vapi's actual webhook payload shape match our current route schemas (`clinic_id`, `call_id`, `event_type`, `action_required`)?
10. **Local tunnel** — Does local Vapi testing require `vapi listen`, ngrok, Cloudflare Tunnel, or another tunneling solution to receive webhooks on a local machine?

---

## E. n8n Compatibility Questions

Before configuring a real n8n workflow, the following must be verified:

1. **Custom headers on HTTP Request nodes** — Can n8n HTTP Request nodes send arbitrary custom headers (`X-Service-Name`, `X-Service-Clinic-Id`, `X-Service-Scopes`, `X-N8N-Signature`) to our API?
2. **HMAC signing in n8n** — Can n8n sign request bodies with HMAC-SHA256 natively using a built-in Code or Function node before sending the HTTP request?
3. **Alternative auth mechanisms** — If n8n cannot easily produce HMAC-SHA256 signatures, should we consider Header auth (a shared static token) or a signed JWT token instead? Any change must be reviewed before implementation.
4. **Inbound vs outbound** — Our n8n route (`POST /webhooks/n8n/calendar-sync`) receives webhooks sent by n8n to PraxisMed (outbound from n8n). Confirm that n8n Webhook credentials (for inbound webhooks from external sources to n8n) are separate from this use case.
5. **Test vs production URL** — What is the exact difference between n8n's test webhook URL and production webhook URL? Does PraxisMed need to register both?
6. **Secrets storage in n8n** — How will local and production secrets (`N8N_WEBHOOK_SECRET`, `X-Service-Clinic-Id` value) be stored safely in the n8n workflow? Credentials manager, environment variables, or another mechanism?
7. **Payload format** — Does the n8n workflow send a body that matches our current schema (`clinic_id`, `provider`, `external_calendar_id`, `event_type`)?

---

## F. Compatibility Gap Analysis

| Area | Current backend expectation | Likely external reality | Risk | Recommendation |
|---|---|---|---|---|
| Vapi signature header | `X-Vapi-Signature: sha256=<hex>` | Vapi may use a different header name (e.g., `x-vapi-secret`) or no HMAC at all | High | Verify Vapi signing docs before configuring; make header name configurable if needed |
| Vapi signed payload format | Raw request body bytes | Vapi may sign a different representation or include timestamp in digest | High | Test with a real Vapi test call and inspect the actual header sent |
| Vapi machine headers | `X-Service-Name`, `X-Service-Clinic-Id`, `X-Service-Scopes` | Vapi likely does not send these by default; may support custom headers in dashboard | Medium | Verify Vapi dashboard for custom header configuration per webhook |
| Vapi tool request body | `clinic_id`, `action_required`, etc. | Vapi tool call bodies are structured by the tool schema; shape must be defined in Vapi | Medium | Review and align Vapi tool schema with our route schema before first real call |
| Vapi webhook request body | `clinic_id`, `call_id`, `event_type`, `action_required` | Vapi's native call event payload may have a different structure | High | Map Vapi's native event body to our schema via an adapter or update schema |
| n8n custom headers | All four required headers per request | n8n HTTP Request nodes support custom headers; should be feasible | Low | Configure headers explicitly in n8n workflow; test before relying on them |
| n8n HMAC signing | `X-N8N-Signature: sha256=<hex>` | n8n does not have built-in HMAC signing; must be done in a Code node | Medium | Write a Code node function to compute HMAC before the HTTP Request node |
| n8n test vs production URL | One stable endpoint | n8n uses separate test/production URLs during workflow development | Low | Register both; confirm which is active before real payloads |
| Public tunnel | Local FastAPI accessible from external services | ngrok or Cloudflare Tunnel required for local webhook delivery | Medium | Set up tunnel before any real dashboard test; rotate secrets after each session |
| Secrets management | `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET` in env | Local shell exports; production needs a secret manager | High | Do not use local secrets in production; configure a real secret manager before production deployment |

---

## G. Recommended Adapter Strategy

1. **Keep the local HMAC verifier** (`backend/app/core/webhook_signature.py` and `backend/app/api/dependencies/webhook_signature.py`). Do not remove or weaken it.

2. **Make the accepted signature header name configurable** if real Vapi or n8n use a different header than `X-Vapi-Signature` or `X-N8N-Signature`. This should be a controlled config change, not a security downgrade.

3. **Do not disable signature verification** to make real dashboards connect faster. A 401 during real setup is informative; skipping verification creates a permanent vulnerability.

4. **If Vapi supports configurable HMAC headers**: map its header name to our dependency, or make the expected header name an environment variable alongside the secret.

5. **If n8n cannot produce HMAC natively**: implement HMAC computation inside an n8n Code node using the `crypto` module, and pass the digest in the `X-N8N-Signature` header. If this is impractical, schedule an explicit review to consider JWT or static token auth as an alternative — do not improvise.

6. **Machine auth headers**: Keep `X-Service-*` headers for now. If real Vapi or n8n cannot send all required headers, introduce provider-specific dependencies after a deliberate review (Module 53 or later). Do not remove machine auth checks without review.

7. **Payload shape mismatches**: If real Vapi webhook bodies differ from our current schemas, add an adapter/transformer inside the route handler rather than weakening schema validation. Document the adapter explicitly.

---

## H. Public Tunnel Plan

- Use **ngrok** or **Cloudflare Tunnel** for local webhook delivery testing only.
- The tunnel URL must point to `http://127.0.0.1:8000` (local FastAPI).
- Do not start the tunnel without local env secrets set.
- Do not use real patient data in local tests.
- Do not reuse tunnel URLs across sessions without rotating secrets.
- Record the tunnel URL used during each test session and close the tunnel when done.
- Tunnel setup is not a production solution; production will use a real hostname behind TLS.

---

## I. Safe Real Setup Sequence

Follow this sequence strictly — do not skip or reorder steps:

1. Keep local PostgreSQL running (`docker compose -f docker-compose.postgres.yml up -d`).
2. Export all required local env secrets (`DATABASE_URL`, `VAPI_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`).
3. Start FastAPI locally (`python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`).
4. Expose the local server using a tunnel (ngrok or Cloudflare Tunnel). Record the tunnel URL.
5. Configure Vapi test assistant or server webhook URL with the tunnel URL only. Do not use production webhook URLs.
6. Configure Vapi HMAC/auth settings and any required custom headers in the Vapi dashboard.
7. Send one test Vapi call event. Inspect the full request (headers + body) received by FastAPI.
8. Verify: valid credentials → HTTP 200; invalid credentials → HTTP 401.
9. Configure n8n test workflow only. Point to the tunnel URL. Set custom headers and signing in the n8n workflow.
10. Send one test n8n calendar sync payload. Inspect headers and body.
11. Verify: valid credentials → HTTP 200; invalid credentials → HTTP 401.
12. Document the exact headers and body format observed from each provider.
13. Only after documenting actual external behavior, decide whether route/auth changes are needed.

---

## J. Do-Not-Do List

- **Do not use real patient data** in local or tunnel testing at any point.
- **Do not use production secrets** in local development environments.
- **Do not disable signature verification** to make a dashboard connect faster. Fix the root cause.
- **Do not expose unauthenticated endpoints** even temporarily.
- **Do not start frontend integration** before the real auth plan is documented and reviewed.
- **Do not mix local and production webhook URLs** in any dashboard configuration.
- **Do not reuse a tunnel session's secrets** in a new session without rotation.
- **Do not skip the compatibility gap review** before configuring real dashboards.

---

## K. Recommended Next Module

**Sprint 6 / Module 53 — Provider Header Compatibility Config**

Before configuring real dashboards, make the accepted signature header name and prefix configurable through environment variables in a controlled way — one env var per provider. This allows Vapi and n8n to be adapted to their actual header names without changing route logic or weakening signature verification.

This module should:

- Add `VAPI_SIGNATURE_HEADER` and `N8N_SIGNATURE_HEADER` env var support to the signature dependencies.
- Keep the default values matching the current local convention so no existing test breaks.
- Add a small number of tests verifying the configurable header name is read correctly.
- Not change any route logic, machine auth logic, or HMAC computation.

This is a minimal, targeted change that eliminates the highest-risk compatibility gap (header name mismatch) before real dashboards are touched.
