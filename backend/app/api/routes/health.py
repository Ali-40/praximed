"""
Health routes — PraxisMed Sprint 1 / Module 7

Two lightweight endpoints that allow load-balancers, uptime monitors, and
container orchestrators to check whether the application is alive (liveness)
and ready to serve traffic (readiness).

/health        — liveness probe  (always returns ok if the process is up)
/health/ready  — readiness probe (will later include DB / dependency checks)
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_liveness() -> dict:
    """Liveness probe — confirms the application process is running."""
    return {"status": "ok", "service": "PraxisMed API"}


@router.get("/health/ready")
async def health_readiness() -> dict:
    """
    Readiness probe — confirms the application is ready to handle requests.

    The ``app`` check is always ``ok`` while the process is alive.
    Future versions will add ``database`` and other dependency checks here
    using the asyncpg pool stored on ``request.app.state``.
    """
    return {
        "status": "ready",
        "checks": {
            "app": "ok",
        },
    }
