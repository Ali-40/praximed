"""
Database smoke test — PraxisMed Sprint 5 / Module 45

Connects to the database and verifies that key tables exist after migrations.

Usage:
    DATABASE_URL=postgresql://... python backend/scripts/db_smoke_test.py

Safe to import in tests — no database connection is opened at import time.
asyncpg is imported inside smoke_test() to avoid any import-time side effects.
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import List


REQUIRED_TABLES: List[str] = [
    "clinics",
    "patients",
    "consultation_sessions",
    "audit_log",
]


async def smoke_test(database_url: str) -> None:
    import asyncpg  # imported inside function — no connection at import time

    conn = await asyncpg.connect(database_url)
    try:
        # Basic connectivity check
        result = await conn.fetchval("SELECT 1")
        assert result == 1
        print("✓ Database connectivity OK (SELECT 1 passed)")

        # Verify each required table exists after migrations
        for table in REQUIRED_TABLES:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name   = $1
                """,
                table,
            )
            if row is None:
                print(
                    f"✗ Table '{table}' not found — run migrations first:\n"
                    "  python backend/scripts/run_migrations.py",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(f"✓ Table '{table}' exists")
    finally:
        await conn.close()

    print("\nSmoke test passed. Database is ready for local development.")


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print(
            "ERROR: DATABASE_URL environment variable is not set.\n"
            "Example: DATABASE_URL=postgresql://praxismed:password@localhost:5433/praxismed_local",
            file=sys.stderr,
        )
        sys.exit(1)

    asyncio.run(smoke_test(database_url))


if __name__ == "__main__":
    main()
