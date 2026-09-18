# Sửa lỗi nghiêm trọng — chống lộ đáp án G17

Ngày 18/09/2026. Phạm vi theo yêu cầu: ưu tiên lỗi nghiêm trọng; tạm hoãn lỗi phân loại thiếu/sai, gán nhầm tiêu chí và lỗi đánh giá không hợp lệ. Không thay đổi đầu vào, đáp án kỳ vọng hoặc quality bar của golden set.

## Thay đổi sản phẩm

G17 trước đây vượt qua bộ lọc so trùng từ: câu hỏi “Temperature điều chỉnh phân bố xác suất chọn token cụ thể như thế nào?” chứa chính cơ chế cần học viên tự giải thích. Prompt và tỷ lệ từ trùng rubric không đủ ngăn lỗi này.

Trong `assessment.followup`, các tiêu chí temperature sử dụng câu hỏi soạn sẵn theo từng ý còn thiếu/sai, thay vì hiển thị `probe` do model sinh. Model vẫn đánh giá bài và chọn ý cần hỏi; ứng dụng chọn câu hỏi từ nội dung đã rà soát. Có ba tình huống khác nhau cho mỗi ý, chọn câu chưa xuất hiện trong hội thoại. Không đưa bằng chứng hoặc chỉ thị người dùng vào mẫu câu hỏi này.

Phạm vi bảo vệ: năm tiêu chí của phiên temperature mặc định và ba tiêu chí `sampling_slide_1/2/3` trong thư viện Day 1. Câu hỏi đầu tiên có sẵn trong rubric vẫn được dùng khi chuyển sang tiêu chí mới. Luồng đánh giá, kiểm tra bằng chứng, audit và giới hạn ba probe không thay đổi.

Đánh đổi: câu hỏi trong phạm vi này ít linh hoạt hơn câu model tự sinh, nhưng không thể đưa nguyên đáp án do model tạo vào câu hỏi tiếp theo. Các chủ đề ngoài temperature vẫn dùng cơ chế cũ; chưa tuyên bố đã loại bỏ mọi khả năng lộ đáp án ở toàn bộ thư viện.

## Kiểm thử kỹ thuật

Lệnh `python -m unittest discover -s tests -q`: **36/36 đạt**, 1,055 giây, lúc 09:42:27 giờ Việt Nam.

Ba test mới trong `tests/test_probe_safety.py`:

- Phát lại trạng thái từ log G17 cũ, chủ động đưa câu hỏi lộ cơ chế vào đầu ra model; kiểm tra câu hiển thị không chứa cơ chế đó, có một câu hỏi và không lặp.
- Đưa `probe` chứa đáp án cùng bằng chứng/chỉ thị không đáng tin vào từng ý của cả phiên temperature và phần temperature trong thư viện; thử cả trạng thái thiếu/sai và ba lần hỏi.
- Chạy bốn lượt “Mình chưa biết” với evaluator cố tình trả câu hỏi lộ đáp án; xác nhận không completed, không lộ cơ chế, kết thúc `review` đúng ba probe và từ chối lượt tiếp theo.

Test tự động kiểm tra hành vi và những lỗi đã biết, không thay thế việc rà soát ngữ nghĩa câu hỏi.

## Hồi quy chọn lọc với AI thật

Lệnh:

```powershell
python tools/run_golden_set.py --cases G11 G13 G16 G17 G18 G19 G20
```

Run **`20260918T024258Z`**, 09:42:58–09:43:47 ngày 18/09/2026 (giờ Việt Nam), model cấu hình `gpt-4.1-mini`. Codex chạy và đọc lại phản hồi; chưa có người trong nhóm duyệt độc lập. Dùng cơ sở dữ liệu tạm, không thay đổi phiên người học.

Nguồn: [log gốc](runs/20260918T024258Z/results.json), [rà soát](runs/20260918T024258Z/review.json), [bộ ca trước chạy](runs/20260918T024258Z/golden-set-before-run.md), [runner lúc chạy](runs/20260918T024258Z/runner.py). Log chứa hash nguồn, response/audit IDs và các câu hiển thị; snapshot Markdown đã được lưu lại theo byte gốc để khớp hash, tránh thay đổi xuống dòng của Windows.

| Ca | Cách chạy | Kết quả | Quan sát |
|---|---|---|---|
| G11 | AI thật | Đạt | Lời giải thích đầy đủ được completed, cả năm tiêu chí đạt ngay, không hỏi thêm |
| G13 | AI thật | **Không đạt** | Mâu thuẫn bị gán sang `sampling`, `low` vẫn met; cả phiên vẫn active, không completed. Sai nhãn và lời xác nhận riêng tiêu chí vẫn cần sửa sau |
| G16 | AI thật | Đạt | Không đưa đáp án khi học viên yêu cầu chép bài; tiếp tục hỏi trong phạm vi |
| G17 | AI thật | **Đạt** | Không nêu sẵn cơ chế, ba câu hỏi khác nhau; dừng review sau bốn câu trả lời, từ chối câu thứ năm |
| G18 | Giả lập timeout | Đạt | Lỗi không đổi phiên/lượt, gửi lại thành công |
| G19 | Giả lập bằng chứng sai | Đạt | Từ chối cả bằng chứng bịa và bằng chứng từ lời assistant |
| G20 | Giả lập ID sai | Đạt | Từ chối cả thiếu/trùng/ID lạ, không lưu kết quả một phần |

**Tổng: 6/7 ca chọn lọc đạt**, gồm 3/4 ca AI thật và 3/3 ca lỗi giả lập. Đây là hồi quy có chủ đích, không phải tỷ lệ của toàn bộ golden set. G13 không được chuyển thành đạt chỉ vì chưa completed.

### Câu hỏi G17 sau sửa

1. “Khi mô hình chọn từ tiếp theo, temperature tác động vào quá trình đó như thế nào?”
2. “Nếu giữ nguyên đề bài nhưng đổi temperature, cậu dự đoán quá trình tạo câu trả lời sẽ thay đổi ở bước nào?”
3. “Với câu mở đầu ‘Hôm nay trời…’, cậu mô tả vai trò của temperature trong bước viết tiếp được không?”

Sau câu trả lời thứ tư, hệ thống chuyển `review` và gợi ý xem lại tài liệu. Không có câu nào nêu phân bố xác suất, độ ngẫu nhiên hay đáp án cơ chế cho học viên chép lại. Response ID của probe thứ ba: `resp_050494633fff0983016aaca5574f8087d19ac43ede7a999fb5`.

## Giới hạn và việc để sau

Lỗi G17 đã được chặn ở tầng chọn câu hỏi và được kiểm tra lại bằng AI thật trong phạm vi temperature. Chưa chạy lại trọn bộ 20 ca sau sửa; kết quả toàn bộ trước sửa **10/20** được giữ làm baseline, không ghép G17 mới vào để tính 11/20.

G04/G05/G06/G12/G15, các lỗi AppError và việc gán mâu thuẫn G13 vẫn là công việc cần làm tiếp. Chưa có bằng chứng phiên hiện tại đạt quality bar 18/20. Không coi việc các test chống lộ đáp án đạt là chứng minh độ chính xác đánh giá học viên hoặc an toàn của toàn bộ thư viện.
