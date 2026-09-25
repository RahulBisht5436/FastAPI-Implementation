from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ragas_eval.dataset.schema import EvalTraceRow


def write_reports(
    *,
    output_path: Path,
    summary: dict,
    traces: list[EvalTraceRow],
    per_sample_frame: pd.DataFrame,
) -> None:
    output_path.mkdir(parents=True, exist_ok=True)

    (output_path / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    per_sample_path = output_path / "per_sample.jsonl"
    with per_sample_path.open("w", encoding="utf-8") as handle:
        for trace in traces:
            handle.write(trace.model_dump_json())
            handle.write("\n")

    per_sample_frame.to_json(output_path / "per_sample_scores.json", orient="records", indent=2)

    failures = summary.get("failures") or []
    regression = summary.get("regression") or {}
    lines = [
        "# RAGAS Evaluation Summary",
        "",
        f"- Run at: {summary.get('run_at')}",
        f"- Mode: {summary.get('mode')}",
        f"- Samples: {summary.get('sample_count')}",
        f"- Passed: {summary.get('passed')}",
        "",
        "## Overall Scores",
    ]
    for metric_name, score in (summary.get("overall_scores") or {}).items():
        lines.append(f"- {metric_name}: {score:.4f}")

    if failures:
        lines.extend(["", "## Threshold Failures"])
        for failure in failures:
            lines.append(
                f"- {failure['metric']}: {failure['score']:.4f} "
                f"(threshold {failure['threshold']:.4f})"
            )

    if regression.get("comparisons"):
        lines.extend(["", "## Regression"])
        for item in regression["comparisons"]:
            lines.append(
                f"- {item['metric']}: baseline={item['baseline']:.4f}, "
                f"current={item['current']:.4f}, delta={item['delta']:.4f}"
            )

    (output_path / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if failures or any(trace.error for trace in traces):
        failure_lines = ["# Evaluation Failures", ""]
        for trace in traces:
            if trace.error:
                failure_lines.append(f"- {trace.sample_id}: {trace.error}")
        for failure in failures:
            failure_lines.append(
                f"- metric {failure['metric']} scored {failure['score']:.4f}"
            )
        (output_path / "failures.md").write_text(
            "\n".join(failure_lines) + "\n",
            encoding="utf-8",
        )
