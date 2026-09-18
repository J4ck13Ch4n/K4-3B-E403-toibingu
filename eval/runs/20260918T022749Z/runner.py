"""Run the documented golden set without changing real learner sessions.

G01-G17 call the configured AI; G18-G20 deliberately inject failures.
Semantic review of questions remains a separate step after this script.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import app


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def run():
    sys.stdout.reconfigure(encoding='utf-8')
    document = (ROOT / 'eval/golden-set.md').read_text(encoding='utf-8')
    rows = {line.split('|')[1].strip(): line.split('|')[3].strip()
            for line in document.splitlines() if line.startswith('| G')}
    answer_a = next(line[2:] for line in document.splitlines() if line.startswith('> Temperature'))
    texts = {key: value[1:-1] for key, value in rows.items()
             if value.startswith('“') and value.endswith('”')}
    texts['G11'] = answer_a
    texts['G13'] = answer_a + ' Temperature thấp cũng bảo đảm mọi thông tin đều đúng.'
    order = [c['id'] for c in app.CRITERIA]
    # None means rubric-based manual review, never automatic permission to pass.
    expected = {
        'G01': ['met', 'missing', 'missing', 'missing', 'missing'],
        'G02': ['missing'] * 5, 'G03': ['missing'] * 5,
        'G04': ['missing', 'incorrect', 'missing', 'missing', 'missing'],
        'G05': ['missing'] * 5,
        'G06': ['met', 'missing', 'missing', 'missing', 'met'],
        'G07': ['missing', 'missing', 'missing', 'missing', 'missing'],
        'G08': [None, 'met', 'missing', 'missing', 'missing'],
        'G09': ['met', 'missing', 'missing', 'missing', 'missing'],
        'G10': ['missing', 'missing', 'missing', 'met', 'missing'],
        'G11': ['met'] * 5,
        'G12': [None, 'met', 'missing', 'missing', 'missing'],
        'G13': ['met', 'incorrect', 'met', 'met', 'met'],
        'G14': [None, 'met', 'missing', 'missing', 'missing'],
        'G15': ['missing'] * 5, 'G16': ['missing'] * 5,
        'G17': ['missing'] * 5,
    }
    now = datetime.now(timezone.utc)
    run_id = now.strftime('%Y%m%dT%H%M%SZ')
    folder = ROOT / 'eval/runs' / run_id
    folder.mkdir(parents=True, exist_ok=False)
    report = {
        'run_id': run_id, 'started_at_utc': now.isoformat(),
        'operator': 'Codex', 'semantic_reviewer': 'pending',
        'model': os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini'),
        'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'sha256': {p: digest(p) for p in ['app.py', 'assessment.py', 'curriculum.py', 'tools/run_golden_set.py']},
        'golden_set_sha256_before_run': digest('eval/golden-set.md'),
        'expected_status_order': order, 'expected': expected,
        'cases': [],
    }
    output = folder / 'results.json'

    def write():
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    def require(condition, message):
        if not condition:
            raise AssertionError(message)

    def rejected(session, evaluator):
        before = copy.deepcopy(session)
        stored = app.get_session(session['id'])
        try:
            app.advance(session, 'Mình chưa biết.', evaluator)
        except app.AppError as exc:
            require(session == before, 'Failed request mutated in-memory session')
            require(app.get_session(session['id']) == stored, 'Failed request mutated database')
            return str(exc)
        raise AssertionError('Invalid evaluation was accepted')

    def missing(messages):
        return [{'id': c['id'], 'status': 'missing', 'evidence': ''} for c in app.CRITERIA], 'injected-retry'

    write()
    with tempfile.TemporaryDirectory(prefix='teachback-golden-') as temp:
        app.DB = Path(temp) / 'sessions.sqlite3'
        for number in range(1, 21):
            cid = f'G{number:02}'
            session = app.create_session()
            result = {'id': cid, 'mode': 'live_ai' if number <= 17 else 'injected_failure',
                      'started_at_utc': datetime.now(timezone.utc).isoformat(), 'steps': []}
            print(f'{cid} started ({result["mode"]})', flush=True)
            try:
                if number <= 17:
                    answers = [texts[cid]] if cid in texts else []
                    if cid == 'G12':
                        answers = [texts['G04'], 'Mình sửa lại: temperature thấp ưu tiên token xác suất cao, ít ngẫu nhiên nên thường ổn định hơn, không bảo đảm luôn đúng hoặc giống hệt.']
                    if cid == 'G17':
                        answers = ['Mình chưa biết'] * 4
                    for text in answers:
                        app.advance(session, text)
                        app.save(session)
                        result['steps'].append(copy.deepcopy(session))
                        result['last_public_session'] = app.public_session(session)
                        write()
                    actual = [c['status'] for c in session['checks']]
                    result['actual'] = actual
                    require(all(e is None or a == e for a, e in zip(actual, expected[cid])),
                            f'Status mismatch: {actual}; expected {expected[cid]}')
                    require(session['status'] == ('completed' if cid == 'G11' else 'review' if cid == 'G17' else 'active'), 'Unexpected session state')
                    if cid == 'G11':
                        require(session['probes'] == 0 and set(session['initial']) == set(order), 'Initial completion not recorded')
                    if cid == 'G12':
                        require(result['steps'][0]['checks'][1]['status'] == 'incorrect', 'Initial misconception not detected')
                        require('low' not in session['initial'], 'Correction recorded as initial knowledge')
                    if cid == 'G17':
                        require(session['probes'] == 3 and session['turn'] == 4, 'Incorrect turn limit')
                        try:
                            app.advance(session, 'Thêm một lượt.')
                        except app.AppError as exc:
                            result['post_completion_error'] = str(exc)
                        else:
                            raise AssertionError('Ended session accepted another turn')
                elif cid == 'G18':
                    def timeout(messages):
                        raise app.AppError('Injected API timeout', 502)
                    result['errors'] = [rejected(session, timeout)]
                    app.advance(session, 'Mình chưa biết.', missing)
                    app.save(session)
                    require(session['turn'] == 1, 'Retry failed')
                    result['retry_succeeded'] = True
                elif cid == 'G19':
                    result['errors'] = []
                    for quote in ['Bằng chứng không có trong hội thoại.', app.OPENING]:
                        def fabricated(messages, quote=quote):
                            checks, _ = missing(messages)
                            checks[0].update(status='met', evidence=quote)
                            return checks, 'injected-fabricated'
                        result['errors'].append(rejected(session, fabricated))
                else:
                    result['errors'] = []
                    for variant in ['missing_id', 'duplicate_id', 'unknown_id']:
                        def malformed(messages, variant=variant):
                            checks, _ = missing(messages)
                            if variant == 'missing_id':
                                checks.pop()
                            else:
                                checks[0]['id'] = checks[1]['id'] if variant == 'duplicate_id' else 'unknown'
                            return checks, 'injected-' + variant
                        result['errors'].append({'variant': variant, 'error': rejected(session, malformed)})
                result['automated_result'] = 'pass'
            except Exception as exc:
                result['automated_result'] = 'fail'
                result['error'] = f'{type(exc).__name__}: {exc}'
            result['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
            result['semantic_review'] = 'pending' if number <= 17 else 'not_applicable'
            report['cases'].append(result)
            write()
            print(f'{cid}: {result["automated_result"]} {result.get("error", "")}', flush=True)
    report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    write()
    print(f'Report: {output}', flush=True)
    return 0 if all(c['automated_result'] == 'pass' for c in report['cases']) else 1


if __name__ == '__main__':
    raise SystemExit(run())
