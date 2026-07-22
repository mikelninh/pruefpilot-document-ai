from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

class Citation(BaseModel):
    source_id: str
    title: str
    page: int
    section: str
    source_url: str
    confidence: float = Field(ge=0.0, le=1.0)

class TraceStep(BaseModel):
    tool: str
    status: Literal["ok", "warning", "error"] = "ok"
    detail: str

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)

class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    trace: list[TraceStep]
    grounded: bool = True

class EvidenceRequest(BaseModel):
    claim: str = Field(min_length=3, max_length=500)

class EvidenceResponse(BaseModel):
    status: Literal["SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_SUPPORTED"]
    summary: str
    supporting_evidence: list[str]
    missing_evidence: list[str]
    trace: list[TraceStep]

class CompletenessItem(BaseModel):
    document_type: str
    title: str
    status: Literal["present", "missing", "review"]

class CompletenessReport(BaseModel):
    present: int
    required: int
    missing: list[CompletenessItem]
    review_flags: list[str]
    trace: list[TraceStep]

class CaseSummary(BaseModel):
    case_id: str
    title: str
    applicant: str
    project_period: dict[str, str]
    documents_present: int
    documents_required: int
    amount_delta_eur: int

class ReviewMemo(BaseModel):
    case_id: str
    decision: Literal["READY_FOR_REVIEW", "NEEDS_INFORMATION"]
    confirmed: list[str]
    open_points: list[str]
    next_actions: list[str]
    citations: list[Citation]
    trace: list[TraceStep]

class QueueCase(BaseModel):
    case_id: str
    applicant: str
    programme: str
    stage: str
    status: Literal["needs_information", "processing", "ready_for_review"]
    risk_score: int = Field(ge=0, le=100)
    open_items: int = Field(ge=0)
    recommended_next_action: str

class IntakeDocument(BaseModel):
    id: str
    title: str
    document_type: str
    status: Literal["classified", "missing", "quarantined"]
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    pages: int = Field(ge=0)
    flags: list[str] = []

class IntakeReport(BaseModel):
    uploaded: int
    classified: int
    quarantined: int
    missing_required: int
    documents: list[IntakeDocument]
    trace: list[TraceStep]

class EvalMetric(BaseModel):
    name: str
    passed: int
    total: int
    gate: str

class EvalSummary(BaseModel):
    status: Literal["passing", "failing"]
    metrics: list[EvalMetric]
    production_metrics_to_add: list[str]

class PhaseOneItem(BaseModel):
    requirement: str
    implemented: str
    evidence: str
    production_next: str
