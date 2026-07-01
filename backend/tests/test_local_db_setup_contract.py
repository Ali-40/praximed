"""
Static contract tests for the local PostgreSQL Docker setup — PraxisMed Sprint 5 / Module 45

Strategy:
- File-existence and text-content checks only using pathlib.
- No Docker required. No real database connection. No subprocess execution.
- Scripts are imported via importlib to verify they are safe to import without
  executing any migrations or database connections.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.parent   # praximed/
BACKEND_DIR  = Path(__file__).parent.parent           # praximed/backend/
SCRIPTS_DIR  = BACKEND_DIR / "scripts"

DOCKER_COMPOSE_FILE = PROJECT_ROOT / "docker-compose.postgres.yml"
ENV_EXAMPLE_FILE    = BACKEND_DIR / ".env.example"
RUN_MIGRATIONS_FILE = SCRIPTS_DIR / "run_migrations.py"
SMOKE_TEST_FILE     = SCRIPTS_DIR / "db_smoke_test.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _import_module_safely(name: str, path: Path):
    """Import a script as a module without triggering its __main__ block."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)       # type: ignore[arg-type]
    spec.loader.exec_module(module)                      # type: ignore[union-attr]
    return module


# ===========================================================================
# 1–7  docker-compose.postgres.yml
# ===========================================================================


def test_docker_compose_file_exists():
    """Test 1 — docker-compose.postgres.yml must exist at the project root."""
    assert DOCKER_COMPOSE_FILE.exists(), f"Missing: {DOCKER_COMPOSE_FILE}"


def test_docker_compose_has_praxismed_postgres_service():
    """Test 2 — Service name praxismed_postgres must be declared."""
    assert "praxismed_postgres" in _read(DOCKER_COMPOSE_FILE)


def test_docker_compose_uses_postgres_image():
    """Test 3 — Must use the official postgres image."""
    content = _read(DOCKER_COMPOSE_FILE)
    assert "postgres:" in content or "image: postgres" in content


def test_docker_compose_maps_host_port_5433_to_5432():
    """Test 4 — Host port 5433 mapped to container port 5432."""
    content = _read(DOCKER_COMPOSE_FILE)
    assert "5433" in content
    assert "5432" in content
    # Both values must appear on the same port-mapping line or adjacent
    assert "5433:5432" in content


def test_docker_compose_defines_named_volume():
    """Test 5 — Named volume praxismed_postgres_data must be declared."""
    content = _read(DOCKER_COMPOSE_FILE)
    assert "praxismed_postgres_data" in content


def test_docker_compose_includes_pg_isready_healthcheck():
    """Test 6 — Healthcheck must use pg_isready."""
    content = _read(DOCKER_COMPOSE_FILE)
    assert "pg_isready" in content
    assert "healthcheck" in content


def test_docker_compose_no_obvious_production_secrets():
    """Test 7 — File must not contain obvious production secret markers."""
    content = _read(DOCKER_COMPOSE_FILE).lower()
    forbidden = [
        "amazonaws.com",
        "cloudsql",
        "rds.",
        "prod_password",
        "production_db",
        "staging_db",
    ]
    for token in forbidden:
        assert token not in content, (
            f"Possible production secret or URL found in docker-compose: {token!r}"
        )


# ===========================================================================
# 8–11  backend/.env.example
# ===========================================================================


def test_env_example_exists():
    """Test 8 — backend/.env.example must exist."""
    assert ENV_EXAMPLE_FILE.exists(), f"Missing: {ENV_EXAMPLE_FILE}"


def test_env_example_contains_database_url():
    """Test 9 — Must define DATABASE_URL."""
    assert "DATABASE_URL" in _read(ENV_EXAMPLE_FILE)


def test_env_example_uses_localhost_5433():
    """Test 10 — DATABASE_URL must point to localhost:5433."""
    assert "localhost:5433" in _read(ENV_EXAMPLE_FILE)


def test_env_example_contains_local_only_comment():
    """Test 11 — Must contain a comment indicating this is for local use only."""
    content = _read(ENV_EXAMPLE_FILE).lower()
    # Must mention both 'local' usage and warn about secrets / production
    assert "local" in content
    assert any(word in content for word in ("secret", "production", "commit")), (
        ".env.example must warn against committing production secrets"
    )


# ===========================================================================
# 12–16  backend/scripts/run_migrations.py
# ===========================================================================


def test_run_migrations_file_exists():
    """Test 12 — run_migrations.py must exist."""
    assert RUN_MIGRATIONS_FILE.exists(), f"Missing: {RUN_MIGRATIONS_FILE}"


def test_run_migrations_reads_database_url():
    """Test 13 — Must read DATABASE_URL from environment."""
    assert "DATABASE_URL" in _read(RUN_MIGRATIONS_FILE)


def test_run_migrations_references_alembic_ini():
    """Test 14 — Must reference backend/alembic.ini."""
    assert "alembic.ini" in _read(RUN_MIGRATIONS_FILE)


def test_run_migrations_has_main_guard():
    """Test 15 — Must use if __name__ == '__main__' guard."""
    content = _read(RUN_MIGRATIONS_FILE)
    assert (
        '__name__ == "__main__"' in content
        or "__name__ == '__main__'" in content
    )


def test_run_migrations_no_hardcoded_production_url():
    """Test 16 — Must not contain hard-coded production database URLs."""
    content = _read(RUN_MIGRATIONS_FILE).lower()
    forbidden = [
        "amazonaws.com",
        "rds.",
        "cloudsql",
        "postgres://prod",
        "postgresql://prod",
    ]
    for token in forbidden:
        assert token not in content, (
            f"Hard-coded production URL fragment in run_migrations.py: {token!r}"
        )


# ===========================================================================
# 17–22  backend/scripts/db_smoke_test.py
# ===========================================================================


def test_smoke_test_file_exists():
    """Test 17 — db_smoke_test.py must exist."""
    assert SMOKE_TEST_FILE.exists(), f"Missing: {SMOKE_TEST_FILE}"


def test_smoke_test_reads_database_url():
    """Test 18 — Must read DATABASE_URL from environment."""
    assert "DATABASE_URL" in _read(SMOKE_TEST_FILE)


def test_smoke_test_checks_select_1():
    """Test 19 — Must include a SELECT 1 connectivity check."""
    assert "SELECT 1" in _read(SMOKE_TEST_FILE)


def test_smoke_test_checks_key_tables():
    """Test 20 — Must check all four key tables exist after migration."""
    content = _read(SMOKE_TEST_FILE)
    for table in ["clinics", "patients", "consultation_sessions", "audit_log"]:
        assert table in content, (
            f"db_smoke_test.py does not reference required table: {table!r}"
        )


def test_smoke_test_has_main_guard():
    """Test 21 — Must use if __name__ == '__main__' guard."""
    content = _read(SMOKE_TEST_FILE)
    assert (
        '__name__ == "__main__"' in content
        or "__name__ == '__main__'" in content
    )


def test_smoke_test_no_top_level_asyncpg_connect():
    """Test 22 — asyncpg.connect / asyncpg.create_pool must not appear at module top level."""
    lines = _read(SMOKE_TEST_FILE).splitlines()
    top_level = [
        line for line in lines
        if line.startswith("asyncpg.connect")
        or line.startswith("asyncpg.create_pool")
    ]
    assert not top_level, (
        f"Top-level asyncpg connection call found in db_smoke_test.py: {top_level}"
    )


# ===========================================================================
# 23–24  Import-safety tests
# ===========================================================================


def test_importing_run_migrations_does_not_execute():
    """Test 23 — Importing run_migrations.py must not execute migrations or call sys.exit."""
    # If main() runs on import (missing __name__ guard), it would call sys.exit(1) because
    # DATABASE_URL is not set — that would raise SystemExit and fail this test.
    module = _import_module_safely("run_migrations_contract", RUN_MIGRATIONS_FILE)
    assert hasattr(module, "main"), "run_migrations.py must expose a main() function"


def test_importing_db_smoke_test_does_not_connect():
    """Test 24 — Importing db_smoke_test.py must not open any database connection."""
    # asyncpg.connect is inside smoke_test() which is only called from main()
    # which is guarded by if __name__ == "__main__".
    module = _import_module_safely("db_smoke_test_contract", SMOKE_TEST_FILE)
    assert hasattr(module, "main"), "db_smoke_test.py must expose a main() function"
    assert hasattr(module, "smoke_test"), "db_smoke_test.py must expose a smoke_test() coroutine"
