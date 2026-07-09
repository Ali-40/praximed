# Clinic Dashboard Language Switch

**Sprint 21 / Module 163**
**Date:** 2026-07-09
**Status:** Complete

---

## Goal

Allow clinic staff to switch the dashboard UI between German and English using a simple
language selector in the Settings tab. German is the default. No external i18n library.
No page reload. Instant switch via React state.

---

## What Was Built

### Language Selector

Added at the top of the Settings tab under the heading:
**"Sprache der Oberfläche / Interface language"**

Two radio options:
- **Deutsch** (default)
- **English**

State variable: `uiLang: 'de' | 'en'`, default `'de'`.

### Translation Dictionary

`TRANSLATIONS` constant in `page.tsx` — plain object, no external library:

```
TRANSLATIONS.de  — German labels (default)
TRANSLATIONS.en  — English labels
```

`t(key)` helper: `const t = (key) => TRANSLATIONS[uiLang][key]`

### Labels That Switch

| Key | German (de) | English (en) |
|---|---|---|
| heute | Heute | Today |
| tabAnfragen | Anfragen | Requests |
| tabPatienten | Patienten | Patients |
| tabEinstellungen | Einstellungen | Settings |
| neueAnfragen | Neue Anfragen | New requests |
| rueckrufNoetig | Rückruf nötig | Needs callback |
| dringendPruefen | Dringend prüfen | Staff review |
| erledigt | Erledigt | Completed |
| demoAnrufErstellen | Demo-Anruf erstellen | Create demo call |
| demoZuruecksetzen | Demo zurücksetzen | Reset demo |
| rueckrufMarkieren | Rückruf markieren | Mark callback |
| alsKontaktiertMarkieren | Als kontaktiert markieren | Mark contacted |
| anfrageImUeberblick | Anfrage im Überblick | Request overview |
| telefon | Telefon | Phone |
| anliegen | Anliegen | Issue |
| gewuenschteZeit | Gewünschte Zeit | Preferred time |
| eingegangen | Eingegangen | Received |
| praxisprofil | Praxisprofil | Practice profile |
| oeffnungszeiten | Öffnungszeiten | Opening hours |
| sprachen | Sprachen | Languages |
| kiRezeption | KI-Rezeption | AI receptionist |
| kiVorschau | KI-Vorschau | Preview |
| summaryArt | Art | Category |
| summaryDringlichkeit | Dringlichkeit | Urgency |
| summaryFruehereBesuche | Frühere Besuche | Past visits |
| summaryEmpfohleneAktion | Empfohlene Aktion | Next step |
| safetyNote | Nur zur internen Planung… | For internal scheduling only… |
| uiSprache | Sprache der Oberfläche | Interface language |

---

## What Was NOT Changed

- No external i18n library (no next-intl, react-i18next, FormatJS)
- No page reload on language switch — instant React state change
- No backend persistence of UI language preference
- No new routes
- No new backend migrations
- No calendar (deferred to Module 164)
- No PHI unlock
- All sr-only strings preserved for existing contract test compatibility
- All prior module markers preserved (demo-strip, live-demo-hint, demo-guide)
- Production PHI remains NO-GO

---

## Files Modified

- `frontend/app/dashboard/page.tsx` — TRANSLATIONS constant, uiLang state, t() helper, language selector in Settings tab
- `backend/tests/test_clinic_dashboard_language_switch_contract.py` — 56 contract tests
- `docs/product/CLINIC_DASHBOARD_LANGUAGE_SWITCH.md` — this file

---

## Test Count

5656 total tests. 56 new. All passing. Build clean.
