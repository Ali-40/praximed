"""Add clinic_onboarding_requests table — PraxisMed Sprint 19 / Module 132.

Revision ID: 0004_clinic_onboarding_requests
Revises: 0003_patient_id_appt_requests
Create Date: 2026-07-06

Stores pilot/onboarding requests submitted by doctors or clinic staff.
Does NOT create a production tenant automatically.
Does NOT store patient PHI.
production_phi_enabled is constrained to false by the DB itself.
"""

from __future__ import annotations

from alembic import op

revision = "0004_clinic_onboarding_requests"
down_revision = "0003_patient_id_appt_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS clinic_onboarding_requests (
            id                       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            clinic_name              TEXT        NOT NULL,
            clinic_type              TEXT,
            specialty                TEXT,
            city                     TEXT,
            address                  TEXT,
            website                  TEXT,
            doctor_name              TEXT        NOT NULL,
            contact_email            TEXT        NOT NULL,
            contact_phone            TEXT,
            preferred_language       TEXT        NOT NULL DEFAULT 'de',
            fallback_language        TEXT        NOT NULL DEFAULT 'en',
            supported_languages      JSONB       NOT NULL DEFAULT '["de","en"]',
            workflow_notes           TEXT,
            estimated_call_volume    TEXT,
            current_booking_system   TEXT,
            wants_ai_phone_intake    BOOLEAN     NOT NULL DEFAULT true,
            wants_dashboard          BOOLEAN     NOT NULL DEFAULT true,
            wants_notifications      BOOLEAN     NOT NULL DEFAULT false,
            pilot_interest_level     TEXT        NOT NULL DEFAULT 'new',
            status                   TEXT        NOT NULL DEFAULT 'submitted',
            source                   TEXT        NOT NULL DEFAULT 'onboarding_page',
            consent_pilot_contact    BOOLEAN     NOT NULL DEFAULT false,
            acknowledges_no_phi      BOOLEAN     NOT NULL DEFAULT false,
            production_phi_enabled   BOOLEAN     NOT NULL DEFAULT false,
            created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT clinic_onboarding_requests_status_check CHECK (
                status IN ('submitted', 'reviewed', 'demo_booked', 'pilot_approved', 'rejected', 'archived')
            ),
            CONSTRAINT clinic_onboarding_requests_preferred_language_check CHECK (
                preferred_language IN ('de', 'en')
            ),
            CONSTRAINT clinic_onboarding_requests_production_phi_false CHECK (
                production_phi_enabled = false
            )
        );
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_clinic_onboarding_requests_email
            ON clinic_onboarding_requests (contact_email);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_clinic_onboarding_requests_status
            ON clinic_onboarding_requests (status);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_clinic_onboarding_requests_created_at
            ON clinic_onboarding_requests (created_at);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_clinic_onboarding_requests_preferred_language
            ON clinic_onboarding_requests (preferred_language);
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_clinic_onboarding_requests_preferred_language;")
    op.execute("DROP INDEX IF EXISTS idx_clinic_onboarding_requests_created_at;")
    op.execute("DROP INDEX IF EXISTS idx_clinic_onboarding_requests_status;")
    op.execute("DROP INDEX IF EXISTS idx_clinic_onboarding_requests_email;")
    op.execute("DROP TABLE IF EXISTS clinic_onboarding_requests;")
