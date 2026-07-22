from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .agents import PruefPilot
from .benchmark import run_benchmark
from .config import settings
from .document_ai import ingest_pdf
from .models import (
    AskRequest,
    AskResponse,
    BenchmarkReport,
    BenchmarkRunRequest,
    CaseSummary,
    CompletenessReport,
    EvidenceRequest,
    EvidenceResponse,
    FeedbackRequest,
    FeedbackResponse,
    QueueItem,
    ReviewMemo,
    UploadResult,
)
from .storage import store

app = FastAPI(
    title="PrüfPilot Document AI",
    version="1.0.0",
    description=(
        "Reviewer-facing Document AI prototype for a synthetic public-sector funding workflow. "
        "Grounded RAG, bounded agents, real PDF intake, evaluation and human approval."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins) + ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
pilot = PruefPilot()


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or f"req_{uuid.uuid4().hex[:12]}"
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    response.headers["x-pruefpilot-persistence"] = store.mode
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["x-frame-options"] = "DENY"
    response.headers["referrer-policy"] = "strict-origin-when-cross-origin"
    return response


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse("/index.html", status_code=307)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "pruefpilot",
        "version": app.version,
        "mode": settings.app_env,
        "persistence": store.mode,
        "llm_providers": {
            "openai": bool(settings.openai_api_key),
            "mistral": bool(settings.mistral_api_key),
            "local": bool(settings.local_model_url),
        },
    }


@app.get("/api/queue", response_model=list[QueueItem])
def queue() -> list[QueueItem]:
    return pilot.queue()


@app.get("/api/cases/{case_id}", response_model=CaseSummary)
def case(case_id: str) -> dict:
    if case_id != pilot.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.case_summary()


@app.post("/api/upload", response_model=UploadResult)
async def upload_document(
    file: UploadFile = File(...),
    case_id: str = Form("GF-2026-014"),
) -> UploadResult:
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF uploads are accepted")
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_bytes} bytes")
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=422, detail="The uploaded file is not a valid PDF")
    try:
        result = ingest_pdf(filename, content)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"PDF extraction failed: {type(exc).__name__}") from exc
    store.save_upload(case_id, result.model_dump())
    return result


@app.post("/api/cases/{case_id}/ask", response_model=AskResponse)
def ask(case_id: str, request: AskRequest) -> AskResponse:
    if case_id != pilot.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.ask(request.question)


@app.post("/api/cases/{case_id}/completeness", response_model=CompletenessReport)
def completeness(case_id: str) -> CompletenessReport:
    if case_id != pilot.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.completeness()


@app.post("/api/cases/{case_id}/evidence", response_model=EvidenceResponse)
def evidence(case_id: str, request: EvidenceRequest) -> EvidenceResponse:
    if case_id != pilot.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.evidence_check(request.claim)


@app.post("/api/cases/{case_id}/review-memo", response_model=ReviewMemo)
def review_memo(case_id: str) -> ReviewMemo:
    if case_id != pilot.case["case_id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    return pilot.review_memo()


@app.post("/api/feedback", response_model=FeedbackResponse)
def feedback(request: FeedbackRequest) -> FeedbackResponse:
    feedback_id, eval_case = store.save_feedback(request.model_dump())
    return FeedbackResponse(
        feedback_id=feedback_id,
        stored=True,
        persistence_mode=store.mode,
        eval_case=eval_case,
    )


@app.get("/api/feedback")
def list_feedback() -> dict:
    return {"persistence_mode": store.mode, "items": store.list_feedback()}


@app.post("/api/benchmark/run", response_model=BenchmarkReport)
def benchmark(request: BenchmarkRunRequest) -> BenchmarkReport:
    report = run_benchmark(request.providers)
    store.save_benchmark(report.run_id, report.model_dump())
    return report


@app.get("/api/product-brief")
def product_brief() -> dict:
    return {
        "company_understanding": [
            "aconium supports public-sector implementation, funding and complex project administration.",
            "The product must fit real reviewer workflows and existing specialist systems.",
            "Traceability, data governance and human responsibility matter as much as model quality.",
        ],
        "phase_one": [
            "One domain and one reviewer workflow first.",
            "FastAPI and typed tools as stable contracts.",
            "Grounded RAG, bounded agents, MCP and evaluation gates.",
            "Measure reviewer correction rate before scaling models or domains.",
        ],
        "production_next": [
            "SSO/RBAC and tenant isolation",
            "durable Postgres/object storage and asynchronous processing",
            "DMS/funding-system adapters",
            "labelled evaluation corpus and provider benchmark",
            "monitoring, SLOs, retention and deletion policies",
        ],
    }


if not os.getenv("VERCEL"):
    public_dir = Path(__file__).resolve().parents[1] / "public"
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
