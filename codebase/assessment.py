"""Atomic rubric and deterministic aggregation of model evidence."""
import re
from difflib import SequenceMatcher

# Reviewed questions for the temperature slice. Never display a model-written
# probe for these criteria: lexical overlap cannot reliably detect answer leaks.
# Each list has three different scenarios, matching the session's probe limit.
TEMPERATURE_PROBES = {
 'definition': {
  'p1': [
   'Nếu giữ nguyên đề bài nhưng đổi temperature, cậu dự đoán quá trình tạo câu trả lời sẽ thay đổi ở bước nào?',
   'Với câu mở đầu “Hôm nay trời…”, cậu mô tả vai trò của temperature trong bước viết tiếp được không?',
   'Cậu sẽ thiết kế một thử nghiệm nhỏ như thế nào để giải thích temperature cho người chưa học?']},
 'low': {
  'p1': [
   'Khi giảm temperature và đang có nhiều cách viết tiếp một câu, cậu dự đoán mô hình sẽ lựa chọn như thế nào?',
   'Với câu mở đầu “Món ăn tôi thích là…”, cậu giải thích cách chọn từ khi temperature thấp được không?',
   'Cậu sẽ quan sát điều gì ở bước chọn từ để kiểm tra tác động của việc giảm temperature?'],
  'p2': [
   'Nếu gửi cùng một đề bài nhiều lần ở temperature thấp, cậu dự đoán kết quả sẽ như thế nào?',
   'Cậu sẽ so sánh những gì giữa các câu trả lời để kiểm chứng dự đoán của mình về temperature thấp?',
   'Khi dùng temperature thấp cho một bài toán mới, cậu sẽ kiểm tra chất lượng kết quả ra sao?']},
 'high': {
  'p1': [
   'Nếu tăng temperature trong lúc mô hình đang viết tiếp một câu, cậu dự đoán bước chọn từ sẽ thay đổi thế nào?',
   'Với câu mở đầu “Một ý tưởng cho chuyến đi là…”, cậu mô tả cách chọn từ khi temperature cao được không?',
   'Cậu sẽ quan sát điều gì ở bước chọn từ để kiểm tra tác động của việc tăng temperature?'],
  'p2': [
   'Nếu chạy cùng một đề bài nhiều lần ở temperature cao, cậu dự đoán các câu trả lời sẽ như thế nào?',
   'Cậu sẽ so sánh những gì giữa các lần chạy để kiểm chứng dự đoán về temperature cao?',
   'Khi dùng temperature cao cho một bài toán mới, cậu sẽ kiểm tra chất lượng kết quả ra sao?']},
 'usage': {
  'p1': [
   'Khi cần trích xuất thông tin từ nhiều hóa đơn, cậu sẽ chọn temperature thế nào và vì sao?',
   'Nếu phải phân loại hàng loạt yêu cầu theo một mẫu cố định, cậu sẽ thử cấu hình temperature nào?',
   'Cậu chọn một công việc cần kết quả theo cùng một quy cách và giải thích cách chọn temperature được không?'],
  'p2': [
   'Khi cần nghĩ ý tưởng cho một chiến dịch mới, cậu sẽ chọn temperature thế nào và vì sao?',
   'Nếu cần nhiều hướng mở đầu cho một truyện ngắn, cậu sẽ thử cấu hình temperature nào?',
   'Cậu chọn một công việc cần tìm nhiều phương án và giải thích cách chọn temperature được không?']},
 'sampling': {
  'p1': [
   'Nếu cài top-k bằng 3, cậu mô tả điều gì xảy ra trước bước chọn token được không?',
   'Khi đổi top-k từ 3 thành 5, cậu dự đoán điều gì thay đổi trong bước chuẩn bị chọn từ?',
   'Cậu sẽ dựng một ví dụ nhỏ như thế nào để phân biệt vai trò top-k với temperature?'],
  'p2': [
   'Nếu cài top-p bằng 0,9, cậu mô tả cách tham số này được sử dụng khi sinh văn bản được không?',
   'Khi đổi top-p từ 0,9 thành 0,5, cậu dự đoán điều gì thay đổi trước bước chọn từ?',
   'Cậu sẽ dựng một ví dụ nhỏ như thế nào để phân biệt vai trò top-p với temperature?'],
  'p3': [
   'Nếu giữ nguyên top-k và top-p nhưng thay temperature, cậu dự đoán điều gì sẽ thay đổi?',
   'Cậu sẽ bố trí thử nghiệm thế nào để phân biệt tác động của temperature với hai tham số còn lại?',
   'Khi giải thích ba tham số cho một người mới, cậu sẽ dùng ví dụ nào để làm rõ vai trò riêng của temperature?']},
}
# The lesson-library version covers the same concepts under different IDs.
TEMPERATURE_PROBES['sampling_slide_1'] = {
    'p1': TEMPERATURE_PROBES['low']['p1'], 'p2': TEMPERATURE_PROBES['high']['p1']}
TEMPERATURE_PROBES['sampling_slide_2'] = {
    'p1': TEMPERATURE_PROBES['sampling']['p2'], 'p2': TEMPERATURE_PROBES['sampling']['p3']}
TEMPERATURE_PROBES['sampling_slide_3'] = {
    'p1': TEMPERATURE_PROBES['usage']['p1'], 'p2': TEMPERATURE_PROBES['usage']['p2'],
    'p3': TEMPERATURE_PROBES['sampling']['p3']}

# Each row is an independently required idea, not an optional example.
# Keep requirements within the scope of the actual learner-facing question.
POINTS = {
 'ai_map_1': ['Phạm vi AI: AI là phạm vi rộng, không chỉ LLM', 'Machine learning: học từ dữ liệu, thuộc AI', 'Deep learning: mạng nhiều tầng, thuộc machine learning', 'Generative AI: sinh nội dung mới, không chỉ ngôn ngữ', 'LLM: mô hình ngôn ngữ, thường dùng deep learning; LLM sinh văn bản là một nhóm GenAI', 'Ví dụ: ít nhất một ví dụ cụ thể được gắn đúng nhóm'],
 'ai_map_2': ['Phân loại: discriminative trả nhãn hoặc dự đoán, ví dụ spam', 'Sinh nội dung: generative tạo nội dung mới, ví dụ viết bài', 'Hành động: agentic lập kế hoạch/dùng công cụ thực hiện nhiều bước theo mục tiêu, có ví dụ'],
 'ai_map_3': ['Hệ chuyên gia: mã hóa tri thức thành luật trong miền hẹp', 'ImageNet: dữ liệu ảnh gán nhãn quy mô lớn hỗ trợ học máy', 'Transformer: attention liên hệ token theo ngữ cảnh, nền tảng LLM', 'ChatGPT: đưa model đến số đông qua giao diện hội thoại dễ dùng'],
 'generation_1': ['Nền tảng chung: học dự đoán token từ dữ liệu rộng hỗ trợ nhiều tác vụ', 'Model và sản phẩm: chatbot là sản phẩm bao quanh model, không đồng nhất với LLM'],
 'generation_2': ['Dự đoán: tạo phân bố xác suất token tiếp theo', 'Chọn và nối: lấy token rồi nối vào ngữ cảnh', 'Lặp: dùng ngữ cảnh đã cập nhật để tiếp tục sinh token'],
 'generation_3': ['Đơn vị token: mảnh văn bản không luôn bằng một từ', 'Phụ thuộc tokenizer: cách chia thay đổi theo tokenizer và nội dung/ký tự', 'Chi phí: phải dùng số token, không suy ra bằng số từ cố định'],
 'context_1': ['Phạm vi context: thông tin model nhìn thấy trong lần gọi, giới hạn token', 'Hệ quả dài: có thể bỏ sót thông tin và tăng chi phí/độ trễ'],
 'context_2': ['Liên quan: attention tính mức liên quan giữa token', 'Khóa nghĩa: dùng thông tin ngữ cảnh để liên hệ đại từ với đối tượng, có minh họa'],
 'context_3': ['Chọn thông tin: lấy đoạn liên quan bằng retrieval hoặc RAG', 'Giảm nhiễu: tóm tắt/lược lịch sử hoặc bỏ dữ liệu không cần', 'Sắp xếp: yêu cầu quan trọng rõ ở đầu/cuối, không chôn giữa tài liệu'],
 'training_1': ['Weights: giá trị học trong huấn luyện, cố định khi suy luận thông thường', 'Lúc sử dụng: context và temperature không trực tiếp huấn luyện lại weights'],
 'training_2': ['Dense: sử dụng toàn bộ mạng liên quan cho mỗi token', 'MoE: kích hoạt một phần chuyên gia, tổng tham số khác số tham số hoạt động', 'Hệ quả chi phí: tổng tham số tăng không đồng nghĩa chi phí mỗi token tăng cùng tỷ lệ'],
 'training_3': ['Pre-training: học dự đoán token từ dữ liệu rộng', 'SFT: học ví dụ hướng dẫn và câu trả lời', 'Phản hồi: RLHF học từ xếp hạng/phản hồi qua mô hình thưởng hoặc DPO học trực tiếp ưu tiên'],
 'limits_1': ['Cutoff: kiến thức huấn luyện không tự cập nhật sự kiện mới', 'Hallucination: sinh câu hợp lý không đồng nghĩa kiểm chứng sự thật', 'Ứng phó: cấp dữ liệu mới qua context/tools/retrieval và kiểm chứng'],
 'limits_2': ['Đường tắt: học tín hiệu tương quan không đồng nghĩa hiểu bản chất, có ví dụ', 'Đánh giá riêng: kiểm thử dữ liệu thực tế/trường hợp biên của tác vụ, không chỉ tin benchmark'],
 'limits_3': ['Lợi ích chia bước: theo dõi phép tính/quan hệ trung gian thay vì đoán', 'Kiểm chứng: vẫn kiểm tra kết quả, không bảo đảm suy luận nhiều bước luôn đúng'],
 'agents_1': ['LLM trần: sinh hoặc suy luận không có công cụ', 'Có tools: truy cập công cụ/dữ liệu ngoài', 'Agent: tự chia bước và kiểm tra kết quả', 'Multi-agent: phối hợp nhiều agent chuyên biệt'],
 'agents_2': ['Goal: xác định mục tiêu cần đạt', 'Reasoning: suy luận/chia bước', 'Tools: tương tác công cụ/hệ thống', 'Memory: ghi nhớ tiến trình/thông tin', 'Action: thực hiện hành động tạo kết quả'],
 'agents_3': ['Quan sát: đọc kết quả công cụ thay vì coi gọi tool là xong', 'Điều chỉnh và lặp: lưu tiến trình, quyết định bước tiếp theo tới mục tiêu'],
 'practical_1': ['Tác vụ đơn giản: thử model đủ tốt và rẻ cho khối lượng lớn', 'Tác vụ khó: nâng năng lực khi kiểm thử chất lượng cho thấy cần', 'Cân đối: dựa chất lượng tác vụ và chi phí/kiểm soát dữ liệu, không chỉ tên model'],
 'practical_2': ['Input: số token input và đơn giá tương ứng', 'Output: số token output và đơn giá tương ứng', 'Công thức: nhân từng loại rồi cộng với đúng đơn vị giá, kiểm tra usage'],
 'practical_3': ['System: vai trò và ràng buộc', 'User: yêu cầu cụ thể tóm tắt', 'Context: cung cấp báo cáo hoặc đoạn liên quan', 'Output: quy định định dạng/độ dài kết quả'],
 'sampling_slide_1': ['Thấp: phân bố tập trung token xác suất cao, thường ổn định hơn', 'Cao: phân bố phẳng hơn, token ít xác suất có thêm cơ hội, đa dạng hơn'],
 'sampling_slide_2': ['Top-p: giữ nhóm token xác suất cao theo ngưỡng cộng dồn 0,9', 'Khác temperature: ngưỡng tập ứng viên khác điều chỉnh phân bố xác suất'],
 'sampling_slide_3': ['Ổn định: dùng temperature thấp cho phân tích nhất quán', 'Đa dạng: tăng temperature cho nhiều ý tưởng và vẫn kiểm chứng', 'Cấu hình: thường thử thay một trong temperature hoặc top-p để hiểu tác động'],
 'discovery_1': ['Discover/Define: mở rộng khảo sát rồi hội tụ xác định vấn đề', 'Develop/Deliver: mở rộng giải pháp rồi chọn triển khai', 'Thứ tự: tránh giải tốt sai vấn đề'],
 'discovery_2': ['Vấn đề cụ thể: ai gặp pain, công việc lặp hoặc tốn thời gian', 'Xác thực: dùng quan sát/phỏng vấn/log/dữ liệu thay vì đoán'],
 'discovery_3': ['Hiện trạng: làm rõ nhu cầu, workflow và bottleneck', 'Đánh giá: hỏi baseline và tiêu chí thành công', 'Phạm vi: xác định ranh giới/rủi ro và cân nhắc giải pháp phi AI'],
 'problem_1': ['Actor: người/bộ phận cụ thể chịu ảnh hưởng', 'Workflow: các bước hiện tại, không chỉ giải pháp đề xuất', 'Bottleneck và impact: chỉ rõ điểm nghẽn và hệ quả', 'Thành công: hướng chỉ số để kiểm tra cải thiện'],
 'problem_2': ['Baseline: số liệu hiện trạng', 'Target: mục tiêu định lượng', 'Measurement: cách thu thập/đo trong phạm vi rõ, số tự đặt là giả định'],
 'problem_3': ['Hao phí: thời gian/chi phí/tần suất hoặc tác động đo được', 'Sai sót: hậu quả thiệt hại cụ thể', 'Ranh giới: giới hạn AI tự quyết và điểm người phê duyệt'],
 'problem_4': ['Output metric: giá trị/kết quả cuối người dùng nhận, có ví dụ', 'Input metrics: đòn bẩy có thể tác động, có ví dụ', 'Liên hệ: cải thiện đòn bẩy phải đo tác động lên kết quả cuối'],
 'pair_1': ['Nhu cầu: AI có thêm giá trị cho vấn đề người dùng không', 'Vai trò: tự động hóa hay hỗ trợ con người', 'Thành công: tiêu chí đo/hàm thưởng xác định đúng sai'],
 'pair_2': ['Ví dụ phù hợp: ngôn ngữ/gợi ý/cá nhân hóa/dự đoán/phát hiện biến đổi', 'Lý do lợi thế: đầu vào đa dạng/ngữ cảnh/học dữ liệu khiến rule tĩnh khó bao quát'],
 'pair_3': ['Phương án đơn giản: cân nhắc rule/hiển thị tĩnh nếu đủ', 'Lập luận: dựa tính dự đoán/chi phí/độ trễ/minh bạch/rủi ro hoặc mong muốn tự làm'],
 'solution_1': ['Model: đọc hiểu và suy luận', 'Context: tri thức nghiệp vụ', 'Planning: điều phối/chia tác vụ', 'Tools: nối hệ thống để đọc/ghi/thực hiện'],
 'solution_2': ['Automate: hợp việc lặp/scale hoặc đáp án đồng thuận', 'Augment: xét stakes/trách nhiệm và mong muốn tự làm', 'Giám sát: có người kiểm tra/preview/edit/undo phù hợp'],
 'solution_3': ['Rule: FAQ logic rõ đầu ra ổn định', 'Workflow: duyệt biểu mẫu theo bước/gate định trước', 'Agent: mục tiêu động cần tự quyết nhiều bước/công cụ', 'Chọn cấp: đơn giản đủ giá trị, kiểm soát rủi ro, không phải luôn nâng cấp'],
 'workflows_1': ['Chuỗi: bước phụ thuộc tuần tự, có ví dụ', 'Gate: kiểm tra/dừng/chuyển khi không đạt', 'Đánh đổi: tăng độ trễ để kiểm soát chất lượng'],
 'workflows_2': ['Định tuyến: phân loại input rồi đưa nhánh/model phù hợp', 'Lợi ích và ví dụ: tối ưu theo loại, ví dụ dễ/rẻ khó/mạnh hoặc FAQ/refund'],
 'workflows_3': ['Song song: phần độc lập hoặc nhiều đánh giá chạy đồng thời', 'Tổng hợp: gộp kết quả hoặc vote sau đó', 'Mục đích: tình huống phù hợp để giảm rủi ro/độ trễ, không bảo đảm đúng tuyệt đối'],
 'metrics_1': ['FP: báo/can thiệp không đúng nhu cầu hoặc gợi ý sai', 'FN: bỏ sót nhu cầu giúp thật', 'Chi phí: giải thích hai loại thiệt hại có thể không đối xứng'],
 'metrics_2': ['Precision: TP/(TP+FP), tỷ lệ đúng trong các trường hợp đã báo', 'Recall: TP/(TP+FN), tỷ lệ tìm được trong nhu cầu thật', 'Cân bằng: chọn theo chi phí báo nhầm/bỏ sót và kiểm thử người dùng'],
 'metrics_3': ['Chỉ số: metric cụ thể', 'Ngưỡng: ngưỡng và khoảng đo có nghĩa', 'Hành động: làm gì khi vượt hoặc không đạt ngưỡng'],
 'decision_1': ['Bài toán: actor, workflow, bottleneck, impact', 'Thành công và ranh giới: success metric và boundary', 'Can thiệp: bước AI tham gia và cấp rule/workflow/agent', 'An toàn: rủi ro và HITL'],
 'decision_2': ['Đối chứng: baseline', 'Kiểm thử: dữ liệu và edge cases cùng pass/fail/HITL', 'Kiểm soát: logging/fallback/rollback', 'Vận hành: người giám sát và cập nhật'],
 'decision_3': ['Go: bài toán/metric/can thiệp/rủi ro đủ rõ', 'Not Yet: còn thiếu dữ liệu/quy trình/chỉ số/ranh giới có thể bổ sung', 'No-Go: không thêm giá trị hoặc rủi ro cao/phi AI tốt hơn', 'Căn cứ: dựa bằng chứng khả thi thay vì sở thích công nghệ'],
 'definition': ['Cơ chế: điều chỉnh phân bố xác suất/độ ngẫu nhiên khi chọn token tiếp theo'],
 'low': ['Chọn token: ưu tiên token xác suất cao', 'Kết quả: ít ngẫu nhiên, thường ổn định hơn'],
 'high': ['Chọn token: token ít xác suất có thêm cơ hội', 'Kết quả: đa dạng/ngẫu nhiên hơn'],
 'usage': ['Thấp: ví dụ cần nhất quán và lý do', 'Cao: ví dụ cần đa dạng và lý do'],
 'sampling': ['Top-k: giữ k token xác suất cao nhất', 'Top-p: giữ theo xác suất cộng dồn', 'Temperature: điều chỉnh phân bố lấy mẫu, không phải số lượng token'],
}

# Neutral scenarios for commonly confused concepts; no answer is disclosed.
PROBES = {
 'ai_map_1': {
  'p1':['Một chương trình chỉ làm theo các luật if/else do người viết sẵn thì cậu sẽ xếp nó vào nhóm nào trong bức tranh AI, và vì sao?', 'Nếu một hệ thống chưa từng được huấn luyện bằng dữ liệu, cậu dựa vào đâu để quyết định nó có thuộc AI không?'],
  'p2':['Với bộ lọc spam, việc người viết sẵn mọi luật khác gì việc đưa nhiều email mẫu để hệ thống học cách phân loại?', 'Nếu đổi tập email dùng để huấn luyện, bộ lọc có thể thay đổi quyết định theo cách nào?'],
  'p3':['Khi nghe một mô hình dùng mạng nơ-ron nhiều tầng để nhận diện ảnh, cậu sẽ đặt nó ở đâu so với machine learning, và vì sao?', 'Cậu dựa vào đặc điểm nào của mô hình để gọi nó là deep learning?'],
  'p4':['Một hệ thống vẽ một bức ảnh mới từ mô tả của cậu sẽ thuộc nhóm nào trong các nhóm vừa nêu, và vì sao?', 'Đầu ra nào giúp cậu phân biệt một hệ thống sinh nội dung với một hệ thống chỉ gán nhãn?'],
  'p5':['Một công cụ tạo ảnh và một mô hình viết email có nhất thiết đều là LLM không, cậu phân biệt bằng đặc điểm nào?', 'Cậu sẽ đặt LLM ở đâu trong mối quan hệ với deep learning và GenAI, dựa trên cách nó hoạt động và đầu ra nào?'],
  'p6':['Cậu chọn một công cụ mình từng dùng và giải thích vì sao nó thuộc một trong các nhóm vừa nói được không?', 'Với một tác vụ thực tế của cậu, đầu vào và đầu ra nào giúp nhận ra nhóm AI phù hợp?']},
 'ai_map_3': {
  'p1':['Nếu xây hệ thống tư vấn trong một lĩnh vực hẹp bằng kinh nghiệm chuyên gia, kiến thức đó sẽ được đưa vào hệ thống theo cách nào?', 'Khi chuyên gia đổi một quy tắc nghiệp vụ, một hệ chuyên gia sẽ cần thay đổi ở đâu?'],
  'p2':['Trong câu chuyện ImageNet, điều gì được bổ sung cho việc học máy ngoài việc nghĩ ra thuật toán mới?', 'Nếu hai nhóm dùng cùng thuật toán nhưng dữ liệu ảnh được gán nhãn khác nhau, cậu dự đoán điều gì và liên hệ ra sao với ImageNet?'],
  'p3':['Trong một câu có đại từ chưa rõ nghĩa, bước ngoặt Transformer giúp liên hệ thông tin trong câu theo cách nào?', 'Vì sao Transformer lại trở thành nền tảng cho nhiều mô hình ngôn ngữ?'],
  'p4':['Với người chưa biết lập trình, sự xuất hiện của ChatGPT đã thay đổi cách họ tiếp cận mô hình ngôn ngữ như thế nào?', 'Điều gì khiến người dùng phổ thông có thể sử dụng năng lực mô hình dễ hơn khi ChatGPT xuất hiện?']}
}


def requirements(criterion):
    rows = POINTS[criterion['id']]
    return [{'id': f'p{i}', 'label': row.split(':',1)[0], 'expected': row.split(':',1)[1].strip()}
            for i,row in enumerate(rows,1)]


def schema(criteria):
    def obj(properties):
        return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
    status={'type':'string','enum':['met','missing','incorrect']}
    proof=obj({'status':status,
               'user_turn':{'type':'integer'},'diagnosis':{'type':'string'}})
    checks={}
    for c in criteria:
        checks[c['id']]=obj({'points':obj({p['id']:proof for p in requirements(c)}),
                            'contradiction':obj({'present':{'type':'boolean'},'user_turn':{'type':'integer'}}),
                            'focus_point':{'type':'string','enum':['']+[p['id'] for p in requirements(c)]},
                            'probe':{'type':'string'}})
    return obj({'checks':obj(checks)})


def normalize(raw, messages, criteria):
    """Fail closed on missing point IDs or invented student evidence."""
    if isinstance(raw,dict):
        raw=[dict(c,id=cid,points=[dict(p,point_id=pid) for pid,p in c['points'].items()]) for cid,c in raw.items()]
    users=[m['text'] for m in messages if m['role']=='user']
    def proof(evidence,turn):
        return (isinstance(evidence,str) and bool(evidence.strip()) and type(turn) is int
                and 1<=turn<=len(users) and evidence in users[turn-1])
    if not isinstance(raw,list) or len(raw)!=len(criteria):raise ValueError('Incomplete criteria')
    if any(not isinstance(c,dict) or not isinstance(c.get('id'),str) for c in raw):raise ValueError('Invalid criterion')
    checks={c['id']:c for c in raw}
    if set(checks)!={c['id'] for c in criteria}:raise ValueError('Wrong criteria')
    normalized=[]
    for criterion in criteria:
        c=checks[criterion['id']]
        expected=requirements(criterion)
        points=c['points']
        if not isinstance(points,list) or len(points)!=len(expected):raise ValueError('Incomplete points')
        by_id={p['point_id']:p for p in points}
        if set(by_id)!={p['id'] for p in expected}:raise ValueError('Wrong points')
        points=[by_id[p['id']] for p in expected]
        for p in points:
            if 'evidence' not in p:
                turn=p.get('user_turn')
                p['evidence']=users[turn-1] if type(turn) is int and 1<=turn<=len(users) else ''
            if p['status'] not in ('met','missing','incorrect'):raise ValueError('Invalid status')
            if not isinstance(p.get('diagnosis'),str):raise ValueError('Invalid diagnosis')
            if p['status']!='missing' and not proof(p['evidence'],p['user_turn']):
                # Model sometimes capitalizes a mid-sentence quote. Restore the
                # actual original substring; never accept invented or other-turn text.
                turn=p['user_turn']; quote=p['evidence']
                source=users[turn-1] if type(turn) is int and 1<=turn<=len(users) else ''
                index=source.lower().find(quote.lower()) if isinstance(quote,str) and quote else -1
                if index>=0:
                    p['evidence']=source[index:index+len(quote)]
                else:
                    # If the model joined actual sentences from the SAME turn,
                    # restore the full original span, including omitted text.
                    fragments=re.split(r'(?<=[.!?])\s+',quote) if isinstance(quote,str) else []
                    cursor=0; spans=[]
                    for fragment in fragments:
                        found=source.lower().find(fragment.lower(),cursor)
                        if found<0:break
                        cursor=found+len(fragment);spans.append((found,cursor))
                    if len(fragments)<2 or len(spans)!=len(fragments):raise ValueError('Invalid quote')
                    p['evidence']=source[spans[0][0]:spans[-1][1]]
            if p['status']=='missing' and (p['evidence'] or p['user_turn']!=0):raise ValueError('Missing has no evidence')
        contradiction=c['contradiction']
        if 'evidence' not in contradiction:
            turn=contradiction.get('user_turn')
            contradiction['evidence']=users[turn-1] if type(turn) is int and 1<=turn<=len(users) else ''
        if type(contradiction['present']) is not bool:raise ValueError('Invalid contradiction')
        if contradiction['present'] and not proof(contradiction['evidence'],contradiction['user_turn']):raise ValueError('Invalid contradiction quote')
        gaps=[p for p in points if p['status']!='met']
        status='incorrect' if contradiction['present'] or any(p['status']=='incorrect' for p in points) else 'missing' if gaps else 'met'
        allowed_focus = {p['id'] for p in expected} if contradiction['present'] else {p['point_id'] for p in gaps}
        if status!='met' and c['focus_point'] not in allowed_focus:raise ValueError('Probe targets no gap')
        if not isinstance(c['probe'],str):raise ValueError('Invalid question')
        evidence=contradiction['evidence'] if contradiction['present'] else next((p['evidence'] for p in points if p['status']=='incorrect'),'') if status=='incorrect' else next((p['evidence'] for p in points if p['status']=='met'),'') if status=='met' else ''
        normalized.append({'id':c['id'],'status':status,'evidence':evidence,'points':points,
                           'contradiction':contradiction,'focus_point':c['focus_point'],'probe':c['probe'].strip()})
    return normalized


def followup(check, criterion, messages, attempt):
    prior=[m['text'].split('\n\n')[-1] for m in messages if m['role']=='assistant']+[criterion['question']]
    def clean(s):return re.sub(r'\W+',' ',s.casefold()).strip()
    reviewed = TEMPERATURE_PROBES.get(criterion['id'])
    if reviewed:
        focus = check.get('focus_point')
        if focus not in reviewed:
            focus = next((p['point_id'] for p in check.get('points', [])
                          if p['status'] != 'met' and p['point_id'] in reviewed), next(iter(reviewed)))
        variants = reviewed[focus]
        # Rotate by the actual conversation, not just the attempt number: this
        # still works when earlier probes targeted a different point.
        return next((q for q in variants if not any(clean(q) in clean(p) for p in prior)), variants[-1])
    question=check.get('probe','').strip()
    repeated=any(clean(question) in clean(p) or SequenceMatcher(None,clean(question),clean(p)).ratio()>.88 for p in prior) if question else True
    point=next((p for p in requirements(criterion) if p['id']==check.get('focus_point')),None)
    expected_words=set(clean(point['expected']).split()) if point else set()
    question_words=set(clean(question).split())
    leaks_answer=bool(expected_words) and len(expected_words & question_words)/len(expected_words)>.6
    # Wrong assertions must be examined directly, never diverted to another gap.
    if check['status']!='incorrect' and not leaks_answer and question and len(question)<=450 and question.count('?')==1 and question.endswith('?') and not repeated:
        return question
    # Conservative fallback: focus a single diagnosed point, never disclose its answer.
    points=check.get('points',[])
    focus=next((p for p in points if p['point_id']==check.get('focus_point')),None)
    label=point['label'] if point else criterion['label']
    contradiction=check.get('contradiction',{})
    quote=contradiction.get('evidence') if contradiction.get('present') else (focus or {}).get('evidence') or check.get('evidence','')
    if check['status']=='incorrect' and quote:
        if criterion['id']=='ai_map_1' and any(term in quote.casefold() for term in ('mọi ai','ai và ml')):
            variants=[f'Cậu vừa nói “{quote}”. {q}' for q in PROBES['ai_map_1']['p1']]
        else:
            variants=[f'Với nhận định “{quote}”, cậu thử lấy một ví dụ cụ thể và kiểm tra xem nhận định đó còn phù hợp không?',
                  f'Cậu có thể tìm một trường hợp khiến nhận định “{quote}” không còn đúng không?',
                  f'Nếu phải kiểm chứng nhận định “{quote}” bằng một tình huống thực tế, cậu sẽ làm thế nào?']
    else:
        variants=PROBES.get(criterion['id'],{}).get(check.get('focus_point')) or [f'Riêng về “{label}”, cậu có thể giải thích bằng một ví dụ cụ thể của mình không?',
                  f'Trong ví dụ của cậu, “{label}” đóng vai trò gì và vì sao?',
                  f'Cậu sẽ giải thích riêng ý “{label}” như thế nào cho một người chưa học bài này?']
    ordered=variants[(attempt-1)%len(variants):]+variants[:(attempt-1)%len(variants)]
    return next((q for q in ordered if not any(clean(q) in clean(p) for p in prior)),ordered[0])
