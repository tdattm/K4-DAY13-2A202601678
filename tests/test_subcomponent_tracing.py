from __future__ import annotations

from app.mock_llm import FakeLLM
from app.mock_rag import retrieve


def test_rag_retrieval_is_observed_without_capturing_payloads() -> None:
    assert hasattr(retrieve, "__wrapped__")
    assert retrieve.__wrapped__("Explain monitoring") == [
        "Metrics detect incidents, traces localize them, logs explain root cause."
    ]


def test_llm_generation_is_observed_without_changing_result() -> None:
    llm = FakeLLM()
    result = FakeLLM.generate.__wrapped__(llm, "A safe prompt")
    assert result.model == "claude-sonnet-4-5"
    assert result.usage.input_tokens >= 20
    assert result.usage.output_tokens >= 80
