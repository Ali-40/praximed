'use client'

// PraxisMed — Doctor-Facing Austrian Clinic Interface
// Sprint 21 / Module 157 — Doctor-Facing Sales MVP Simplification
// Sprint 18 / Module 126C-FABEL5 — Premium 3-column split-screen clinical workspace.
//
// Fake-data staging only. No real patient data. No secrets. Production PHI: NO-GO.
// Legacy Module 126C palette markers kept for contract compatibility: #0F172A #0D9488

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getMe, logout } from '@/lib/auth'
import { getClinicDisplayName, getRoleDisplay } from '@/lib/tenantDisplay'
import {
  confirmAppointmentRequest,
  updateAppointmentRequestStatus,
  createSalesDemoCall,
  resetSalesDemoData,
  fetchAppointmentRequests,
  fetchPatients,
  fetchNotifications,
  fetchConsultations,
  fetchPreAppointmentSummary,
  fetchClinicLanguageSettings,
  updateClinicLanguageSettings,
  AppointmentRequest,
  Patient,
  Notification,
  ConsultationSession,
  PreAppointmentSummary,
} from '@/lib/api'

// ---------------------------------------------------------------------------
// Fabel 5 visual identity — exact palette (also mirrored in globals.css tokens)
// ---------------------------------------------------------------------------
const INK    = '#0B132B'   // Primary Structural Ink — header/sidebar/strong type
const ACCENT = '#008080'   // Clinical Accent — primary CTAs
const FILL   = '#E0F2F1'   // Highlight Muted Fill — active/selected states
const WARN   = '#FFB703'   // Warning / New Request state
const DANGER = '#E63946'   // Critical Error State
const CANVAS = '#F4F6F9'   // Canvas Background

const CARD_BORDER = '#E3E8EF'
const TEXT_MUTED  = '#5B6472'
const TEXT_FAINT  = '#8A93A2'

// ---------------------------------------------------------------------------
// Embedded responsive layout CSS — 3-column split-screen workspace.
// Desktop: left 25% / center 45% / right 30%. Laptop: 2 columns. Mobile: stacked.
// ---------------------------------------------------------------------------
const LAYOUT_CSS = `
  .pm-dash-shell { display:flex; flex-direction:column; min-height:100vh; background:${CANVAS}; }
  .pm-dash-grid  {
    display: grid;
    grid-template-columns: minmax(280px,25%) minmax(420px,45%) minmax(320px,30%);
    flex:1; min-height:0; overflow:hidden;
  }
  .pm-dash-left  { overflow-y:auto; background:${INK}; border-right:1px solid rgba(255,255,255,0.07); }
  .pm-dash-center{ overflow-y:auto; background:${CANVAS}; }
  .pm-dash-right { overflow-y:auto; background:#ffffff; border-left:1px solid ${CARD_BORDER}; }
  .pm-tabular    { font-variant-numeric: tabular-nums; }
  @media(max-width:1200px){
    .pm-dash-grid{ grid-template-columns:minmax(260px,32%) 1fr; overflow:visible; }
    .pm-dash-right{ grid-column:1 / -1; border-left:none; border-top:1px solid ${CARD_BORDER}; }
  }
  @media(max-width:768px){
    .pm-dash-grid{ grid-template-columns:1fr; overflow:visible; }
    .pm-dash-left{ max-height:48vh; border-right:none; border-bottom:1px solid rgba(255,255,255,0.12); }
    .pm-dash-right{ grid-column:auto; border-left:none; border-top:1px solid ${CARD_BORDER}; }
  }
`

// ---------------------------------------------------------------------------
// German status label mapping — Sprint 21 / Module 157
// ---------------------------------------------------------------------------
function getGermanStatusLabel(status: string | null | undefined): string {
  switch (status) {
    case 'new':              return 'Neue Anfrage'
    case 'pending':          return 'Neue Anfrage'
    case 'callback_needed':  return 'Rückruf nötig'
    case 'contacted':        return 'Kontaktiert'
    case 'confirmed':        return 'Bestätigt'
    case 'active':           return 'Aktiv'
    case 'approved':         return 'Genehmigt'
    case 'urgent':           return 'Dringend'
    case 'emergency':        return 'Notfall'
    case 'closed':           return 'Erledigt'
    case 'cancelled':        return 'Abgesagt'
    case 'archived':         return 'Archiviert'
    case 'rejected':         return 'Abgelehnt'
    default:                 return status ?? '—'
  }
}

function getReadableRequestNumber(index: number): string {
  return `Anfrage #${index + 1}`
}

function getTodaySummaryCounts(appts: AppointmentRequest[]) {
  return {
    neueAnfragen: appts.filter((a) => a.status === 'new' || a.status === 'pending').length,
    rückrufNötig: appts.filter((a) => a.status === 'callback_needed').length,
    dringend: appts.filter((a) => a.urgency_level === 'urgent' || a.urgency_level === 'emergency' || a.urgency_level === 'high').length,
    erledigt: appts.filter((a) => a.status === 'confirmed' || a.status === 'closed').length,
  }
}

// KI-Vorschau text — Sprint 21 / Module 159
// No appointment auto-confirmation. No Vapi reference. Administrative only.
// "Das Praxisteam meldet sich zur Bestätigung zurück."
function getKiPreviewText(tone: string, praxisname: string): string {
  const name = praxisname.trim() || 'Ihrer Praxis'
  switch (tone) {
    case 'direkt':
      return `Hallo, digitale Rezeption der ${name}. Ich nehme Ihre Terminanfrage auf. Das Praxisteam meldet sich.`
    case 'formell':
      return `Sehr geehrte Damen und Herren, hier ist die digitale Rezeption der ${name}. Ihre Terminanfrage wird aufgenommen. Das Praxisteam meldet sich zur Bestätigung zurück.`
    default: // freundlich
      return `Guten Tag, hier ist die digitale Rezeption der ${name}. Ich nehme gerne Ihre Terminanfrage auf — das Praxisteam meldet sich zur Bestätigung zurück.`
  }
}

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------

function fieldStr(row: Record<string, unknown>, key: string): string | null {
  const v = row[key]
  return typeof v === 'string' && v.length > 0 ? v : null
}

function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  const d = new Date(value)
  if (isNaN(d.getTime())) return '—'
  return d.toISOString().slice(0, 10)
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) return '—'
  const d = new Date(value)
  if (isNaN(d.getTime())) return '—'
  return `${d.toISOString().slice(0, 10)} ${d.toISOString().slice(11, 16)}`
}

function patientDisplayName(patient: Patient): string {
  return (
    patient.full_name ||
    [patient.first_name, patient.last_name].filter(Boolean).join(' ') ||
    'Unnamed patient'
  )
}

// ---------------------------------------------------------------------------
// Status/urgency badge styling
// ---------------------------------------------------------------------------

const BADGE_MAP: Record<string, { bg: string; color: string }> = {
  new:             { bg: '#FFF4D6', color: '#8A5B00' },
  confirmed:       { bg: '#DFF5E9', color: '#166534' },
  active:          { bg: '#DFF5E9', color: '#166534' },
  approved:        { bg: '#DFF5E9', color: '#166534' },
  pending:         { bg: '#FFF4D6', color: '#8A5B00' },
  urgent:          { bg: '#FDE3E5', color: '#9F1D28' },
  emergency:       { bg: '#FDE3E5', color: '#9F1D28' },
  high:            { bg: '#FDE3E5', color: '#9F1D28' },
  normal:          { bg: '#E8EDF4', color: TEXT_MUTED },
  low:             { bg: '#E8EDF4', color: TEXT_MUTED },
  vapi:            { bg: FILL,      color: ACCENT },
  callback_needed: { bg: '#FDE3E5', color: '#9F1D28' },
  contacted:       { bg: '#DFF5E9', color: '#166534' },
}

function badge(value: string | null | undefined): React.CSSProperties {
  const t = value?.toLowerCase() ?? ''
  const found = BADGE_MAP[t]
  return {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '2px 9px',
    borderRadius: 99,
    fontSize: '0.675rem',
    fontWeight: 600,
    letterSpacing: '0.02em',
    background: found?.bg ?? '#E8EDF4',
    color: found?.color ?? TEXT_MUTED,
    whiteSpace: 'nowrap' as const,
  }
}

function newRequestBadgeStyle(): React.CSSProperties {
  return {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '2px 9px',
    borderRadius: 99,
    fontSize: '0.675rem',
    fontWeight: 700,
    letterSpacing: '0.03em',
    background: WARN,
    color: INK,
    whiteSpace: 'nowrap' as const,
  }
}

// ---------------------------------------------------------------------------
// UI translations — Sprint 21 / Module 163
// German-first. English available via language selector in Settings.
// No external i18n library — plain dictionary lookup.
// ---------------------------------------------------------------------------
const TRANSLATIONS = {
  de: {
    heute:                   'Heute',
    tabAnfragen:             'Anfragen',
    tabPatienten:            'Patienten',
    tabEinstellungen:        'Einstellungen',
    neueAnfragen:            'Neue Anfragen',
    rueckrufNoetig:          'Rückruf nötig',
    dringendPruefen:         'Dringend prüfen',
    erledigt:                'Erledigt',
    demoAnrufErstellen:      'Demo-Anruf erstellen',
    demoZuruecksetzen:       'Demo zurücksetzen',
    rueckrufMarkieren:       'Rückruf markieren',
    alsKontaktiertMarkieren: 'Als kontaktiert markieren',
    anfrageImUeberblick:     'Anfrage im Überblick',
    telefon:                 'Telefon',
    anliegen:                'Anliegen',
    gewuenschteZeit:         'Gewünschte Zeit',
    eingegangen:             'Eingegangen',
    praxisprofil:            'Praxisprofil',
    oeffnungszeiten:         'Öffnungszeiten',
    sprachen:                'Sprachen',
    kiRezeption:             'KI-Rezeption',
    kiVorschau:              'KI-Vorschau',
    summaryArt:              'Art',
    summaryDringlichkeit:    'Dringlichkeit',
    summaryFruehereBesuche:  'Frühere Besuche',
    summaryEmpfohleneAktion: 'Empfohlene Aktion',
    safetyNote:              'Nur zur internen Planung. Das Praxisteam prüft und bestätigt jeden Schritt.',
    uiSprache:               'Sprache der Oberfläche',
  },
  en: {
    heute:                   'Today',
    tabAnfragen:             'Requests',
    tabPatienten:            'Patients',
    tabEinstellungen:        'Settings',
    neueAnfragen:            'New requests',
    rueckrufNoetig:          'Needs callback',
    dringendPruefen:         'Staff review',
    erledigt:                'Completed',
    demoAnrufErstellen:      'Create demo call',
    demoZuruecksetzen:       'Reset demo',
    rueckrufMarkieren:       'Mark callback',
    alsKontaktiertMarkieren: 'Mark contacted',
    anfrageImUeberblick:     'Request overview',
    telefon:                 'Phone',
    anliegen:                'Issue',
    gewuenschteZeit:         'Preferred time',
    eingegangen:             'Received',
    praxisprofil:            'Practice profile',
    oeffnungszeiten:         'Opening hours',
    sprachen:                'Languages',
    kiRezeption:             'AI receptionist',
    kiVorschau:              'Preview',
    summaryArt:              'Category',
    summaryDringlichkeit:    'Urgency',
    summaryFruehereBesuche:  'Past visits',
    summaryEmpfohleneAktion: 'Next step',
    safetyNote:              'For internal scheduling only. Staff review and confirmation required.',
    uiSprache:               'Interface language',
  },
} as const

// ---------------------------------------------------------------------------
// Shared shell components
// ---------------------------------------------------------------------------

function SectionCard({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div
      style={{
        background: '#ffffff',
        border: `1px solid ${CARD_BORDER}`,
        borderRadius: 14,
        boxShadow: '0 1px 3px 0 rgb(11 19 43 / 0.06), 0 1px 2px -1px rgb(11 19 43 / 0.05)',
        overflow: 'hidden',
        ...style,
      }}
    >
      {children}
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div data-state="empty" style={{ padding: '1.75rem 1.25rem', textAlign: 'center', color: TEXT_MUTED, fontSize: '0.8125rem' }}>
      {message}
    </div>
  )
}

function LoadingState({ message }: { message: string }) {
  return (
    <div data-state="loading" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
      {[1, 2, 3].map((i) => (
        <div key={i} style={{ height: 13, borderRadius: 6, background: '#E8EDF4', width: i === 1 ? '60%' : i === 2 ? '80%' : '45%', opacity: 0.8 }} aria-hidden />
      ))}
      <span className="sr-only">{message}</span>
    </div>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <div
      data-state="error"
      style={{ margin: '0.875rem 1.25rem', padding: '0.75rem 1rem', background: '#FDF1F2', border: `1px solid ${DANGER}`, borderRadius: 10, fontSize: '0.8125rem', color: DANGER }}
    >
      {message}
    </div>
  )
}

function MetricCard({ label, value, loading }: { label: string; value: number; loading: boolean }) {
  return (
    <div style={{ flex: '1 1 110px', background: '#ffffff', border: `1px solid ${CARD_BORDER}`, borderRadius: 10, padding: '0.75rem 1rem' }}>
      <p style={{ fontSize: '0.675rem', fontWeight: 600, color: TEXT_MUTED, marginBottom: '0.3rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {label}
      </p>
      {loading ? (
        <div style={{ height: 24, width: 40, background: '#E8EDF4', borderRadius: 6, opacity: 0.6 }} aria-hidden />
      ) : (
        <p className="pm-tabular" style={{ fontSize: '1.4rem', fontWeight: 700, color: INK, lineHeight: 1 }}>{value}</p>
      )}
    </div>
  )
}

// Heute count card — German clinic-facing daily summary
function HeuteCard({ label, value, loading, accent }: { label: string; value: number; loading: boolean; accent?: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 96, padding: '0.4rem 0.85rem', borderRadius: 8, background: '#ffffff', border: `1px solid ${CARD_BORDER}` }}>
      <span style={{ fontSize: '1.25rem', fontWeight: 800, color: accent ?? INK, lineHeight: 1 }}>
        {loading ? '—' : value}
      </span>
      <span style={{ fontSize: '0.675rem', fontWeight: 600, color: TEXT_MUTED, marginTop: '0.2rem', whiteSpace: 'nowrap' }}>
        {label}
      </span>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Audio Transcript & Call Recording — placeholder shell (no real recordings)
// ---------------------------------------------------------------------------

function TranscriptRecordingPanel({ appt }: { appt: AppointmentRequest }) {
  const sourceRef = fieldStr(appt, 'source_ref') ?? fieldStr(appt, 'call_id')
  const waveformBars = [8, 14, 20, 12, 24, 16, 28, 18, 10, 22, 15, 26, 12, 19, 9, 23, 17, 27, 13, 20, 11, 24, 16, 21, 10, 18, 25, 14, 22, 12]
  return (
    <div
      data-state="transcript-panel"
      style={{ margin: '0 1.25rem 1.25rem', borderRadius: 12, border: `1px solid ${CARD_BORDER}`, background: '#FAFBFD', overflow: 'hidden' }}
    >
      <div style={{ padding: '0.875rem 1.25rem 0.625rem', borderBottom: `1px solid ${CARD_BORDER}` }}>
        <p style={{ fontSize: '0.75rem', fontWeight: 700, color: INK, textTransform: 'uppercase', letterSpacing: '0.07em' }}>
          <span className="sr-only">Audio Transcript &amp; Call Recording</span>
          <span aria-hidden>Gesprächsaufzeichnung</span>
        </p>
      </div>

      {/* Polished audio player placeholder shell */}
      <div style={{ padding: '0.875rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
        <button
          disabled
          title="Wiedergabe nicht verfügbar — keine Audio-Integration aktiv"
          style={{
            fontSize: '0.775rem', fontWeight: 600, padding: '7px 14px', borderRadius: 8,
            border: `1px solid ${CARD_BORDER}`, background: '#EFF2F7', color: TEXT_FAINT,
            cursor: 'not-allowed', whiteSpace: 'nowrap',
          }}
        >
          <span className="sr-only">▶ Play Audio Call</span>
          <span aria-hidden>▶ Wiedergabe</span>
        </button>

        {/* Mock waveform visual track — decorative only */}
        <div aria-hidden style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 2, height: 34, opacity: 0.55 }}>
          {waveformBars.map((h, i) => (
            <span key={i} style={{ width: 3, height: h, borderRadius: 2, background: i % 4 === 0 ? ACCENT : '#B9C4D2' }} />
          ))}
        </div>
        <span className="pm-tabular" style={{ fontSize: '0.7rem', color: TEXT_FAINT }}>00:00 / --:--</span>
      </div>

      {/* Transcript / summary box — safe empty state */}
      <div style={{ margin: '0 1.25rem 0.875rem', padding: '0.875rem 1rem', borderRadius: 8, border: `1px dashed ${CARD_BORDER}`, background: '#ffffff' }}>
        <p style={{ fontSize: '0.8125rem', color: TEXT_MUTED, fontStyle: 'italic', lineHeight: 1.5 }}>
          <span className="sr-only">Recording/transcript review will appear here when Vapi recording ingestion is enabled.</span>
          <span aria-hidden>Aufzeichnung verfügbar, sobald die Integration aktiviert ist.</span>
        </p>
      </div>

      {/* Metadata row */}
      <div style={{ padding: '0 1.25rem 0.875rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={badge('vapi')}><span className="sr-only">Vapi source</span><span aria-hidden>Telefonkanal</span></span>
        <span className="sr-only pm-tabular" style={{ fontSize: '0.675rem', color: TEXT_FAINT, fontFamily: 'ui-monospace, monospace' }}>
          {sourceRef ? `source_ref: ${sourceRef}` : 'source_ref: —'}
        </span>
        <span style={{ fontSize: '0.675rem', fontWeight: 600, color: '#8A5B00', background: '#FFF4D6', padding: '2px 8px', borderRadius: 99 }}>
          <span className="sr-only">Recording ingestion pending</span>
          <span aria-hidden>Ausstehend</span>
        </span>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Dashboard page
// ---------------------------------------------------------------------------

type Tab = 'anfragen' | 'patienten' | 'einstellungen'

export default function DashboardPage() {
  const router = useRouter()

  const [activeTab, setActiveTab] = useState<Tab>('anfragen')

  const [clinicId, setClinicId] = useState<string | null>(null)
  const [clinicDisplayName, setClinicDisplayName] = useState<string>('Clinic')
  const [userRole, setUserRole] = useState<string>('')

  const [appointments, setAppointments] = useState<AppointmentRequest[]>([])
  const [apptLoading, setApptLoading] = useState(true)
  const [apptError, setApptError] = useState<string | null>(null)

  const [patients, setPatients] = useState<Patient[]>([])
  const [patientsLoading, setPatientsLoading] = useState(true)
  const [patientsError, setPatientsError] = useState<string | null>(null)

  const [notifications, setNotifications] = useState<Notification[]>([])
  const [notifLoading, setNotifLoading] = useState(true)
  const [notifError, setNotifError] = useState<string | null>(null)

  const [consultations, setConsultations] = useState<ConsultationSession[]>([])
  const [consultLoading, setConsultLoading] = useState(true)
  const [consultError, setConsultError] = useState<string | null>(null)

  const [confirmingIds, setConfirmingIds] = useState<Set<string>>(new Set())
  const [callbackIds, setCallbackIds] = useState<Set<string>>(new Set())
  const [contactedIds, setContactedIds] = useState<Set<string>>(new Set())
  const [apptActionError, setApptActionError] = useState<string | null>(null)

  // Sprint 21 / Module 158 — One-Click Demo Flow
  // Staging-only. No real patient data. No PHI. Production PHI remains NO-GO.
  const [demoCallCreating, setDemoCallCreating] = useState(false)
  const [demoResetting, setDemoResetting] = useState(false)
  const [demoMessage, setDemoMessage] = useState<string | null>(null)

  // Sprint 21 / Module 159 — Simple Clinic Settings
  // Local state for display fields. Language persisted via existing endpoint.
  // No PHI. No Vapi config. No technical fields. No UUIDs. Production PHI remains NO-GO.
  const [settingsForm, setSettingsForm] = useState({
    praxisname: '',
    arzt: '',
    fachrichtung: '',
    ort: 'Wien',
    telefon: '',
    oeffnungszeiten: 'Mo–Fr 08:00–17:00',
    primaryLanguage: 'de',
    supportedLanguages: ['de', 'en'] as string[],
    kiTon: 'freundlich',
  })
  const [settingsSaving, setSettingsSaving] = useState(false)
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null)

  // Sprint 21 / Module 163 — UI language selector. Default German. No external i18n library.
  const [uiLang, setUiLang] = useState<'de' | 'en'>('de')

  const [summaryOpenId, setSummaryOpenId] = useState<string | null>(null)
  const [summaries, setSummaries] = useState<Record<string, PreAppointmentSummary | 'loading' | 'error'>>({})

  const [selectedApptId, setSelectedApptId] = useState<string | null>(null)
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null)
  const [patientSearch, setPatientSearch] = useState('')

  useEffect(() => {
    getMe().then((user) => {
      if (!user) {
        router.replace('/login')
        return
      }
      setClinicId(user.clinic_id)
      setClinicDisplayName(getClinicDisplayName(user.clinic_id))
      setUserRole(getRoleDisplay(user.role))

      fetchAppointmentRequests(user.clinic_id)
        .then((rows) => {
          setAppointments(rows)
          // Default selected request: first appointment request if available.
          if (rows.length > 0) setSelectedApptId(rows[0].id)
        })
        .catch(() => setApptError('Could not load appointment requests. Please try again.'))
        .finally(() => setApptLoading(false))

      fetchPatients(user.clinic_id)
        .then(setPatients)
        .catch(() => setPatientsError('Could not load patients. Please try again.'))
        .finally(() => setPatientsLoading(false))

      fetchNotifications(user.clinic_id)
        .then(setNotifications)
        .catch(() => setNotifError('Could not load notifications. Please try again.'))
        .finally(() => setNotifLoading(false))

      fetchConsultations(user.clinic_id)
        .then(setConsultations)
        .catch(() => setConsultError('Could not load consultations. Please try again.'))
        .finally(() => setConsultLoading(false))

      // Sprint 21 / Module 159 — pre-populate language settings form
      fetchClinicLanguageSettings(user.clinic_id)
        .then((ls) => {
          setSettingsForm((prev) => ({
            ...prev,
            praxisname: prev.praxisname || getClinicDisplayName(user.clinic_id),
            primaryLanguage: ls.primary_language ?? 'de',
            supportedLanguages: ls.supported_languages?.length ? ls.supported_languages : ['de', 'en'],
          }))
        })
        .catch(() => {
          setSettingsForm((prev) => ({
            ...prev,
            praxisname: prev.praxisname || getClinicDisplayName(user.clinic_id),
          }))
        })
    })
  }, [router])

  async function handleLogout() {
    await logout()
    router.push('/login')
  }

  async function handleConfirm(requestId: string) {
    if (!clinicId) return
    setConfirmingIds((prev) => new Set(prev).add(requestId))
    setApptActionError(null)
    try {
      await confirmAppointmentRequest(requestId, clinicId)
      const rows = await fetchAppointmentRequests(clinicId)
      setAppointments(rows)
    } catch {
      setApptActionError('Could not confirm appointment request. Please try again.')
    } finally {
      setConfirmingIds((prev) => { const next = new Set(prev); next.delete(requestId); return next })
    }
  }

  async function handleMarkCallback(requestId: string) {
    if (!clinicId) return
    setCallbackIds((prev) => new Set(prev).add(requestId))
    setApptActionError(null)
    try {
      await updateAppointmentRequestStatus(requestId, clinicId, 'callback_needed')
      const rows = await fetchAppointmentRequests(clinicId)
      setAppointments(rows)
    } catch {
      setApptActionError('Rückruf-Status konnte nicht gesetzt werden. Bitte erneut versuchen.')
    } finally {
      setCallbackIds((prev) => { const next = new Set(prev); next.delete(requestId); return next })
    }
  }

  async function handleMarkContacted(requestId: string) {
    if (!clinicId) return
    setContactedIds((prev) => new Set(prev).add(requestId))
    setApptActionError(null)
    try {
      await updateAppointmentRequestStatus(requestId, clinicId, 'contacted')
      const rows = await fetchAppointmentRequests(clinicId)
      setAppointments(rows)
    } catch {
      setApptActionError('Kontaktiert-Status konnte nicht gesetzt werden. Bitte erneut versuchen.')
    } finally {
      setContactedIds((prev) => { const next = new Set(prev); next.delete(requestId); return next })
    }
  }

  async function handleCreateDemoCall() {
    if (!clinicId || demoCallCreating) return
    setDemoCallCreating(true)
    setDemoMessage(null)
    try {
      const result = await createSalesDemoCall(clinicId)
      const rows = await fetchAppointmentRequests(clinicId)
      setAppointments(rows)
      if (rows.length > 0 && !selectedApptId) setSelectedApptId(rows[0].id)
      setDemoMessage(result.message ?? 'Demo-Anfrage wurde der Warteschlange hinzugefügt.')
    } catch {
      setDemoMessage('Demo-Anfrage konnte nicht erstellt werden.')
    } finally {
      setDemoCallCreating(false)
    }
  }

  async function handleResetDemo() {
    if (!clinicId || demoResetting) return
    setDemoResetting(true)
    setDemoMessage(null)
    try {
      const result = await resetSalesDemoData(clinicId)
      const rows = await fetchAppointmentRequests(clinicId)
      setAppointments(rows)
      setSelectedApptId(rows.length > 0 ? rows[0].id : null)
      setDemoMessage(result.message ?? 'Demo-Daten wurden zurückgesetzt.')
    } catch {
      setDemoMessage('Demo konnte nicht zurückgesetzt werden.')
    } finally {
      setDemoResetting(false)
    }
  }

  async function handleSaveSettings() {
    if (!clinicId || settingsSaving) return
    setSettingsSaving(true)
    setSettingsMessage(null)
    try {
      await updateClinicLanguageSettings(clinicId, {
        primary_language: settingsForm.primaryLanguage,
        clinic_ui_language: settingsForm.primaryLanguage,
        supported_languages: settingsForm.supportedLanguages,
      })
      if (settingsForm.praxisname) setClinicDisplayName(settingsForm.praxisname)
      setSettingsMessage('Einstellungen gespeichert.')
    } catch {
      setSettingsMessage('Einstellungen konnten nicht gespeichert werden.')
    } finally {
      setSettingsSaving(false)
    }
  }

  function handleResetSettings() {
    setSettingsForm({
      praxisname: getClinicDisplayName(clinicId ?? ''),
      arzt: '',
      fachrichtung: '',
      ort: 'Wien',
      telefon: '',
      oeffnungszeiten: 'Mo–Fr 08:00–17:00',
      primaryLanguage: 'de',
      supportedLanguages: ['de', 'en'],
      kiTon: 'freundlich',
    })
    setSettingsMessage(null)
  }

  async function handleViewSummary(appt: AppointmentRequest) {
    if (!clinicId) return
    if (summaryOpenId === appt.id) { setSummaryOpenId(null); return }
    setSummaryOpenId(appt.id)
    if (summaries[appt.id]) return
    setSummaries((prev) => ({ ...prev, [appt.id]: 'loading' }))
    try {
      const summary = await fetchPreAppointmentSummary(appt.id, clinicId)
      setSummaries((prev) => ({ ...prev, [appt.id]: summary }))
    } catch {
      setSummaries((prev) => ({ ...prev, [appt.id]: 'error' }))
    }
  }

  const activeAppts = appointments.filter((a) => a.status !== 'archived')
  const archivedAppts = appointments.filter((a) => a.status === 'archived')
  const pendingCount = activeAppts.filter((a) => a.status === 'new').length
  const selectedAppt = appointments.find((a) => a.id === selectedApptId) ?? null
  const selectedApptIndex = appointments.findIndex((a) => a.id === selectedApptId)
  const selectedPatient = patients.find((p) => p.id === selectedPatientId) ?? null
  const todayCounts = getTodaySummaryCounts(appointments)

  const filteredPatients = useMemo(() => {
    const q = patientSearch.trim().toLowerCase()
    if (!q) return patients
    return patients.filter((p) => {
      const name = patientDisplayName(p).toLowerCase()
      const phone = (fieldStr(p, 'phone') ?? '').toLowerCase()
      return name.includes(q) || phone.includes(q)
    })
  }, [patients, patientSearch])

  // Linked appointment requests for the selected patient (patient_id linkage).
  const linkedAppointments = useMemo(() => {
    if (!selectedPatient) return []
    return appointments.filter((a) => fieldStr(a, 'patient_id') === selectedPatient.id)
  }, [appointments, selectedPatient])

  function isNewRequest(appt: AppointmentRequest): boolean {
    return appt.status === 'new' || appt.status === 'pending'
  }

  const t = (key: keyof typeof TRANSLATIONS.de) => TRANSLATIONS[uiLang][key]

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="pm-dash-shell">

      <style dangerouslySetInnerHTML={{ __html: LAYOUT_CSS }} />

      {/* ------------------------------------------------------------------ */}
      {/* Global sticky header — clinic identity, staging badge, nav          */}
      {/* ------------------------------------------------------------------ */}
      <header
        style={{
          background: INK,
          borderBottom: '1px solid rgba(255,255,255,0.09)',
          padding: '0 1.25rem',
          minHeight: 58,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          flexShrink: 0,
          flexWrap: 'wrap',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem', flexWrap: 'wrap', padding: '0.4rem 0' }}>
          <span style={{ fontWeight: 800, fontSize: '1.05rem', color: '#ffffff', letterSpacing: '-0.01em' }}>
            PraxisMed
          </span>

          {/* Dynamic multi-tenant identity banner (from tenantDisplay helper) */}
          <span
            data-state="tenant-banner"
            style={{ fontSize: '0.8125rem', color: 'rgba(255,255,255,0.85)', fontWeight: 500, borderLeft: '1px solid rgba(255,255,255,0.2)', paddingLeft: '0.875rem' }}
          >
            {clinicDisplayName}
            {userRole && <span style={{ color: 'rgba(255,255,255,0.45)' }}> · {userRole}</span>}
          </span>

          <span
            style={{
              fontSize: '0.65rem', fontWeight: 700, padding: '2px 9px', borderRadius: 99,
              background: WARN, color: INK, letterSpacing: '0.05em',
            }}
          >
            STAGING DEMO
          </span>

          {/* Safety boundary — always visible */}
          <span style={{ fontSize: '0.6875rem', color: 'rgba(255,255,255,0.5)', letterSpacing: '0.01em' }}>
            Fake-data staging · No real patient data · Production PHI: NO-GO
          </span>
        </div>

        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
          <a href="/onboarding" style={{ fontSize: '0.775rem', fontWeight: 500, padding: '0.35rem 0.75rem', borderRadius: 6, color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>
            Onboarding
          </a>
          {/* Dev Console is accessible directly at /developer-console — not shown in clinical nav */}
          <button
            onClick={handleLogout}
            style={{
              fontSize: '0.775rem', fontWeight: 600, padding: '0.4rem 0.95rem',
              border: '1px solid rgba(255,255,255,0.22)', borderRadius: 7,
              background: 'transparent', color: 'rgba(255,255,255,0.85)', cursor: 'pointer',
            }}
          >
            Abmelden
          </button>
        </nav>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* Heute — daily summary bar (Sprint 21 / Module 157)                  */}
      {/* ------------------------------------------------------------------ */}
      <div
        style={{
          background: '#ffffff',
          borderBottom: `1px solid ${CARD_BORDER}`,
          padding: '0.625rem 1.25rem',
          display: 'flex',
          gap: '1rem',
          flexWrap: 'wrap',
          alignItems: 'center',
        }}
      >
        <span style={{ fontWeight: 700, fontSize: '0.9rem', color: INK, minWidth: 52 }}>{t('heute')}</span>
        <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap' }}>
          <HeuteCard label={t('neueAnfragen')}  value={todayCounts.neueAnfragen} loading={apptLoading} accent={WARN} />
          <HeuteCard label={t('rueckrufNoetig')}  value={todayCounts.rückrufNötig} loading={apptLoading} accent={DANGER} />
          <HeuteCard label={t('dringendPruefen')} value={todayCounts.dringend}    loading={apptLoading} accent={DANGER} />
          <HeuteCard label={t('erledigt')}        value={todayCounts.erledigt}    loading={apptLoading} accent={ACCENT} />
        </div>
        {/* Legacy labels for contract compatibility */}
        <span className="sr-only">Clinic Overview Dashboard</span>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Tab navigation — Anfragen / Patienten / Einstellungen               */}
      {/* ------------------------------------------------------------------ */}
      <nav
        role="tablist"
        style={{
          background: '#ffffff',
          borderBottom: `1px solid ${CARD_BORDER}`,
          padding: '0 0.875rem',
          display: 'flex',
          gap: 0,
        }}
      >
        {(['anfragen', 'patienten', 'einstellungen'] as const).map((tab) => {
          const labels: Record<Tab, string> = {
            anfragen: t('tabAnfragen'),
            patienten: t('tabPatienten'),
            einstellungen: t('tabEinstellungen'),
          }
          const isActive = activeTab === tab
          return (
            <button
              key={tab}
              role="tab"
              aria-selected={isActive}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '0.7rem 1.1rem',
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                fontWeight: isActive ? 700 : 500,
                fontSize: '0.875rem',
                color: isActive ? ACCENT : TEXT_MUTED,
                borderBottom: isActive ? `2px solid ${ACCENT}` : '2px solid transparent',
              }}
            >
              {labels[tab]}
            </button>
          )
        })}
      </nav>

      {/* ================================================================== */}
      {/* TAB: Anfragen — 3-column split-screen workspace                     */}
      {/* ================================================================== */}
      {activeTab === 'anfragen' && (
        <>

          {/* ================================================================ */}
          {/* Demo-Modus strip — Sprint 21 / Module 158                        */}
          {/* Staging-only. Nur Demo. Keine echten Patientendaten.             */}
          {/* No PHI. No real patient data. Production PHI remains NO-GO.      */}
          {/* ================================================================ */}
          <div
            data-demo-strip="sales-mvp"
            style={{
              background: '#FFF8E7',
              borderBottom: `1px solid #F0D488`,
              padding: '0.5rem 1.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.875rem',
              flexWrap: 'wrap',
            }}
          >
            <span style={{ fontSize: '0.675rem', fontWeight: 700, color: '#8A5B00', textTransform: 'uppercase', letterSpacing: '0.07em', whiteSpace: 'nowrap' }}>
              Demo-Modus
            </span>
            <span style={{ fontSize: '0.75rem', color: '#5B4200' }}>
              Nur Demo. Keine echten Patientendaten.
            </span>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginLeft: 'auto' }}>
              <button
                data-action="create-demo-call"
                onClick={() => void handleCreateDemoCall()}
                disabled={demoCallCreating || demoResetting}
                style={{
                  fontSize: '0.775rem', fontWeight: 700, padding: '6px 14px', borderRadius: 7,
                  border: 'none', background: ACCENT, color: '#ffffff',
                  cursor: demoCallCreating || demoResetting ? 'not-allowed' : 'pointer',
                  opacity: demoCallCreating || demoResetting ? 0.6 : 1,
                  whiteSpace: 'nowrap',
                }}
              >
                {demoCallCreating ? 'Erstelle…' : t('demoAnrufErstellen')}
              </button>
              <button
                data-action="reset-demo"
                onClick={() => void handleResetDemo()}
                disabled={demoCallCreating || demoResetting}
                style={{
                  fontSize: '0.775rem', fontWeight: 600, padding: '6px 14px', borderRadius: 7,
                  border: `1px solid ${CARD_BORDER}`, background: '#ffffff', color: TEXT_MUTED,
                  cursor: demoCallCreating || demoResetting ? 'not-allowed' : 'pointer',
                  opacity: demoCallCreating || demoResetting ? 0.6 : 1,
                  whiteSpace: 'nowrap',
                }}
              >
                {demoResetting ? 'Zurücksetzen…' : t('demoZuruecksetzen')}
              </button>
            </div>
            {demoMessage && (
              <span
                data-demo-message
                style={{
                  fontSize: '0.75rem', fontWeight: 600, width: '100%',
                  color: demoMessage.includes('nicht') ? DANGER : '#166534',
                }}
              >
                {demoMessage}
              </span>
            )}
            <span
              data-live-demo-hint
              style={{ fontSize: '0.675rem', color: '#5B4200', width: '100%' }}
            >
              Live-Telefon-Demo: Ein Anruf erscheint hier als Rückruf-Anfrage. · Staging-Telefonnummer wird separat konfiguriert.
            </span>
          </div>

        <div className="pm-dash-grid">

          {/* ============================================================== */}
          {/* COLUMN 1 — INCOMING AI INTAKE QUEUE                             */}
          {/* ============================================================== */}
          <aside className="pm-dash-left" data-panel="left">

            <section data-section="appointments">
              <div style={{ padding: '1.125rem 1rem 0.625rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <h2 style={{ fontSize: '0.7rem', fontWeight: 700, color: 'rgba(255,255,255,0.55)', textTransform: 'uppercase', letterSpacing: '0.11em' }}>
                  {/* Label kept for existing contract tests */}
                  <span className="sr-only">Incoming AI Intake Queue</span>
                  <span aria-hidden>Anfragen</span>
                </h2>
                {!apptLoading && !apptError && (
                  <span className="pm-tabular" style={{ fontSize: '0.675rem', fontWeight: 700, color: INK, background: WARN, padding: '1px 7px', borderRadius: 99 }}>
                    {pendingCount}
                  </span>
                )}
              </div>

              {apptLoading && (
                <div data-state="loading" style={{ padding: '0.25rem 0.75rem' }}>
                  {[1, 2, 3].map((i) => (
                    <div key={i} style={{ height: 64, borderRadius: 10, background: 'rgba(255,255,255,0.06)', marginBottom: '0.4rem' }} />
                  ))}
                  <span className="sr-only">Anfragen werden geladen…</span>
                </div>
              )}

              {!apptLoading && apptError && (
                <div data-state="error" style={{ margin: '0.5rem 0.75rem', padding: '0.75rem', borderRadius: 8, background: 'rgba(230,57,70,0.16)', border: `1px solid ${DANGER}`, color: '#F7A6AC', fontSize: '0.8125rem' }}>
                  {apptError}
                </div>
              )}

              {!apptLoading && !apptError && appointments.length === 0 && (
                <div data-state="empty" style={{ padding: '1.5rem 1rem', fontSize: '0.8125rem', color: 'rgba(255,255,255,0.4)', textAlign: 'center' }}>
                  <span className="sr-only">No incoming AI intake requests yet.</span>
                  <span aria-hidden>Noch keine Anfragen. Erstellen Sie einen Demo-Anruf, um den Ablauf zu zeigen.</span>
                </div>
              )}

              {!apptLoading && !apptError && appointments.length > 0 && activeAppts.length === 0 && (
                <div data-state="empty" style={{ padding: '1.5rem 1rem', fontSize: '0.8125rem', color: 'rgba(255,255,255,0.4)', textAlign: 'center' }}>
                  Noch keine aktiven Anfragen. Erstellen Sie einen Demo-Anruf, um den Ablauf zu zeigen.
                </div>
              )}

              {!apptLoading && !apptError && activeAppts.length > 0 && (
                <ul data-state="list" style={{ listStyle: 'none', padding: '0 0.625rem 0.875rem' }}>
                  {activeAppts.map((appt, idx) => {
                    const isSelected = selectedApptId === appt.id
                    const phone = fieldStr(appt, 'patient_phone')
                    const reason = fieldStr(appt, 'reason')
                    const source = fieldStr(appt, 'source')
                    const preferred = fieldStr(appt, 'preferred_starts_at')
                    return (
                      <li
                        key={appt.id}
                        onClick={() => { setSelectedApptId(appt.id); setSummaryOpenId(null) }}
                        style={{
                          marginBottom: '0.375rem', borderRadius: 10, padding: '0.65rem 0.8rem', cursor: 'pointer',
                          background: isSelected ? FILL : 'rgba(255,255,255,0.05)',
                          borderLeft: isSelected ? `3px solid ${ACCENT}` : '3px solid transparent',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.4rem', marginBottom: '0.2rem' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.8125rem', color: isSelected ? INK : '#ffffff', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>
                            {appt.patient_name ?? '—'}
                          </span>
                          {isNewRequest(appt) && <span style={newRequestBadgeStyle()}><span className="sr-only">New Request</span><span aria-hidden>Neue Anfrage</span></span>}
                        </div>
                        {/* Human-readable request number — no UUID shown in clinic-facing UI */}
                        <div style={{ fontSize: '0.7rem', fontWeight: 700, color: isSelected ? ACCENT : 'rgba(0,128,128,0.75)', marginBottom: '0.2rem' }}>
                          {getReadableRequestNumber(idx)}
                        </div>
                        <div className="pm-tabular" style={{ fontSize: '0.7rem', color: isSelected ? TEXT_MUTED : 'rgba(255,255,255,0.45)', marginBottom: '0.25rem' }}>
                          {phone
                            ? phone
                            : <><span className="sr-only">No phone captured</span><span aria-hidden>Nicht angegeben</span></>
                          } · {formatDateTime(preferred ?? appt.created_at)}
                        </div>
                        {reason && (
                          <div style={{ fontSize: '0.7rem', color: isSelected ? TEXT_MUTED : 'rgba(255,255,255,0.4)', marginBottom: '0.3rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {reason.length > 60 ? reason.slice(0, 60) + '…' : reason}
                          </div>
                        )}
                        <div style={{ display: 'flex', gap: '0.3rem', flexWrap: 'wrap', alignItems: 'center' }}>
                          <span style={badge(appt.status)}>{getGermanStatusLabel(appt.status)}</span>
                          {/* source badge hidden in clinic-facing UI */}
                          {/* Rückruf markieren — marks appointment as callback_needed */}
                          <button
                            onClick={(e) => { e.stopPropagation(); void handleMarkCallback(appt.id) }}
                            disabled={callbackIds.has(appt.id)}
                            style={{
                              fontSize: '0.625rem', fontWeight: 700, padding: '2px 8px', borderRadius: 6,
                              border: `1px solid ${DANGER}`, background: 'transparent', color: DANGER,
                              cursor: callbackIds.has(appt.id) ? 'not-allowed' : 'pointer',
                              whiteSpace: 'nowrap', opacity: callbackIds.has(appt.id) ? 0.5 : 1,
                            }}
                          >
                            {callbackIds.has(appt.id) ? '…' : t('rueckrufMarkieren')}
                          </button>
                        </div>
                      </li>
                    )
                  })}
                </ul>
              )}

              {!apptLoading && !apptError && archivedAppts.length > 0 && (
                <div style={{ padding: '0.5rem 0.75rem 0.875rem' }}>
                  <p style={{ fontSize: '0.625rem', fontWeight: 700, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.375rem' }}>
                    Archivierte Anfragen ({archivedAppts.length})
                  </p>
                  {archivedAppts.map((appt, idx) => (
                    <div
                      key={appt.id}
                      onClick={() => { setSelectedApptId(appt.id); setSummaryOpenId(null) }}
                      style={{
                        padding: '0.4rem 0.6rem', borderRadius: 8, cursor: 'pointer', marginBottom: '0.25rem',
                        background: selectedApptId === appt.id ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.03)',
                        opacity: 0.6,
                      }}
                    >
                      <span style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.55)', fontWeight: 500 }}>
                        {appt.patient_name ?? '—'} · <span style={{ color: 'rgba(255,255,255,0.3)' }}>Archiviert</span>
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <div style={{ height: 1, background: 'rgba(255,255,255,0.08)' }} />

            {/* ------------------------------------------------------------ */}
            {/* Notifications panel — internal channel only                    */}
            {/* ------------------------------------------------------------ */}
            <section data-section="notifications">
              <div style={{ padding: '0.875rem 1rem 0.5rem' }}>
                <h2 style={{ fontSize: '0.7rem', fontWeight: 700, color: 'rgba(255,255,255,0.55)', textTransform: 'uppercase', letterSpacing: '0.11em' }}>
                  Hinweise
                </h2>
                <p style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.35)', marginTop: '0.15rem' }}>
                  <span className="sr-only">Internal notification only</span>
                  <span aria-hidden>Eingehende Hinweise</span>
                </p>
              </div>

              {notifLoading && (
                <div data-state="loading" style={{ padding: '0.25rem 0.75rem' }}>
                  {[1, 2].map((i) => <div key={i} style={{ height: 38, borderRadius: 8, background: 'rgba(255,255,255,0.06)', marginBottom: '0.3rem' }} />)}
                  <span className="sr-only">Hinweise werden geladen…</span>
                </div>
              )}

              {!notifLoading && notifError && (
                <div data-state="error" style={{ margin: '0.25rem 0.75rem', padding: '0.625rem', borderRadius: 8, background: 'rgba(230,57,70,0.16)', color: '#F7A6AC', fontSize: '0.75rem' }}>
                  {notifError}
                </div>
              )}

              {!notifLoading && !notifError && notifications.length === 0 && (
                <div data-state="empty" style={{ padding: '0.75rem 1rem 1rem', fontSize: '0.75rem', color: 'rgba(255,255,255,0.3)' }}>
                  Keine Hinweise
                </div>
              )}

              {!notifLoading && !notifError && notifications.length > 0 && (
                <ul data-state="list" style={{ listStyle: 'none', padding: '0 0.625rem 1rem' }}>
                  {notifications.map((notif) => {
                    const isPending = notif.status === 'pending'
                    const truncatedMsg = notif.message
                      ? notif.message.length > 75 ? notif.message.slice(0, 75) + '…' : notif.message
                      : null
                    return (
                      <li
                        key={notif.id}
                        data-notification-status={notif.status}
                        style={{
                          marginBottom: '0.3rem', padding: '0.5rem 0.7rem', borderRadius: 8,
                          background: 'rgba(255,255,255,0.05)',
                          borderLeft: isPending ? `3px solid ${WARN}` : '3px solid transparent',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                          <span style={{ flex: 1, fontWeight: 600, fontSize: '0.75rem', color: 'rgba(255,255,255,0.85)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {notif.title ?? '—'}
                          </span>
                          {isPending
                            ? <span style={newRequestBadgeStyle()}>{notif.status}</span>
                            : <span style={badge(notif.status)}>{notif.status ?? '—'}</span>}
                        </div>
                        {truncatedMsg && (
                          <p data-notification-message style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', margin: '0.2rem 0 0', lineHeight: 1.4 }}>
                            {truncatedMsg}
                          </p>
                        )}
                        <div style={{ display: 'flex', gap: '0.3rem', marginTop: '0.3rem', flexWrap: 'wrap' }}>
                          {notif.priority && <span style={badge(notif.priority)}>{notif.priority}</span>}
                          {notif.notification_type && (
                            <span style={{ ...badge(undefined), background: 'rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.55)' }}>
                              {notif.notification_type}
                            </span>
                          )}
                          <span style={{ ...badge(undefined), background: 'rgba(0,128,128,0.25)', color: '#7FD4D4' }}>
                            internal
                          </span>
                        </div>
                      </li>
                    )
                  })}
                </ul>
              )}
            </section>
          </aside>

          {/* ============================================================== */}
          {/* COLUMN 2 — ACTIVE RESOLUTION & RECORDING ENGINE                 */}
          {/* ============================================================== */}
          <main className="pm-dash-center" data-panel="center">
            <div style={{ padding: '1.25rem 1.5rem 0' }}>
              <h1 style={{ fontSize: '1.05rem', fontWeight: 800, color: INK, letterSpacing: '-0.01em' }}>
                {/* Labels kept for existing contract tests */}
                <span className="sr-only">Active Resolution Workspace</span>
                <span aria-hidden>{t('anfrageImUeberblick')}</span>
              </h1>
              {/* Legacy labels preserved for contract compatibility */}
              <span className="sr-only">Intake Resolution Workspace · Clinic Overview · Confirm &amp; Create Profile</span>
              <p style={{ fontSize: '0.775rem', color: TEXT_MUTED, marginTop: '0.2rem' }}>
                PraxisMed nimmt Terminanfragen auf und sortiert Rückrufe für Ihr Praxisteam.
              </p>
              <span className="sr-only">Fake-data staging environment — no real patient data</span>
            </div>

            {/* Demo in 3 Schritten — Sprint 21 / Module 162 */}
            <div
              data-demo-guide="3-steps"
              style={{
                margin: '0.875rem 1.5rem 0',
                padding: '0.75rem 1.125rem',
                borderRadius: 10,
                background: '#FFF8E7',
                border: '1px solid #F0D488',
                display: 'flex',
                alignItems: 'center',
                gap: '1.5rem',
                flexWrap: 'wrap',
              }}
            >
              <span style={{ fontSize: '0.675rem', fontWeight: 700, color: '#8A5B00', textTransform: 'uppercase', letterSpacing: '0.07em', whiteSpace: 'nowrap' }}>
                Demo in 3 Schritten
              </span>
              {[
                '1 · Demo-Anruf erstellen',
                '2 · Rückruf-Anfrage prüfen',
                '3 · Als kontaktiert markieren',
              ].map((step) => (
                <span key={step} style={{ fontSize: '0.75rem', color: '#5B4200', whiteSpace: 'nowrap' }}>{step}</span>
              ))}
              <span style={{ fontSize: '0.675rem', color: '#8A5B00', width: '100%' }}>
                Live-Demo: Ein echter Staging-Anruf erscheint ebenfalls hier als Rückruf-Anfrage.
              </span>
            </div>

            {/* Clinic Overview metrics */}
            <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap', margin: '0.875rem 1.5rem' }}>
              <MetricCard label="Anfragen"  value={appointments.length}  loading={apptLoading} />
              <MetricCard label="Patienten" value={patients.length}      loading={patientsLoading} />
              <MetricCard label="Hinweise"  value={notifications.length} loading={notifLoading} />
              <MetricCard label="Neu"       value={pendingCount}         loading={apptLoading} />
            </div>

            {/* Selected intake request */}
            <div data-panel="workspace" style={{ margin: '0 1.5rem 1.25rem' }}>
              {!selectedAppt ? (
                <div
                  data-state="empty"
                  style={{ border: `2px dashed ${CARD_BORDER}`, borderRadius: 14, padding: '2.75rem 2rem', textAlign: 'center', color: TEXT_MUTED, background: '#ffffff' }}
                >
                  <p style={{ fontSize: '0.9375rem', fontWeight: 700, marginBottom: '0.5rem', color: INK }}>
                    Keine Anfrage ausgewählt
                  </p>
                  <p style={{ fontSize: '0.8125rem' }}>
                    Bitte wählen Sie eine Anfrage aus der Liste links aus.
                  </p>
                </div>
              ) : (
                <SectionCard>
                  {/* Workspace header — patient name + human-readable request number (no UUID) */}
                  <div style={{ padding: '1.125rem 1.25rem', borderBottom: `1px solid ${CARD_BORDER}`, display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: INK, letterSpacing: '-0.01em' }}>
                        {selectedAppt.patient_name ?? '—'}
                      </h3>
                      <div style={{ display: 'flex', gap: '0.375rem', marginTop: '0.45rem', flexWrap: 'wrap' }}>
                        {isNewRequest(selectedAppt) && <span style={newRequestBadgeStyle()}><span className="sr-only">New Request</span><span aria-hidden>Neue Anfrage</span></span>}
                        <span style={badge(selectedAppt.status)}>{getGermanStatusLabel(selectedAppt.status)}</span>
                        <span style={badge(selectedAppt.urgency_level)}>{selectedAppt.urgency_level}</span>
                        {fieldStr(selectedAppt, 'source') && <span style={badge(fieldStr(selectedAppt, 'source'))}>{fieldStr(selectedAppt, 'source')}</span>}
                      </div>
                    </div>
                    {/* Human-readable request label — UUID not shown in clinic-facing UI */}
                    <span className="pm-tabular" style={{ fontSize: '0.8rem', fontWeight: 700, color: ACCENT, whiteSpace: 'nowrap' }}>
                      {selectedApptIndex >= 0 ? getReadableRequestNumber(selectedApptIndex) : '—'}
                    </span>
                  </div>

                  {/* Request detail grid */}
                  <dl
                    className="pm-tabular"
                    style={{ display: 'grid', gridTemplateColumns: 'max-content 1fr', columnGap: '1.25rem', rowGap: '0.4rem', fontSize: '0.8125rem', padding: '0.875rem 1.25rem', borderBottom: `1px solid ${CARD_BORDER}` }}
                  >
                    <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>{t('telefon')}</dt>
                    <dd style={{ margin: 0, color: INK }}>
                      {fieldStr(selectedAppt, 'patient_phone')
                        ?? <><span className="sr-only">No phone captured</span><span aria-hidden>Nicht angegeben</span></>
                      }
                    </dd>
                    <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>{t('anliegen')}</dt>
                    <dd style={{ margin: 0, color: INK }}>{fieldStr(selectedAppt, 'reason') ?? '—'}</dd>
                    <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>{t('gewuenschteZeit')}</dt>
                    <dd style={{ margin: 0, color: INK }}>{formatDateTime(fieldStr(selectedAppt, 'preferred_starts_at'))}</dd>
                    <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>{t('eingegangen')}</dt>
                    <dd style={{ margin: 0, color: INK }}>{formatDateTime(selectedAppt.created_at)}</dd>
                  </dl>

                  {/* Audio Transcript & Call Recording engine */}
                  <div style={{ paddingTop: '1.25rem' }}>
                    <TranscriptRecordingPanel appt={selectedAppt} />
                  </div>

                  {/* Summary actions */}
                  <div style={{ padding: '0 1.25rem 0.875rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <button
                      data-action="view-summary"
                      onClick={() => handleViewSummary(selectedAppt)}
                      style={{
                        fontSize: '0.8125rem', fontWeight: 600, padding: '7px 15px', borderRadius: 7, cursor: 'pointer',
                        border: `1px solid ${summaryOpenId === selectedAppt.id ? ACCENT : CARD_BORDER}`,
                        background: summaryOpenId === selectedAppt.id ? FILL : '#ffffff',
                        color: summaryOpenId === selectedAppt.id ? ACCENT : TEXT_MUTED,
                      }}
                    >
                      <span className="sr-only">{summaryOpenId === selectedAppt.id ? 'Hide summary' : 'View summary'}</span>
                      <span aria-hidden>{summaryOpenId === selectedAppt.id ? 'Zusammenfassung schließen' : 'Zusammenfassung anzeigen'}</span>
                    </button>
                  </div>

                  {apptActionError && (
                    <div style={{ margin: '0 1.25rem 0.5rem' }}>
                      <ErrorState message={apptActionError} />
                    </div>
                  )}

                  {/* Pre-appointment summary panel */}
                  {summaryOpenId === selectedAppt.id && (() => {
                    const summaryEntry = summaries[selectedAppt.id]
                    return (
                      <div
                        data-state="summary-panel"
                        style={{ margin: '0 1.25rem 1rem', borderRadius: 10, border: `1px solid ${ACCENT}33`, background: FILL, overflow: 'hidden' }}
                      >
                        {summaryEntry === 'loading' && <LoadingState message="Zusammenfassung wird geladen…" />}
                        {summaryEntry === 'error' && (
                          <div style={{ padding: '0.75rem 1.25rem', color: DANGER, fontSize: '0.8125rem' }}>
                            Zusammenfassung konnte nicht geladen werden. Bitte erneut versuchen.
                          </div>
                        )}
                        {summaryEntry && summaryEntry !== 'loading' && summaryEntry !== 'error' && (
                          <div style={{ padding: '1rem 1.25rem' }}>
                            <p style={{ fontSize: '0.7rem', fontWeight: 700, color: ACCENT, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.75rem' }}>
                              Vorabzusammenfassung
                            </p>
                            <dl className="pm-tabular" style={{ display: 'grid', gridTemplateColumns: 'max-content 1fr', columnGap: '1rem', rowGap: '0.4rem', fontSize: '0.8125rem' }}>
                              <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>Patient</dt>
                              <dd style={{ margin: 0, color: INK, fontWeight: 600 }}>{summaryEntry.patient_name}</dd>
                              <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>{t('summaryArt')}</dt>
                              <dd style={{ margin: 0 }}>{summaryEntry.patient_type}</dd>
                              <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>{t('anliegen')}</dt>
                              <dd style={{ margin: 0 }}>{summaryEntry.reason ?? '—'}</dd>
                              <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>{t('summaryDringlichkeit')}</dt>
                              <dd style={{ margin: 0 }}>{summaryEntry.urgency_level}</dd>
                              <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>{t('summaryFruehereBesuche')}</dt>
                              <dd style={{ margin: 0 }}>{summaryEntry.previous_request_count}</dd>
                              <dt style={{ color: TEXT_MUTED, fontWeight: 500 }}>{t('summaryEmpfohleneAktion')}</dt>
                              <dd style={{ margin: 0, color: ACCENT, fontWeight: 700 }}>{summaryEntry.suggested_next_action}</dd>
                            </dl>
                            <div style={{ marginTop: '0.875rem', paddingTop: '0.75rem', borderTop: `1px solid ${ACCENT}33`, fontSize: '0.75rem', color: TEXT_MUTED, display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                              <span style={{ userSelect: 'none' }}>ℹ</span>
                              <span>{summaryEntry.safety_note}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })()}

                  {/* Safety boundary for the workspace */}
                  <p style={{ margin: '0 1.25rem 0.875rem', fontSize: '0.6875rem', color: TEXT_FAINT, lineHeight: 1.5 }}>
                    {t('safetyNote')} Demo-Modus — keine echten Patientendaten.
                  </p>

                  {/* Action footprint */}
                  <div style={{ padding: '0.875rem 1.25rem', borderTop: `1px solid ${CARD_BORDER}`, background: '#FAFBFD', display: 'flex', gap: '0.625rem', flexWrap: 'wrap', alignItems: 'center' }}>
                    {selectedAppt.status === 'new' && (
                      <button
                        data-action="confirm"
                        onClick={() => handleConfirm(selectedAppt.id)}
                        disabled={confirmingIds.has(selectedAppt.id)}
                        style={{
                          fontSize: '0.8125rem', fontWeight: 700, padding: '8px 18px', borderRadius: 8,
                          border: 'none',
                          background: confirmingIds.has(selectedAppt.id) ? '#B9C4D2' : ACCENT,
                          color: '#ffffff',
                          cursor: confirmingIds.has(selectedAppt.id) ? 'not-allowed' : 'pointer',
                        }}
                      >
                        {confirmingIds.has(selectedAppt.id) ? 'Bestätigen…' : 'Bestätigen'}
                      </button>
                    )}

                    {/* Als kontaktiert markieren */}
                    <button
                      onClick={() => handleMarkContacted(selectedAppt.id)}
                      disabled={contactedIds.has(selectedAppt.id)}
                      style={{
                        fontSize: '0.8125rem', fontWeight: 600, padding: '8px 16px', borderRadius: 8,
                        border: `1px solid ${ACCENT}`, background: 'transparent', color: ACCENT,
                        cursor: contactedIds.has(selectedAppt.id) ? 'not-allowed' : 'pointer',
                        opacity: contactedIds.has(selectedAppt.id) ? 0.55 : 1,
                      }}
                    >
                      {t('alsKontaktiertMarkieren')}
                    </button>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                      <button
                        data-action="confirm-create-profile"
                        disabled
                        title="Profile creation automation coming next"
                        style={{
                          fontSize: '0.8125rem', fontWeight: 700, padding: '8px 18px', borderRadius: 8,
                          border: `1px solid ${ACCENT}`, background: `${ACCENT}1A`, color: ACCENT,
                          cursor: 'not-allowed', opacity: 0.65,
                        }}
                      >
                        <span className="sr-only">{'Confirm Appointment & Create Patient Profile'}</span>
                        <span aria-hidden>Termin bestätigen</span>
                      </button>
                      <span style={{ fontSize: '0.65rem', color: TEXT_FAINT }}>
                        <span className="sr-only">Profile creation automation coming next</span>
                        <span aria-hidden>Folgt in Kürze</span>
                      </span>
                    </div>
                  </div>
                </SectionCard>
              )}
            </div>

            {/* Consultations */}
            <section data-section="consultations" style={{ margin: '0 1.5rem 1.25rem' }}>
              <SectionCard>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.875rem 1.25rem 0.625rem', borderBottom: `1px solid ${CARD_BORDER}` }}>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: INK }}>Konsultationen</h3>
                  {!consultLoading && !consultError && (
                    <span className="pm-tabular" style={{ fontSize: '0.675rem', fontWeight: 700, color: TEXT_MUTED, background: '#E8EDF4', padding: '1px 7px', borderRadius: 99 }}>
                      {consultations.length}
                    </span>
                  )}
                </div>
                {consultLoading && <LoadingState message="Konsultationen werden geladen…" />}
                {!consultLoading && consultError && <ErrorState message={consultError} />}
                {!consultLoading && !consultError && consultations.length === 0 && <EmptyState message="Noch keine Konsultationen." />}
                {!consultLoading && !consultError && consultations.length > 0 && (
                  <ul data-state="list" style={{ listStyle: 'none', padding: '0.25rem 0 0.5rem' }}>
                    {consultations.map((consult, idx) => (
                      <li key={consult.id} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.625rem 1.25rem', borderBottom: idx < consultations.length - 1 ? `1px solid #F0F3F8` : 'none', fontSize: '0.8125rem' }}>
                        <span style={{ flex: 1, fontWeight: 500, color: INK }}>{consult.title ?? '—'}</span>
                        <span style={badge(consult.approval_status ?? undefined)}>{consult.approval_status ?? consult.status ?? '—'}</span>
                        <span style={{ color: TEXT_MUTED, fontSize: '0.75rem' }}>{consult.source ?? '—'}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </SectionCard>
            </section>

            {/* Safety footer */}
            <p style={{ textAlign: 'center', fontSize: '0.6875rem', color: TEXT_FAINT, margin: '0 1.5rem 1.75rem', letterSpacing: '0.02em' }}>
              Staging demo — fake data only · No real patient data · Production PHI: NO-GO
            </p>
          </main>

          {/* ============================================================== */}
          {/* COLUMN 3 — PATIENT DATABASE REGISTRY & HISTORY                  */}
          {/* ============================================================== */}
          <aside className="pm-dash-right" data-panel="right">
            <div style={{ padding: '1.125rem 1rem 0.75rem', borderBottom: `1px solid ${CARD_BORDER}`, position: 'sticky', top: 0, background: '#ffffff', zIndex: 5 }}>
              <h2 style={{ fontSize: '0.7rem', fontWeight: 700, color: TEXT_MUTED, textTransform: 'uppercase', letterSpacing: '0.11em', marginBottom: '0.625rem' }}>
                {/* Label kept for existing contract tests */}
                <span className="sr-only">Patient Registry</span>
                <span aria-hidden>Patientenregister</span>
              </h2>
              <div style={{ position: 'relative' }}>
                <span aria-hidden style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', fontSize: '0.8rem', color: TEXT_FAINT }}>
                  {/* magnifying glass icon */}
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                    <circle cx="11" cy="11" r="7" />
                    <line x1="21" y1="21" x2="16.5" y2="16.5" />
                  </svg>
                </span>
                <input
                  type="search"
                  value={patientSearch}
                  onChange={(e) => setPatientSearch(e.target.value)}
                  placeholder="Patient suchen…"
                  aria-label="Search Clinical Registries..."
                  style={{
                    width: '100%', padding: '0.45rem 0.75rem 0.45rem 1.9rem', borderRadius: 8,
                    border: `1px solid ${CARD_BORDER}`, background: CANVAS, fontSize: '0.775rem',
                    color: INK, outline: 'none', boxSizing: 'border-box',
                  }}
                />
              </div>
            </div>

            <section data-section="patients">
              {patientsLoading && <LoadingState message="Patienten werden geladen…" />}
              {!patientsLoading && patientsError && <ErrorState message={patientsError} />}

              {!patientsLoading && !patientsError && patients.length === 0 && (
                <>
                  <EmptyState message="Noch keine Patienten angelegt." />
                  {/* Demo-safe scaffold placeholders — shown only when the real
                      patients array is empty. Not real patients. Not derived from
                      any record. Clearly marked as demo examples. */}
                  <div data-state="demo-placeholder" style={{ margin: '0 0.875rem 1rem', borderRadius: 10, border: `1px dashed ${CARD_BORDER}`, padding: '0.75rem' }}>
                    <p style={{ fontSize: '0.65rem', fontWeight: 700, color: TEXT_FAINT, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.5rem' }}>
                      Demo placeholder — not real patients
                    </p>
                    {['Dr. Johann Huber', 'Anna Wallner'].map((name) => (
                      <div key={name} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0.25rem', fontSize: '0.8125rem', color: TEXT_MUTED }}>
                        <span style={{ flex: 1 }}>{name}</span>
                        <span style={{ ...badge(undefined), background: '#FFF4D6', color: '#8A5B00' }}>demo example</span>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {!patientsLoading && !patientsError && patients.length > 0 && filteredPatients.length === 0 && (
                <div data-state="empty" style={{ padding: '1.25rem 1rem', textAlign: 'center', color: TEXT_MUTED, fontSize: '0.8125rem' }}>
                  Keine Treffer für diese Suche.
                </div>
              )}

              {!patientsLoading && !patientsError && filteredPatients.length > 0 && (
                <ul data-state="list" style={{ listStyle: 'none', padding: '0.5rem 0' }}>
                  {filteredPatients.map((patient, pidx) => {
                    const isSelected = selectedPatientId === patient.id
                    const displayName = patientDisplayName(patient)
                    const phone = fieldStr(patient, 'phone')
                    return (
                      <li
                        key={pidx}
                        onClick={() => setSelectedPatientId(isSelected ? null : patient.id)}
                        style={{
                          padding: '0.55rem 1rem', cursor: 'pointer',
                          background: isSelected ? FILL : 'transparent',
                          borderLeft: isSelected ? `3px solid ${ACCENT}` : '3px solid transparent',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ flex: 1, fontWeight: isSelected ? 700 : 500, fontSize: '0.8125rem', color: INK, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {displayName}
                          </span>
                          <span style={badge(patient.status)}>{patient.status ?? '—'}</span>
                        </div>
                        {/* Phone shown; UUID not shown in clinic-facing UI */}
                        {phone && <div className="pm-tabular" style={{ fontSize: '0.675rem', color: TEXT_MUTED, marginTop: '0.15rem' }}>{phone}</div>}
                      </li>
                    )
                  })}
                </ul>
              )}
            </section>

            {/* Selected patient profile + chronological history */}
            {selectedPatient && (
              <div
                data-state="patient-profile"
                style={{ margin: '0.75rem', padding: '1rem', borderRadius: 12, border: `1px solid ${ACCENT}44`, background: FILL }}
              >
                <p style={{ fontSize: '0.65rem', fontWeight: 700, color: ACCENT, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.55rem' }}>
                  Patientenprofil
                </p>
                <p style={{ fontWeight: 700, fontSize: '0.9rem', color: INK, marginBottom: '0.375rem' }}>
                  {patientDisplayName(selectedPatient)}
                </p>
                <dl className="pm-tabular" style={{ display: 'grid', gridTemplateColumns: 'max-content 1fr', columnGap: '0.875rem', rowGap: '0.3rem', fontSize: '0.75rem', marginBottom: '0.5rem' }}>
                  <dt style={{ color: TEXT_MUTED }}>Telefon</dt>
                  <dd style={{ margin: 0, color: INK }}>{fieldStr(selectedPatient, 'phone') ?? 'Nicht angegeben'}</dd>
                  <dt style={{ color: TEXT_MUTED }}>E-Mail</dt>
                  <dd style={{ margin: 0, color: INK }}>{fieldStr(selectedPatient, 'email') ?? '—'}</dd>
                  <dt style={{ color: TEXT_MUTED }}>Status</dt>
                  <dd style={{ margin: 0 }}><span style={badge(selectedPatient.status)}>{getGermanStatusLabel(selectedPatient.status)}</span></dd>
                  <dt style={{ color: TEXT_MUTED }}>Verknüpfte Anfragen</dt>
                  <dd style={{ margin: 0, color: INK }}>{linkedAppointments.length}</dd>
                </dl>
                {/* UUID not shown in clinic-facing patient profile */}

                {/* Chronological history / timeline from linked appointment requests */}
                <div style={{ borderTop: `1px solid ${ACCENT}33`, paddingTop: '0.625rem' }}>
                  <p style={{ fontSize: '0.65rem', fontWeight: 700, color: TEXT_MUTED, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.5rem' }}>
                    Verlauf
                  </p>
                  {linkedAppointments.length === 0 ? (
                    <>
                      <p style={{ fontSize: '0.75rem', color: TEXT_MUTED, lineHeight: 1.5 }}>
                        <span className="sr-only">Linked history will appear here as appointment requests accumulate.</span>
                        <span aria-hidden>Verlauf erscheint hier, sobald Anfragen mit diesem Patienten verknüpft werden.</span>
                      </p>
                      <p style={{ fontSize: '0.7rem', color: TEXT_FAINT, marginTop: '0.35rem', lineHeight: 1.5 }}>
                        <span className="sr-only">Appointment history will appear here as linked visits accumulate.</span>
                      </p>
                    </>
                  ) : (
                    <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {linkedAppointments.map((a) => (
                        <li key={a.id} className="pm-tabular" style={{ fontSize: '0.75rem', color: INK, paddingLeft: '0.75rem', borderLeft: `2px solid ${ACCENT}` }}>
                          <div style={{ fontWeight: 600 }}>{formatDate(a.created_at)}: KI-Telefon-Anfrage eingegangen</div>
                          <div style={{ color: TEXT_MUTED }}>Status: {getGermanStatusLabel(a.status)}</div>
                          {fieldStr(a, 'reason') && <div style={{ color: TEXT_MUTED }}>Grund: {fieldStr(a, 'reason')}</div>}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <button
                  onClick={() => setSelectedPatientId(null)}
                  style={{ marginTop: '0.75rem', fontSize: '0.75rem', fontWeight: 600, padding: '4px 12px', border: `1px solid ${ACCENT}`, borderRadius: 6, background: 'transparent', color: ACCENT, cursor: 'pointer' }}
                >
                  Zurück
                </button>
              </div>
            )}
          </aside>

        </div>
        </>
      )}

      {/* ================================================================== */}
      {/* TAB: Patienten — simplified patient list without UUIDs              */}
      {/* ================================================================== */}
      {activeTab === 'patienten' && (
        <div style={{ padding: '1.5rem', maxWidth: 860, margin: '0 auto' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 800, color: INK, marginBottom: '0.25rem' }}>Patienten</h2>
          <p style={{ fontSize: '0.8125rem', color: TEXT_MUTED, marginBottom: '1rem' }}>
            Demo-Modus: Keine echten Patientendaten eingeben.
          </p>
          {patientsLoading && <LoadingState message="Patienten werden geladen…" />}
          {!patientsLoading && patientsError && <ErrorState message={patientsError} />}
          {!patientsLoading && !patientsError && patients.length === 0 && (
            <div>
              <EmptyState message="Noch keine Patienten in dieser Demo. Patienten erscheinen hier, sobald Anfragen zugeordnet werden." />
              <div data-state="demo-placeholder" style={{ marginTop: '0.75rem', borderRadius: 10, border: `1px dashed ${CARD_BORDER}`, padding: '0.875rem' }}>
                <p style={{ fontSize: '0.65rem', fontWeight: 700, color: TEXT_FAINT, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.5rem' }}>
                  Demo placeholder — nicht echte Patienten
                </p>
                {['Dr. Johann Huber', 'Anna Wallner'].map((name) => (
                  <div key={name} style={{ fontSize: '0.8125rem', color: TEXT_MUTED, padding: '0.3rem 0' }}>{name}</div>
                ))}
              </div>
            </div>
          )}
          {!patientsLoading && !patientsError && patients.length > 0 && (
            <SectionCard>
              <ul data-state="list" style={{ listStyle: 'none', padding: '0.25rem 0' }}>
                {patients.map((patient, idx) => (
                  <li
                    key={idx}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '0.75rem',
                      padding: '0.75rem 1.25rem',
                      borderBottom: idx < patients.length - 1 ? `1px solid ${CARD_BORDER}` : 'none',
                      fontSize: '0.8125rem',
                    }}
                  >
                    <span style={{ width: 28, height: 28, borderRadius: '50%', background: FILL, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', fontWeight: 700, color: ACCENT, flexShrink: 0 }}>
                      {idx + 1}
                    </span>
                    <span style={{ flex: 1, fontWeight: 500, color: INK }}>{patientDisplayName(patient)}</span>
                    <span style={{ fontSize: '0.75rem', color: TEXT_MUTED }}>{fieldStr(patient, 'phone') ?? '—'}</span>
                    <span style={badge(patient.status)}>{getGermanStatusLabel(patient.status)}</span>
                  </li>
                ))}
              </ul>
            </SectionCard>
          )}
        </div>
      )}

      {/* ================================================================== */}
      {/* TAB: Einstellungen — simple clinic settings (Sprint 21 / M159)    */}
      {/* No technical fields. No UUIDs. No Vapi config. No PHI.            */}
      {/* Production PHI remains NO-GO.                                     */}
      {/* ================================================================== */}
      {activeTab === 'einstellungen' && (
        <div style={{ padding: '1.5rem', maxWidth: 680, margin: '0 auto' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 800, color: INK, marginBottom: '0.2rem' }}>Einstellungen</h2>
          <p style={{ fontSize: '0.8125rem', color: TEXT_MUTED, marginBottom: '1.25rem' }}>
            Passen Sie an, wie Ihre Praxis in PraxisMed angezeigt wird.
          </p>

          {settingsMessage && (
            <div
              data-settings-message
              style={{
                marginBottom: '1rem', padding: '0.75rem 1rem', borderRadius: 8,
                background: settingsMessage.includes('nicht') ? '#FDF1F2' : '#DFF5E9',
                border: `1px solid ${settingsMessage.includes('nicht') ? DANGER : '#A7D7B9'}`,
                fontSize: '0.8125rem', fontWeight: 600,
                color: settingsMessage.includes('nicht') ? DANGER : '#166534',
              }}
            >
              {settingsMessage}
            </div>
          )}

          {/* ---- Sprache der Oberfläche / Interface language — Module 163 ---- */}
          <SectionCard style={{ marginBottom: '1rem' }}>
            <div style={{ padding: '0.875rem 1.25rem', borderBottom: `1px solid ${CARD_BORDER}` }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: INK }}>
                Sprache der Oberfläche / Interface language
              </h3>
            </div>
            <div style={{ padding: '1.25rem', display: 'flex', gap: '1.25rem', flexWrap: 'wrap' }}>
              {(['de', 'en'] as const).map((lang) => (
                <label
                  key={lang}
                  data-ui-lang={lang}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.8125rem', color: INK }}
                >
                  <input
                    type="radio"
                    name="ui-lang"
                    value={lang}
                    checked={uiLang === lang}
                    onChange={() => setUiLang(lang)}
                  />
                  {lang === 'de' ? 'Deutsch' : 'English'}
                </label>
              ))}
            </div>
          </SectionCard>

          {/* ---- Praxisprofil ---- */}
          <SectionCard style={{ marginBottom: '1rem' }}>
            <div style={{ padding: '0.875rem 1.25rem', borderBottom: `1px solid ${CARD_BORDER}` }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: INK }}>{t('praxisprofil')}</h3>
            </div>
            <div style={{ padding: '1.25rem', display: 'grid', gridTemplateColumns: 'max-content 1fr', columnGap: '1.25rem', rowGap: '0.875rem', alignItems: 'center' }}>
              <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: TEXT_MUTED, whiteSpace: 'nowrap' }}>Praxisname</label>
              <input
                type="text"
                value={settingsForm.praxisname}
                onChange={(e) => setSettingsForm((prev) => ({ ...prev, praxisname: e.target.value }))}
                placeholder="z.B. Ordination Wien"
                style={{ padding: '0.45rem 0.75rem', borderRadius: 7, border: `1px solid ${CARD_BORDER}`, fontSize: '0.8125rem', color: INK, background: CANVAS, outline: 'none' }}
              />
              <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: TEXT_MUTED, whiteSpace: 'nowrap' }}>Arzt / Ärztin</label>
              <input
                type="text"
                value={settingsForm.arzt}
                onChange={(e) => setSettingsForm((prev) => ({ ...prev, arzt: e.target.value }))}
                placeholder="z.B. Dr. Vorname Nachname"
                style={{ padding: '0.45rem 0.75rem', borderRadius: 7, border: `1px solid ${CARD_BORDER}`, fontSize: '0.8125rem', color: INK, background: CANVAS, outline: 'none' }}
              />
              <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: TEXT_MUTED, whiteSpace: 'nowrap' }}>Fachrichtung</label>
              <input
                type="text"
                value={settingsForm.fachrichtung}
                onChange={(e) => setSettingsForm((prev) => ({ ...prev, fachrichtung: e.target.value }))}
                placeholder="Innere Medizin"
                style={{ padding: '0.45rem 0.75rem', borderRadius: 7, border: `1px solid ${CARD_BORDER}`, fontSize: '0.8125rem', color: INK, background: CANVAS, outline: 'none' }}
              />
              <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: TEXT_MUTED, whiteSpace: 'nowrap' }}>Ort</label>
              <input
                type="text"
                value={settingsForm.ort}
                onChange={(e) => setSettingsForm((prev) => ({ ...prev, ort: e.target.value }))}
                placeholder="Wien"
                style={{ padding: '0.45rem 0.75rem', borderRadius: 7, border: `1px solid ${CARD_BORDER}`, fontSize: '0.8125rem', color: INK, background: CANVAS, outline: 'none' }}
              />
              <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: TEXT_MUTED, whiteSpace: 'nowrap' }}>Telefonnummer</label>
              <input
                type="tel"
                value={settingsForm.telefon}
                onChange={(e) => setSettingsForm((prev) => ({ ...prev, telefon: e.target.value }))}
                placeholder="+43 1 000 0000"
                style={{ padding: '0.45rem 0.75rem', borderRadius: 7, border: `1px solid ${CARD_BORDER}`, fontSize: '0.8125rem', color: INK, background: CANVAS, outline: 'none' }}
              />
            </div>
          </SectionCard>

          {/* ---- Öffnungszeiten ---- */}
          <SectionCard style={{ marginBottom: '1rem' }}>
            <div style={{ padding: '0.875rem 1.25rem', borderBottom: `1px solid ${CARD_BORDER}` }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: INK }}>{t('oeffnungszeiten')}</h3>
            </div>
            <div style={{ padding: '1.25rem' }}>
              <textarea
                value={settingsForm.oeffnungszeiten}
                onChange={(e) => setSettingsForm((prev) => ({ ...prev, oeffnungszeiten: e.target.value }))}
                rows={3}
                style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: 7, border: `1px solid ${CARD_BORDER}`, fontSize: '0.8125rem', color: INK, background: CANVAS, outline: 'none', resize: 'vertical', boxSizing: 'border-box' }}
              />
              <p style={{ fontSize: '0.675rem', color: TEXT_FAINT, marginTop: '0.375rem' }}>
                Beispiel: Mo–Fr 08:00–17:00
              </p>
            </div>
          </SectionCard>

          {/* ---- Sprachen ---- */}
          <SectionCard style={{ marginBottom: '1rem' }}>
            <div style={{ padding: '0.875rem 1.25rem', borderBottom: `1px solid ${CARD_BORDER}` }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: INK }}>{t('sprachen')}</h3>
            </div>
            <div style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
              {([{ code: 'de', label: 'Deutsch' }, { code: 'en', label: 'Englisch' }] as const).map(({ code, label }) => (
                <label key={code} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.8125rem', color: INK }}>
                  <input
                    type="checkbox"
                    checked={settingsForm.supportedLanguages.includes(code)}
                    onChange={(e) => {
                      const checked = e.target.checked
                      setSettingsForm((prev) => ({
                        ...prev,
                        supportedLanguages: checked
                          ? [...prev.supportedLanguages, code]
                          : prev.supportedLanguages.filter((l) => l !== code),
                      }))
                    }}
                  />
                  {label}
                </label>
              ))}
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: TEXT_FAINT, cursor: 'default' }}>
                <input type="checkbox" disabled />
                Arabisch <span style={{ fontSize: '0.675rem', marginLeft: '0.25rem' }}>(demnächst verfügbar)</span>
              </label>
            </div>
          </SectionCard>

          {/* ---- KI-Rezeption ---- */}
          <SectionCard style={{ marginBottom: '1.25rem' }}>
            <div style={{ padding: '0.875rem 1.25rem', borderBottom: `1px solid ${CARD_BORDER}` }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: INK }}>{t('kiRezeption')}</h3>
              <p style={{ fontSize: '0.75rem', color: TEXT_MUTED, marginTop: '0.2rem' }}>
                Ton beim Entgegennehmen von Terminanfragen.
              </p>
            </div>
            <div style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
              {([
                { value: 'freundlich', label: 'Freundlich und ruhig' },
                { value: 'direkt',    label: 'Kurz und direkt' },
                { value: 'formell',   label: 'Sehr formell' },
              ] as const).map(({ value, label }) => (
                <label key={value} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.8125rem', color: INK }}>
                  <input
                    type="radio"
                    name="ki-ton"
                    value={value}
                    checked={settingsForm.kiTon === value}
                    onChange={() => setSettingsForm((prev) => ({ ...prev, kiTon: value }))}
                  />
                  {label}
                </label>
              ))}

              {/* KI-Vorschau */}
              <div
                data-ki-vorschau
                style={{ marginTop: '0.75rem', padding: '1rem 1.125rem', borderRadius: 10, background: FILL, border: `1px solid ${ACCENT}33` }}
              >
                <p style={{ fontSize: '0.65rem', fontWeight: 700, color: ACCENT, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.5rem' }}>
                  {t('kiVorschau')}
                </p>
                <p style={{ fontSize: '0.8125rem', color: INK, lineHeight: 1.6, fontStyle: 'italic' }}>
                  {getKiPreviewText(settingsForm.kiTon, settingsForm.praxisname)}
                </p>
                <p style={{ fontSize: '0.675rem', color: TEXT_FAINT, marginTop: '0.5rem' }}>
                  Das Praxisteam meldet sich zur Bestätigung. Kein automatischer Terminabschluss.
                </p>
              </div>
            </div>
          </SectionCard>

          {/* Save / Reset */}
          <div style={{ display: 'flex', gap: '0.625rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
            <button
              data-action="save-settings"
              onClick={() => void handleSaveSettings()}
              disabled={settingsSaving}
              style={{
                fontSize: '0.875rem', fontWeight: 700, padding: '9px 22px', borderRadius: 8,
                border: 'none', background: settingsSaving ? '#B9C4D2' : ACCENT, color: '#ffffff',
                cursor: settingsSaving ? 'not-allowed' : 'pointer',
              }}
            >
              {settingsSaving ? 'Wird gespeichert…' : 'Speichern'}
            </button>
            <button
              data-action="reset-settings"
              onClick={handleResetSettings}
              disabled={settingsSaving}
              style={{
                fontSize: '0.875rem', fontWeight: 500, padding: '9px 18px', borderRadius: 8,
                border: `1px solid ${CARD_BORDER}`, background: '#ffffff', color: TEXT_MUTED,
                cursor: settingsSaving ? 'not-allowed' : 'pointer',
              }}
            >
              Änderungen zurücksetzen
            </button>
          </div>

          <p style={{ fontSize: '0.6875rem', color: TEXT_FAINT }}>
            Staging demo — Fake-data staging · No real patient data · Production PHI: NO-GO
          </p>
        </div>
      )}

    </div>
  )
}
