# Architecture Checkpoint 05 — External Integration Review

**Date:** Sprint 6 / Module 58 complete
**Scope:** Sprint 6 — Modules 52–58 (external integration compatibility, real Vapi tunnel, real n8n tunnel)
**Type:** External integration readiness review

---

## 1. Current Status

Sprint 6 is complete. Both the Vapi phone agent and n8n calendar sync have been tested end-to-end against a real local backend through a public ngrok tunnel and have returned successful responses.

The backend is **local-only and test-ready**. It is not production-deployed. All tests confirmed in this sprint used local test secrets and seeded deterministic UUIDs — no real patient data, no production credentials, no live hosted environment.

Full backend test suite: **1386/1386 passed**.

---

## 2. Completed External Integration Proof

### Vapi (Sprint 6 / Modules 55–57)

| Step | Result |
|---|---|
| Real Vapi webhook delivery reached ngrok | Confirmed |
| Real Vapi webhook delivery reached local FastAPI | Confirmed |
| HMAC-SHA256 signature accepted (`x-signature`, `{body}`, hex) | Confirmed |
| Machine auth alias headers accepted (`X-Vapi-Service-Name`, `X-Vapi-Clinic-Id`, `X-Vapi-Scopes`) | Confirmed |
| Payload adapter resolved missing `clinic_id` from machine auth | Confirmed |
| Payload adapter mapped `message.type` → internal `event_type` | Confirmed |
| Final HTTP response | **200 OK** |

Observed real Vapi payload root: `{"message": {"type": "end-of-call-report", ...}}`.
Prior failures (401 digest mismatch, 502 bad gateway, 400 missing clinic_id) were all resolved before the 200 result.

### n8n (Sprint 6 / Module 58)

| Step | Result |
|---|---|
| Real n8n HTTP Request node reached ngrok | Confirmed |
| Real n8n request reached local FastAPI | Confirmed |
| HMAC-SHA256 signature accepted (`X-Signature: sha256=...` over raw compact JSON) | Confirmed |
| Machine auth alias headers accepted (`X-N8N-Service-Name`, `X-N8N-Clinic-Id`, `X-N8N-Scopes`) | Confirmed |
| Calendar sync route processed real payload | Confirmed |
| Final HTTP response | **Success** |

Prior failure (digest mismatch) was fixed by computing the HMAC over the exact raw bytes transmitted by the HTTP Request node.

---

## 3. What Is Proven

| Capability | Evidence |
|---|---|
| Vapi can deliver real webhooks to PraxisMed | Real tunnel test, HTTP 200 |
| n8n can deliver real calendar sync payloads to PraxisMed | Real tunnel test, success |
| HMAC-SHA256 signature verification works against real providers | Both providers confirmed |
| Machine auth header aliases for Vapi and n8n work | Both providers confirmed |
| Provider alias config (Modules 53–54) is correct | Integration smoke tests passed |
| Real Vapi payload adapter (Module 56) handles production payload shape | Confirmed |
| Tenant isolation via `clinic_id` is enforced end-to-end | Confirmed — missing clinic_id rejected with 400 |
| Audit logging records machine webhook events | Covered by existing tests |
| Local PostgreSQL, Alembic migrations, seed data are stable | Confirmed across Sprint 5–6 |

---

## 4. What Is Not Proven

| Area | Status |
|---|---|
| Production deployment (real hostname, real TLS) | Not started |
| Production secrets management (secret manager, env injection) | Not started — only local shell exports used |
| Human authentication (doctor/admin login, JWT, session) | Not started |
| Frontend / clinic dashboard | Not started |
| Real patient data processing | Not tested and not permitted yet |
| Real Google Calendar OAuth workflow for n8n | Not started |
| Production Vapi assistant wired to a real phone number | Not tested |
| n8n production workflow with real calendar data | Not tested |
| Replay protection (timestamp/nonce checks) | Not implemented |
| Multi-tenant production routing (multiple real clinics) | Not tested beyond seed UUIDs |
| Rate limiting or abuse protection | Not implemented |

---

## 5. Security Review

### HMAC Signatures

- HMAC-SHA256 is enforced on all Vapi and n8n webhook routes via `backend/app/core/webhook_signature.py`.
- Missing signatures return HTTP 401. Invalid digests return HTTP 401. Missing secrets return HTTP 503.
- Provider alias configs (Module 53) accept controlled header name variants without weakening verification.
- **Gap**: No replay protection. A captured valid webhook request could be replayed within its validity window. Vapi does support optional timestamp headers but they are not yet used. This should be addressed before production.

### Machine Auth Headers

- All webhook and tool routes require machine auth (`X-Service-Name`, `X-Service-Clinic-Id`, `X-Service-Scopes`).
- Provider alias configs (Module 54) accept Vapi and n8n header name variants without weakening auth.
- Invalid service names return HTTP 401. Missing scopes return HTTP 403. Clinic mismatch returns HTTP 403.
- Conflicting alias values (same field, different values) are rejected with HTTP 401.
- **Gap**: Machine auth is header-based trust only. There is no cryptographic proof that the caller is actually Vapi or n8n — any caller who knows the header values and HMAC secret could spoof a request. In production, machine auth and HMAC secrets must be kept confidential and rotated.

### Tenant / Clinic Isolation

- All PHI routes enforce `clinic_id` from the auth context. Route-level `require_*` helpers check that the machine auth clinic matches the requested clinic.
- Missing `clinic_id` causes the request to fail (400 or 403 depending on path).
- The real Vapi payload adapter falls back to machine auth `clinic_id` when the payload omits it — this is correct because the machine auth credential already binds the caller to a specific clinic.

### Audit Logging

- All machine webhook events are recorded via `audit_logger` (Modules 42–44).
- Audit metadata for Vapi call events includes `event_type` only — no transcript, prompt, or artifact text.
- Audit records carry `actor_type: machine`, `clinic_id`, `resource_type`, and `severity`.

### Local Secrets Only

- All Sprint 6 tests used placeholder secrets (`local-vapi-secret-change-me`, etc.).
- No production credentials were used at any point.
- The Vapi dashboard test credential was named "PraxisMed Local HMAC Test" to make its test-only nature explicit.

---

## 6. Main Risks Before Production

| Risk | Severity | Notes |
|---|---|---|
| Local tunnel only — no real deployed hostname | High | ngrok URL is ephemeral; cannot be used for production |
| No production auth / JWT for human users | High | Doctors and admins have no login; dashboard cannot be built yet |
| No production secrets management | High | Secrets are local shell exports; must use a real secret manager before deployment |
| No replay protection | Medium | Captured valid HMAC signatures could be replayed; add timestamp/nonce validation before production |
| No frontend / dashboard | Medium | No way for clinic staff to view data, approve summaries, or manage appointments |
| No real Google Calendar OAuth | Medium | n8n calendar sync is tested with manual payloads; no live Google Calendar integration yet |
| No deployment pipeline | Medium | No Docker production image, no CI/CD, no cloud hosting |
| No real patient data allowed yet | High | Data governance, consent flows, and GDPR/DSGVO compliance work has not started |
| Machine auth is header trust only | Medium | HMAC + shared secret is the only binding; no PKI or OAuth client credential flow |
| No rate limiting | Low–Medium | Uncapped webhook delivery rate; no protection against misconfigured providers flooding the endpoint |

---

## 7. Recommended Next Sprint Options

### A. Production Auth / JWT Foundation
Build doctor/admin user accounts, password hashing, JWT issuance, and session refresh. This is the prerequisite for any frontend and for protecting PHI routes with human auth in addition to machine auth.

**Pros:** Unblocks frontend, unblocks real patient data handling.
**Cons:** Requires schema changes (users table), new auth middleware, and careful security design.

### B. Clinic Dashboard / Frontend Foundation
Build the Next.js frontend skeleton: login page, clinic overview, appointment queue, and doctor review workflow.

**Pros:** Makes the product visible and testable by clinic staff.
**Cons:** Blocked by option A — frontend needs human auth to be useful.

### C. Provider Workflow Hardening
Add replay protection (Vapi timestamp headers), Vapi tool route smoke test, n8n production workflow with real Google Calendar, and multi-clinic routing validation.

**Pros:** Closes remaining integration gaps.
**Cons:** Does not unblock the frontend or patient data handling.

### D. Deployment / Secrets Foundation
Set up a Docker production image, CI/CD pipeline, and a secrets manager (AWS Secrets Manager, Vault, or equivalent).

**Pros:** Required before any real production traffic.
**Cons:** Does not add product features visible to clinic staff.

---

## 8. Recommended Next Path

**Sprint 7 / Module 59 — Production Auth and User Session Foundation**

**Reason:** Human authentication is the highest-priority unblocked dependency. Without it:

- The clinic dashboard cannot be built (no login = no protected views).
- Doctors cannot be identified for PHI access or approval workflows.
- The audit log has no human actor entries — only machine actors.
- GDPR/DSGVO compliance work cannot begin (consent, access control, and data subject rights all require user identity).

The backend already has machine-to-machine auth (Modules 39–40) and tenant isolation (Modules 36–38). Adding human auth as a parallel trust model is the next logical layer before expanding features or building the frontend.

This sprint should:

- Add a `users` table (doctor, admin, viewer roles).
- Add secure password hashing (bcrypt or argon2).
- Add JWT access and refresh token issuance.
- Add a FastAPI `get_current_user` dependency protecting PHI routes.
- Add tests covering login, token refresh, and unauthorized access rejection.
- Not yet build the frontend — API-first, testable via curl or Postman.

After this module, the dashboard frontend (Option B) and deployment (Option D) become unblocked in parallel.
