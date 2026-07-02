"""
Local seed data script — PraxisMed Sprint 5 / Module 50
Updated: Sprint 9 / Module 72 — added password_hash for local browser login
Updated: Sprint 9 / Module 73 — added sys.path project-root safety for direct execution

Inserts deterministic local-only test rows into the local PostgreSQL database.
Run after migrations and before local integration testing.

Usage (from project root):
    export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
    python backend/scripts/seed_local_data.py

The script is idempotent — safe to run multiple times.
asyncpg is imported only inside the async function; importing this module
does not open a database connection.
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Dict

# Ensure the project root is on sys.path when this script is run directly
# (e.g. `python backend/scripts/seed_local_data.py`). When run via pytest or
# imported as a module, the project root is already on sys.path.
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from backend.app.core.password_hashing import hash_password  # noqa: E402

# ---------------------------------------------------------------------------
# Deterministic local-only UUIDs — NEVER used in production
# ---------------------------------------------------------------------------

LOCAL_CLINIC_ID               = "11111111-1111-1111-1111-111111111111"
LOCAL_DOCTOR_USER_ID          = "22222222-2222-2222-2222-222222222222"
LOCAL_PATIENT_ID              = "33333333-3333-3333-3333-333333333333"
LOCAL_CONSULTATION_SESSION_ID = "44444444-4444-4444-4444-444444444444"

# ---------------------------------------------------------------------------
# Local-dev login credentials — fake/local only, NEVER used in production
# ---------------------------------------------------------------------------

LOCAL_LOGIN_EMAIL          = "doctor.local@praximed.test"
LOCAL_LOGIN_PASSWORD_LABEL = "local-dev-password"   # label only — hash computed at runtime


async def seed_local_data(database_url: str) -> Dict[str, Any]:
    """Insert (or update) deterministic local seed rows using asyncpg.

    Returns a dict with the seeded IDs for logging/verification.
    Does not print secrets.
    """
    import asyncpg  # imported here — no connection at module import time

    # Compute bcrypt hash at call time, not at import time
    pwd_hash = hash_password(LOCAL_LOGIN_PASSWORD_LABEL)

    conn = await asyncpg.connect(database_url)
    try:
        # 1. clinics — root tenant row
        await conn.execute(
            """
            INSERT INTO clinics (id, slug, name, status, timezone, locale)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (id) DO UPDATE SET
                name       = EXCLUDED.name,
                updated_at = now()
            """,
            LOCAL_CLINIC_ID,
            "local-test-clinic",
            "Local Test Clinic",
            "active",
            "Europe/Vienna",
            "de-AT",
        )

        # 2. clinic_users — doctor user with login-capable password_hash
        await conn.execute(
            """
            INSERT INTO clinic_users (id, clinic_id, email, full_name, role, status, password_hash)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO UPDATE SET
                email         = EXCLUDED.email,
                full_name     = EXCLUDED.full_name,
                password_hash = EXCLUDED.password_hash,
                updated_at    = now()
            """,
            LOCAL_DOCTOR_USER_ID,
            LOCAL_CLINIC_ID,
            LOCAL_LOGIN_EMAIL,
            "Dr. Local Test",
            "doctor",
            "active",
            pwd_hash,
        )

        # 3. patients — one test patient
        await conn.execute(
            """
            INSERT INTO patients (
                id, clinic_id, full_name, preferred_language, status
            )
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id) DO UPDATE SET
                full_name  = EXCLUDED.full_name,
                updated_at = now()
            """,
            LOCAL_PATIENT_ID,
            LOCAL_CLINIC_ID,
            "Local Test Patient",
            "de-AT",
            "active",
        )

        # 4. consultation_sessions — one test session
        await conn.execute(
            """
            INSERT INTO consultation_sessions (
                id, clinic_id, patient_id, doctor_user_id,
                source, status, title, approval_status
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (id) DO UPDATE SET
                title      = EXCLUDED.title,
                updated_at = now()
            """,
            LOCAL_CONSULTATION_SESSION_ID,
            LOCAL_CLINIC_ID,
            LOCAL_PATIENT_ID,
            LOCAL_DOCTOR_USER_ID,
            "manual",
            "created",
            "Local Test Consultation Session",
            "not_ready",
        )
    finally:
        await conn.close()

    return {
        "clinic_id":               LOCAL_CLINIC_ID,
        "doctor_user_id":          LOCAL_DOCTOR_USER_ID,
        "patient_id":              LOCAL_PATIENT_ID,
        "consultation_session_id": LOCAL_CONSULTATION_SESSION_ID,
    }


def main() -> int:
    """CLI entry point — reads DATABASE_URL and runs the seed."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print(
            "ERROR: DATABASE_URL environment variable is not set.",
            file=sys.stderr,
        )
        return 1

    print("Seeding local test data...")
    result = asyncio.run(seed_local_data(database_url))

    print("Local seed data inserted successfully (fake/local only — not production data):")
    print(f"  clinic_id:               {result['clinic_id']}")
    print(f"  doctor_user_id:          {result['doctor_user_id']}")
    print(f"  patient_id:              {result['patient_id']}")
    print(f"  consultation_session_id: {result['consultation_session_id']}")
    print()
    print("LOCAL-DEV LOGIN (fake/local only — NOT for production):")
    print(f"  clinic_id: {LOCAL_CLINIC_ID}")
    print(f"  email:     {LOCAL_LOGIN_EMAIL}")
    print(f"  password:  {LOCAL_LOGIN_PASSWORD_LABEL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
