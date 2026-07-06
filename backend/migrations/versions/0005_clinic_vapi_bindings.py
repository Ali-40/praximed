"""Add clinic_vapi_bindings table — PraxisMed Sprint 19 / Module 145.

Revision ID: 0005_clinic_vapi_bindings
Revises: 0004_clinic_onboarding_requests
Create Date: 2026-07-06

Stores Vapi binding metadata — secret reference names only, never secret values.
No VAPI_API_KEY value stored. No VAPI_WEBHOOK_SECRET value stored. No PHI.
production_phi_enabled is not a column here; it is enforced at the service layer.
"""

from __future__ import annotations

from alembic import op

revision = "0005_clinic_vapi_bindings"
down_revision = "0004_clinic_onboarding_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS clinic_vapi_bindings (
            id                       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            clinic_id                UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
            assistant_id             TEXT,
            phone_number_id          TEXT,
            vapi_project_id          TEXT,
            api_key_secret_ref       TEXT        NOT NULL,
            webhook_secret_ref       TEXT        NOT NULL,
            assistant_config_version TEXT,
            language_mode            TEXT        NOT NULL DEFAULT 'german_first',
            status                   TEXT        NOT NULL DEFAULT 'draft',
            created_by_user_id       UUID,
            created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT clinic_vapi_bindings_status_check CHECK (
                status IN ('draft', 'configured', 'disabled', 'revoked')
            ),
            CONSTRAINT clinic_vapi_bindings_language_mode_check CHECK (
                language_mode IN ('german_first', 'english_first', 'bilingual_auto')
            )
        );
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_clinic_vapi_bindings_clinic_id
            ON clinic_vapi_bindings (clinic_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_clinic_vapi_bindings_status
            ON clinic_vapi_bindings (status);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_clinic_vapi_bindings_language_mode
            ON clinic_vapi_bindings (language_mode);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_clinic_vapi_bindings_created_at
            ON clinic_vapi_bindings (created_at);
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_clinic_vapi_bindings_created_at;")
    op.execute("DROP INDEX IF EXISTS idx_clinic_vapi_bindings_language_mode;")
    op.execute("DROP INDEX IF EXISTS idx_clinic_vapi_bindings_status;")
    op.execute("DROP INDEX IF EXISTS idx_clinic_vapi_bindings_clinic_id;")
    op.execute("DROP TABLE IF EXISTS clinic_vapi_bindings;")
