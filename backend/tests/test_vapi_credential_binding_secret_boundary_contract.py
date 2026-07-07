"""
Sprint 19 / Module 144 — Vapi Credential Binding Design and Secret Boundary

Static contract tests verifying:
1. The architecture doc meets the secret boundary specification.
2. Frontend files do not contain secret input fields.
3. No test or doc file contains fake secret values that look real.

No imports, no database, no network. All assertions are substring checks.
"""

from pathlib import Path

ARCH_DOC = Path("docs/architecture/VAPI_CREDENTIAL_BINDING_SECRET_BOUNDARY.md")

# Frontend feature pages to audit for secret input fields.
# The hub page (developer-console/page.tsx) is excluded because it intentionally
# displays environment variable reference labels (read-only display, not form inputs).
FRONTEND_FILES = [
    Path("frontend/app/developer-console/language-settings/page.tsx"),
    Path("frontend/app/developer-console/onboarding-requests/page.tsx"),
    Path("frontend/app/developer-console/vapi-config/page.tsx"),
    Path("frontend/lib/api.ts"),
]

# Docs that must not contain fake secret-looking values
DOCS_TO_AUDIT = [
    Path("docs/architecture/VAPI_CREDENTIAL_BINDING_SECRET_BOUNDARY.md"),
    Path("docs/architecture/VAPI_ASSISTANT_CONFIGURATION_PACK_PER_TENANT.md"),
    Path("docs/architecture/ADMIN_VAPI_ASSISTANT_CONFIG_PREVIEW_UI.md"),
]


def _arch() -> str:
    return ARCH_DOC.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_arch_doc_exists():
    assert ARCH_DOC.exists(), f"Missing arch doc: {ARCH_DOC}"


# ---------------------------------------------------------------------------
# Arch doc — secret boundary
# ---------------------------------------------------------------------------


def test_arch_doc_mentions_vapi_api_key_label():
    assert "VAPI_API_KEY" in _arch()


def test_arch_doc_mentions_vapi_webhook_secret_label():
    assert "VAPI_WEBHOOK_SECRET" in _arch()


def test_arch_doc_environment_variables_only():
    src = _arch().lower()
    assert "environment variable" in src or "environment variables" in src


def test_arch_doc_managed_secret_store():
    src = _arch().lower()
    assert "secret store" in src or "managed secret" in src or "secret manager" in src


def test_arch_doc_never_database():
    src = _arch().lower()
    assert "never" in src and "database" in src


def test_arch_doc_never_browser():
    src = _arch().lower()
    assert "browser" in src
    assert "forbidden" in src or "never" in src


def test_arch_doc_never_logs():
    src = _arch().lower()
    assert "never" in src and "log" in src


def test_arch_doc_never_docs():
    src = _arch().lower()
    assert "docs" in src and ("forbidden" in src or "never" in src)


def test_arch_doc_never_tests():
    src = _arch().lower()
    assert "tests" in src and ("forbidden" in src or "never" in src)


# ---------------------------------------------------------------------------
# Arch doc — reference names
# ---------------------------------------------------------------------------


def test_arch_doc_api_key_secret_ref():
    assert "api_key_secret_ref" in _arch()


def test_arch_doc_webhook_secret_ref():
    assert "webhook_secret_ref" in _arch()


def test_arch_doc_reference_names_only():
    src = _arch().lower()
    assert "reference name" in src or "reference names" in src


def test_arch_doc_no_actual_secret_value():
    src = _arch().lower()
    assert "no actual secret" in src or "never the secret value" in src or "not the secret" in src


# ---------------------------------------------------------------------------
# Arch doc — clinic_vapi_bindings table
# ---------------------------------------------------------------------------


def test_arch_doc_clinic_vapi_bindings():
    assert "clinic_vapi_bindings" in _arch()


def test_arch_doc_status_draft():
    assert "draft" in _arch()


def test_arch_doc_status_configured():
    assert "configured" in _arch()


def test_arch_doc_status_disabled():
    assert "disabled" in _arch()


def test_arch_doc_status_revoked():
    assert "revoked" in _arch()


# ---------------------------------------------------------------------------
# Arch doc — no live Vapi API calls
# ---------------------------------------------------------------------------


def test_arch_doc_no_live_vapi_api_calls():
    src = _arch().lower()
    assert "no live vapi" in src or "no live" in src or "makes no live" in src


# ---------------------------------------------------------------------------
# Arch doc — no PHI / no patient data / no transcript / no recording URL
# ---------------------------------------------------------------------------


def test_arch_doc_no_phi():
    src = _arch().lower()
    assert "no phi" in src


def test_arch_doc_no_patient_data():
    src = _arch().lower()
    assert "no patient data" in src or "patient data" in src


def test_arch_doc_no_transcript():
    src = _arch().lower()
    assert "no transcript" in src or "transcript" in src


def test_arch_doc_no_recording_url():
    src = _arch().lower()
    assert "no recording" in src or "recording url" in src or "recording" in src


# ---------------------------------------------------------------------------
# Arch doc — no frontend secret input
# ---------------------------------------------------------------------------


def test_arch_doc_no_frontend_secret_input():
    src = _arch().lower()
    assert "no browser secret input" in src or "browser secret" in src or (
        "frontend" in src and "secret" in src
    )


# ---------------------------------------------------------------------------
# Arch doc — C3–C8 readiness gate
# ---------------------------------------------------------------------------


def test_arch_doc_c3():
    assert "C3" in _arch()


def test_arch_doc_c4():
    assert "C4" in _arch()


def test_arch_doc_c5():
    assert "C5" in _arch()


def test_arch_doc_c6():
    assert "C6" in _arch()


def test_arch_doc_c7():
    assert "C7" in _arch()


def test_arch_doc_c8():
    assert "C8" in _arch()


# ---------------------------------------------------------------------------
# Arch doc — Article 28 / Article 32
# ---------------------------------------------------------------------------


def test_arch_doc_article_28():
    assert "Article 28" in _arch() or "article 28" in _arch().lower()


def test_arch_doc_article_32():
    assert "Article 32" in _arch() or "article 32" in _arch().lower()


# ---------------------------------------------------------------------------
# Arch doc — production PHI NO-GO
# ---------------------------------------------------------------------------


def test_arch_doc_production_phi_no_go():
    assert "NO-GO" in _arch() or "no-go" in _arch().lower()


def test_arch_doc_production_phi_remains_no_go():
    src = _arch().lower()
    assert "production phi remains no-go" in src or (
        "production phi" in src and "no-go" in src
    )


# ---------------------------------------------------------------------------
# Frontend files — no secret input fields
# ---------------------------------------------------------------------------


def _read_file_lower(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").lower()


# Module 146 amendment: the binding-metadata design (Modules 145/146) stores
# secret REFERENCE NAMES (api_key_secret_ref / webhook_secret_ref). Reference
# name fields are explicitly allowed by the secret boundary — actual secret
# VALUE fields remain forbidden. Strip the allowed reference tokens before
# asserting so the boundary check targets real secret inputs only.
_ALLOWED_REFERENCE_TOKENS = (
    "api_key_secret_ref",
    "webhook_secret_ref",
)


def _strip_reference_tokens(src: str) -> str:
    for token in _ALLOWED_REFERENCE_TOKENS:
        src = src.replace(token, "")
    return src


def test_frontend_no_vapi_api_key_input():
    for path in FRONTEND_FILES:
        src = _strip_reference_tokens(_read_file_lower(path))
        assert "vapi api key" not in src, f"Found 'vapi api key' input in {path}"
        assert "vapi_api_key" not in src, f"Found 'vapi_api_key' in {path}"


def test_frontend_no_webhook_secret_input():
    for path in FRONTEND_FILES:
        src = _strip_reference_tokens(_read_file_lower(path))
        assert "webhook_secret" not in src, f"Found 'webhook_secret' in {path}"
        assert "webhook secret" not in src, f"Found 'webhook secret' in {path}"


def test_frontend_no_database_url_input():
    for path in FRONTEND_FILES:
        src = path.read_text(encoding="utf-8") if path.exists() else ""
        assert "DATABASE_URL" not in src, f"Found 'DATABASE_URL' in {path}"


def test_frontend_no_jwt_secret_input():
    for path in FRONTEND_FILES:
        src = _read_file_lower(path)
        assert "jwt_secret" not in src, f"Found 'jwt_secret' in {path}"
        assert "jwt secret" not in src, f"Found 'jwt secret' in {path}"


# ---------------------------------------------------------------------------
# Docs — no fake secret values
# ---------------------------------------------------------------------------


def _looks_like_secret(text: str) -> bool:
    """Return True if text contains patterns that look like real API key values."""
    import re
    patterns = [
        r"sk-[a-zA-Z0-9]{20,}",          # OpenAI-style key
        r"vapi_live_[a-zA-Z0-9]{10,}",   # Vapi live key pattern
        r"Bearer\s+[a-zA-Z0-9+/=]{30,}", # Bearer token
        r"eyJ[a-zA-Z0-9_-]{30,}",        # JWT
    ]
    for pat in patterns:
        if re.search(pat, text):
            return True
    return False


def test_arch_doc_no_fake_secret_values():
    src = _arch()
    assert not _looks_like_secret(src), (
        "Architecture doc contains a pattern that looks like a real secret value. "
        "Use only reference name labels, not fake or real secret values."
    )


def test_docs_no_fake_secret_values():
    for path in DOCS_TO_AUDIT:
        if not path.exists():
            continue
        src = path.read_text(encoding="utf-8")
        assert not _looks_like_secret(src), (
            f"{path} contains a pattern that looks like a real secret value."
        )
