from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.v5_cases import answer, evidence, get_case, list_cases, memo


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=600)


class EvidenceRequest(BaseModel):
    claim: str = Field(min_length=3, max_length=600)


app = FastAPI(
    title="PrüfPilot V5 Case Engine",
    version="5.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "pruefpilot-v5",
        "version": app.version,
        "cases": len(list_cases()),
        "mode": "synthetic-demo",
    }


@app.get("/api/v5/cases")
def cases() -> list[dict]:
    return list_cases()


@app.get("/api/v5/cases/{case_id}")
def case(case_id: str) -> dict:
    value = get_case(case_id)
    if not value:
        raise HTTPException(status_code=404, detail="Case not found")
    return value


@app.post("/api/v5/cases/{case_id}/ask")
def ask_case(case_id: str, request: AskRequest) -> dict:
    value = answer(case_id, request.question)
    if not value:
        raise HTTPException(status_code=404, detail="Case not found")
    return value


@app.post("/api/v5/cases/{case_id}/evidence")
def evidence_case(case_id: str, request: EvidenceRequest) -> dict:
    value = evidence(case_id, request.claim)
    if not value:
        raise HTTPException(status_code=404, detail="Case not found")
    return value


@app.post("/api/v5/cases/{case_id}/memo")
def memo_case(case_id: str) -> dict:
    value = memo(case_id)
    if not value:
        raise HTTPException(status_code=404, detail="Case not found")
    return value
