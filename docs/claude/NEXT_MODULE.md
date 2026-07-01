# Sprint 5 / Module 49 — Local Runtime Database Pool Startup

Task scope:
Wire FastAPI runtime startup/shutdown to initialize and close the asyncpg database pool from DATABASE_URL.

Purpose:
Tests inject fake db_pool into app.state, but real local runtime does not initialize app.state.db_pool.
Local webhook/API requests therefore return "Database pool is not initialised."

This module adds safe runtime DB pool lifecycle management so local development can use the PostgreSQL Docker database created in Module 45.

Files created/updated:
- backend/app/main.py (lifespan handler added)
- backend/tests/test_app_lifespan_db_pool.py (new)

Commit message:
Sprint 5 / Module 49 — Local runtime database pool startup
