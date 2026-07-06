'use client'

export default function OnboardingPage() {
  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'var(--color-bg)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '3rem 1.5rem',
      }}
    >
      <div style={{ width: '100%', maxWidth: 680 }}>

        {/* Header */}
        <div style={{ marginBottom: '2.5rem', textAlign: 'center' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-navy)', letterSpacing: '-0.02em', marginBottom: '0.5rem' }}>
            Start with PraxisMed
          </h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
            Invite-only pilot setup — 5 steps to activate your clinic&apos;s AI intake assistant
          </p>
          <div
            style={{
              display: 'inline-block',
              marginTop: '0.75rem',
              fontSize: '0.6875rem',
              fontWeight: 600,
              padding: '2px 10px',
              borderRadius: 99,
              background: 'var(--badge-amber-bg)',
              color: 'var(--badge-amber-text)',
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
            }}
          >
            Staging scaffold — not functional
          </div>
        </div>

        {/* Steps */}
        {[
          {
            number: 1,
            title: 'Clinic details',
            description: 'Legal clinic name, address, specialty, and contact information.',
            status: 'active',
          },
          {
            number: 2,
            title: 'Doctor / admin account',
            description: 'Primary doctor or practice manager login and role assignment.',
            status: 'pending',
          },
          {
            number: 3,
            title: 'Workflow preferences',
            description: 'Language (German / English), call routing rules, and office hours.',
            status: 'pending',
          },
          {
            number: 4,
            title: 'AI intake setup',
            description: 'Vapi machine credential binding, intake script, and appointment flow.',
            status: 'pending',
          },
          {
            number: 5,
            title: 'Review &amp; pilot activation',
            description: 'Review configuration, sign pilot agreement, and activate.',
            status: 'pending',
          },
        ].map((step) => (
          <div
            key={step.number}
            data-onboarding-step={step.number}
            style={{
              display: 'flex',
              gap: '1rem',
              marginBottom: '1rem',
              padding: '1.25rem',
              borderRadius: 'var(--radius-lg)',
              border: `1px solid ${step.status === 'active' ? 'var(--color-teal-light)' : 'var(--color-border)'}`,
              background: step.status === 'active' ? 'var(--color-teal-bg)' : 'var(--color-card)',
              boxShadow: 'var(--shadow-xs)',
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
                background: step.status === 'active' ? 'var(--color-teal)' : 'var(--color-border)',
                color: step.status === 'active' ? '#ffffff' : 'var(--color-text-muted)',
              }}
            >
              {step.number}
            </div>
            <div>
              <p style={{ fontWeight: 600, fontSize: '0.9375rem', color: 'var(--color-text)', marginBottom: '0.25rem' }}>
                {step.title}
              </p>
              <p
                style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}
                dangerouslySetInnerHTML={{ __html: step.description }}
              />
            </div>
          </div>
        ))}

        {/* CTA */}
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <button
            disabled
            style={{
              fontSize: '0.9375rem',
              fontWeight: 600,
              padding: '0.75rem 2rem',
              borderRadius: 'var(--radius)',
              border: 'none',
              background: 'var(--color-teal)',
              color: '#ffffff',
              cursor: 'not-allowed',
              opacity: 0.5,
            }}
          >
            Request pilot setup
          </button>
          <p
            style={{
              marginTop: '1rem',
              fontSize: '0.75rem',
              color: 'var(--color-text-muted)',
              maxWidth: 460,
              margin: '1rem auto 0',
              lineHeight: 1.5,
            }}
          >
            Pilot activation requires security, legal, and production-readiness review before real patient data can be processed.
            This page is a scaffold — submission is not yet wired.
          </p>
        </div>

        {/* Back link */}
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <a href="/dashboard" style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', textDecoration: 'none' }}>
            ← Back to dashboard
          </a>
        </div>
      </div>
    </div>
  )
}
