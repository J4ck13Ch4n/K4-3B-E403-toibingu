"""Isolated browser integration check using test evaluation, never the user's DB."""
import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'codebase'),str(ROOT/'runtime'/'browser')]
from playwright.sync_api import sync_playwright, expect
import app


def judge(messages,criteria):
    text=messages[-1]['text']
    return [{'id':c['id'],'status':'missing' if text=='unknown' else 'met','evidence':'' if text=='unknown' else text} for c in criteria], 'browser-test'


with tempfile.TemporaryDirectory() as directory, patch.object(app,'DB',Path(directory)/'browser.sqlite3'), patch.object(app,'evaluate',side_effect=judge), patch.dict(app.os.environ,{'OPENAI_API_KEY':'test-not-real'}):
    server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(channel='msedge',headless=True)
            page=browser.new_page(viewport={'width':1440,'height':1000})
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}')
            page.locator('.lesson-card').first.wait_for()
            assert page.locator('.lesson-card').count()==2
            assert page.locator('.section-card').count()==8
            page.locator('[data-select="day2"]').click()
            assert page.locator('.section-card').count()==7
            page.locator('[data-practice="problem"]').click()
            page.locator('#composer').wait_for(state='visible')
            assert page.locator('.practice-check').count()==4
            page.locator('#answer').fill('sample answer')
            page.locator('#send').click()
            page.locator('#result').wait_for(state='visible')
            assert '4/4' in page.locator('#result').inner_text()
            page.locator('#next-part').click()
            expect(page.locator('[data-select="day2"]')).to_contain_text('4/22')
            page.reload()
            expect(page.locator('[data-select="day2"]')).to_contain_text('4/22')
            page.locator('[data-select="day2"]').click()
            page.locator('[data-practice="problem"]').click()
            for _ in range(4):
                page.locator('#answer').fill('unknown')
                page.locator('#send').click()
                expect(page.locator('#thinking')).to_be_hidden()
            page.locator('#result').wait_for(state='visible')
            assert '0/4' in page.locator('#result').inner_text()
            page.locator('#next-part').click()
            expect(page.locator('[data-select="day2"]')).to_contain_text('0/22')
            page.screenshot(path=str(ROOT/'runtime'/'lessons-desktop.png'),full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('() => document.documentElement.scrollWidth <= window.innerWidth')
            page.screenshot(path=str(ROOT/'runtime'/'lessons-mobile.png'),full_page=True)
            page.locator('[data-page="dashboard"]').click()
            page.locator('#dashboard-lesson').select_option('day2')
            expect(page.locator('tbody tr')).to_have_count(22)
            assert not errors,errors
            browser.close()
            print('Browser passed: lessons, four criteria, success, retry, 3-probe limit, persistence, dashboard, mobile overflow.')
    finally:
        server.shutdown();server.server_close();thread.join()
