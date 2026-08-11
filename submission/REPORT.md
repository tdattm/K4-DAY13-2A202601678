# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: nhóm Abe
- Repository URL: https://github.com/tdattm/K4-DAY13-2A202601678.git
- Commit nộp bài: commit chứa phiên bản báo cáo này; lấy SHA chính xác bằng `git rev-parse HEAD` sau commit cuối.
- Thành viên và vai trò:
  - Nguyễn Tiến Đạt (2A202601678) — Role A: API & Middleware
  - Lã Phan Hoài An (2A202601846) — Role B: Security Engineer / PII
  - Kiều Phúc Huy (2A202601056) — Role C: Metrics & Dashboard
  - Nguyễn Nam Phong (2A202601320) — Role D: SRE & Alerts Engineer
  - Lê Hồ Quang Huy (2A202602026) — Role E: QA, Tracing & Chief Investigator

## 2. Kết quả kỹ thuật và checkpoint

- Tests: 38 passed.
- `validate_logs.py`: 100/100, không thiếu trường bắt buộc/enrichment và không phát hiện PII leak.
- `validate_dashboard.py`: hợp lệ 6/6 panel.
- `validate_slo_alerts.py`: hợp lệ 4 SLO/SLI, 4 alert rules và tất cả runbook links.
- CP0 — Setup và baseline: hoàn thành; evidence tại `submission/evidence/health.jpg`, `metrics-baseline.jpg` và `cp0-validate-logs.txt`.
- CP1 — Logging và PII: hoàn thành; evidence tại `submission/evidence/logging-pii-evidence.json`.
- CP2 — Metrics, traces và dashboard: hoàn thành; có 20 managed traces, prompt v1/v2, rollback, dashboard 6 panel, SLO và alert evidence.
- CP3 — Challenge chính thức: hoàn thành; đã nối metrics → trace → log/correlation ID → root cause và đề xuất fix/prevention.

## 3. Logging và tracing

- Correlation ID: `req-6626cca7` xuất hiện nhất quán ở cả `request_received` và `response_sent`, kèm `user_id_hash`, `session_id`, `feature`, `model`, `env`.
- PII scrubbing: evidence chứa các mẫu email, số điện thoại Việt Nam và thẻ thử nghiệm đã được thay bằng `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]`; validator phát hiện 0 leak.
- Evidence log/correlation/PII: `submission/evidence/logging-pii-evidence.json`.
- Trace waterfall: `submission/evidence/trace-waterfall.jpg`; payload đối chiếu tại `submission/evidence/trace-waterfall.json`.
- Trace challenge `669f47429b92d176724ce6faf894218d` có end-to-end latency khoảng 2.65 giây và session `k4-challenge-s01`.
- Sau khi bổ sung explicit child spans, trace `ffd7a0b5068630e95dd1b231704a5670` ghi nhận `rag.retrieve` 2500 ms và `llm.generate` 151 ms; payload kiểm chứng tại `submission/evidence/subcomponent-trace.json`. Instrumentation nằm trong `app/mock_rag.py` và `app/mock_llm.py`.

## 4. Prompt versioning

- Prompt managed trên Langfuse: `day13-chat`.
- Version 1: label `baseline`; label `production` được đưa trở lại version 1 sau rollback.
- Version 2: label `candidate`; từng được gắn `production` trước thao tác rollback.
- Có 10 trace version 1 trong `submission/evidence/traces-baseline.json` và 10 trace version 2 trong `submission/evidence/traces-candidate.json`.
- Trace mẫu: baseline `909fb67bf106543270ddd4afc46018b1`; candidate `83bd3cc86f42ad53c7ae9cdaa157d613`.
- Evidence danh sách version: `submission/evidence/prompt-versions.jpg` và `prompt-versions.json`.
- Evidence trước/sau rollback: `submission/evidence/prompt-production-v2.jpg`, `prompt-production-v1-rollback.jpg` và `prompt-rollback.json`.

## 5. Dashboard, SLO và alerts

- Dashboard runtime và contract: `submission/evidence/dashboard-runtime.png`, `dashboard.html`, `config/dashboard.yaml`.
- Sáu nhóm chỉ số: latency P50/P95/P99, traffic, error rate/breakdown, cost, tokens và quality proxy.
- SLO reporting window 28 ngày, múi giờ `Asia/Bangkok`:
  - Latency: 99.5% cửa sổ đủ traffic có P95 ≤ 3000 ms.
  - Reliability: 99.0% cửa sổ đủ traffic có error rate ≤ 2%.
  - Cost: tổng cost mỗi ngày ≤ 2.5 USD.
  - Quality proxy: 95.0% cửa sổ đủ traffic có mean quality ≥ 0.75.
- Alert rules: `HighP95Latency`, `HighRequestErrorRate`, `DailyCostBudgetExceeded`, `LowAverageQuality`.
- SLO/alerts/runbook: `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md`.
- Evidence validator: `submission/evidence/sre-validators.png`.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1`; incident: `rag_slow`.
- Metrics của năm response challenge: traffic 5, P50/P95/P99 đều 2651 ms, error rate 0%, quality trung bình 0.84; xem `submission/evidence/challenge-metrics.json`.
- Trace đại diện: `669f47429b92d176724ce6faf894218d`; session `k4-challenge-s01`; trace latency khoảng 2.65 giây.
- Correlation ID đại diện: `req-6626cca7`; log `response_sent` ghi latency 2651 ms. Bốn ID còn lại và trace tương ứng nằm trong `submission/evidence/challenge-investigation.json`.
- Root cause: `app/mock_rag.py` gọi `time.sleep(2.5)` trong `retrieve()` khi `incidents.STATE["rag_slow"]` bật. Metrics xác định tail latency tăng, trace xác nhận request chậm end-to-end, còn log/correlation ID và source code khoanh vùng cơ chế gây chậm.
- Mitigation đã thực hiện: tắt incident bằng `python scripts/inject_incident.py --scenario rag_slow --disable`.
- Fix đề xuất: timeout/circuit breaker cho retrieval và fallback khi RAG quá chậm. Explicit `rag.retrieve` và `llm.generate` child spans đã được bổ sung để lần điều tra sau xác định thời gian từng sub-component trực tiếp trên waterfall.
- Prevention: alert P95 latency, latency regression test và so sánh dashboard/trace trước–sau thay đổi.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Tiến Đạt (2A202601678) | Correlation ID middleware, context lifecycle, response timing và safe exception responses | `adb1662` | Chưa được thành viên cung cấp; cần Nguyễn Tiến Đạt xác nhận trước khi nộp. |
| Lã Phan Hoài An (2A202601846) | PII patterns và recursive structured-log scrubbing | `f8828a6` | Hiểu cách dùng regex nhận diện PII và viết processor đệ quy cho `structlog` để làm sạch JSON lồng nhau mà vẫn giữ metrics. |
| Kiều Phúc Huy (2A202601056) | `error_rate_pct`, log enrichment và dashboard 6 panel/runtime renderer | `fad79fe`, `0f58f48`, `d0ce8fb` | Chưa được thành viên cung cấp; cần Kiều Phúc Huy xác nhận trước khi nộp. |
| Nguyễn Nam Phong (2A202601320) | SLO, alert rules, runbook và SRE validator | `5d4419c`, `49a1509`, `a36daf6`, `bfc109e` | Hiểu cách thiết lập SLI/SLO cho latency, reliability, cost, quality và xây alert rules gắn với runbook xử lý sự cố. |
| Lê Hồ Quang Huy (2A202602026) | Load test, prompt/traces, rollback evidence và điều tra challenge | `2095b06`, `0148867` | Chưa được thành viên cung cấp; cần Lê Hồ Quang Huy xác nhận trước khi nộp. |

## 8. Danh sách evidence

- CP0: `health.jpg`, `metrics-baseline.jpg`, `cp0-validate-logs.txt`.
- CP1: `logging-pii-evidence.json`.
- CP2: `dashboard-runtime.png`, `dashboard.html`, `sre-validators.png`, `traces-baseline.json`, `traces-candidate.json`, `trace-waterfall.jpg`, `trace-waterfall.json`, `prompt-versions.jpg`, `prompt-versions.json`, `prompt-production-v2.jpg`, `prompt-production-v1-rollback.jpg`, `prompt-rollback.json`.
- CP3: `challenge-metrics.json`, `challenge-investigation.json`, `trace-waterfall.jpg`, `subcomponent-trace.json`, `logging-pii-evidence.json`.

Tất cả đường dẫn evidence ở trên tương đối với thư mục `submission/evidence/`.
