from __future__ import annotations

import re

from fastapi.testclient import TestClient

from app import logging_config, main
from app.main import app


def test_request_without_id_receives_generated_correlation_id() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert re.fullmatch(r"req-[0-9a-f]{8}", response.headers["x-request-id"])


def test_request_with_id_preserves_correlation_id_and_response_time() -> None:
    request_id = "request-from-client"

    with TestClient(app) as client:
        response = client.get("/health", headers={"x-request-id": request_id})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == request_id
    assert float(response.headers["x-response-time-ms"]) >= 0


def test_sequential_requests_do_not_share_correlation_id() -> None:
    with TestClient(app) as client:
        first = client.get("/health", headers={"x-request-id": "first-request"})
        second = client.get("/health")

    assert first.headers["x-request-id"] == "first-request"
    assert re.fullmatch(r"req-[0-9a-f]{8}", second.headers["x-request-id"])
    assert second.headers["x-request-id"] != first.headers["x-request-id"]


def test_invalid_request_has_correlation_headers_and_safe_json_response() -> None:
    private_input = "private-input-value"

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "invalid-chat-request"},
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "",
                "unused": private_input,
            },
        )

    assert response.status_code == 422
    assert response.headers["x-request-id"] == "invalid-chat-request"
    assert float(response.headers["x-response-time-ms"]) >= 0
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"detail": "Request validation failed"}
    assert private_input not in response.text


def test_chat_failure_has_correlation_headers_and_safe_json_response(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(logging_config, "LOG_PATH", tmp_path / "logs.jsonl")

    def raise_upstream_error(**_kwargs):
        raise RuntimeError("upstream details must not reach the client")

    monkeypatch.setattr(main.agent, "run", raise_upstream_error)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "failing-chat-request"},
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "Explain observability",
            },
        )

    assert response.status_code == 500
    assert response.headers["x-request-id"] == "failing-chat-request"
    assert float(response.headers["x-response-time-ms"]) >= 0
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"detail": "Internal server error"}
    assert "upstream details" not in response.text
