# Kết quả kiểm thử kỹ thuật — 18/09/2026

Người thực hiện: Codex. Lệnh: `python -m unittest discover -s tests -q`.
Chạy trên Windows với Python 3.14; dùng quyền ngoài sandbox để tạo SQLite trong thư mục tạm. Model được giả lập trong test; không dùng số này làm độ chính xác AI.

| Lần | Giờ Việt Nam | Kết quả | Chi tiết |
|---|---|---|---|
| 1 | 09:27:13 | 32/33 đạt; 1 error | `test_http_roundtrip`: `ConnectionResetError [WinError 10054]` khi đọc phản hồi kiểm tra chặn Origin ngoài; server đã log HTTP 403. Tổng thời gian 0,943 giây. |
| 2 | 09:27:25 | 33/33 đạt | Chạy lại nguyên bộ, không sửa mã ứng dụng hoặc test. Tổng thời gian 0,927 giây. |

Kết quả lần hai cho thấy lỗi kết nối không tái hiện ngay; chưa đủ căn cứ xác định nguyên nhân. Giữ cả hai lần chạy, không ghi thành hai lần đều đạt.

Phạm vi: logic phiên, giới hạn lượt, cập nhật tiến độ, rubric từng ý, bằng chứng, kiểm tra audit giả lập, HTTP và bảo vệ tài nguyên nội bộ. Chưa kiểm tra tương tác trình duyệt hoặc tải nhiều người dùng.

## Sau sửa lỗi nghiêm trọng G17

Ngày 18/09/2026, 09:42:27 (giờ Việt Nam): cùng lệnh chạy toàn bộ **36/36 test đạt**, 1,055 giây. Có thêm ba test chống lộ đáp án, kiểm tra từng ý của temperature và giới hạn phiên trong `tests/test_probe_safety.py`. Chi tiết cùng kết quả AI thật chọn lọc tại [critical-fixes.md](critical-fixes.md).
