"""
Unit tests for backend/app/db/pool.py

All tests are fully isolated — no real database connection is made.
asyncpg.create_pool is replaced by an AsyncMock so the pool lifecycle
and health-check logic can be exercised in a pure unit-test context.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest


# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------


def _make_mock_pool() -> MagicMock:
    """
    Return a MagicMock that behaves like a minimal asyncpg.Pool:

    - pool.close()    → awaitable (AsyncMock)
    - pool.acquire()  → async context manager yielding a mock connection
    - conn.fetchval() → awaitable returning 1  (simulates SELECT 1)
    """
    pool = MagicMock(name="asyncpg_pool")

    # close() must be awaitable
    pool.close = AsyncMock()

    # acquire() must work as `async with pool.acquire() as conn`
    mock_conn = AsyncMock(name="asyncpg_conn")
    mock_conn.fetchval = AsyncMock(return_value=1)

    acquire_ctx = MagicMock()
    acquire_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    acquire_ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=acquire_ctx)

    return pool, mock_conn


# ---------------------------------------------------------------------------
# 1. Missing DATABASE_URL raises the custom error
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_missing_database_url_raises_when_env_absent():
    """create_db_pool must raise MissingDatabaseURLError when no URL is given
    and DATABASE_URL is not in the environment."""
    from backend.app.db.pool import create_db_pool, MissingDatabaseURLError

    with patch.dict(os.environ, {}, clear=False):
        # Ensure the key is absent regardless of the real environment
        os.environ.pop("DATABASE_URL", None)
        with pytest.raises(MissingDatabaseURLError, match="DATABASE_URL"):
            await create_db_pool()


@pytest.mark.asyncio
async def test_missing_database_url_raises_when_none_passed():
    """Passing None explicitly while DATABASE_URL is unset must also raise."""
    from backend.app.db.pool import create_db_pool, MissingDatabaseURLError

    env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(MissingDatabaseURLError):
            await create_db_pool(None)


@pytest.mark.asyncio
async def test_missing_database_url_raises_when_empty_string_passed():
    """An empty string is treated the same as None — no DSN → error."""
    from backend.app.db.pool import create_db_pool, MissingDatabaseURLError

    env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(MissingDatabaseURLError):
            await create_db_pool("")


# ---------------------------------------------------------------------------
# 2. Pool creation calls asyncpg.create_pool correctly
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_db_pool_calls_asyncpg_with_explicit_url():
    """create_db_pool must forward the DSN to asyncpg.create_pool."""
    from backend.app.db.pool import create_db_pool

    mock_pool, _ = _make_mock_pool()
    dsn = "postgresql://user:pass@localhost:5432/praximed"

    with patch("backend.app.db.pool.asyncpg.create_pool", new=AsyncMock(return_value=mock_pool)) as mock_create:
        pool = await create_db_pool(dsn)

    mock_create.assert_awaited_once()
    args, kwargs = mock_create.call_args
    assert args[0] == dsn or kwargs.get("dsn") == dsn or (args and args[0] == dsn)
    assert pool is mock_pool


@pytest.mark.asyncio
async def test_create_db_pool_reads_url_from_environment():
    """When no URL is passed, create_db_pool must read DATABASE_URL from env."""
    from backend.app.db.pool import create_db_pool

    mock_pool, _ = _make_mock_pool()
    dsn = "postgresql://env_user:env_pass@db:5432/praximed"

    with patch.dict(os.environ, {"DATABASE_URL": dsn}):
        with patch("backend.app.db.pool.asyncpg.create_pool", new=AsyncMock(return_value=mock_pool)) as mock_create:
            pool = await create_db_pool()

    mock_create.assert_awaited_once()
    called_dsn = mock_create.call_args.args[0] if mock_create.call_args.args else mock_create.call_args.kwargs.get("dsn", mock_create.call_args.kwargs.get("database_url"))
    # asyncpg.create_pool receives the DSN as the first positional argument
    assert mock_create.call_args.args[0] == dsn
    assert pool is mock_pool


@pytest.mark.asyncio
async def test_create_db_pool_passes_size_and_timeout():
    """Default pool sizing and timeout values must be forwarded to asyncpg."""
    from backend.app.db.pool import create_db_pool

    mock_pool, _ = _make_mock_pool()
    dsn = "postgresql://u:p@h/db"

    with patch("backend.app.db.pool.asyncpg.create_pool", new=AsyncMock(return_value=mock_pool)) as mock_create:
        await create_db_pool(dsn)

    _, kwargs = mock_create.call_args
    assert kwargs.get("min_size") == 2
    assert kwargs.get("max_size") == 10
    assert kwargs.get("command_timeout") == 30.0


# ---------------------------------------------------------------------------
# 3. close_db_pool calls pool.close()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_close_db_pool_calls_pool_close():
    """close_db_pool must await pool.close() exactly once."""
    from backend.app.db.pool import close_db_pool

    mock_pool, _ = _make_mock_pool()
    await close_db_pool(mock_pool)
    mock_pool.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_db_pool_with_none_does_not_raise():
    """Passing None must log a warning and return without raising."""
    from backend.app.db.pool import close_db_pool

    # Should not raise any exception
    await close_db_pool(None)


# ---------------------------------------------------------------------------
# 4. check_db_connection returns True on successful SELECT 1
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_db_connection_returns_true_on_success():
    """check_db_connection must return True when SELECT 1 succeeds."""
    from backend.app.db.pool import check_db_connection

    mock_pool, mock_conn = _make_mock_pool()
    result = await check_db_connection(mock_pool)

    assert result is True
    mock_conn.fetchval.assert_awaited_once_with("SELECT 1")


# ---------------------------------------------------------------------------
# 5. check_db_connection returns False on database exception
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_db_connection_returns_false_on_exception():
    """check_db_connection must catch any exception and return False."""
    from backend.app.db.pool import check_db_connection

    mock_pool = MagicMock(name="asyncpg_pool")

    # Make acquire().__aenter__ raise to simulate a connectivity failure
    acquire_ctx = MagicMock()
    acquire_ctx.__aenter__ = AsyncMock(side_effect=OSError("connection refused"))
    acquire_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_pool.acquire = MagicMock(return_value=acquire_ctx)

    result = await check_db_connection(mock_pool)
    assert result is False


@pytest.mark.asyncio
async def test_check_db_connection_returns_false_when_fetchval_raises():
    """check_db_connection returns False when fetchval itself raises."""
    from backend.app.db.pool import check_db_connection
    import asyncpg

    mock_pool, mock_conn = _make_mock_pool()
    mock_conn.fetchval = AsyncMock(
        side_effect=asyncpg.ConnectionDoesNotExistError("lost connection")
    )

    result = await check_db_connection(mock_pool)
    assert result is False
