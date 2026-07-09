'use client'

// PraxisMed — Master Developer Administrative Console
// Sprint 18 / Module 126C-FABEL5 — explicit dense dark-mode command theme.
//
// Visually segregated from the clinical UI to prevent accidental configuration.
// Demo-only scaffold: no live mutation, no real provisioning, no secrets, no PHI.
// Background: #0B132B · teal accents #008080 · red guardrails #E63946 · amber #FFB703

const INK    = '#0B132B'   // console background — Primary Structural Ink
const PANEL  = '#111C3D'   // panel surface on ink
const EDGE   = 'rgba(255,255,255,0.10)'
const ACCENT = '#008080'   // teal accents
const DANGER = '#E63946'   // red guardrails
const WARN   = '#FFB703'   // amber warnings
const TEXT   = '#E6EAF2'   // white/slate text
const MUTED  = '#93A0B8'   // slate muted

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
        background: PANEL,
        border: `1px solid ${EDGE}`,
        borderRadius: 12,
        overflow: 'hidden',
        marginBottom: '1.25rem',
      }}
    >
      <div
        style={{
          padding: '0.875rem 1.25rem',
          borderBottom: `1px solid ${EDGE}`,
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
        }}
      >
        <span aria-hidden style={{ width: 7, height: 7, borderRadius: 99, background: ACCENT }} />
        <h3 style={{ flex: 1, fontSize: '0.9rem', fontWeight: 700, color: TEXT, letterSpacing: '0.01em' }}>
          {title}
        </h3>
        <span
          style={{
            fontSize: '0.6875rem',
            fontWeight: 700,
            padding: '2px 9px',
            borderRadius: 99,
            background: 'rgba(255,183,3,0.15)',
            color: WARN,
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
            border: `1px solid rgba(255,183,3,0.4)`,
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
            borderRadius: 8,
            background: 'rgba(255,183,3,0.10)',
            border: `1px solid rgba(255,183,3,0.35)`,
            fontSize: '0.775rem',
            color: WARN,
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
          fontSize: '0.7rem',
          fontWeight: 700,
          color: MUTED,
          marginBottom: '0.3rem',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
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
          borderRadius: 7,
          border: `1px solid ${EDGE}`,
          background: 'rgba(255,255,255,0.04)',
          color: MUTED,
          fontSize: '0.8125rem',
          fontFamily: 'ui-monospace, monospace',
          cursor: 'not-allowed',
          boxSizing: 'border-box',
        }}
      />
    </div>
  )
}

function DisabledButton({ label }: { label: string }) {
  return (
    <button
      disabled
      style={{
        fontSize: '0.8125rem',
        fontWeight: 700,
        padding: '0.5rem 1.25rem',
        borderRadius: 7,
        border: `1px solid ${ACCENT}`,
        background: 'rgba(0,128,128,0.15)',
        color: ACCENT,
        cursor: 'not-allowed',
        opacity: 0.7,
      }}
    >
      {label}
    </button>
  )
}

function ChecklistItem({ label, status }: { label: string; status: 'pass' | 'pending' | 'blocked' }) {
  const colors = {
    pass:    { color: '#4ADE80', icon: '✓' },
    pending: { color: WARN,      icon: '○' },
    blocked: { color: DANGER,    icon: '✗' },
  }
  const c = colors[status]
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.625rem',
        padding: '0.5rem 0',
        borderBottom: `1px solid ${EDGE}`,
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
          border: `1px solid ${c.color}`,
          color: c.color,
          fontSize: '0.7rem',
          fontWeight: 700,
        }}
      >
        {c.icon}
      </span>
      <span style={{ flex: 1, color: TEXT }}>{label}</span>
      <span style={{ fontSize: '0.7rem', fontWeight: 700, color: c.color, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{status}</span>
    </div>
  )
}

// Environment variable names are shown as labels only — values are never
// displayed, requested, or entered in this console.
const ENV_CHECKLIST = [
  'DATABASE_URL',
  'JWT_SECRET_KEY',
  'VAPI_WEBHOOK_SECRET',
  'INTERNAL_WEBHOOK_SECRET',
  'FRONTEND_CORS_ORIGINS',
] as const

export default function DeveloperConsolePage() {
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
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.01em' }}>
              Developer Console
            </h1>
            <span
              style={{
                fontSize: '0.6875rem',
                fontWeight: 700,
                padding: '2px 10px',
                borderRadius: 99,
                background: WARN,
                color: INK,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
              }}
            >
              Staging scaffold
            </span>
            <span style={{ fontSize: '0.6875rem', color: MUTED, letterSpacing: '0.02em' }}>
              Administrative command console — segregated from clinical UI
            </span>
          </div>

          {/* Red guardrail alert panel */}
          <div
            data-state="security-boundary"
            style={{
              padding: '0.875rem 1.25rem',
              borderRadius: 10,
              background: 'rgba(230,57,70,0.12)',
              border: `1px solid ${DANGER}`,
              fontSize: '0.8125rem',
              color: '#F7A6AC',
              lineHeight: 1.6,
            }}
          >
            <strong style={{ color: '#FFCDD1' }}>Never paste secrets into browser UI.</strong>{' '}
            Machine credentials are managed via secure environment variables, not this demo page.{' '}
            <strong style={{ color: '#FFCDD1' }}>Production PHI remains NO-GO until hardening and legal review are complete.</strong>
          </div>
        </div>

        {/* 1. Tenant provisioning */}
        <ConsolePanel
          title="Tenant Provisioning"
          warning="Tenant provisioning is disabled — demo only. Real tenant provisioning requires backend admin endpoint and audit trail."
        >
          <DisabledField label="Clinic name" placeholder="e.g. Hausarzt Praxis Wien" />
          <DisabledField label="Clinic ID (auto-generated)" placeholder="uuid auto-assigned" />
          <DisabledField label="Specialty" placeholder="e.g. Innere Medizin" />
          <DisabledField label="Contact email" placeholder="praxis@example.at" />
          <DisabledButton label="Provision tenant" />
        </ConsolePanel>

        {/* 2. Clinic ID scope injection */}
        <ConsolePanel
          title="Clinic ID Scope Injection"
          warning="Scope injection is not wired — demo only. Clinic scope is set via authenticated session, not this panel. Cross-tenant scope overrides are a safety-sensitive operation."
        >
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.875rem' }}>
            Current session scope:{' '}
            <code style={{ fontFamily: 'ui-monospace, monospace', fontSize: '0.8rem', background: 'rgba(0,128,128,0.15)', color: '#7FD4D4', padding: '1px 6px', borderRadius: 4 }}>
              1a5bbc75-c1b0-4488-94aa-64b3f1c50056
            </code>{' '}
            (Staging Fake Clinic — display identity resolved via tenantDisplay helper)
          </p>
          <DisabledField label="Override clinic_id" placeholder="uuid — leave blank to use session default" />
          <DisabledButton label="Apply scope" />
        </ConsolePanel>

        {/* 3. Vapi machine credential binding */}
        <ConsolePanel
          title="Vapi Machine Credential Binding"
          warning="Never paste secrets into browser UI. Machine credentials are managed via secure environment variables, not this demo page."
        >
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.875rem' }}>
            Vapi machine credentials are injected at deploy time via secure environment
            variables. This panel is a placeholder — no token fields carry real values and
            no credential input is accepted.
          </p>
          <DisabledField label="Vapi machine credential ID" placeholder="Set via environment variable — not entered here" />
          <DisabledField label="Vapi phone number" placeholder="Set via environment variable — not entered here" />
          <DisabledButton label="Bind credential" />
        </ConsolePanel>

        {/* 4. Environment checklist — labels only, never values */}
        <ConsolePanel title="Environment Checklist">
          <p style={{ fontSize: '0.75rem', color: MUTED, marginBottom: '0.625rem' }}>
            Required environment variables — shown as labels only. Values are never displayed here.
          </p>
          {ENV_CHECKLIST.map((name) => (
            <div
              key={name}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.625rem',
                padding: '0.45rem 0',
                borderBottom: `1px solid ${EDGE}`,
                fontSize: '0.8125rem',
              }}
            >
              <span style={{ fontFamily: 'ui-monospace, monospace', color: '#7FD4D4', flex: 1 }}>{name}</span>
              <span style={{ fontSize: '0.675rem', color: MUTED, letterSpacing: '0.04em' }}>value hidden — managed in deployment environment</span>
            </div>
          ))}
          <div style={{ marginTop: '0.875rem' }}>
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
          </div>
        </ConsolePanel>

        {/* 5. Pilot request review */}
        <ConsolePanel title="Pilot Request Review">
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.875rem' }}>
            Review submitted clinic pilot requests, update their review status, and track
            the onboarding workflow. No tenant is activated by any status change.
            Production PHI remains NO-GO.
          </p>
          <a
            href="/developer-console/onboarding-requests"
            style={{
              display: 'inline-block',
              fontSize: '0.8125rem',
              fontWeight: 700,
              padding: '0.5rem 1.25rem',
              borderRadius: 7,
              border: `1px solid ${ACCENT}`,
              background: 'rgba(0,128,128,0.15)',
              color: ACCENT,
              textDecoration: 'none',
            }}
          >
            Review onboarding requests →
          </a>
        </ConsolePanel>

        {/* 6. Tenant language settings */}
        <ConsolePanel title="Tenant Language Settings">
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.875rem' }}>
            Read and update German-first language settings for a provisioned clinic shell.
            Controls clinic UI language, patient language fallback, and future Vapi assistant
            language mode. No PHI. No Vapi credentials. No production activation.
          </p>
          <a
            href="/developer-console/language-settings"
            style={{
              display: 'inline-block',
              fontSize: '0.8125rem',
              fontWeight: 700,
              padding: '0.5rem 1.25rem',
              borderRadius: 7,
              border: `1px solid ${ACCENT}`,
              background: 'rgba(0,128,128,0.15)',
              color: ACCENT,
              textDecoration: 'none',
            }}
          >
            Configure language settings →
          </a>
        </ConsolePanel>

        {/* 7. Vapi assistant config preview */}
        <ConsolePanel title="Vapi Assistant Config Preview">
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.875rem' }}>
            Preview the generated Vapi assistant configuration pack for a provisioned clinic shell.
            Inspect German/English prompts, required capture fields, tool schema, and safety rules.
            Read-only preview. No live Vapi binding. No secrets. No PHI. No production activation.
          </p>
          <a
            href="/developer-console/vapi-config"
            style={{
              display: 'inline-block',
              fontSize: '0.8125rem',
              fontWeight: 700,
              padding: '0.5rem 1.25rem',
              borderRadius: 7,
              border: `1px solid ${ACCENT}`,
              background: 'rgba(0,128,128,0.15)',
              color: ACCENT,
              textDecoration: 'none',
            }}
          >
            Preview Vapi config →
          </a>
        </ConsolePanel>

        {/* 8. Vapi binding metadata — Sprint 19 / Module 146 */}
        <ConsolePanel title="Vapi Binding Metadata">
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.875rem' }}>
            Create and view Vapi binding metadata for a clinic using secret reference names only.
            Internal secret-reference configuration — no Vapi secrets are stored or transmitted,
            no live Vapi API calls, no PHI, no production activation. Production PHI remains NO-GO.
          </p>
          <a
            href="/developer-console/vapi-bindings"
            style={{
              display: 'inline-block',
              fontSize: '0.8125rem',
              fontWeight: 700,
              padding: '0.5rem 1.25rem',
              borderRadius: 7,
              border: `1px solid ${ACCENT}`,
              background: 'rgba(0,128,128,0.15)',
              color: ACCENT,
              textDecoration: 'none',
            }}
          >
            Manage binding metadata →
          </a>
        </ConsolePanel>

        {/* 9. Patient Intake Links — Sprint 20 / Module 151 */}
        <ConsolePanel title="Patient Intake Links">
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.875rem' }}>
            Generate demo-only tokenized intake links for consent-first patient questionnaires.
            Demo tokens only. No real patient data. No PHI. No patient history writes.
            No AI structuring. intake_url shown once only after creation.
            Production PHI remains NO-GO.
          </p>
          <a
            href="/developer-console/intake-links"
            style={{
              display: 'inline-block',
              fontSize: '0.8125rem',
              fontWeight: 700,
              padding: '0.5rem 1.25rem',
              borderRadius: 7,
              border: `1px solid ${ACCENT}`,
              background: 'rgba(0,128,128,0.15)',
              color: ACCENT,
              textDecoration: 'none',
            }}
          >
            Manage intake links →
          </a>
        </ConsolePanel>

        {/* 10. Patient History Review — Sprint 20 / Module 154 */}
        <ConsolePanel title="Patient History Review">
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.875rem' }}>
            Review unverified AI-structured history proposals and merge only after staff approval.
            Doctor-reviewed merge queue. No auto-approval. No diagnosis. No medical advice. No PHI.
            Production PHI remains NO-GO.
          </p>
          <a
            href="/developer-console/history-review"
            style={{
              display: 'inline-block',
              fontSize: '0.8125rem',
              fontWeight: 700,
              padding: '0.5rem 1.25rem',
              borderRadius: 7,
              border: `1px solid ${ACCENT}`,
              background: 'rgba(0,128,128,0.15)',
              color: ACCENT,
              textDecoration: 'none',
            }}
          >
            Review history proposals →
          </a>
        </ConsolePanel>

        {/* 11. Longitudinal Patient Timeline — Sprint 20 / Module 156 */}
        <ConsolePanel title="Longitudinal Patient Timeline">
          <p style={{ fontSize: '0.8125rem', color: MUTED, marginBottom: '0.875rem' }}>
            View approved history, intake events, consent events, and unverified proposals in one patient timeline.
            Approved entries only after staff review. Delta view shows changes since last visit.
            No diagnosis, no medical advice, no PHI. Production PHI remains NO-GO.
          </p>
          <a
            href="/developer-console/patient-timeline"
            style={{
              display: 'inline-block',
              fontSize: '0.8125rem',
              fontWeight: 700,
              padding: '0.5rem 1.25rem',
              borderRadius: 7,
              border: `1px solid ${ACCENT}`,
              background: 'rgba(0,128,128,0.15)',
              color: ACCENT,
              textDecoration: 'none',
            }}
          >
            Open patient timeline →
          </a>
        </ConsolePanel>

        {/* 12. Safety guardrails */}
        <ConsolePanel title="Safety Guardrails">
          {[
            'Never paste secrets into browser UI.',
            'Production PHI remains NO-GO until hardening and legal review are complete.',
            'Real tenant provisioning requires backend admin endpoint and audit trail.',
            'This staging environment uses synthetic fake data only — no real patient records.',
            'No DSGVO / Austrian data protection compliance claim is made at this stage.',
            'Machine credentials are managed via secure environment variables, not this demo page.',
          ].map((line, i, arr) => (
            <div
              key={i}
              style={{
                display: 'flex',
                gap: '0.625rem',
                alignItems: 'flex-start',
                padding: '0.5rem 0',
                borderBottom: i < arr.length - 1 ? `1px solid ${EDGE}` : 'none',
                fontSize: '0.8125rem',
                color: TEXT,
              }}
            >
              <span style={{ flexShrink: 0, color: DANGER, fontWeight: 700 }}>!</span>
              <span>{line}</span>
            </div>
          ))}
          {/* Legacy Safety Boundary label preserved */}
          <span className="sr-only">Safety Boundary</span>
        </ConsolePanel>

        {/* Back link */}
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <a href="/dashboard" style={{ fontSize: '0.8125rem', color: MUTED, textDecoration: 'none' }}>
            ← Back to dashboard
          </a>
        </div>
      </div>
    </div>
  )
}
