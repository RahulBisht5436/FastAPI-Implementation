from __future__ import annotations

from typing import Any


def _status_icon(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def format_score_table(
    scores: dict[str, float],
    thresholds: dict[str, float] | None = None,
) -> str:
    lines = [
        "",
        "RAGAS Scores",
        "=" * 72,
        f"{'Metric':<22} {'Score':>8}  {'Threshold':>10}  {'Status':>6}",
        "-" * 72,
    ]
    for metric_name, score in scores.items():
        threshold = thresholds.get(metric_name) if thresholds else None
        threshold_text = f"{threshold:.2f}" if threshold is not None else "-"
        status = "-"
        if threshold is not None:
            status = _status_icon(score >= threshold)
        lines.append(
            f"{metric_name:<22} {score:>8.4f}  {threshold_text:>10}  {status:>6}"
        )
    lines.append("=" * 72)
    return "\n".join(lines)


def format_summary(summary: dict[str, Any]) -> str:
    parts = [
        "",
        "Evaluation Summary",
        "=" * 72,
        f"Samples evaluated : {summary.get('successful_samples', 0)}/{summary.get('sample_count', 0)}",
        f"Mode              : {summary.get('mode')}",
        f"Overall result    : {_status_icon(bool(summary.get('passed')))}",
        f"Reports           : see output directory",
        format_score_table(
            summary.get("overall_scores") or {},
            summary.get("thresholds") or {},
        ),
    ]

    failures = summary.get("failures") or []
    if failures:
        parts.extend(["", "Threshold failures:"])
        for failure in failures:
            parts.append(
                f"  - {failure['metric']}: {failure['score']:.4f} "
                f"(needs >= {failure['threshold']:.2f})"
            )

    regression = summary.get("regression") or {}
    comparisons = regression.get("comparisons") or []
    if comparisons:
        parts.extend(["", "Regression vs baseline:"])
        for item in comparisons:
            parts.append(
                f"  - {item['metric']}: baseline={item['baseline']:.4f}, "
                f"current={item['current']:.4f}, delta={item['delta']:+.4f}"
            )

    return "\n".join(parts)


def format_smoke_result(payload: dict[str, Any]) -> str:
    answer = payload.get("answer", "")
    contexts = payload.get("contexts") or []
    metadata = payload.get("context_metadata") or []

    lines = [
        "",
        "Smoke Test Result (no RAGAS scores in this mode)",
        "=" * 72,
        f"Question            : {payload.get('question', '')}",
        f"Answer              : {answer}",
        f"Retrieved chunks    : {len(contexts)}",
        f"Retrieval latency   : {payload.get('retrieval_latency_ms')} ms",
        f"Generation latency  : {payload.get('generation_latency_ms')} ms",
        f"KB chunks           : {payload.get('kb_chunk_count')}",
        "",
        "Top retrieved sources:",
    ]

    seen: set[str] = set()
    for item in metadata:
        label = item.get("file_name", "unknown")
        if label in seen:
            continue
        seen.add(label)
        score = item.get("score")
        score_text = f" (score={score:.4f})" if score is not None else ""
        lines.append(f"  - {label}{score_text}")

    lines.extend(
        [
            "",
            "To get RAGAS scores, run one of:",
            '  uv run ragas-eval --sample-id edu-001',
            '  uv run ragas-eval --question "..." --ground-truth "..." --score',
            "  uv run ragas-eval --max-samples 5",
            "=" * 72,
        ]
    )
    return "\n".join(lines)


def format_single_score_result(
    *,
    question: str,
    answer: str,
    ground_truth: str,
    scores: dict[str, float],
    thresholds: dict[str, float],
) -> str:
    passed = all(
        scores.get(metric, 0) >= threshold
        for metric, threshold in thresholds.items()
        if metric in scores
    )
    parts = [
        "",
        "Single-Question RAGAS Evaluation",
        "=" * 72,
        f"Question     : {question}",
        f"Ground truth : {ground_truth}",
        f"Answer       : {answer}",
        f"Result       : {_status_icon(passed)}",
        format_score_table(scores, thresholds),
    ]
    return "\n".join(parts)
