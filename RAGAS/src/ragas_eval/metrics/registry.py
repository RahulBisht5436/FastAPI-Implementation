from __future__ import annotations

from ragas.metrics import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)


def get_default_metrics():
    return [
        Faithfulness(),
        AnswerRelevancy(),
        ContextPrecision(),
        ContextRecall(),
    ]


def get_retrieval_metrics():
    return [
        ContextPrecision(),
        ContextRecall(),
    ]
