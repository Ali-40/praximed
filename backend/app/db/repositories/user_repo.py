"""
User Repository — PraxisMed Sprint 7 / Module 59

Provides async read and write operations for the ``clinic_users`` table,
including the password_hash column added in Module 59.

All SQL is parameterised ($1, $2, …) — no string interpolation.
Tests use MagicMock pools; no real database connection is required.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class UserRepoError(RuntimeError):
    """Base class for user repository errors."""


class InvalidUserError(UserRepoError):
    """Raised when required fields are missing or values are invalid."""


# ---------------------------------------------------------------------------
# Allowed values
# ---------------------------------------------------------------------------

_VALID_ROLES = frozenset({"owner", "admin", "doctor", "staff", "viewer"})
_VALID_STATUSES = frozenset({"active", "inactive", "archived"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def _assert_nonempty(value: Any, name: str) -> None:
    if not value or not str(value).strip():
        raise InvalidUserError(f"{name!r} must not be empty")


# ---------------------------------------------------------------------------
# 1. get_user_by_email
# ---------------------------------------------------------------------------


async def get_user_by_email(
    pool: Any,
    clinic_id: str,
    email: str,
) -> Optional[Dict[str, Any]]:
    """Return the clinic_users row matching (clinic_id, email), or None."""
    _assert_nonempty(clinic_id, "clinic_id")
    _assert_nonempty(email, "email")
    row = await pool.fetchrow(
        """
        SELECT id, clinic_id, email, full_name, role, status, password_hash,
               created_at, updated_at
        FROM   clinic_users
        WHERE  clinic_id = $1 AND email = $2
        """,
        clinic_id,
        email.strip().lower(),
    )
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 2. get_user_by_id
# ---------------------------------------------------------------------------


async def get_user_by_id(
    pool: Any,
    user_id: str,
) -> Optional[Dict[str, Any]]:
    """Return the clinic_users row matching user_id, or None."""
    _assert_nonempty(user_id, "user_id")
    row = await pool.fetchrow(
        """
        SELECT id, clinic_id, email, full_name, role, status, password_hash,
               created_at, updated_at
        FROM   clinic_users
        WHERE  id = $1
        """,
        user_id,
    )
    return _row_to_dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# 3. create_user
# ---------------------------------------------------------------------------


async def create_user(
    pool: Any,
    clinic_id: str,
    email: str,
    full_name: str,
    role: str,
    password_hash: str,
) -> Dict[str, Any]:
    """Insert a new clinic_users row and return the created record.

    The caller is responsible for hashing the password before passing it here.
    No plaintext password is accepted or stored.
    """
    _assert_nonempty(clinic_id,     "clinic_id")
    _assert_nonempty(email,         "email")
    _assert_nonempty(full_name,     "full_name")
    _assert_nonempty(role,          "role")
    _assert_nonempty(password_hash, "password_hash")

    if role not in _VALID_ROLES:
        raise InvalidUserError(
            f"'role' must be one of {sorted(_VALID_ROLES)!r}; got {role!r}"
        )

    row = await pool.fetchrow(
        """
        INSERT INTO clinic_users (clinic_id, email, full_name, role, password_hash)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, clinic_id, email, full_name, role, status, password_hash,
                  created_at, updated_at
        """,
        clinic_id,
        email.strip().lower(),
        full_name.strip(),
        role,
        password_hash,
    )
    return _row_to_dict(row)
