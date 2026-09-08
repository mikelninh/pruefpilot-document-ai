from security.security_delta import build_security_delta_proof


def test_security_delta_proves_containment_without_breaking_benign_documents():
    report = build_security_delta_proof()
    summary = report["summary"]
    assert report["version"] == "security-delta-target-proof/v1"
    assert summary["attackCases"] >= 4
    assert summary["before"]["impactEscapes"] == summary["attackCases"]
    assert summary["after"]["impactEscapes"] == 0
    assert summary["delta"]["relativeImpactReduction"] == 1
    assert summary["holdout"]["contained"] == summary["holdout"]["total"]
    assert summary["benign"]["retentionRate"] == 1
    assert report["mutation"]["historicalVulnerabilityClaimed"] is False
