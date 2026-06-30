"""
Shared FastAPI dependencies — PraxisMed Sprint 1 / Module 8

Dependencies defined here are injected into route handlers via
``Depends()``.  Keeping them in one module makes test overrides easy:
tests call ``app.dependency_overrides[get_db_pool] = lambda: fake_pool``.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request


def get_config_loader(request: Request) -> Any:
    """
    Return the ClinicConfigLoader stored on ``app.state.config_loader``.

    Raises 503 when the loader is absent so callers get a clear signal rather
    than an AttributeError traceback.
    """
    try:
        return request.app.state.config_loader
    except AttributeError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Config loader is not initialised. "
                "The service may still be starting up."
            ),
        )


def get_db_pool(request: Request) -> Any:
    """
    Return the asyncpg pool stored on ``app.state.db_pool``.

    The pool is attached during application startup (lifespan handler, added
    in a later sprint).  Raising 503 here gives load-balancers a clean signal
    that the instance is not yet ready rather than a misleading 500.
    """
    try:
        return request.app.state.db_pool
    except AttributeError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Database pool is not initialised. "
                "The service may still be starting up."
            ),
        )
