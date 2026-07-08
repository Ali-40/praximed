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

-- ---------------------------------------------------------------------------
-- consent_events — Sprint 20 / Module 148
-- Consent ledger: records who consented, when, for what purpose/channel/language.
-- Append-only; revocation uses revoked_at marker, never deletion.
-- No real patient PHI stored here. production_phi_enabled always false.
-- Synthetic/fake staging only. Production PHI remains NO-GO.
-- ---------------------------------------------------------------------------

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
    metadata                JSONB       NOT NULL DEFAULT '{}'::jsonb,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT consent_events_production_phi_check CHECK (
        production_phi_enabled = false
    ),
    CONSTRAINT consent_events_channel_check CHECK (
        channel IN ('onboarding_form','intake_link','phone_call','staff_console','developer_console','import_demo')
    ),
    CONSTRAINT consent_events_language_check CHECK (
        language IN ('de','en','ar')
    ),
    CONSTRAINT consent_events_purpose_check CHECK (
        purpose IN ('appointment_intake','patient_history_collection','phone_history_questions','demo_seed','data_processing_acknowledgement')
    )
);

CREATE INDEX IF NOT EXISTS idx_consent_events_clinic_id
    ON consent_events (clinic_id);

CREATE INDEX IF NOT EXISTS idx_consent_events_patient_id
    ON consent_events (patient_id);

CREATE INDEX IF NOT EXISTS idx_consent_events_appointment_request_id
    ON consent_events (appointment_request_id);

CREATE INDEX IF NOT EXISTS idx_consent_events_purpose
    ON consent_events (purpose);

CREATE INDEX IF NOT EXISTS idx_consent_events_channel
    ON consent_events (channel);

CREATE INDEX IF NOT EXISTS idx_consent_events_language
    ON consent_events (language);

CREATE INDEX IF NOT EXISTS idx_consent_events_granted
    ON consent_events (granted);

CREATE INDEX IF NOT EXISTS idx_consent_events_created_at
    ON consent_events (created_at);

CREATE INDEX IF NOT EXISTS idx_consent_events_revoked_at
    ON consent_events (revoked_at);

-- ── FHIR-aligned patient history tables (Module 149) ─────────────────────────
-- All tables: tenant-scoped, patient-scoped, consent-linked, append-only/versioned.
-- production_phi_enabled always false (DB CHECK).
-- No DELETE. Staff/doctor review required (status=unverified default).
-- Synthetic/fake staging only. No real patient PHI.
-- No diagnosis generated. No medical advice. No triage scoring.
-- Production PHI remains NO-GO.

CREATE TABLE IF NOT EXISTS patient_history_allergies (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
    consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
    version_group_id        UUID        NOT NULL,
    version_number          INTEGER     NOT NULL DEFAULT 1,
    supersedes_entry_id     UUID,
    correction_reason       TEXT,
    status                  TEXT        NOT NULL DEFAULT 'unverified',
    source_type             TEXT        NOT NULL DEFAULT 'staff_console',
    source_ref              TEXT,
    entered_by_user_id      UUID,
    reviewed_by_user_id     UUID,
    reviewed_at             TIMESTAMPTZ,
    review_note             TEXT,
    effective_start_date    DATE,
    effective_end_date      DATE,
    notes                   TEXT,
    fhir_resource_type      TEXT        NOT NULL,
    fhir_payload            JSONB       NOT NULL DEFAULT '{}'::jsonb,
    metadata                JSONB       NOT NULL DEFAULT '{}'::jsonb,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    substance_text          TEXT        NOT NULL,
    reaction_text           TEXT,
    severity                TEXT,
    clinical_status         TEXT,
    verification_status     TEXT,
    category                TEXT,
    criticality             TEXT,
    onset_text              TEXT,
    CONSTRAINT patient_history_allergies_phi_check CHECK (production_phi_enabled = false),
    CONSTRAINT patient_history_allergies_status_check CHECK (status IN ('unverified','approved','rejected','superseded')),
    CONSTRAINT patient_history_allergies_source_type_check CHECK (source_type IN ('staff_console','intake_link','phone_call','ai_proposal','demo_seed','import_demo')),
    CONSTRAINT patient_history_allergies_version_check CHECK (version_number >= 1),
    UNIQUE (version_group_id, version_number)
);
CREATE INDEX IF NOT EXISTS idx_patient_history_allergies_clinic_id ON patient_history_allergies (clinic_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_allergies_patient_id ON patient_history_allergies (patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_allergies_consent_event_id ON patient_history_allergies (consent_event_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_allergies_status ON patient_history_allergies (status);
CREATE INDEX IF NOT EXISTS idx_patient_history_allergies_created_at ON patient_history_allergies (created_at);

CREATE TABLE IF NOT EXISTS patient_history_medications (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
    consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
    version_group_id        UUID        NOT NULL,
    version_number          INTEGER     NOT NULL DEFAULT 1,
    supersedes_entry_id     UUID,
    correction_reason       TEXT,
    status                  TEXT        NOT NULL DEFAULT 'unverified',
    source_type             TEXT        NOT NULL DEFAULT 'staff_console',
    source_ref              TEXT,
    entered_by_user_id      UUID,
    reviewed_by_user_id     UUID,
    reviewed_at             TIMESTAMPTZ,
    review_note             TEXT,
    effective_start_date    DATE,
    effective_end_date      DATE,
    notes                   TEXT,
    fhir_resource_type      TEXT        NOT NULL,
    fhir_payload            JSONB       NOT NULL DEFAULT '{}'::jsonb,
    metadata                JSONB       NOT NULL DEFAULT '{}'::jsonb,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    medication_text         TEXT        NOT NULL,
    dosage_text             TEXT,
    frequency_text          TEXT,
    route_text              TEXT,
    medication_status       TEXT,
    start_text              TEXT,
    end_text                TEXT,
    reason_text             TEXT,
    CONSTRAINT patient_history_medications_phi_check CHECK (production_phi_enabled = false),
    CONSTRAINT patient_history_medications_status_check CHECK (status IN ('unverified','approved','rejected','superseded')),
    CONSTRAINT patient_history_medications_source_type_check CHECK (source_type IN ('staff_console','intake_link','phone_call','ai_proposal','demo_seed','import_demo')),
    CONSTRAINT patient_history_medications_version_check CHECK (version_number >= 1),
    UNIQUE (version_group_id, version_number)
);
CREATE INDEX IF NOT EXISTS idx_patient_history_medications_clinic_id ON patient_history_medications (clinic_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_medications_patient_id ON patient_history_medications (patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_medications_consent_event_id ON patient_history_medications (consent_event_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_medications_status ON patient_history_medications (status);
CREATE INDEX IF NOT EXISTS idx_patient_history_medications_created_at ON patient_history_medications (created_at);

CREATE TABLE IF NOT EXISTS patient_history_conditions (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
    consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
    version_group_id        UUID        NOT NULL,
    version_number          INTEGER     NOT NULL DEFAULT 1,
    supersedes_entry_id     UUID,
    correction_reason       TEXT,
    status                  TEXT        NOT NULL DEFAULT 'unverified',
    source_type             TEXT        NOT NULL DEFAULT 'staff_console',
    source_ref              TEXT,
    entered_by_user_id      UUID,
    reviewed_by_user_id     UUID,
    reviewed_at             TIMESTAMPTZ,
    review_note             TEXT,
    effective_start_date    DATE,
    effective_end_date      DATE,
    notes                   TEXT,
    fhir_resource_type      TEXT        NOT NULL,
    fhir_payload            JSONB       NOT NULL DEFAULT '{}'::jsonb,
    metadata                JSONB       NOT NULL DEFAULT '{}'::jsonb,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    condition_text          TEXT        NOT NULL,
    clinical_status         TEXT,
    verification_status     TEXT,
    onset_text              TEXT,
    abatement_text          TEXT,
    body_site_text          TEXT,
    severity_text           TEXT,
    patient_reported        BOOLEAN     NOT NULL DEFAULT true,
    CONSTRAINT patient_history_conditions_phi_check CHECK (production_phi_enabled = false),
    CONSTRAINT patient_history_conditions_status_check CHECK (status IN ('unverified','approved','rejected','superseded')),
    CONSTRAINT patient_history_conditions_source_type_check CHECK (source_type IN ('staff_console','intake_link','phone_call','ai_proposal','demo_seed','import_demo')),
    CONSTRAINT patient_history_conditions_version_check CHECK (version_number >= 1),
    UNIQUE (version_group_id, version_number)
);
CREATE INDEX IF NOT EXISTS idx_patient_history_conditions_clinic_id ON patient_history_conditions (clinic_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_conditions_patient_id ON patient_history_conditions (patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_conditions_consent_event_id ON patient_history_conditions (consent_event_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_conditions_status ON patient_history_conditions (status);
CREATE INDEX IF NOT EXISTS idx_patient_history_conditions_created_at ON patient_history_conditions (created_at);

CREATE TABLE IF NOT EXISTS patient_history_procedures (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
    consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
    version_group_id        UUID        NOT NULL,
    version_number          INTEGER     NOT NULL DEFAULT 1,
    supersedes_entry_id     UUID,
    correction_reason       TEXT,
    status                  TEXT        NOT NULL DEFAULT 'unverified',
    source_type             TEXT        NOT NULL DEFAULT 'staff_console',
    source_ref              TEXT,
    entered_by_user_id      UUID,
    reviewed_by_user_id     UUID,
    reviewed_at             TIMESTAMPTZ,
    review_note             TEXT,
    effective_start_date    DATE,
    effective_end_date      DATE,
    notes                   TEXT,
    fhir_resource_type      TEXT        NOT NULL,
    fhir_payload            JSONB       NOT NULL DEFAULT '{}'::jsonb,
    metadata                JSONB       NOT NULL DEFAULT '{}'::jsonb,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    procedure_text          TEXT        NOT NULL,
    performed_text          TEXT,
    body_site_text          TEXT,
    outcome_text            TEXT,
    performer_text          TEXT,
    reason_text             TEXT,
    CONSTRAINT patient_history_procedures_phi_check CHECK (production_phi_enabled = false),
    CONSTRAINT patient_history_procedures_status_check CHECK (status IN ('unverified','approved','rejected','superseded')),
    CONSTRAINT patient_history_procedures_source_type_check CHECK (source_type IN ('staff_console','intake_link','phone_call','ai_proposal','demo_seed','import_demo')),
    CONSTRAINT patient_history_procedures_version_check CHECK (version_number >= 1),
    UNIQUE (version_group_id, version_number)
);
CREATE INDEX IF NOT EXISTS idx_patient_history_procedures_clinic_id ON patient_history_procedures (clinic_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_procedures_patient_id ON patient_history_procedures (patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_procedures_consent_event_id ON patient_history_procedures (consent_event_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_procedures_status ON patient_history_procedures (status);
CREATE INDEX IF NOT EXISTS idx_patient_history_procedures_created_at ON patient_history_procedures (created_at);

CREATE TABLE IF NOT EXISTS patient_history_immunizations (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
    consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
    version_group_id        UUID        NOT NULL,
    version_number          INTEGER     NOT NULL DEFAULT 1,
    supersedes_entry_id     UUID,
    correction_reason       TEXT,
    status                  TEXT        NOT NULL DEFAULT 'unverified',
    source_type             TEXT        NOT NULL DEFAULT 'staff_console',
    source_ref              TEXT,
    entered_by_user_id      UUID,
    reviewed_by_user_id     UUID,
    reviewed_at             TIMESTAMPTZ,
    review_note             TEXT,
    effective_start_date    DATE,
    effective_end_date      DATE,
    notes                   TEXT,
    fhir_resource_type      TEXT        NOT NULL,
    fhir_payload            JSONB       NOT NULL DEFAULT '{}'::jsonb,
    metadata                JSONB       NOT NULL DEFAULT '{}'::jsonb,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    vaccine_text            TEXT        NOT NULL,
    occurrence_text         TEXT,
    lot_number              TEXT,
    site_text               TEXT,
    route_text              TEXT,
    dose_number             TEXT,
    series_text             TEXT,
    immunization_status     TEXT,
    CONSTRAINT patient_history_immunizations_phi_check CHECK (production_phi_enabled = false),
    CONSTRAINT patient_history_immunizations_status_check CHECK (status IN ('unverified','approved','rejected','superseded')),
    CONSTRAINT patient_history_immunizations_source_type_check CHECK (source_type IN ('staff_console','intake_link','phone_call','ai_proposal','demo_seed','import_demo')),
    CONSTRAINT patient_history_immunizations_version_check CHECK (version_number >= 1),
    UNIQUE (version_group_id, version_number)
);
CREATE INDEX IF NOT EXISTS idx_patient_history_immunizations_clinic_id ON patient_history_immunizations (clinic_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_immunizations_patient_id ON patient_history_immunizations (patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_immunizations_consent_event_id ON patient_history_immunizations (consent_event_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_immunizations_status ON patient_history_immunizations (status);
CREATE INDEX IF NOT EXISTS idx_patient_history_immunizations_created_at ON patient_history_immunizations (created_at);

CREATE TABLE IF NOT EXISTS patient_history_family_history (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
    consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
    version_group_id        UUID        NOT NULL,
    version_number          INTEGER     NOT NULL DEFAULT 1,
    supersedes_entry_id     UUID,
    correction_reason       TEXT,
    status                  TEXT        NOT NULL DEFAULT 'unverified',
    source_type             TEXT        NOT NULL DEFAULT 'staff_console',
    source_ref              TEXT,
    entered_by_user_id      UUID,
    reviewed_by_user_id     UUID,
    reviewed_at             TIMESTAMPTZ,
    review_note             TEXT,
    effective_start_date    DATE,
    effective_end_date      DATE,
    notes                   TEXT,
    fhir_resource_type      TEXT        NOT NULL,
    fhir_payload            JSONB       NOT NULL DEFAULT '{}'::jsonb,
    metadata                JSONB       NOT NULL DEFAULT '{}'::jsonb,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    relationship_text       TEXT        NOT NULL,
    condition_text          TEXT,
    age_text                TEXT,
    deceased                BOOLEAN,
    note_text               TEXT,
    CONSTRAINT patient_history_family_history_phi_check CHECK (production_phi_enabled = false),
    CONSTRAINT patient_history_family_history_status_check CHECK (status IN ('unverified','approved','rejected','superseded')),
    CONSTRAINT patient_history_family_history_source_type_check CHECK (source_type IN ('staff_console','intake_link','phone_call','ai_proposal','demo_seed','import_demo')),
    CONSTRAINT patient_history_family_history_version_check CHECK (version_number >= 1),
    UNIQUE (version_group_id, version_number)
);
CREATE INDEX IF NOT EXISTS idx_patient_history_family_history_clinic_id ON patient_history_family_history (clinic_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_family_history_patient_id ON patient_history_family_history (patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_family_history_consent_event_id ON patient_history_family_history (consent_event_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_family_history_status ON patient_history_family_history (status);
CREATE INDEX IF NOT EXISTS idx_patient_history_family_history_created_at ON patient_history_family_history (created_at);

CREATE TABLE IF NOT EXISTS patient_history_social_history (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
    consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
    version_group_id        UUID        NOT NULL,
    version_number          INTEGER     NOT NULL DEFAULT 1,
    supersedes_entry_id     UUID,
    correction_reason       TEXT,
    status                  TEXT        NOT NULL DEFAULT 'unverified',
    source_type             TEXT        NOT NULL DEFAULT 'staff_console',
    source_ref              TEXT,
    entered_by_user_id      UUID,
    reviewed_by_user_id     UUID,
    reviewed_at             TIMESTAMPTZ,
    review_note             TEXT,
    effective_start_date    DATE,
    effective_end_date      DATE,
    notes                   TEXT,
    fhir_resource_type      TEXT        NOT NULL,
    fhir_payload            JSONB       NOT NULL DEFAULT '{}'::jsonb,
    metadata                JSONB       NOT NULL DEFAULT '{}'::jsonb,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    observation_category    TEXT        NOT NULL,
    observation_text        TEXT        NOT NULL,
    value_text              TEXT,
    period_text             TEXT,
    CONSTRAINT patient_history_social_history_phi_check CHECK (production_phi_enabled = false),
    CONSTRAINT patient_history_social_history_status_check CHECK (status IN ('unverified','approved','rejected','superseded')),
    CONSTRAINT patient_history_social_history_source_type_check CHECK (source_type IN ('staff_console','intake_link','phone_call','ai_proposal','demo_seed','import_demo')),
    CONSTRAINT patient_history_social_history_version_check CHECK (version_number >= 1),
    UNIQUE (version_group_id, version_number)
);
CREATE INDEX IF NOT EXISTS idx_patient_history_social_history_clinic_id ON patient_history_social_history (clinic_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_social_history_patient_id ON patient_history_social_history (patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_social_history_consent_event_id ON patient_history_social_history (consent_event_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_social_history_status ON patient_history_social_history (status);
CREATE INDEX IF NOT EXISTS idx_patient_history_social_history_created_at ON patient_history_social_history (created_at);

-- ─── Anamnesis Templates (Module 150) ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS anamnesis_templates (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        REFERENCES clinics(id) ON DELETE CASCADE,
    template_key            TEXT        NOT NULL,
    display_name            TEXT        NOT NULL,
    specialty               TEXT        NOT NULL,
    version                 INTEGER     NOT NULL DEFAULT 1,
    status                  TEXT        NOT NULL DEFAULT 'draft',
    primary_language        TEXT        NOT NULL DEFAULT 'de',
    supported_languages     JSONB       NOT NULL DEFAULT '["de","en"]'::jsonb,
    template_schema         JSONB       NOT NULL DEFAULT '{}'::jsonb,
    escalation_keywords     JSONB       NOT NULL DEFAULT '[]'::jsonb,
    consent_purpose         TEXT        NOT NULL DEFAULT 'patient_history_collection',
    synthetic_demo          BOOLEAN     NOT NULL DEFAULT true,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_by_user_id      UUID,
    updated_by_user_id      UUID,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT anamnesis_templates_phi_check     CHECK (production_phi_enabled = false),
    CONSTRAINT anamnesis_templates_status_check  CHECK (status IN ('draft','active','archived')),
    CONSTRAINT anamnesis_templates_language_check CHECK (primary_language IN ('de','en','ar')),
    CONSTRAINT anamnesis_templates_purpose_check CHECK (consent_purpose IN ('patient_history_collection','phone_history_questions','demo_seed')),
    CONSTRAINT anamnesis_templates_version_check CHECK (version >= 1)
);

CREATE INDEX IF NOT EXISTS idx_anamnesis_templates_clinic_id       ON anamnesis_templates (clinic_id);
CREATE INDEX IF NOT EXISTS idx_anamnesis_templates_template_key    ON anamnesis_templates (template_key);
CREATE INDEX IF NOT EXISTS idx_anamnesis_templates_specialty       ON anamnesis_templates (specialty);
CREATE INDEX IF NOT EXISTS idx_anamnesis_templates_status          ON anamnesis_templates (status);
CREATE INDEX IF NOT EXISTS idx_anamnesis_templates_primary_language ON anamnesis_templates (primary_language);
CREATE INDEX IF NOT EXISTS idx_anamnesis_templates_synthetic_demo  ON anamnesis_templates (synthetic_demo);
CREATE INDEX IF NOT EXISTS idx_anamnesis_templates_created_at      ON anamnesis_templates (created_at);

CREATE UNIQUE INDEX IF NOT EXISTS uidx_anamnesis_templates_global_key_version
    ON anamnesis_templates (template_key, version)
    WHERE clinic_id IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uidx_anamnesis_templates_clinic_key_version
    ON anamnesis_templates (clinic_id, template_key, version)
    WHERE clinic_id IS NOT NULL;

-- ─── Patient Intake Link Flow (Module 151) ────────────────────────────────────

CREATE TABLE IF NOT EXISTS patient_intake_links (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        REFERENCES patients(id) ON DELETE SET NULL,
    appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
    template_id             UUID        NOT NULL REFERENCES anamnesis_templates(id) ON DELETE RESTRICT,
    token_hash              TEXT        NOT NULL UNIQUE,
    token_prefix            TEXT        NOT NULL,
    status                  TEXT        NOT NULL DEFAULT 'active',
    purpose                 TEXT        NOT NULL DEFAULT 'patient_history_collection',
    language                TEXT        NOT NULL DEFAULT 'de',
    expires_at              TIMESTAMPTZ NOT NULL,
    max_submissions         INTEGER     NOT NULL DEFAULT 1,
    submission_count        INTEGER     NOT NULL DEFAULT 0,
    synthetic_demo          BOOLEAN     NOT NULL DEFAULT true,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    created_by_user_id      UUID,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT patient_intake_links_phi_check       CHECK (production_phi_enabled = false),
    CONSTRAINT patient_intake_links_demo_check      CHECK (synthetic_demo = true),
    CONSTRAINT patient_intake_links_status_check    CHECK (status IN ('active','submitted','expired','revoked')),
    CONSTRAINT patient_intake_links_purpose_check   CHECK (purpose IN ('patient_history_collection','phone_history_questions','demo_seed')),
    CONSTRAINT patient_intake_links_language_check  CHECK (language IN ('de','en','ar')),
    CONSTRAINT patient_intake_links_max_sub_check   CHECK (max_submissions >= 1),
    CONSTRAINT patient_intake_links_sub_count_check CHECK (submission_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_patient_intake_links_clinic_id              ON patient_intake_links (clinic_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_links_patient_id             ON patient_intake_links (patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_links_appointment_request_id ON patient_intake_links (appointment_request_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_links_template_id            ON patient_intake_links (template_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_links_status                 ON patient_intake_links (status);
CREATE INDEX IF NOT EXISTS idx_patient_intake_links_language               ON patient_intake_links (language);
CREATE INDEX IF NOT EXISTS idx_patient_intake_links_expires_at             ON patient_intake_links (expires_at);
CREATE INDEX IF NOT EXISTS idx_patient_intake_links_created_at             ON patient_intake_links (created_at);

CREATE TABLE IF NOT EXISTS patient_intake_submissions (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    intake_link_id          UUID        NOT NULL REFERENCES patient_intake_links(id) ON DELETE CASCADE,
    clinic_id               UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id              UUID        REFERENCES patients(id) ON DELETE SET NULL,
    appointment_request_id  UUID        REFERENCES appointment_requests(id) ON DELETE SET NULL,
    template_id             UUID        NOT NULL REFERENCES anamnesis_templates(id) ON DELETE RESTRICT,
    consent_event_id        UUID        NOT NULL REFERENCES consent_events(id) ON DELETE RESTRICT,
    language                TEXT        NOT NULL DEFAULT 'de',
    answers                 JSONB       NOT NULL DEFAULT '{}'::jsonb,
    skipped_questions       JSONB       NOT NULL DEFAULT '[]'::jsonb,
    escalation_matches      JSONB       NOT NULL DEFAULT '[]'::jsonb,
    status                  TEXT        NOT NULL DEFAULT 'submitted',
    synthetic_demo          BOOLEAN     NOT NULL DEFAULT true,
    production_phi_enabled  BOOLEAN     NOT NULL DEFAULT false,
    submitted_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT patient_intake_submissions_phi_check      CHECK (production_phi_enabled = false),
    CONSTRAINT patient_intake_submissions_demo_check     CHECK (synthetic_demo = true),
    CONSTRAINT patient_intake_submissions_status_check   CHECK (status IN ('submitted','review_pending','archived_demo')),
    CONSTRAINT patient_intake_submissions_language_check CHECK (language IN ('de','en','ar'))
);

CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_intake_link_id          ON patient_intake_submissions (intake_link_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_clinic_id               ON patient_intake_submissions (clinic_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_patient_id              ON patient_intake_submissions (patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_appointment_request_id  ON patient_intake_submissions (appointment_request_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_template_id             ON patient_intake_submissions (template_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_consent_event_id        ON patient_intake_submissions (consent_event_id);
CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_status                  ON patient_intake_submissions (status);
CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_language                ON patient_intake_submissions (language);
CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_submitted_at            ON patient_intake_submissions (submitted_at);
CREATE INDEX IF NOT EXISTS idx_patient_intake_submissions_created_at              ON patient_intake_submissions (created_at);

COMMIT;
