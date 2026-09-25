from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from ragas_eval.client.chatbot_client import ChatbotEvalClient
from ragas_eval.config import (
    BASELINE_PATH,
    CHATBOT_BASE_URL,
    DEFAULT_THRESHOLDS,
    EVAL_DATASET_PATH,
    EVAL_SECRET,
    REPORTS_DIR,
)
from ragas_eval.dataset.loader import load_golden_dataset
from ragas_eval.report.console import (
    format_single_score_result,
    format_smoke_result,
    format_summary,
)
from ragas_eval.runner.batch_runner import run_evaluation
from ragas_eval.runner.single_runner import score_single_trace


def _default_output_dir() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPORTS_DIR / stamp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation against personalChatBot.")
    parser.add_argument("--dataset", default=EVAL_DATASET_PATH, help="Path to golden dataset JSON")
    parser.add_argument("--output", default=None, help="Directory for evaluation reports")
    parser.add_argument("--mode", choices=["full", "retrieval-only"], default="full")
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument(
        "--question",
        default=None,
        help="Run one question through /eval/run (smoke test unless --score is set)",
    )
    parser.add_argument(
        "--sample-id",
        default=None,
        help="Run one golden dataset sample by id, including RAGAS scores",
    )
    parser.add_argument(
        "--ground-truth",
        default=None,
        help="Reference answer used when scoring a single --question",
    )
    parser.add_argument(
        "--score",
        action="store_true",
        help="Compute RAGAS scores for --question (requires --ground-truth)",
    )
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--baseline", default=BASELINE_PATH)
    parser.add_argument("--fail-on-regression", action="store_true")
    parser.add_argument("--chatbot-url", default=CHATBOT_BASE_URL)
    parser.add_argument("--eval-secret", default=EVAL_SECRET)
    return parser


def _resolve_single_question(args, client: ChatbotEvalClient) -> None:
    if args.sample_id:
        dataset = load_golden_dataset(args.dataset)
        sample = next((item for item in dataset.samples if item.id == args.sample_id), None)
        if sample is None:
            raise SystemExit(f"Sample id not found in dataset: {args.sample_id}")

        payload = client.run_eval(sample.question)
        scores = score_single_trace(
            question=sample.question,
            answer=payload.get("answer", ""),
            contexts=payload.get("contexts") or [],
            ground_truth=sample.ground_truth,
            mode=args.mode,
        )
        thresholds = (
            DEFAULT_THRESHOLDS
            if args.mode == "full"
            else {
                "context_precision": DEFAULT_THRESHOLDS["context_precision"],
                "context_recall": DEFAULT_THRESHOLDS["context_recall"],
            }
        )
        print(
            format_single_score_result(
                question=sample.question,
                answer=payload.get("answer", ""),
                ground_truth=sample.ground_truth,
                scores=scores,
                thresholds=thresholds,
            )
        )
        return

    if not args.question:
        return

    payload = client.run_eval(args.question)

    if not args.score:
        print(format_smoke_result(payload))
        return

    if not args.ground_truth:
        raise SystemExit(
            "Scoring a custom question requires --ground-truth.\n"
            "Example:\n"
            '  uv run ragas-eval --question "What is your degree?" '
            '--ground-truth "Rahul completed a B.Tech from MGM College, Noida." --score'
        )

    scores = score_single_trace(
        question=args.question,
        answer=payload.get("answer", ""),
        contexts=payload.get("contexts") or [],
        ground_truth=args.ground_truth,
        mode=args.mode,
    )
    thresholds = (
        DEFAULT_THRESHOLDS
        if args.mode == "full"
        else {
            "context_precision": DEFAULT_THRESHOLDS["context_precision"],
            "context_recall": DEFAULT_THRESHOLDS["context_recall"],
        }
    )
    print(
        format_single_score_result(
            question=args.question,
            answer=payload.get("answer", ""),
            ground_truth=args.ground_truth,
            scores=scores,
            thresholds=thresholds,
        )
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.eval_secret:
        raise SystemExit(
            "EVAL_SECRET is not set. Add it to RAGAS/.env (same value as personalChatBot/.env) "
            "or run: $env:EVAL_SECRET='your-secret'; uv run ragas-eval ..."
        )

    client = ChatbotEvalClient(
        base_url=args.chatbot_url,
        eval_secret=args.eval_secret,
    )

    if args.question or args.sample_id:
        _resolve_single_question(args, client)
        return

    output_dir = Path(args.output) if args.output else _default_output_dir()
    summary = run_evaluation(
        dataset_path=args.dataset,
        output_dir=output_dir,
        client=client,
        mode=args.mode,
        max_samples=args.max_samples,
        update_baseline=args.update_baseline,
        baseline_path=args.baseline,
        fail_on_regression=args.fail_on_regression,
    )
    print(format_summary(summary))
    print(f"\nDetailed reports written to: {output_dir}")


if __name__ == "__main__":
    main()
