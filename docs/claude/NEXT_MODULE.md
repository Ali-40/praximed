# Sprint 5 / Module 45 — Local PostgreSQL Docker + Migration Runner Smoke Test

Task scope:
Create a safe local PostgreSQL Docker setup and migration runner smoke-test foundation.

Purpose:
PraxisMed now has an Alembic-style migration foundation, but it has not been prepared for real local
PostgreSQL execution. Before real Vapi/n8n setup, external AI providers, frontend work, or pilots,
the backend needs:

* a local PostgreSQL Docker Compose file
* a local environment example
* a migration runner script
* a database smoke-test script
* static tests verifying the setup is safe and does not hard-code production secrets

Files created:

* docker-compose.postgres.yml
* backend/.env.example
* backend/scripts/__init__.py
* backend/scripts/run_migrations.py
* backend/scripts/db_smoke_test.py
* backend/tests/test_local_db_setup_contract.py

Commit message:
Sprint 5 / Module 45 — Local PostgreSQL Docker and migration smoke test
