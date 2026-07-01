"""
Alembic environment — PraxisMed Sprint 4 / Module 41

Database URL is read from the DATABASE_URL environment variable at migration
run time. No credentials are hard-coded. No application modules are imported.
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_url() -> str:
    """Read the database URL from the DATABASE_URL environment variable."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Export it before running Alembic migrations. "
            "Example: export DATABASE_URL=<driver>://<user>:<pass>@<host>/<db>"
        )
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL script output, no live DB)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a live database connection."""
    from sqlalchemy import create_engine

    connectable = create_engine(get_url())
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
