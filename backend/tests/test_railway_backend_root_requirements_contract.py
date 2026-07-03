"""
Static contract tests for Sprint 16 / Module 110 — Railway Backend Root Requirements Fix.

Verifies:
- Root requirements.txt exists and references backend/requirements.txt
- Procfile and runtime.txt are correct
- Railway deployment docs document the root directory fix and import path error
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


def _procfile() -> str:
    with open(_PROCFILE, encoding="utf-8") as f:
        return f.read()


def _runtime() -> str:
    with open(_RUNTIME_TXT, encoding="utf-8") as f:
        return f.read()


def _runbook() -> str:
    with open(_RUNBOOK_PATH, encoding="utf-8") as f:
        return f.read()


def _prep() -> str:
    with open(_PREP_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Root requirements.txt
# ---------------------------------------------------------------------------


def test_root_requirements_exists() -> None:
    assert os.path.isfile(_ROOT_REQUIREMENTS), (
        f"Root requirements.txt not found at {_ROOT_REQUIREMENTS}"
    )


def test_root_requirements_references_backend_requirements() -> None:
    text = _root_req()
    assert "-r backend/requirements.txt" in text, (
        "Root requirements.txt must contain '-r backend/requirements.txt'"
    )


# ---------------------------------------------------------------------------
# 2. Procfile
# ---------------------------------------------------------------------------


def test_procfile_exists() -> None:
    assert os.path.isfile(_PROCFILE), f"Procfile not found at {_PROCFILE}"


def test_procfile_mentions_backend_app_main() -> None:
    assert "backend.app.main:app" in _procfile()


def test_procfile_mentions_host_0000() -> None:
    assert "0.0.0.0" in _procfile()


def test_procfile_mentions_port_env_var() -> None:
    assert "$PORT" in _procfile()


# ---------------------------------------------------------------------------
# 3. runtime.txt
# ---------------------------------------------------------------------------


def test_runtime_txt_exists() -> None:
    assert os.path.isfile(_RUNTIME_TXT), f"runtime.txt not found at {_RUNTIME_TXT}"


def test_runtime_txt_mentions_python_311() -> None:
    assert "python-3.11" in _runtime()


# ---------------------------------------------------------------------------
# 4. Railway runbook — root directory fix
# ---------------------------------------------------------------------------


def test_runbook_mentions_repo_root() -> None:
    text = _runbook().lower()
    assert "repo root" in text


def test_runbook_warns_not_to_set_root_to_backend() -> None:
    text = _runbook().lower()
    assert (
        "do not set" in text or "must not" in text or "never" in text or "not to `backend`" in text
        or "do not" in text
    ) and "backend" in text and "root" in text


def test_runbook_mentions_module_not_found_error() -> None:
    text = _runbook()
    assert "ModuleNotFoundError" in text and "No module named 'backend'" in text


def test_runbook_mentions_root_requirements_bridge() -> None:
    text = _runbook().lower()
    assert (
        "requirements.txt" in text
        and ("bridge" in text or "nixpacks" in text or "repo root" in text)
    )


def test_runbook_mentions_no_secrets() -> None:
    text = _runbook().lower()
    assert (
        "no secret" in text
        or "never" in text
        or "do not print" in text
        or "not record" in text
    )


def test_runbook_mentions_fake_non_phi_staging() -> None:
    text = _runbook().lower()
    assert ("fake" in text or "non-phi" in text) and "staging" in text


# ---------------------------------------------------------------------------
# 5. Railway deployment prep doc — root directory fix
# ---------------------------------------------------------------------------


def test_prep_mentions_repo_root() -> None:
    text = _prep().lower()
    assert "repo root" in text


def test_prep_mentions_module_not_found_error() -> None:
    text = _prep()
    assert "ModuleNotFoundError" in text or "No module named 'backend'" in text
