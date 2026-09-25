from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import evaluate

from ragas_eval.collector.trace_collector import collect_traces
from ragas_eval.config import (
    DEFAULT_THRESHOLDS,
    OPENAI_API_KEY,
    RAGAS_JUDGE_MODEL,
    REGRESSION_DROP_LIMIT,
)
from ragas_eval.dataset.loader import load_golden_dataset, validate_manifest_hash
from ragas_eval.dataset.schema import EvalTraceRow, GoldenDataset
from ragas_eval.metrics.registry import get_default_metrics, get_retrieval_metrics
from ragas_eval.report.generator import write_reports
from ragas_eval.report.regression import compare_with_baseline


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_ragas_dataset(traces: list[EvalTraceRow]) -> Dataset:
    rows = []
    for trace in traces:
        if trace.error:
            continue
        rows.append(
            {
                "user_input": trace.question,
                "response": trace.answer,
                "retrieved_contexts": trace.contexts,
                "reference": trace.ground_truth,
            }
        )
    if not rows:
        raise ValueError("No successful traces available for RAGAS evaluation.")
    return Dataset.from_list(rows)


def _mean_scores(result: Any, metrics: list) -> dict[str, float]:
    repr_dict = getattr(result, "_repr_dict", {}) or {}
    metric_names = {metric.name for metric in metrics}
    return {
        name: float(value)
        for name, value in repr_dict.items()
        if name in metric_names
    }


def _category_scores(traces: list[EvalTraceRow], result: Any) -> dict[str, dict[str, float]]:
    per_sample = result.to_pandas()
    successful_traces = [trace for trace in traces if not trace.error]
    per_sample["sample_id"] = [trace.sample_id for trace in successful_traces]
    per_sample["category"] = [trace.category for trace in successful_traces]

    grouped: dict[str, dict[str, float]] = {}
    metric_columns = [
        column
        for column in per_sample.columns
        if column not in {
            "sample_id",
            "category",
            "user_input",
            "response",
            "reference",
            "retrieved_contexts",
            "reference_contexts",
        }
    ]
    for category, frame in per_sample.groupby("category"):
        grouped[str(category)] = {
            column: float(frame[column].mean())
            for column in metric_columns
            if frame[column].dtype.kind in {"f", "i"}
        }
    return grouped


def run_evaluation(
    *,
    dataset_path: str,
    output_dir: str | Path,
    client,
    mode: str = "full",
    max_samples: int | None = None,
    update_baseline: bool = False,
    baseline_path: str | None = None,
    fail_on_regression: bool = False,
) -> dict[str, Any]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for RAGAS judge metrics.")

    dataset: GoldenDataset = load_golden_dataset(dataset_path)
    if max_samples is not None:
        dataset = GoldenDataset(
            version=dataset.version,
            kb_manifest_hash=dataset.kb_manifest_hash,
            require_manifest_match=dataset.require_manifest_match,
            samples=dataset.samples[:max_samples],
        )

    kb_status = client.kb_status()
    live_manifest_hash = kb_status.get("kb_manifest_hash") or kb_status.get(
        "manifest_hash"
    )
    if live_manifest_hash:
        validate_manifest_hash(dataset, live_manifest_hash)

    chunk_count = kb_status.get("collection", {}).get("chunk_count", 0)
    if chunk_count <= 0:
        raise RuntimeError("Knowledge base has no ingested chunks. Run ingest-rag first.")

    traces = collect_traces(client, dataset)
    ragas_dataset = _build_ragas_dataset(traces)

    judge_llm = ChatOpenAI(model=RAGAS_JUDGE_MODEL, temperature=0)
    judge_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    metrics = get_retrieval_metrics() if mode == "retrieval-only" else get_default_metrics()
    result = evaluate(
        dataset=ragas_dataset,
        metrics=metrics,
        llm=judge_llm,
        embeddings=judge_embeddings,
    )

    overall_scores = _mean_scores(result, metrics)
    category_scores = _category_scores(traces, result)
    thresholds = DEFAULT_THRESHOLDS if mode == "full" else {
        "context_precision": DEFAULT_THRESHOLDS["context_precision"],
        "context_recall": DEFAULT_THRESHOLDS["context_recall"],
    }

    failures = [
        {
            "metric": metric_name,
            "score": score,
            "threshold": thresholds[metric_name],
        }
        for metric_name, score in overall_scores.items()
        if metric_name in thresholds and score < thresholds[metric_name]
    ]

    regression = compare_with_baseline(
        overall_scores,
        baseline_path=baseline_path,
        drop_limit=REGRESSION_DROP_LIMIT,
    )

    summary = {
        "run_at": _utc_now(),
        "dataset_version": dataset.version,
        "dataset_path": str(dataset_path),
        "mode": mode,
        "sample_count": len(traces),
        "successful_samples": len([trace for trace in traces if not trace.error]),
        "kb_manifest_hash": live_manifest_hash,
        "kb_chunk_count": chunk_count,
        "overall_scores": overall_scores,
        "category_scores": category_scores,
        "thresholds": thresholds,
        "failures": failures,
        "regression": regression,
        "passed": not failures and not regression.get("failed", False),
    }

    output_path = Path(output_dir)
    write_reports(
        output_path=output_path,
        summary=summary,
        traces=traces,
        per_sample_frame=result.to_pandas(),
    )

    if update_baseline and baseline_path:
        baseline_payload = {
            "created_at": summary["run_at"],
            "kb_manifest_hash": live_manifest_hash,
            "overall_scores": overall_scores,
            "category_scores": category_scores,
        }
        Path(baseline_path).write_text(
            json.dumps(baseline_payload, indent=2),
            encoding="utf-8",
        )

    if fail_on_regression and (failures or regression.get("failed")):
        raise RuntimeError(
            "Evaluation failed thresholds or regression checks. "
            f"failures={failures}, regression={regression}"
        )

    return summary
