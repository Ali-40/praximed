// API client — PraxisMed Sprint 8 / Module 66
// Updated Sprint 17 / Module 120 — cookie-based session; credentials: "include" on all fetches.
// Set NEXT_PUBLIC_API_BASE_URL in .env.local to point to your backend.
// Falls back to the local dev backend when the env var is not set.

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000'

export { API_BASE_URL }

export async function apiFetch(
  path: string,
  options: RequestInit = {},
): Promise<Response> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  })
}

// ---------------------------------------------------------------------------
// Appointment requests — Sprint 8 / Module 68
// ---------------------------------------------------------------------------

export interface AppointmentRequest {
  id: string
  patient_name: string | null
  status: string
  urgency_level: string
  action_required: boolean
  created_at: string
  [key: string]: unknown
}

// Fetches GET /appointment-requests?clinic_id=<clinicId> using the session cookie.
// Returns the requests array from the response body.
export async function fetchAppointmentRequests(
  clinicId: string,
): Promise<AppointmentRequest[]> {
  const resp = await apiFetch(
    `/appointment-requests?clinic_id=${encodeURIComponent(clinicId)}`,
  )
  if (!resp.ok) {
    throw new Error(`Failed to load appointment requests (HTTP ${resp.status})`)
  }
  const data = (await resp.json()) as { ok: boolean; requests: AppointmentRequest[] }
  return data.requests ?? []
}

// ---------------------------------------------------------------------------
// Patients — Sprint 8 / Module 69
// ---------------------------------------------------------------------------

export interface Patient {
  id: string
  full_name: string | null      // primary field — backend returns a single full_name column
  first_name: string | null     // kept for defensive compatibility
  last_name: string | null      // kept for defensive compatibility
  status: string
  created_at: string
  [key: string]: unknown
}

// Fetches GET /patients?clinic_id=<clinicId> using the session cookie.
// Returns the patients array from the response body.
export async function fetchPatients(
  clinicId: string,
): Promise<Patient[]> {
  const resp = await apiFetch(
    `/patients?clinic_id=${encodeURIComponent(clinicId)}`,
  )
  if (!resp.ok) {
    throw new Error(`Failed to load patients (HTTP ${resp.status})`)
  }
  const data = (await resp.json()) as { ok: boolean; patients: Patient[] }
  return data.patients ?? []
}

// ---------------------------------------------------------------------------
// Consultations — Sprint 8 / Module 71
// ---------------------------------------------------------------------------

export interface ConsultationSession {
  id: string
  status: string
  approval_status: string | null
  title: string | null
  source: string | null
  created_at: string | null
  [key: string]: unknown
}

// Fetches GET /consultations?clinic_id=<clinicId> using the session cookie.
// Returns the consultations array from the response body.
export async function fetchConsultations(
  clinicId: string,
): Promise<ConsultationSession[]> {
  const resp = await apiFetch(
    `/consultations?clinic_id=${encodeURIComponent(clinicId)}`,
  )
  if (!resp.ok) {
    throw new Error(`Failed to load consultations (HTTP ${resp.status})`)
  }
  const data = (await resp.json()) as { ok: boolean; consultations: ConsultationSession[] }
  return data.consultations ?? []
}

// ---------------------------------------------------------------------------
// Appointment request workflow actions — Sprint 11 / Module 81
// ---------------------------------------------------------------------------

// Confirms an appointment request via PATCH /appointment-requests/{id}/status.
// Throws on non-2xx response.
export async function confirmAppointmentRequest(
  requestId: string,
  clinicId: string,
): Promise<void> {
  const resp = await apiFetch(
    `/appointment-requests/${encodeURIComponent(requestId)}/status?clinic_id=${encodeURIComponent(clinicId)}`,
    {
      method: 'PATCH',
      body: JSON.stringify({ status: 'confirmed', action_required: false }),
    },
  )
  if (!resp.ok) {
    throw new Error(`Failed to confirm appointment request (HTTP ${resp.status})`)
  }
}

// Sprint 21 / Module 157 — Doctor-Facing Sales MVP
// Updates appointment request status via PATCH /appointment-requests/{id}/status.
// Used for callback_needed, contacted, and other workflow transitions.
// Throws on non-2xx response. No PHI. No browser storage.
export async function updateAppointmentRequestStatus(
  requestId: string,
  clinicId: string,
  status: string,
): Promise<void> {
  const resp = await apiFetch(
    `/appointment-requests/${encodeURIComponent(requestId)}/status?clinic_id=${encodeURIComponent(clinicId)}`,
    {
      method: 'PATCH',
      body: JSON.stringify({ status, action_required: status === 'callback_needed' }),
    },
  )
  if (!resp.ok) {
    throw new Error(`Failed to update appointment request status (HTTP ${resp.status})`)
  }
}

// ---------------------------------------------------------------------------
// Notifications — Sprint 8 / Module 70
// ---------------------------------------------------------------------------

export interface Notification {
  id: string
  title: string
  message: string
  notification_type: string
  priority: string
  status: string
  created_at: string | null
  [key: string]: unknown
}

// Fetches GET /notifications?clinic_id=<clinicId> using the session cookie.
// Returns the notifications array from the response body.
export async function fetchNotifications(
  clinicId: string,
): Promise<Notification[]> {
  const resp = await apiFetch(
    `/notifications?clinic_id=${encodeURIComponent(clinicId)}`,
  )
  if (!resp.ok) {
    throw new Error(`Failed to load notifications (HTTP ${resp.status})`)
  }
  const data = (await resp.json()) as { ok: boolean; notifications: Notification[] }
  return data.notifications ?? []
}

// ---------------------------------------------------------------------------
// Clinic onboarding requests — Sprint 19 / Module 134
// ---------------------------------------------------------------------------

export interface ClinicOnboardingRequest {
  id: string
  clinic_name: string
  doctor_name: string
  contact_email: string
  preferred_language: string
  fallback_language: string
  status: string
  created_at: string
  [key: string]: unknown
}

// Fetches GET /clinic-onboarding-requests using the session cookie.
// Protected — requires admin session. Returns the requests array.
export async function fetchClinicOnboardingRequests(): Promise<ClinicOnboardingRequest[]> {
  const resp = await apiFetch('/clinic-onboarding-requests')
  if (!resp.ok) {
    throw new Error(`Failed to load clinic onboarding requests (HTTP ${resp.status})`)
  }
  const data = (await resp.json()) as { ok: boolean; requests: ClinicOnboardingRequest[] }
  return data.requests ?? []
}

// Updates status via PATCH /clinic-onboarding-requests/{requestId}/status.
// Protected — requires admin session. Throws on non-2xx response.
export async function updateClinicOnboardingRequestStatus(
  requestId: string,
  status: string,
): Promise<void> {
  const resp = await apiFetch(
    `/clinic-onboarding-requests/${encodeURIComponent(requestId)}/status`,
    {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    },
  )
  if (!resp.ok) {
    throw new Error(`Failed to update onboarding request status (HTTP ${resp.status})`)
  }
}

export interface ClinicShellProvisionResult {
  ok: boolean
  clinic_id: string
  clinic_name: string
  clinic_slug: string
  preferred_language: string
  production_phi_enabled: boolean
  message: string
  already_provisioned: boolean
}

// Provisions a safe clinic shell via POST /clinic-onboarding-requests/{requestId}/provision-clinic-shell.
// Protected — requires admin session. Only succeeds when request status is pilot_approved.
// production_phi_enabled is always false. No Vapi credentials collected or stored.
export async function provisionClinicShell(
  requestId: string,
): Promise<ClinicShellProvisionResult> {
  const resp = await apiFetch(
    `/clinic-onboarding-requests/${encodeURIComponent(requestId)}/provision-clinic-shell`,
    { method: 'POST' },
  )
  if (!resp.ok) {
    throw new Error(`Failed to provision clinic shell (HTTP ${resp.status})`)
  }
  return (await resp.json()) as ClinicShellProvisionResult
}

// ---------------------------------------------------------------------------
// Clinic language settings — Sprint 19 / Module 139
// ---------------------------------------------------------------------------

export interface ClinicLanguageSettings {
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

export interface ClinicLanguageSettingsUpdatePayload {
  primary_language?: string
  fallback_language?: string
  supported_languages?: string[]
  default_patient_language?: string
  vapi_assistant_language_mode?: string
  clinic_ui_language?: string
}

// Fetches GET /clinics/{clinicId}/language-settings using the session cookie.
// Protected — requires admin session. No PHI. No Vapi credentials.
export async function fetchClinicLanguageSettings(
  clinicId: string,
): Promise<ClinicLanguageSettings> {
  const resp = await apiFetch(`/clinics/${encodeURIComponent(clinicId)}/language-settings`)
  if (!resp.ok) {
    throw new Error(`Failed to load clinic language settings (HTTP ${resp.status})`)
  }
  return (await resp.json()) as ClinicLanguageSettings
}

// Updates language settings via PATCH /clinics/{clinicId}/language-settings.
// Protected — requires admin session. Partial update — only provided fields are changed.
// No PHI. No Vapi credentials. No secrets.
export async function updateClinicLanguageSettings(
  clinicId: string,
  payload: ClinicLanguageSettingsUpdatePayload,
): Promise<ClinicLanguageSettings> {
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/language-settings`,
    {
      method: 'PATCH',
      body: JSON.stringify(payload),
    },
  )
  if (!resp.ok) {
    throw new Error(`Failed to update clinic language settings (HTTP ${resp.status})`)
  }
  return (await resp.json()) as ClinicLanguageSettings
}

// ---------------------------------------------------------------------------
// Vapi assistant config pack — Sprint 19 / Module 142
// ---------------------------------------------------------------------------

export interface VapiAssistantConfigPack {
  clinic_id: string
  clinic_display_name: string
  specialty: string
  city: string
  primary_language: string
  fallback_language: string
  supported_languages: string[]
  vapi_assistant_language_mode: string
  assistant_name: string
  voice_locale_recommendation: string
  first_message_de: string
  first_message_en: string
  system_prompt_de: string
  system_prompt_en: string
  tool_schema: Record<string, unknown>
  required_capture_fields: string[]
  safety_rules: string[]
  escalation_rules: string[]
  forbidden_claims: string[]
  production_phi_enabled: boolean
  recording_ingestion_enabled: boolean
  transcript_ingestion_enabled: boolean
  generated_at: string | null
}

// Fetches GET /clinics/{clinicId}/vapi-assistant-config-pack using the session cookie.
// Protected — requires admin session. No PHI. No Vapi credentials. No secrets.
export async function fetchVapiAssistantConfigPack(
  clinicId: string,
): Promise<VapiAssistantConfigPack> {
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/vapi-assistant-config-pack`,
  )
  if (!resp.ok) {
    throw new Error(`Failed to load Vapi assistant config pack (HTTP ${resp.status})`)
  }
  return (await resp.json()) as VapiAssistantConfigPack
}

// ---------------------------------------------------------------------------
// Clinic Vapi binding metadata — Sprint 19 / Module 146
// Secret reference names only — no actual Vapi secrets are ever sent, stored,
// or returned. No live Vapi API calls. No PHI. Production PHI remains NO-GO.
// All requests use apiFetch (NEXT_PUBLIC_API_BASE_URL + credentials: "include").
// ---------------------------------------------------------------------------

export interface ClinicVapiBinding {
  id: string
  clinic_id: string
  assistant_id: string | null
  phone_number_id: string | null
  vapi_project_id: string | null
  api_key_secret_ref: string        // environment-variable reference name only
  webhook_secret_ref: string        // environment-variable reference name only
  assistant_config_version: string | null
  language_mode: string             // german_first / english_first / bilingual_auto
  status: string                    // draft / configured / disabled / revoked
  created_by_user_id: string | null
  created_at: string
  updated_at: string
  production_phi_enabled: boolean   // always false
}

// Non-throwing result wrapper so admin UI can map 401/403/404/422 states safely.
export interface ClinicVapiBindingResult {
  ok: boolean
  status: number
  binding: ClinicVapiBinding | null
  detail: string | null
}

async function parseVapiBindingResponse(resp: Response): Promise<ClinicVapiBindingResult> {
  let binding: ClinicVapiBinding | null = null
  let detail: string | null = null
  try {
    const data = (await resp.json()) as {
      ok?: boolean
      binding?: ClinicVapiBinding
      detail?: string | Array<{ msg: string }>
    }
    binding = data.binding ?? null
    if (typeof data.detail === 'string') detail = data.detail
    else if (Array.isArray(data.detail)) detail = data.detail.map((d) => d.msg).join(' ')
  } catch {
    // non-JSON body — keep nulls
  }
  return { ok: resp.ok, status: resp.status, binding, detail }
}

// GET /clinics/{clinicId}/vapi-bindings — latest binding metadata (reference names only).
export async function fetchClinicVapiBindings(
  clinicId: string,
): Promise<ClinicVapiBindingResult> {
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/vapi-bindings`,
  )
  return parseVapiBindingResponse(resp)
}

export interface ClinicVapiBindingCreatePayload {
  api_key_secret_ref: string        // env-var reference name label only — never a key value
  webhook_secret_ref: string        // env-var reference name label only — never a secret value
  language_mode: string
}

// POST /clinics/{clinicId}/vapi-bindings — create binding metadata record.
// Reference names only; the backend rejects actual secret values.
export async function createClinicVapiBinding(
  clinicId: string,
  payload: ClinicVapiBindingCreatePayload,
): Promise<ClinicVapiBindingResult> {
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/vapi-bindings`,
    {
      method: 'POST',
      body: JSON.stringify({ clinic_id: clinicId, ...payload }),
    },
  )
  return parseVapiBindingResponse(resp)
}

// PATCH /clinic-vapi-bindings/{bindingId}/status — update binding status.
export async function updateClinicVapiBindingStatus(
  bindingId: string,
  status: string,
): Promise<ClinicVapiBindingResult> {
  const resp = await apiFetch(
    `/clinic-vapi-bindings/${encodeURIComponent(bindingId)}/status`,
    {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    },
  )
  return parseVapiBindingResponse(resp)
}

// ---------------------------------------------------------------------------
// Pre-appointment summary — Sprint 17 / Module 125
// ---------------------------------------------------------------------------

export interface PreAppointmentSummary {
  request_id: string
  clinic_id: string
  patient_name: string
  patient_phone: string | null
  patient_type: string
  previous_request_count: number
  reason: string | null
  preferred_starts_at: string | null
  preferred_ends_at: string | null
  source: string
  status: string
  action_required: boolean
  urgency_level: string
  suggested_next_action: string
  generated_at: string
  safety_note: string
}

// Fetches GET /appointment-requests/{requestId}/pre-appointment-summary?clinic_id=<clinicId>.
// Returns the structured safe summary dict. Never contains diagnosis or medical advice.
export async function fetchPreAppointmentSummary(
  requestId: string,
  clinicId: string,
): Promise<PreAppointmentSummary> {
  const resp = await apiFetch(
    `/appointment-requests/${encodeURIComponent(requestId)}/pre-appointment-summary?clinic_id=${encodeURIComponent(clinicId)}`,
  )
  if (!resp.ok) {
    throw new Error(`Failed to load pre-appointment summary (HTTP ${resp.status})`)
  }
  const data = (await resp.json()) as { ok: boolean; summary: PreAppointmentSummary }
  return data.summary
}

// ---------------------------------------------------------------------------
// Patient Intake Links — Sprint 20 / Module 151
// Protected admin helpers use credentials: "include".
// Public helpers use a plain fetch (no auth cookie).
// Demo tokens only. No real patient data. No PHI. Production PHI remains NO-GO.
// ---------------------------------------------------------------------------

export interface PatientIntakeLink {
  id: string
  clinic_id: string
  patient_id: string | null
  appointment_request_id: string | null
  template_id: string
  token_prefix: string
  status: string
  purpose: string
  language: string
  expires_at: string
  max_submissions: number
  submission_count: number
  synthetic_demo: boolean
  production_phi_enabled: false
  created_by_user_id: string | null
  created_at: string
  updated_at: string
  [key: string]: unknown
}

export interface PatientIntakeSubmission {
  id: string
  intake_link_id: string
  clinic_id: string
  patient_id: string | null
  template_id: string
  consent_event_id: string
  language: string
  answers: Record<string, unknown>
  skipped_questions: string[]
  escalation_matches: string[]
  status: string
  synthetic_demo: boolean
  production_phi_enabled: false
  submitted_at: string
  created_at: string
  [key: string]: unknown
}

export interface PatientIntakeLinkCreateResult {
  ok: boolean
  link?: PatientIntakeLink
  intake_url?: string
  raw_token_shown_once?: boolean
  production_phi_enabled?: false
  message?: string
}

// POST /clinics/{clinicId}/patient-intake-links — admin protected.
export async function createPatientIntakeLink(
  clinicId: string,
  payload: {
    template_id: string
    language?: string
    purpose?: string
    expires_at: string
    patient_id?: string
    appointment_request_id?: string
    max_submissions?: number
  },
): Promise<PatientIntakeLinkCreateResult> {
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/patient-intake-links`,
    { method: 'POST', body: JSON.stringify(payload) },
  )
  return resp.json() as Promise<PatientIntakeLinkCreateResult>
}

// GET /clinics/{clinicId}/patient-intake-links — admin protected.
export async function fetchPatientIntakeLinks(
  clinicId: string,
): Promise<PatientIntakeLink[]> {
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/patient-intake-links`,
  )
  if (!resp.ok) {
    throw new Error(`Failed to load intake links (HTTP ${resp.status})`)
  }
  const data = (await resp.json()) as { ok: boolean; links: PatientIntakeLink[] }
  return data.links ?? []
}

// GET /clinics/{clinicId}/patient-intake-submissions — admin protected.
export async function fetchPatientIntakeSubmissions(
  clinicId: string,
): Promise<PatientIntakeSubmission[]> {
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/patient-intake-submissions`,
  )
  if (!resp.ok) {
    throw new Error(`Failed to load intake submissions (HTTP ${resp.status})`)
  }
  const data = (await resp.json()) as { ok: boolean; submissions: PatientIntakeSubmission[] }
  return data.submissions ?? []
}

// PATCH /patient-intake-links/{linkId}/revoke — admin protected.
export async function revokePatientIntakeLink(
  linkId: string,
): Promise<{ ok: boolean; message?: string }> {
  const resp = await apiFetch(
    `/patient-intake-links/${encodeURIComponent(linkId)}/revoke`,
    { method: 'PATCH', body: JSON.stringify({}) },
  )
  return resp.json() as Promise<{ ok: boolean; message?: string }>
}

// GET /intake/{token} — public demo route, no auth cookie.
export async function fetchPublicIntakeTemplate(
  token: string,
): Promise<{ ok: boolean; template?: unknown; message?: string }> {
  const resp = await fetch(`${API_BASE_URL}/intake/${encodeURIComponent(token)}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!resp.ok) {
    throw new Error(`Intake link error (HTTP ${resp.status})`)
  }
  return resp.json() as Promise<{ ok: boolean; template?: unknown; message?: string }>
}

// POST /intake/{token}/submit — public demo route, no auth cookie.
export async function submitPublicIntake(
  token: string,
  payload: {
    language: string
    answers: Record<string, unknown>
    skipped_questions: string[]
    consent_granted: boolean
    consent_text_version: string
    consent_text_snapshot: string
  },
): Promise<{ ok: boolean; submission_id?: string; consent_event_id?: string; escalation_matches?: string[]; status?: string; message?: string }> {
  const resp = await fetch(`${API_BASE_URL}/intake/${encodeURIComponent(token)}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!resp.ok) {
    throw new Error(`Intake submit error (HTTP ${resp.status})`)
  }
  return resp.json()
}

// ── Patient History Review — Sprint 20 / Module 154 ──────────────────────────
// Protected admin helpers. credentials: "include". No PHI. No secrets.

export async function fetchPatientHistoryReviewQueue(
  clinicId: string,
  filters?: { patientId?: string; historyType?: string; status?: string },
): Promise<unknown[]> {
  const params = new URLSearchParams()
  if (filters?.patientId) params.set('patient_id', filters.patientId)
  if (filters?.historyType) params.set('history_type', filters.historyType)
  if (filters?.status) params.set('status', filters.status)
  const query = params.toString() ? `?${params.toString()}` : ''
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/patient-history-review-queue${query}`,
  )
  if (!resp.ok) throw new Error(`Failed to load review queue (HTTP ${resp.status})`)
  const data = (await resp.json()) as { ok: boolean; proposals: unknown[] }
  return data.proposals ?? []
}

export async function fetchPatientHistoryProposalReview(
  proposalId: string,
  clinicId: string,
): Promise<unknown> {
  const resp = await apiFetch(
    `/patient-history-proposals/${encodeURIComponent(proposalId)}/review?clinic_id=${encodeURIComponent(clinicId)}`,
  )
  if (!resp.ok) throw new Error(`Failed to load proposal review (HTTP ${resp.status})`)
  return resp.json()
}

export async function approveMergePatientHistoryProposal(
  proposalId: string,
  clinicId: string,
  payload: {
    edited_fields: Record<string, unknown>
    edited_fhir_payload?: Record<string, unknown>
    review_note?: string
    confirm_staff_review: boolean
  },
): Promise<{ ok: boolean; merged_history_entry_id?: string; message?: string }> {
  const resp = await apiFetch(
    `/patient-history-proposals/${encodeURIComponent(proposalId)}/approve-merge?clinic_id=${encodeURIComponent(clinicId)}`,
    { method: 'PATCH', body: JSON.stringify(payload) },
  )
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({})) as { detail?: string }
    throw new Error(body.detail ?? `Merge failed (HTTP ${resp.status})`)
  }
  return resp.json() as Promise<{ ok: boolean; merged_history_entry_id?: string; message?: string }>
}

export async function rejectReviewPatientHistoryProposal(
  proposalId: string,
  clinicId: string,
  payload: { rejected_reason?: string; review_note?: string },
): Promise<{ ok: boolean; message?: string }> {
  const resp = await apiFetch(
    `/patient-history-proposals/${encodeURIComponent(proposalId)}/reject-review?clinic_id=${encodeURIComponent(clinicId)}`,
    { method: 'PATCH', body: JSON.stringify(payload) },
  )
  if (!resp.ok) throw new Error(`Reject failed (HTTP ${resp.status})`)
  return resp.json() as Promise<{ ok: boolean; message?: string }>
}

// ---------------------------------------------------------------------------
// Patient Timeline — Sprint 20 / Module 156
// credentials: "include". No browser storage. No token storage.
// ---------------------------------------------------------------------------

export async function fetchPatientTimeline(
  clinicId: string,
  patientId: string,
  options?: { includeUnverified?: boolean; limit?: number },
): Promise<unknown> {
  const params = new URLSearchParams()
  if (options?.includeUnverified !== undefined)
    params.set('include_unverified', String(options.includeUnverified))
  if (options?.limit !== undefined)
    params.set('limit', String(options.limit))
  const query = params.toString() ? `?${params.toString()}` : ''
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/patients/${encodeURIComponent(patientId)}/timeline${query}`,
  )
  if (!resp.ok) throw new Error(`Failed to load patient timeline (HTTP ${resp.status})`)
  return resp.json()
}

export async function fetchPatientTimelineDelta(
  clinicId: string,
  patientId: string,
  options?: { includeUnverified?: boolean },
): Promise<unknown> {
  const params = new URLSearchParams()
  if (options?.includeUnverified !== undefined)
    params.set('include_unverified', String(options.includeUnverified))
  const query = params.toString() ? `?${params.toString()}` : ''
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/patients/${encodeURIComponent(patientId)}/timeline/delta${query}`,
  )
  if (!resp.ok) throw new Error(`Failed to load timeline delta (HTTP ${resp.status})`)
  return resp.json()
}

export async function fetchPatientTimelineDeltaSince(
  clinicId: string,
  patientId: string,
  since: string,
  options?: { includeUnverified?: boolean },
): Promise<unknown> {
  const params = new URLSearchParams({ since })
  if (options?.includeUnverified !== undefined)
    params.set('include_unverified', String(options.includeUnverified))
  const resp = await apiFetch(
    `/clinics/${encodeURIComponent(clinicId)}/patients/${encodeURIComponent(patientId)}/timeline/delta-since?${params.toString()}`,
  )
  if (!resp.ok) throw new Error(`Failed to load timeline delta-since (HTTP ${resp.status})`)
  return resp.json()
}
