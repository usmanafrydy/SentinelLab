"""Faithful bounded snapshots, inert rendering, CLI files and protected HTTP."""
from contextlib import closing, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import re
import sqlite3
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

from sentinellab import reports
from sentinellab.storage.database import StorageError, import_events
from sentinellab.storage.alerts import save_detection, list_history, get_alert
from sentinellab.storage.cases import create_case, add_note, change_state, CaseConflict, case_history
from sentinellab.web.auth import Auth, create_account, IDLE_SECONDS
from sentinellab.web.server import LocalServer
from tests.integration import test_web as web_fixture

ROOT = Path(__file__).resolve().parents[2]


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'events.db'
        import_events(ROOT / 'data/samples/day07_all_rules.jsonl', self.db)
        save_detection(self.db)
        alert = next(a for a in list_history(self.db)['items'] if a['rule_id'] == 'R3')
        self.alert_id = alert['alert_id']
        self.case = create_case(self.db, self.alert_id, 'Review synthetic success', 'lab')['case']

    def report(self, **kwargs):
        return reports.build_report(self.db, self.case['id'], **kwargs)

    def test_both_formats_preserve_all_saved_fields_and_database_bytes(self):
        add_note(self.db, self.case['id'], 'Ask the account owner.\nAbhi tasdeeq nahi hui.', 'lab')
        change_state(self.db, self.case['id'], 'in_progress', 'suspicious', 'Further investigation required.', 'lab', 2)
        before = self.db.read_bytes()
        report = self.report(expected_revision=3)
        decoded = json.loads(reports.render_report(report, 'json'))
        self.assertEqual(decoded, report)
        self.assertEqual(report['alert'], reports._string_ids(get_alert(self.db, self.alert_id)['alert']))
        self.assertEqual(report['actions'], reports._string_ids(case_history(self.db, self.case['id'])['items']))
        with closing(sqlite3.connect(self.db)) as conn:
            for item in report['evidence']:
                original = conn.execute('SELECT original_record FROM events WHERE id=?', (item['internal_id'],)).fetchone()[0]
                self.assertEqual(item['original_record'], original)
        markdown = reports.render_report(report, 'markdown').decode()
        blocks = [json.loads(b) for b in re.findall(r'^```json\n(.*?)\n```$', markdown, re.M | re.S)]
        self.assertEqual(blocks, [{k: report[k] for k in ('report_version', 'exported_at')},
                         *[report[k] for k in ('case', 'alert', 'first_detection_run', 'actions', 'evidence', 'limitations')]])
        self.assertEqual(self.db.read_bytes(), before)

    def test_each_rule_exports_parameters_references_and_roles(self):
        for item in list_history(self.db)['items']:
            case = create_case(self.db, item['alert_id'], 'Rule check', 'lab')['case']
            report = reports.build_report(self.db, case['id'])
            self.assertEqual(report['alert']['parameters']['threshold'], 10 if item['rule_id'] == 'R2' else 5)
            for row, ref in zip(report['evidence'], report['alert']['evidence']):
                self.assertEqual(row['internal_id'], ref['internal_id'])
                self.assertEqual(row['role'], ref.get('role', 'failure'))

    def test_full_history_not_only_visible_page_and_closed_conclusion(self):
        for n in range(22):
            add_note(self.db, self.case['id'], f'Observation {n}', 'lab')
        change_state(self.db, self.case['id'], 'closed', 'benign', 'Synthetic scenario reviewed.', 'lab', 23)
        report = self.report()
        self.assertEqual(len(report['actions']), 24)
        self.assertEqual(report['case']['disposition'], 'benign')
        self.assertEqual(report['case']['revision'], '24')

    def test_stale_revision_and_invalid_ids(self):
        add_note(self.db, self.case['id'], 'A new note', 'lab')
        with self.assertRaises(CaseConflict): self.report(expected_revision=1)
        for value in (0, -1, True, 2**63, '1'):
            with self.assertRaises(StorageError): reports.build_report(self.db, value)
            with self.assertRaises(StorageError): self.report(expected_revision=value)

    def test_missing_case_database_and_old_schemas_do_not_migrate(self):
        self.assertIsNone(reports.build_report(self.db, 999))
        absent = self.db.parent / 'missing.db'
        with self.assertRaises(StorageError): reports.build_report(absent, 1)
        self.assertFalse(absent.exists())
        old = self.db.parent / 'old.db'
        import_events(ROOT / 'data/samples/day07_all_rules.jsonl', old)
        for version in (1, 2):
            if version == 2: save_detection(old)
            before = old.read_bytes()
            self.assertIsNone(reports.build_report(old, 1))
            self.assertEqual(old.read_bytes(), before)

    def test_hostile_text_stays_inside_dynamic_fences(self):
        hostile = '```\n# Fake conclusion\n``````\n<script>alert(1)</script>\n[click](https://example.invalid)'
        add_note(self.db, self.case['id'], hostile, 'lab')
        report = self.report()
        markdown = reports.render_report(report, 'markdown').decode()
        self.assertIn('```````json\n', markdown)
        self.assertEqual(json.loads(reports.render_report(report, 'json'))['actions'][-1]['text'], hostile)
        # All stored markup is JSON text within an unbreakable fence, never a raw heading/tag line.
        self.assertNotIn('\n# Fake conclusion\n', markdown)
        self.assertNotIn('\n<script>', markdown)

    def test_large_case_ids_are_decimal_strings(self):
        large = 2**53 + 7
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('UPDATE investigations SET id=?', (large,))
            conn.execute('UPDATE investigation_actions SET case_id=?', (large,))
            conn.commit()
        report = reports.build_report(self.db, large)
        self.assertEqual(report['case']['id'], str(large))
        self.assertEqual(report['actions'][0]['case_id'], str(large))

    def test_row_source_and_encoded_limits_fail_without_partial_reports(self):
        before = self.db.read_bytes()
        with patch.object(reports, 'MAX_SOURCE_BYTES', 10):
            with self.assertRaisesRegex(StorageError, 'source limit'): self.report()
        with patch.object(reports, 'MAX_OUTPUT_BYTES', 100):
            for format in ('json', 'markdown'):
                with self.assertRaisesRegex(StorageError, '16 MiB'): reports.render_report(self.report(), format)
        with self.assertRaises(StorageError): reports.render_report(self.report(), 'html')
        self.assertEqual(self.db.read_bytes(), before)
        with closing(sqlite3.connect(self.db)) as conn:
            for revision in range(2, 1002):
                conn.execute('INSERT INTO investigation_actions(case_id,revision,kind,occurred_at,author,text,before_json,after_json) '
                             "VALUES (?,?, 'note', '2026-10-03T00:00:00+00:00', 'lab', 'test', '{}','{}')", (self.case['id'], revision))
            conn.commit()
        with self.assertRaisesRegex(StorageError, 'row'): self.report()

    def test_missing_evidence_fails_instead_of_omitting_it(self):
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('DELETE FROM events WHERE id=(SELECT event_id FROM alert_evidence WHERE alert_id=? LIMIT 1)', (self.alert_id,))
            conn.commit()
        with self.assertRaisesRegex(StorageError, 'inconsistent'): self.report()

    def test_inconsistent_history_fails_instead_of_misreporting(self):
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute("UPDATE investigation_actions SET after_json='{}'")
            conn.commit()
        with self.assertRaisesRegex(StorageError, 'inconsistent'): self.report()

    def test_wal_writer_during_export_cannot_mix_case_and_history(self):
        with closing(sqlite3.connect(self.db)) as conn: conn.execute('PRAGMA journal_mode=WAL')
        original = reports._rows
        changed = False
        def interleave(conn, query, *args, **kwargs):
            nonlocal changed
            rows = original(conn, query, *args, **kwargs)
            if 'FROM investigations WHERE' in query and not changed:
                changed = True
                add_note(self.db, self.case['id'], 'Committed after snapshot began.', 'other')
            return rows
        with patch.object(reports, '_rows', side_effect=interleave):
            report = self.report()
        self.assertTrue(changed)
        self.assertEqual(report['case']['revision'], '1')
        self.assertEqual(len(report['actions']), 1)
        self.assertEqual(self.report()['case']['revision'], '2')

    def test_cli_private_output_refuses_overwrite_and_other_locations(self):
        spec = importlib.util.spec_from_file_location('export_cli_test', ROOT / 'scripts/export_report.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with patch.object(module, 'ROOT', self.db.parent), redirect_stdout(io.StringIO()):
            argv = ['--database', str(self.db), '--case-id', str(self.case['id']), '--format', 'json']
            self.assertEqual(module.main(argv), 0)
            output = self.db.parent / 'reports/generated/sentinellab-case-1-rev-1.json'
            data = output.read_bytes()
            self.assertEqual(json.loads(data)['case']['id'], '1')
            self.assertEqual(module.main(argv), 2)
            self.assertEqual(output.read_bytes(), data)
            before = self.db.read_bytes()
            self.assertEqual(module.main(argv + ['--output', str(self.db)]), 2)
            self.assertEqual(self.db.read_bytes(), before)
            self.assertEqual(module.main(argv + ['--expected-revision', '99']), 2)

    def test_cli_removes_new_file_when_close_fails(self):
        spec = importlib.util.spec_from_file_location('export_cli_failure', ROOT / 'scripts/export_report.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        real_open = Path.open
        class FailingClose:
            def __init__(self, stream): self.stream = stream
            def __enter__(self): return self.stream
            def __exit__(self, *args):
                self.stream.close()
                raise OSError('Simulated flush failure')
        def opened(path, mode='r', *args, **kwargs):
            stream = real_open(path, mode, *args, **kwargs)
            return FailingClose(stream) if mode == 'xb' else stream
        with patch.object(module, 'ROOT', self.db.parent), patch.object(Path, 'open', opened), redirect_stdout(io.StringIO()):
            self.assertEqual(module.main(['--database', str(self.db), '--case-id', '1', '--format', 'json']), 2)
        self.assertEqual(list((self.db.parent / 'reports/generated').iterdir()), [])


class ReportHTTPTests(unittest.TestCase):
    request = web_fixture.WebTests.request
    cleanup = web_fixture.WebTests.cleanup

    @classmethod
    def setUpClass(cls):
        cls.account_temp = tempfile.TemporaryDirectory()
        cls.account = Path(cls.account_temp.name) / 'account.json'
        create_account(cls.account, 'report_test', 'Synthetic report password only 2026')

    @classmethod
    def tearDownClass(cls): cls.account_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'events.db'
        import_events(ROOT / 'data/samples/day07_all_rules.jsonl', self.db)
        save_detection(self.db)
        self.case = create_case(self.db, list_history(self.db)['items'][0]['alert_id'], 'HTTP case', 'lab')['case']
        self.now = 10.0
        self.auth = Auth(self.account, clock=lambda: self.now)
        self.server = LocalServer(self.db, port=0, auth=self.auth)
        self.worker = Thread(target=self.server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
        self.worker.start(); self.addCleanup(self.cleanup)
        code, key = self.auth.login('report_test', 'Synthetic report password only 2026')
        self.assertEqual(code, 200)
        self.headers = {'Cookie': f'{self.server.cookie_name}={key}'}
        self.path = f'/api/cases/{self.case["id"]}/report?format=json&revision=1'

    def test_attachments_match_and_reads_preserve_database(self):
        before = self.db.read_bytes()
        for format, extension in (('json', 'json'), ('markdown', 'md')):
            code, headers, data = self.request('GET', self.path.replace('format=json', 'format='+format), headers=self.headers)
            self.assertEqual(code, 200, data)
            self.assertEqual(headers['Content-Disposition'], f'attachment; filename="sentinellab-case-1-rev-1.{extension}"')
            self.assertEqual(headers['Cache-Control'], 'no-store')
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
            self.assertNotIn(b'Synthetic report password', data)
            self.assertNotIn(str(self.db).encode(), data)
        self.assertEqual(self.db.read_bytes(), before)

    def test_anonymous_cross_site_and_expired_downloads_fail(self):
        self.assertEqual(self.request('GET', self.path)[0], 401)
        self.assertEqual(self.request('GET', self.path, headers={**self.headers, 'Origin':'https://example.invalid'})[0], 403)
        self.now += IDLE_SECONDS + 1
        self.assertEqual(self.request('GET', self.path, headers=self.headers)[0], 401)

    def test_stale_missing_and_invalid_queries_are_not_attachments(self):
        cases = [(self.path.replace('revision=1','revision=2'),409),
                 (self.path.replace('/1/', '/999/'),404),
                 (self.path+'&format=json',400), (self.path+'&extra=x',400),
                 (self.path.replace('format=json','format=html'),400),
                 (self.path.replace('&revision=1',''),400)]
        for path, expected in cases:
            code, headers, data = self.request('GET', path, headers=self.headers)
            self.assertEqual(code, expected, data)
            self.assertNotIn('Content-Disposition', headers)
