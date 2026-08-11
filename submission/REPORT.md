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
- Tổng số traces Langfuse: [CHƯA XÁC NHẬN — hai manifest baseline/candidate có tổng 20 request nhưng `trace_ids` còn rỗng].
- Số PII leak còn lại: 0.
- Dashboard: `submission/evidence/dashboard.html` và `submission/evidence/dashboard-runtime.png`.

## 3. Logging và tracing

- Evidence correlation ID: [CHƯA CÓ ảnh/log line riêng; log runtime có correlation ID và CP0 baseline đã lưu].
- Evidence PII redaction: [CHƯA CÓ ảnh/log line riêng; validator ghi nhận 0 PII leak].
- Evidence trace waterfall: [CHƯA CÓ — cần chụp từ Langfuse].
- Giải thích một span đáng chú ý: [CHƯA ĐIỀU TRA challenge].

## 4. Prompt versioning

- Prompt name: `day13-chat` theo cấu hình mặc định của app; cần xác nhận trên Langfuse.
- Version/label baseline: [CHƯA XÁC NHẬN TRÊN LANGFUSE].
- Version/label candidate: [CHƯA XÁC NHẬN TRÊN LANGFUSE].
- Trace ID của mỗi version: [CHƯA CÓ trace ID thật; không dùng correlation ID thay thế].
- Bằng chứng đổi label hoặc rollback: [CHƯA CÓ ảnh trước/sau trên Langfuse].

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
- Triệu chứng từ metrics: [CHƯA CHẠY/CHƯA GHI KẾT QUẢ challenge].
- Trace ID liên quan: [CHƯA CÓ].
- Log line/correlation ID liên quan: [CHƯA CÓ].
- Root cause: [CHƯA KẾT LUẬN; cần evidence Metrics → Traces → Logs].
- Fix action: [CHƯA CÓ].
- Preventive measure: [CHƯA CÓ].

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Tiến Đạt (2A202601678) | Correlation ID middleware, context lifecycle, response timing và safe exception responses | `adb1662` | [THÀNH VIÊN BỔ SUNG] |
| Lã Phan Hoài An (2A202601846) | PII patterns và recursive structured-log scrubbing | `f8828a6` | Hiểu cách dùng Regex để nhận diện dữ liệu nhạy cảm (PII); biết cách viết custom processor cho `structlog` bằng hàm đệ quy để tự động làm sạch PII trong các cấu trúc JSON lồng nhau mà không làm mất các metrics quan trọng. |
| Kiều Phúc Huy (2A202601056) | `error_rate_pct`, log enrichment và dashboard 6 panel/runtime renderer | `fad79fe`, `0f58f48`, `d0ce8fb` | [THÀNH VIÊN BỔ SUNG] |
| Nguyễn Nam Phong (2A202601320) | SLO, alert rules, runbook và SRE validator | `5d4419c`, `49a1509`, `a36daf6`, `bfc109e` | Hiểu cách thiết lập các chỉ số SLOs/SLIs quan trọng (Latency, Reliability, Cost, Quality) cho hệ thống AI. Nắm rõ quy trình xây dựng Alert rules kết hợp với Runbook để xử lý sự cố hiệu quả. |
| Lê Hồ Quang Huy (2A202602026) | Automation chạy request cho prompt/trace evidence và chuẩn bị điều tra challenge | `2095b06` | [THÀNH VIÊN BỔ SUNG] |
