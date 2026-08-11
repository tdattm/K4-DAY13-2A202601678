# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: Chạy `python scripts/validate_dashboard.py`; contract yêu cầu và đã khai báo đủ 6/6 panel.
- Evidence dashboard: `submission/evidence/dashboard.html` (khi demo cần chụp thêm ảnh runtime có time range và threshold rõ ràng).
- Kết quả SRE validator: Chạy `python scripts/validate_slo_alerts.py`; kiểm tra 4 SLO/SLI, 4 alert rules, threshold/window và toàn bộ runbook link.
- SLO đã chọn (reporting window 28 ngày, múi giờ `Asia/Bangkok`):
  - Latency: 99.5% cửa sổ 5 phút có P95 <= 3000 ms; bảo vệ thời gian chờ của người dùng, error budget 40 bad windows/28 ngày.
  - Reliability: 99.0% cửa sổ 5 phút có error rate <= 2%; bảo vệ khả năng nhận được câu trả lời, error budget 80 bad windows/28 ngày.
  - Cost: tổng cost mỗi ngày <= 2.5 USD; ngăn vượt ngân sách vận hành, không cho phép bad day trong 28 ngày.
  - Quality proxy: 95.0% cửa sổ 5 phút có mean quality >= 0.75; phát hiện regression không biểu hiện qua HTTP error, error budget 403 bad windows/28 ngày.
  - Latency/error/quality chỉ đánh giá alert khi có tối thiểu 20 request/response để tránh nhiễu do sample nhỏ; thiếu dữ liệu được ghi `no_data`, không tự coi là đạt.
- Alert rules: `config/alert_rules.yaml` gồm `HighP95Latency`, `HighRequestErrorRate`, `DailyCostBudgetExceeded` và `LowAverageQuality`; tất cả là symptom-based, có severity, duration, owner, recovery condition và liên kết SLI.
- Runbook: `docs/alerts.md`; mỗi alert có ảnh hưởng người dùng, ba bước triage theo luồng Metrics -> Traces -> Logs, mitigation, recovery, escalation và evidence cần lưu.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
