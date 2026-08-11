# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: nhóm Abe
- Repository URL: https://github.com/tdattm/K4-DAY13-2A202601678.git
- Commit SHA cuối tại thời điểm cập nhật report: `f04ab35` (cần cập nhật lại sau commit report/evidence cuối).
- Thành viên và vai trò:
  - Nguyễn Tiến Đạt (2A202601678) — Role A: API & Middleware
  - Lã Phan Hoài An (2A202601846) — Role B: Security Engineer / PII
  - Kiều Phúc Huy (2A202601056) — Role C: Metrics & Dashboard
  - Nguyễn Nam Phong (2A202601320) — Role D: SRE & Alerts Engineer
  - Lê Hồ Quang Huy (2A202602026) — Role E: QA, Tracing & Chief Investigator

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100.
- CP0 baseline: `submission/evidence/health.jpg`, `submission/evidence/metrics-baseline.jpg`, `submission/evidence/cp0-validate-logs.txt`.
- Tổng số traces Langfuse: 20 managed traces (10 baseline/version 1 và 10 candidate/version 2); danh sách tại `submission/evidence/traces-baseline.json` và `traces-candidate.json`.
- Số PII leak còn lại: 0.
- Dashboard: `submission/evidence/dashboard.html` và `submission/evidence/dashboard-runtime.png`.

## 3. Logging và tracing

- Evidence correlation ID: [CHƯA CÓ ảnh/log line riêng; log runtime có correlation ID và CP0 baseline đã lưu].
- Evidence PII redaction: [CHƯA CÓ ảnh/log line riêng; validator ghi nhận 0 PII leak].
- Evidence trace waterfall: payload của trace challenge tại `submission/evidence/trace-waterfall.json`; [CẦN BỔ SUNG ẢNH waterfall từ Langfuse].
- Giải thích một span đáng chú ý: trace `669f47429b92d176724ce6faf894218d` thuộc challenge; cần dùng ảnh/UI để trình bày span RAG chậm.

## 4. Prompt versioning

- Prompt name: `day13-chat` theo cấu hình mặc định của app; cần xác nhận trên Langfuse.
- Version/label baseline: version 1, labels `baseline` và `production`.
- Version/label candidate: version 2, label `candidate`.
- Trace ID của mỗi version: 10 ID version 1 và 10 ID version 2 trong hai manifest evidence; ví dụ baseline `909fb67bf106543270ddd4afc46018b1`, candidate `83bd3cc86f42ad53c7ae9cdaa157d613`.
- Bằng chứng đổi label hoặc rollback: `submission/evidence/prompt-rollback.json` ghi production version 2 trước rollback và version 1 sau rollback; [CẦN BỔ SUNG ẢNH UI nếu giảng viên yêu cầu ảnh].

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: `submission/evidence/dashboard.html`, `submission/evidence/dashboard-runtime.png`.
- Kết quả SRE validator: `HỢP LỆ: 4 SLO/SLI, 4 alert rules và tất cả runbook links tồn tại.`
- SLO đã chọn, reporting window 28 ngày, múi giờ `Asia/Bangkok`:
  - Latency: 99.5% cửa sổ 5 phút có P95 <= 3000 ms.
  - Reliability: 99.0% cửa sổ 5 phút có error rate <= 2%.
  - Cost: tổng cost mỗi ngày <= 2.5 USD.
  - Quality proxy: 95.0% cửa sổ 5 phút có mean quality >= 0.75.
  - Cửa sổ latency/error/quality yêu cầu tối thiểu 20 request/response; thiếu traffic được ghi `no_data`.
- Alert rules: `HighP95Latency`, `HighRequestErrorRate`, `DailyCostBudgetExceeded`, `LowAverageQuality`.
- Runbook: `docs/alerts.md`, gồm triage, mitigation, recovery, escalation và evidence cần lưu.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1`.
- Triệu chứng từ metrics: khi `rag_slow` bật, challenge ghi nhận response latency khoảng 2650–2651 ms; metrics snapshot có P95 2651 ms, error rate 0%.
- Trace ID liên quan: `669f47429b92d176724ce6faf894218d` (các trace còn lại nằm trong `challenge-investigation.json`).
- Log line/correlation ID liên quan: `req-6626cca7` (2651 ms), `req-8cb25506` (2650 ms), `req-1b5f1120` (2651 ms), `req-71fd567f` (2650 ms), `req-d3349609` (2651 ms).
- Root cause: `app/mock_rag.py` thực hiện `time.sleep(2.5)` trong `retrieve()` khi `incidents.STATE["rag_slow"]` bật; log và trace cùng thời gian/feature chứng minh ảnh hưởng ở luồng RAG.
- Fix action: đã tắt practice incident bằng `python scripts/inject_incident.py --scenario rag_slow --disable`; production fix đề xuất là timeout/circuit breaker cho RAG và giới hạn thời gian retrieval.
- Preventive measure: alert P95 latency, trace RAG span, timeout/fallback, test latency regression và dashboard baseline trước/sau incident.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Tiến Đạt (2A202601678) | Correlation ID middleware, context lifecycle, response timing và safe exception responses | `adb1662` | [THÀNH VIÊN BỔ SUNG] |
| Lã Phan Hoài An (2A202601846) | PII patterns và recursive structured-log scrubbing | `f8828a6` | [THÀNH VIÊN BỔ SUNG] |
| Kiều Phúc Huy (2A202601056) | `error_rate_pct`, log enrichment và dashboard 6 panel/runtime renderer | `fad79fe`, `0f58f48`, `d0ce8fb` | [THÀNH VIÊN BỔ SUNG] |
| Nguyễn Nam Phong (2A202601320) | SLO, alert rules, runbook và SRE validator | `5d4419c`, `49a1509`, `a36daf6`, `bfc109e` | [THÀNH VIÊN BỔ SUNG] |
| Lê Hồ Quang Huy (2A202602026) | Automation chạy request cho prompt/trace evidence và chuẩn bị điều tra challenge | `2095b06` | [THÀNH VIÊN BỔ SUNG] |
