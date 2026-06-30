"""
PostgreSQL connection pool — PraxisMed Sprint 1 / Module 2

Public API
----------
create_db_pool(database_url)  -> asyncpg.Pool
close_db_pool(pool)           -> None
check_db_connection(pool)     -> bool

The pool is created via asyncpg.create_pool and is intended to be initialised
once at application start-up and stored on the FastAPI app state object.  It is
intentionally kept framework-agnostic so it can be used from CLI scripts,
background workers, and test fixtures without importing FastAPI.

Configuration
-------------
DATABASE_URL is read from the environment when not supplied explicitly.
Expected format: postgresql://user:password@host:port/dbname
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class MissingDatabaseURLError(RuntimeError):
    """Raised when DATABASE_URL is not provided and not set in the environment."""


# ---------------------------------------------------------------------------
# Pool lifecycle
# ---------------------------------------------------------------------------


async def create_db_pool(
    database_url: Optional[str] = None,
    *,
    min_size: int = 2,
    max_size: int = 10,
    command_timeout: float = 30.0,
) -> asyncpg.Pool:
    """
    Create and return an asyncpg connection pool.

    Parameters
    ----------
    database_url:
        PostgreSQL DSN.  Reads ``DATABASE_URL`` from the environment when
        omitted or ``None``.
    min_size:
        Minimum number of connections kept open in the pool.
    max_size:
        Maximum number of connections the pool will open simultaneously.
    command_timeout:
        Per-query timeout in seconds passed to asyncpg.

    Raises
    ------
    MissingDatabaseURLError
        When no URL is provided and ``DATABASE_URL`` is absent from the
        environment.
    asyncpg.PostgresError
        Propagated directly when the initial connection attempt fails so the
        caller can distinguish a configuration error from a connectivity error.
    """
    url = database_url or os.environ.get("DATABASE_URL")
    if not url:
        raise MissingDatabaseURLError(
            "DATABASE_URL is required but was not provided and is not set in "
            "the environment.  Set it as an environment variable or pass it "
            "explicitly to create_db_pool()."
        )

    logger.info("Creating asyncpg pool (min=%d, max=%d)", min_size, max_size)
    pool: asyncpg.Pool = await asyncpg.create_pool(
        url,
        min_size=min_size,
        max_size=max_size,
        command_timeout=command_timeout,
    )
    logger.info("asyncpg pool created successfully")
    return pool


async def close_db_pool(pool: asyncpg.Pool) -> None:
    """
    Gracefully close all connections in *pool*.

    Safe to call even if the pool is already closed; asyncpg is idempotent
    here.  Logs a warning instead of raising so shutdown code stays clean.
    """
    if pool is None:
        logger.warning("close_db_pool called with None — skipping")
        return
    logger.info("Closing asyncpg pool")
    await pool.close()
    logger.info("asyncpg pool closed")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


async def check_db_connection(pool: asyncpg.Pool) -> bool:
    """
    Return ``True`` when the database is reachable, ``False`` otherwise.

    Acquires a single connection from the pool, runs ``SELECT 1``, and
    releases it immediately.  Any exception is caught and logged so this
    function is safe to call from health-check endpoints without try/except
    at the call site.
    """
    try:
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Database health check failed: %s", exc)
        return False
