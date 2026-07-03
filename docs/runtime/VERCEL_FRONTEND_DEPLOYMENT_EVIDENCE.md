# Vercel Frontend Deployment Evidence — PraxisMed

**Date:** 2026-07-03
**Sprint:** Sprint 15 / Module 107
**Status:** BLOCKED/PENDING — Vercel frontend project has not yet been created

---

## 1. Purpose

This document records the actual evidence from creating and deploying the PraxisMed
frontend to Vercel for fake/non-PHI staging.

**Accuracy policy:** No evidence step is marked PASS without real proof from a real
Vercel project deployment. No evidence is fabricated. If a step has not been executed
against a real Vercel service, its status is PENDING or BLOCKED.

Staging uses fake/non-PHI data only. No production frontend. No real patient data.
No production secrets in Vercel env.

---

## 2. Current Result

**Overall result: BLOCKED/PENDING**

A Vercel frontend project has not yet been created and deployment evidence has not been
provided. This result is accurate — it is not a failure. The runbook
(`VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md`) defines all steps required to move this
document to PASS.

This document will be updated to PASS when:
1. Vercel project is created and linked to the GitHub repo
2. Root directory is confirmed set to `frontend`
3. `NEXT_PUBLIC_API_BASE_URL` is set to the Railway backend HTTPS URL
4. First deploy succeeds (green build status in Vercel dashboard)
5. Vercel URL (*.vercel.app) is captured
6. Browser smoke confirms the login page renders and no console errors appear
7. Sanitized evidence is captured for each step above

---

## 3. Preconditions Available / Missing

| Precondition | Status | Notes |
|---|---|---|
| Railway backend service exists (Module 105) | **PENDING** | Runbook published; service not yet confirmed created |
| Railway backend HTTPS URL known | **PENDING** | Required for `NEXT_PUBLIC_API_BASE_URL` |
| Railway PostgreSQL provisioned (Module 106) | **PENDING** | Runbook published; DB not yet provisioned |
| Vercel account available | **UNKNOWN** | Not confirmed |
| GitHub repo accessible from Vercel | **UNKNOWN** | Not confirmed |
| `NEXT_PUBLIC_API_BASE_URL` value ready | **PENDING** | Depends on Railway backend URL |

**Repo-side readiness (no external services required):**

| Item | Status |
|---|---|
| `frontend/package.json` — `"build": "next build"` | READY |
| `frontend/next.config.js` — no `output: 'standalone'` | READY |
| `frontend/.env.example` — `NEXT_PUBLIC_API_BASE_URL` documented | READY |
| Next.js 14.2.3 (auto-detected by Vercel) | READY |
| No `vercel.json` needed | READY |
| No backend secrets in frontend env | READY |

---

## 4. Deployment Evidence Table

| Evidence Item | Evidence Available? | Current Value | Status |
|---|---|---|---|
| Vercel project name | Not available yet | — | PENDING |
| Vercel URL (*.vercel.app) | Not available yet | — | PENDING |
| Root directory setting confirmed as `frontend` | Not available yet | — | PENDING |
| `NEXT_PUBLIC_API_BASE_URL` env var name confirmed | Not available yet | — | PENDING |
| `NEXT_PUBLIC_API_BASE_URL` value (Railway HTTPS URL) | Not available yet | — | PENDING |
| Build status (success/failure) | Not available yet | — | PENDING |
| Commit SHA deployed | Not available yet | — | PENDING |
| Build log snippet (sanitized) | Not available yet | — | PENDING |
| Login page renders in browser | Not available yet | — | PENDING |
| No backend secrets in Vercel env (confirmed) | Not available yet | — | PENDING |
| `FRONTEND_CORS_ORIGINS` dependency noted | Not available yet | — | PENDING |
| No real patient data in deployment | Not available yet | — | PENDING |
| No production secrets in Vercel env | Not available yet | — | PENDING |
| Module 108 CORS wiring ready to proceed | Not available yet | — | PENDING |

---

## 5. Blockers

The following external actions must be completed before any evidence row can be captured.
All require manual developer action.

| # | Blocker | Level |
|---|---|---|
| 1 | Railway backend service not yet created (Module 105 prerequisite) | **HIGH** |
| 2 | Railway backend HTTPS URL not yet known | **HIGH** |
| 3 | Railway PostgreSQL not yet provisioned (Module 106 prerequisite) | **HIGH** |
| 4 | Vercel project not yet created | **HIGH** |
| 5 | `NEXT_PUBLIC_API_BASE_URL` not yet set in Vercel env | **HIGH** |
| 6 | First Vercel deploy not yet triggered | **HIGH** |
| 7 | Vercel URL (*.vercel.app) not yet assigned | **HIGH** |
| 8 | `FRONTEND_CORS_ORIGINS` not yet set on Railway (Module 108) | MEDIUM |

---

## 6. Next Evidence Needed

To update this document from BLOCKED/PENDING to PASS, the developer must:

1. Complete Module 105 (Railway backend service creation) — obtain Railway HTTPS backend URL
2. Complete Module 106 (Railway PostgreSQL provisioning and migration)
3. Follow `VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` Sections 3–8
4. Capture each evidence item from Section 9 of that runbook
5. Update this document with real values
6. Confirm no secrets or PII appear in any recorded evidence

Once this document is updated to PASS, proceed to Module 108
(Staging Environment Wiring Evidence — set `FRONTEND_CORS_ORIGINS` on Railway).
