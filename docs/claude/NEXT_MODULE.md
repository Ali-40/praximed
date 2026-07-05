# Sprint 17 / Module 119 — Production Hardening Gap Review

Status: pending structured review of production readiness gaps identified in Architecture Checkpoint 16.

## Context

Architecture Checkpoint 16 complete:
- Sprint 16 fake-data staging core: FAKE-DATA STAGING CORE PASS
- Full deployed loop confirmed: Vapi → Railway backend → Railway PostgreSQL → Vercel dashboard → staff Confirm
- n8n staging: PENDING/DEFERRED
- Production PHI readiness: NO-GO
- Full test suite: 2468/2468 passed (+ Architecture Checkpoint 16 contract tests)
- Commit: f602612 (Module 118B)

## Primary Recommendation

**Sprint 17 / Module 119 — Production Hardening Gap Review**

Before production use, clinic demos with real patients, or onboarding real data, the
project needs a structured review of production hardening gaps. This module produces a
prioritized, actionable module plan for closing those gaps.

## Scope

Docs only. No runtime code changes. No deployment changes. No secrets. No production data.

## What Module 119 should deliver

### 1. Gap inventory

Review each item from Architecture Checkpoint 16 Section 6 and produce a gap record:

| Gap | Current state | Risk level | Recommended module(s) |
|---|---|---|---|
| Production auth/session hardening (httpOnly cookie for JWT) | sessionStorage (fake-data only; XSS-accessible) | HIGH | Module 120+ |
| Production secrets rotation | Staging secrets still in use | HIGH | Module 120+ |
| PHI/compliance review (GDPR/HIPAA) | Not reviewed | HIGH | Module 120+ |
| Custom domain | Vercel/Railway default URLs | MEDIUM | Module 120+ |
| Monitoring / logging / alerting / rollback | Not configured | MEDIUM | Module 120+ |
| Real clinic onboarding flow | No admin workflow | MEDIUM | Module 121+ |
| n8n staging workflow | PENDING/DEFERRED | LOW | Module 122+ (optional) |
| UI/UX polish (Fabel 5 or equivalent) | Deferred | LOW | Separate UX sprint |

### 2. Ordered module plan

Produce a recommended ordered sprint/module plan (Sprint 17+) that addresses the HIGH
priority items before any production or PHI-bearing use.

### 3. Production NO-GO confirmation

Explicitly confirm that the following must be true before production PHI access:

- httpOnly cookie auth replaces sessionStorage JWT
- JWT_SECRET_KEY, VAPI_WEBHOOK_SECRET, DATABASE_URL rotated to fresh production secrets
- PHI/compliance review complete
- Railway log stream sanitized (no secrets or PII in logs)
- Rollback path confirmed

## What not to do

- Do not implement httpOnly cookie auth in this module (plan only)
- Do not deploy to production
- Do not start Fabel 5/UX sprint
- Do not configure n8n in this module (it is the alternative path below)
- Do not record secrets
- Do not use real patient data

## Alternative path

**Sprint 16 / Module 119 — n8n Staging Workflow Wiring Evidence**

Choose this instead of the Production Hardening Gap Review only if n8n is immediately
needed for a demo or integration milestone. n8n staging does not unblock production PHI
access. Both paths are available — the recommendation is to address production hardening
first.

## Acceptance

- Production hardening gap inventory created
- Ordered module plan (Sprint 17+) produced
- Production PHI NO-GO explicitly confirmed with gap conditions
- Full tests pass
- Commit: `Sprint 17 / Module 119 — Production hardening gap review`
