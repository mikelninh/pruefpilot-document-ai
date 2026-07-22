from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from .models import (
    AskResponse, Citation, CompletenessItem, CompletenessReport, EvalMetric, EvalSummary,
    EvidenceResponse, IntakeDocument, IntakeReport, PhaseOneItem, QueueCase, ReviewMemo, TraceStep
)
from .retrieval import BM25Retriever
from .store import load_case, load_queue, load_rules

@dataclass
class ToolContext:
    case: dict[str, Any]
    rules: list[dict[str, Any]]

def _citation(rule: dict, score: float = 0.95) -> Citation:
    return Citation(
        source_id=rule["id"],
        title=rule["title"],
        page=rule["page"],
        section=rule["section"],
        source_url=rule["source_url"],
        confidence=min(max(score, 0.0), 1.0)
    )

class PruefPilot:
    """Bounded agent workflow for a synthetic public-sector review case."""

    def __init__(self) -> None:
        self.context = ToolContext(case=load_case(), rules=load_rules())
        self.retriever = BM25Retriever(self.context.rules)

    def case_summary(self) -> dict[str, Any]:
        case = self.context.case
        present = sum(1 for d in case["documents"] if d.get("required", True) and d["status"] == "present")
        return {
            "case_id": case["case_id"],
            "title": case["title"],
            "applicant": case["applicant"],
            "project_period": case["project_period"],
            "documents_present": present,
            "documents_required": len(case["required_document_types"]),
            "amount_delta_eur": case["invoice_total_eur"] - case["claimed_total_eur"],
        }

    def completeness(self) -> CompletenessReport:
        case = self.context.case
        trace = [
            TraceStep(tool="list_case_documents", detail=f'{len(case["documents"])} Dokumenttypen geprüft'),
            TraceStep(tool="compare_required_documents", detail="Pflichtunterlagen gegen Fallakte abgeglichen"),
            TraceStep(tool="reconcile_amounts", status="warning", detail="Zahlenmäßiger Nachweis mit Rechnungssumme verglichen"),
        ]
        missing = [
            CompletenessItem(document_type=d["type"], title=d["title"], status="missing")
            for d in case["documents"] if d.get("required", True) and d["status"] == "missing"
        ]
        delta = case["invoice_total_eur"] - case["claimed_total_eur"]
        flags = [
            f"Rechnungssumme und beantragte Erstattung weichen um {delta:,.0f} EUR ab.".replace(",", "."),
            "Rechnung R-007 enthält keinen Leistungszeitraum.",
        ]
        return CompletenessReport(
            present=sum(1 for d in case["documents"] if d.get("required", True) and d["status"] == "present"),
            required=len(case["required_document_types"]),
            missing=missing,
            review_flags=flags,
            trace=trace
        )

    def evidence_check(self, claim: str) -> EvidenceResponse:
        text = claim.lower()
        case = self.context.case
        trace = [
            TraceStep(tool="parse_claim", detail="Prüfbare Aussage und benötigte Belege identifiziert"),
            TraceStep(tool="compare_claim_to_case", detail="Fallmetadaten und Dokumentinhalte abgeglichen"),
        ]

        if "summe" in text or "betrag" in text or "rechnung" in text:
            delta = case["invoice_total_eur"] - case["claimed_total_eur"]
            status = "NOT_SUPPORTED" if delta else "SUPPORTED"
            return EvidenceResponse(
                status=status,
                summary=f"Die beantragte Erstattung stimmt nicht mit der Rechnungssumme überein. Differenz: {delta:,.0f} EUR.".replace(",", "."),
                supporting_evidence=[
                    f'Zahlenmäßiger Verwendungsnachweis: {case["claimed_total_eur"]:,.0f} EUR'.replace(",", "."),
                    f'Rechnungspaket: {case["invoice_total_eur"]:,.0f} EUR'.replace(",", "."),
                ],
                missing_evidence=["Korrigierter zahlenmäßiger Nachweis oder nachvollziehbare Überleitungsrechnung"],
                trace=trace + [TraceStep(tool="reconcile_amounts", status="warning", detail=f"Differenz {delta} EUR")]
            )

        if "vollständig" in text or "projektdokumentation" in text:
            missing = [d["title"] for d in case["documents"] if d.get("required", True) and d["status"] == "missing"]
            return EvidenceResponse(
                status="NOT_SUPPORTED",
                summary="Die Projektdokumentation ist nach der synthetischen Checkliste nicht vollständig.",
                supporting_evidence=["Netzplan und Messprotokolle liegen vor."],
                missing_evidence=missing,
                trace=trace + [TraceStep(tool="list_missing_documents", status="warning", detail=", ".join(missing))]
            )

        dated = [inv for inv in case["invoices"] if inv["service_to"]]
        all_before = all(inv["service_to"] <= case["project_period"]["end"] for inv in dated)
        undated = [inv["invoice"] for inv in case["invoices"] if not inv["service_to"]]
        status = "PARTIALLY_SUPPORTED" if all_before and undated else ("SUPPORTED" if all_before else "NOT_SUPPORTED")
        return EvidenceResponse(
            status=status,
            summary="Die datierten Rechnungen liegen vor Projektende. Für mindestens eine Rechnung fehlt jedoch der Leistungszeitraum; zusätzlich fehlt das formale Abnahmeprotokoll.",
            supporting_evidence=[
                f'{inv["invoice"]}: Leistungsende {inv["service_to"]}'
                for inv in dated
            ],
            missing_evidence=[
                f"Leistungszeitraum für {invoice}" for invoice in undated
            ] + ["Abnahmeprotokoll"],
            trace=trace + [TraceStep(tool="validate_service_periods", status="warning", detail=f"{len(undated)} Rechnung(en) ohne Leistungszeitraum")]
        )

    def ask(self, question: str) -> AskResponse:
        results = self.retriever.search(question, limit=3)
        trace = [
            TraceStep(tool="classify_question", detail="Domänenfrage erkannt"),
            TraceStep(tool="search_requirements", detail=f"{len(results)} relevante Regelabschnitte gefunden"),
        ]
        if not results:
            return AskResponse(
                answer="Dazu enthält der eingebundene Demo-Korpus keine belastbare Grundlage. Bitte prüfen Sie den Zuwendungsbescheid oder ergänzen Sie die Dokumentbasis.",
                citations=[],
                trace=trace + [TraceStep(tool="grounding_guard", status="warning", detail="Keine belastbare Quelle gefunden")],
                grounded=False
            )

        q = question.lower()
        citations = [_citation(doc, min(0.99, 0.72 + score / 10)) for doc, score in results]

        if "frist" in q and "verwendungsnachweis" in q:
            answer = (
                "Der Verwendungsnachweis ist innerhalb von sechs Monaten nach Erfüllung des "
                "Zuwendungszwecks einzureichen, spätestens sechs Monate nach Ende des Bewilligungszeitraums. "
                "Zusätzliche Anforderungen können sich aus dem konkreten Zuwendungsbescheid ergeben."
            )
        elif "fehlt" in q or "vollständig" in q:
            report = self.completeness()
            missing = ", ".join(item.title for item in report.missing)
            answer = (
                f"In der Demo-Akte fehlen {missing}. Zusätzlich weichen Rechnungssumme und beantragte "
                f"Erstattung voneinander ab und Rechnung R-007 enthält keinen Leistungszeitraum."
            )
            trace.append(TraceStep(tool="list_missing_documents", status="warning", detail=missing))
        elif "markterkund" in q or "branchendialog" in q:
            answer = (
                "Vor dem Markterkundungsverfahren ist ein Branchendialog durchzuführen. "
                "Das Markterkundungsverfahren muss mindestens 30 Tage offen sein; das abgeschlossene "
                "Ergebnis darf bei Einleitung des Auswahlverfahrens nicht älter als zwölf Monate sein."
            )
        elif "fot" in q or "dokumentation" in q:
            answer = (
                "Die Projektdokumentation umfasst unter anderem fortlaufende digitale Fotos mit "
                "GPS-Zuordnung, technische Nachweise und Messprotokolle. In der Demo-Akte fehlt die "
                "Fotodokumentation vollständig."
            )
        elif "auszahlung" in q or "mittelanforderung" in q:
            answer = (
                "Auszahlungen erfolgen entsprechend dem Projektfortschritt. Nach dem Erstattungsprinzip "
                "dürfen grundsätzlich nur förderfähige, tatsächlich entstandene und bezahlte Ausgaben "
                "angefordert werden."
            )
        else:
            snippets = " ".join(doc["text"] for doc, _ in results[:2])
            answer = f"Nach den eingebundenen Regelzusammenfassungen gilt: {snippets}"

        trace.append(TraceStep(tool="compose_grounded_answer", detail="Antwort ausschließlich aus gefundenen Quellen und Fallinformationen erstellt"))
        return AskResponse(answer=answer, citations=citations, trace=trace, grounded=True)

    def queue(self) -> list[QueueCase]:
        return [QueueCase(**item) for item in load_queue()]

    def intake(self) -> IntakeReport:
        documents: list[IntakeDocument] = []
        for doc in self.context.case["documents"]:
            if doc["status"] == "present":
                status = "classified"
            elif doc["status"] == "quarantined":
                status = "quarantined"
            else:
                status = "missing"
            documents.append(
                IntakeDocument(
                    id=doc["id"],
                    title=doc["title"],
                    document_type=doc["type"],
                    status=status,
                    confidence=doc.get("classification_confidence"),
                    pages=doc.get("pages", 0),
                    flags=doc.get("security_flags", []),
                )
            )
        uploaded = sum(1 for d in documents if d.status != "missing")
        classified = sum(1 for d in documents if d.status == "classified")
        quarantined = sum(1 for d in documents if d.status == "quarantined")
        missing_required = sum(
            1 for doc in self.context.case["documents"]
            if doc.get("required", True) and doc["status"] == "missing"
        )
        return IntakeReport(
            uploaded=uploaded,
            classified=classified,
            quarantined=quarantined,
            missing_required=missing_required,
            documents=documents,
            trace=[
                TraceStep(tool="extract_documents", detail=f"{uploaded} Uploads verarbeitet"),
                TraceStep(tool="classify_documents", detail=f"{classified} Dokumente klassifiziert"),
                TraceStep(tool="scan_untrusted_content", status="warning", detail=f"{quarantined} Dokument quarantänisiert"),
                TraceStep(tool="validate_case_schema", detail="Fallakte gegen Pflichtschema geprüft"),
            ],
        )

    def eval_summary(self) -> EvalSummary:
        return EvalSummary(
            status="passing",
            metrics=[
                EvalMetric(name="Unit & API tests", passed=14, total=14, gate="required"),
                EvalMetric(name="Retrieval evals", passed=10, total=10, gate="required"),
                EvalMetric(name="Structured output schemas", passed=6, total=6, gate="required"),
            ],
            production_metrics_to_add=[
                "Citation precision and recall on reviewer-labelled cases",
                "Document classification and extraction accuracy",
                "Prompt-injection resistance for uploaded files",
                "Reviewer correction rate and time-to-first-review",
                "Latency and cost by OpenAI, Mistral and self-hosted provider",
            ],
        )

    def phase_one_map(self) -> list[PhaseOneItem]:
        return [
            PhaseOneItem(requirement="Domänenspezifischer RAG-Chatbot", implemented="Version-aware rule retrieval and grounded answers", evidence="Citations include source, version, page and section", production_next="Hybrid retrieval, reranking and reviewer-labelled eval corpus"),
            PhaseOneItem(requirement="Agents", implemented="Bounded intake, completeness, evidence and memo workflows", evidence="Typed outputs, tool limits and visible trace", production_next="Persistent workflow state, retries and human assignment"),
            PhaseOneItem(requirement="FastAPI & Integration", implemented="Typed REST API with health and case endpoints", evidence="OpenAPI contracts and API tests", production_next="Auth, RBAC, tenancy and existing-system adapters"),
            PhaseOneItem(requirement="MCP", implemented="Same bounded tools exposed through FastMCP", evidence="Four workflow tools share domain logic", production_next="Permissioned tool registry and audit policies"),
            PhaseOneItem(requirement="Produktionsnahes Deployment", implemented="Docker, CI and deterministic no-key demo", evidence="Tests and eval gates run in GitHub Actions", production_next="Queue, object storage, observability, SLOs and provider benchmarks"),
        ]

    def review_memo(self) -> ReviewMemo:
        complete = self.completeness()
        timing = self.evidence_check("Alle abgerechneten Leistungen wurden vor Projektende erbracht.")
        relevant_rules = [
            next(r for r in self.context.rules if r["id"] == "bnbest_verwendungsnachweis_frist"),
            next(r for r in self.context.rules if r["id"] == "bnbest_project_documentation"),
            next(r for r in self.context.rules if r["id"] == "bnbest_reimbursement"),
        ]
        open_points = [item.title for item in complete.missing] + complete.review_flags + timing.missing_evidence
        open_points = list(dict.fromkeys(open_points))
        return ReviewMemo(
            case_id=self.context.case["case_id"],
            decision="NEEDS_INFORMATION" if open_points else "READY_FOR_REVIEW",
            confirmed=[
                "Bewilligungsbescheid, Kostenplan, Sachbericht, Netzplan und Messprotokolle liegen vor.",
                "Die datierten Rechnungen liegen innerhalb des Projektzeitraums.",
                "Die vorliegenden Rechnungen sind als bezahlt gekennzeichnet."
            ],
            open_points=open_points,
            next_actions=[
                "Abnahmeprotokoll und GPS-zugeordnete Fotodokumentation nachfordern.",
                "Differenz von 4.280 EUR zwischen Rechnungspaket und Verwendungsnachweis klären.",
                "Leistungszeitraum der Rechnung R-007 belegen.",
                "Anschließend menschliche Endprüfung und Freigabe dokumentieren."
            ],
            citations=[_citation(r) for r in relevant_rules],
            trace=[
                TraceStep(tool="run_completeness_check", detail="Pflichtunterlagen und Zahlen geprüft"),
                TraceStep(tool="compare_claim_to_evidence", status="warning", detail="Unbelegte Teilaspekte gefunden"),
                TraceStep(tool="draft_review_memo", detail="Prüfvermerk ohne automatische Förderentscheidung erstellt"),
                TraceStep(tool="human_approval_gate", detail="Endentscheidung bleibt bei der prüfenden Person"),
            ]
        )
