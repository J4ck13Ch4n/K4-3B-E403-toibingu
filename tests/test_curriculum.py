import copy
import unittest
from unittest.mock import patch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'codebase'))
import app
from curriculum import LESSONS, find_section
import test_app


class CurriculumTests(unittest.TestCase):
    setUp = test_app.FlowTests.setUp
    tearDown = test_app.FlowTests.tearDown

    def attempt(self, lesson='day1', section='generation', status='met'):
        s = app.create_session(lesson, section)
        def judge(messages):
            return [{'id': c['id'], 'status': status, 'evidence': messages[-1]['text'] if status != 'missing' else ''} for c in s['rubric']], 'mock'
        app.advance(s, 'Lời giải thích thử.', judge)
        app.save(s)
        return s

    def test_catalog_sources_and_coverage(self):
        ids = []
        for lesson in LESSONS:
            covered = set()
            for part in lesson['sections']:
                self.assertTrue(3 <= len(part['criteria']) <= 4)
                for c in part['criteria']:
                    ids.append(c['id'])
                    self.assertTrue(c['question'] and c['rule'] and c['review'])
                    self.assertTrue(all(1 <= p <= lesson['page_count'] for p in c['pages']))
                    covered.update(c['pages'])
            self.assertEqual(covered, set(range(3,30)))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 46)

    def test_unassessed_is_not_failed(self):
        catalog = app.lesson_catalog()
        self.assertEqual([l['total'] for l in catalog], [24,22])
        self.assertTrue(all(l['assessed'] == l['met'] == 0 for l in catalog))
        self.assertEqual(catalog[0]['sections'][0]['criteria'][0]['status'], 'unassessed')

    def test_progress_scoped_to_lesson_and_section(self):
        self.attempt()
        first, second = app.lesson_catalog()
        self.assertEqual((first['met'], first['assessed'], first['percent']), (3,3,12))
        self.assertEqual(second['met'],0)
        self.assertEqual(first['completed_sections'],1)
        self.assertEqual(app.dashboard('day1')['completed'],1)
        self.assertEqual(app.dashboard('day2')['total'],0)

    def test_latest_evaluation_replaces_prior_success(self):
        self.attempt()
        app.create_session('day1','generation')
        self.assertEqual(app.lesson_catalog()[0]['met'],3)
        self.attempt(status='missing')
        result=app.lesson_catalog()[0]
        self.assertEqual(result['met'],0)
        self.assertEqual(result['assessed'],3)

    def test_dynamic_four_criteria_and_snapshot(self):
        s=self.attempt('day2','problem')
        self.assertEqual(len(s['checks']),4)
        self.assertEqual(s['status'],'completed')
        self.assertEqual(app.lesson_catalog()[1]['met'],4)
        public=app.public_session(s)
        self.assertNotIn('rubric',public)
        self.assertIn('review',public['criteria'][0])
        self.assertNotIn('rule',public['criteria'][0])

    def test_active_rubric_is_private(self):
        s=app.create_session('day2','metrics')
        public=app.public_session(s)
        self.assertNotIn('rubric',public)
        self.assertNotIn('rule',public['criteria'][0])
        self.assertNotIn('review',public['criteria'][0])

    def test_invalid_selection_and_cross_section_evidence(self):
        for lesson,part in [('day1','problem'),('day3','generation'),('day1',None)]:
            with self.assertRaises(app.AppError):app.create_session(lesson,part)
        s=app.create_session('day1','generation')
        before=copy.deepcopy(s)
        wrong=[{'id':c['id'],'status':'missing','evidence':''} for c in find_section('day2','metrics')[1]['criteria']]
        with self.assertRaises(app.AppError):app.advance(s,'x',lambda _: (wrong,'mock'))
        self.assertEqual(s,before)

    def test_evaluator_receives_only_selected_rubric(self):
        s=app.create_session('day2','metrics')
        checks=[{'id':c['id'],'status':'missing','evidence':''} for c in s['rubric']]
        with patch.object(app,'evaluate',return_value=(checks,'mock')) as evaluate:
            app.advance(s,'Mình chưa hiểu.')
        self.assertEqual(evaluate.call_args.args[1],s['rubric'])
        self.assertEqual(s['probes'],1)

    def test_acknowledge_before_next_question(self):
        s=app.create_session('day1','ai_map')
        def judge(messages):
            return [{'id':c['id'],'status':'met' if i==0 else 'missing',
                     'evidence':messages[-1]['text'] if i==0 else ''}
                    for i,c in enumerate(s['rubric'])], 'mock'
        app.advance(s,'Giải thích quan hệ giữa các nhóm AI.',judge)
        reply=s['messages'][-1]['text']
        self.assertLess(reply.index('mình đã hiểu'),reply.index(s['rubric'][1]['question']))
        self.assertIn(s['rubric'][0]['label'],reply)
        self.assertEqual(s['target'],s['rubric'][1]['id'])

    def test_stay_on_unresolved_question_without_false_acknowledgement(self):
        s=app.create_session('day1','ai_map')
        def judge(_):
            return [{'id':c['id'],'status':'missing' if i==0 else 'incorrect','evidence':'' if i==0 else 'Sai.'}
                    for i,c in enumerate(s['rubric'])], 'mock'
        app.advance(s,'Sai.',judge)
        reply=s['messages'][-1]['text']
        self.assertNotIn('đã hiểu',reply)
        self.assertNotIn(s['rubric'][0]['question'],reply)
        self.assertEqual(s['target'],s['rubric'][0]['id'])


if __name__=='__main__':unittest.main()
