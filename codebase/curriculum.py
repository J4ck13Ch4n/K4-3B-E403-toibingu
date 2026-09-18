"""Reviewed question bank derived from the two local slide decks.

Page numbers are 1-based PDF pages, NOT the original slide footer numbers.
Rules and review notes are paraphrases, not quotations or live extracted content.
"""


def section(sid, title, rows):
    return {'id': sid, 'title': title, 'criteria': [
        {'id': f'{sid}_{i}', 'label': label, 'question': question, 'pages': pages,
         'rule': rule, 'review': rule, 'source': 'Trang PDF ' + ', '.join(map(str, pages))}
        for i, (label, pages, question, rule) in enumerate(rows, 1)]}


LESSONS = [
    {'id': 'day1', 'title': 'AI & LLM Foundation', 'day': 'Day 1', 'file': 'd1-slide-hackathon.pdf',
     'description': 'Từ bức tranh AI đến cơ chế LLM, agent và cách sử dụng model.', 'page_count': 29,
     'sections': [
         section('ai_map', 'Bức tranh và lịch sử AI', [
             ('AI, ML, Deep Learning và LLM', [3], 'Cậu giải thích mối quan hệ giữa AI, machine learning, deep learning, GenAI và LLM bằng ví dụ được không?', 'Phân biệt AI là phạm vi rộng, ML học từ dữ liệu, deep learning dùng mạng nhiều tầng, GenAI sinh nội dung và LLM chuyên ngôn ngữ; LLM không đồng nghĩa toàn bộ AI.'),
             ('Phân loại, sinh nội dung, hành động', [4], 'Lọc spam, viết bài và tự xử lý một mục tiêu nhiều bước khác nhau ở đầu ra như thế nào?', 'Phân biệt discriminative cho nhãn/dự đoán, generative sinh nội dung và agentic lập kế hoạch/dùng công cụ/hành động theo mục tiêu, gắn đúng ví dụ.'),
             ('Các bước ngoặt của AI', [5,6,7,8,9], 'Từ hệ chuyên gia đến ImageNet, Transformer rồi ChatGPT, mỗi bước đã thay đổi điều gì?', 'Giải thích hệ chuyên gia mã hóa luật miền hẹp; dữ liệu gán nhãn lớn hỗ trợ bước tiến học máy; Transformer dùng attention xử lý ngữ cảnh; ChatGPT đưa model đến người dùng qua giao diện hội thoại. Không yêu cầu thuộc số liệu hoặc ngày tháng.')]),
         section('generation', 'LLM sinh văn bản như thế nào?', [
             ('Model khác sản phẩm chatbot', [10], 'Vì sao cùng một LLM có thể dùng cho chatbot, dịch và viết code?', 'LLM là mô hình nền học dự đoán token trên dữ liệu rộng, dùng chung cho nhiều tác vụ; chatbot là một sản phẩm bao quanh model.'),
             ('Vòng lặp sinh token', [11,12], 'Từ một câu chưa hoàn chỉnh, mô hình tạo ra cả đoạn văn bằng cách nào?', 'Mô hình tạo phân bố xác suất token tiếp theo, chọn token, nối token vào ngữ cảnh và lặp lại; không xuất cả đoạn một lần hay chỉ tra một câu có sẵn.'),
             ('Token không phải luôn là từ', [13], 'Vì sao không thể tính chi phí bằng cách đếm số từ của một đoạn tiếng Việt?', 'Token là mảnh văn bản, một từ có thể thành nhiều token, dấu/ký tự cũng ảnh hưởng; số token phụ thuộc tokenizer và nội dung, không có tỷ lệ từ-token cố định.')]),
         section('context', 'Context, attention và cách đưa tài liệu', [
             ('Giới hạn context', [14], 'Bàn làm việc của mô hình có giới hạn gì khi mình gửi một cuộc chat quá dài?', 'Context chứa thông tin mô hình nhìn thấy trong lần gọi, có giới hạn token; quá dài có thể bỏ sót thông tin và tăng chi phí/độ trễ, không đồng nghĩa bộ nhớ vĩnh viễn.'),
             ('Attention và ngữ cảnh', [15], 'Trong câu có đại từ “nó”, attention giúp liên hệ nghĩa với các từ khác như thế nào?', 'Attention tính mức liên quan giữa token để tổng hợp thông tin theo ngữ cảnh, giúp xác định đại từ liên quan đối tượng nào; cần giải thích quan hệ thay vì chỉ nhắc từ attention.'),
             ('Quản lý context và retrieval', [16], 'Nếu tài liệu rất dài, cậu sẽ đưa thông tin nào vào prompt và sắp xếp ra sao?', 'Chọn đoạn liên quan bằng retrieval/RAG, bỏ nhiễu hoặc tóm tắt lịch sử; đặt yêu cầu quan trọng rõ ở đầu/cuối. RAG cung cấp dữ liệu trong context, không bảo đảm nhớ hoặc đúng tuyệt đối.')]),
         section('training', 'Tham số và quá trình huấn luyện', [
             ('Weights khác núm vặn khi sử dụng', [17], 'Tham số model khác context và temperature mình chỉnh lúc gọi như thế nào?', 'Weights là các giá trị học trong huấn luyện, thường cố định khi suy luận; thay context/temperature lúc gọi không trực tiếp huấn luyện lại weights.'),
             ('Dense và MoE', [17], 'Vì sao model nhiều tham số hơn không nhất thiết tăng chi phí mỗi token theo cùng tỷ lệ?', 'Dense sử dụng toàn bộ mạng liên quan mỗi token; MoE kích hoạt một phần chuyên gia, nên tổng tham số khác tham số hoạt động. Không yêu cầu tên model hoặc số liệu trên slide.'),
             ('Pre-training, SFT và phản hồi', [18,19], 'Cậu phân biệt học dự đoán token, học ví dụ trả lời và học từ phản hồi con người được không?', 'Pre-training học từ nhiều token; SFT học ví dụ hướng dẫn/trả lời; RLHF dùng đánh giá/xếp hạng để học mô hình thưởng và tối ưu phản hồi, DPO trực tiếp dùng ưu tiên. Luyện suy luận dùng tác vụ kiểm chứng được; không yêu cầu công thức.')]),
         section('limits', 'Giới hạn, kiểm chứng và suy luận', [
             ('Cutoff và hallucination', [20], 'Vì sao mô hình có thể trả lời tự tin nhưng sai, nhất là với sự kiện mới?', 'Kiến thức huấn luyện có cutoff; sinh câu hợp ngữ cảnh không đồng nghĩa xác minh sự thật. Cần dữ liệu mới qua context/tools/retrieval và kiểm chứng.'),
             ('Benchmark và học đường tắt', [21], 'Điểm benchmark cao có đủ để tin model làm tốt dữ liệu thực tế của mình không?', 'Không; model có thể dựa vào tín hiệu tương quan/đường tắt như số link thay vì nội dung. Cần kiểm thử dữ liệu và trường hợp biên của tác vụ thật.'),
             ('Suy luận nhiều bước', [22], 'Chia một bài toán thành các bước có thể giúp gì, và mình còn cần kiểm tra điều gì?', 'Phân rã bài toán giúp theo dõi các phép tính/quan hệ trung gian thay vì đoán đáp án; vẫn phải kiểm tra kết quả, không khẳng định cứ suy luận nhiều bước là chắc đúng.')]),
         section('agents', 'Từ LLM đến agent', [
             ('Các mức năng lực agent', [23], 'LLM trần, LLM có tool, agent lập kế hoạch và multi-agent khác nhau ở năng lực nào?', 'Phân biệt sinh/suy luận; truy cập công cụ/dữ liệu; tự chia bước và kiểm tra; phối hợp nhiều agent chuyên biệt. Agent là hệ thống vận hành model, không nhất thiết model mới.'),
             ('Các thành phần agent', [24], 'Một agent cần mục tiêu, reasoning, tools, memory và action để làm gì?', 'Giải thích vai trò mục tiêu, suy luận/chia bước, công cụ tương tác, bộ nhớ lưu tiến trình và hành động tạo kết quả; không chỉ liệt kê tên.'),
             ('Vòng lặp hành động', [24], 'Sau khi agent dùng một công cụ, bước tiếp theo nên diễn ra như thế nào?', 'Quan sát kết quả, ghi/đọc tiến trình, điều chỉnh bước tiếp theo và lặp tới mục tiêu; không coi một câu trả lời văn bản là đã thực thi công việc.')]),
         section('practical', 'Chọn model, chi phí và prompt', [
             ('Chọn theo tác vụ', [25,26], 'Cậu chọn model thế nào cho tác vụ đơn giản số lượng lớn và tác vụ suy luận khó?', 'Bắt đầu model đủ tốt/đủ rẻ, kiểm thử chất lượng tác vụ rồi nâng cấp khi cần; cân nhắc kiểm soát dữ liệu/self-host và chi phí vận hành. Không bắt thuộc model hay giá có thể lỗi thời.'),
             ('Chi phí input và output', [27], 'Muốn ước tính chi phí một lần gọi API, cậu cần những số nào?', 'Tính riêng số token input nhân đơn giá input và output nhân đơn giá output rồi cộng, đúng đơn vị tính giá; input gồm prompt/context/lịch sử; kiểm tra usage, không coi hệ số 3–5 là hằng số mọi model.'),
             ('Bốn phần prompt', [28], 'Cậu thiết kế prompt tóm tắt một báo cáo với bốn phần nào?', 'Phân biệt system instruction định vai/ràng buộc, yêu cầu user, context/tài liệu và định dạng đầu ra; nêu cách áp dụng hợp lý cho báo cáo.')]),
         section('sampling_slide', 'Temperature và top-p', [
             ('Phân bố khi đổi temperature', [29], 'Temperature thấp và cao thay đổi cách chọn token và tính đa dạng ra sao?', 'Thấp tập trung vào token xác suất cao, thường ổn định hơn; cao làm phân bố phẳng hơn và đa dạng hơn. Không bảo đảm luôn chính xác/giống hệt hoặc bổ sung tri thức.'),
             ('Top-p khoanh tập ứng viên', [29], 'Top-p bằng 0,9 chọn phạm vi token như thế nào và khác temperature ở đâu?', 'Top-p giữ nhóm token xác suất cao theo ngưỡng cộng dồn 0,9 rồi chuẩn hóa/lấy mẫu; temperature điều chỉnh phân bố xác suất, không phải ngưỡng cộng dồn hoặc số lượng token cố định.'),
             ('Chọn cấu hình theo mục đích', [29], 'Với phân tích cần ổn định và viết ý tưởng đa dạng, cậu dùng các núm vặn này ra sao?', 'Chọn temperature thấp cho ổn định, cao hơn cho đa dạng, vẫn kiểm chứng; thường thử thay một trong temperature/top-p để hiểu tác động. Các núm chỉ đổi lấy mẫu, không làm model có thêm tri thức.')])]},
    {'id': 'day2', 'title': 'Xác định bài toán cho AI', 'day': 'Day 2', 'file': 'd2-slide-hackathon.pdf',
     'description': 'Từ vấn đề thực tế đến quyết định giải pháp và tiêu chí thành công.', 'page_count': 29,
     'sections': [
         section('discovery', 'Tìm đúng vấn đề', [
             ('Double Diamond', [3,4], 'Vì sao cần Discover và Define trước khi Develop và Deliver?', 'Hai pha đầu mở rộng bằng khảo sát/quan sát rồi hội tụ xác định vấn đề; hai pha sau mở rộng giải pháp rồi chọn/triển khai; tránh giải tốt sai vấn đề.'),
             ('Quan sát và bằng chứng', [4,5,6], 'Cậu tìm một vấn đề đáng giải quanh mình và xác thực nó bằng cách nào?', 'Nhận diện người gặp pain, công việc lặp/tốn thời gian, hiểu lĩnh vực; dùng quan sát/phỏng vấn/log/dữ liệu xác thực thay vì chỉ nghĩ giải pháp công nghệ.'),
             ('Tránh solution-first', [7,8], 'Nếu nhận brief “làm chatbot AI”, cậu cần hỏi lại những gì trước khi xây?', 'Làm rõ nhu cầu/workflow/bottleneck/baseline/đo thành công/ranh giới, cân nhắc giải pháp phi AI và giá trị AI bổ sung; không mặc định chatbot là câu trả lời.')]),
         section('problem', 'Problem Card và đo tác động', [
             ('Problem Card cụ thể', [9,10], 'Cậu mô tả một bài toán ngắn có người dùng, quy trình, nút thắt và tác động được không?', 'Nêu actor cụ thể, bước quy trình hiện tại, nút thắt và hệ quả; tách phát biểu vấn đề khỏi giải pháp, có hướng/chỉ số kiểm tra thành công.'),
             ('Baseline, target, measurement', [11], 'Câu “giảm thời gian xử lý” cần bổ sung gì để biết cải tiến có thành công?', 'Có số hiện trạng baseline, mục tiêu định lượng và cách đo/thu thập trong phạm vi rõ ràng; ví dụ con số tự đặt phải nói là giả định.'),
             ('Chi phí và phạm vi lỗi', [10], 'Trước khi tự động hóa một bước, cậu cần biết hao phí và hậu quả sai sót như thế nào?', 'Xác định thời gian/chi phí/tần suất hoặc tác động đo được; xác định thiệt hại khi sai, giới hạn tự quyết và điểm con người phê duyệt, không chỉ nêu lợi ích.'),
             ('Output metric và input metrics', [12], 'Chỉ số kết quả cuối khác các chỉ số đầu vào có thể tác động như thế nào?', 'Output metric phản ánh giá trị/kết quả cuối như thời gian hoàn tất; input metrics là các đòn bẩy như độ đúng phân loại, chuyển tiếp hoặc thời gian chỉnh bản nháp; cần đo quan hệ giữa cải thiện đòn bẩy và kết quả.')]),
         section('pair', 'AI có thực sự thêm giá trị?', [
             ('Ba quyết định PAIR', [13], 'Khung PAIR giúp trả lời ba câu hỏi gì khi cân nhắc AI?', 'Xác định nhu cầu/giá trị AI, chọn tự động hóa hay hỗ trợ, định nghĩa thành công/hàm thưởng; gắn với vấn đề người dùng thay vì chỉ chọn model.'),
             ('Trường hợp AI có lợi thế', [14], 'Cậu nêu một tác vụ AI có lợi thế và giải thích tại sao rule tĩnh khó xử lý được không?', 'Ví dụ ngôn ngữ tự nhiên/gợi ý/cá nhân hóa/dự đoán/phát hiện biến đổi, giải thích tính đa dạng/phụ thuộc ngữ cảnh hoặc học dữ liệu; không coi mọi việc đều cần AI.'),
             ('Khi nên không dùng AI', [15], 'Nếu nội dung cố định hoặc quy trình phải rất dễ dự đoán, cậu có chọn AI không, vì sao?', 'Cân nhắc rule/hiển thị tĩnh khi giải quyết được; giải thích chi phí/độ trễ, minh bạch, hậu quả lỗi hoặc quyền tự làm của người dùng có thể khiến AI không đáng dùng.')]),
         section('solution', 'Vai trò con người và cấp độ giải pháp', [
             ('Hệ thống không chỉ có model', [16], 'Một hệ thống AI làm việc nghiệp vụ cần thêm gì ngoài model?', 'Giải thích context cung cấp tri thức, planning điều phối, tools nối hệ thống; model đọc hiểu/suy luận không tự thay toàn bộ hệ thống.'),
             ('Automate hay augment', [17], 'Cậu chọn AI làm thay hay hỗ trợ con người dựa trên những yếu tố nào?', 'Xét tính lặp/khả năng scale và đáp án đồng thuận so với stakes/trách nhiệm/ý muốn tự làm; cần giám sát, preview/edit/undo thích hợp, phân biệt vai trò với cấp kỹ thuật.'),
             ('Rule, workflow hay agent', [18,19,21], 'Với FAQ cố định, duyệt biểu mẫu và xử lý mục tiêu động nhiều công cụ, cậu chọn cấp nào?', 'Rule cho logic rõ ổn định, workflow cho các bước/gate định sẵn có LLM, agent cho tự quyết nhiều bước/công cụ; chọn mức đơn giản đủ giá trị với kiểm soát rủi ro, không bắt nâng tuần tự.')]),
         section('workflows', 'Các mẫu workflow', [
             ('Prompt chaining', [20], 'Khi nào nên chia một tác vụ thành chuỗi gọi AI có gate kiểm tra?', 'Các bước phụ thuộc tuần tự, có cổng kiểm tra dừng/chuyển khi không đạt; ví dụ outline rồi kiểm tra rồi viết; đổi thêm độ trễ lấy kiểm soát chất lượng.'),
             ('Routing', [20], 'Routing khác gửi mọi yêu cầu đến cùng một model như thế nào?', 'Phân loại đầu vào rồi chuyển nhánh/model chuyên biệt, ví dụ FAQ/refund/kỹ thuật hoặc dễ/rẻ khó/mạnh, nhằm tối ưu từng loại.'),
             ('Parallelization', [20], 'Cậu giải thích chạy song song rồi tổng hợp hoặc bỏ phiếu dùng trong trường hợp nào?', 'Chia phần độc lập hoặc nhiều đánh giá chạy song song, tổng hợp/vote sau đó; khác chuỗi phụ thuộc, có thể giảm rủi ro một đầu ra sai nhưng không bảo đảm đúng.')]),
         section('metrics', 'Đánh giá đúng sai và thành công', [
             ('False positive và false negative', [22], 'Trong hệ thống phát hiện học viên cần giúp, báo nhầm và bỏ sót khác nhau thế nào?', 'FP báo/gợi ý can thiệp khi không đúng, FN bỏ sót nhu cầu thật; mô tả thiệt hại khác nhau và chi phí không đối xứng, cần cân nhắc người dùng.'),
             ('Precision và recall', [23], 'Precision và recall đo hai điều gì, cậu chọn cân bằng dựa trên đâu?', 'Precision TP/(TP+FP), recall TP/(TP+FN) hoặc diễn giải đúng hai mẫu số; cân nhắc báo nhầm/bỏ sót và test người dùng, không có ngưỡng luôn tối ưu.'),
             ('Metric dẫn đến hành động', [24], 'Cậu viết một tiêu chí thành công gồm chỉ số, ngưỡng và hành động được không?', 'Đưa metric cụ thể, ngưỡng/khoảng đo có nghĩa và hành động khi vượt/không đạt; xét tác động nhóm người dùng và review định kỳ. Con số ví dụ không phải quy tắc bắt buộc.')]),
         section('decision', 'Từ Problem Statement đến quyết định', [
             ('Problem Statement đủ phạm vi', [27], 'Một Problem Statement cho AI cần nêu gì để người khác biết làm ở đâu và dừng ở đâu?', 'Có actor, workflow, bottleneck, impact, success metric, boundary; điểm AI can thiệp, mức rule/workflow/agent, rủi ro và HITL. Chấp nhận diễn đạt tương đương có đủ ý.'),
             ('Demo khác production', [25,26], 'Một demo trả lời đúng vài lần còn thiếu gì trước khi dùng thực tế?', 'Cần baseline, dữ liệu test và edge cases/tiêu chí pass-fail-HITL; đánh giá tác vụ, quy trình, rủi ro; logging/fallback/rollback và người vận hành. Không coi vài ví dụ là đủ.'),
             ('Go, Not Yet và No-Go', [28,29], 'Cậu phân biệt khi nào nên Go, Not Yet hoặc No-Go cho một đề xuất AI?', 'Go khi bài toán/metric/can thiệp/rủi ro rõ; Not Yet khi còn thiếu dữ liệu/quy trình/chỉ số/ranh giới có thể bổ sung; No-Go khi không thêm giá trị hoặc rủi ro cao/phi AI tốt hơn. Dựa bằng chứng thay vì thích công nghệ.')])]},
]


def find_section(lesson_id, section_id):
    lesson = next((x for x in LESSONS if x['id'] == lesson_id), None)
    part = next((x for x in lesson['sections'] if x['id'] == section_id), None) if lesson else None
    if not part:
        raise ValueError('Bài học hoặc phần kiến thức không tồn tại.')
    return lesson, part
