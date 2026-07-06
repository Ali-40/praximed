'use client'

// PraxisMed — Tenant Language Settings Admin UI
// Sprint 19 / Module 139 — Admin-triggered language settings read/update.
//
// Protected: requires admin session cookie. Uses GET/PATCH /clinics/{id}/language-settings.
// Dark developer-console theme. No PHI. No secrets. No Vapi credentials.
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

const selectStyle = {
  width: '100%',
  padding: '0.5rem 0.75rem',
  borderRadius: 7,
  border: `1px solid ${EDGE}`,
  background: 'rgba(255,255,255,0.06)',
  color: TEXT,
  fontSize: '0.8125rem',
  fontFamily: 'ui-monospace, monospace',
} as const

const labelStyle = {
  display: 'block',
  fontSize: '0.7rem',
  fontWeight: 700,
  color: MUTED,
  letterSpacing: '0.05em',
  textTransform: 'uppercase',
  marginBottom: '0.3rem',
} as const

const helperStyle = {
  fontSize: '0.75rem',
  color: MUTED,
  marginTop: '0.25rem',
} as const

type LoadState = 'idle' | 'loading' | 'loaded' | 'auth_error' | 'not_found' | 'error'
type SaveState = 'idle' | 'saving' | 'saved' | 'error'

interface LanguageSettings {
  ok: boolean
  clinic_id: string
  primary_language: string
  fallback_language: string
  supported_languages: string[]
  default_patient_language: string
  vapi_assistant_language_mode: string
  clinic_ui_language: string
  updated_at: string | null
}

export default function TenantLanguageSettingsPage() {
  const [clinicId, setClinicId]         = useState('')
  const [loadState, setLoadState]       = useState<LoadState>('idle')
  const [settings, setSettings]         = useState<LanguageSettings | null>(null)
  const [loadError, setLoadError]       = useState<string | null>(null)
  const [saveState, setSaveState]       = useState<SaveState>('idle')
  const [saveError, setSaveError]       = useState<string | null>(null)

  // Form state — mirrors current settings, defaulting German-first
  const [primaryLanguage, setPrimaryLanguage]                 = useState('de')
  const [fallbackLanguage, setFallbackLanguage]               = useState('en')
  const [supportedLanguages, setSupportedLanguages]           = useState<string[]>(['de', 'en'])
  const [defaultPatientLanguage, setDefaultPatientLanguage]   = useState('de')
  const [vapiMode, setVapiMode]                               = useState('german_first')
  const [clinicUiLanguage, setClinicUiLanguage]               = useState('de')

  function populateForm(s: LanguageSettings) {
    setPrimaryLanguage(s.primary_language ?? 'de')
    setFallbackLanguage(s.fallback_language ?? 'en')
    setSupportedLanguages(
      Array.isArray(s.supported_languages) ? s.supported_languages : ['de', 'en']
    )
    setDefaultPatientLanguage(s.default_patient_language ?? 'de')
    setVapiMode(s.vapi_assistant_language_mode ?? 'german_first')
    setClinicUiLanguage(s.clinic_ui_language ?? 'de')
  }

  async function handleLoad() {
    const id = clinicId.trim()
    if (!id) return
    setLoadState('loading')
    setLoadError(null)
    setSaveState('idle')
    setSaveError(null)
    try {
      const resp = await fetch(
        `${API_BASE_URL}/clinics/${encodeURIComponent(id)}/language-settings`,
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
        setLoadError('Could not load language settings.')
        setLoadState('error')
        return
      }
      const data = await resp.json() as LanguageSettings
      setSettings(data)
      populateForm(data)
      setLoadState('loaded')
    } catch {
      setLoadError('Could not load language settings.')
      setLoadState('error')
    }
  }

  async function handleSave() {
    const id = clinicId.trim()
    if (!id) return
    setSaveState('saving')
    setSaveError(null)
    try {
      const payload = {
        primary_language:             primaryLanguage,
        fallback_language:            fallbackLanguage,
        supported_languages:          supportedLanguages,
        default_patient_language:     defaultPatientLanguage,
        vapi_assistant_language_mode: vapiMode,
        clinic_ui_language:           clinicUiLanguage,
      }
      const resp = await fetch(
        `${API_BASE_URL}/clinics/${encodeURIComponent(id)}/language-settings`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload),
        },
      )
      if (resp.status === 401 || resp.status === 403) {
        setSaveError('Admin session required.')
        setSaveState('error')
        return
      }
      if (resp.status === 400) {
        setSaveError('Unsupported language configuration.')
        setSaveState('error')
        return
      }
      if (!resp.ok) {
        setSaveError('Could not save language settings.')
        setSaveState('error')
        return
      }
      const data = await resp.json() as LanguageSettings
      setSettings(data)
      populateForm(data)
      setSaveState('saved')
    } catch {
      setSaveError('Could not save language settings.')
      setSaveState('error')
    }
  }

  function toggleSupported(lang: string) {
    setSupportedLanguages((prev) => {
      if (prev.includes(lang)) {
        if (prev.length <= 1) return prev   // must not allow empty selection
        return prev.filter((l) => l !== lang)
      }
      return [...prev, lang]
    })
  }

  const canLoad = clinicId.trim().length > 0 && loadState !== 'loading'
  const canSave = loadState === 'loaded' && saveState !== 'saving'

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
      <div style={{ width: '100%', maxWidth: 760 }}>

        {/* Header */}
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.625rem' }}>
            <h1 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.01em' }}>
              Tenant Language Settings
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
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.5rem' }}>
            Internal clinic configuration — configure language settings for provisioned clinic shells.
          </p>

          {/* Safety warning */}
          <div
            style={{
              padding: '0.75rem 1rem', borderRadius: 9,
              background: 'rgba(230,57,70,0.10)', border: `1px solid ${DANGER}`,
              fontSize: '0.775rem', color: '#F7A6AC', lineHeight: 1.6,
            }}
          >
            <strong style={{ color: '#FFCDD1' }}>No PHI.</strong>{' '}
            <strong style={{ color: '#FFCDD1' }}>No secrets.</strong>{' '}
            <strong style={{ color: '#FFCDD1' }}>No Vapi credentials.</strong>{' '}
            Language settings do not enable production PHI, Vapi credentials, or patient-data processing.{' '}
            <strong style={{ color: '#FFCDD1' }}>Production PHI remains NO-GO.</strong>
          </div>
        </div>

        {/* Clinic ID panel */}
        <div
          style={{
            background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12,
            overflow: 'hidden', marginBottom: '1.25rem',
          }}
        >
          <div style={{ padding: '0.875rem 1.25rem', borderBottom: `1px solid ${EDGE}` }}>
            <span style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT }}>Clinic ID</span>
          </div>
          <div style={{ padding: '1rem 1.25rem' }}>
            <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.75rem' }}>
              Paste a provisioned clinic_id from tenant provisioning smoke evidence.
            </p>
            <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap', alignItems: 'flex-start' }}>
              <input
                type="text"
                value={clinicId}
                onChange={(e) => {
                  setClinicId(e.target.value)
                  setLoadState('idle')
                  setSettings(null)
                  setSaveState('idle')
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
                {loadState === 'loading' ? 'Loading…' : 'Load settings'}
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
          </div>
        </div>

        {/* Language settings form — only visible when loaded */}
        {loadState === 'loaded' && settings && (
          <div
            style={{
              background: PANEL, border: `1px solid ${EDGE}`, borderRadius: 12,
              overflow: 'hidden', marginBottom: '1.25rem',
            }}
          >
            <div
              style={{
                padding: '0.875rem 1.25rem', borderBottom: `1px solid ${EDGE}`,
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              }}
            >
              <span style={{ fontSize: '0.875rem', fontWeight: 700, color: TEXT }}>Language Settings</span>
              {settings.updated_at && (
                <span style={{ fontSize: '0.75rem', color: MUTED }}>
                  Updated: {settings.updated_at}
                </span>
              )}
            </div>
            <div style={{ padding: '1rem 1.25rem' }}>

              {/* Primary language */}
              <div style={{ marginBottom: '1rem' }}>
                <label style={labelStyle}>Primary language</label>
                <select value={primaryLanguage} onChange={(e) => setPrimaryLanguage(e.target.value)} style={selectStyle}>
                  <option value="de">de — Deutsch</option>
                  <option value="en">en — English</option>
                </select>
                <p style={helperStyle}>German-first is recommended for Austrian Wahlärzte.</p>
              </div>

              {/* Fallback language */}
              <div style={{ marginBottom: '1rem' }}>
                <label style={labelStyle}>Fallback language</label>
                <select value={fallbackLanguage} onChange={(e) => setFallbackLanguage(e.target.value)} style={selectStyle}>
                  <option value="en">en — English</option>
                  <option value="de">de — Deutsch</option>
                </select>
              </div>

              {/* Supported languages */}
              <div style={{ marginBottom: '1rem' }}>
                <label style={labelStyle}>Supported languages</label>
                <div style={{ display: 'flex', gap: '1.25rem', padding: '0.375rem 0' }}>
                  {([['de', 'Deutsch'], ['en', 'English']] as const).map(([code, label]) => (
                    <label
                      key={code}
                      style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: TEXT, cursor: 'pointer' }}
                    >
                      <input
                        type="checkbox"
                        checked={supportedLanguages.includes(code)}
                        onChange={() => toggleSupported(code)}
                      />
                      {label}
                    </label>
                  ))}
                </div>
              </div>

              {/* Default patient language */}
              <div style={{ marginBottom: '1rem' }}>
                <label style={labelStyle}>Default patient language</label>
                <select value={defaultPatientLanguage} onChange={(e) => setDefaultPatientLanguage(e.target.value)} style={selectStyle}>
                  <option value="de">de — Deutsch</option>
                  <option value="en">en — English</option>
                </select>
              </div>

              {/* Vapi assistant language mode */}
              <div style={{ marginBottom: '1rem' }}>
                <label style={labelStyle}>Vapi assistant language mode</label>
                <select value={vapiMode} onChange={(e) => setVapiMode(e.target.value)} style={selectStyle}>
                  <option value="german_first">german_first</option>
                  <option value="english_first">english_first</option>
                  <option value="bilingual_auto">bilingual_auto</option>
                </select>
                <p style={helperStyle}>
                  This controls future Vapi assistant configuration. It does not bind Vapi credentials yet.
                </p>
              </div>

              {/* Clinic UI language */}
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={labelStyle}>Clinic UI language</label>
                <select value={clinicUiLanguage} onChange={(e) => setClinicUiLanguage(e.target.value)} style={selectStyle}>
                  <option value="de">de — Deutsch</option>
                  <option value="en">en — English</option>
                </select>
              </div>

              {/* Safety copy */}
              <div
                style={{
                  padding: '0.625rem 0.875rem', borderRadius: 8,
                  background: 'rgba(255,183,3,0.08)', border: `1px solid rgba(255,183,3,0.35)`,
                  fontSize: '0.775rem', color: WARN, lineHeight: 1.55, marginBottom: '0.875rem',
                }}
              >
                Language settings only control clinic/UI/assistant defaults. No PHI is stored.
                No secrets are accepted. No Vapi credentials are bound.
                No production activation occurs.{' '}
                <strong style={{ color: '#FFD350' }}>Production PHI remains NO-GO.</strong>
              </div>

              {/* Save button */}
              <button
                onClick={handleSave}
                disabled={!canSave}
                style={{
                  padding: '0.5rem 1.25rem', borderRadius: 7,
                  border: `1px solid ${ACCENT}`, background: 'rgba(0,128,128,0.15)',
                  color: ACCENT, fontSize: '0.8125rem', fontWeight: 700,
                  cursor: canSave ? 'pointer' : 'not-allowed',
                  opacity: canSave ? 1 : 0.5,
                }}
              >
                {saveState === 'saving' ? 'Saving…' : 'Save language settings'}
              </button>

              {saveState === 'saved' && (
                <p style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: GREEN }}>
                  Language settings saved
                </p>
              )}
              {saveState === 'error' && saveError && (
                <p style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: DANGER }}>
                  {saveError}
                </p>
              )}
            </div>
          </div>
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
