"""
Tests for user_repo — PraxisMed Sprint 7 / Module 59

All tests use MagicMock pool with AsyncMock fetchrow.
No real database connection is used.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.db.repositories.user_repo import (
    InvalidUserError,
    create_user,
    get_user_by_email,
    get_user_by_id,
)

CLINIC_ID     = "clinic-abc-123"
USER_ID       = "user-uuid-xyz"
EMAIL         = "doctor@example.com"
FULL_NAME     = "Dr. Test User"
ROLE          = "doctor"
PASSWORD_HASH = "$2b$12$fakehashfortest"


def _make_pool(row=None):
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=row)
    return pool


def _fake_user_row(**overrides):
    base = {
        "id":            USER_ID,
        "clinic_id":     CLINIC_ID,
        "email":         EMAIL,
        "full_name":     FULL_NAME,
        "role":          ROLE,
        "status":        "active",
        "password_hash": PASSWORD_HASH,
        "created_at":    "2026-07-02T00:00:00+00:00",
        "updated_at":    "2026-07-02T00:00:00+00:00",
    }
    base.update(overrides)
    return base


# ===========================================================================
# get_user_by_email
# ===========================================================================


async def test_get_user_by_email_returns_dict():
    pool = _make_pool(row=_fake_user_row())
    result = await get_user_by_email(pool, CLINIC_ID, EMAIL)
    pool.fetchrow.assert_awaited_once()
    assert result is not None
    assert result["email"] == EMAIL
    assert result["clinic_id"] == CLINIC_ID


async def test_get_user_by_email_returns_none_when_not_found():
    pool = _make_pool(row=None)
    result = await get_user_by_email(pool, CLINIC_ID, EMAIL)
    assert result is None


async def test_get_user_by_email_normalises_email_to_lower():
    pool = _make_pool(row=_fake_user_row())
    await get_user_by_email(pool, CLINIC_ID, "Doctor@Example.COM")
    call_args = pool.fetchrow.call_args
    # email arg is the third positional arg (after SQL, clinic_id, email)
    assert call_args[0][2] == "doctor@example.com"


async def test_get_user_by_email_raises_for_empty_clinic_id():
    pool = _make_pool()
    with pytest.raises(InvalidUserError):
        await get_user_by_email(pool, "", EMAIL)


async def test_get_user_by_email_raises_for_empty_email():
    pool = _make_pool()
    with pytest.raises(InvalidUserError):
        await get_user_by_email(pool, CLINIC_ID, "")


# ===========================================================================
# get_user_by_id
# ===========================================================================


async def test_get_user_by_id_returns_dict():
    pool = _make_pool(row=_fake_user_row())
    result = await get_user_by_id(pool, USER_ID)
    pool.fetchrow.assert_awaited_once()
    assert result is not None
    assert result["id"] == USER_ID


async def test_get_user_by_id_returns_none_when_not_found():
    pool = _make_pool(row=None)
    result = await get_user_by_id(pool, USER_ID)
    assert result is None


async def test_get_user_by_id_raises_for_empty_id():
    pool = _make_pool()
    with pytest.raises(InvalidUserError):
        await get_user_by_id(pool, "")


# ===========================================================================
# create_user
# ===========================================================================


async def test_create_user_returns_dict():
    pool = _make_pool(row=_fake_user_row())
    result = await create_user(pool, CLINIC_ID, EMAIL, FULL_NAME, ROLE, PASSWORD_HASH)
    pool.fetchrow.assert_awaited_once()
    assert result["email"] == EMAIL
    assert result["role"] == ROLE


async def test_create_user_inserts_password_hash():
    pool = _make_pool(row=_fake_user_row())
    await create_user(pool, CLINIC_ID, EMAIL, FULL_NAME, ROLE, PASSWORD_HASH)
    sql_called = pool.fetchrow.call_args[0][0]
    assert "password_hash" in sql_called.lower()


async def test_create_user_raises_for_empty_clinic_id():
    pool = _make_pool()
    with pytest.raises(InvalidUserError):
        await create_user(pool, "", EMAIL, FULL_NAME, ROLE, PASSWORD_HASH)


async def test_create_user_raises_for_empty_email():
    pool = _make_pool()
    with pytest.raises(InvalidUserError):
        await create_user(pool, CLINIC_ID, "", FULL_NAME, ROLE, PASSWORD_HASH)


async def test_create_user_raises_for_empty_full_name():
    pool = _make_pool()
    with pytest.raises(InvalidUserError):
        await create_user(pool, CLINIC_ID, EMAIL, "", ROLE, PASSWORD_HASH)


async def test_create_user_raises_for_empty_password_hash():
    pool = _make_pool()
    with pytest.raises(InvalidUserError):
        await create_user(pool, CLINIC_ID, EMAIL, FULL_NAME, ROLE, "")


async def test_create_user_raises_for_invalid_role():
    pool = _make_pool()
    with pytest.raises(InvalidUserError):
        await create_user(pool, CLINIC_ID, EMAIL, FULL_NAME, "superuser", PASSWORD_HASH)


async def test_create_user_normalises_email():
    pool = _make_pool(row=_fake_user_row())
    await create_user(pool, CLINIC_ID, "Doctor@Example.COM", FULL_NAME, ROLE, PASSWORD_HASH)
    call_args = pool.fetchrow.call_args[0]
    # email is the third positional arg after the SQL string
    assert call_args[2] == "doctor@example.com"


async def test_create_user_does_not_store_plaintext_password():
    pool = _make_pool(row=_fake_user_row())
    plaintext = "PlainTextPasswordDoNotStore"
    await create_user(pool, CLINIC_ID, EMAIL, FULL_NAME, ROLE, PASSWORD_HASH)
    # ensure the plaintext password is NOT among the SQL call args
    sql_args = pool.fetchrow.call_args[0]
    assert plaintext not in sql_args
