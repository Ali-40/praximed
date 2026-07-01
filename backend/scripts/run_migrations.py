"""
Migration runner — PraxisMed Sprint 5 / Module 45

Runs Alembic migrations against the database configured via DATABASE_URL.

Usage:
    DATABASE_URL=postgresql://... python backend/scripts/run_migrations.py

Safe to import in tests — reads DATABASE_URL and executes Alembic only inside
main(), which is guarded by the if __name__ == "__main__" block.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


# Resolved relative to this file: backend/scripts/ -> backend/ -> backend/alembic.ini
_ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print(
            "ERROR: DATABASE_URL environment variable is not set.\n"
            "Set DATABASE_URL before running migrations.\n"
            "Example: DATABASE_URL=postgresql://praxismed:password@localhost:5433/praxismed_local",
            file=sys.stderr,
        )
        sys.exit(1)

    if not _ALEMBIC_INI.exists():
        print(
            f"ERROR: alembic.ini not found at {_ALEMBIC_INI}\n"
            "Run this script from the project root or ensure backend/alembic.ini exists.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Running: alembic -c {_ALEMBIC_INI} upgrade head")
    result = subprocess.run(
        ["alembic", "-c", str(_ALEMBIC_INI), "upgrade", "head"],
        env={**os.environ, "DATABASE_URL": database_url},
    )

    if result.returncode != 0:
        print("ERROR: Migration failed. Check the output above.", file=sys.stderr)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
