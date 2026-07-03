# Sprint 13 / Module 99 — Production Deployment Execution Plan

Status: pending Module 98 review.

## Context

Sprint 13 documentation set is now complete:
- Module 95: Staging topology (Railway + Vercel)
- Module 96: Staging environment variable matrix
- Module 97: Staging deployment dry-run checklist
- Module 98: Auth/session hardening implementation plan

The staging dry-run checklist (Module 97) is ready to execute. The auth hardening plan
(Module 98) is ready for Sprint 14 implementation.

Before the Sprint 13 Checkpoint, there is one remaining planning artifact: a
**production deployment execution plan** that sequences the remaining milestones from
staging deployment through production PHI launch, covering what must happen in what
order and what gate each step requires.

Module 99 is docs-first. No deployment execution. No code changes. No production secrets.

## Scope

### 1. Read and audit current state

Read:
- `docs/architecture/ARCHITECTURE_CHECKPOINT_12_PRODUCTION_READINESS_REVIEW.md` — 12 production blockers
- `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` — staging gate
- `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` — staging env vars
- `docs/security/AUTH_SESSION_HARDENING_IMPLEMENTATION_PLAN.md` — auth migration plan
- `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` — all-tier env contract
- `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` — smoke runbook
- `docs/claude/CURRENT_STATE.md`

### 2. Create `docs/deployment/PRODUCTION_DEPLOYMENT_EXECUTION_PLAN.md`

Sections:
1. **Purpose** — sequence-of-events plan from staging deployment to production PHI launch; no execution in this module
2. **Current status** — what is complete (local loop proven; staging docs complete); what is NOT done (staging not deployed; auth not hardened; production not ready)
3. **Production blockers tracker** — the 12 blockers from Checkpoint 12; track which are resolved by Sprint 13 docs; which remain open
4. **Milestone sequence** — table of milestones from staging deployment to production PHI launch; each with go/no-go gate and sprint estimate
5. **Milestone 1: Staging deployment** — execute Module 97 dry-run checklist; confirm staging smoke passes; go/no-go gate
6. **Milestone 2: Staging smoke validation** — run smoke runbook against staging; capture evidence; go/no-go gate
7. **Milestone 3: Auth/session hardening** — implement Module 98 plan; cookie auth on staging; re-run smoke; go/no-go gate
8. **Milestone 4: Production domain and TLS** — stable production HTTPS domains; TLS certs; DNS; go/no-go gate
9. **Milestone 5: Production secrets provisioning** — production high-entropy secrets in production secret manager; go/no-go gate
10. **Milestone 6: Production database** — managed PostgreSQL with backups and PITR; migrations applied; go/no-go gate
11. **Milestone 7: Production Vapi assistant** — production Vapi assistant pointing at production HTTPS URL; no ngrok; go/no-go gate
12. **Milestone 8: Legal/GDPR/compliance review** — Austrian healthcare data protection review; `raw_payload` PHI policy; go/no-go gate (hard blocker)
13. **Milestone 9: CI/CD pipeline** — automated test gate on push; deployment automation; go/no-go gate
14. **Milestone 10: Production monitoring** — APM, structured logs, alerting, on-call; go/no-go gate
15. **Milestone 11: Production PHI launch** — all gates passed; architecture checkpoint; go/no-go decision
16. **Explicit deferrals** — what is NOT in scope for any of the above milestones
17. **Next step** — Architecture Checkpoint 13: Sprint 13 Go/No-Go Review

### 3. Static contract tests

Create `backend/tests/test_production_deployment_execution_plan_contract.py`:
- Plan doc exists
- Mentions staging deployment
- Mentions staging smoke
- Mentions auth/session hardening (httpOnly cookie)
- Mentions production domain and TLS/HTTPS
- Mentions production secrets
- Mentions production database / PostgreSQL
- Mentions production Vapi assistant
- Mentions legal/GDPR/compliance review
- Mentions CI/CD pipeline
- Mentions production monitoring
- Mentions go/no-go gates
- Mentions production PHI launch is blocked until all gates pass
- Mentions no deployment in this module
- Mentions architecture checkpoint 13
- Confirms no obvious real secrets in doc

### 4. Update docs

- `docs/claude/CURRENT_STATE.md` — record Module 99
- `docs/claude/NEXT_MODULE.md` — Architecture Checkpoint 13: Sprint 13 Go/No-Go Review

## What not to do

- Do not execute any deployment
- Do not provision real infrastructure
- Do not add real production secrets or real domain names
- Do not change backend/frontend code
- Do not implement the httpOnly cookie auth (that is Sprint 14)
- Do not start the Fabel 5/UX sprint

## Acceptance

- `docs/deployment/PRODUCTION_DEPLOYMENT_EXECUTION_PLAN.md` created
- Contract tests pass
- Full test suite passes (1892/1892 minimum)
- Commit: `Sprint 13 / Module 99 — Production deployment execution plan`
