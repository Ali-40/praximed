"""Add consent_events table — PraxisMed Sprint 20 / Module 148.

Revision ID: 0006_consent_events
Revises: 0005_clinic_vapi_bindings
Create Date: 2026-07-08

Consent ledger: records who consented to what, when, for what purpose, via which
channel, and in which language. Append-only; revocation uses revoked_at marker.

No real patient PHI stored here. No history write authorised yet.
production_phi_enabled is always false and enforced by DB CHECK constraint.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

from alembic import op

revision = "0006_consent_events"
down_revision = "0005_clinic_vapi_bindings"
branch_labels = None
depends_on = None

_CHANNEL_VALUES = "('onboarding_form','intake_link','phone_call','staff_console','developer_console','import_demo')"
_LANGUAGE_VALUES = "('de','en','ar')"
_PURPOSE_VALUES = "('appointment_intake','patient_history_collection','phone_history_questions','demo_seed','data_processing_acknowledgement')"


def upgrade() -> None:
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS consent_events (
            id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
            patient_id              UUID        REFERENCES patients(id) ON DELETE SET NULL,
            appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
            consent_subject_type    TEXT        NOT NULL DEFAULT 'patient',
            consent_subject_ref     TEXT,
            purpose                 TEXT        NOT NULL,
            scope                   TEXT        NOT NULL,
            channel                 TEXT        NOT NULL,
            language                TEXT        NOT NULL DEFAULT 'de',
            consent_text_version    TEXT        NOT NULL,
            consent_text_snapshot   TEXT        NOT NULL,
            granted                 BOOLEAN     NOT NULL DEFAULT true,
            revoked_at              TIMESTAMPTZ,
            revoked_by_user_id      UUID,
            revocation_reason       TEXT,
            captured_by_user_id     UUID,
            captured_by_system      TEXT,
            source_ip_hash          TEXT,
            user_agent_hash         TEXT,
            metadata                JSONB       NOT NULL DEFAULT '{{}}'::jsonb,
            production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT consent_events_production_phi_check CHECK (
                production_phi_enabled = false
            ),
            CONSTRAINT consent_events_channel_check CHECK (
                channel IN {_CHANNEL_VALUES}
            ),
            CONSTRAINT consent_events_language_check CHECK (
                language IN {_LANGUAGE_VALUES}
            ),
            CONSTRAINT consent_events_purpose_check CHECK (
                purpose IN {_PURPOSE_VALUES}
            )
        );
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_consent_events_clinic_id
            ON consent_events (clinic_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_consent_events_patient_id
            ON consent_events (patient_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_consent_events_appointment_request_id
            ON consent_events (appointment_request_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_consent_events_purpose
            ON consent_events (purpose);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_consent_events_channel
            ON consent_events (channel);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_consent_events_language
            ON consent_events (language);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_consent_events_granted
            ON consent_events (granted);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_consent_events_created_at
            ON consent_events (created_at);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_consent_events_revoked_at
            ON consent_events (revoked_at);
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_consent_events_revoked_at;")
    op.execute("DROP INDEX IF EXISTS idx_consent_events_created_at;")
    op.execute("DROP INDEX IF EXISTS idx_consent_events_granted;")
    op.execute("DROP INDEX IF EXISTS idx_consent_events_language;")
    op.execute("DROP INDEX IF EXISTS idx_consent_events_channel;")
    op.execute("DROP INDEX IF EXISTS idx_consent_events_purpose;")
    op.execute("DROP INDEX IF EXISTS idx_consent_events_appointment_request_id;")
    op.execute("DROP INDEX IF EXISTS idx_consent_events_patient_id;")
    op.execute("DROP INDEX IF EXISTS idx_consent_events_clinic_id;")
    op.execute("DROP TABLE IF EXISTS consent_events;")
