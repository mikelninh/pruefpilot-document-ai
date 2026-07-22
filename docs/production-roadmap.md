# Production Roadmap

## Phase 1 - Narrow pilot

- Ein Förderprogramm, ein Aktenworkflow, ein Reviewer-Team
- Versionierter Regelkorpus und 30-50 gelabelte Pilotfälle
- Intake, cited RAG, completeness, evidence check und review memo
- FastAPI, MCP, CI, eval gate und sichtbare Failure Cases

## Phase 2 - Production hardening

- SSO, RBAC, Mandanten- und Fallberechtigungen
- Virenprüfung, PII-Klassifikation, verschlüsselte Objektablage
- Asynchrone Pipeline mit Queue, Retry, Idempotenz und Dead-Letter Handling
- Layout-aware Parsing, Tabellenextraktion und OCR-Fallback
- Observability: Trace IDs, Tool-/Prompt-Versionen, Kosten, Latenz und SLOs
- Provider-Benchmarks für OpenAI, Mistral und selbst gehostete Modelle

## Phase 3 - Programme and workflow platform

- Konfigurierbare Dokumenttypen, Checklisten, Regeln und Output-Schemata
- Reviewer Feedback als Eval- und Verbesserungsschleife
- Adapter für bestehende DMS-, Förder- und Fachverfahren
- Rollenbasierte Freigaben, Aufgaben und Eskalationen
- Governance für Modellwechsel, Datenhaltung und Audit

## Go-live gates

1. Citation precision und recall über vereinbartem Schwellenwert
2. 100 % Schema-Validität für kritische Outputs
3. Keine autonome Entscheidung oder externe Aktion ohne Freigabe
4. Belastungstest und dokumentierte Fallbacks
5. Datenschutz- und Informationssicherheitsfreigabe
6. Reviewer-Schulung und messbare Akzeptanz
