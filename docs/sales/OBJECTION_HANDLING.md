# Objection Handling

**Sprint 21 / Module 161**
**Date:** 2026-07-09

Short, honest answers for common clinic objections. No overclaims. No technical jargon.

---

## 1. "Wir haben schon eine Rezeptionistin."

PraxisMed ersetzt die Rezeptionistin nicht. Es fängt Anrufe auf, die sonst verlorengehen — außerhalb der Öffnungszeiten, bei Stoßzeiten, wenn das Telefon besetzt ist — und sortiert sie für das Team.

Die Rezeptionistin ruft dann geordnet zurück, statt Nachrichten aus Notizblöcken zu entziffern.

---

## 2. "Kann es Termine automatisch bestätigen?"

Nicht im Pilot und nicht in der aktuellen Version.

Das Praxisteam bestätigt jeden Termin. PraxisMed nimmt die Anfrage auf und zeigt sie im Dashboard — die Entscheidung bleibt beim Praxisteam.

---

## 3. "Kann es medizinische Beratung geben?"

Nein. PraxisMed gibt keine medizinische Beratung, stellt keine Diagnosen und nimmt keine Triage vor.

Es nimmt nur den Terminwunsch auf. Alle medizinischen Entscheidungen bleiben beim Arzt und seinem Team.

Bei akuten Notfällen verweist das System sofort auf **144**.

---

## 4. "Ist das DSGVO-konform?"

Keine Übertreibungen hier.

Für den Pilot starten wir bewusst mit einer kontrollierten Demo-Umgebung und synthetischen Daten — ohne unnötige echte Patientendaten.

Vor der Verarbeitung echter Patientendaten besprechen wir AVV, Datenschutzprüfung, technische und organisatorische Maßnahmen sowie Aufbewahrungsfristen gemeinsam. Das passiert Schritt für Schritt, nicht über Nacht.

Keine Zertifizierungsversprechen — das wäre kein seriöser Anspruch für ein System im Pilotbetrieb.

---

## 5. "Werden Patienten eine KI akzeptieren?"

Das System spricht klar und freundlich auf Deutsch. Es erklärt sofort, dass das Praxisteam den Termin bestätigt und zurückruft.

In der Praxis: Patienten wollen vor allem gehört werden und eine klare nächste Aktion. Beides liefert das System.

---

## 6. "Was passiert bei Notfällen?"

Das System triagiert keine Notfälle und gibt keine medizinische Einschätzung.

Bei Anzeichen eines akuten Notfalls sagt das System klar:

> "Bei einem medizinischen Notfall wählen Sie bitte sofort die 144. Auf Wiederhören."

Das System schließt das Gespräch. Es übernimmt keine klinische Funktion.

---

## 7. "Wie aufwendig ist die Einrichtung?"

Für den Demo/Pilot minimal:
- Praxisname, Arzt, Öffnungszeiten, Sprache und Ton einstellen
- Rückruf-Workflow einmal besprechen
- Walkthrough mit dem Team: 30–45 Minuten

Wir übernehmen die technische Einrichtung. Das Praxisteam tut nichts Technisches.

---

## 8. "Warum nicht einfach Doctena oder Online-Buchung?"

PraxisMed fokussiert auf Telefonanrufe und verpasste Anfragen — nicht auf Online-Buchungsslots.

Viele Patienten rufen lieber an, als online zu buchen — besonders ältere oder neue Patienten. Genau diese Anfragen gehen heute verloren.

Doctena und PraxisMed schließen sich nicht aus.

---

## 9. "Kann es sich in unser bestehendes System integrieren?"

Pilot startet eigenständig — kein Integrationsbedarf für den Anfang.

Nach dem Pilot und erfolgreicher Workflow-Validierung können wir Integrationen besprechen. Aber erst wenn der Grundablauf funktioniert.

---

## 10. "Was wenn es einen Fehler macht?"

Das Praxisteam prüft jede Anfrage vor einer Aktion. Es gibt keine automatische Buchung, keine automatische Bestätigung, keine automatische Entscheidung.

Wenn eine Anfrage falsch oder unklar ist, ruft das Team einfach zurück und klärt es direkt mit dem Patienten — genauso wie heute.

---

## What Never to Say in Response

- Do not make DSGVO certification claims.
- Do not make full-compliance claims.
- Do not say the AI makes clinical decisions.
- Do not imply appointments are booked or confirmed without staff.
- Do not say the system can diagnose.
- Do not claim the system is ready for all production scenarios.

---

## Safety Wording (Always Available)

> "Demo/Staging: Keine echten Patientendaten."
> "Keine Diagnose. Keine medizinische Beratung."
> "Kein automatischer Terminabschluss."
> "Notfälle: Verweis auf 144."
> "Production PHI: Erst nach Datenschutzprüfung und AVV."
