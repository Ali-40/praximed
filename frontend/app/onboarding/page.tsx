'use client'

// PraxisMed — Doctor Onboarding & Gateway Flow
// Sprint 18 / Module 126C-FABEL5 — Premium Austrian Clinic Interface Overhaul.
//
// Gated access entry + five-step pilot onboarding wizard.
// Staging scaffold only — non-functional. No secrets collected. No Vapi secret
// keys. No real patient data. Production PHI: NO-GO.
//
// HTML rendering bug fixed: the step title renders as plain text
// "Review & Pilot Activation" (previously an escaped entity leaked into the UI).

const INK    = '#0B132B'   // Primary Structural Ink
const ACCENT = '#008080'   // Clinical Accent
const FILL   = '#E0F2F1'   // Highlight Muted Fill
const WARN   = '#FFB703'   // Warning / staging marker
const CANVAS = '#F4F6F9'   // Canvas Background
const BORDER = '#E3E8EF'
const MUTED  = '#5B6472'

const STEPS = [
  {
    number: 1,
    title: 'Clinic Details',
    description: 'Legal clinic name, address, specialty, and contact information.',
    status: 'active',
  },
  {
    number: 2,
    title: 'Doctor / Admin Account',
    description: 'Primary doctor or practice manager login and role assignment.',
    status: 'pending',
  },
  {
    number: 3,
    title: 'Workflow Preferences',
    description: 'Primary language (German / English fallback), call routing rules, and office hours.',
    status: 'pending',
  },
  {
    number: 4,
    title: 'AI Intake Setup',
    description:
      'Vapi intake script and appointment flow configuration. Machine credentials are managed via secure environment variables — never entered in this wizard.',
    status: 'pending',
  },
  {
    number: 5,
    // Plain rendered text — no escaped HTML entities in the visible label.
    title: 'Review & Pilot Activation',
    description: 'Review configuration, sign pilot agreement, and activate.',
    status: 'pending',
  },
] as const

export default function OnboardingPage() {
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
        {/* Gated access entry module                                            */}
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
              disabled
              title="Pilot registration is a staging scaffold — not functional"
              style={{
                fontSize: '0.875rem', fontWeight: 700, padding: '0.65rem 1.5rem', borderRadius: 9,
                background: 'transparent', color: 'rgba(255,255,255,0.85)',
                border: '1px solid rgba(255,255,255,0.35)', cursor: 'not-allowed',
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
            STAGING SCAFFOLD — NOT FUNCTIONAL
          </div>
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* Five-step onboarding workflow                                        */}
        {/* ------------------------------------------------------------------ */}
        {STEPS.map((step) => (
          <div
            key={step.number}
            data-onboarding-step={step.number}
            style={{
              display: 'flex',
              gap: '1rem',
              marginBottom: '1rem',
              padding: '1.25rem',
              borderRadius: 14,
              border: `1px solid ${step.status === 'active' ? ACCENT : BORDER}`,
              background: step.status === 'active' ? FILL : '#ffffff',
              boxShadow: '0 1px 2px 0 rgb(11 19 43 / 0.05)',
            }}
          >
            <div
              style={{
                flexShrink: 0,
                width: 32,
                height: 32,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.8125rem',
                fontWeight: 700,
                background: step.status === 'active' ? ACCENT : BORDER,
                color: step.status === 'active' ? '#ffffff' : MUTED,
              }}
            >
              {step.number}
            </div>
            <div>
              <p style={{ fontWeight: 700, fontSize: '0.9375rem', color: INK, marginBottom: '0.25rem' }}>
                {step.title}
              </p>
              <p style={{ fontSize: '0.8125rem', color: MUTED }}>
                {step.description}
              </p>
            </div>
          </div>
        ))}

        {/* ------------------------------------------------------------------ */}
        {/* Language foundation selector (Step 3 preview — scaffold only)       */}
        {/* ------------------------------------------------------------------ */}
        <div
          data-section="language-foundation"
          style={{
            marginTop: '1.5rem',
            marginBottom: '1rem',
            padding: '1.25rem',
            borderRadius: 14,
            border: `1px solid ${BORDER}`,
            background: '#ffffff',
            boxShadow: '0 1px 2px 0 rgb(11 19 43 / 0.05)',
          }}
        >
          <p style={{ fontWeight: 700, fontSize: '0.9375rem', color: INK, marginBottom: '0.5rem' }}>
            Language Configuration
          </p>
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '1rem' }}>
            Your clinic interface and AI receptionist will use German as the primary language, with English as the fallback. This is configurable during pilot setup.
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            {[
              { code: 'de', label: 'Deutsch', description: 'Primary — Austrian clinic default', selected: true },
              { code: 'en', label: 'English', description: 'Fallback — for non-German speakers', selected: false },
            ].map((lang) => (
              <div
                key={lang.code}
                data-language-option={lang.code}
                style={{
                  flex: '1 1 180px',
                  padding: '0.875rem 1rem',
                  borderRadius: 10,
                  border: `1.5px solid ${lang.selected ? ACCENT : BORDER}`,
                  background: lang.selected ? FILL : '#f9fafb',
                  opacity: 0.85,
                }}
              >
                <p style={{ fontWeight: 700, fontSize: '0.875rem', color: INK, marginBottom: '0.125rem' }}>
                  {lang.label}
                  {lang.selected && (
                    <span style={{ marginLeft: '0.5rem', fontSize: '0.7rem', color: ACCENT, fontWeight: 700 }}>
                      ✓ Default
                    </span>
                  )}
                </p>
                <p style={{ fontSize: '0.75rem', color: MUTED }}>{lang.description}</p>
              </div>
            ))}
          </div>
          <p style={{ fontSize: '0.7rem', color: MUTED, marginTop: '0.75rem' }}>
            Language selection is not yet interactive — configurable during pilot onboarding.
          </p>
        </div>

        {/* CTA */}
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <button
            disabled
            style={{
              fontSize: '0.9375rem',
              fontWeight: 700,
              padding: '0.75rem 2rem',
              borderRadius: 10,
              border: 'none',
              background: ACCENT,
              color: '#ffffff',
              cursor: 'not-allowed',
              opacity: 0.5,
            }}
          >
            Request pilot setup
          </button>
          <p
            style={{
              fontSize: '0.75rem',
              color: MUTED,
              maxWidth: 460,
              margin: '1rem auto 0',
              lineHeight: 1.5,
            }}
          >
            Pilot activation requires security, legal, and production-readiness review before real patient data can be processed.
            This page is a scaffold — submission is not yet wired. No secrets or Vapi credentials are collected here.
          </p>
        </div>

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
