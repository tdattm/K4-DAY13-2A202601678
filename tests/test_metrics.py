from collections import Counter

import app.metrics as metrics
from app.metrics import error_rate_pct, percentile, record_error, record_request, snapshot


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_error_rate_pct_no_traffic_is_zero(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 0)
    monkeypatch.setattr(metrics, "ERRORS", Counter())

    assert error_rate_pct() == 0.0


def test_error_rate_pct_reflects_success_and_failure_mix(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 0)
    monkeypatch.setattr(metrics, "ERRORS", Counter())
    monkeypatch.setattr(metrics, "REQUEST_LATENCIES", [])
    monkeypatch.setattr(metrics, "REQUEST_COSTS", [])
    monkeypatch.setattr(metrics, "REQUEST_TOKENS_IN", [])
    monkeypatch.setattr(metrics, "REQUEST_TOKENS_OUT", [])
    monkeypatch.setattr(metrics, "QUALITY_SCORES", [])

    for _ in range(9):
        record_request(latency_ms=100, cost_usd=0.001, tokens_in=10, tokens_out=10, quality_score=0.9)
    record_error("TimeoutError")

    assert error_rate_pct() == 10.0
    assert snapshot()["error_rate_pct"] == 10.0
