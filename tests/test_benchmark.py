from app.benchmark import run_benchmark, run_deterministic


def test_deterministic_benchmark_is_measured():
    metric = run_deterministic()
    assert metric.status == "measured"
    assert metric.cases == 12
    assert metric.classification_accuracy == 1.0
    assert metric.extraction_accuracy == 1.0
    assert metric.security_recall == 1.0
    assert metric.estimated_cost_eur == 0.0


def test_unconfigured_providers_are_not_fabricated():
    report = run_benchmark(["openai", "mistral", "local"])
    assert all(metric.status == "not_configured" for metric in report.metrics)
    assert all(metric.classification_accuracy is None for metric in report.metrics)
