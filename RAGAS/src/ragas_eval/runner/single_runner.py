from __future__ import annotations

from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import evaluate

from ragas_eval.config import DEFAULT_THRESHOLDS, OPENAI_API_KEY, RAGAS_JUDGE_MODEL
from ragas_eval.metrics.registry import get_default_metrics, get_retrieval_metrics


def score_single_trace(
    *,
    question: str,
    answer: str,
    contexts: list[str],
    ground_truth: str,
    mode: str = "full",
) -> dict[str, float]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for RAGAS judge metrics.")

    dataset = Dataset.from_list(
        [
            {
                "user_input": question,
                "response": answer,
                "retrieved_contexts": contexts,
                "reference": ground_truth,
            }
        ]
    )

    judge_llm = ChatOpenAI(model=RAGAS_JUDGE_MODEL, temperature=0)
    judge_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    metrics = get_retrieval_metrics() if mode == "retrieval-only" else get_default_metrics()

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=judge_llm,
        embeddings=judge_embeddings,
        show_progress=False,
    )

    repr_dict = getattr(result, "_repr_dict", {}) or {}
    metric_names = {metric.name for metric in metrics}
    return {
        name: float(value)
        for name, value in repr_dict.items()
        if name in metric_names
    }
