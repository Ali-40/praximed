'use client'

// PraxisMed — Clinic Pilot Access Request Form
// Sprint 19 / Module 133 — Connect Onboarding Frontend to Backend Request API
//
// Real controlled form submitting to POST /clinic-onboarding-requests.
// No patient data. No secrets. No automatic tenant creation. Production PHI: NO-GO.

import { useState } from 'react'
import { API_BASE_URL } from '../../lib/api'

const INK    = '#0B132B'
const ACCENT = '#008080'
const FILL   = '#E0F2F1'
const WARN   = '#FFB703'
const DANGER = '#E63946'
const CANVAS = '#F4F6F9'
const BORDER = '#E3E8EF'
const MUTED  = '#5B6472'

interface FormFields {
  clinic_name: string
  clinic_type: string
  specialty: string
  city: string
  address: string
  website: string
  doctor_name: string
  contact_email: string
  contact_phone: string
  preferred_language: 'de' | 'en'
  workflow_notes: string
  estimated_call_volume: string
  current_booking_system: string
  wants_ai_phone_intake: boolean
  wants_dashboard: boolean
  wants_notifications: boolean
  consent_pilot_contact: boolean
  acknowledges_no_phi: boolean
}

const DEFAULTS: FormFields = {
  clinic_name: '',
  clinic_type: '',
  specialty: '',
  city: 'Wien',
  address: '',
  website: '',
  doctor_name: '',
  contact_email: '',
  contact_phone: '',
  preferred_language: 'de',
  workflow_notes: '',
  estimated_call_volume: '',
  current_booking_system: '',
  wants_ai_phone_intake: true,
  wants_dashboard: true,
  wants_notifications: false,
  consent_pilot_contact: false,
  acknowledges_no_phi: false,
}

type SubmitState = 'idle' | 'submitting' | 'success' | 'error'

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.625rem 0.75rem',
  borderRadius: 8,
  border: `1px solid ${BORDER}`,
  fontSize: '0.875rem',
  color: INK,
  background: '#fff',
  boxSizing: 'border-box',
  outline: 'none',
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.8125rem',
  fontWeight: 600,
  color: INK,
  marginBottom: '0.375rem',
}

const fieldWrap: React.CSSProperties = { marginBottom: '0.875rem' }

const sectionCard: React.CSSProperties = {
  marginBottom: '1rem',
  padding: '1.25rem',
  borderRadius: 14,
  border: `1px solid ${BORDER}`,
  background: '#ffffff',
  boxShadow: '0 1px 2px 0 rgb(11 19 43 / 0.05)',
}

const sectionTitle: React.CSSProperties = {
  fontWeight: 700,
  fontSize: '0.9375rem',
  color: INK,
  marginBottom: '1rem',
  display: 'flex',
  alignItems: 'center',
  gap: '0.625rem',
}

const stepBadge = (n: number): React.CSSProperties => ({
  flexShrink: 0,
  width: 26,
  height: 26,
  borderRadius: '50%',
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '0.75rem',
  fontWeight: 700,
  background: ACCENT,
  color: '#ffffff',
})

export default function OnboardingPage() {
  const [form, setForm]               = useState<FormFields>(DEFAULTS)
  const [submitState, setSubmitState] = useState<SubmitState>('idle')
  const [requestId, setRequestId]     = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  function set<K extends keyof FormFields>(key: K, value: FormFields[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setSubmitState('submitting')
    setErrorMessage(null)

    const payload = {
      clinic_name:            form.clinic_name,
      clinic_type:            form.clinic_type   || undefined,
      specialty:              form.specialty      || undefined,
      city:                   form.city          || undefined,
      address:                form.address        || undefined,
      website:                form.website        || undefined,
      doctor_name:            form.doctor_name,
      contact_email:          form.contact_email,
      contact_phone:          form.contact_phone  || undefined,
      preferred_language:     form.preferred_language,
      fallback_language:      form.preferred_language === 'de' ? 'en' : 'de',
      supported_languages:    ['de', 'en'],
      workflow_notes:         form.workflow_notes         || undefined,
      estimated_call_volume:  form.estimated_call_volume  || undefined,
      current_booking_system: form.current_booking_system || undefined,
      wants_ai_phone_intake:  form.wants_ai_phone_intake,
      wants_dashboard:        form.wants_dashboard,
      wants_notifications:    form.wants_notifications,
      consent_pilot_contact:  form.consent_pilot_contact,
      acknowledges_no_phi:    form.acknowledges_no_phi,
    }

    try {
      const resp = await fetch(`${API_BASE_URL}/clinic-onboarding-requests`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      })

      if (resp.ok) {
        const data = await resp.json() as { ok: boolean; request?: { id?: string } }
        setRequestId(data?.request?.id ?? null)
        setSubmitState('success')
      } else {
        let msg = 'Your request could not be submitted. Please review your details and try again.'
        try {
          const errData = await resp.json() as { detail?: string | Array<{ msg: string }> }
          if (typeof errData.detail === 'string') {
            msg = errData.detail
          } else if (Array.isArray(errData.detail)) {
            msg = errData.detail.map((d) => d.msg).join(' ')
          }
        } catch { /* keep default */ }
        setErrorMessage(msg)
        setSubmitState('error')
      }
    } catch {
      setErrorMessage('A network error occurred. Please check your connection and try again.')
      setSubmitState('error')
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: CANVAS,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '3rem 1.5rem',
      }}
    >
      <div style={{ width: '100%', maxWidth: 680 }}>

        {/* ------------------------------------------------------------------ */}
        {/* Gateway header                                                       */}
        {/* ------------------------------------------------------------------ */}
        <div
          data-section="onboarding-gateway"
          style={{
            marginBottom: '2rem',
            borderRadius: 16,
            background: INK,
            padding: '2rem 1.75rem',
            textAlign: 'center',
            boxShadow: '0 4px 14px -4px rgb(11 19 43 / 0.35)',
          }}
        >
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.02em', marginBottom: '0.4rem' }}>
            Start with PraxisMed
          </h1>
          <p style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.65)', marginBottom: '1.25rem' }}>
            AI intake and workflow automation for Austrian private clinics
          </p>

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <a
              href="/login"
              style={{
                fontSize: '0.875rem', fontWeight: 700, padding: '0.65rem 1.5rem', borderRadius: 9,
                background: ACCENT, color: '#ffffff', textDecoration: 'none',
              }}
            >
              Existing Clinic Login
            </a>
            <button
              type="button"
              onClick={() => document.getElementById('pilot-form')?.scrollIntoView({ behavior: 'smooth' })}
              style={{
                fontSize: '0.875rem', fontWeight: 700, padding: '0.65rem 1.5rem', borderRadius: 9,
                background: 'transparent', color: 'rgba(255,255,255,0.9)',
                border: '1px solid rgba(255,255,255,0.45)', cursor: 'pointer',
              }}
            >
              Request Pilot Access Registration
            </button>
          </div>

          <div
            style={{
              display: 'inline-block',
              marginTop: '1.25rem',
              fontSize: '0.6875rem',
              fontWeight: 700,
              padding: '3px 12px',
              borderRadius: 99,
              background: WARN,
              color: INK,
              letterSpacing: '0.05em',
            }}
          >
            STAGING DEMO — FAKE DATA ONLY
          </div>
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* Success state                                                        */}
        {/* ------------------------------------------------------------------ */}
        {submitState === 'success' && (
          <div
            data-state="success"
            style={{
              marginBottom: '2rem',
              padding: '1.5rem',
              borderRadius: 14,
              border: `1.5px solid ${ACCENT}`,
              background: FILL,
              boxShadow: '0 1px 4px 0 rgb(0 128 128 / 0.12)',
            }}
          >
            <p style={{ fontWeight: 800, fontSize: '1.0625rem', color: ACCENT, marginBottom: '0.5rem' }}>
              Pilot request submitted
            </p>
            <p style={{ fontSize: '0.875rem', color: INK, marginBottom: '0.375rem' }}>
              PraxisMed will contact you at <strong>{form.contact_email}</strong>.
            </p>
            {requestId && (
              <p style={{ fontSize: '0.75rem', color: MUTED, marginBottom: '0.375rem' }}>
                Request ID: {requestId}
              </p>
            )}
            <p style={{ fontSize: '0.75rem', color: MUTED }}>
              No production PHI is activated. This is a pilot intake only.
            </p>
          </div>
        )}

        {/* ------------------------------------------------------------------ */}
        {/* Pilot request form                                                   */}
        {/* ------------------------------------------------------------------ */}
        {submitState !== 'success' && (
          <form id="pilot-form" onSubmit={handleSubmit} noValidate>

            {/* Step 1 — Clinic Details */}
            <div data-onboarding-step={1} style={sectionCard}>
              <p style={sectionTitle}>
                <span style={stepBadge(1)}>1</span>
                Clinic Details
              </p>
              <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '1rem' }}>
                Legal clinic name, address, specialty, and contact information.
              </p>

              <div style={fieldWrap}>
                <label htmlFor="clinic_name" style={labelStyle}>
                  Clinic name <span style={{ color: DANGER }}>*</span>
                </label>
                <input
                  id="clinic_name"
                  name="clinic_name"
                  type="text"
                  required
                  value={form.clinic_name}
                  onChange={(e) => set('clinic_name', e.target.value)}
                  placeholder="e.g. Wahlarztpraxis Wien"
                  style={inputStyle}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <div style={{ ...fieldWrap, flex: '1 1 200px' }}>
                  <label htmlFor="clinic_type" style={labelStyle}>Clinic type</label>
                  <input
                    id="clinic_type"
                    name="clinic_type"
                    type="text"
                    value={form.clinic_type}
                    onChange={(e) => set('clinic_type', e.target.value)}
                    placeholder="e.g. Wahlarzt, Kassenarzt"
                    style={inputStyle}
                  />
                </div>
                <div style={{ ...fieldWrap, flex: '1 1 200px' }}>
                  <label htmlFor="specialty" style={labelStyle}>Specialty</label>
                  <input
                    id="specialty"
                    name="specialty"
                    type="text"
                    value={form.specialty}
                    onChange={(e) => set('specialty', e.target.value)}
                    placeholder="e.g. Innere Medizin"
                    style={inputStyle}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <div style={{ ...fieldWrap, flex: '1 1 200px' }}>
                  <label htmlFor="city" style={labelStyle}>City</label>
                  <input
                    id="city"
                    name="city"
                    type="text"
                    value={form.city}
                    onChange={(e) => set('city', e.target.value)}
                    placeholder="Wien"
                    style={inputStyle}
                  />
                </div>
                <div style={{ ...fieldWrap, flex: '1 1 200px' }}>
                  <label htmlFor="address" style={labelStyle}>Address</label>
                  <input
                    id="address"
                    name="address"
                    type="text"
                    value={form.address}
                    onChange={(e) => set('address', e.target.value)}
                    placeholder="Street and number"
                    style={inputStyle}
                  />
                </div>
              </div>

              <div style={fieldWrap}>
                <label htmlFor="website" style={labelStyle}>Website</label>
                <input
                  id="website"
                  name="website"
                  type="url"
                  value={form.website}
                  onChange={(e) => set('website', e.target.value)}
                  placeholder="https://..."
                  style={inputStyle}
                />
              </div>
            </div>

            {/* Step 2 — Doctor / Admin Account */}
            <div data-onboarding-step={2} style={sectionCard}>
              <p style={sectionTitle}>
                <span style={stepBadge(2)}>2</span>
                Doctor / Admin Account
              </p>
              <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '1rem' }}>
                Primary doctor or practice manager login and role assignment.
              </p>

              <div style={fieldWrap}>
                <label htmlFor="doctor_name" style={labelStyle}>
                  Doctor name <span style={{ color: DANGER }}>*</span>
                </label>
                <input
                  id="doctor_name"
                  name="doctor_name"
                  type="text"
                  required
                  value={form.doctor_name}
                  onChange={(e) => set('doctor_name', e.target.value)}
                  placeholder="e.g. Dr. Med. Martina Müller"
                  style={inputStyle}
                />
              </div>

              <div style={fieldWrap}>
                <label htmlFor="contact_email" style={labelStyle}>
                  Contact email <span style={{ color: DANGER }}>*</span>
                </label>
                <input
                  id="contact_email"
                  name="contact_email"
                  type="email"
                  required
                  value={form.contact_email}
                  onChange={(e) => set('contact_email', e.target.value)}
                  placeholder="doctor@clinic.at"
                  style={inputStyle}
                />
              </div>

              <div style={fieldWrap}>
                <label htmlFor="contact_phone" style={labelStyle}>Contact phone</label>
                <input
                  id="contact_phone"
                  name="contact_phone"
                  type="tel"
                  value={form.contact_phone}
                  onChange={(e) => set('contact_phone', e.target.value)}
                  placeholder="+43 ..."
                  style={inputStyle}
                />
              </div>
            </div>

            {/* Step 3 — Workflow Preferences */}
            <div data-onboarding-step={3} style={sectionCard}>
              <p style={sectionTitle}>
                <span style={stepBadge(3)}>3</span>
                Workflow Preferences
              </p>
              <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '1rem' }}>
                Primary language (German / English fallback), call routing rules, and office hours.
              </p>

              {/* Language configuration */}
              <div
                data-section="language-foundation"
                style={{ marginBottom: '1rem', padding: '1rem', borderRadius: 10, border: `1px solid ${BORDER}`, background: CANVAS }}
              >
                <p style={{ fontWeight: 700, fontSize: '0.875rem', color: INK, marginBottom: '0.25rem' }}>
                  Language Configuration
                </p>
                <p style={{ fontSize: '0.75rem', color: MUTED, marginBottom: '0.75rem' }}>
                  Deutsch zuerst / Englisch als Fallback — Default for Austrian clinics: German-first
                </p>
                <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap' }}>
                  {([
                    { code: 'de' as const, label: 'Deutsch',            description: 'Primary — Austrian clinic default' },
                    { code: 'en' as const, label: 'English (Fallback)',  description: 'English fallback — for non-German speakers' },
                  ]).map((lang) => (
                    <button
                      key={lang.code}
                      type="button"
                      data-language-option={lang.code}
                      onClick={() => set('preferred_language', lang.code)}
                      style={{
                        flex: '1 1 160px',
                        padding: '0.75rem 1rem',
                        borderRadius: 10,
                        border: `1.5px solid ${form.preferred_language === lang.code ? ACCENT : BORDER}`,
                        background: form.preferred_language === lang.code ? FILL : '#f9fafb',
                        cursor: 'pointer',
                        textAlign: 'left',
                      }}
                    >
                      <p style={{ fontWeight: 700, fontSize: '0.875rem', color: INK, marginBottom: '0.125rem' }}>
                        {lang.label}
                        {form.preferred_language === lang.code && (
                          <span style={{ marginLeft: '0.5rem', fontSize: '0.7rem', color: ACCENT, fontWeight: 700 }}>
                            ✓ Selected
                          </span>
                        )}
                      </p>
                      <p style={{ fontSize: '0.75rem', color: MUTED }}>{lang.description}</p>
                    </button>
                  ))}
                </div>
                <p style={{ fontSize: '0.7rem', color: MUTED, marginTop: '0.625rem' }}>
                  Language preference controls future Vapi assistant and clinic UI defaults. This module stores preference only.
                </p>
              </div>

              <div style={fieldWrap}>
                <label htmlFor="estimated_call_volume" style={labelStyle}>Estimated call volume</label>
                <input
                  id="estimated_call_volume"
                  name="estimated_call_volume"
                  type="text"
                  value={form.estimated_call_volume}
                  onChange={(e) => set('estimated_call_volume', e.target.value)}
                  placeholder="e.g. 10–20 calls per day"
                  style={inputStyle}
                />
              </div>

              <div style={fieldWrap}>
                <label htmlFor="current_booking_system" style={labelStyle}>Current booking system</label>
                <input
                  id="current_booking_system"
                  name="current_booking_system"
                  type="text"
                  value={form.current_booking_system}
                  onChange={(e) => set('current_booking_system', e.target.value)}
                  placeholder="e.g. Doctolib, Ordio, manual"
                  style={inputStyle}
                />
              </div>

              <div style={fieldWrap}>
                <label htmlFor="workflow_notes" style={labelStyle}>Workflow notes</label>
                <textarea
                  id="workflow_notes"
                  name="workflow_notes"
                  rows={3}
                  value={form.workflow_notes}
                  onChange={(e) => set('workflow_notes', e.target.value)}
                  placeholder="Any special workflow requirements or scheduling constraints..."
                  style={{ ...inputStyle, resize: 'vertical', fontFamily: 'inherit' }}
                />
              </div>
            </div>

            {/* Step 4 — AI Intake Setup */}
            <div data-onboarding-step={4} style={sectionCard}>
              <p style={sectionTitle}>
                <span style={stepBadge(4)}>4</span>
                AI Intake Setup
              </p>
              <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '1rem' }}>
                Vapi intake script and appointment flow configuration. Machine credentials are managed via secure environment variables — never entered in this wizard.
              </p>

              {[
                { key: 'wants_ai_phone_intake' as const,  label: 'AI phone intake receptionist',   hint: 'Automated Austrian-German phone intake via Vapi' },
                { key: 'wants_dashboard' as const,         label: 'Clinical dashboard',              hint: 'Doctor-facing appointment queue and patient registry' },
                { key: 'wants_notifications' as const,     label: 'Internal notifications',          hint: 'In-app alerts for new appointment requests' },
              ].map(({ key, label, hint }) => (
                <label
                  key={key}
                  style={{
                    display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
                    padding: '0.75rem', borderRadius: 9, marginBottom: '0.625rem',
                    border: `1px solid ${form[key] ? ACCENT : BORDER}`,
                    background: form[key] ? FILL : '#f9fafb',
                    cursor: 'pointer',
                  }}
                >
                  <input
                    type="checkbox"
                    name={key}
                    checked={form[key]}
                    onChange={(e) => set(key, e.target.checked)}
                    style={{ marginTop: 3, accentColor: ACCENT, width: 16, height: 16, flexShrink: 0 }}
                  />
                  <div>
                    <p style={{ fontWeight: 600, fontSize: '0.875rem', color: INK, marginBottom: '0.125rem' }}>{label}</p>
                    <p style={{ fontSize: '0.75rem', color: MUTED }}>{hint}</p>
                  </div>
                </label>
              ))}
            </div>

            {/* Step 5 — Review & Pilot Activation */}
            <div data-onboarding-step={5} style={{ ...sectionCard, borderColor: ACCENT, background: '#fcfefe' }}>
              <p style={sectionTitle}>
                <span style={stepBadge(5)}>5</span>
                Review & Pilot Activation
              </p>
              <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '1rem' }}>
                Review configuration, sign pilot agreement, and activate.
              </p>

              {/* Safety copy */}
              <div
                style={{
                  padding: '0.875rem 1rem',
                  borderRadius: 9,
                  background: '#fffbee',
                  border: `1px solid ${WARN}`,
                  marginBottom: '1.125rem',
                  fontSize: '0.8125rem',
                  color: INK,
                  lineHeight: 1.6,
                }}
              >
                <p style={{ fontWeight: 700, marginBottom: '0.375rem', color: WARN }}>Safety Notice</p>
                <p>Do not enter patient data. This form collects clinic and contact information only.</p>
                <p style={{ marginTop: '0.375rem' }}>Pilot activation does not enable production PHI processing.</p>
                <p style={{ marginTop: '0.375rem', fontSize: '0.75rem', color: MUTED }}>
                  Pilot activation requires security, legal, and production-readiness review before real patient data can be processed.
                </p>
              </div>

              {/* Consent checkboxes */}
              <label
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
                  padding: '0.875rem', borderRadius: 9, marginBottom: '0.625rem',
                  border: `1px solid ${form.consent_pilot_contact ? ACCENT : BORDER}`,
                  background: form.consent_pilot_contact ? FILL : '#f9fafb',
                  cursor: 'pointer',
                }}
              >
                <input
                  type="checkbox"
                  name="consent_pilot_contact"
                  required
                  checked={form.consent_pilot_contact}
                  onChange={(e) => set('consent_pilot_contact', e.target.checked)}
                  style={{ marginTop: 3, accentColor: ACCENT, width: 16, height: 16, flexShrink: 0 }}
                />
                <span style={{ fontSize: '0.8125rem', color: INK, lineHeight: 1.5 }}>
                  I agree to be contacted by PraxisMed about this pilot request. No spam — pilot onboarding enquiry only.
                </span>
              </label>

              <label
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
                  padding: '0.875rem', borderRadius: 9, marginBottom: '1rem',
                  border: `1px solid ${form.acknowledges_no_phi ? ACCENT : BORDER}`,
                  background: form.acknowledges_no_phi ? FILL : '#f9fafb',
                  cursor: 'pointer',
                }}
              >
                <input
                  type="checkbox"
                  name="acknowledges_no_phi"
                  required
                  checked={form.acknowledges_no_phi}
                  onChange={(e) => set('acknowledges_no_phi', e.target.checked)}
                  style={{ marginTop: 3, accentColor: ACCENT, width: 16, height: 16, flexShrink: 0 }}
                />
                <span style={{ fontSize: '0.8125rem', color: INK, lineHeight: 1.5 }}>
                  I acknowledge this is a pilot onboarding request, not a production patient data system activation.
                  No real patient health information (PHI) will be processed until a full compliance review is complete.
                </span>
              </label>

              {/* Error state */}
              {submitState === 'error' && errorMessage && (
                <div
                  data-state="error"
                  style={{
                    padding: '0.875rem 1rem',
                    borderRadius: 9,
                    background: '#fff5f5',
                    border: `1px solid ${DANGER}`,
                    marginBottom: '1rem',
                    fontSize: '0.8125rem',
                    color: DANGER,
                  }}
                >
                  <strong>Submission error</strong>
                  <p style={{ marginTop: '0.25rem', color: INK }}>{errorMessage}</p>
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={submitState === 'submitting'}
                style={{
                  width: '100%',
                  padding: '0.8125rem 1.5rem',
                  borderRadius: 10,
                  border: 'none',
                  background: ACCENT,
                  color: '#ffffff',
                  fontSize: '0.9375rem',
                  fontWeight: 700,
                  cursor: submitState === 'submitting' ? 'wait' : 'pointer',
                  opacity: submitState === 'submitting' ? 0.7 : 1,
                }}
              >
                {submitState === 'submitting' ? 'Submitting…' : 'Submit Pilot Access Request'}
              </button>
            </div>

          </form>
        )}

        {/* Back link */}
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <a href="/dashboard" style={{ fontSize: '0.8125rem', color: MUTED, textDecoration: 'none' }}>
            ← Back to dashboard
          </a>
        </div>
      </div>
    </div>
  )
}
