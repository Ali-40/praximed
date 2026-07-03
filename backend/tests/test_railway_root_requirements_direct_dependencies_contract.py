"""
Static contract tests for Sprint 16 / Module 111 — Railway Root Requirements Direct
Dependency Fix.

Verifies:
- Root requirements.txt lists dependencies directly (no nested -r include)
- All expected packages are present
- Procfile, runtime.txt, and Railway docs remain correct
"""

from __future__ import annotations

import os


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

_ROOT_REQUIREMENTS = os.path.join(_REPO_ROOT, "requirements.txt")
_BACKEND_REQUIREMENTS = os.path.join(_REPO_ROOT, "backend", "requirements.txt")
_PROCFILE = os.path.join(_REPO_ROOT, "Procfile")
_RUNTIME_TXT = os.path.join(_REPO_ROOT, "runtime.txt")

_RUNBOOK_PATH = os.path.join(
    _REPO_ROOT,
    "docs",
    "deployment",
    "RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md",
)

_PREP_PATH = os.path.join(
    _REPO_ROOT,
    "docs",
    "deployment",
    "RAILWAY_BACKEND_DEPLOYMENT_PREP.md",
)


def _root_req() -> str:
    with open(_ROOT_REQUIREMENTS, encoding="utf-8") as f:
        return f.read()


def _runbook() -> str:
    with open(_RUNBOOK_PATH, encoding="utf-8") as f:
        return f.read()


def _prep() -> str:
    with open(_PREP_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Root requirements.txt — structure
# ---------------------------------------------------------------------------


def test_root_requirements_exists() -> None:
    assert os.path.isfile(_ROOT_REQUIREMENTS), (
        f"Root requirements.txt not found at {_ROOT_REQUIREMENTS}"
    )


def test_root_requirements_does_not_use_nested_include() -> None:
    assert "-r backend/requirements.txt" not in _root_req(), (
        "Root requirements.txt must not use '-r backend/requirements.txt' — "
        "Railway/Railpack cannot resolve nested includes during build cache"
    )


# ---------------------------------------------------------------------------
# 2. Root requirements.txt — direct dependencies
# ---------------------------------------------------------------------------


def test_root_requirements_mentions_fastapi() -> None:
    assert "fastapi" in _root_req().lower()


def test_root_requirements_mentions_uvicorn() -> None:
    assert "uvicorn" in _root_req().lower()


def test_root_requirements_mentions_asyncpg() -> None:
    assert "asyncpg" in _root_req().lower()


def test_root_requirements_mentions_alembic() -> None:
    assert "alembic" in _root_req().lower()


def test_root_requirements_mentions_pydantic() -> None:
    assert "pydantic" in _root_req().lower()


def test_root_requirements_mentions_pyjwt() -> None:
    assert "pyjwt" in _root_req().lower()


def test_root_requirements_mentions_bcrypt() -> None:
    assert "bcrypt" in _root_req().lower()


# ---------------------------------------------------------------------------
# 3. backend/requirements.txt still exists
# ---------------------------------------------------------------------------


def test_backend_requirements_exists() -> None:
    assert os.path.isfile(_BACKEND_REQUIREMENTS), (
        f"backend/requirements.txt not found at {_BACKEND_REQUIREMENTS}"
    )


# ---------------------------------------------------------------------------
# 4. Procfile
# ---------------------------------------------------------------------------


def test_procfile_exists() -> None:
    assert os.path.isfile(_PROCFILE)


def test_procfile_mentions_backend_app_main() -> None:
    with open(_PROCFILE, encoding="utf-8") as f:
        assert "backend.app.main:app" in f.read()


# ---------------------------------------------------------------------------
# 5. runtime.txt
# ---------------------------------------------------------------------------


def test_runtime_txt_exists() -> None:
    assert os.path.isfile(_RUNTIME_TXT)


def test_runtime_txt_mentions_python_311() -> None:
    with open(_RUNTIME_TXT, encoding="utf-8") as f:
        assert "python-3.11" in f.read()


# ---------------------------------------------------------------------------
# 6. Railway runbook — direct deps explanation
# ---------------------------------------------------------------------------


def test_runbook_mentions_repo_root() -> None:
    assert "repo root" in _runbook().lower()


def test_runbook_warns_not_to_set_root_to_backend() -> None:
    text = _runbook().lower()
    assert "root" in text and "backend" in text and (
        "do not" in text or "must not" in text or "never" in text
    )


def test_runbook_mentions_direct_dependencies_in_root_requirements() -> None:
    text = _runbook().lower()
    assert "direct" in text and "requirements" in text


def test_runbook_mentions_railpack_cannot_resolve_nested_include() -> None:
    text = _runbook().lower()
    assert (
        "railpack" in text or "railway" in text
    ) and (
        "cannot" in text or "nested" in text or "resolve" in text
    )


def test_runbook_mentions_no_secrets() -> None:
    text = _runbook().lower()
    assert "no secret" in text or "never" in text or "do not print" in text


def test_runbook_mentions_fake_non_phi_staging() -> None:
    text = _runbook().lower()
    assert ("fake" in text or "non-phi" in text) and "staging" in text


# ---------------------------------------------------------------------------
# 7. Railway prep doc — direct deps explanation
# ---------------------------------------------------------------------------


def test_prep_mentions_repo_root() -> None:
    assert "repo root" in _prep().lower()


def test_prep_mentions_direct_dependencies_not_nested_include() -> None:
    text = _prep().lower()
    assert (
        "direct" in text or "flat" in text or "nested" in text
    ) and "requirements" in text
