'use client'

// PraxisMed — Public Patient Intake Page
// Sprint 20 / Module 151 — Demo-only tokenized consent-first questionnaire.
//
// Mobile-first. No login required. Synthetic/fake staging only.
// Do not enter real medical information.
// Consent step required before questionnaire.
// de / en / ar language support. ar sets dir="rtl".
//
// No real patient data. No PHI. No diagnosis. No medical advice.
// No appointment confirmation promise. No treatment recommendations.
// No localStorage. No sessionStorage. Production PHI remains NO-GO.

import { useEffect, useState } from 'react'
import { fetchPublicIntakeTemplate, submitPublicIntake } from '../../../lib/api'

// ── Colours ────────────────────────────────────────────────────────────────────

const BG     = '#F7F8FA'
const WHITE  = '#FFFFFF'
const INK    = '#1A2236'
const MUTED  = '#6B7A99'
const ACCENT = '#006B75'
const WARN   = '#C8390E'
const EDGE   = '#E2E6EF'
const GREEN  = '#1A7A4A'

// ── Types ──────────────────────────────────────────────────────────────────────

interface Question {
  question_key: string
  history_target: string
  type: string
  label: Record<string, string>
  help_text?: Record<string, string>
  required: boolean
  skip_allowed: boolean
  options?: { value?: string; label: Record<string, string> }[]
}

interface Section {
  section_key: string
  title: Record<string, string>
  description?: Record<string, string>
  questions: Question[]
}

interface IntakeTemplate {
  link_id: string
  clinic_id: string
  language: string
  purpose: string
  template_key: string
  display_name: string
  specialty: string
  primary_language: string
  template_schema: { sections: Section[] }
  escalation_keywords: string[]
  demo_notice: string
}

type Step = 'loading' | 'error' | 'consent' | 'questionnaire' | 'submitting' | 'success'

const LANGUAGES = [
  { code: 'de', label: 'Deutsch' },
  { code: 'en', label: 'English' },
  { code: 'ar', label: 'العربية' },
] as const

function t(labels: Record<string, string>, lang: string): string {
  return labels[lang] ?? labels['de'] ?? labels['en'] ?? Object.values(labels)[0] ?? ''
}

// ── Main page ──────────────────────────────────────────────────────────────────

export default function IntakePage({ params }: { params: { token: string } }) {
  const { token } = params
  const [step, setStep] = useState<Step>('loading')
  const [errorMsg, setErrorMsg] = useState('')
  const [template, setTemplate] = useState<IntakeTemplate | null>(null)
  const [language, setLanguage] = useState<string>('de')
  const [consentChecked, setConsentChecked] = useState(false)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [skipped, setSkipped] = useState<Set<string>>(new Set())
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [submissionId, setSubmissionId] = useState('')

  const isRtl = language === 'ar'

  useEffect(() => {
    fetchPublicIntakeTemplate(token)
      .then((data) => {
        if (data?.template) {
          const tmpl = data.template as IntakeTemplate
          setTemplate(tmpl)
          setLanguage(tmpl.language ?? tmpl.primary_language ?? 'de')
          setStep('consent')
        } else {
          setErrorMsg(data?.message ?? 'Intake link not found.')
          setStep('error')
        }
      })
      .catch((err: Error) => {
        const msg = err.message ?? ''
        if (msg.includes('410') || msg.includes('expired')) {
          setErrorMsg('This intake link has expired or been revoked.')
        } else if (msg.includes('404') || msg.includes('not found')) {
          setErrorMsg('Intake link not found or invalid.')
        } else {
          setErrorMsg('Could not load intake. Please try again later.')
        }
        setStep('error')
      })
  }, [token])

  function handleConsentProceed() {
    if (!consentChecked) return
    setStep('questionnaire')
  }

  function setAnswer(key: string, value: string) {
    setAnswers((prev) => ({ ...prev, [key]: value }))
    setValidationErrors((prev) => {
      const next = { ...prev }
      delete next[key]
      return next
    })
    setSkipped((prev) => {
      const next = new Set(prev)
      next.delete(key)
      return next
    })
  }

  function toggleSkip(key: string) {
    setSkipped((prev) => {
      const next = new Set(prev)
      if (next.has(key)) {
        next.delete(key)
      } else {
        next.add(key)
        setAnswers((a) => {
          const cp = { ...a }
          delete cp[key]
          return cp
        })
      }
      return next
    })
  }

  function validateBeforeSubmit(): boolean {
    if (!template) return false
    const errors: Record<string, string> = {}
    for (const section of template.template_schema.sections) {
      for (const q of section.questions) {
        if (q.required && !skipped.has(q.question_key)) {
          const val = answers[q.question_key]
          if (!val || !val.trim()) {
            errors[q.question_key] = 'This question is required.'
          }
        }
      }
    }
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  async function handleSubmit() {
    if (!validateBeforeSubmit()) return
    setStep('submitting')
    try {
      const result = await submitPublicIntake(token, {
        language,
        answers,
        skipped_questions: Array.from(skipped),
        consent_granted: true,
        consent_text_version: 'v1',
        consent_text_snapshot:
          'I understand this is a demo intake and consent to submit synthetic information for testing.',
      })
      if (result?.ok) {
        setSubmissionId(result.submission_id ?? '')
        setStep('success')
      } else {
        setErrorMsg('Could not submit intake. Please try again.')
        setStep('questionnaire')
      }
    } catch {
      setErrorMsg('Could not submit intake. Please try again.')
      setStep('questionnaire')
    }
  }

  const containerStyle: React.CSSProperties = {
    minHeight: '100vh',
    background: BG,
    fontFamily: 'system-ui, -apple-system, sans-serif',
    direction: isRtl ? 'rtl' : 'ltr',
  }

  const cardStyle: React.CSSProperties = {
    maxWidth: 560,
    margin: '0 auto',
    padding: '1.25rem',
  }

  const warningBanner = (
    <div
      style={{
        background: '#FFF8E6',
        border: `1px solid ${WARN}`,
        borderRadius: 8,
        padding: '0.75rem 1rem',
        fontSize: '0.8125rem',
        color: WARN,
        fontWeight: 600,
        marginBottom: '1.25rem',
      }}
    >
      Demo staging intake only. Do not enter real medical information.
    </div>
  )

  // ── Loading ────────────────────────────────────────────────────────────────

  if (step === 'loading') {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <p style={{ color: MUTED, padding: '2rem 0', textAlign: 'center' }}>Loading…</p>
        </div>
      </div>
    )
  }

  // ── Error ──────────────────────────────────────────────────────────────────

  if (step === 'error') {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          {warningBanner}
          <div
            style={{
              background: WHITE,
              borderRadius: 12,
              padding: '2rem',
              border: `1px solid ${EDGE}`,
              textAlign: 'center',
            }}
          >
            <p style={{ color: WARN, fontWeight: 700, marginBottom: '0.5rem' }}>
              {errorMsg || 'Intake link not found or invalid.'}
            </p>
            <p style={{ color: MUTED, fontSize: '0.8125rem' }}>
              Please request a new intake link from your clinic.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // ── Success ────────────────────────────────────────────────────────────────

  if (step === 'success') {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          {warningBanner}
          <div
            style={{
              background: WHITE,
              borderRadius: 12,
              padding: '2rem',
              border: `1px solid ${EDGE}`,
              textAlign: 'center',
            }}
          >
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 99,
                background: 'rgba(26,122,74,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
                fontSize: '1.5rem',
              }}
            >
              ✓
            </div>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: GREEN, marginBottom: '0.5rem' }}>
              Intake submitted for staff review.
            </h2>
            <p style={{ color: MUTED, fontSize: '0.8125rem', lineHeight: 1.5 }}>
              Your answers have been recorded for staff review. No appointment confirmation is made
              at this stage. Your clinic will follow up with you.
            </p>
            {submissionId && (
              <p style={{ color: MUTED, fontSize: '0.75rem', marginTop: '1rem' }}>
                Reference: {submissionId.slice(0, 8)}…
              </p>
            )}
          </div>
        </div>
      </div>
    )
  }

  // ── Consent ────────────────────────────────────────────────────────────────

  if (step === 'consent') {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          {warningBanner}
          <div style={{ background: WHITE, borderRadius: 12, padding: '1.5rem', border: `1px solid ${EDGE}` }}>
            <h1 style={{ fontSize: '1.125rem', fontWeight: 700, color: INK, marginBottom: '0.25rem' }}>
              {template?.display_name ?? 'Patient Intake'}
            </h1>
            <p style={{ color: MUTED, fontSize: '0.8125rem', marginBottom: '1.25rem' }}>
              {template?.specialty} · Demo staging
            </p>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: 700, color: MUTED, display: 'block', marginBottom: '0.3rem' }}>
                Language / Sprache / اللغة
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{
                  padding: '0.5rem 0.75rem',
                  borderRadius: 7,
                  border: `1px solid ${EDGE}`,
                  background: WHITE,
                  color: INK,
                  fontSize: '0.8125rem',
                  minWidth: 140,
                }}
              >
                {LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code}>{l.label}</option>
                ))}
              </select>
            </div>

            <div
              style={{
                background: '#F0F8FF',
                border: `1px solid ${ACCENT}`,
                borderRadius: 8,
                padding: '1rem',
                marginBottom: '1.25rem',
                fontSize: '0.8125rem',
                color: INK,
                lineHeight: 1.6,
              }}
            >
              I understand this is a demo intake and consent to submit synthetic information for testing.
            </div>

            <label
              style={{ display: 'flex', alignItems: 'flex-start', gap: '0.625rem', cursor: 'pointer', marginBottom: '1.25rem' }}
            >
              <input
                type="checkbox"
                checked={consentChecked}
                onChange={(e) => setConsentChecked(e.target.checked)}
                style={{ marginTop: 2, accentColor: ACCENT }}
              />
              <span style={{ fontSize: '0.8125rem', color: INK, lineHeight: 1.5 }}>
                I have read and agree to the above. I will only enter synthetic/demo information.
              </span>
            </label>

            <button
              onClick={handleConsentProceed}
              disabled={!consentChecked}
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: 8,
                border: 'none',
                background: consentChecked ? ACCENT : EDGE,
                color: consentChecked ? '#fff' : MUTED,
                fontWeight: 700,
                fontSize: '0.9rem',
                cursor: consentChecked ? 'pointer' : 'not-allowed',
              }}
            >
              Continue to questionnaire →
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ── Questionnaire ──────────────────────────────────────────────────────────

  const sections = template?.template_schema?.sections ?? []

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        {warningBanner}

        <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '1rem', fontWeight: 700, color: INK }}>
            {template?.display_name}
          </h1>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{
              padding: '0.3rem 0.5rem',
              borderRadius: 6,
              border: `1px solid ${EDGE}`,
              background: WHITE,
              color: INK,
              fontSize: '0.75rem',
            }}
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>{l.label}</option>
            ))}
          </select>
        </div>

        {sections.map((section) => (
          <div
            key={section.section_key}
            style={{
              background: WHITE,
              borderRadius: 12,
              border: `1px solid ${EDGE}`,
              marginBottom: '1rem',
              overflow: 'hidden',
            }}
          >
            <div style={{ padding: '1rem 1.25rem', borderBottom: `1px solid ${EDGE}` }}>
              <h2 style={{ fontSize: '0.9375rem', fontWeight: 700, color: INK }}>
                {t(section.title, language)}
              </h2>
              {section.description && (
                <p style={{ fontSize: '0.8125rem', color: MUTED, marginTop: '0.25rem' }}>
                  {t(section.description, language)}
                </p>
              )}
            </div>

            <div style={{ padding: '1rem 1.25rem' }}>
              {section.questions.map((q, qi) => {
                const isSkipped = skipped.has(q.question_key)
                const err = validationErrors[q.question_key]
                const label = t(q.label, language)
                const helpText = q.help_text ? t(q.help_text, language) : undefined

                return (
                  <div
                    key={q.question_key}
                    style={{
                      marginBottom: qi < section.questions.length - 1 ? '1.25rem' : 0,
                      opacity: isSkipped ? 0.45 : 1,
                    }}
                  >
                    <label style={{ fontSize: '0.875rem', fontWeight: 600, color: INK, display: 'block', marginBottom: '0.25rem' }}>
                      {label}
                      {q.required && !isSkipped && (
                        <span style={{ color: WARN, marginLeft: '0.25rem' }}>*</span>
                      )}
                    </label>

                    {helpText && (
                      <p style={{ fontSize: '0.75rem', color: MUTED, marginBottom: '0.375rem' }}>
                        {helpText}
                      </p>
                    )}

                    {!isSkipped && renderInput(q, language, answers, setAnswer)}

                    {err && (
                      <p style={{ fontSize: '0.75rem', color: WARN, marginTop: '0.25rem' }}>{err}</p>
                    )}

                    {q.skip_allowed && (
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.375rem', cursor: 'pointer' }}>
                        <input
                          type="checkbox"
                          checked={isSkipped}
                          onChange={() => toggleSkip(q.question_key)}
                          style={{ accentColor: MUTED }}
                        />
                        <span style={{ fontSize: '0.75rem', color: MUTED }}>Skip this question</span>
                      </label>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        ))}

        {errorMsg && (
          <div style={{ color: WARN, fontSize: '0.8125rem', marginBottom: '0.75rem', fontWeight: 600 }}>
            {errorMsg}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={step === 'submitting'}
          style={{
            width: '100%',
            padding: '0.875rem',
            borderRadius: 8,
            border: 'none',
            background: ACCENT,
            color: '#fff',
            fontWeight: 700,
            fontSize: '1rem',
            cursor: step === 'submitting' ? 'not-allowed' : 'pointer',
            marginTop: '0.5rem',
          }}
        >
          {step === 'submitting' ? 'Submitting…' : 'Submit intake'}
        </button>

        <p style={{ fontSize: '0.75rem', color: MUTED, textAlign: 'center', marginTop: '0.75rem', lineHeight: 1.5 }}>
          Answers are submitted for staff review only. No medical diagnosis is provided.
          No appointment is confirmed at this stage.
        </p>
      </div>
    </div>
  )
}

function renderInput(
  q: Question,
  language: string,
  answers: Record<string, string>,
  setAnswer: (key: string, value: string) => void,
): React.ReactNode {
  const INK = '#1A2236'
  const EDGE = '#E2E6EF'
  const WHITE = '#FFFFFF'

  const baseInput: React.CSSProperties = {
    width: '100%',
    padding: '0.5rem 0.75rem',
    borderRadius: 7,
    border: `1px solid ${EDGE}`,
    background: WHITE,
    color: INK,
    fontSize: '0.875rem',
    boxSizing: 'border-box',
  }

  const val = answers[q.question_key] ?? ''

  if (q.type === 'text') {
    return (
      <input
        type="text"
        value={val}
        onChange={(e) => setAnswer(q.question_key, e.target.value)}
        style={baseInput}
      />
    )
  }
  if (q.type === 'textarea') {
    return (
      <textarea
        value={val}
        onChange={(e) => setAnswer(q.question_key, e.target.value)}
        rows={3}
        style={{ ...baseInput, resize: 'vertical' }}
      />
    )
  }
  if (q.type === 'yes_no') {
    return (
      <div style={{ display: 'flex', gap: '0.75rem' }}>
        {['yes', 'no'].map((opt) => (
          <label key={opt} style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', cursor: 'pointer', fontSize: '0.875rem', color: INK }}>
            <input
              type="radio"
              name={q.question_key}
              value={opt}
              checked={val === opt}
              onChange={() => setAnswer(q.question_key, opt)}
            />
            {opt === 'yes' ? 'Ja / Yes / نعم' : 'Nein / No / لا'}
          </label>
        ))}
      </div>
    )
  }
  if (q.type === 'single_select') {
    return (
      <select
        value={val}
        onChange={(e) => setAnswer(q.question_key, e.target.value)}
        style={baseInput}
      >
        <option value="">—</option>
        {(q.options ?? []).map((opt, i) => (
          <option key={i} value={opt.value ?? String(i)}>
            {opt.label ? (opt.label[language] ?? opt.label['de'] ?? opt.label['en'] ?? String(i)) : String(i)}
          </option>
        ))}
      </select>
    )
  }
  if (q.type === 'multi_select') {
    const vals = val ? val.split(',') : []
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
        {(q.options ?? []).map((opt, i) => {
          const optVal = opt.value ?? String(i)
          const optLabel = opt.label ? (opt.label[language] ?? opt.label['de'] ?? opt.label['en'] ?? optVal) : optVal
          return (
            <label key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', cursor: 'pointer', fontSize: '0.875rem', color: INK }}>
              <input
                type="checkbox"
                checked={vals.includes(optVal)}
                onChange={(e) => {
                  const next = e.target.checked
                    ? [...vals, optVal]
                    : vals.filter((v) => v !== optVal)
                  setAnswer(q.question_key, next.join(','))
                }}
              />
              {optLabel}
            </label>
          )
        })}
      </div>
    )
  }
  if (q.type === 'date') {
    return (
      <input
        type="date"
        value={val}
        onChange={(e) => setAnswer(q.question_key, e.target.value)}
        style={baseInput}
      />
    )
  }
  if (q.type === 'number') {
    return (
      <input
        type="number"
        value={val}
        onChange={(e) => setAnswer(q.question_key, e.target.value)}
        style={baseInput}
      />
    )
  }
  return (
    <input
      type="text"
      value={val}
      onChange={(e) => setAnswer(q.question_key, e.target.value)}
      style={baseInput}
    />
  )
}
