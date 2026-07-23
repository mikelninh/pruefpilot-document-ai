# PrüfPilot V5.1 — Interview-Deck-Outline

Die Slides sind Interview-Unterstützung, nicht der primäre Bewerbungslink. Die Live-App bleibt der zentrale Einstieg.

## Empfohlene 10 Slides

1. **Problem:** Nicht mit PDFs chatten — Prüfarbeit verlässlich unterstützen.
2. **Produktthese:** Eine kontrollierte Case Engine, keine freie Agentenschleife.
3. **Drei verständliche Fälle:** Glasfaser, Wohngeld, Vergaberegel.
4. **Live-Fall Glasfaser:** fehlende Dokumente, 4.280 EUR Differenz, Quarantänefall.
5. **Grounded Questions:** freie Fragen, Quellen, Grounding Guard.
6. **GitLaw-Brücke:** von versionierten Regeln zur betroffenen Fallakte.
7. **Architektur:** FastAPI, typed tools, bounded agents, Domain Packs.
8. **Sicherheit:** untrusted documents, Prompt Injection, Human Approval.
9. **Qualität und Grenzen:** 22/22 Tests, 10/10 Retrieval-Evals, keine erfundenen Provider-Scores.
10. **Production Next:** SSO, RBAC, Postgres, Object Storage, Queue, DMS/Fachverfahren.

## 90-Sekunden-Einstieg

> PrüfPilot ist kein allgemeiner PDF-Chat. Die zentrale Frage lautet: Kann das System einer prüfenden Person zuverlässig zeigen, was vorliegt, was fehlt, was widersprüchlich ist und was als Nächstes getan werden sollte? Dafür zeigt V5.1 drei vollständig synthetische Fälle. Die Fachregeln unterscheiden sich; der sichere Kern bleibt gleich: Dokumente aufnehmen, Regeln und Fall zusammenführen, Belege prüfen, Unsicherheit sichtbar machen und einen nächsten Schritt vorbereiten. Die Entscheidung bleibt immer beim Menschen.

## Einsatz im Gespräch

- Die Live-App zuerst öffnen.
- Einen verständlichen Fall auswählen.
- Eine Frage stellen und die Quellen zeigen.
- Danach in die Technikansicht wechseln.
- Slides nur als Struktur oder Fallback verwenden.
