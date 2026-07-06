-- =============================================================================
-- PraxisMed — PostgreSQL Database Schema
-- Sprint 1 / Module 3
--
-- Design principles:
--   • Multi-tenant: every row is scoped to a clinic via clinic_id.
--   • UUID primary keys throughout (gen_random_uuid() requires pgcrypto or
--     Postgres ≥ 13 where it is built-in).
--   • Immutable audit trail: audit_log rows are never updated or deleted.
--   • All timestamps stored as TIMESTAMPTZ (UTC-normalised).
--   • Schema is idempotent: wrapped in a transaction; use IF NOT EXISTS so
--     re-running against an existing DB is safe during development.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- Enable the pgcrypto extension for gen_random_uuid() on Postgres < 13.
-- On Postgres ≥ 13 this is a no-op because gen_random_uuid() is built-in.
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- A) clinics
--    Root tenant table.  Every other table references this via clinic_id.
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- B) clinic_users
--    Staff / admin users belonging to a clinic.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clinic_users (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id     UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    email         TEXT        NOT NULL,
    full_name     TEXT        NOT NULL,
    role          TEXT        NOT NULL,
    status        TEXT        NOT NULL DEFAULT 'active',
    password_hash TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (clinic_id, email)
);

-- ---------------------------------------------------------------------------
-- C) clinic_calendar_connections
--    OAuth / API connections to external calendar providers (Google, Microsoft
--    Bookings, etc.).  One clinic may have multiple connections.
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- D) clinic_calendar_blocks
--    Busy periods the AI booking layer must respect.
--    Sources: calendar sync, manual entry, vacation uploads.
--    Vapi and WhatsApp check this table before proposing appointment slots.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clinic_calendar_blocks (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id        UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    connection_id    UUID        REFERENCES clinic_calendar_connections(id) ON DELETE SET NULL,
    external_event_id TEXT,
    title            TEXT,
    block_type       TEXT        NOT NULL,
    starts_at        TIMESTAMPTZ NOT NULL,
    ends_at          TIMESTAMPTZ NOT NULL,
    is_all_day       BOOLEAN     NOT NULL DEFAULT false,
    source           TEXT        NOT NULL DEFAULT 'calendar_sync',
    raw_payload      JSONB,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT clinic_calendar_blocks_ends_after_starts CHECK (ends_at > starts_at)
);

-- ---------------------------------------------------------------------------
-- E) clinic_calendar_sync_events
--    Append-only log of sync operations triggered by n8n or webhooks.
--    Consumed by the dashboard and by alerting pipelines.
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- F) audit_log
--    Immutable compliance trail.  Rows are never updated or deleted.
--    clinic_id may be NULL for system-level actions (before a clinic exists).
-- ---------------------------------------------------------------------------
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

-- =============================================================================
-- Indexes
-- =============================================================================

-- clinics
CREATE INDEX IF NOT EXISTS idx_clinics_slug
    ON clinics (slug);

CREATE INDEX IF NOT EXISTS idx_clinics_status
    ON clinics (status);

-- clinic_users
CREATE INDEX IF NOT EXISTS idx_clinic_users_clinic_id
    ON clinic_users (clinic_id);

-- clinic_calendar_connections
CREATE INDEX IF NOT EXISTS idx_clinic_calendar_connections_clinic_id
    ON clinic_calendar_connections (clinic_id);

-- clinic_calendar_blocks — composite index optimised for time-range availability
-- queries ("is there a block overlapping this slot for this clinic?")
CREATE INDEX IF NOT EXISTS idx_clinic_calendar_blocks_clinic_time
    ON clinic_calendar_blocks (clinic_id, starts_at, ends_at);

CREATE INDEX IF NOT EXISTS idx_clinic_calendar_blocks_clinic_type
    ON clinic_calendar_blocks (clinic_id, block_type);

-- clinic_calendar_sync_events
CREATE INDEX IF NOT EXISTS idx_clinic_calendar_sync_events_clinic_created
    ON clinic_calendar_sync_events (clinic_id, created_at);

-- audit_log
CREATE INDEX IF NOT EXISTS idx_audit_log_clinic_created
    ON audit_log (clinic_id, created_at);

-- ---------------------------------------------------------------------------
-- clinic_call_logs  (Module 13)
-- One row per inbound/outbound phone call handled by the Vapi voice agent.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS clinic_call_logs (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id           UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    provider            TEXT        NOT NULL DEFAULT 'vapi',
    external_call_id    TEXT        NOT NULL,
    caller_phone        TEXT,
    direction           TEXT        NOT NULL DEFAULT 'inbound',
    call_status         TEXT        NOT NULL,
    started_at          TIMESTAMPTZ,
    ended_at            TIMESTAMPTZ,
    duration_seconds    INTEGER,
    transcript_text     TEXT,
    summary             TEXT,
    action_required     BOOLEAN     NOT NULL DEFAULT false,
    urgency_level       TEXT        NOT NULL DEFAULT 'normal',
    raw_payload         JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
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

-- ---------------------------------------------------------------------------
-- G) appointment_requests  (Module 15)
--    Appointment requests captured by phone AI, WhatsApp, web forms, or
--    clinic staff.  Reviewed by clinic staff before confirmation.
-- ---------------------------------------------------------------------------

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
    -- patient_id added Module 121 / migration 0003 — links to the matched or
    -- created patient row. Nullable (pre-121 rows and staff entries without
    -- patient lookup have no linked patient). The patients table is defined later
    -- in this file and the FK is applied at runtime via migration 0003.
    patient_id          UUID,
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

-- Added Module 121 / migration 0003
CREATE INDEX IF NOT EXISTS idx_appointment_requests_clinic_patient
    ON appointment_requests (clinic_id, patient_id);

-- ---------------------------------------------------------------------------
-- H) clinic_notifications  (Module 19)
--    Internal notification records for alerting clinic staff about events
--    such as urgent calls, human handoffs, new appointment requests, etc.
-- ---------------------------------------------------------------------------

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

-- ---------------------------------------------------------------------------
-- I) patients  (Module 24)
--    Multi-tenant patient identity and contact data.
--    Stores only admin/identity/contact information — no clinical notes,
--    diagnosis, or consultation data (those belong in future tables).
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS patients (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id            UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    external_patient_id  TEXT,
    full_name            TEXT        NOT NULL,
    date_of_birth        DATE,
    phone                TEXT,
    email                TEXT,
    preferred_language   TEXT        NOT NULL DEFAULT 'de-AT',
    status               TEXT        NOT NULL DEFAULT 'active',
    notes                TEXT,
    raw_payload          JSONB,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
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

-- ---------------------------------------------------------------------------
-- J) consultation_sessions  (Module 27)
--    One row per patient consultation session.  Tracks the full lifecycle
--    from recording through transcription, AI summary draft, doctor review,
--    and final approval.  AI output stays in draft_summary until a doctor
--    promotes it to approved_summary.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS consultation_sessions (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id            UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id           UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_user_id       UUID        REFERENCES clinic_users(id) ON DELETE SET NULL,
    source               TEXT        NOT NULL DEFAULT 'manual',
    status               TEXT        NOT NULL DEFAULT 'created',
    title                TEXT,
    reason_for_visit     TEXT,
    audio_file_path      TEXT,
    transcript_text      TEXT,
    draft_summary        JSONB,
    approved_summary     JSONB,
    approval_status      TEXT        NOT NULL DEFAULT 'not_ready',
    approved_by_user_id  UUID        REFERENCES clinic_users(id) ON DELETE SET NULL,
    approved_at          TIMESTAMPTZ,
    rejected_reason      TEXT,
    raw_payload          JSONB,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
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

-- ---------------------------------------------------------------------------
-- N) clinic_onboarding_requests
--    Pilot/onboarding requests submitted by doctors or clinic staff.
--    Does NOT create a production tenant automatically.
--    Does NOT store patient PHI. production_phi_enabled defaults false.
-- ---------------------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_clinic_onboarding_requests_email
    ON clinic_onboarding_requests (contact_email);

CREATE INDEX IF NOT EXISTS idx_clinic_onboarding_requests_status
    ON clinic_onboarding_requests (status);

CREATE INDEX IF NOT EXISTS idx_clinic_onboarding_requests_created_at
    ON clinic_onboarding_requests (created_at);

CREATE INDEX IF NOT EXISTS idx_clinic_onboarding_requests_preferred_language
    ON clinic_onboarding_requests (preferred_language);

-- ---------------------------------------------------------------------------
-- clinic_vapi_bindings — Sprint 19 / Module 145
-- Stores Vapi binding metadata. Secret reference names only — no secret values.
-- No VAPI_API_KEY value. No VAPI_WEBHOOK_SECRET value. No PHI.
-- ---------------------------------------------------------------------------

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

CREATE INDEX IF NOT EXISTS idx_clinic_vapi_bindings_clinic_id
    ON clinic_vapi_bindings (clinic_id);

CREATE INDEX IF NOT EXISTS idx_clinic_vapi_bindings_status
    ON clinic_vapi_bindings (status);

CREATE INDEX IF NOT EXISTS idx_clinic_vapi_bindings_language_mode
    ON clinic_vapi_bindings (language_mode);

CREATE INDEX IF NOT EXISTS idx_clinic_vapi_bindings_created_at
    ON clinic_vapi_bindings (created_at);

COMMIT;
