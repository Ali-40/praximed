const STAGING_CLINIC_MAP: Record<string, string> = {
  '1a5bbc75-c1b0-4488-94aa-64b3f1c50056': 'Staging Fake Clinic',
}

export function getClinicDisplayName(clinicId: string | null | undefined): string {
  if (!clinicId) return 'Clinic'
  return STAGING_CLINIC_MAP[clinicId] ?? 'Staging Fake Clinic'
}

export function getRoleDisplay(role: string | null | undefined): string {
  if (!role) return ''
  return role.charAt(0).toUpperCase() + role.slice(1)
}
