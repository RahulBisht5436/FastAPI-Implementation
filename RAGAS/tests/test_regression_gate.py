from ragas_eval.report.regression import compare_with_baseline


def test_regression_detects_drop(tmp_path):
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(
        '{"overall_scores": {"faithfulness": 0.90, "answer_relevancy": 0.85}}',
        encoding="utf-8",
    )
    result = compare_with_baseline(
        {"faithfulness": 0.80, "answer_relevancy": 0.84},
        baseline_path=str(baseline_path),
        drop_limit=0.05,
    )
    assert result["failed"] is True


def test_regression_passes_when_within_limit(tmp_path):
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(
        '{"overall_scores": {"faithfulness": 0.90}}',
        encoding="utf-8",
    )
    result = compare_with_baseline(
        {"faithfulness": 0.88},
        baseline_path=str(baseline_path),
        drop_limit=0.05,
    )
    assert result["failed"] is False
