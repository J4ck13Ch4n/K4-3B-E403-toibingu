# Checklist theo slide bài học

Biên soạn từ hai PDF trong `data/vlearn-pack/slides`. Số trang là vị trí PDF (bắt đầu từ 1), không phải số slide in ở chân trang. Câu hỏi và tiêu chí là diễn giải của nhóm. Không yêu cầu học thuộc tên model, giá hoặc số liệu thời điểm trên slide.

Tiến độ = số tiêu chí đạt / tổng tiêu chí bài học; trạng thái chưa kiểm tra tách riêng. Chỉ dùng trong phạm vi hackathon.

## Day 1 — AI & LLM Foundation

Nguồn: `d1-slide-hackathon.pdf` · 29 trang.

### Bức tranh và lịch sử AI

- [ ] Cậu giải thích mối quan hệ giữa AI, machine learning, deep learning, GenAI và LLM bằng ví dụ được không? — Trang PDF 3 (`ai_map_1`)
- [ ] Lọc spam, viết bài và tự xử lý một mục tiêu nhiều bước khác nhau ở đầu ra như thế nào? — Trang PDF 4 (`ai_map_2`)
- [ ] Từ hệ chuyên gia đến ImageNet, Transformer rồi ChatGPT, mỗi bước đã thay đổi điều gì? — Trang PDF 5, 6, 7, 8, 9 (`ai_map_3`)

### LLM sinh văn bản như thế nào?

- [ ] Vì sao cùng một LLM có thể dùng cho chatbot, dịch và viết code? — Trang PDF 10 (`generation_1`)
- [ ] Từ một câu chưa hoàn chỉnh, mô hình tạo ra cả đoạn văn bằng cách nào? — Trang PDF 11, 12 (`generation_2`)
- [ ] Vì sao không thể tính chi phí bằng cách đếm số từ của một đoạn tiếng Việt? — Trang PDF 13 (`generation_3`)

### Context, attention và cách đưa tài liệu

- [ ] Bàn làm việc của mô hình có giới hạn gì khi mình gửi một cuộc chat quá dài? — Trang PDF 14 (`context_1`)
- [ ] Trong câu có đại từ “nó”, attention giúp liên hệ nghĩa với các từ khác như thế nào? — Trang PDF 15 (`context_2`)
- [ ] Nếu tài liệu rất dài, cậu sẽ đưa thông tin nào vào prompt và sắp xếp ra sao? — Trang PDF 16 (`context_3`)

### Tham số và quá trình huấn luyện

- [ ] Tham số model khác context và temperature mình chỉnh lúc gọi như thế nào? — Trang PDF 17 (`training_1`)
- [ ] Vì sao model nhiều tham số hơn không nhất thiết tăng chi phí mỗi token theo cùng tỷ lệ? — Trang PDF 17 (`training_2`)
- [ ] Cậu phân biệt học dự đoán token, học ví dụ trả lời và học từ phản hồi con người được không? — Trang PDF 18, 19 (`training_3`)

### Giới hạn, kiểm chứng và suy luận

- [ ] Vì sao mô hình có thể trả lời tự tin nhưng sai, nhất là với sự kiện mới? — Trang PDF 20 (`limits_1`)
- [ ] Điểm benchmark cao có đủ để tin model làm tốt dữ liệu thực tế của mình không? — Trang PDF 21 (`limits_2`)
- [ ] Chia một bài toán thành các bước có thể giúp gì, và mình còn cần kiểm tra điều gì? — Trang PDF 22 (`limits_3`)

### Từ LLM đến agent

- [ ] LLM trần, LLM có tool, agent lập kế hoạch và multi-agent khác nhau ở năng lực nào? — Trang PDF 23 (`agents_1`)
- [ ] Một agent cần mục tiêu, reasoning, tools, memory và action để làm gì? — Trang PDF 24 (`agents_2`)
- [ ] Sau khi agent dùng một công cụ, bước tiếp theo nên diễn ra như thế nào? — Trang PDF 24 (`agents_3`)

### Chọn model, chi phí và prompt

- [ ] Cậu chọn model thế nào cho tác vụ đơn giản số lượng lớn và tác vụ suy luận khó? — Trang PDF 25, 26 (`practical_1`)
- [ ] Muốn ước tính chi phí một lần gọi API, cậu cần những số nào? — Trang PDF 27 (`practical_2`)
- [ ] Cậu thiết kế prompt tóm tắt một báo cáo với bốn phần nào? — Trang PDF 28 (`practical_3`)

### Temperature và top-p

- [ ] Temperature thấp và cao thay đổi cách chọn token và tính đa dạng ra sao? — Trang PDF 29 (`sampling_slide_1`)
- [ ] Top-p bằng 0,9 chọn phạm vi token như thế nào và khác temperature ở đâu? — Trang PDF 29 (`sampling_slide_2`)
- [ ] Với phân tích cần ổn định và viết ý tưởng đa dạng, cậu dùng các núm vặn này ra sao? — Trang PDF 29 (`sampling_slide_3`)

## Day 2 — Xác định bài toán cho AI

Nguồn: `d2-slide-hackathon.pdf` · 29 trang.

### Tìm đúng vấn đề

- [ ] Vì sao cần Discover và Define trước khi Develop và Deliver? — Trang PDF 3, 4 (`discovery_1`)
- [ ] Cậu tìm một vấn đề đáng giải quanh mình và xác thực nó bằng cách nào? — Trang PDF 4, 5, 6 (`discovery_2`)
- [ ] Nếu nhận brief “làm chatbot AI”, cậu cần hỏi lại những gì trước khi xây? — Trang PDF 7, 8 (`discovery_3`)

### Problem Card và đo tác động

- [ ] Cậu mô tả một bài toán ngắn có người dùng, quy trình, nút thắt và tác động được không? — Trang PDF 9, 10 (`problem_1`)
- [ ] Câu “giảm thời gian xử lý” cần bổ sung gì để biết cải tiến có thành công? — Trang PDF 11 (`problem_2`)
- [ ] Trước khi tự động hóa một bước, cậu cần biết hao phí và hậu quả sai sót như thế nào? — Trang PDF 10 (`problem_3`)
- [ ] Chỉ số kết quả cuối khác các chỉ số đầu vào có thể tác động như thế nào? — Trang PDF 12 (`problem_4`)

### AI có thực sự thêm giá trị?

- [ ] Khung PAIR giúp trả lời ba câu hỏi gì khi cân nhắc AI? — Trang PDF 13 (`pair_1`)
- [ ] Cậu nêu một tác vụ AI có lợi thế và giải thích tại sao rule tĩnh khó xử lý được không? — Trang PDF 14 (`pair_2`)
- [ ] Nếu nội dung cố định hoặc quy trình phải rất dễ dự đoán, cậu có chọn AI không, vì sao? — Trang PDF 15 (`pair_3`)

### Vai trò con người và cấp độ giải pháp

- [ ] Một hệ thống AI làm việc nghiệp vụ cần thêm gì ngoài model? — Trang PDF 16 (`solution_1`)
- [ ] Cậu chọn AI làm thay hay hỗ trợ con người dựa trên những yếu tố nào? — Trang PDF 17 (`solution_2`)
- [ ] Với FAQ cố định, duyệt biểu mẫu và xử lý mục tiêu động nhiều công cụ, cậu chọn cấp nào? — Trang PDF 18, 19, 21 (`solution_3`)

### Các mẫu workflow

- [ ] Khi nào nên chia một tác vụ thành chuỗi gọi AI có gate kiểm tra? — Trang PDF 20 (`workflows_1`)
- [ ] Routing khác gửi mọi yêu cầu đến cùng một model như thế nào? — Trang PDF 20 (`workflows_2`)
- [ ] Cậu giải thích chạy song song rồi tổng hợp hoặc bỏ phiếu dùng trong trường hợp nào? — Trang PDF 20 (`workflows_3`)

### Đánh giá đúng sai và thành công

- [ ] Trong hệ thống phát hiện học viên cần giúp, báo nhầm và bỏ sót khác nhau thế nào? — Trang PDF 22 (`metrics_1`)
- [ ] Precision và recall đo hai điều gì, cậu chọn cân bằng dựa trên đâu? — Trang PDF 23 (`metrics_2`)
- [ ] Cậu viết một tiêu chí thành công gồm chỉ số, ngưỡng và hành động được không? — Trang PDF 24 (`metrics_3`)

### Từ Problem Statement đến quyết định

- [ ] Một Problem Statement cho AI cần nêu gì để người khác biết làm ở đâu và dừng ở đâu? — Trang PDF 27 (`decision_1`)
- [ ] Một demo trả lời đúng vài lần còn thiếu gì trước khi dùng thực tế? — Trang PDF 25, 26 (`decision_2`)
- [ ] Cậu phân biệt khi nào nên Go, Not Yet hoặc No-Go cho một đề xuất AI? — Trang PDF 28, 29 (`decision_3`)
