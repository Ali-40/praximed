# PraxisMed — Compliance Readiness Gate

**Sprint 19 / Module 130**
**Date:** 2026-07-06
**Status:** Implemented — staging/local unblocked, production PHI remains NO-GO

---

## 1. Purpose

The PraxisMed compliance readiness gate is a hard backend circuit breaker that prevents
production PHI processing until explicit security and legal readiness criteria are met.

It is implemented in `backend/app/core/compliance.py` as a set of environment-driven helpers
and a FastAPI async dependency (`enforce_phi_safeguard`).

**This is not DSGVO certification.** It is a technical gate that prevents accidental
production PHI exposure during the staging and development phases.

---

## 2. Environment Variables

| Variable | Values | Default | Purpose |
|---|---|---|---|
| `ENVIRONMENT` | `local` / `staging` / `production` | `local` | Controls which checks are active |
| `PRODUCTION_COMPLIANCE_UNLOCKED` | `true` / `false` / unset | `false` | Must be explicitly `true` to allow production PHI |
| `AUTH_METHOD` | `COOKIE_HTTPONLY` | `COOKIE_HTTPONLY` | Must be `COOKIE_HTTPONLY` for production readiness |
| `PSEUDONYMIZATION_PEPPER` | any string | none | Pepper for HMAC-SHA256 PII pseudonymization — required for production |
| `DEFAULT_CLINIC_LANGUAGE` | BCP-47 tag | `de` | Default language for new clinic tenants |
| `SUPPORTED_CLINIC_LANGUAGES` | comma-separated BCP-47 | `de,en` | Supported clinic interface languages |

**Never commit secret values.** All sensitive env vars are managed via Railway secrets.

---

## 3. How It Works

### Local / Staging

`enforce_phi_safeguard()` is a no-op. All PHI-processing routes proceed normally.
Staging uses synthetic fake data only — no real patient data. Production PHI: NO-GO.

### Production (ENVIRONMENT=production)

`enforce_phi_safeguard()` checks two conditions before allowing a request:

1. **Auth method gate:** `AUTH_METHOD` must be `COOKIE_HTTPONLY`.
   - If another auth method is in use, `assert_production_auth_ready()` raises `AssertionError`.
   - Cookie-based HttpOnly session auth is required because JWT tokens in browser storage
     are vulnerable to XSS and are not safe for production PHI.

2. **Compliance unlock gate:** `PRODUCTION_COMPLIANCE_UNLOCKED` must be `true`.
   - If unset or `false`, `enforce_phi_safeguard()` raises `HTTP 403 Forbidden`.
   - This flag must only be set after completing all C3–C8 hardening blockers:
     - C3 — Secrets hardening
     - C4 — PHI logging/redaction hardening
     - C5 — Tenant isolation verification
     - C6 — Audit trail hardening
     - C7 — Backup/restore runbook
     - C8 — Legal / DSGVO review

---

## 4. API Reference

```python
from backend.app.core.compliance import (
    get_environment,          # → "local" / "staging" / "production"
    is_production,            # → bool
    is_production_compliance_unlocked,  # → bool
    get_auth_method,          # → "COOKIE_HTTPONLY" (or override)
    assert_production_auth_ready,       # raises AssertionError in prod with wrong auth
    assert_production_compliance_ready, # raises AssertionError in prod if not unlocked
    enforce_phi_safeguard,    # async FastAPI dependency → HTTP 403 in prod if locked
    get_default_clinic_language,        # → "de" (from DEFAULT_CLINIC_LANGUAGE)
    get_supported_clinic_languages,     # → ["de", "en"] (from SUPPORTED_CLINIC_LANGUAGES)
)
```

---

## 5. Route Wiring

`enforce_phi_safeguard` is applied as a router-level dependency on all PHI-processing routes:

| Router | Applied at |
|---|---|
| `/appointment-requests/*` | Router level |
| `/patients/*` | Router level |
| `/consultations/*` | Router level |
| `/clinical-workflows/*` | Router level |
| `POST /vapi/tools/capture-appointment-request` | Route level |

**Not applied to:**
- `GET /health`
- `GET /health/ready`
- `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`
- Vapi check-availability and suggest-slots (no persistent PHI capture)

---

## 6. Article 28/32 Readiness Status

This gate does NOT claim DSGVO/GDPR compliance. Article 28 (data processor agreements)
and Article 32 (technical/organisational measures) readiness requires:

- Completion of C3–C8 hardening blockers (security, PHI, audit, legal)
- Legal review and data processing agreement with clinic tenants
- External security assessment
- Production infrastructure hardening

**None of these are complete at this stage. Production PHI remains NO-GO.**

---

## 7. Safety Summary

| Constraint | Status |
|---|---|
| Fake/non-PHI staging data only | **ENFORCED** |
| No real patient data in staging | **ENFORCED** |
| Production PHI processing | **BLOCKED** — gate raises HTTP 403 |
| COOKIE_HTTPONLY auth required for production | **ENFORCED** |
| Explicit operator unlock required | **ENFORCED** — `PRODUCTION_COMPLIANCE_UNLOCKED=true` |
| DSGVO/Article 32 compliance | **NOT CLAIMED** — pending C8 legal review |
| No secrets committed to code | **CONFIRMED** |
