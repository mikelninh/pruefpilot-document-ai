from app.agents import PruefPilot


def test_queue_is_prioritised():
    queue = PruefPilot().queue()
    assert [item.risk_score for item in queue] == sorted([item.risk_score for item in queue], reverse=True)
    assert queue[0].case_id == "GF-2026-014"


def test_completeness_detects_missing_documents_and_amount_delta():
    report = PruefPilot().completeness()
    assert {item.document_type for item in report.missing} == {"abnahmeprotokoll", "fotodokumentation"}
    assert any("4.280" in flag for flag in report.review_flags)


def test_evidence_check_is_partial_for_timing_claim():
    result = PruefPilot().evidence_check("Alle abgerechneten Leistungen wurden vor Projektende erbracht.")
    assert result.status == "PARTIALLY_SUPPORTED"
    assert any("R-007" in item for item in result.missing_evidence)


def test_grounded_answer_has_versioned_citation():
    result = PruefPilot().ask("Welche Frist gilt für den Verwendungsnachweis?")
    assert result.grounded is True
    assert result.citations
    assert result.citations[0].version
    assert result.citations[0].page > 0


def test_unknown_question_triggers_grounding_guard():
    result = PruefPilot().ask("Welche Farbe hat das Dienstfahrrad der prüfenden Person?")
    assert result.grounded is False
    assert result.uncertainty == "high"


def test_review_memo_requires_human_approval():
    memo = PruefPilot().review_memo()
    assert memo.decision == "NEEDS_INFORMATION"
    assert memo.human_approval_required is True
    assert any(step.tool == "human_approval_gate" for step in memo.trace)
