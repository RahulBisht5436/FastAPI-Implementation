from __future__ import annotations

from ragas_eval.client.chatbot_client import ChatbotEvalClient
from ragas_eval.dataset.schema import EvalTraceRow, GoldenDataset, GoldenSample


def collect_trace(
    client: ChatbotEvalClient,
    sample: GoldenSample,
) -> EvalTraceRow:
    try:
        payload = client.run_eval(sample.question)
        return EvalTraceRow(
            sample_id=sample.id,
            question=sample.question,
            answer=payload.get("answer", ""),
            contexts=payload.get("contexts") or [],
            ground_truth=sample.ground_truth,
            category=sample.category.value,
            context_metadata=payload.get("context_metadata") or [],
            retrieval_latency_ms=payload.get("retrieval_latency_ms"),
            generation_latency_ms=payload.get("generation_latency_ms"),
        )
    except Exception as error:
        return EvalTraceRow(
            sample_id=sample.id,
            question=sample.question,
            answer="",
            contexts=[],
            ground_truth=sample.ground_truth,
            category=sample.category.value,
            error=str(error),
        )


def collect_traces(
    client: ChatbotEvalClient,
    dataset: GoldenDataset,
) -> list[EvalTraceRow]:
    traces: list[EvalTraceRow] = []
    for sample in dataset.samples:
        if sample.skip_generation:
            continue
        traces.append(collect_trace(client, sample))
    return traces
