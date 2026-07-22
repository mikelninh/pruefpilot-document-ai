from __future__ import annotations
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agents import PruefPilot
from .models import (
    AskRequest, AskResponse, CaseSummary, CompletenessReport, EvalSummary,
    EvidenceRequest, EvidenceResponse, IntakeReport, PhaseOneItem, QueueCase, ReviewMemo
)

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "static"

app = FastAPI(
    title="PrüfPilot Document AI",
    version="0.2.0",
    description="Production-shaped agentic document review prototype for a synthetic GovTech funding file."
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

pilot = PruefPilot()

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "pruefpilot", "mode": "deterministic-demo"}

@app.get("/api/queue", response_model=list[QueueCase])
def case_queue() -> list[QueueCase]:
    return pilot.queue()

@app.post("/api/cases/{case_id}/intake", response_model=IntakeReport)
def run_intake(case_id: str) -> IntakeReport:
    if case_id != pilot.context.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.intake()

@app.get("/api/evals", response_model=EvalSummary)
def eval_summary() -> EvalSummary:
    return pilot.eval_summary()

@app.get("/api/phase-one", response_model=list[PhaseOneItem])
def phase_one_map() -> list[PhaseOneItem]:
    return pilot.phase_one_map()

@app.get("/api/cases", response_model=list[CaseSummary])
def list_cases() -> list[dict]:
    return [pilot.case_summary()]

@app.get("/api/cases/{case_id}", response_model=CaseSummary)
def get_case(case_id: str) -> dict:
    summary = pilot.case_summary()
    if case_id != summary["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return summary

@app.post("/api/cases/{case_id}/ask", response_model=AskResponse)
def ask_case(case_id: str, request: AskRequest) -> AskResponse:
    if case_id != pilot.context.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.ask(request.question)

@app.post("/api/cases/{case_id}/completeness", response_model=CompletenessReport)
def run_completeness(case_id: str) -> CompletenessReport:
    if case_id != pilot.context.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.completeness()

@app.post("/api/cases/{case_id}/evidence", response_model=EvidenceResponse)
def check_evidence(case_id: str, request: EvidenceRequest) -> EvidenceResponse:
    if case_id != pilot.context.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.evidence_check(request.claim)

@app.post("/api/cases/{case_id}/review-memo", response_model=ReviewMemo)
def review_memo(case_id: str) -> ReviewMemo:
    if case_id != pilot.context.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.review_memo()

app.mount("/static", StaticFiles(directory=STATIC), name="static")

@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")
