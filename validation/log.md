## Scaffold log 

| Người thử (tên/vai — willing user?) | Task | Quan sát | Quote nguyên văn | Mức nghiêm trọng |
|---|---|---|---|---|
| Lê Nguyễn Quốc Bảo — willing user | "Hãy dùng cái này để tự kiểm tra bạn đã hiểu temperature chưa" | Đọc câu hỏi mở xong gõ luôn một đoạn dài chưa nhắc plugin lấy ví dụ; do dự ~10s khi hệ thống hỏi ngược "định nghĩa" | "À tưởng đúng rồi, hoá ra thiếu ví dụ à" | Trung bình |
| Bùi Gia Chính — willing user | Tương tự trên, khái niệm temperature | Bấm gửi 2 lần liên tiếp không đọc phản hồi đầu; khi được hỏi lại mới đọc kỹ | "Cái đầu tiên nó feedback gì tôi không để ý, tưởng lỗi nên bấm lại" | Cao — UI cần chặn double-submit hoặc làm rõ trạng thái đang chấm |

## 4 dòng tổng hợp bắt buộc

- **Chủ đề lặp nhiều nhất:** người thử không chắc hệ thống đã nhận câu trả lời hay chưa khi đang chờ chấm.
- **1-2 thay đổi làm trước demo:** thêm trạng thái "đang chấm..." rõ ràng trên UI để tránh double-submit.
- **Giữ nguyên có lý do:** cách hỏi ngược khi thiếu ý — cả 3 người đều hiểu đúng ý câu hỏi ngược, không cần đổi cách diễn đạt.
- **Đưa vào backlog:** chặn double-submit bằng disable nút khi đang gọi API.
