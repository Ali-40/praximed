"""
Static contract tests for frontend dashboard foundation — PraxisMed Sprint 8 / Module 66.

These tests verify file existence and content structure only.
No JS/TS runtime is invoked.
"""

from __future__ import annotations

import json
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
# 1. package.json exists
# ---------------------------------------------------------------------------

def test_package_json_exists():
    assert os.path.isfile(os.path.join(FRONTEND, "package.json")), \
        "frontend/package.json must exist"


# ---------------------------------------------------------------------------
# 2. Uses Next.js and TypeScript
# ---------------------------------------------------------------------------

def test_uses_nextjs_and_typescript():
    pkg = json.loads(_read("package.json"))
    all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    assert "next" in all_deps, "package.json must declare 'next' as a dependency"
    assert "typescript" in all_deps, "package.json must declare 'typescript' as a devDependency"


# ---------------------------------------------------------------------------
# 3. /login page exists
# ---------------------------------------------------------------------------

def test_login_page_exists():
    path = os.path.join(FRONTEND, "app", "login", "page.tsx")
    assert os.path.isfile(path), "frontend/app/login/page.tsx must exist"


# ---------------------------------------------------------------------------
# 4. /dashboard page exists
# ---------------------------------------------------------------------------

def test_dashboard_page_exists():
    path = os.path.join(FRONTEND, "app", "dashboard", "page.tsx")
    assert os.path.isfile(path), "frontend/app/dashboard/page.tsx must exist"


# ---------------------------------------------------------------------------
# 5. api helper uses NEXT_PUBLIC_API_BASE_URL
# ---------------------------------------------------------------------------

def test_api_helper_uses_env_var():
    content = _read("lib/api.ts")
    assert "NEXT_PUBLIC_API_BASE_URL" in content, \
        "lib/api.ts must reference NEXT_PUBLIC_API_BASE_URL"


# ---------------------------------------------------------------------------
# 6. api helper has localhost fallback
# ---------------------------------------------------------------------------

def test_api_helper_has_localhost_fallback():
    content = _read("lib/api.ts")
    assert "127.0.0.1:8000" in content or "localhost:8000" in content, \
        "lib/api.ts must include a localhost fallback URL"


# ---------------------------------------------------------------------------
# 7. auth helper does not contain real credentials or secrets
# ---------------------------------------------------------------------------

def test_auth_helper_no_real_credentials():
    content = _read("lib/auth.ts")
    # No hardcoded JWT bearer token values (base64url-encoded JSON header)
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), \
        "lib/auth.ts must not contain hardcoded JWT token values"
    # No API key patterns
    assert "sk-" not in content, \
        "lib/auth.ts must not contain API key strings"
    # No hardcoded long base64 blobs that look like secrets
    assert not re.search(r"['\"][A-Za-z0-9+/]{40,}={0,2}['\"]", content), \
        "lib/auth.ts must not contain hardcoded base64-encoded secrets"


# ---------------------------------------------------------------------------
# 8. Dashboard page contains placeholder sections for all four areas
# ---------------------------------------------------------------------------

def test_dashboard_has_placeholder_sections():
    content = _read("app/dashboard/page.tsx")
    for section in ("Patients", "Appointments", "Notifications", "Consultations"):
        assert section in content, \
            f"app/dashboard/page.tsx must contain placeholder section: {section}"


# ---------------------------------------------------------------------------
# 9. README exists and explains local startup
# ---------------------------------------------------------------------------

def test_readme_exists_with_startup_instructions():
    readme_path = os.path.join(FRONTEND, "README.md")
    assert os.path.isfile(readme_path), "frontend/README.md must exist"
    content = _read("README.md")
    assert any(kw in content for kw in ("npm", "yarn", "pnpm")), \
        "README.md must mention npm, yarn, or pnpm for local startup"
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
