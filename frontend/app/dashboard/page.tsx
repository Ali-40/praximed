// Dashboard page — PraxisMed Sprint 8 / Module 66
// Placeholder only. Data fetching and auth guards are wired in Module 67.

const SECTIONS = [
  {
    key: 'appointments',
    label: 'Appointments',
    description: 'View and manage incoming appointment requests.',
  },
  {
    key: 'patients',
    label: 'Patients',
    description: 'Browse and search registered patients.',
  },
  {
    key: 'notifications',
    label: 'Notifications',
    description: 'Review clinic alerts and urgent call notifications.',
  },
  {
    key: 'consultations',
    label: 'Consultations',
    description: 'Access consultation sessions and clinical summaries.',
  },
]

export default function DashboardPage() {
  return (
    <main style={{ minHeight: '100vh', background: 'var(--color-surface)' }}>
      {/* Header */}
      <header
        style={{
          background: '#fff',
          borderBottom: '1px solid var(--color-border)',
          padding: '1rem 2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span style={{ fontWeight: 700, fontSize: '1.25rem', color: 'var(--color-brand)' }}>
          PraxisMed
        </span>
        <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
          Clinic Dashboard
        </span>
      </header>

      {/* Content */}
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem 1rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem' }}>
          Welcome to PraxisMed
        </h2>

        {/* Placeholder section cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: '1rem',
          }}
        >
          {SECTIONS.map((section) => (
            <div
              key={section.key}
              data-section={section.key}
              style={{
                background: '#fff',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius)',
                padding: '1.25rem',
                boxShadow: 'var(--shadow-card)',
                opacity: 0.7,
                cursor: 'not-allowed',
              }}
            >
              <h3 style={{ fontWeight: 600, marginBottom: '0.4rem' }}>{section.label}</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                {section.description}
              </p>
              <span
                style={{
                  display: 'inline-block',
                  marginTop: '0.75rem',
                  fontSize: '0.7rem',
                  background: 'var(--color-border)',
                  borderRadius: 4,
                  padding: '2px 6px',
                  color: 'var(--color-text-muted)',
                }}
              >
                Coming in Module 67
              </span>
            </div>
          ))}
        </div>

        <p style={{ marginTop: '2rem', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
          Data loading and auth guards are wired in Sprint 8 / Module 67.
        </p>
      </div>
    </main>
  )
}
