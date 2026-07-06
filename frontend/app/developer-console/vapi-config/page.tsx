'use client'

// PraxisMed — Admin Vapi Assistant Config Preview UI
// Sprint 19 / Module 142 — Read-only preview of the generated Vapi assistant config pack.
//
// Protected: requires admin session cookie. Uses GET /clinics/{id}/vapi-assistant-config-pack.
// Dark developer-console theme. No PHI. No secrets. No Vapi credentials. No live Vapi binding.
// Production PHI remains NO-GO.

import { useState } from 'react'
import { API_BASE_URL } from '../../../lib/api'

const INK    = '#0B132B'
const PANEL  = '#111C3D'
const EDGE   = 'rgba(255,255,255,0.10)'
const ACCENT = '#008080'
const DANGER = '#E63946'
const WARN   = '#FFB703'
const TEXT   = '#E6EAF2'
const MUTED  = '#93A0B8'
const GREEN  = '#4ADE80'

const monoStyle = {
  fontFamily: 'ui-monospace, monospace',
  fontSize: '0.8125rem',
  color: TEXT,
} as const

const labelStyle = {
  display: 'block',
  fontSize: '0.7rem',
  fontWeight: 700 as const,
  color: MUTED,
  letterSpacing: '0.05em',
  textTransform: 'uppercase' as const,
  marginBottom: '0.25rem',
}

const sectionTitleStyle = {
  fontSize: '0.8125rem',
  fontWeight: 700 as const,
  color: TEXT,
  marginBottom: '0.75rem',
  paddingBottom: '0.375rem',
  borderBottom: `1px solid ${EDGE}`,
}

const fieldRowStyle = {
  display: 'flex',
  gap: '0.5rem',
  alignItems: 'flex-start',
  padding: '0.375rem 0',
  borderBottom: `1px solid rgba(255,255,255,0.05)`,
  fontSize: '0.8125rem',
}

const preStyle = {
  background: 'rgba(0,0,0,0.3)',
  border: `1px solid ${EDGE}`,
  borderRadius: 7,
  padding: '0.75rem 1rem',
  fontSize: '0.75rem',
  color: TEXT,
  fontFamily: 'ui-monospace, monospace',
  whiteSpace: 'pre-wrap' as const,
  wordBreak: 'break-word' as const,
  lineHeight: 1.6,
  overflowX: 'auto' as const,
} as const

type LoadState = 'idle' | 'loading' | 'loaded' | 'auth_error' | 'not_found' | 'error'

interface VapiConfigPack {
  clinic_id: string
  clinic_display_name: string
  specialty: string
  city: string
  primary_language: string
  fallback_language: string
  supported_languages: string[]
  vapi_assistant_language_mode: string
  assistant_name: string
  voice_locale_recommendation: string
  first_message_de: string
  first_message_en: string
  system_prompt_de: string
  system_prompt_en: string
  tool_schema: Record<string, unknown>
  required_capture_fields: string[]
  safety_rules: string[]
  escalation_rules: string[]
  forbidden_claims: string[]
  production_phi_enabled: boolean
  recording_ingestion_enabled: boolean
  transcript_ingestion_enabled: boolean
  generated_at: string | null
}

function SectionPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        background: PANEL,
        border: `1px solid ${EDGE}`,
        borderRadius: 12,
        overflow: 'hidden',
        marginBottom: '1.25rem',
      }}
    >
      <div style={{ padding: '0.75rem 1.25rem', borderBottom: `1px solid ${EDGE}` }}>
        <span style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT }}>{title}</span>
      </div>
      <div style={{ padding: '1rem 1.25rem' }}>{children}</div>
    </div>
  )
}

function FieldRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div style={fieldRowStyle}>
      <span style={{ ...monoStyle, color: MUTED, flexShrink: 0, width: '220px', fontSize: '0.75rem' }}>{label}</span>
      <span style={monoStyle}>{value}</span>
    </div>
  )
}

function FlagRow({ label, value }: { label: string; value: boolean }) {
  return (
    <div style={fieldRowStyle}>
      <span style={{ ...monoStyle, color: MUTED, flexShrink: 0, width: '260px', fontSize: '0.75rem' }}>{label}</span>
      <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: '0.8125rem', color: value ? DANGER : GREEN, fontWeight: 700 }}>
        {String(value)}
      </span>
    </div>
  )
}

export default function VapiAssistantConfigPreviewPage() {
  const [clinicId, setClinicId]   = useState('')
  const [loadState, setLoadState] = useState<LoadState>('idle')
  const [config, setConfig]       = useState<VapiConfigPack | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  async function handleLoad() {
    const id = clinicId.trim()
    if (!id) return
    setLoadState('loading')
    setLoadError(null)
    setConfig(null)
    try {
      const resp = await fetch(
        `${API_BASE_URL}/clinics/${encodeURIComponent(id)}/vapi-assistant-config-pack`,
        { credentials: 'include' },
      )
      if (resp.status === 401 || resp.status === 403) {
        setLoadError('Admin session required. Please log in first.')
        setLoadState('auth_error')
        return
      }
      if (resp.status === 404) {
        setLoadError('Clinic not found or no access.')
        setLoadState('not_found')
        return
      }
      if (!resp.ok) {
        setLoadError('Could not load Vapi assistant config.')
        setLoadState('error')
        return
      }
      const data = await resp.json() as VapiConfigPack
      setConfig(data)
      setLoadState('loaded')
    } catch {
      setLoadError('Could not load Vapi assistant config.')
      setLoadState('error')
    }
  }

  const canLoad = clinicId.trim().length > 0 && loadState !== 'loading'

  return (
    <div
      style={{
        minHeight: '100vh',
        background: INK,
        color: TEXT,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '3rem 1.5rem',
        fontFamily: 'Inter, system-ui, sans-serif',
      }}
    >
      <div style={{ width: '100%', maxWidth: 800 }}>

        {/* Header */}
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
            <h1 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.01em' }}>
              Vapi Assistant Config Preview
            </h1>
            <span
              style={{
                fontSize: '0.6875rem', fontWeight: 700, padding: '2px 10px', borderRadius: 99,
                background: WARN, color: INK, letterSpacing: '0.05em', textTransform: 'uppercase',
              }}
            >
              ADMIN / STAGING
            </span>
          </div>
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.625rem' }}>
            Read-only tenant assistant configuration — preview the generated Vapi assistant config pack per clinic.
          </p>

          {/* Safety warning */}
          <div
            style={{
              padding: '0.75rem 1rem', borderRadius: 9,
              background: 'rgba(230,57,70,0.10)', border: `1px solid ${DANGER}`,
              fontSize: '0.775rem', color: '#F7A6AC', lineHeight: 1.6,
            }}
          >
            <strong style={{ color: '#FFCDD1' }}>Preview only. No Vapi credentials are stored or transmitted.</strong>{' '}
            No PHI. No secrets. No live Vapi binding. No production activation.{' '}
            <strong style={{ color: '#FFCDD1' }}>Production PHI remains NO-GO.</strong>
          </div>
        </div>

        {/* Clinic ID input */}
        <SectionPanel title="Clinic ID">
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.75rem' }}>
            Paste a provisioned clinic_id or the staging clinic_id.
          </p>
          <p style={{ fontSize: '0.75rem', color: MUTED, marginBottom: '0.75rem', fontFamily: 'ui-monospace, monospace' }}>
            Example (staging): <span style={{ color: '#7FD4D4' }}>1a5bbc75-c1b0-4488-94aa-64b3f1c50056</span>
          </p>
          <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap', alignItems: 'flex-start' }}>
            <input
              type="text"
              value={clinicId}
              onChange={(e) => {
                setClinicId(e.target.value)
                setLoadState('idle')
                setConfig(null)
                setLoadError(null)
              }}
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              style={{
                flex: '1 1 320px',
                padding: '0.5rem 0.75rem',
                borderRadius: 7,
                border: `1px solid ${EDGE}`,
                background: 'rgba(255,255,255,0.06)',
                color: TEXT,
                fontSize: '0.8125rem',
                fontFamily: 'ui-monospace, monospace',
              }}
            />
            <button
              onClick={handleLoad}
              disabled={!canLoad}
              style={{
                padding: '0.5rem 1.25rem', borderRadius: 7,
                border: `1px solid ${ACCENT}`, background: 'rgba(0,128,128,0.15)',
                color: ACCENT, fontSize: '0.8125rem', fontWeight: 700,
                cursor: canLoad ? 'pointer' : 'not-allowed',
                opacity: canLoad ? 1 : 0.5,
              }}
            >
              {loadState === 'loading' ? 'Loading…' : 'Load config pack'}
            </button>
          </div>

          {loadState === 'auth_error' && (
            <p style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: DANGER }}>
              Admin session required. Please log in first.
            </p>
          )}
          {loadState === 'not_found' && (
            <p style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: WARN }}>
              Clinic not found or no access.
            </p>
          )}
          {loadState === 'error' && loadError && (
            <p style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: WARN }}>
              {loadError}
            </p>
          )}
        </SectionPanel>

        {/* Config pack sections — only visible when loaded */}
        {loadState === 'loaded' && config && (
          <>
            {/* A. Clinic / Language */}
            <SectionPanel title="A — Clinic / Language">
              <div style={sectionTitleStyle}>Clinic identity and language configuration</div>
              <FieldRow label="clinic_id"                    value={config.clinic_id} />
              <FieldRow label="clinic_display_name"          value={config.clinic_display_name} />
              <FieldRow label="specialty"                    value={config.specialty} />
              <FieldRow label="city"                         value={config.city} />
              <FieldRow label="primary_language"             value={config.primary_language} />
              <FieldRow label="fallback_language"            value={config.fallback_language} />
              <FieldRow label="supported_languages"          value={config.supported_languages.join(', ')} />
              <FieldRow label="vapi_assistant_language_mode" value={config.vapi_assistant_language_mode} />
              <FieldRow label="assistant_name"               value={config.assistant_name} />
              <FieldRow label="voice_locale_recommendation"  value={config.voice_locale_recommendation} />
            </SectionPanel>

            {/* B. German Assistant Prompt */}
            <SectionPanel title="B — German-First Prompt">
              <div style={sectionTitleStyle}>German-first prompt — de-AT</div>
              <div style={{ marginBottom: '0.875rem' }}>
                <span style={labelStyle}>First message (German)</span>
                <pre style={preStyle}>{config.first_message_de}</pre>
              </div>
              <div>
                <span style={labelStyle}>System prompt (German)</span>
                <pre style={preStyle}>{config.system_prompt_de}</pre>
              </div>
            </SectionPanel>

            {/* C. English Fallback Prompt */}
            <SectionPanel title="C — English Fallback Prompt">
              <div style={sectionTitleStyle}>English fallback prompt — en-US</div>
              <div style={{ marginBottom: '0.875rem' }}>
                <span style={labelStyle}>First message (English)</span>
                <pre style={preStyle}>{config.first_message_en}</pre>
              </div>
              <div>
                <span style={labelStyle}>System prompt (English)</span>
                <pre style={preStyle}>{config.system_prompt_en}</pre>
              </div>
            </SectionPanel>

            {/* D. Required Capture Fields */}
            {/* Standard required fields: patient_name, phone, reason, preferred_time, language_preference, urgency_level */}
            <SectionPanel title="D — Required Capture Fields">
              <div style={sectionTitleStyle}>Fields the assistant must collect from the caller</div>
              {config.required_capture_fields.map((field, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '0.5rem',
                    padding: '0.375rem 0', borderBottom: `1px solid rgba(255,255,255,0.05)`,
                    fontSize: '0.8125rem',
                  }}
                >
                  <span style={{ color: ACCENT, flexShrink: 0 }}>→</span>
                  <span style={{ fontFamily: 'ui-monospace, monospace', color: TEXT }}>{field}</span>
                </div>
              ))}
            </SectionPanel>

            {/* E. Tool Schema */}
            <SectionPanel title="E — Tool Schema">
              <div style={sectionTitleStyle}>
                Appointment capture tool — POST /vapi/tools/capture-appointment-request
              </div>
              <p style={{ fontSize: '0.775rem', color: MUTED, marginBottom: '0.75rem' }}>
                Required header names (values are never shown):
                X-Vapi-Service-Name · X-Vapi-Clinic-Id · X-Vapi-Scopes
              </p>
              <span style={labelStyle}>Tool schema (JSON)</span>
              <pre style={preStyle}>{JSON.stringify(config.tool_schema, null, 2)}</pre>
            </SectionPanel>

            {/* F. Safety Rules */}
            <SectionPanel title="F — Safety Rules">
              <div style={sectionTitleStyle}>Enforced boundaries for the assistant</div>
              {config.safety_rules.map((rule, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex', gap: '0.5rem', alignItems: 'flex-start',
                    padding: '0.5rem 0', borderBottom: `1px solid rgba(255,255,255,0.05)`,
                    fontSize: '0.8125rem', color: TEXT, lineHeight: 1.5,
                  }}
                >
                  <span style={{ color: DANGER, flexShrink: 0, fontWeight: 700 }}>!</span>
                  <span>{rule}</span>
                </div>
              ))}
              {config.escalation_rules.length > 0 && (
                <>
                  <p style={{ fontSize: '0.75rem', fontWeight: 700, color: MUTED, marginTop: '0.75rem', marginBottom: '0.25rem', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                    Escalation rules
                  </p>
                  {config.escalation_rules.map((rule, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex', gap: '0.5rem', alignItems: 'flex-start',
                        padding: '0.375rem 0', borderBottom: `1px solid rgba(255,255,255,0.05)`,
                        fontSize: '0.8125rem', color: TEXT, lineHeight: 1.5,
                      }}
                    >
                      <span style={{ color: WARN, flexShrink: 0, fontWeight: 700 }}>⚠</span>
                      <span>{rule}</span>
                    </div>
                  ))}
                </>
              )}
            </SectionPanel>

            {/* G. Forbidden Claims */}
            <SectionPanel title="G — Forbidden Claims">
              <div style={sectionTitleStyle}>Claims the assistant must never make</div>
              {config.forbidden_claims.map((claim, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex', gap: '0.5rem', alignItems: 'flex-start',
                    padding: '0.375rem 0', borderBottom: `1px solid rgba(255,255,255,0.05)`,
                    fontSize: '0.8125rem', color: TEXT, lineHeight: 1.5,
                  }}
                >
                  <span style={{ color: DANGER, flexShrink: 0 }}>✗</span>
                  <span>{claim}</span>
                </div>
              ))}
            </SectionPanel>

            {/* H. Readiness Flags */}
            <SectionPanel title="H — Readiness Flags">
              <div style={sectionTitleStyle}>Safety and ingestion flags — all must be false before live Vapi binding</div>
              <FlagRow label="production_phi_enabled"      value={config.production_phi_enabled} />
              <FlagRow label="recording_ingestion_enabled" value={config.recording_ingestion_enabled} />
              <FlagRow label="transcript_ingestion_enabled" value={config.transcript_ingestion_enabled} />
              {config.generated_at && (
                <div style={{ ...fieldRowStyle, borderBottom: 'none' }}>
                  <span style={{ ...monoStyle, color: MUTED, flexShrink: 0, width: '260px', fontSize: '0.75rem' }}>generated_at</span>
                  <span style={monoStyle}>{config.generated_at}</span>
                </div>
              )}
              <div
                style={{
                  marginTop: '0.875rem',
                  padding: '0.625rem 0.875rem', borderRadius: 8,
                  background: 'rgba(255,183,3,0.08)', border: `1px solid rgba(255,183,3,0.35)`,
                  fontSize: '0.775rem', color: WARN, lineHeight: 1.55,
                }}
              >
                This is a read-only preview. No Vapi credentials are stored or transmitted.
                No live Vapi binding occurs. No PHI. No secrets.{' '}
                <strong style={{ color: '#FFD350' }}>Production PHI remains NO-GO.</strong>
              </div>
            </SectionPanel>
          </>
        )}

        {/* Nav */}
        <div style={{ marginTop: '2rem', display: 'flex', gap: '1.5rem', justifyContent: 'center' }}>
          <a href="/developer-console" style={{ fontSize: '0.8125rem', color: MUTED, textDecoration: 'none' }}>
            ← Developer Console
          </a>
          <a href="/dashboard" style={{ fontSize: '0.8125rem', color: MUTED, textDecoration: 'none' }}>
            ← Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}
