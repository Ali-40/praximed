# Architecture Checkpoint 11 — Post-Vapi Integration Direction Review

**Date:** 2026-07-03
**Sprint:** Sprint 11 complete (Modules 81–90)
**Backend tests:** 1625/1625 passed
**Status:** Local/test Vapi intake loop fully proven. Deciding next sprint direction.

---

## 1. Current Status

Sprint 11 delivered the full Vapi appointment intake loop and proved it end-to-end
with a real live test assistant. All evidence gaps from Architecture Checkpoint 10
are closed. The codebase is stable, tested, and locally demonstrated.

**The sprint 11 integration result:**

```
Real Vapi test assistant
  → called capture_appointment_request server tool
  → ngrok forwarded POST /vapi/tools/capture-appointment-request
  → machine auth verified (X-Vapi-Service-Name, X-Vapi-Clinic-Id, X-Vapi-Scopes: vapi:tool)
  → adapt_vapi_tool_call_body normalised nested payload
  → clinic_ref resolved from X-Vapi-Clinic-Id header (not patient-supplied arguments)
  → appointment_request created: source=vapi, status=new, action_required=True
  → dashboard showed row; staff clicked Confirm
  → PATCH /appointment-requests/{id}/status → status=confirmed
  → Confirm button disappeared; no auto-confirmation; no calendar booking
```

This checkpoint reviews what was built across Sprint 11, the current security posture,
the remaining gaps, and the recommended next direction.

---

## 2. Proven End-to-End Flow

| Step | Proven | Evidence |
|---|---|---|
| Real Vapi test assistant calls `capture_appointment_request` | YES | Module 90 — Vapi tool logs, ngrok POST |
| ngrok forwards request to local backend | YES | Module 89–90 |
| Backend accepts nested `message.toolCallList` shape | YES | Modules 88–90 |
| `clinic_ref` resolved from machine auth header, not body | YES | Module 88 unit tests + Module 90 live |
| Appointment request created: `source=vapi`, `status=new`, `action_required=True` | YES | Modules 85–90 |
| `caller_phone` from `message.call.customer.number` | YES | Module 88 unit test 31 + Module 89 |
| Dashboard row visible after Vapi intake | YES | Modules 86–90 |
| Staff clicks Confirm; status new → confirmed | YES | Modules 82–90 |
| Confirm button disappears on confirmed rows | YES | Modules 82–90 |
| No auto-confirmation by AI at any layer | YES | Service docstring + code + all smokes |
| No calendar booking on Confirm | YES | All smokes |
| Other dashboard sections stable throughout | YES | All smokes |

---

## 3. Security Posture

### 3.1 What Is Enforced

| Concern | Status |
|---|---|
| JWT auth protects all PHI routes (`/patients`, `/consultations`, `/appointment-requests`, `/notifications`) | ACTIVE — `get_current_user` dependency on all PHI routes |
| Machine auth protects Vapi/n8n-style routes (`/vapi/tools/*`, `/webhooks/*`, `/calendar/*`) | ACTIVE — `get_machine_auth_context` + `require_vapi_tool_access` |
| Tenant isolation — `clinic_id` enforced on all routes | ACTIVE — all queries filter by `clinic_id` |
| `clinic_ref` in Vapi tool call always from machine auth (`X-Vapi-Clinic-Id`) | ACTIVE — `adapt_vapi_tool_call_body` enforces; patient-supplied clinic_ref silently ignored |
| Staff Confirm requires human JWT (Bearer token in `Authorization` header) | ACTIVE — `PATCH /appointment-requests/{id}/status` requires `get_current_user` |
| Password storage — bcrypt hash; no plaintext | ACTIVE — `password_hashing.py` |
| Audit logging on PHI mutations | ACTIVE — `audit_logger` on all mutation routes |
| HMAC signature verification on webhooks (`/webhooks/vapi/*`, `/webhooks/n8n/*`) | ACTIVE — Module 47 |
| CORS — explicit allowed origins only; no wildcard | ACTIVE — `FRONTEND_CORS_ORIGINS` env or localhost defaults |
| No secrets in committed code or docs | CONFIRMED throughout |

### 3.2 What Is Not Yet Production-Safe

| Gap | Risk |
|---|---|
| JWT in `sessionStorage` | `sessionStorage` is accessible to JavaScript — XSS risk; httpOnly cookie path not built |
| No token refresh | Expired tokens cause generic errors with no auto-redirect |
| `DATABASE_URL` hardcoded in local `.env` files / shell exports | Needs secrets manager or platform env injection for production |
| `JWT_SECRET_KEY`, machine auth secrets, webhook secrets — local-dev values | Must be rotated and injected securely before production |
| CORS `FRONTEND_CORS_ORIGINS` — defaults to `localhost:3000` | Production domain must be set explicitly |
| Vapi tool URL — currently ngrok (`https://<id>.ngrok-free.app/...`) | ngrok is ephemeral; production needs a stable HTTPS URL |
| No HTTPS termination in the app | Relies on reverse proxy (not yet configured) |
| No production DB | Local Docker PostgreSQL; production needs a managed DB service |
| No CI/CD pipeline | No automated test runs on push; no deployment automation |
| No production build for frontend | `npm run dev` only; no `next build` / production server |
| `sessionStorage` auth | Tokens lost on browser close; no "remember me" path |

### 3.3 No Security Regressions

All security measures from Sprints 1–10 remain active. Sprint 11 added:
- Machine auth scope enforcement (`vapi:tool` singular)
- Adapter security boundary (patient payload cannot select tenant)
- Raw payload stored for audit trail but never logged

---

## 4. Current Architecture State (Relevant Components)

### 4.1 Backend (`main.py`)

| Component | Current State | Production Gap |
|---|---|---|
| `DATABASE_URL` | Read from env; pool set to None if absent (returns 503) | Must be production DB URL |
| `FRONTEND_CORS_ORIGINS` | Env override or localhost defaults | Must include production frontend domain |
| `ClinicConfigLoader` | Disk config from `backend/tenants/configs/{clinic_id}/clinic_config.json` | Production config storage strategy needed |
| CORS `allow_headers` | `["Content-Type", "Authorization"]` | Sufficient for current flows |
| No HTTPS | App serves plain HTTP; relies on reverse proxy | Nginx / Caddy / cloud LB required |
| Health route | `GET /health` returns `{"status": "ok"}` | Suitable for basic readiness probes |

### 4.2 Frontend (`lib/api.ts`)

| Component | Current State | Production Gap |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Env var or `http://127.0.0.1:8000` fallback | Must point to production backend URL |
| `Authorization: Bearer <token>` | Token from `sessionStorage` | httpOnly cookie path not built |
| API base URL hardcoded fallback | `http://127.0.0.1:8000` | Must be overridden via env for production |

### 4.3 Secrets Required at Runtime

| Secret | Used By | Current State |
|---|---|---|
| `DATABASE_URL` | DB pool | Local Docker; must be production DB |
| `JWT_SECRET_KEY` | JWT issue/verify | Local-dev value; must be rotated |
| `VAPI_WEBHOOK_SECRET` | HMAC on `/webhooks/vapi/*` | Local-dev value |
| `N8N_WEBHOOK_SECRET` | HMAC on `/webhooks/n8n/*` | Local-dev value |
| `INTERNAL_WEBHOOK_SECRET` | Internal webhooks | Local-dev value |
| `MACHINE_SERVICE_SECRET` | Machine auth | Local-dev value |
| `FRONTEND_CORS_ORIGINS` | CORS middleware | Localhost; needs production domain |

---

## 5. Remaining Strategic Options

### Option A — Production Deployment Preparation (Recommended)

**What:** Inventory all deployment blockers, map required secrets and env vars, define
the production DB strategy, plan the HTTPS/domain config, and create a deployment
runbook for the first real deployment.

**Why first:** The core local/test integration loop is proven. Before expanding features
or redesigning the UI, the project needs clarity on what production deployment actually
requires — secrets, infrastructure, DB migration plan, CORS domains, Vapi production URL,
and operational risks. Without this inventory, feature work may be built on assumptions
that are incompatible with the target deployment environment.

**What it is not:** This is an inventory and plan phase — not a full production launch.
The output is a runbook and a blockers list, not a deployed system.

### Option B — Appointment Workflow Expansion

**What:** Add Reject action (`status: "rejected"`), Assign to doctor, mark-handled
flag, appointment detail drawer/page, and audit trail visibility in the dashboard.

**Why defer:** The backend routes for status transitions already exist (Modules 17 + 64).
This is valuable for clinic staff workflow completeness but not a prerequisite for
production readiness. Best built after deployment blockers are mapped, so the expanded
workflow is built for the target environment.

### Option C — Doctor-Facing Frontend UX Sprint

**What:** Evaluate Fabel 5 / Claude-related frontend generation tooling. Upgrade the
clinic dashboard from functional → premium and user-friendly. Better cards, tables,
action feedback, status transitions, typography.

**Why defer:** The dashboard is functional and browser-smoke confirmed. A UI polish
sprint is high-value for stakeholder demos and pilot credibility, but it should happen
after the production readiness inventory is done — otherwise UI quality investments
are made before deployment assumptions are clear. This remains a confirmed future sprint
(noted by user in Module 89).

---

## 6. Recommendation

**Sprint 12 — Production Deployment Readiness Inventory**

Before any production launch, feature expansion, or major UI work, map every deployment
blocker and requirement. The recommended Sprint 12 sequence:

| Module | Description |
|---|---|
| 91 | Production Deployment Readiness Inventory — env vars, secrets, infrastructure components |
| 92 | Environment and Secrets Contract — define which secrets are required, how they are injected, and what the `.env.example` for production looks like |
| 93 | Production CORS/Auth/Domain Plan — production frontend URL, backend URL, CORS policy, httpOnly cookie strategy |
| 94 | Deployment Smoke Runbook — step-by-step runbook for the first production deployment |
| Checkpoint 12 | Production Readiness Review — go/no-go decision for first real deployment |

**After Sprint 12:** With the deployment picture clear, Option C (UX sprint with Fabel 5
evaluation) or Option B (workflow expansion) can proceed with confidence.

---

## 7. Deferred Items

| Item | Deferred Until |
|---|---|
| Fabel 5 / premium frontend UX sprint | After Sprint 12 production readiness inventory |
| Appointment workflow expansion (Reject, Assign, Archive) | After production deployment blockers mapped |
| httpOnly cookie JWT session | Sprint 12 (Option C in Auth/Domain Plan) |
| Token refresh | Sprint 12 or 13 |
| Calendar handoff on Confirm | Future module |
| Patient notification on Confirm | Future module |
| Production Vapi assistant configuration | Sprint 12 runbook item |
| CI/CD pipeline | Sprint 12 or dedicated DevOps sprint |

---

## 8. Sprint Summary (all sprints)

| Sprint | Scope | Modules | Tests at End |
|---|---|---|---|
| Sprint 1 | Backend API foundation | 1–23 | 545 |
| Sprint 2 | Clinical documentation engine | 24–34 | 908 |
| Sprint 3 | Clinical workflow API routes + access control | 35–40 | 1083 |
| Sprint 4 | Database migration + audit logging | 41–44 | 1193 |
| Sprint 5 | Local PostgreSQL + smoke test | 45–51 | 1312 |
| Sprint 6 | External integration compatibility | 52–58 | 1386 |
| Sprint 7 | Production auth and JWT wiring | 59–65 | 1461 |
| Sprint 8 | Frontend dashboard foundation | 66–71 | 1521 |
| Sprint 9 | Local runtime smoke, CORS, browser demo | 72–77 | 1547 |
| Sprint 10 | Dashboard demo polish | 78–80 | 1560 |
| Sprint 11 | Vapi appointment intake loop | 81–90 | 1625 |
