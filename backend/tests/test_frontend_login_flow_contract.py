"""
Static contract tests for frontend login flow integration — PraxisMed Sprint 8 / Module 67.

These tests verify file content structure only.
No JS/TS runtime is invoked.
"""

from __future__ import annotations

import os
import re

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")


def _read(rel: str) -> str:
    with open(os.path.join(FRONTEND, rel), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Login page calls /auth/login via loginUser helper
# ---------------------------------------------------------------------------

def test_login_page_calls_login_helper():
    content = _read("app/login/page.tsx")
    assert "loginUser" in content, \
        "login/page.tsx must call loginUser from the auth helper"


# ---------------------------------------------------------------------------
# 2. Login page shows a generic error on failure
# ---------------------------------------------------------------------------

def test_login_page_handles_generic_error():
    content = _read("app/login/page.tsx")
    # Must have error state and catch block
    assert "setError" in content or "error" in content.lower(), \
        "login/page.tsx must handle login errors"
    assert "catch" in content, \
        "login/page.tsx must have a try/catch around the login call"
    # Error message must be generic — must not reveal email vs password
    assert "Invalid credentials" not in content or \
        "Sign-in failed" in content or \
        "check your details" in content.lower(), \
        "login error message must be generic"


# ---------------------------------------------------------------------------
# 3. Login page stores token through storeToken helper
# ---------------------------------------------------------------------------

def test_login_page_stores_token():
    content = _read("app/login/page.tsx")
    assert "storeToken" in content, \
        "login/page.tsx must call storeToken after successful login"


# ---------------------------------------------------------------------------
# 4. Login page redirects to /dashboard on success
# ---------------------------------------------------------------------------

def test_login_page_redirects_to_dashboard():
    content = _read("app/login/page.tsx")
    assert "/dashboard" in content, \
        "login/page.tsx must redirect to /dashboard on successful login"
    # Must use router.push or router.replace
    assert "router.push" in content or "router.replace" in content, \
        "login/page.tsx must use router navigation for the redirect"


# ---------------------------------------------------------------------------
# 5. Dashboard checks authentication state before rendering
# ---------------------------------------------------------------------------

def test_dashboard_checks_auth_state():
    content = _read("app/dashboard/page.tsx")
    assert "isAuthenticated" in content or "getToken" in content, \
        "dashboard/page.tsx must check authentication state"
    # Must redirect unauthenticated users
    assert "/login" in content, \
        "dashboard/page.tsx must reference /login for unauthenticated redirect"


# ---------------------------------------------------------------------------
# 6. Dashboard supports logout via clearToken
# ---------------------------------------------------------------------------

def test_dashboard_supports_logout():
    content = _read("app/dashboard/page.tsx")
    assert "clearToken" in content, \
        "dashboard/page.tsx must call clearToken for logout"
    assert "logout" in content.lower() or "Logout" in content, \
        "dashboard/page.tsx must have a logout control"


# ---------------------------------------------------------------------------
# 7. Auth helper does not contain real credentials or secrets
# ---------------------------------------------------------------------------

def test_auth_helper_no_real_credentials():
    content = _read("lib/auth.ts")
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), \
        "lib/auth.ts must not contain hardcoded JWT token values"
    assert "sk-" not in content, \
        "lib/auth.ts must not contain API key strings"
    assert not re.search(r"['\"][A-Za-z0-9+/]{40,}={0,2}['\"]", content), \
        "lib/auth.ts must not contain hardcoded base64-encoded secrets"


# ---------------------------------------------------------------------------
# 8. API helper still uses NEXT_PUBLIC_API_BASE_URL with localhost fallback
# ---------------------------------------------------------------------------

def test_api_helper_env_var_and_fallback():
    content = _read("lib/api.ts")
    assert "NEXT_PUBLIC_API_BASE_URL" in content, \
        "lib/api.ts must reference NEXT_PUBLIC_API_BASE_URL"
    assert "127.0.0.1:8000" in content or "localhost:8000" in content, \
        "lib/api.ts must include a localhost fallback URL"


# ---------------------------------------------------------------------------
# 9. README explains the local login flow
# ---------------------------------------------------------------------------

def test_readme_explains_login_flow():
    content = _read("README.md")
    assert "login" in content.lower(), \
        "README.md must describe the login flow"
    assert "clinic" in content.lower(), \
        "README.md must mention the Clinic ID requirement"
    assert "npm run dev" in content or "yarn dev" in content or "pnpm dev" in content, \
        "README.md must include the dev server command"


# ---------------------------------------------------------------------------
# 10. No real patient data markers in login or dashboard pages
# ---------------------------------------------------------------------------

def test_no_real_patient_data_markers():
    login = _read("app/login/page.tsx")
    dashboard = _read("app/dashboard/page.tsx")
    forbidden = ("DOB:", "1234567890", "SVNR", "sozialversicherung")
    for pattern in forbidden:
        assert pattern not in login, \
            f"login page must not contain real patient data marker: {pattern!r}"
        assert pattern not in dashboard, \
            f"dashboard page must not contain real patient data marker: {pattern!r}"
