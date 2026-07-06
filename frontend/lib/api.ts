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
