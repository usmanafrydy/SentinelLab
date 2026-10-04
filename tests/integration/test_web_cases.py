"""Real HTTP investigation workflows and rejected writes."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from tests.integration import test_web as fixture
from sentinellab.storage.database import import_events
from sentinellab.storage.alerts import save_detection, list_history, get_alert
from sentinellab.storage.cases import case_history, get_case
from sentinellab.web.case_api import wire

ROOT = Path(__file__).resolve().parents[2]

class WebCaseTests(unittest.TestCase):
    setUp = fixture.WebTests.setUp
    cleanup = fixture.WebTests.cleanup
    request = fixture.WebTests.request

    def ready(self):
        import_events(ROOT / 'data/samples/day07_all_rules.jsonl', self.db)
        save_detection(self.db)
        return list_history(self.db)['items'][0]['alert_id']

    def post(self, path, data, **changes):
        headers = {'Origin': self.server.origin, 'X-SentinelLab-Token': self.server.token,
                   'Content-Type': 'application/json'}
        headers.update(changes)
        raw = data if isinstance(data, bytes) else json.dumps(data).encode()
        code, _, body = self.request('POST', path, raw, headers)
        return code, json.loads(body)

    def create(self):
        return self.post('/api/cases', {'alert_id': self.ready(), 'title': 'Review sample', 'author': 'lab'})

    def state(self, revision='1', **changes):
        data = dict(status='in_progress', disposition='undecided', reason='Review originals',
                    author='lab', expected_revision=revision)
        data.update(changes)
        return self.post('/api/cases/1/state', data)

    def test_old_schema_reads_do_not_write(self):
        for version in (1, 2):
            if version == 2: self.ready()
            before = self.db.read_bytes()
            self.assertEqual(json.loads(self.request('GET', '/api/cases')[2])['total'], 0)
            self.assertEqual(self.request('GET', '/api/cases/1')[0], 404)
            self.assertEqual(self.request('GET', '/api/cases/1/history')[0], 404)
            self.assertEqual(self.db.read_bytes(), before)

    def test_complete_workflow_duplicate_and_originals(self):
        code, result = self.create()
        self.assertEqual(code, 200)
        self.assertTrue(result['created'])
        self.assertEqual(result['case']['id'], '1')
        alert_id = result['case']['alert_id']
        before = get_alert(self.db, alert_id)
        duplicate = self.post('/api/cases', dict(alert_id=alert_id, title='Different', author='other'))[1]
        self.assertFalse(duplicate['created'])
        self.assertEqual(duplicate['case'], result['case'])
        note = '<img src=x onerror=alert(1)>\nSynthetic observation'
        self.assertEqual(self.post('/api/cases/1/notes', dict(text=note, author='lab'))[0], 200)
        self.assertEqual(self.state('2')[0], 200)
        self.assertEqual(self.state('3', status='closed', disposition='benign')[0], 200)
        self.assertEqual(self.state('4')[0], 200)
        history = json.loads(self.request('GET', '/api/cases/1/history')[2])
        self.assertEqual(history['total'], 5)
        self.assertEqual(history['items'][1]['text'], note)
        self.assertEqual(history['items'][-1]['revision'], '5')
        self.assertEqual(get_alert(self.db, alert_id), before)

    def test_stale_revision_has_recovery_code_and_no_write(self):
        self.create()
        self.post('/api/cases/1/notes', dict(text='New observation', author='second'))
        before = self.db.read_bytes()
        code, body = self.state()
        self.assertEqual((code, body['code']), (409, 'stale_revision'))
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual(self.state('2')[0], 200)

    def test_strict_json_and_types_do_not_write(self):
        self.create()
        before = self.db.read_bytes()
        invalid = [b'{}', b'null', b'[]', b'{', b'\xff', b'{"text":"x","text":"y","author":"lab"}',
                   b'{"text":NaN,"author":"lab"}', b'[' * 1100 + b']' * 1100,
                   {'text': 1, 'author': 'lab'}, {'text': 'x', 'author': 'lab', 'extra': 'x'},
                   {'text': '', 'author': 'lab'}, {'text': 'x'*4001, 'author': 'lab'}]
        for data in invalid:
            with self.subTest(data=str(data)[:60]):
                self.assertEqual(self.post('/api/cases/1/notes', data)[0], 400)
        for revision in (1, None, '0', '-1', '1.0', '9223372036854775808'):
            self.assertEqual(self.state(revision)[0], 400)
        self.assertEqual(self.db.read_bytes(), before)

    def test_all_case_writes_require_origin_host_token_and_bounded_json(self):
        self.create()
        before = self.db.read_bytes()
        for path in ('/api/cases', '/api/cases/1/notes', '/api/cases/1/state'):
            for header in ({'Origin':'null'}, {'Origin':'https://untrusted.invalid'},
                           {'Host':'untrusted.invalid'}, {'X-SentinelLab-Token':'wrong'},
                           {'Sec-Fetch-Site':'cross-site'}):
                self.assertEqual(self.post(path, {}, **header)[0], 403)
            self.assertEqual(self.post(path, {}, **{'Content-Type':'text/plain'})[0], 415)
            self.assertEqual(self.post(path, b'', **{'Content-Length':'65537'})[0], 413)
            self.assertEqual(self.post(path, b'', **{'Transfer-Encoding':'chunked'})[0], 411)
        self.assertEqual(self.db.read_bytes(), before)

    def test_paging_filters_routes_and_read_only_history(self):
        self.create()
        for item in list_history(self.db)['items'][1:]:
            self.post('/api/cases', dict(alert_id=item['alert_id'], title='Next', author='lab'))
        self.state()
        before = self.db.read_bytes()
        page = json.loads(self.request('GET', '/api/cases?limit=1')[2])
        self.assertEqual((page['total'], page['next_offset']), (3, 1))
        second = json.loads(self.request('GET', '/api/cases?limit=1&offset=1')[2])
        self.assertNotEqual(page['items'][0]['id'], second['items'][0]['id'])
        filtered = json.loads(self.request('GET', '/api/cases?status=in_progress')[2])
        self.assertEqual(filtered['total'], 1)
        history = json.loads(self.request('GET', '/api/cases/1/history?limit=1&offset=1')[2])
        self.assertEqual(history['items'][0]['revision'], '2')
        for query in ('limit=201','offset=-1','status=bad','unknown=x','limit=1&limit=2'):
            self.assertEqual(self.request('GET', '/api/cases?'+query)[0], 400)
        self.assertEqual(self.request('GET', '/api/cases/1?status=open')[0], 400)
        for path in ('/api/cases/0','/api/cases/no','/api/cases/1/delete'):
            self.assertEqual(self.request('GET', path)[0], 404)
        self.assertEqual(self.db.read_bytes(), before)
        for asset in ('cases.js','cases.css'):
            self.assertEqual(self.request('GET', '/static/'+asset)[0], 200)

    def test_failed_action_rolls_back(self):
        self.create()
        before = get_case(self.db, 1)
        with patch('sentinellab.storage.cases._append_action', side_effect=OSError('failure')):
            self.assertEqual(self.post('/api/cases/1/notes', dict(text='test',author='lab'))[0], 400)
        self.assertEqual(get_case(self.db, 1), before)
        self.assertEqual(case_history(self.db, 1)['total'], 1)

    def test_large_identifiers_are_decimal_strings(self):
        value = 9223372036854775807
        self.assertEqual(wire({'id':value,'items':[{'case_id':value,'revision':value}], 'total':1}),
                         {'id':str(value),'items':[{'case_id':str(value),'revision':str(value)}], 'total':1})

