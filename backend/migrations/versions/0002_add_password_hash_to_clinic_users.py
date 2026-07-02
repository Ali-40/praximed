"""Add password_hash column to clinic_users — PraxisMed Sprint 7 / Module 59.

Revision ID: 0002_password_hash
Revises: 0001_initial_schema
Create Date: 2026-07-02

Adds the password_hash TEXT column to clinic_users so that clinic staff
can authenticate via email + password.  The column is nullable to preserve
compatibility with existing rows that were created before this migration.
"""

from __future__ import annotations

from alembic import op

revision = "0002_password_hash"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE clinic_users ADD COLUMN IF NOT EXISTS password_hash TEXT;"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE clinic_users DROP COLUMN IF EXISTS password_hash;"
    )
