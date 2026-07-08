'use client'

// PraxisMed — Admin Patient Intake Links Console
// Sprint 20 / Module 151 — Demo intake link creation and management.
//
// Protected: requires admin session cookie. Uses lib/api helpers.
// Demo tokens only. No real patient data. No PHI. No secrets.
// intake_url shown once after creation. token_prefix shown in list only.
// Production PHI remains NO-GO.

import { useState, useEffect } from 'react'
import {
  createPatientIntakeLink,
  fetchPatientIntakeLinks,
  fetchPatientIntakeSubmissions,
  revokePatientIntakeLink,
  PatientIntakeLink,
  PatientIntakeSubmission,
} from '../../../lib/api'

const INK    = '#0B132B'
const PANEL  = '#111C3D'
const EDGE   = 'rgba(255,255,255,0.10)'
const ACCENT = '#008080'
const DANGER = '#E63946'
const WARN   = '#FFB703'
const TEXT   = '#E6EAF2'
const MUTED  = '#93A0B8'
const GREEN  = '#4ADE80'

const labelStyle = {
  display: 'block',
  fontSize: '0.7rem',
  fontWeight: 700 as const,
  color: MUTED,
  letterSpacing: '0.05em',
  textTransform: 'uppercase' as const,
  marginBottom: '0.3rem',
}

const inputStyle = {
  width: '100%',
  padding: '0.5rem 0.75rem',
  borderRadius: 7,
  border: `1px solid ${EDGE}`,
  background: 'rgba(255,255,255,0.04)',
  color: TEXT,
  fontSize: '0.8125rem',
  fontFamily: 'ui-monospace, monospace',
  boxSizing: 'border-box' as const,
}

const LANGUAGES = ['de', 'en', 'ar'] as const
const PURPOSES = [
  'patient_history_collection',
  'phone_history_questions',
  'demo_seed',
] as const

type LoadState = 'idle' | 'loading' | 'loaded' | 'auth_error' | 'error'
type CreateState = 'idle' | 'submitting' | 'created' | 'error'
type RevokeState = Record<string, 'idle' | 'revoking' | 'revoked' | 'error'>

export default function IntakeLinksPage() {
  const [clinicId, setClinicId] = useState('')
  const [loadState, setLoadState] = useState<LoadState>('idle')
  const [links, setLinks] = useState<PatientIntakeLink[]>([])
  const [submissions, setSubmissions] = useState<PatientIntakeSubmission[]>([])
  const [loadError, setLoadError] = useState('')

  const [templateId, setTemplateId] = useState('')
  const [language, setLanguage] = useState<typeof LANGUAGES[number]>('de')
  const [purpose, setPurpose] = useState<typeof PURPOSES[number]>('patient_history_collection')
  const [expiresHours, setExpiresHours] = useState('72')
  const [patientId, setPatientId] = useState('')
  const [createState, setCreateState] = useState<CreateState>('idle')
  const [createdIntakeUrl, setCreatedIntakeUrl] = useState('')
  const [createError, setCreateError] = useState('')

  const [revokeState, setRevokeState] = useState<RevokeState>({})

  async function handleLoad() {
    if (!clinicId.trim()) return
    setLoadState('loading')
    setLoadError('')
    try {
      const [linksData, subsData] = await Promise.all([
        fetchPatientIntakeLinks(clinicId.trim()),
        fetchPatientIntakeSubmissions(clinicId.trim()),
      ])
      setLinks(linksData)
      setSubmissions(subsData)
      setLoadState('loaded')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      if (msg.includes('401') || msg.includes('403')) {
        setLoadError('Admin session required. Please log in first.')
        setLoadState('auth_error')
      } else {
        setLoadError('Could not load intake links.')
        setLoadState('error')
      }
    }
  }

  async function handleCreate() {
    if (!clinicId.trim() || !templateId.trim()) return
    setCreateState('submitting')
    setCreateError('')
    setCreatedIntakeUrl('')
    try {
      const hours = parseInt(expiresHours, 10) || 72
      const expiresAt = new Date(Date.now() + hours * 3600 * 1000).toISOString()
      const result = await createPatientIntakeLink(clinicId.trim(), {
        template_id: templateId.trim(),
        language,
        purpose,
        expires_at: expiresAt,
        patient_id: patientId.trim() || undefined,
        max_submissions: 1,
      })
      if (result.ok && result.intake_url) {
        setCreatedIntakeUrl(result.intake_url)
        setCreateState('created')
        await handleLoad()
      } else {
        setCreateError(result.message ?? 'Creation failed.')
        setCreateState('error')
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      setCreateError(msg || 'Creation failed.')
      setCreateState('error')
    }
  }

  async function handleRevoke(linkId: string) {
    setRevokeState((s) => ({ ...s, [linkId]: 'revoking' }))
    try {
      await revokePatientIntakeLink(linkId)
      setRevokeState((s) => ({ ...s, [linkId]: 'revoked' }))
      await handleLoad()
    } catch {
      setRevokeState((s) => ({ ...s, [linkId]: 'error' }))
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: INK, fontFamily: 'ui-monospace, monospace', padding: '1.5rem 1rem' }}>
      <div style={{ maxWidth: 780, margin: '0 auto' }}>

        {/* Header */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <h1 style={{ fontSize: '1.125rem', fontWeight: 700, color: TEXT }}>Patient Intake Links</h1>
            <span style={{ fontSize: '0.6875rem', fontWeight: 700, padding: '2px 9px', borderRadius: 99, background: 'rgba(255,183,3,0.15)', color: WARN, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              ADMIN / STAGING
            </span>
          </div>
          <div style={{ fontSize: '0.75rem', color: DANGER, fontWeight: 600, border: `1px solid ${DANGER}`, borderRadius: 6, padding: '0.4rem 0.75rem', display: 'inline-block' }}>
            Demo tokens only. No real patient data. No PHI. Production PHI remains NO-GO.
          </div>
        </div>

        {/* Clinic ID loader */}
        <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12, padding: '1.25rem', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT, marginBottom: '0.875rem' }}>Clinic</h3>
          <label style={labelStyle}>Clinic ID (UUID)</label>
          <div style={{ display: 'flex', gap: '0.625rem' }}>
            <input
              style={{ ...inputStyle, flex: 1 }}
              value={clinicId}
              onChange={(e) => setClinicId(e.target.value)}
              placeholder="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
            />
            <button
              onClick={handleLoad}
              disabled={loadState === 'loading'}
              style={{ padding: '0.5rem 1rem', borderRadius: 7, border: 'none', background: ACCENT, color: '#fff', fontWeight: 700, fontSize: '0.8125rem', cursor: 'pointer' }}
            >
              {loadState === 'loading' ? 'Loading…' : 'Load'}
            </button>
          </div>
          {loadError && <p style={{ color: DANGER, fontSize: '0.75rem', marginTop: '0.5rem' }}>{loadError}</p>}
        </div>

        {/* Create link */}
        <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12, padding: '1.25rem', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT, marginBottom: '0.875rem' }}>Create Demo Intake Link</h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
            <div>
              <label style={labelStyle}>Template ID (UUID)</label>
              <input style={inputStyle} value={templateId} onChange={(e) => setTemplateId(e.target.value)} placeholder="bbbbbbbb-bbbb-4bbb-…" />
            </div>
            <div>
              <label style={labelStyle}>Language</label>
              <select style={inputStyle} value={language} onChange={(e) => setLanguage(e.target.value as typeof LANGUAGES[number])}>
                {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Purpose</label>
              <select style={inputStyle} value={purpose} onChange={(e) => setPurpose(e.target.value as typeof PURPOSES[number])}>
                {PURPOSES.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Expires in (hours)</label>
              <input style={inputStyle} type="number" min="1" value={expiresHours} onChange={(e) => setExpiresHours(e.target.value)} />
            </div>
            <div style={{ gridColumn: 'span 2' }}>
              <label style={labelStyle}>Patient ID (UUID, optional)</label>
              <input style={inputStyle} value={patientId} onChange={(e) => setPatientId(e.target.value)} placeholder="optional — leave blank for anonymous" />
            </div>
          </div>

          <button
            onClick={handleCreate}
            disabled={createState === 'submitting' || !clinicId.trim() || !templateId.trim()}
            style={{ padding: '0.5rem 1.25rem', borderRadius: 7, border: 'none', background: ACCENT, color: '#fff', fontWeight: 700, fontSize: '0.8125rem', cursor: 'pointer' }}
          >
            {createState === 'submitting' ? 'Creating…' : 'Create intake link'}
          </button>

          {createState === 'created' && createdIntakeUrl && (
            <div style={{ marginTop: '0.875rem', background: 'rgba(74,222,128,0.08)', border: `1px solid ${GREEN}`, borderRadius: 8, padding: '0.75rem 1rem' }}>
              <p style={{ fontSize: '0.7rem', fontWeight: 700, color: GREEN, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                Generated intake URL — shown once only
              </p>
              <code style={{ fontSize: '0.8125rem', color: GREEN, wordBreak: 'break-all' }}>
                {createdIntakeUrl}
              </code>
            </div>
          )}

          {createError && (
            <p style={{ color: DANGER, fontSize: '0.75rem', marginTop: '0.5rem' }}>{createError}</p>
          )}
        </div>

        {/* Links list */}
        {loadState === 'loaded' && (
          <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12, padding: '1.25rem', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT, marginBottom: '0.875rem' }}>
              Intake Links ({links.length})
            </h3>

            {links.length === 0 ? (
              <p style={{ color: MUTED, fontSize: '0.8125rem' }}>No intake links found for this clinic.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
                {links.map((link) => (
                  <div key={link.id} style={{ border: `1px solid ${EDGE}`, borderRadius: 8, padding: '0.875rem 1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <div>
                        <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: link.status === 'active' ? GREEN : MUTED, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                          {link.status}
                        </span>
                        {' · '}
                        <span style={{ fontSize: '0.75rem', color: MUTED }}>prefix: <code style={{ color: TEXT }}>{link.token_prefix}</code></span>
                      </div>
                      {link.status === 'active' && (
                        <button
                          onClick={() => handleRevoke(link.id)}
                          disabled={revokeState[link.id] === 'revoking'}
                          style={{ padding: '0.25rem 0.625rem', borderRadius: 5, border: `1px solid ${DANGER}`, background: 'transparent', color: DANGER, fontSize: '0.7rem', fontWeight: 700, cursor: 'pointer' }}
                        >
                          {revokeState[link.id] === 'revoking' ? 'Revoking…' : 'Revoke'}
                        </button>
                      )}
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.25rem 1rem', fontSize: '0.75rem', color: MUTED }}>
                      <span>lang: <code style={{ color: TEXT }}>{link.language}</code></span>
                      <span>purpose: <code style={{ color: TEXT }}>{link.purpose}</code></span>
                      <span>submissions: <code style={{ color: TEXT }}>{link.submission_count}/{link.max_submissions}</code></span>
                      <span>expires: <code style={{ color: TEXT }}>{new Date(link.expires_at).toLocaleString()}</code></span>
                    </div>
                    <div style={{ fontSize: '0.7rem', color: MUTED, marginTop: '0.375rem' }}>
                      production_phi_enabled: <code style={{ color: TEXT }}>false</code>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Submissions list */}
        {loadState === 'loaded' && (
          <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12, padding: '1.25rem', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT, marginBottom: '0.875rem' }}>
              Intake Submissions ({submissions.length})
            </h3>

            {submissions.length === 0 ? (
              <p style={{ color: MUTED, fontSize: '0.8125rem' }}>No submissions found for this clinic.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
                {submissions.map((sub) => (
                  <div key={sub.id} style={{ border: `1px solid ${EDGE}`, borderRadius: 8, padding: '0.875rem 1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem' }}>
                      <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: GREEN, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                        {sub.status}
                      </span>
                      <span style={{ fontSize: '0.7rem', color: MUTED }}>{new Date(sub.submitted_at).toLocaleString()}</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.25rem 1rem', fontSize: '0.75rem', color: MUTED }}>
                      <span>lang: <code style={{ color: TEXT }}>{sub.language}</code></span>
                      <span>escalation flags: <code style={{ color: sub.escalation_matches?.length > 0 ? WARN : TEXT }}>{sub.escalation_matches?.length ?? 0}</code></span>
                    </div>
                    <div style={{ fontSize: '0.7rem', color: MUTED, marginTop: '0.375rem' }}>
                      production_phi_enabled: <code style={{ color: TEXT }}>false</code>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Safety boundary */}
        <div style={{ background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12, padding: '1rem 1.25rem', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT, marginBottom: '0.5rem' }}>Safety Boundary</h3>
          {[
            'Demo tokens only — no live patient intake.',
            'Generated intake_url shown once only — not stored after creation.',
            'token_prefix displayed for admin identification only — no raw token.',
            'No real patient data. No PHI. No diagnosis. No medical advice.',
            'No patient history writes in this module.',
            'No AI structuring in this module.',
            'production_phi_enabled is always false.',
            'Production PHI remains NO-GO.',
          ].map((line, i, arr) => (
            <div key={i} style={{ display: 'flex', gap: '0.5rem', padding: '0.375rem 0', borderBottom: i < arr.length - 1 ? `1px solid ${EDGE}` : 'none', fontSize: '0.75rem', color: TEXT }}>
              <span style={{ color: DANGER, fontWeight: 700, flexShrink: 0 }}>!</span>
              <span>{line}</span>
            </div>
          ))}
        </div>

        <div style={{ textAlign: 'center' }}>
          <a href="/developer-console" style={{ fontSize: '0.8125rem', color: MUTED, textDecoration: 'none' }}>
            ← Back to developer console
          </a>
        </div>
      </div>
    </div>
  )
}
