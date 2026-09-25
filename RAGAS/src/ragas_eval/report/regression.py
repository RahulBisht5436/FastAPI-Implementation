from __future__ import annotations

import json
from pathlib import Path


def compare_with_baseline(
    current_scores: dict[str, float],
    *,
    baseline_path: str | None,
    drop_limit: float,
) -> dict:
    if not baseline_path:
        return {"enabled": False, "failed": False, "comparisons": []}

    baseline_file = Path(baseline_path)
    if not baseline_file.exists():
        return {
            "enabled": True,
            "failed": False,
            "missing_baseline": True,
            "comparisons": [],
        }

    baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
    baseline_scores = baseline.get("overall_scores") or {}
    comparisons = []
    failed = False

    for metric_name, current_value in current_scores.items():
        baseline_value = baseline_scores.get(metric_name)
        if baseline_value is None:
            continue
        delta = current_value - float(baseline_value)
        comparisons.append(
            {
                "metric": metric_name,
                "baseline": float(baseline_value),
                "current": float(current_value),
                "delta": delta,
            }
        )
        if delta < -drop_limit:
            failed = True

    return {
        "enabled": True,
        "failed": failed,
        "drop_limit": drop_limit,
        "comparisons": comparisons,
    }
