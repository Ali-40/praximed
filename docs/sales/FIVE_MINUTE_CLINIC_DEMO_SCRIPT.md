# Five-Minute Clinic Demo Script

**Sprint 21 / Module 161**
**Date:** 2026-07-09
**Audience:** Vienna private clinic — receptionist + doctor

---

## Before You Walk In

Reset the demo queue:
- Open `/dashboard` → click **Demo zurücksetzen**
- Then click **Demo-Anruf erstellen** once — one request visible
- Verify "Rückruf nötig" appears
- Verify the clinic name in settings looks right
- Verify no technical words are visible on screen

Use synthetic data only. No real patient data. No PHI.

---

## Opening Line (00:00 – 00:30)

Speak to the receptionist:

> "Wie viele Anrufe verlieren Sie in der Woche, weil das Telefon nicht abgenommen wird?"

Wait for the answer. Then:

> "PraxisMed fängt diese Anrufe auf und zeigt Ihnen, wer zurückgerufen werden muss — ohne dass Sie etwas verpassen."

---

## 1. Show the Dashboard (00:30 – 01:30)

Open `/dashboard`. Point to the **Heute** summary bar at the top:

> "Das hier ist Ihre tägliche Übersicht. Wie viele Anfragen sind heute eingegangen, wie viele warten noch auf Rückruf."

Click into the **Anfragen** tab. Show the one demo request:

> "Eine neue Anfrage. Patient hat angerufen, Terminwunsch wurde aufgenommen. Kein Termin wurde bestätigt — das entscheiden Sie."

Click **Rückruf**:

> "Sie klicken hier, wenn Sie zurückrufen möchten. Das System merkt sich den Status."

Click **Als kontaktiert markieren**:

> "Oder Sie markieren es als erledigt. Keine Zettelwirtschaft, kein Vergessen."

---

## 2. Show Patienten Tab (01:30 – 02:00)

Click **Patienten** tab:

> "Hier sehen Sie alle Kontakte, die jemals eine Anfrage gestellt haben — in einem einfachen Überblick."

Keep it brief. Do not explain technical details.

---

## 3. Show Einstellungen Tab (02:00 – 02:30)

Click **Einstellungen**:

> "Hier stellen Sie den Namen Ihrer Praxis, den Arzt, die Öffnungszeiten und den Ton der KI-Rezeption ein. Freundlich, kurz und direkt, oder sehr formell — wie Sie es möchten."

Point to KI-Vorschau:

> "So klingt die KI, wenn ein Patient anruft — in Ihrem Namen, auf Deutsch."

---

## 4. Live Phone Demo Moment (02:30 – 03:30)

Say to the room:

> "Ich rufe jetzt unsere Demo-Nummer an. Das KI-System antwortet auf Deutsch, nimmt die Terminanfrage auf — und in wenigen Sekunden sehen Sie die Anfrage hier in der Warteschlange als 'Rückruf nötig'."

Call the staging Vapi number. Speak a short synthetic request:
- "Guten Tag, ich möchte einen Termin vereinbaren."
- Give a fake name, fake phone number, fake reason.

Hang up. Refresh `/dashboard`. Show the new entry:

> "Das war ein Demo-Anruf mit Testdaten. Aber genau so funktioniert es im echten Betrieb — der Patient spricht, die Anfrage erscheint, Ihr Team ruft zurück."

**Important:** Remind the room:
> "Die KI bestätigt keinen Termin. Das tun Sie — wenn und wann Sie es entscheiden."

---

## 5. Close with Pilot Offer (03:30 – 05:00)

Ask the doctor or practice manager:

> "Wie viele neue Patienten gehen Ihnen pro Monat durch verpasste Anrufe verloren?"

Then:

> "Wir bieten einen 30-Tage-Pilot an — €390 Einrichtung, dann €290 bis €490 pro Monat, je nach Praxisgröße. Wir konfigurieren alles. Sie müssen nichts Technisches tun. Nach 30 Tagen entscheiden Sie."

Closing question:

> "Darf ich Ihnen heute Ihren Pilot einrichten?"

---

## Receptionist Talk Track

Focus points for the receptionist:

- "Das System nimmt Anrufe entgegen, wenn Sie beschäftigt oder nicht erreichbar sind."
- "Sie sehen alle Anfragen auf einem Blick und rufen zurück, wenn Sie Zeit haben."
- "Kein Termin wird automatisch bestätigt — Sie haben immer die Kontrolle."
- "Keine neuen Programme zu lernen. Ein einfaches Dashboard."
- "Keine Diagnose, keine medizinische Beratung — nur Terminanfragen."

Listen for:
- "Wir haben zu viele Anrufe gleichzeitig." → "Genau dafür ist es gemacht."
- "Patienten wollen mit einer Person sprechen." → "Das KI erklärt sofort, dass das Team zurückruft."

---

## Doctor Talk Track

Focus points for the doctor:

- "Neue Patienten gehen nicht verloren, auch wenn das Telefon gerade besetzt ist."
- "Sie sehen den Überblick — Ihr Team kümmert sich um die Details."
- "Kein Arzt muss das System bedienen. Es läuft im Hintergrund."
- "Wir testen das 30 Tage — ohne Risiko, ohne langen Vertrag."
- "Die KI stellt keine Diagnosen, gibt keine medizinische Beratung, und bestätigt keine Termine."

Listen for:
- "Wir sind zufrieden mit dem aktuellen Ablauf." → "Wie viele Anrufe verpassen Sie außerhalb der Öffnungszeiten?"
- "Zu teuer." → "Was kostet ein verlorener neuer Patient?"

---

## What to Never Say

- Do not claim the AI makes decisions
- Do not claim appointments are booked without staff
- Do not make certification or compliance claims
- Do not reference clinical terms: Diagnose, medizinische Beratung, Triage
- Do not show UUIDs, API endpoints, Vapi config, webhook URLs
- Do not claim production PHI readiness

---

## Safety Wording (Always Include)

> "Demo/Staging: Keine echten Patientendaten."
> "Kein automatischer Terminabschluss — das Praxisteam bestätigt jeden Termin."
> "Keine Diagnose, keine medizinische Beratung."
> "Bei Notfällen: Das System verweist sofort an 144."
> "Production PHI: Das besprechen wir erst nach Pilot und Datenschutzprüfung."
