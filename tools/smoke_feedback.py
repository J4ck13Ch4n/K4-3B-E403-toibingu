"""Real AI regression cases for partial answers and adaptive probes, no saved sessions."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import app
import assessment
from curriculum import find_section

criteria=find_section('day1','ai_map')[1]['criteria']
messages=[{'role':'assistant','text':criteria[0]['question']}]
report=[]
original_normalize=assessment.normalize
def capture(raw,messages,criteria):
    try:
        return original_normalize(raw,messages,criteria)
    except (ValueError,KeyError,TypeError) as exc:
        (ROOT/'runtime'/'feedback-invalid.json').write_text(json.dumps({'error':str(exc),'raw':raw},ensure_ascii=False,indent=2),encoding='utf-8')
        print('Invalid assessment:',str(exc),flush=True)
        raise
assessment.normalize=capture


def run(name,answer,expected,focus=0):
    messages.append({'role':'user','text':answer})
    checks,rid=app.evaluate(messages,criteria)
    c=checks[focus]
    question=assessment.followup(c,criteria[focus],messages,len(report)+1) if c['status']!='met' else ''
    report.append({'case':name,'status':c['status'],'points':c['points'],'question':question,'response_id':rid})
    (ROOT/'runtime'/'feedback-smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(name,c['status'],rid,flush=True)
    assert c['status']==expected,(name,c)
    if question:
        assert question!=criteria[focus]['question']
        assert question not in [m['text'] for m in messages if m['role']=='assistant']
        messages.append({'role':'assistant','text':question})
    return checks


run('partial_definitions','AI là lĩnh vực trí tuệ nhân tạo. ML là học máy, ví dụ lọc spam. Mình chưa giải thích được những nhóm còn lại.','missing')
run('wrong_relationship','Theo mình AI và ML là hai tên của cùng một thứ, mọi AI bắt buộc phải học từ dữ liệu.','incorrect')
run('same_misconception_new_probe','Mình vẫn nghĩ mọi AI đều phải học từ dữ liệu, không có ngoại lệ.','incorrect')
run('explicit_correction','Mình sửa lại ý trước: AI rộng hơn ML và không phải mọi AI đều học dữ liệu, chẳng hạn hệ chuyên gia luật tay. ML thuộc AI, học từ dữ liệu, ví dụ phân loại spam. Deep learning thuộc ML, dùng mạng nơ-ron nhiều tầng, ví dụ nhận diện ảnh. GenAI sinh nội dung mới như ảnh hoặc văn bản. LLM là model ngôn ngữ thường dùng deep learning; LLM sinh văn bản thuộc GenAI, ví dụ viết email. GenAI không chỉ có LLM và LLM không phải toàn bộ AI.','met')
run('partial_history','Transformer dùng attention để liên hệ các token theo ngữ cảnh, làm nền tảng cho LLM. Mình chưa biết các mốc còn lại.','missing',2)
print('5 feedback cases passed; report: runtime/feedback-smoke.json')
