"""Initial schema baseline — PraxisMed Modules 1–40.

Revision ID: 0001_initial_schema
Revises: (none — this is the baseline)
Create Date: 2026-07-01

Captures the full schema from backend/app/db/schema.sql as it existed at
Module 40 (Sprint 3 complete).  All subsequent schema changes must be applied
through new migration files, not by modifying this one.

Tables created (in dependency order):
  clinics
  clinic_users
  clinic_calendar_connections
  clinic_calendar_blocks
  clinic_calendar_sync_events
  audit_log
  clinic_call_logs
  appointment_requests
  clinic_notifications
  patients
  consultation_sessions
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the full PraxisMed schema: all tables, indexes, and constraints."""

    op.execute("""
-- ===========================================================================
-- Enable extensions
-- ===========================================================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ===========================================================================
-- A) clinics — root tenant table
-- ===========================================================================
CREATE TABLE IF NOT EXISTS clinics (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            TEXT        UNIQUE NOT NULL,
    name            TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'active',
    config_path     TEXT,
    config_version  INTEGER     NOT NULL DEFAULT 1,
    timezone        TEXT        NOT NULL DEFAULT 'Europe/Vienna',
    locale          TEXT        NOT NULL DEFAULT 'de-AT',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_clinics_slug
    ON clinics (slug);

CREATE INDEX IF NOT EXISTS idx_clinics_status
    ON clinics (status);

-- ===========================================================================
-- B) clinic_users — staff / admin users belonging to a clinic
-- ===========================================================================
CREATE TABLE IF NOT EXISTS clinic_users (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id   UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    email       TEXT        NOT NULL,
    full_name   TEXT        NOT NULL,
    role        TEXT        NOT NULL,
    status      TEXT        NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (clinic_id, email)
);

CREATE INDEX IF NOT EXISTS idx_clinic_users_clinic_id
    ON clinic_users (clinic_id);

-- ===========================================================================
-- C) clinic_calendar_connections — external calendar provider connections
-- ===========================================================================
CREATE TABLE IF NOT EXISTS clinic_calendar_connections (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id            UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    provider             TEXT        NOT NULL,
    external_calendar_id TEXT        NOT NULL,
    sync_status          TEXT        NOT NULL DEFAULT 'active',
    last_synced_at       TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (clinic_id, provider, external_calendar_id)
);

CREATE INDEX IF NOT EXISTS idx_clinic_calendar_connections_clinic_id
    ON clinic_calendar_connections (clinic_id);

-- ===========================================================================
-- D) clinic_calendar_blocks — busy periods the booking layer must respect
-- ===========================================================================
CREATE TABLE IF NOT EXISTS clinic_calendar_blocks (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id         UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    connection_id     UUID        REFERENCES clinic_calendar_connections(id) ON DELETE SET NULL,
    external_event_id TEXT,
    title             TEXT,
    block_type        TEXT        NOT NULL,
    starts_at         TIMESTAMPTZ NOT NULL,
    ends_at           TIMESTAMPTZ NOT NULL,
    is_all_day        BOOLEAN     NOT NULL DEFAULT false,
    source            TEXT        NOT NULL DEFAULT 'calendar_sync',
    raw_payload       JSONB,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT clinic_calendar_blocks_ends_after_starts CHECK (ends_at > starts_at)
);

CREATE INDEX IF NOT EXISTS idx_clinic_calendar_blocks_clinic_time
    ON clinic_calendar_blocks (clinic_id, starts_at, ends_at);

CREATE INDEX IF NOT EXISTS idx_clinic_calendar_blocks_clinic_type
    ON clinic_calendar_blocks (clinic_id, block_type);

-- ===========================================================================
-- E) clinic_calendar_sync_events — append-only sync log
-- ===========================================================================
CREATE TABLE IF NOT EXISTS clinic_calendar_sync_events (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id     UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    connection_id UUID        REFERENCES clinic_calendar_connections(id) ON DELETE SET NULL,
    event_type    TEXT        NOT NULL,
    status        TEXT        NOT NULL,
    message       TEXT,
    raw_payload   JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_clinic_calendar_sync_events_clinic_created
    ON clinic_calendar_sync_events (clinic_id, created_at);

-- ===========================================================================
-- F) audit_log — immutable compliance trail
-- ===========================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id     UUID        REFERENCES clinics(id) ON DELETE SET NULL,
    actor_type    TEXT        NOT NULL,
    actor_id      TEXT,
    action        TEXT        NOT NULL,
    resource_type TEXT        NOT NULL,
    resource_id   TEXT,
    metadata      JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_clinic_created
    ON audit_log (clinic_id, created_at);

-- ===========================================================================
-- G) clinic_call_logs — one row per Vapi phone call
-- ===========================================================================
CREATE TABLE IF NOT EXISTS clinic_call_logs (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id        UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    provider         TEXT        NOT NULL DEFAULT 'vapi',
    external_call_id TEXT        NOT NULL,
    caller_phone     TEXT,
    direction        TEXT        NOT NULL DEFAULT 'inbound',
    call_status      TEXT        NOT NULL,
    started_at       TIMESTAMPTZ,
    ended_at         TIMESTAMPTZ,
    duration_seconds INTEGER,
    transcript_text  TEXT,
    summary          TEXT,
    action_required  BOOLEAN     NOT NULL DEFAULT false,
    urgency_level    TEXT        NOT NULL DEFAULT 'normal',
    raw_payload      JSONB,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (clinic_id, provider, external_call_id)
);

CREATE INDEX IF NOT EXISTS idx_clinic_call_logs_clinic_created
    ON clinic_call_logs (clinic_id, created_at);

CREATE INDEX IF NOT EXISTS idx_clinic_call_logs_clinic_status
    ON clinic_call_logs (clinic_id, call_status);

CREATE INDEX IF NOT EXISTS idx_clinic_call_logs_clinic_action
    ON clinic_call_logs (clinic_id, action_required);

CREATE INDEX IF NOT EXISTS idx_clinic_call_logs_clinic_urgency
    ON clinic_call_logs (clinic_id, urgency_level);

-- ===========================================================================
-- H) appointment_requests — patient appointment requests for staff review
-- ===========================================================================
CREATE TABLE IF NOT EXISTS appointment_requests (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id           UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    source              TEXT        NOT NULL,
    source_ref          TEXT,
    patient_name        TEXT        NOT NULL,
    patient_phone       TEXT,
    patient_email       TEXT,
    date_of_birth       DATE,
    reason              TEXT,
    preferred_starts_at TIMESTAMPTZ,
    preferred_ends_at   TIMESTAMPTZ,
    status              TEXT        NOT NULL DEFAULT 'new',
    urgency_level       TEXT        NOT NULL DEFAULT 'normal',
    action_required     BOOLEAN     NOT NULL DEFAULT true,
    assigned_user_id    UUID        REFERENCES clinic_users(id) ON DELETE SET NULL,
    raw_payload         JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT appointment_requests_time_range_check CHECK (
        preferred_ends_at IS NULL OR preferred_starts_at IS NULL OR preferred_ends_at > preferred_starts_at
    ),
    CONSTRAINT appointment_requests_status_check CHECK (
        status IN ('new', 'confirmed', 'rejected', 'callback_needed', 'cancelled', 'archived')
    ),
    CONSTRAINT appointment_requests_urgency_check CHECK (
        urgency_level IN ('low', 'normal', 'urgent', 'emergency')
    ),
    CONSTRAINT appointment_requests_source_check CHECK (
        source IN ('vapi', 'whatsapp', 'web', 'staff', 'system')
    )
);

CREATE INDEX IF NOT EXISTS idx_appointment_requests_clinic_created
    ON appointment_requests (clinic_id, created_at);

CREATE INDEX IF NOT EXISTS idx_appointment_requests_clinic_status
    ON appointment_requests (clinic_id, status);

CREATE INDEX IF NOT EXISTS idx_appointment_requests_clinic_action
    ON appointment_requests (clinic_id, action_required);

CREATE INDEX IF NOT EXISTS idx_appointment_requests_clinic_urgency
    ON appointment_requests (clinic_id, urgency_level);

CREATE INDEX IF NOT EXISTS idx_appointment_requests_clinic_preferred_starts
    ON appointment_requests (clinic_id, preferred_starts_at);

CREATE INDEX IF NOT EXISTS idx_appointment_requests_clinic_source
    ON appointment_requests (clinic_id, source);

-- ===========================================================================
-- I) clinic_notifications — internal staff notification records
-- ===========================================================================
CREATE TABLE IF NOT EXISTS clinic_notifications (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id             UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    recipient_user_id     UUID        REFERENCES clinic_users(id) ON DELETE SET NULL,
    channel               TEXT        NOT NULL,
    notification_type     TEXT        NOT NULL,
    priority              TEXT        NOT NULL DEFAULT 'normal',
    title                 TEXT        NOT NULL,
    message               TEXT        NOT NULL,
    status                TEXT        NOT NULL DEFAULT 'pending',
    related_resource_type TEXT,
    related_resource_id   TEXT,
    scheduled_for         TIMESTAMPTZ,
    sent_at               TIMESTAMPTZ,
    read_at               TIMESTAMPTZ,
    error_message         TEXT,
    raw_payload           JSONB,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT clinic_notifications_channel_check CHECK (
        channel IN ('internal', 'sms', 'push', 'email', 'webhook')
    ),
    CONSTRAINT clinic_notifications_type_check CHECK (
        notification_type IN ('urgent_call', 'human_handoff', 'callback_needed', 'appointment_request', 'cancellation', 'calendar_sync_failure', 'summary_ready', 'system')
    ),
    CONSTRAINT clinic_notifications_priority_check CHECK (
        priority IN ('low', 'normal', 'high', 'urgent', 'emergency')
    ),
    CONSTRAINT clinic_notifications_status_check CHECK (
        status IN ('pending', 'sent', 'failed', 'read', 'cancelled')
    )
);

CREATE INDEX IF NOT EXISTS idx_clinic_notifications_clinic_created
    ON clinic_notifications (clinic_id, created_at);

CREATE INDEX IF NOT EXISTS idx_clinic_notifications_clinic_status
    ON clinic_notifications (clinic_id, status);

CREATE INDEX IF NOT EXISTS idx_clinic_notifications_clinic_priority
    ON clinic_notifications (clinic_id, priority);

CREATE INDEX IF NOT EXISTS idx_clinic_notifications_clinic_type
    ON clinic_notifications (clinic_id, notification_type);

CREATE INDEX IF NOT EXISTS idx_clinic_notifications_clinic_recipient
    ON clinic_notifications (clinic_id, recipient_user_id);

CREATE INDEX IF NOT EXISTS idx_clinic_notifications_clinic_scheduled
    ON clinic_notifications (clinic_id, scheduled_for);

CREATE INDEX IF NOT EXISTS idx_clinic_notifications_clinic_resource
    ON clinic_notifications (clinic_id, related_resource_type, related_resource_id);

-- ===========================================================================
-- J) patients — multi-tenant patient identity and contact data
-- ===========================================================================
CREATE TABLE IF NOT EXISTS patients (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id           UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    external_patient_id TEXT,
    full_name           TEXT        NOT NULL,
    date_of_birth       DATE,
    phone               TEXT,
    email               TEXT,
    preferred_language  TEXT        NOT NULL DEFAULT 'de-AT',
    status              TEXT        NOT NULL DEFAULT 'active',
    notes               TEXT,
    raw_payload         JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (clinic_id, external_patient_id),
    CONSTRAINT patients_status_check CHECK (
        status IN ('active', 'inactive', 'archived')
    ),
    CONSTRAINT patients_preferred_language_check CHECK (
        preferred_language <> ''
    ),
    CONSTRAINT patients_full_name_check CHECK (
        full_name <> ''
    )
);

CREATE INDEX IF NOT EXISTS idx_patients_clinic_created
    ON patients (clinic_id, created_at);

CREATE INDEX IF NOT EXISTS idx_patients_clinic_full_name
    ON patients (clinic_id, full_name);

CREATE INDEX IF NOT EXISTS idx_patients_clinic_dob
    ON patients (clinic_id, date_of_birth);

CREATE INDEX IF NOT EXISTS idx_patients_clinic_phone
    ON patients (clinic_id, phone);

CREATE INDEX IF NOT EXISTS idx_patients_clinic_email
    ON patients (clinic_id, email);

CREATE INDEX IF NOT EXISTS idx_patients_clinic_status
    ON patients (clinic_id, status);

CREATE INDEX IF NOT EXISTS idx_patients_clinic_external_id
    ON patients (clinic_id, external_patient_id);

-- ===========================================================================
-- K) consultation_sessions — full clinical documentation lifecycle
-- ===========================================================================
CREATE TABLE IF NOT EXISTS consultation_sessions (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id           UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id          UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_user_id      UUID        REFERENCES clinic_users(id) ON DELETE SET NULL,
    source              TEXT        NOT NULL DEFAULT 'manual',
    status              TEXT        NOT NULL DEFAULT 'created',
    title               TEXT,
    reason_for_visit    TEXT,
    audio_file_path     TEXT,
    transcript_text     TEXT,
    draft_summary       JSONB,
    approved_summary    JSONB,
    approval_status     TEXT        NOT NULL DEFAULT 'not_ready',
    approved_by_user_id UUID        REFERENCES clinic_users(id) ON DELETE SET NULL,
    approved_at         TIMESTAMPTZ,
    rejected_reason     TEXT,
    raw_payload         JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT consultation_sessions_source_check CHECK (
        source IN ('manual', 'vapi', 'web', 'doctor_mobile', 'system')
    ),
    CONSTRAINT consultation_sessions_status_check CHECK (
        status IN ('created', 'recording', 'audio_uploaded', 'transcribing', 'transcribed', 'draft_ready', 'approved', 'rejected', 'archived')
    ),
    CONSTRAINT consultation_sessions_approval_status_check CHECK (
        approval_status IN ('not_ready', 'pending_review', 'approved', 'rejected')
    ),
    CONSTRAINT consultation_sessions_approved_at_check CHECK (
        (approval_status = 'approved' AND approved_at IS NOT NULL)
        OR approval_status <> 'approved'
    )
);

CREATE INDEX IF NOT EXISTS idx_consultation_sessions_clinic_created
    ON consultation_sessions (clinic_id, created_at);

CREATE INDEX IF NOT EXISTS idx_consultation_sessions_clinic_patient
    ON consultation_sessions (clinic_id, patient_id);

CREATE INDEX IF NOT EXISTS idx_consultation_sessions_clinic_doctor
    ON consultation_sessions (clinic_id, doctor_user_id);

CREATE INDEX IF NOT EXISTS idx_consultation_sessions_clinic_status
    ON consultation_sessions (clinic_id, status);

CREATE INDEX IF NOT EXISTS idx_consultation_sessions_clinic_approval
    ON consultation_sessions (clinic_id, approval_status);

CREATE INDEX IF NOT EXISTS idx_consultation_sessions_clinic_approved_at
    ON consultation_sessions (clinic_id, approved_at);

CREATE INDEX IF NOT EXISTS idx_consultation_sessions_clinic_source
    ON consultation_sessions (clinic_id, source);
""")


def downgrade() -> None:
    """Drop all tables in reverse dependency order (children before parents)."""

    op.execute("""
-- Drop in reverse dependency order so foreign key constraints are satisfied.

-- consultation_sessions depends on: patients, clinic_users, clinics
DROP TABLE IF EXISTS consultation_sessions;

-- patients depends on: clinics
DROP TABLE IF EXISTS patients;

-- clinic_notifications depends on: clinic_users, clinics
DROP TABLE IF EXISTS clinic_notifications;

-- appointment_requests depends on: clinic_users, clinics
DROP TABLE IF EXISTS appointment_requests;

-- clinic_call_logs depends on: clinics
DROP TABLE IF EXISTS clinic_call_logs;

-- audit_log depends on: clinics (ON DELETE SET NULL — safe to drop after clinics)
DROP TABLE IF EXISTS audit_log;

-- clinic_calendar_sync_events depends on: clinic_calendar_connections, clinics
DROP TABLE IF EXISTS clinic_calendar_sync_events;

-- clinic_calendar_blocks depends on: clinic_calendar_connections, clinics
DROP TABLE IF EXISTS clinic_calendar_blocks;

-- clinic_calendar_connections depends on: clinics
DROP TABLE IF EXISTS clinic_calendar_connections;

-- clinic_users depends on: clinics
DROP TABLE IF EXISTS clinic_users;

-- clinics is the root tenant table — dropped last
DROP TABLE IF EXISTS clinics;
""")
