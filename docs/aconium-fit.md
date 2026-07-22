# Was diese Demo über aconium und die Rolle verstanden hat

## 1. Das Produkt ist kein allgemeiner PDF-Chat

Die Rolle beschreibt Document AI als Agentic Document Processing Tool, das Prüfer:innen im öffentlichen Sektor täglich unterstützt. Deshalb optimiert PrüfPilot nicht auf möglichst freie Konversation, sondern auf einen kontrollierten Prüfworkflow: Intake, Vollständigkeit, Belegabgleich, zitierte Rückfragen, Prüfvermerk und menschliche Freigabe.

## 2. aconium arbeitet an der Schnittstelle von Verwaltung, Förderung und Umsetzung

aconium begleitet komplexe öffentliche Vorhaben und organisiert bzw. administriert Infrastruktur- und Regionalförderung. Daraus folgen besondere Produktanforderungen:

- Regeln und Dokumentversionen müssen nachvollziehbar sein.
- Ergebnisse müssen in bestehende Sachbearbeitungsprozesse passen.
- Fachliche Entscheidungshoheit bleibt beim Menschen.
- Auditierbarkeit, Datenschutz und Informationssicherheit sind keine späteren Add-ons.
- Das System muss unterschiedliche Programme und Domänen über konfigurierbare Schemata unterstützen.

## 3. Phase 1 braucht einen engen, messbaren Scope

Der Prototyp konzentriert sich auf einen synthetischen Verwendungsnachweis in der Gigabitförderung. Das ist klein genug für schnelle Iteration und realistisch genug, um die riskanten Teile zu testen: Dokumentklassifikation, versioniertes Retrieval, Zahlendifferenzen, fehlende Nachweise, Prompt Injection und Human Approval.

## 4. Der technische Stack spiegelt die Ausschreibung

| Ausschreibung | PrüfPilot |
|---|---|
| Python / FastAPI | Typisierte API mit OpenAPI und Tests |
| Domänenspezifisches RAG | Versionierte Regelabschnitte mit Seiten- und Abschnittszitaten |
| Agents | Begrenzte Intake-, Completeness-, Evidence- und Review-Workflows |
| MCP | Gleiche Domänentools über FastMCP |
| MLOps | Docker, CI, Test- und Eval-Gates, Provider-Boundary |
| OpenAI / Mistral / Open Source | Austauschbares Provider-Protokoll; öffentliche Demo bleibt no-key und deterministisch |
| Produktionssystem | Roadmap für Auth, RBAC, Queue, Storage, Observability, SLOs und Datenschutz |

## 5. Erfolg wird an Reviewer-Nutzen gemessen

Nicht "wie intelligent klingt der Chatbot?", sondern:

- Zeit bis zur ersten belastbaren Prüfung
- Anteil korrekt zitierter Aussagen
- Trefferquote bei fehlenden oder widersprüchlichen Unterlagen
- Korrekturrate durch Prüfer:innen
- Anteil sicher eskalierter Unsicherheiten
- Kosten und Latenz pro Fall
