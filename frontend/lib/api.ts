// API client — PraxisMed Sprint 8 / Module 66
// Set NEXT_PUBLIC_API_BASE_URL in .env.local to point to your backend.
// Falls back to the local dev backend when the env var is not set.

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000'

export { API_BASE_URL }

export async function apiFetch(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<Response> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
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

// Fetches GET /appointment-requests?clinic_id=<clinicId> with a Bearer JWT.
// Returns the requests array from the response body.
export async function fetchAppointmentRequests(
  clinicId: string,
  token: string,
): Promise<AppointmentRequest[]> {
  const resp = await apiFetch(
    `/appointment-requests?clinic_id=${encodeURIComponent(clinicId)}`,
    {},
    token,
  )
  if (!resp.ok) {
    throw new Error(`Failed to load appointment requests (HTTP ${resp.status})`)
  }
  const data = (await resp.json()) as { ok: boolean; requests: AppointmentRequest[] }
  return data.requests ?? []
}
