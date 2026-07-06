// Tenant display helper — PraxisMed
// Sprint 17 / Module 126 foundation · Updated Sprint 18 / Module 126C-FABEL5.
//
// Centralized multi-tenant identity mapping for the dynamic header banner.
// The backend user context currently exposes only clinic_id/role, so the
// staging fallback mapping lives here — do NOT hardcode display names in
// individual pages. Fake-data staging only; no real clinic or patient data.

const STAGING_CLINIC_MAP: Record<string, string> = {
  // Staging fake tenant (demo identity — not a real clinic or doctor)
  '1a5bbc75-c1b0-4488-94aa-64b3f1c50056':
    'Dr. Med. Alexander Huber | Innere Medizin Wien',
}

// Legacy fallback label kept for unknown staging tenants ("Staging Fake Clinic").
const UNKNOWN_TENANT_FALLBACK = 'Staging Fake Clinic'

export function getClinicDisplayName(clinicId: string | null | undefined): string {
  if (!clinicId) return 'Clinic'
  return STAGING_CLINIC_MAP[clinicId] ?? UNKNOWN_TENANT_FALLBACK
}

export function getRoleDisplay(role: string | null | undefined): string {
  if (!role) return ''
  return role.charAt(0).toUpperCase() + role.slice(1)
}
