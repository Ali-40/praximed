"""
Static contract tests for Sprint 13 / Module 98 — Auth/Session Hardening Plan.

Verifies:
- Plan document exists and covers all required sections
- Current and target auth architectures are described
- Cookie strategy, CSRF, logout, backend/frontend changes are present
- Staging cross-domain risk is addressed
- No implementation in this module (plan only)
- No obvious real secrets in the document
"""

from __future__ import annotations

import os
import re


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

_PLAN_PATH = os.path.join(
    _REPO_ROOT, "docs", "security", "AUTH_SESSION_HARDENING_IMPLEMENTATION_PLAN.md"
)


def _plan() -> str:
    with open(_PLAN_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Document exists and is non-trivial
# ---------------------------------------------------------------------------


def test_auth_session_hardening_plan_exists() -> None:
    assert os.path.isfile(_PLAN_PATH), f"Plan not found at {_PLAN_PATH}"


def test_auth_session_hardening_plan_not_empty() -> None:
    assert len(_plan()) > 5000


# ---------------------------------------------------------------------------
# 2. sessionStorage risk documented
# ---------------------------------------------------------------------------


def test_plan_mentions_session_storage_risk() -> None:
    text = _plan()
    assert "sessionStorage" in text and (
        "risk" in text.lower()
        or "xss" in text.lower()
        or "blocker" in text.lower()
    )


def test_plan_mentions_xss() -> None:
    text = _plan()
    assert "xss" in text.lower() or "cross-site script" in text.lower()


# ---------------------------------------------------------------------------
# 3. httpOnly cookie
# ---------------------------------------------------------------------------


def test_plan_mentions_httponly() -> None:
    text = _plan()
    assert "httponly" in text.lower() or "HttpOnly" in text


def test_plan_mentions_secure_attribute() -> None:
    text = _plan()
    assert "secure" in text.lower() and "cookie" in text.lower()


def test_plan_mentions_samesite() -> None:
    text = _plan()
    assert "samesite" in text.lower() or "SameSite" in text


def test_plan_mentions_set_cookie_on_login() -> None:
    text = _plan()
    assert (
        "set_cookie" in text.lower()
        or "Set-Cookie" in text
        or "set cookie" in text.lower()
    )


# ---------------------------------------------------------------------------
# 4. Logout route
# ---------------------------------------------------------------------------


def test_plan_mentions_post_auth_logout() -> None:
    text = _plan()
    assert "/auth/logout" in text


def test_plan_mentions_delete_cookie_on_logout() -> None:
    text = _plan()
    assert (
        "delete_cookie" in text.lower()
        or "max-age=0" in text.lower()
        or "Max-Age=0" in text
    )


# ---------------------------------------------------------------------------
# 5. Frontend changes
# ---------------------------------------------------------------------------


def test_plan_mentions_credentials_include() -> None:
    text = _plan()
    assert "credentials" in text.lower() and "include" in text.lower()


def test_plan_mentions_removing_authorization_header() -> None:
    text = _plan()
    assert (
        "authorization" in text.lower()
        and (
            "remov" in text.lower()
            or "no longer" in text.lower()
            or "bearer" in text.lower()
        )
    )


# ---------------------------------------------------------------------------
# 6. CSRF protection
# ---------------------------------------------------------------------------


def test_plan_mentions_csrf() -> None:
    text = _plan()
    assert "csrf" in text.lower()


def test_plan_mentions_samesite_lax_csrf_protection() -> None:
    text = _plan()
    assert "lax" in text.lower() and "csrf" in text.lower()


# ---------------------------------------------------------------------------
# 7. CORS allow_credentials
# ---------------------------------------------------------------------------


def test_plan_mentions_allow_credentials() -> None:
    text = _plan()
    assert "allow_credentials" in text or "credentials" in text.lower()


# ---------------------------------------------------------------------------
# 8. Backend changes: get_current_user reads cookie
# ---------------------------------------------------------------------------


def test_plan_mentions_get_current_user_reads_cookie() -> None:
    text = _plan()
    assert "get_current_user" in text and "cookie" in text.lower()


def test_plan_mentions_bearer_fallback_during_migration() -> None:
    text = _plan()
    assert (
        "bearer" in text.lower()
        and (
            "fallback" in text.lower()
            or "migration window" in text.lower()
        )
    )


# ---------------------------------------------------------------------------
# 9. clinic_id after migration
# ---------------------------------------------------------------------------


def test_plan_mentions_clinic_id_not_in_jwt_after_migration() -> None:
    text = _plan()
    assert "clinic_id" in text and (
        "localstorage" in text.lower()
        or "login response" in text.lower()
        or "body" in text.lower()
    )


# ---------------------------------------------------------------------------
# 10. Staging cross-domain risk
# ---------------------------------------------------------------------------


def test_plan_mentions_staging_cross_domain_cookie_risk() -> None:
    text = _plan()
    assert (
        "samesite=none" in text.lower()
        or "SameSite=None" in text
        or "cross-domain" in text.lower()
        or "cross-site" in text.lower()
    ) and "staging" in text.lower()


def test_plan_mentions_samesite_none_for_staging() -> None:
    text = _plan()
    assert (
        "none" in text.lower()
        and "staging" in text.lower()
        and "samesite" in text.lower()
    )


# ---------------------------------------------------------------------------
# 11. Refresh token deferred
# ---------------------------------------------------------------------------


def test_plan_mentions_refresh_token_deferred() -> None:
    text = _plan()
    assert (
        "refresh" in text.lower()
        and (
            "defer" in text.lower()
            or "out of scope" in text.lower()
            or "sprint 14" in text.lower()
        )
    )


# ---------------------------------------------------------------------------
# 12. Production PHI blocker
# ---------------------------------------------------------------------------


def test_plan_mentions_production_phi_blocker() -> None:
    text = _plan()
    assert "phi" in text.lower() and (
        "blocker" in text.lower() or "no-go" in text.lower()
    )


# ---------------------------------------------------------------------------
# 13. Testing strategy
# ---------------------------------------------------------------------------


def test_plan_mentions_testing_strategy() -> None:
    text = _plan()
    assert "test" in text.lower() and (
        "strategy" in text.lower()
        or "unit test" in text.lower()
        or "contract" in text.lower()
    )


# ---------------------------------------------------------------------------
# 14. No implementation in this module
# ---------------------------------------------------------------------------


def test_plan_mentions_planning_only_no_implementation() -> None:
    text = _plan()
    assert (
        "planning only" in text.lower()
        or "no implementation" in text.lower()
        or "plan only" in text.lower()
    )


# ---------------------------------------------------------------------------
# 15. Sprint 14 execution
# ---------------------------------------------------------------------------


def test_plan_mentions_sprint_14_execution() -> None:
    text = _plan()
    assert "sprint 14" in text.lower() or "Sprint 14" in text


# ---------------------------------------------------------------------------
# 16. No obvious real secrets in the document
# ---------------------------------------------------------------------------


def test_plan_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    matches = real_key_pattern.findall(_plan())
    assert not matches, f"Possible real key in plan: {matches}"


def test_plan_no_real_db_password() -> None:
    text = _plan()
    for line in text.splitlines():
        if "postgresql://" in line:
            assert (
                "placeholder" in line.lower()
                or "example" in line.lower()
                or "<" in line
                or "#" in line
            ), f"Unexpected non-placeholder DATABASE_URL: {line!r}"
