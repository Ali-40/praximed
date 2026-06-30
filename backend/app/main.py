"""
PraxisMed API — FastAPI application entry point (Sprint 1 / Module 7)

Start the server with:
    uvicorn backend.app.main:app --reload

The database pool, authentication middleware, and additional routers will be
wired up in later sprints.  This skeleton keeps startup side-effects to a
minimum so the app can be imported safely in tests without any I/O.
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.app.api.router import api_router

app = FastAPI(
    title="PraxisMed API",
    version="0.1.0",
    description=(
        "Multi-tenant AI automation backend for private medical clinics in Austria."
    ),
)

app.include_router(api_router)
