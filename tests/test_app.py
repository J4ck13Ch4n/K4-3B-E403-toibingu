import copy
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import app


def evaluator(statuses):
    def run(messages):
        return [{'id': c['id'], 'status': status, 'evidence': messages[-1]['text'] if status != 'missing' else ''}
                for c, status in zip(app.CRITERIA, statuses)], 'test-response'
    return run


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(app, 'DB', Path(self.temp.name) / 'test.sqlite3')
        self.db_patch.start()
        self.session = app.create_session()

    def tearDown(self):
        self.db_patch.stop()
        self.temp.cleanup()

    def test_complete_immediately(self):
        app.advance(self.session, 'Lời giải thích đủ.', evaluator(['met'] * 5))
        self.assertEqual(self.session['status'], 'completed')
        self.assertEqual(self.session['probes'], 0)
        self.assertEqual(len(self.session['initial']), 5)

    def test_stop_after_three_probes_and_four_answers(self):
        for index in range(4):
            app.advance(self.session, 'Chưa biết.', evaluator(['missing'] * 5))
            self.assertEqual(self.session['probes'], min(index + 1, 3))
        self.assertEqual(self.session['status'], 'review')
        with self.assertRaises(app.AppError):
            app.advance(self.session, 'Thêm nữa.', evaluator(['met'] * 5))

    def test_correct_after_probing_and_record_target(self):
        app.advance(self.session, 'Giải thích lần đầu.', evaluator(['met', 'missing', 'missing', 'missing', 'missing']))
        app.advance(self.session, 'Bổ sung.', evaluator(['met'] * 5))
        self.assertEqual(self.session['initial'], ['definition'])
        self.assertEqual(self.session['history'][1]['prompted_for'], 'low')
        app.save(self.session)
        self.assertEqual(app.get_session(self.session['id']), self.session)
        self.assertEqual(app.dashboard()['criteria'][1]['prompted'], 1)

    def test_misconception_prioritized_and_retracted(self):
        app.advance(self.session, 'Lần đầu.', evaluator(['met'] * 4 + ['missing']))
        app.advance(self.session, 'Mâu thuẫn.', evaluator(['incorrect'] + ['met'] * 3 + ['missing']))
        self.assertEqual(self.session['target'], 'sampling')
        self.assertEqual(self.session['checks'][0]['status'], 'incorrect')
        app.advance(self.session, 'Làm rõ sampling.', evaluator(['incorrect'] + ['met'] * 4))
        self.assertEqual(self.session['target'], 'definition')
        self.assertIn('mình đã hiểu', self.session['messages'][-1]['text'])

    def test_failure_preserves_turn(self):
        before = copy.deepcopy(self.session)
        def fail(_):
            raise app.AppError('API timeout', 502)
        with self.assertRaises(app.AppError):
            app.advance(self.session, 'Câu trả lời.', fail)
        self.assertEqual(self.session, before)

    def test_no_fabricated_evidence(self):
        checks, _ = evaluator(['met'] * 5)([{'text': 'Không có trong lời học viên.'}])
        with self.assertRaises(app.AppError):
            app.validate_checks(checks, [{'role': 'user', 'text': 'Tôi chưa biết.'}])

    def test_invalid_and_duplicate_checks(self):
        checks, _ = evaluator(['missing'] * 5)([{'text': 'x'}])
        checks[-1]['id'] = checks[0]['id']
        with self.assertRaises(app.AppError):
            app.validate_checks(checks, [])

    def test_input_limits_and_active_feedback(self):
        for text in ('', ' ', 'a' * 6001, None):
            with self.assertRaises(app.AppError):
                app.advance(self.session, text, evaluator(['met'] * 5))
        app.advance(self.session, 'Lời học viên.', evaluator(['met'] + ['missing'] * 4))
        public = app.public_session(self.session)
        self.assertNotIn('history', public)
        self.assertNotIn('evidence', public['checks'][0])

    def test_missing_key_is_explicit(self):
        with patch.dict(app.os.environ, {'OPENAI_API_KEY': ''}):
            with self.assertRaises(app.AppError) as error:
                app.evaluate([])
        self.assertEqual(error.exception.status, 503)

    def test_responses_request_and_parsing(self):
        messages = [{'role': 'user', 'text': 'Giải thích.'}]
        checks, _ = evaluator(['met'] * 5)(messages)
        response = {'status': 'completed', 'id': 'resp_test', 'output': [{'content': [{'type': 'output_text', 'text': json.dumps({'checks': checks})}]}]}
        import io
        with patch.dict(app.os.environ, {'OPENAI_API_KEY': 'test-only'}), patch.object(app, 'urlopen', return_value=io.BytesIO(json.dumps(response).encode())) as mock:
            actual, rid = app.evaluate(messages)
        request = mock.call_args.args[0]
        payload = json.loads(request.data)
        self.assertFalse(payload['store'])
        self.assertTrue(payload['text']['format']['strict'])
        self.assertEqual(actual, checks)
        self.assertEqual(rid, 'resp_test')


class HTTPTests(unittest.TestCase):
    setUp = FlowTests.setUp
    tearDown = FlowTests.tearDown
    def test_http_roundtrip(self):
        server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        def request(path, body=None, origin=None):
            headers = {'Content-Type': 'application/json'}
            if origin:
                headers['Origin'] = origin
            req = Request(base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
            with urlopen(req) as response:
                return response.read()
        try:
            self.assertIn(b'TeachBack', request('/'))
            self.assertEqual(len(json.loads(request('/api/config'))['criteria']), 5)
            sid = json.loads(request('/api/sessions', {}))['id']
            with patch.object(app, 'advance', side_effect=lambda s, t: original(s, t, evaluator(['met'] * 5))):
                result = json.loads(request(f'/api/sessions/{sid}/turns', {'text': 'Đủ.', 'expected_turn': 0}))
            self.assertEqual(result['status'], 'completed')
            with self.assertRaises(HTTPError) as error:
                request(f'/api/sessions/{sid}/turns', {'text': 'Lặp.', 'expected_turn': 0})
            self.assertEqual(error.exception.code, 409)
            error.exception.close()
            for path in ('/.env', '/data/README.md', '/../app.py'):
                with self.assertRaises(HTTPError) as error:
                    request(path)
                self.assertEqual(error.exception.code, 404)
                error.exception.close()
            with self.assertRaises(HTTPError) as error:
                request('/api/sessions', {}, 'https://example.com')
            self.assertEqual(error.exception.code, 403)
            error.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


original = app.advance
if __name__ == '__main__':
    unittest.main()
