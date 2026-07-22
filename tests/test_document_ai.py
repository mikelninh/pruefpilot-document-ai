from app.data import load_benchmark_cases
from app.document_ai import classify_document, extract_fields, scan_security


def test_classification_gold_set():
    for case in load_benchmark_cases():
        got, confidence, _ = classify_document(case["text"], case["filename"])
        assert got == case["expected_type"], case["id"]
        assert 0 <= confidence <= 1


def test_amount_extraction_gold_set():
    for case in load_benchmark_cases():
        if case.get("expected_amount") is None:
            continue
        doc_type, _, _ = classify_document(case["text"], case["filename"])
        values = " ".join(field.value for field in extract_fields(case["text"], doc_type))
        assert case["expected_amount"] in values, case["id"]


def test_prompt_injection_recall():
    for case in load_benchmark_cases():
        findings = scan_security(case["text"])
        got = "quarantine" if any(item.action == "quarantine" for item in findings) else "allow"
        assert got == case["expected_security"], case["id"]
