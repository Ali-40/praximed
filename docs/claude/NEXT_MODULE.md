# Architecture Checkpoint 15 — Staging Deployment Evidence Review

Status: pending Module 109 review.

## Context

Sprint 15 complete:
- Module 105 — Railway backend service creation runbook (READY)
- Module 106 — Railway PostgreSQL provisioning/migration runbook + evidence (BLOCKED/PENDING)
- Module 107 — Vercel frontend project creation runbook + evidence (BLOCKED/PENDING)
- Module 108 — Staging environment wiring runbook + evidence (BLOCKED/PENDING)
- Module 109 — Staging smoke execution PASS/BLOCKED evidence (BLOCKED/PENDING)
- Full suite: 2266/2266 passed

Sprint 15 produced the complete set of human-executable runbooks for fake-data staging
deployment. All runbooks are READY. All evidence documents are BLOCKED/PENDING because
no external staging services have been created yet.

Architecture Checkpoint 15 reviews Sprint 15 and decides the next step.

## Scope

Docs only. No deployment. No code changes. No real secrets.

### Decisions to make

1. **Stop-planning gate:** Sprint 15 has produced 5 complete human-executable runbooks
   covering every staging deployment step. No further planning documents are needed before
   manual service creation. The checkpoint should formally declare the planning phase complete
   and identify the exact first manual action for the developer.

2. **External service creation:** The next action is manual — the developer must:
   1. Create Railway backend service (follow `RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md`)
   2. Create Railway PostgreSQL (follow `RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md`)
   3. Create Vercel frontend (follow `VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md`)
   4. Wire environment variables (follow `STAGING_ENVIRONMENT_WIRING_RUNBOOK.md`)
   5. Execute staging smoke (follow `DEPLOYMENT_SMOKE_RUNBOOK.md`)
   6. Update evidence documents when services exist and smoke passes

3. **Production PHI launch:** Remains NO-GO. No staging smoke evidence = no production approval.

4. **Auth/session hardening (httpOnly cookie):** Scheduled after fake-data staging smoke PASS.
   Module 98 plan is complete. Do not implement until smoke evidence exists.

5. **Fabel 5/UX sprint:** Remains DEFERRED. Implement after staging topology confirmed and
   auth hardened.

6. **Appointment workflow expansion:** Remains DEFERRED.

### What checkpoint 15 should produce

1. `docs/architecture/ARCHITECTURE_CHECKPOINT_15_STAGING_DEPLOYMENT_EVIDENCE_REVIEW.md`

Sections:
1. Purpose — review Sprint 15; declare planning complete; identify first manual action
2. Sprint 15 deliverables review — list all 5 modules + 2266 tests
3. Evidence document status — BLOCKED/PENDING across all 5 evidence docs; confirm accurate
4. Planning-complete declaration — no further runbooks needed; next step is manual service creation
5. First manual action — exact first step: `RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md`
6. Production PHI launch — NO-GO; 12 blockers still open; staging smoke evidence required first
7. Auth/session hardening — GO after fake-data staging smoke; Module 98 plan ready
8. Fabel 5/UX — DEFERRED; criteria for starting
9. Appointment workflow expansion — DEFERRED
10. What this checkpoint does not authorize — production launch; auth changes; Fabel 5

2. Static contract tests for checkpoint 15 doc

3. `docs/claude/CURRENT_STATE.md` updated

4. `docs/claude/NEXT_MODULE.md` updated — Sprint 16 or user-driven external service creation

### 2. Create `docs/architecture/ARCHITECTURE_CHECKPOINT_15_STAGING_DEPLOYMENT_EVIDENCE_REVIEW.md`

### 3. Create `backend/tests/test_architecture_checkpoint_15_contract.py`

Static tests:
- Checkpoint doc exists
- Mentions Sprint 15
- Mentions planning complete
- Mentions first manual action / Railway backend runbook
- Mentions no further runbooks needed
- Mentions production PHI NO-GO
- Mentions staging smoke evidence required for production
- Mentions auth hardening after staging smoke
- Mentions Fabel 5 deferred
- Mentions appointment expansion deferred
- Mentions BLOCKED/PENDING evidence status
- Mentions Module 105/106/107/108/109
- No obvious real secrets in doc

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 109 (already done); record Checkpoint 15
- `docs/claude/NEXT_MODULE.md` — Sprint 16 / actual external service creation (user-driven)

## What not to do

- Do not create Railway or Vercel services
- Do not run migrations
- Do not add real secrets
- Do not implement httpOnly cookie auth
- Do not change CORS implementation
- Do not start Fabel 5/UX sprint
- Do not change DB schema or migration files
- Do not expand appointment workflow
- Do not fabricate smoke PASS evidence

## Acceptance

- `docs/architecture/ARCHITECTURE_CHECKPOINT_15_STAGING_DEPLOYMENT_EVIDENCE_REVIEW.md` created
- Static contract tests pass
- Full test suite passes (2266/2266 minimum)
- Commit: `Architecture Checkpoint 15 — Staging deployment evidence review`
