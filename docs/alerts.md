# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: HighP95Latency
- Severity: warning
- SLI/SLO liên quan: `latency_p95_ms`; P95 latency phải nhỏ hơn hoặc bằng 3000 ms trong ít nhất 99.5% các cửa sổ đánh giá 5 phút.
- Điều kiện và thời gian duy trì: Kích hoạt khi `latency_p95_ms > 3000` liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: Người dùng phải chờ lâu để nhận câu trả lời; request có nguy cơ timeout hoặc bị gửi lại, làm tăng traffic và chi phí.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra panel latency để xác nhận P95 vượt 3000 ms; đồng thời đối chiếu traffic và error rate trong cùng khoảng thời gian.
  2. Mở một trace chậm trong Langfuse và xác định span RAG, LLM hoặc sub-component nào chiếm nhiều thời gian nhất.
  3. Lấy correlation ID từ request/trace, tìm log tương ứng và kiểm tra feature, model, latency, error hoặc incident xuất hiện cùng thời điểm.
- Mitigation tạm thời: Giảm concurrency hoặc rate-limit traffic; chuyển sang fallback nhanh hơn nếu có; tạm tắt feature không thiết yếu; rollback thay đổi gần nhất nếu trace và log chứng minh thay đổi đó liên quan.
- Tiêu chí khôi phục: P95 latency trở lại nhỏ hơn hoặc bằng 3000 ms trong ít nhất 5 phút và error rate không tăng bất thường.
- Evidence cần lưu: Thời điểm alert, ảnh metric trước/sau, trace ID của request chậm và correlation ID hoặc log line liên quan.
- Owner: member-d-sre

## Alert 2

- Tên: HighRequestErrorRate
- Severity: critical
- SLI/SLO liên quan: `error_rate_pct`; error rate phải nhỏ hơn hoặc bằng 2% trong ít nhất 99.0% các cửa sổ đánh giá 5 phút.
- Điều kiện và thời gian duy trì: Kích hoạt khi `error_rate_pct > 2` liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: Một phần người dùng không nhận được câu trả lời hoặc nhận HTTP error; request gửi lại có thể làm tăng traffic, latency và chi phí.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra panel error rate, tổng số request và breakdown theo `error_type`; xác nhận alert không xuất phát từ một mẫu traffic quá nhỏ.
  2. Mở một trace lỗi trong Langfuse và xác định span RAG, LLM hoặc sub-component nào thất bại hoặc trả lỗi bất thường.
  3. Lấy correlation ID của request lỗi, tìm log `request_failed` hoặc log lỗi liên quan và đối chiếu `error_type`, feature, model và thời điểm thay đổi cấu hình/deploy.
- Mitigation tạm thời: Chuyển request sang fallback nếu có; tạm tắt feature gây lỗi; rollback thay đổi gần nhất khi có bằng chứng liên quan; rate-limit traffic nếu downstream đang quá tải.
- Tiêu chí khôi phục: Error rate trở lại nhỏ hơn hoặc bằng 2% trong ít nhất 5 phút với lượng request đủ để đánh giá và không còn error type tăng bất thường.
- Evidence cần lưu: Thời điểm alert, tổng request, error rate, error breakdown, trace ID của request lỗi và correlation ID hoặc log line `request_failed`.
- Owner: member-d-sre

## Alert 3

- Tên: DailyCostBudgetExceeded
- Severity: warning
- SLI/SLO liên quan: `daily_cost_usd`; tổng chi phí dịch vụ trong mỗi ngày phải nhỏ hơn hoặc bằng 2.5 USD.
- Điều kiện và thời gian duy trì: Kích hoạt khi `daily_cost_usd > 2.5` liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: Chi phí vận hành vượt ngân sách; hệ thống có thể phải rate-limit, giảm quota hoặc tạm dừng một số tính năng, từ đó ảnh hưởng tới khả năng phục vụ người dùng.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận tổng cost từ đầu ngày đã vượt 2.5 USD; so sánh traffic, cost trên mỗi request và tốc độ tăng cost. Nếu dashboard đang dùng cửa sổ mặc định 60 phút, phải mở rộng time range hoặc tổng hợp log từ đầu ngày.
  2. Kiểm tra token input/output và mở các trace có cost hoặc số token cao nhất; tìm model đắt, prompt quá dài, output bất thường hoặc số lần gọi LLM lặp lại.
  3. Lấy correlation ID của request có cost cao, tìm log `response_sent` tương ứng và đối chiếu `cost_usd`, `tokens_in`, `tokens_out`, feature và model.
- Mitigation tạm thời: Rate-limit feature gây cost cao; giảm giới hạn output token; chuyển sang model rẻ hơn nếu có fallback đã được kiểm chứng; tạm tắt luồng gọi LLM lặp bất thường.
- Tiêu chí khôi phục: Tốc độ tăng cost và cost trên mỗi request trở về mức baseline trong ít nhất 5 phút, đồng thời không còn request có token hoặc số lần gọi LLM bất thường. Vi phạm daily cost vẫn phải được ghi nhận cho tới khi sang cửa sổ ngày mới.
- Evidence cần lưu: Tổng cost từ đầu ngày, traffic, cost trên mỗi request, token trước/sau mitigation, trace ID của request có cost cao và correlation ID hoặc log line `response_sent`.
- Owner: member-d-sre