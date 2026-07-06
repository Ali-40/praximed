'use client'

function ConsolePanel({
  title,
  children,
  warning,
}: {
  title: string
  children: React.ReactNode
  warning?: string
}) {
  return (
    <div
      style={{
        background: 'var(--color-card)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-card)',
        overflow: 'hidden',
        marginBottom: '1.25rem',
      }}
    >
      <div
        style={{
          padding: '0.875rem 1.25rem',
          borderBottom: '1px solid var(--color-border-soft)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
        }}
      >
        <h3 style={{ flex: 1, fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-text)' }}>
          {title}
        </h3>
        <span
          style={{
            fontSize: '0.6875rem',
            fontWeight: 600,
            padding: '2px 8px',
            borderRadius: 99,
            background: 'var(--color-border)',
            color: 'var(--color-text-muted)',
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
          }}
        >
          Demo only
        </span>
      </div>
      <div style={{ padding: '1rem 1.25rem' }}>{children}</div>
      {warning && (
        <div
          style={{
            margin: '0 1.25rem 1rem',
            padding: '0.625rem 1rem',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--color-warning-bg)',
            border: '1px solid var(--badge-amber-bg)',
            fontSize: '0.775rem',
            color: 'var(--color-warning)',
            display: 'flex',
            gap: '0.5rem',
            alignItems: 'flex-start',
          }}
        >
          <span style={{ userSelect: 'none', flexShrink: 0 }}>⚠</span>
          <span>{warning}</span>
        </div>
      )}
    </div>
  )
}

function DisabledField({ label, placeholder }: { label: string; placeholder: string }) {
  return (
    <div style={{ marginBottom: '0.75rem' }}>
      <label
        style={{
          display: 'block',
          fontSize: '0.75rem',
          fontWeight: 600,
          color: 'var(--color-text-muted)',
          marginBottom: '0.3rem',
          letterSpacing: '0.02em',
        }}
      >
        {label}
      </label>
      <input
        disabled
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '0.5rem 0.75rem',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--color-border)',
          background: 'var(--color-bg)',
          color: 'var(--color-text-faint)',
          fontSize: '0.8125rem',
          cursor: 'not-allowed',
          boxSizing: 'border-box',
        }}
      />
    </div>
  )
}

function ChecklistItem({ label, status }: { label: string; status: 'pass' | 'pending' | 'blocked' }) {
  const colors = {
    pass:    { bg: 'var(--badge-green-bg)', text: 'var(--badge-green-text)', icon: '✓' },
    pending: { bg: 'var(--badge-amber-bg)', text: 'var(--badge-amber-text)', icon: '○' },
    blocked: { bg: 'var(--badge-red-bg)',   text: 'var(--badge-red-text)',   icon: '✗' },
  }
  const c = colors[status]
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.625rem',
        padding: '0.5rem 0',
        borderBottom: '1px solid var(--color-border-soft)',
        fontSize: '0.8125rem',
      }}
    >
      <span
        style={{
          flexShrink: 0,
          width: 22,
          height: 22,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: '50%',
          background: c.bg,
          color: c.text,
          fontSize: '0.7rem',
          fontWeight: 700,
        }}
      >
        {c.icon}
      </span>
      <span style={{ flex: 1, color: 'var(--color-text)' }}>{label}</span>
      <span style={{ fontSize: '0.7rem', fontWeight: 600, color: c.text }}>{status}</span>
    </div>
  )
}

export default function DeveloperConsolePage() {
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
      <div style={{ width: '100%', maxWidth: 760 }}>

        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-navy)', letterSpacing: '-0.02em' }}>
              Developer Console
            </h1>
            <span
              style={{
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
              Staging scaffold
            </span>
          </div>
          <div
            data-state="security-boundary"
            style={{
              padding: '0.875rem 1.25rem',
              borderRadius: 'var(--radius)',
              background: 'var(--color-danger-bg)',
              border: '1px solid var(--badge-red-bg)',
              fontSize: '0.8125rem',
              color: 'var(--color-danger)',
              lineHeight: 1.6,
            }}
          >
            <strong>Never paste secrets into browser UI.</strong>{' '}
            Machine credentials are managed via secure environment variables, not this demo page.{' '}
            <strong>Production PHI remains NO-GO until hardening and legal review are complete.</strong>
          </div>
        </div>

        {/* Tenant provisioning panel */}
        <ConsolePanel
          title="Tenant Provisioning"
          warning="Tenant provisioning is disabled — demo only. Real provisioning requires backend admin endpoint."
        >
          <DisabledField label="Clinic name" placeholder="e.g. Hausarzt Praxis Wien" />
          <DisabledField label="Clinic ID (auto-generated)" placeholder="uuid auto-assigned" />
          <DisabledField label="Specialty" placeholder="e.g. Allgemeinmedizin" />
          <DisabledField label="Contact email" placeholder="praxis@example.at" />
          <button
            disabled
            style={{
              fontSize: '0.8125rem',
              fontWeight: 600,
              padding: '0.5rem 1.25rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: 'var(--color-border)',
              color: 'var(--color-text-muted)',
              cursor: 'not-allowed',
              opacity: 0.65,
            }}
          >
            Provision tenant
          </button>
        </ConsolePanel>

        {/* Clinic ID scope injection */}
        <ConsolePanel
          title="Clinic ID Scope Injection"
          warning="Scope injection is not wired — demo only. Clinic scope is set via authenticated session, not this panel."
        >
          <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            Current session scope: <code style={{ fontFamily: 'monospace', fontSize: '0.8rem', background: 'var(--color-bg)', padding: '1px 6px', borderRadius: 4 }}>1a5bbc75-c1b0-4488-94aa-64b3f1c50056</code> (Staging Fake Clinic)
          </p>
          <DisabledField label="Override clinic_id" placeholder="uuid — leave blank to use session default" />
          <button
            disabled
            style={{
              fontSize: '0.8125rem',
              fontWeight: 600,
              padding: '0.5rem 1.25rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: 'var(--color-border)',
              color: 'var(--color-text-muted)',
              cursor: 'not-allowed',
              opacity: 0.65,
            }}
          >
            Apply scope
          </button>
        </ConsolePanel>

        {/* Vapi machine credential binding */}
        <ConsolePanel
          title="Vapi Machine Credential Binding"
          warning="Never paste secrets into browser UI. Machine credentials are managed via secure environment variables, not this demo page."
        >
          <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            Vapi credentials are injected at deploy time via <code style={{ fontFamily: 'monospace', fontSize: '0.8rem', background: 'var(--color-bg)', padding: '1px 6px', borderRadius: 4 }}>VAPI_API_KEY</code> environment variable.
            This panel is a placeholder — no credential input is accepted.
          </p>
          <DisabledField label="Vapi machine credential ID" placeholder="Set via environment variable — not entered here" />
          <DisabledField label="Vapi phone number" placeholder="Set via environment variable — not entered here" />
          <button
            disabled
            style={{
              fontSize: '0.8125rem',
              fontWeight: 600,
              padding: '0.5rem 1.25rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: 'var(--color-border)',
              color: 'var(--color-text-muted)',
              cursor: 'not-allowed',
              opacity: 0.65,
            }}
          >
            Bind credential
          </button>
        </ConsolePanel>

        {/* Environment checklist */}
        <ConsolePanel title="Environment Checklist">
          <ChecklistItem label="Backend API reachable" status="pass" />
          <ChecklistItem label="Cookie session auth active" status="pass" />
          <ChecklistItem label="Staging fake-data tenant loaded" status="pass" />
          <ChecklistItem label="Vapi webhook endpoint registered" status="pending" />
          <ChecklistItem label="C3 — Secrets hardening complete" status="blocked" />
          <ChecklistItem label="C4 — PHI logging/redaction hardening" status="blocked" />
          <ChecklistItem label="C5 — Tenant isolation verification" status="blocked" />
          <ChecklistItem label="C6 — Audit trail hardening" status="blocked" />
          <ChecklistItem label="C7 — Backup/restore runbook" status="blocked" />
          <ChecklistItem label="C8 — Legal / DSGVO review" status="blocked" />
        </ConsolePanel>

        {/* Safety boundary panel */}
        <ConsolePanel title="Safety Boundary">
          {[
            'Production PHI remains NO-GO until C3–C8 hardening and legal review are complete.',
            'This staging environment uses synthetic fake data only — no real patient records.',
            'No DSGVO / Austrian data protection compliance claim is made at this stage.',
            'Machine credentials are managed via secure environment variables, not this demo page.',
            'Never paste secrets into browser UI.',
          ].map((line, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                gap: '0.625rem',
                alignItems: 'flex-start',
                padding: '0.5rem 0',
                borderBottom: i < 4 ? '1px solid var(--color-border-soft)' : 'none',
                fontSize: '0.8125rem',
                color: 'var(--color-text)',
              }}
            >
              <span style={{ flexShrink: 0, color: 'var(--color-danger)', fontWeight: 700 }}>!</span>
              <span>{line}</span>
            </div>
          ))}
        </ConsolePanel>

        {/* Back link */}
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <a href="/dashboard" style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', textDecoration: 'none' }}>
            ← Back to dashboard
          </a>
        </div>
      </div>
    </div>
  )
}
