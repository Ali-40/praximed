# Sprint 4 / Module 43 — Audit Logging Integration for PHI Mutations

Task scope:
Wire audit logging into human-facing PHI-changing routes.

Purpose:
PraxisMed now has an audit repository and audit logger service.
This module records audit events for important human-facing actions that create,
update, approve, reject, archive, or otherwise mutate patient/clinical/internal records.

This module uses safe audit logging so audit failures do not break the primary business action.

Routes audited:
1. /patients mutation routes
2. /consultations mutation routes
3. /clinical-workflows mutation routes that save/change data
4. /appointment-requests mutation routes
5. /notifications mutation routes

Commit message:
Sprint 4 / Module 43 — Audit logging integration for PHI mutations
