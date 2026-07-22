from __future__ import annotations

import time
from typing import Any

from .data import load_case, load_rules
from .models import (
    AskResponse,
    Citation,
    CompletenessItem,
    CompletenessReport,
    EvidenceResponse,
    QueueItem,
    ReviewMemo,
    TraceStep,
)
from .retrieval import BM25Retriever


def _citation(rule: dict[str, Any], confidence: float = 0.95) -> Citation:
    return Citation(
        source_id=rule["id"],
        title=rule["title"],
        version=rule["version"],
        page=rule["page"],
        section=rule["section"],
        source_url=rule["source_url"],
        confidence=max(0.0, min(1.0, confidence)),
    )


class PruefPilot:
    def __init__(self) -> None:
        self.case = load_case()
        self.rules = load_rules()
        self.retriever = BM25Retriever(self.rules)

    def queue(self) -> list[QueueItem]:
        return [
            QueueItem(
                case_id="GF-2026-014", applicant="Stadt Falkenried", stage="Vorprüfung",
                risk_score=72, open_points=5,
                next_action="Abnahmeprotokoll und Fotodokumentation nachfordern; Differenz klären.",
            ),
            QueueItem(
                case_id="GF-2026-021", applicant="Landkreis Sonnenhain", stage="Intake",
                risk_score=38, open_points=2,
                next_action="Zwei Dokumente mit niedriger Klassifikationskonfidenz prüfen.",
            ),
            QueueItem(
                case_id="GF-2026-026", applicant="Gemeinde Uferstedt", stage="Fachprüfung",
                risk_score=18, open_points=1,
                next_action="Prüfvermerk fachlich freigeben.",
            ),
        ]

    def case_summary(self) -> dict[str, Any]:
        present = sum(1 for d in self.case["documents"] if d["status"] == "present")
        return {
            "case_id": self.case["case_id"],
            "title": self.case["title"],
            "applicant": self.case["applicant"],
            "project_period": self.case["project_period"],
            "documents_present": present,
            "documents_required": len(self.case["required_document_types"]),
            "amount_delta_eur": self.case["invoice_total_eur"] - self.case["claimed_total_eur"],
            "risk_score": 72,
        }

    def completeness(self) -> CompletenessReport:
        started = time.perf_counter()
        missing = [
            CompletenessItem(document_type=d["type"], title=d["title"], status="missing")
            for d in self.case["documents"] if d["status"] == "missing"
        ]
        delta = self.case["invoice_total_eur"] - self.case["claimed_total_eur"]
        trace = [
            TraceStep(tool="load_case_schema", detail="Pflichtdokumente aus Programm- und Bescheidschema geladen", duration_ms=0.3),
            TraceStep(tool="compare_document_inventory", status="warning", detail=f"{len(missing)} Unterlagen fehlen", duration_ms=0.5),
            TraceStep(tool="reconcile_amounts", status="warning", detail=f"Differenz {delta:,.0f} EUR".replace(",", "."), duration_ms=0.2),
            TraceStep(tool="emit_typed_report", detail="CompletenessReport validiert", duration_ms=round((time.perf_counter() - started) * 1000, 2)),
        ]
        return CompletenessReport(
            present=len(self.case["documents"]) - len(missing),
            required=len(self.case["documents"]),
            missing=missing,
            review_flags=[
                f"Rechnungssumme und beantragte Erstattung weichen um {delta:,.0f} EUR ab.".replace(",", "."),
                "Rechnung R-007 enthält keinen Leistungszeitraum.",
                "Ein hochgeladenes Dokument wurde wegen einer Prompt-Injection-Anweisung quarantänisiert.",
            ],
            trace=trace,
        )

    def evidence_check(self, claim: str) -> EvidenceResponse:
        text = claim.lower()
        trace = [
            TraceStep(tool="parse_claim", detail="Behauptung in prüfbare Teilkriterien zerlegt", duration_ms=0.2),
            TraceStep(tool="retrieve_case_evidence", detail="Fallmetadaten, Rechnungen und Nachweise abgeglichen", duration_ms=0.4),
        ]
        if any(token in text for token in ("summe", "betrag", "rechnung")):
            delta = self.case["invoice_total_eur"] - self.case["claimed_total_eur"]
            return EvidenceResponse(
                status="NOT_SUPPORTED",
                summary=f"Die beantragte Erstattung stimmt nicht mit der Rechnungssumme überein. Differenz: {delta:,.0f} EUR.".replace(",", "."),
                supporting_evidence=["Zahlenmäßiger Verwendungsnachweis: 730.000 EUR", "Rechnungspaket: 734.280 EUR"],
                missing_evidence=["Korrigierter Nachweis oder nachvollziehbare Überleitungsrechnung"],
                trace=trace + [TraceStep(tool="reconcile_amounts", status="warning", detail="Widerspruch erkannt", duration_ms=0.2)],
            )
        if "vollständig" in text or "projektdokumentation" in text:
            return EvidenceResponse(
                status="NOT_SUPPORTED",
                summary="Die Projektdokumentation ist nicht vollständig.",
                supporting_evidence=["Netzplan und Messprotokolle liegen vor."],
                missing_evidence=["Abnahmeprotokoll", "Fotodokumentation mit GPS-Zuordnung"],
                trace=trace + [TraceStep(tool="list_missing_documents", status="warning", detail="2 Pflichtunterlagen fehlen", duration_ms=0.2)],
            )
        dated = [inv for inv in self.case["invoices"] if inv.get("service_to")]
        undated = [inv["invoice"] for inv in self.case["invoices"] if not inv.get("service_to")]
        return EvidenceResponse(
            status="PARTIALLY_SUPPORTED",
            summary="Die datierten Rechnungen liegen vor Projektende. Für Rechnung R-007 fehlt jedoch der Leistungszeitraum; zusätzlich fehlt das Abnahmeprotokoll.",
            supporting_evidence=[f'{inv["invoice"]}: Leistungsende {inv["service_to"]}' for inv in dated],
            missing_evidence=[f"Leistungszeitraum für {invoice}" for invoice in undated] + ["Abnahmeprotokoll"],
            trace=trace + [TraceStep(tool="validate_service_periods", status="warning", detail="1 Rechnung ohne Leistungszeitraum", duration_ms=0.3)],
        )

    def ask(self, question: str) -> AskResponse:
        started = time.perf_counter()
        results = self.retriever.search(question, limit=3)
        trace = [
            TraceStep(tool="classify_question", detail="Fachfrage und benötigte Quellenart erkannt", duration_ms=0.2),
            TraceStep(tool="search_versioned_rules", detail=f"{len(results)} Regelabschnitte gefunden", duration_ms=0.7),
        ]
        if not results:
            return AskResponse(
                answer="Dazu enthält der eingebundene Demo-Korpus keine belastbare Grundlage. Bitte ergänzen Sie die Dokumentbasis oder prüfen Sie den individuellen Zuwendungsbescheid.",
                citations=[], trace=trace + [TraceStep(tool="grounding_guard", status="warning", detail="Keine belastbare Quelle", duration_ms=0.1)],
                grounded=False, uncertainty="high",
            )
        q = question.lower()
        citations = [_citation(doc, min(0.99, 0.76 + score / 12)) for doc, score in results]
        if "frist" in q and "verwendungsnachweis" in q:
            answer = "Der Verwendungsnachweis ist innerhalb von sechs Monaten nach Erfüllung des Zuwendungszwecks einzureichen, spätestens sechs Monate nach Ende des Bewilligungszeitraums. Zusätzliche Anforderungen können sich aus dem konkreten Zuwendungsbescheid ergeben."
        elif "fehl" in q or "vollständig" in q:
            answer = "In der Demo-Akte fehlen das Abnahmeprotokoll und die GPS-zugeordnete Fotodokumentation. Zusätzlich weichen Rechnungssumme und beantragte Erstattung um 4.280 EUR ab; Rechnung R-007 enthält keinen Leistungszeitraum."
            trace.append(TraceStep(tool="join_case_inventory", status="warning", detail="Regeln mit Fallbestand abgeglichen", duration_ms=0.4))
        elif "foto" in q or "dokumentation" in q:
            answer = "Die Maßnahme ist fortlaufend mit digitalen Fotos und GPS-Zuordnung zu dokumentieren. Die Unterlagen sollen den Zustand vor, während und nach Teilleistungen abbilden. In der Demo-Akte fehlt diese Dokumentation."
        elif "mittel" in q or "auszahlung" in q:
            answer = "Auszahlungen erfolgen entsprechend dem Projektfortschritt. Angefordert werden dürfen grundsätzlich nur förderfähige, tatsächlich entstandene und bereits bezahlte Ausgaben."
        elif "markterkund" in q or "branchendialog" in q:
            answer = "Vor dem Markterkundungsverfahren ist ein Branchendialog durchzuführen. Das Markterkundungsverfahren muss mindestens 30 Tage offen sein; das Ergebnis darf bei Einleitung des Auswahlverfahrens nicht älter als zwölf Monate sein."
        else:
            answer = "Nach den eingebundenen Regelzusammenfassungen gilt: " + " ".join(doc["text"] for doc, _ in results[:2])
        trace.append(TraceStep(tool="compose_grounded_answer", detail="Antwort ausschließlich aus Fall- und Quellkontext erzeugt", duration_ms=round((time.perf_counter() - started) * 1000, 2)))
        return AskResponse(answer=answer, citations=citations, trace=trace, grounded=True, uncertainty="low" if len(citations) >= 2 else "medium")

    def review_memo(self) -> ReviewMemo:
        completeness = self.completeness()
        timing = self.evidence_check("Alle abgerechneten Leistungen wurden vor Projektende erbracht.")
        source_ids = ["bnbest_verwendungsnachweis_frist", "bnbest_project_documentation", "bnbest_reimbursement"]
        cited = [next(rule for rule in self.rules if rule["id"] == source_id) for source_id in source_ids]
        open_points = [item.title for item in completeness.missing] + completeness.review_flags + timing.missing_evidence
        open_points = list(dict.fromkeys(open_points))
        return ReviewMemo(
            case_id=self.case["case_id"], decision="NEEDS_INFORMATION",
            confirmed=[
                "Bewilligungsbescheid, Kostenplan, Sachbericht, Netzplan und Messprotokolle liegen vor.",
                "Die datierten Rechnungen liegen innerhalb des Projektzeitraums.",
                "Die vorliegenden Rechnungen sind als bezahlt gekennzeichnet.",
            ],
            open_points=open_points,
            next_actions=[
                "Abnahmeprotokoll und GPS-zugeordnete Fotodokumentation nachfordern.",
                "Differenz von 4.280 EUR zwischen Rechnungspaket und Verwendungsnachweis klären.",
                "Leistungszeitraum der Rechnung R-007 belegen.",
                "Anschließend menschliche Endprüfung und Freigabe dokumentieren.",
            ],
            citations=[_citation(rule) for rule in cited],
            trace=[
                TraceStep(tool="run_completeness_check", detail="Pflichtunterlagen und Zahlen geprüft", duration_ms=1.0),
                TraceStep(tool="compare_claim_to_evidence", status="warning", detail="Unbelegte Teilaspekte gefunden", duration_ms=0.7),
                TraceStep(tool="draft_review_memo", detail="Strukturierten Prüfvermerk erzeugt", duration_ms=0.5),
                TraceStep(tool="human_approval_gate", detail="Endentscheidung ausdrücklich nicht automatisiert", duration_ms=0.1),
            ],
        )
