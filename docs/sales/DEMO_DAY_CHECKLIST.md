# Demo Day Checklist

**Sprint 21 / Module 161**
**Date:** 2026-07-09

Use before and during every clinic visit. No technical words in front of the clinic.

---

## Before Entering the Clinic

- [ ] Open `/dashboard` — confirm login works
- [ ] Click **Demo zurücksetzen** — queue is empty
- [ ] Click **Demo-Anruf erstellen** once — one request appears
- [ ] Verify "Rückruf nötig" is visible
- [ ] Verify no UUID is visible in the queue or UI
- [ ] Open **Einstellungen** — verify clinic name and doctor name look realistic
- [ ] Verify KI-Ton is set to "Freundlich und ruhig"
- [ ] Verify KI-Vorschau text says "Praxisteam meldet sich zur Bestätigung zurück"
- [ ] Verify **Vapi staging number is ready** if doing live phone moment
- [ ] Use synthetic/fake data only for all demo calls
- [ ] Confirm internet connection is stable
- [ ] Close all irrelevant browser tabs

---

## During the Demo

**Language rules:**
- No technical words: no UUID, no API, no webhook, no Vapi, no FHIR, no JWT
- No compliance claims: do not mention certification or full compliance
- No medical automation claims: no diagnosis, no advice, no triage

**Sequence:**
- [ ] Show **Heute** summary bar — point to the numbers
- [ ] Show **Anfragen** tab — one demo request visible
- [ ] Click **Rückruf** to show the callback action
- [ ] Click **Als kontaktiert markieren** to show status tracking
- [ ] Show **Patienten** tab briefly — patient overview
- [ ] Show **Einstellungen** tab — name, tone, KI-Vorschau
- [ ] Do the **live phone demo moment** (if Vapi number is ready)
  - Call the staging number
  - Speak: fake name, fake phone, "Ich möchte einen Termin"
  - Hang up
  - Refresh `/dashboard` — show new entry
- [ ] Say out loud: "Das Praxisteam bestätigt jeden Termin — nicht das System."
- [ ] Reset demo if needed: **Demo zurücksetzen**

---

## After the Demo

- [ ] Ask: "Wie viele Anrufe verlieren Sie pro Woche, die nicht abgenommen werden?"
- [ ] Ask: "Wer in Ihrem Team kümmert sich aktuell um Rückrufe?"
- [ ] Ask: "Zu welchen Zeiten klingelt das Telefon am häufigsten?"
- [ ] Ask: "Wie tracken Sie heute verpasste Anrufe?"
- [ ] Offer the 30-day pilot
- [ ] Leave the one-page handout
- [ ] Note: final pricing confirmed after workflow review

---

## Pilot Close Question

> "Darf ich Ihnen heute Ihren Pilot einrichten?"

or

> "Wann wäre ein guter Zeitpunkt für den 30-Tage-Pilot?"

---

## What This Demo Is Not

- Not a production deployment
- Not processing real patient data
- Not carrying any compliance certification
- Not auto-confirming or auto-booking appointments
- Not giving medical advice or diagnoses
- Not replacing the receptionist

---

## Safety Wording (Always Say If Asked)

> "Das ist unser Demo-System mit Testdaten — keine echten Patientendaten."
> "Die KI bestätigt keine Termine. Das Praxisteam entscheidet."
> "Keine Diagnose, keine medizinische Beratung."
> "Notfälle: Das System verweist sofort auf 144."
> "Wiener Privatpraxen · 30-Tage-Pilot · €390 Einrichtung"
