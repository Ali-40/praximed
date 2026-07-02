"""
PraxisMed API — FastAPI application entry point (Sprint 1 / Module 7)
Updated: Sprint 9 / Module 74 — local frontend CORS support
Updated: Sprint 11 / Module 84 — wire app.state.config_loader in lifespan

Start the server with:
    python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

Database pool lifecycle (Module 49)
-------------------------------------
On startup the app reads DATABASE_URL from the environment and initialises an
asyncpg connection pool via create_db_pool, storing it on app.state.db_pool.
If DATABASE_URL is absent the pool is set to None and DB-backed routes return
503 until the variable is configured — the app itself does not crash.
On shutdown the pool is closed and app.state.db_pool is reset to None.

No migrations are run automatically; use backend/scripts/run_migrations.py.

CORS (Module 74)
------------------
Set FRONTEND_CORS_ORIGINS (comma-separated) to override the default allowed origins.
Default: http://localhost:3000, http://127.0.0.1:3000
Wildcard origins are never used; only explicit origins are permitted.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.core.config_loader import ClinicConfigLoader
from backend.app.db.pool import close_db_pool, create_db_pool

# ---------------------------------------------------------------------------
# CORS — local frontend origins
# ---------------------------------------------------------------------------

_DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def _cors_origins() -> list[str]:
    """Return allowed CORS origins from env or local-dev default.

    Set FRONTEND_CORS_ORIGINS to a comma-separated list to override.
    Wildcard origins (*) are never returned.
    """
    raw = os.environ.get("FRONTEND_CORS_ORIGINS", "")
    if raw.strip():
        return [o.strip() for o in raw.split(",") if o.strip()]
    return _DEFAULT_CORS_ORIGINS

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # --------------- startup ---------------
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        try:
            pool = await create_db_pool(database_url)
            app.state.db_pool = pool
            logger.info("Database pool initialised successfully")
        except Exception as exc:
            logger.error("Failed to initialise database pool: %s", exc)
            app.state.db_pool = None
    else:
        logger.warning(
            "DATABASE_URL is not set — app.state.db_pool is None. "
            "DB-backed routes will return 503 until DATABASE_URL is configured."
        )
        app.state.db_pool = None

    # Config loader — available even without a DB pool (disk-only config fallback).
    # Routes that call get_config_loader() rely on this being set.
    app.state.config_loader = ClinicConfigLoader(pool=app.state.db_pool)

    yield

    # --------------- shutdown ---------------
    pool = getattr(app.state, "db_pool", None)
    if pool is not None:
        await close_db_pool(pool)
        app.state.db_pool = None
    app.state.config_loader = None


app = FastAPI(
    title="PraxisMed API",
    version="0.1.0",
    description=(
        "Multi-tenant AI automation backend for private medical clinics in Austria."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "PUT"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(api_router)
