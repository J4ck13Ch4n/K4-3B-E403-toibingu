## 5 tiêu chí nghiệm thu — canvas

- **1 · Pain cụ thể**
  Học viên vừa hoàn thành buổi Foundation Day 1 (có quiz cuối buổi) — chọn đúng đáp án trắc nghiệm về temperature, nhưng khi được hỏi lại "tại sao" thì không giải thích được cơ chế. Hệ thống hiện tại không có gì phát hiện khoảng cách này, nên lỗ hổng hiểu vẫn tồn tại sau khi "làm đúng bài" và chỉ lộ ra muộn hơn, khi cần áp dụng vào tình huống mới.

- **2 · Bằng chứng**
  **(B) Mining data:** toàn khoá, `understanding_level` chỉ được tutor dùng ở 20/13.494 lượt (0,15%); `move_used = ask_probing_question` chỉ 28/13.494 lượt — đếm bằng group-by trên `tutor_turns.csv`, kiểm lại được trong 2 phút.
  Ví dụ nguyên văn: lượt `T10471` (quiz, học viên K4 chọn đúng "temperature thấp") nối tiếp ngay bởi `T10472` "tại sao temperature thấp giúp ổn định hơn?" và `T10473` "temperature có thể hiểu là gì" — chọn đúng đáp án nhưng phải hỏi lại cơ chế.
  *Cần bổ sung trước CP4: đủ ≥5 ví dụ nguyên văn (hiện mới có 3 lượt của 1 case, cần mining thêm 1–2 case tương tự ở buổi khác).*

- **3 · Problem statement + impact**
  **Problem statement (không chữ AI):** Học viên không có cách nào xác nhận đã thực sự hiểu một khái niệm sau khi học, ngoài trả lời đúng câu hỏi trắc nghiệm — vốn không phân biệt được "nhớ đáp án" và "hiểu cơ chế".
  **Impact 3 phương án sản phẩm** (cùng job executor, cùng bằng chứng — `ask_probing_question` 0,21% + khảo sát 25 người 64%/84%, chi tiết ở `spec.md` §2):
  - *A · TeachBack — dạy lại cho "Mầm"* (chọn) — giữ được vòng hỏi ngược có kiểm soát trước khi kết luận "đã hiểu", khớp đúng tín hiệu tutor hiện tại hiếm hỏi lại (0,21%); khảo sát 84% tin dạy lại giúp hiểu chắc hơn
  - *B · Hỏi ngược ngay trong quiz VLearn* — loại vì phải sửa/tích hợp trực tiếp vào hệ thống quiz thật của VLearn, không khả thi build trong 39 giờ
  - *C · Form tự chấm một lượt, không hỏi lại* — loại vì dễ báo "đạt" cho câu trả lời mới đúng một phần (64% khảo sát chỉ tự nhận giải thích được "một phần"), vi phạm nguyên tắc báo đạt sai phải đắt hơn báo thiếu sai

  **Lý do chọn A:** duy nhất vừa giữ được bước hỏi ngược vừa giới hạn được phạm vi chấm bằng checklist cố định để build trong 39 giờ.

  **Ghi chú phạm vi (không phải bảng impact thứ hai):** chọn xong sản phẩm rồi mới chọn nội dung khởi động là temperature/sampling — duy nhất có sẵn 1 câu quiz thật trong data (golden-set item miễn phí) + checklist 5 điểm rõ ràng, so với attention/self-attention (khái niệm trừu tượng, khó chấm "đạt" rõ ràng) và hallucination (trùng ví dụ mẫu có sẵn trong đề D3) — chi tiết ở `spec.md` §4.

- **4 · Lát cắt prototype được**
  Một học viên · vừa học xong một khái niệm trong buổi giảng · dạy lại khái niệm đó cho agent "học trò AI" · AI so khớp lời giải thích với checklist các điểm bắt buộc rút từ tài liệu (transcript/slide) của khái niệm đó để quyết định đã đủ đúng hay còn hổng, nếu hổng thì hỏi ngược đúng chỗ thiếu mà không tiết lộ đáp án · kết quả là xác nhận "đã dạy được" kèm log điểm nào tự giải thích đúng ngay, điểm nào phải được hỏi mới bổ sung.
  *Ghi chú kỹ thuật (để giữ tiêu chí "build được trong thời gian sự kiện"): checklist không tự trích theo thời gian thực từ transcript bất kỳ — bản demo CP2/CP3 dùng một checklist 5 điểm soạn sẵn cho khái niệm temperature (rút từ `[T04-070]`–`[T04-072]`), câu tổng quát ở trên là hướng thiết kế, không phải phạm vi build thật của prototype.*

- **5 · User sẵn sàng thử**
  Lê Nguyễn Quốc Bảo, Bùi Gia Chính
