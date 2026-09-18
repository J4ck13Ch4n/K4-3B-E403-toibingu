"""Export the reviewed question bank; no API call or raw source upload."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / 'codebase'))
from curriculum import LESSONS

lines=['# Checklist theo slide bài học', '', 'Biên soạn từ hai PDF trong `data/vlearn-pack/slides`. Số trang là vị trí PDF (bắt đầu từ 1), không phải số slide in ở chân trang. Câu hỏi và tiêu chí là diễn giải của nhóm. Không yêu cầu học thuộc tên model, giá hoặc số liệu thời điểm trên slide.', '', 'Tiến độ = số tiêu chí đạt / tổng tiêu chí bài học; trạng thái chưa kiểm tra tách riêng. Chỉ dùng trong phạm vi hackathon.', '']
for lesson in LESSONS:
    lines.extend([f'## {lesson["day"]} — {lesson["title"]}', '', f'Nguồn: `{lesson["file"]}` · {lesson["page_count"]} trang.', ''])
    for part in lesson['sections']:
        lines.extend([f'### {part["title"]}', ''])
        for c in part['criteria']:
            lines.append(f'- [ ] {c["question"]} — {c["source"]} (`{c["id"]}`)')
        lines.append('')
target=ROOT/'docs'/'checklist.md'
target.parent.mkdir(exist_ok=True)
target.write_text('\n'.join(lines),encoding='utf-8')
print('Exported docs/checklist.md')
