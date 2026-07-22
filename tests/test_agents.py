from app.agents import PruefPilot

def test_completeness_detects_missing_documents_and_delta():
    pilot = PruefPilot()
    report = pilot.completeness()
    missing = {item.document_type for item in report.missing}
    assert missing == {"abnahmeprotokoll", "fotodokumentation"}
    assert any("4.280" in flag for flag in report.review_flags)

def test_evidence_timing_is_partial():
    result = PruefPilot().evidence_check("Alle abgerechneten Leistungen wurden vor Projektende erbracht.")
    assert result.status == "PARTIALLY_SUPPORTED"
    assert any("R-007" in item for item in result.missing_evidence)

def test_review_memo_requires_human_follow_up():
    memo = PruefPilot().review_memo()
    assert memo.decision == "NEEDS_INFORMATION"
    assert any(step.tool == "human_approval_gate" for step in memo.trace)
