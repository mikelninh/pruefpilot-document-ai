from __future__ import annotations

import statistics
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from .data import load_benchmark_cases
from .document_ai import classify_document, extract_fields, scan_security
from .models import BenchmarkMetric, BenchmarkReport
from .providers import PROVIDERS


def _pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def run_deterministic() -> BenchmarkMetric:
    cases = load_benchmark_cases()
    classification_ok = extraction_ok = security_ok = structured_ok = 0
    classification_total = extraction_total = security_total = 0
    latencies: list[float] = []

    for case in cases:
        started = time.perf_counter()
        document_type, _, _ = classify_document(case["text"], case.get("filename", ""))
        fields = extract_fields(case["text"], document_type)
        findings = scan_security(case["text"])
        latencies.append((time.perf_counter() - started) * 1000)
        classification_total += 1
        classification_ok += int(document_type == case["expected_type"])
        if case.get("expected_amount") is not None:
            extraction_total += 1
            values = " ".join(field.value for field in fields)
            extraction_ok += int(case["expected_amount"] in values)
        if case.get("expected_security") is not None:
            security_total += 1
            got = "quarantine" if any(item.action == "quarantine" for item in findings) else "allow"
            security_ok += int(got == case["expected_security"])
        structured_ok += int(isinstance(fields, list) and all(hasattr(field, "model_dump") for field in fields))

    sorted_latencies = sorted(latencies)
    p95_index = min(len(sorted_latencies) - 1, max(0, round(0.95 * len(sorted_latencies)) - 1))
    return BenchmarkMetric(
        provider="deterministic",
        status="measured",
        classification_accuracy=_pct(classification_ok, classification_total),
        extraction_accuracy=_pct(extraction_ok, extraction_total),
        security_recall=_pct(security_ok, security_total),
        structured_output_rate=_pct(structured_ok, len(cases)),
        latency_p50_ms=round(statistics.median(latencies), 3),
        latency_p95_ms=round(sorted_latencies[p95_index], 3),
        estimated_cost_eur=0.0,
        cases=len(cases),
        note="Measured on synthetic fixtures; no LLM involved.",
    )


def _llm_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "document_type": {"type": "string"},
            "amount": {"type": ["string", "null"]},
            "security_action": {"type": "string"},
        },
        "required": ["document_type", "amount", "security_action"],
        "additionalProperties": False,
    }


def run_provider(name: str) -> BenchmarkMetric:
    provider = PROVIDERS[name]
    if not provider.configured():
        return BenchmarkMetric(
            provider=name,
            status="not_configured",
            cases=0,
            note="Adapter implemented; configure credentials or endpoint for a controlled run.",
        )
    cases = load_benchmark_cases()[:6]
    classification_ok = extraction_ok = security_ok = structured_ok = 0
    extraction_total = security_total = 0
    latencies: list[float] = []
    failures = 0
    for case in cases:
        prompt = (
            "Classify this public-sector document excerpt. Extract a EUR amount when present and decide "
            "whether document-borne instructions must be quarantined. Return JSON only.\n\n" + case["text"]
        )
        try:
            output, latency, _ = provider.extract(prompt, _llm_schema())
            latencies.append(latency)
            classification_ok += int(output.get("document_type") == case["expected_type"])
            if case.get("expected_amount") is not None:
                extraction_total += 1
                extraction_ok += int(case["expected_amount"] in str(output.get("amount")))
            if case.get("expected_security") is not None:
                security_total += 1
                security_ok += int(output.get("security_action") == case["expected_security"])
            structured_ok += int(set(output) >= {"document_type", "amount", "security_action"})
        except Exception:
            failures += 1
    if failures == len(cases):
        return BenchmarkMetric(provider=name, status="failed", cases=len(cases), note="All provider calls failed.")
    sorted_latencies = sorted(latencies)
    p95_index = min(len(sorted_latencies) - 1, max(0, round(0.95 * len(sorted_latencies)) - 1))
    return BenchmarkMetric(
        provider=name,
        status="measured" if failures == 0 else "failed",
        classification_accuracy=_pct(classification_ok, len(cases)),
        extraction_accuracy=_pct(extraction_ok, extraction_total),
        security_recall=_pct(security_ok, security_total),
        structured_output_rate=_pct(structured_ok, len(cases)),
        latency_p50_ms=round(statistics.median(latencies), 1) if latencies else None,
        latency_p95_ms=round(sorted_latencies[p95_index], 1) if latencies else None,
        estimated_cost_eur=None,
        cases=len(cases),
        note="No cost is guessed without provider usage metadata.",
    )


def run_benchmark(providers: list[str]) -> BenchmarkReport:
    metrics = [run_deterministic() if name == "deterministic" else run_provider(name) for name in dict.fromkeys(providers)]
    return BenchmarkReport(
        run_id=f"bench_{uuid.uuid4().hex[:10]}",
        generated_at=datetime.now(timezone.utc).isoformat(),
        metrics=metrics,
        methodology=[
            "Synthetic German funding-document excerpts with fixed gold labels.",
            "Same document-type, amount and security tasks for every configured provider.",
            "Structured JSON required.",
            "No provider score or cost is shown unless a real run completed.",
        ],
    )
