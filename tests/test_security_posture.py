import json
from pathlib import Path

POSTURE = json.loads((Path(__file__).parents[1] / "security" / "security-posture.json").read_text(encoding="utf-8"))


def test_security_posture_matches_document_security_benchmark():
    benchmark = json.loads((Path(__file__).parents[1] / "data" / "benchmark_cases.json").read_text(encoding="utf-8"))
    assert POSTURE["version"] == "security-posture/v1"
    assert POSTURE["project"]["repository"] == "mikelninh/pruefpilot"
    assert POSTURE["adversarial"]["cases"] == len(benchmark) == 12
    assert POSTURE["adversarial"]["passed"] == 12
    assert POSTURE["adversarial"]["criticalEscapes"] == 0
    assert sum(case["expected_security"] == "quarantine" for case in benchmark) == 2


def test_security_posture_keeps_security_nonclaims_explicit():
    assert POSTURE["claims"] == {"productionSecure": False, "promptInjectionSolved": False, "certified": False}
    assert any("not proof" in risk.lower() or "not" in risk.lower() for risk in POSTURE["residualRisks"])


def test_implemented_controls_have_repository_evidence():
    for control in POSTURE["controls"]:
        if control["status"] == "implemented":
            assert control["evidence"], control["id"]
