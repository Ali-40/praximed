"""
PraxisMed compliance readiness gate — Sprint 19 / Module 130.

Provides a hard circuit-breaker that prevents production PHI processing until
explicit security and legal readiness criteria are met.

Environment variables consumed (never logged):
  ENVIRONMENT                    — local | staging | production  (default: local)
  PRODUCTION_COMPLIANCE_UNLOCKED — must be "true" / "1" / "yes" to allow production PHI
  AUTH_METHOD                    — must be "COOKIE_HTTPONLY" for production (default)
  PSEUDONYMIZATION_PEPPER        — optional in local/staging; required for production unlock

Usage as FastAPI route dependency (PHI-processing routes only):
    from backend.app.core.compliance import enforce_phi_safeguard
    @router.post("/some-phi-route", dependencies=[Depends(enforce_phi_safeguard)])

Do NOT apply to /health or /health/ready.
"""

from __future__ import annotations

import os

from fastapi import HTTPException, status

PRODUCTION = "production"
COOKIE_HTTPONLY = "COOKIE_HTTPONLY"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_environment() -> str:
    """Return the normalized ENVIRONMENT value (lowercase). Defaults to 'local'."""
    return _env("ENVIRONMENT", "local").lower()


def is_production() -> bool:
    """Return True only when ENVIRONMENT is explicitly set to 'production'."""
    return get_environment() == PRODUCTION


def is_production_compliance_unlocked() -> bool:
    """Return True only when PRODUCTION_COMPLIANCE_UNLOCKED is a truthy string."""
    return _truthy(os.getenv("PRODUCTION_COMPLIANCE_UNLOCKED"))


def get_auth_method() -> str:
    """Return the normalized AUTH_METHOD value (uppercase). Defaults to 'COOKIE_HTTPONLY'."""
    return _env("AUTH_METHOD", COOKIE_HTTPONLY).upper()


def get_default_clinic_language() -> str:
    """Return the DEFAULT_CLINIC_LANGUAGE env value. Defaults to 'de'."""
    val = _env("DEFAULT_CLINIC_LANGUAGE", "de").lower()
    return val if val else "de"


def get_supported_clinic_languages() -> list[str]:
    """Return the SUPPORTED_CLINIC_LANGUAGES env value split into a list. Defaults to ['de','en']."""
    raw = _env("SUPPORTED_CLINIC_LANGUAGES", "de,en")
    return [lang.strip().lower() for lang in raw.split(",") if lang.strip()]


def assert_production_auth_ready() -> None:
    """
    Raise AssertionError if running in production with a non-cookie auth method.

    In local/staging this is a no-op. Only fires when ENVIRONMENT=production.
    """
    if is_production() and get_auth_method() != COOKIE_HTTPONLY:
        raise AssertionError(
            "Production PHI processing requires AUTH_METHOD=COOKIE_HTTPONLY. "
            "Frontend token storage is not allowed for production PHI."
        )


def assert_production_compliance_ready() -> None:
    """
    Raise AssertionError if running in production without compliance unlock.

    Checks both auth method and the PRODUCTION_COMPLIANCE_UNLOCKED flag.
    In local/staging this is a no-op.
    """
    assert_production_auth_ready()
    if is_production() and not is_production_compliance_unlocked():
        raise AssertionError(
            "Production PHI processing is locked. Set "
            "PRODUCTION_COMPLIANCE_UNLOCKED=true only after security/legal readiness. "
            "Blockers: C3 secrets hardening, C4 PHI logging/redaction, C5 tenant isolation, "
            "C6 audit trail, C7 backup/restore, C8 legal/DSGVO review."
        )


async def enforce_phi_safeguard() -> None:
    """
    FastAPI dependency — blocks PHI-processing routes in production until compliance is unlocked.

    Apply as a route dependency on PHI-sensitive routes only:
        @router.post("/route", dependencies=[Depends(enforce_phi_safeguard)])

    Do NOT apply to /health or /health/ready.

    In local/staging: no-op (passes through).
    In production without unlock: raises HTTP 403 Forbidden.
    """
    try:
        assert_production_compliance_ready()
    except AssertionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Production PHI processing is blocked by the PraxisMed compliance readiness gate.",
        ) from exc
