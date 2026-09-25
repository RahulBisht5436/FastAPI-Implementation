from unittest.mock import MagicMock

from ragas_eval.collector.trace_collector import collect_trace
from ragas_eval.dataset.schema import GoldenSample, SampleCategory


def test_collect_trace_success():
    sample = GoldenSample(
        id="edu-001",
        question="What is your degree?",
        ground_truth="B.Tech",
        category=SampleCategory.EDUCATION,
    )
    client = MagicMock()
    client.run_eval.return_value = {
        "answer": "Rahul completed a B.Tech.",
        "contexts": ["Education: B.Tech"],
        "context_metadata": [{"file_name": "resume.pdf", "score": 0.9}],
        "retrieval_latency_ms": 12.0,
        "generation_latency_ms": 400.0,
    }

    trace = collect_trace(client, sample)
    assert trace.error is None
    assert trace.answer.startswith("Rahul")
    assert trace.contexts == ["Education: B.Tech"]


def test_collect_trace_failure():
    sample = GoldenSample(
        id="edu-001",
        question="What is your degree?",
        ground_truth="B.Tech",
        category=SampleCategory.EDUCATION,
    )
    client = MagicMock()
    client.run_eval.side_effect = RuntimeError("connection failed")

    trace = collect_trace(client, sample)
    assert trace.error == "connection failed"
    assert trace.answer == ""
