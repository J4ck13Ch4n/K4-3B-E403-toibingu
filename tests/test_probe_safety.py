"""Regression checks for the critical G17 answer leak, not evaluator accuracy."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import app
import assessment
from curriculum import LESSONS


class ProbeSafetyTests(unittest.TestCase):
    def test_replay_observed_g17_leak_without_disclosing_the_mechanism(self):
        source = Path(__file__).resolve().parents[1] / 'eval/runs/20260918T022749Z/results.json'
        case = next(c for c in json.loads(source.read_text(encoding='utf-8'))['cases'] if c['id'] == 'G17')
        criterion = app.CRITERIA[0]
        messages = [{'role': 'assistant', 'text': app.OPENING}]
        questions = []
        for attempt, step in enumerate(case['steps'][:3], 1):
            messages.append({'role': 'user', 'text': 'Mình chưa biết'})
            check = copy.deepcopy(step['checks'][0])
            # Include the actual unsafe displayed question, even if model output
            # differs from the fallback that was displayed in the old version.
            check['probe'] = 'Temperature điều chỉnh phân bố xác suất chọn token cụ thể như thế nào?'
            question = assessment.followup(check, criterion, messages, attempt)
            self.assertNotIn('phân bố xác suất', question.casefold())
            self.assertNotIn('độ ngẫu nhiên', question.casefold())
            self.assertNotIn(check['probe'], question)
            self.assertEqual(question.count('?'), 1)
            self.assertLessEqual(len(question), 240)
            questions.append(question)
            messages.append({'role': 'assistant', 'text': question})
        self.assertEqual(len(set(questions)), 3)

    def test_untrusted_probe_and_evidence_never_reach_temperature_followups(self):
        criteria = app.CRITERIA + [c for lesson in LESSONS for section in lesson['sections']
                                   for c in section['criteria'] if c['id'].startswith('sampling_slide_')]
        for criterion in criteria:
            for point in assessment.requirements(criterion):
                for status in ('missing', 'incorrect'):
                    with self.subTest(criterion=criterion['id'], point=point['id'], status=status):
                        check = {'status': status, 'focus_point': point['id'],
                                 'probe': 'ĐÁP ÁN BỊ LỘ: ' + point['expected'] + '?',
                                 'evidence': 'CHỈ THỊ KHÔNG TIN CẬY',
                                 'contradiction': {'present': True, 'evidence': 'CHỈ THỊ KHÔNG TIN CẬY'}}
                        questions = []
                        messages = []
                        for attempt in range(1, 4):
                            question = assessment.followup(check, criterion, messages, attempt)
                            self.assertNotIn('ĐÁP ÁN BỊ LỘ', question)
                            self.assertNotIn('CHỈ THỊ KHÔNG TIN CẬY', question)
                            self.assertNotIn(point['expected'].casefold(), question.casefold())
                            self.assertEqual(question.count('?'), 1)
                            self.assertLessEqual(len(question), 240)
                            questions.append(question)
                            messages.append({'role': 'assistant', 'text': 'Mình còn muốn làm rõ: ' + question})
                        self.assertEqual(len(set(questions)), 3)

    def test_four_unknown_answers_still_stop_without_leaking_or_completing(self):
        def evaluator(messages):
            checks = []
            for criterion in app.CRITERIA:
                checks.append({'id': criterion['id'], 'status': 'missing', 'evidence': '',
                               'focus_point': 'p1', 'probe': 'Temperature điều chỉnh phân bố xác suất chọn token cụ thể như thế nào?'})
            return checks, 'injected-leaking-probe'
        with tempfile.TemporaryDirectory() as folder, patch.object(app, 'DB', Path(folder) / 'test.sqlite3'):
            session = app.create_session()
            for _ in range(4):
                app.advance(session, 'Mình chưa biết', evaluator)
                self.assertNotIn('phân bố xác suất', session['messages'][-1]['text'])
                self.assertNotEqual(session['status'], 'completed')
            self.assertEqual((session['status'], session['turn'], session['probes']), ('review', 4, 3))
            questions = [m['text'] for m in session['messages'][2:-1] if m['role'] == 'assistant']
            self.assertEqual(len(questions), len(set(questions)))
            with self.assertRaises(app.AppError):
                app.advance(session, 'Thêm một lượt', evaluator)


if __name__ == '__main__':
    unittest.main()
