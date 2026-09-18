"""Live model smoke check for every authored lesson section.

Answers are assembled from the section's reviewed required points. This checks
the live evaluator, schema normalization, audit path, and rubric wiring; it is
not a learner-accuracy evaluation.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'codebase'))

import app
import assessment
from curriculum import LESSONS


def authored_answer(criteria):
    return ' '.join(
        point['expected']
        for criterion in criteria
        for point in assessment.requirements(criterion)
    )


def run():
    report = {
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'all_lesson_sections',
        'lesson_count': len(LESSONS),
        'section_count': sum(len(lesson['sections']) for lesson in LESSONS),
        'criterion_count': sum(len(section['criteria']) for lesson in LESSONS for section in lesson['sections']),
        'answer_source': 'assembled_from_reviewed_required_points',
        'learner_accuracy_claim': False,
        'sections': [],
    }
    for lesson in LESSONS:
        for section in lesson['sections']:
            criteria = section['criteria']
            item = {
                'lesson_id': lesson['id'],
                'section_id': section['id'],
                'criteria_count': len(criteria),
            }
            try:
                checks, response_id = app.evaluate(
                    [{'role': 'user', 'text': authored_answer(criteria)}], criteria
                )
                item.update({
                    'status': 'pass' if all(check['status'] == 'met' for check in checks) else 'fail',
                    'actual': [check['status'] for check in checks],
                    'response_id': response_id,
                })
            except app.AppError as exc:
                item.update({'status': 'error', 'error': str(exc), 'http_status': exc.status})
            report['sections'].append(item)
            print(lesson['id'], section['id'], item['status'], item.get('actual', item.get('error', '')), flush=True)
    report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    report['passed_sections'] = sum(item['status'] == 'pass' for item in report['sections'])
    report['failed_sections'] = sum(item['status'] != 'pass' for item in report['sections'])
    output = ROOT / 'runtime' / 'lesson-library-live.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Report: {output}', flush=True)
    return 0 if report['failed_sections'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(run())