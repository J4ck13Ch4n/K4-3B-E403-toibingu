import copy
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'codebase'))
import assessment
from curriculum import find_section


def raw_check(criterion, text='Giải thích.', statuses=None):
    points=assessment.requirements(criterion)
    statuses=statuses or ['met']*len(points)
    return {'id':criterion['id'], 'points':[{'point_id':p['id'],'status':s,'evidence':text if s!='missing' else '',
             'user_turn':1 if s!='missing' else 0,'diagnosis':'Test diagnosis'} for p,s in zip(points,statuses)],
            'contradiction':{'present':False,'evidence':'','user_turn':0},
            'focus_point':next((p['id'] for p,s in zip(points,statuses) if s!='met'),''),
            'probe':'Trong ví dụ lọc spam của cậu, điều gì sẽ xảy ra nếu hệ thống chỉ sử dụng các luật do người viết sẵn?' if any(s!='met' for s in statuses) else ''}


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.c=find_section('day1','ai_map')[1]['criteria'][0]
        self.messages=[{'role':'user','text':'Giải thích.'}]

    def test_every_question_has_atomic_requirements(self):
        from curriculum import LESSONS
        import app
        for c in [c for l in LESSONS for s in l['sections'] for c in s['criteria']]+app.CRITERIA:
            self.assertGreater(len(assessment.requirements(c)),0)

    def test_one_missing_point_prevents_pass(self):
        raw=raw_check(self.c,statuses=['met']*5+['missing'])
        result=assessment.normalize([raw],self.messages,[self.c])[0]
        self.assertEqual(result['status'],'missing')
        self.assertEqual(sum(p['status']=='met' for p in result['points']),5)

    def test_one_wrong_point_prevents_pass(self):
        raw=raw_check(self.c,statuses=['met']*5+['incorrect'])
        self.assertEqual(assessment.normalize([raw],self.messages,[self.c])[0]['status'],'incorrect')

    def test_unresolved_contradiction_overrides_all_points(self):
        raw=raw_check(self.c)
        raw['contradiction']={'present':True,'evidence':'Giải thích.','user_turn':1}
        raw['focus_point']='p1'
        self.assertEqual(assessment.normalize([raw],self.messages,[self.c])[0]['status'],'incorrect')

    def test_missing_duplicate_and_invented_points_rejected(self):
        for transform in [lambda r:r['points'].pop(),lambda r:r['points'][0].update(point_id='p2'),lambda r:r['points'][0].update(evidence='Bịa')]:
            raw=raw_check(self.c);transform(raw)
            with self.assertRaises(ValueError):assessment.normalize([raw],self.messages,[self.c])

    def test_assistant_quote_cannot_be_student_evidence(self):
        raw=raw_check(self.c,text='Đáp án của Mầm.')
        with self.assertRaises(ValueError):
            assessment.normalize([raw],[{'role':'assistant','text':'Đáp án của Mầm.'}]+self.messages,[self.c])

    def test_turn_attribution_must_match(self):
        raw=raw_check(self.c)
        raw['points'][0]['user_turn']=2
        with self.assertRaises(ValueError):assessment.normalize([raw],self.messages,[self.c])

    def test_dynamic_probe_and_repeat_fallback(self):
        raw=raw_check(self.c,statuses=['missing']*6)
        check=assessment.normalize([raw],self.messages,[self.c])[0]
        question=assessment.followup(check,self.c,self.messages,1)
        self.assertEqual(question,raw['probe'])
        messages=self.messages+[{'role':'assistant','text':question}]
        retry=assessment.followup(check,self.c,messages,2)
        self.assertNotEqual(question,retry)
        self.assertNotEqual(retry,self.c['question'])
        self.assertNotIn(assessment.requirements(self.c)[0]['expected'],retry)

    def test_leaking_probe_is_replaced_with_neutral_scenario(self):
        raw=raw_check(self.c,statuses=['met','met','missing','missing','missing','met'])
        raw['probe']='Cậu có thể giải thích deep learning là mạng nhiều tầng thuộc machine learning không?'
        check=assessment.normalize([raw],self.messages,[self.c])[0]
        self.assertNotEqual(assessment.followup(check,self.c,self.messages,1),raw['probe'])

    def test_wrong_assertion_stays_on_the_actual_claim(self):
        raw=raw_check(self.c,statuses=['incorrect']+['missing']*5)
        raw['probe']='Deep learning khác machine learning như thế nào?'
        check=assessment.normalize([raw],self.messages,[self.c])[0]
        question=assessment.followup(check,self.c,self.messages,1)
        self.assertIn('Giải thích.',question)
        self.assertNotIn('Deep learning',question)

    def test_independent_audit_can_reject_initial_pass(self):
        import io,json,app
        from unittest.mock import patch
        first=raw_check(self.c)
        second=raw_check(self.c,statuses=['met']*5+['missing'])
        def response(check,rid):
            return io.BytesIO(json.dumps({'status':'completed','id':rid,'output':[{'content':[{'type':'output_text','text':json.dumps({'checks':[check]})}]}]}).encode())
        with patch.dict(app.os.environ,{'OPENAI_API_KEY':'test'}),patch.object(app,'urlopen',side_effect=[response(first,'primary'),response(second,'audit')]) as call:
            checks,rid=app.evaluate(self.messages,[self.c])
        self.assertEqual(call.call_count,2)
        self.assertEqual(checks[0]['status'],'missing')
        self.assertEqual(checks[0]['audit_response_id'],'audit')

    def test_server_copies_student_turn_instead_of_generated_quote(self):
        raw=raw_check(self.c)
        for point in raw['points']:point.pop('evidence')
        raw['contradiction'].pop('evidence')
        normalized=assessment.normalize([raw],self.messages,[self.c])[0]
        self.assertTrue(all(p['evidence']=='Giải thích.' for p in normalized['points']))


if __name__=='__main__':unittest.main()
