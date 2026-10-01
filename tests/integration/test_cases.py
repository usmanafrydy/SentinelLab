"""Investigation persistence, immutable evidence, concurrency, and compatibility."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen

from sentinellab.storage.database import StorageError, import_events, database_summary, initialize_database
from sentinellab.storage.alerts import save_detection, list_history, get_alert, alert_summary
from sentinellab.storage.cases import create_case, add_note, change_state, get_case, list_cases, case_history
from sentinellab.detection.engine import detect
from sentinellab.web.server import LocalServer

ROOT = Path(__file__).resolve().parents[2]


class CaseTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db = Path(temp.name) / 'events.db'
        import_events(ROOT / 'data/samples/day07_all_rules.jsonl', self.db)

    def query(self, sql):
        with closing(sqlite3.connect(self.db)) as conn:
            return conn.execute(sql).fetchall()

    def execute(self, sql):
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute(sql); conn.commit()

    def ready(self):
        save_detection(self.db)
        return list_history(self.db)['items'][0]['alert_id']

    def create(self):
        return create_case(self.db, self.ready(), 'Review sample success', 'lab_analyst')['case']

    def cli(self, *args):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/cases.py'), *args,
                                 '--database', str(self.db)], capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def test_reads_on_old_versions_do_not_migrate(self):
        for version in (1, 2):
            if version == 2: self.ready()
            before = self.db.read_bytes()
            self.assertEqual(list_cases(self.db)['total'], 0)
            self.assertIsNone(get_case(self.db, 1))
            self.assertIsNone(case_history(self.db, 1))
            self.assertEqual(self.db.read_bytes(), before)

    def test_missing_alert_and_missing_database_do_not_create_or_migrate(self):
        before = self.db.read_bytes()
        with self.assertRaises(StorageError): create_case(self.db, 'R1-'+'0'*64, 'Review', 'lab')
        self.assertEqual(self.db.read_bytes(), before)
        self.ready(); before = self.db.read_bytes()
        with self.assertRaises(StorageError): create_case(self.db, 'R1-'+'0'*64, 'Review', 'lab')
        self.assertEqual(self.db.read_bytes(), before)
        absent = self.db.parent / 'missing.db'
        with self.assertRaises(StorageError): create_case(absent, 'R1-'+'0'*64, 'Review', 'lab')
        self.assertFalse(absent.exists())

    def test_create_migrates_preserves_evidence_and_deduplicates(self):
        alert_id = self.ready()
        tables = ('events','imports','saved_alerts','alert_evidence','detection_runs','run_alerts')
        before = {t:self.query('SELECT * FROM '+t) for t in tables}
        first = create_case(self.db, alert_id, 'Review sample', 'lab')
        repeat = create_case(self.db, alert_id, 'Different title', 'another_label')
        self.assertTrue(first['created']); self.assertFalse(repeat['created'])
        self.assertEqual(first['case'], repeat['case'])
        self.assertEqual(database_summary(self.db)['schema_version'], 3)
        self.assertEqual(case_history(self.db, 1)['total'], 1)
        self.assertEqual(before, {t:self.query('SELECT * FROM '+t) for t in tables})
        self.assertEqual(self.query('PRAGMA foreign_key_check'), [])

    def test_note_state_close_correct_and_reopen_keep_history(self):
        case = self.create()
        alert_before = get_alert(self.db, case['alert_id'])
        note = add_note(self.db, 1, 'Synthetic example only.\nNeed context.', 'lab')
        self.assertEqual(note['revision'], 2)
        working = change_state(self.db, 1, 'in_progress', 'undecided', 'Reviewing originals', 'lab', 2)
        closed = change_state(self.db, 1, 'closed', 'benign', 'Synthetic exercise conclusion', 'lab', 3)
        corrected = change_state(self.db, 1, 'closed', 'suspicious', 'Demonstrate revised conclusion', 'lab', 4)
        reopened = change_state(self.db, 1, 'in_progress', 'undecided', 'Further review needed', 'lab', 5)
        self.assertEqual(reopened['revision'], 6)
        history = case_history(self.db, 1)['items']
        self.assertEqual([a['revision'] for a in history], list(range(1,7)))
        self.assertEqual(history[1]['text'], 'Synthetic example only.\nNeed context.')
        self.assertEqual(history[4]['before']['disposition'], 'benign')
        self.assertEqual(history[4]['after']['disposition'], 'suspicious')
        self.assertEqual(get_alert(self.db, case['alert_id']), alert_before)
        self.assertEqual(history[-1]['after']['status'], 'in_progress')

    def test_state_validation_and_stale_revision_never_write(self):
        self.create()
        before = self.db.read_bytes()
        for status, disposition, reason, revision in (
            ('closed','undecided','review',1), ('invalid','benign','review',1),
            ('open','invalid','review',1), ('open','undecided','same',1),
            ('in_progress','undecided','',1), ('in_progress','undecided','review',2)):
            with self.subTest(status=status,disposition=disposition,revision=revision):
                with self.assertRaises(StorageError):
                    change_state(self.db,1,status,disposition,reason,'lab',revision)
                self.assertEqual(self.db.read_bytes(),before)
        add_note(self.db,1,'New context','lab')
        with self.assertRaisesRegex(StorageError,'Refresh'):
            change_state(self.db,1,'closed','benign','review','lab',1)

    def test_closed_case_reopen_policy_and_notes(self):
        self.create()
        change_state(self.db,1,'closed','benign','Lab exercise','lab',1)
        for status, disposition in (('open','undecided'),('in_progress','benign')):
            with self.assertRaises(StorageError):
                change_state(self.db,1,status,disposition,'Reopen','lab',2)
        note = add_note(self.db,1,'Post-close clarification','lab')
        self.assertEqual(note['status'],'closed')
        self.assertEqual(note['revision'],3)

    def test_input_bounds_control_characters_and_sql_text(self):
        alert_id=self.ready()
        for title in ('',' '*4,'x'*121,'bad\x00','bad\u202e','bad\ud800'):
            with self.assertRaises(StorageError):create_case(self.db,alert_id,title,'lab')
        with self.assertRaises(StorageError):create_case(self.db,alert_id,'ok','x'*81)
        with self.assertRaises(StorageError):create_case(self.db,'invalid','ok','lab')
        create_case(self.db,alert_id,"'; DROP TABLE events; --",'lab')
        for note in ('','x'*4001,'bad\x1b'):
            with self.assertRaises(StorageError):add_note(self.db,1,note,'lab')
        literal='<img src=x onerror="alert(1)">\nTabs\tare text'
        add_note(self.db,1,literal,'lab')
        self.assertEqual(case_history(self.db,1)['items'][-1]['text'],literal)
        self.assertEqual(database_summary(self.db)['total_events'],16)

    def test_history_and_list_paging_filters_and_read_only(self):
        self.ready()
        for a in list_history(self.db)['items']:create_case(self.db,a['alert_id'],'Review','lab')
        for i in range(3):add_note(self.db,1,f'Note {i}','lab')
        change_state(self.db,1,'in_progress','undecided','Begin','lab',4)
        before=self.db.read_bytes()
        self.assertEqual(list_cases(self.db,limit=1)['next_offset'],1)
        self.assertEqual(list_cases(self.db,limit=1,offset=1)['items'][0]['id'],2)
        self.assertEqual(list_cases(self.db,status='in_progress')['total'],1)
        self.assertEqual(case_history(self.db,1,limit=2)['next_offset'],2)
        self.assertEqual(case_history(self.db,1,limit=2,offset=2)['items'][0]['revision'],3)
        self.assertIsNone(case_history(self.db,1,offset=100)['next_offset'])
        self.assertIsNone(get_case(self.db,999));self.assertIsNone(case_history(self.db,999))
        self.assertEqual(before,self.db.read_bytes())

    def test_numeric_and_page_bounds(self):
        for bad in (0,-1,True,2**63,'1'):
            with self.assertRaises(StorageError):get_case(self.db,bad)
        for kwargs in ({'limit':0},{'limit':201},{'offset':-1},{'offset':1000001}):
            with self.assertRaises(StorageError):list_cases(self.db,**kwargs)
            with self.assertRaises(StorageError):case_history(self.db,1,**kwargs)

    def test_failed_creation_rolls_back_migration(self):
        alert_id=self.ready();before=self.db.read_bytes()
        with patch('sentinellab.storage.cases._append_action',side_effect=sqlite3.IntegrityError):
            with self.assertRaises(StorageError):create_case(self.db,alert_id,'Review','lab')
        self.assertEqual(before,self.db.read_bytes())
        self.assertEqual(self.query('PRAGMA user_version'),[(2,)])

    def test_migration_table_conflict_rolls_back(self):
        alert_id=self.ready()
        self.execute('CREATE TABLE investigation_actions (unrelated TEXT)')
        with self.assertRaises(StorageError):create_case(self.db,alert_id,'Review','lab')
        self.assertEqual(self.query('PRAGMA user_version'),[(2,)])
        self.assertEqual(self.query("SELECT name FROM sqlite_master WHERE name='investigations'"),[])

    def test_failed_note_and_state_roll_back_current_state(self):
        self.create();before=self.db.read_bytes()
        with patch('sentinellab.storage.cases._append_action',side_effect=sqlite3.IntegrityError):
            with self.assertRaises(StorageError):add_note(self.db,1,'A note','lab')
            with self.assertRaises(StorageError):change_state(self.db,1,'closed','benign','review','lab',1)
        self.assertEqual(before,self.db.read_bytes())

    def test_concurrent_creates_notes_and_stale_state(self):
        alert_id=self.ready()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:create_case(self.db,alert_id,'Review','lab'),range(2)))
            self.assertEqual(sum(r['created'] for r in results),1)
            notes=list(pool.map(lambda n:add_note(self.db,1,f'Note {n}','lab'),range(2)))
        self.assertEqual(sorted(n['revision'] for n in notes),[2,3])
        def update(disposition):
            try:return change_state(self.db,1,'closed',disposition,'Review','lab',3)
            except StorageError:return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(update,('benign','suspicious')))
        self.assertEqual(sum(r is not None for r in results),1)
        self.assertEqual(case_history(self.db,1)['total'],4)

    def test_v3_works_with_existing_detection_import_and_browser_reads(self):
        self.create()
        before=self.db.read_bytes()
        self.assertEqual(detect(self.db)['alert_count'],3)
        self.assertEqual(self.db.read_bytes(),before)
        self.assertEqual(save_detection(self.db)['schema_version'],3)
        self.assertEqual(alert_summary(self.db)['saved_alerts'],3)
        self.assertEqual(import_events(ROOT/'data/samples/day07_all_rules.jsonl',self.db)['duplicates'],16)
        initialize_database(self.db)
        with LocalServer(self.db,0) as server:
            worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
            try:
                for path,key,value in (('/api/alerts/summary','saved_alerts',3),('/api/events','total_matches',16)):
                    with urlopen(server.origin+path) as response:
                        self.assertEqual(json.load(response)[key],value)
            finally:server.shutdown();worker.join()
        self.assertEqual(get_case(self.db,1)['revision'],1)

    def test_cli_persistence_and_exit_codes(self):
        alert_id=self.ready()
        code,result=self.cli('create','--alert-id',alert_id,'--title','Review','--author','lab')
        self.assertEqual(code,0);self.assertEqual(result['case']['revision'],1)
        code,result=self.cli('note','--case-id','1','--text','Check originals','--author','lab')
        self.assertEqual((code,result['revision']),(0,2))
        code,result=self.cli('state','--case-id','1','--status','in_progress','--disposition','undecided',
                             '--reason','Review underway','--author','lab','--expected-revision','2')
        self.assertEqual((code,result['revision']),(0,3))
        self.assertEqual(self.cli('get','--case-id','1')[1]['status'],'in_progress')
        self.assertEqual(self.cli('history','--case-id','1')[1]['total'],3)
        self.assertEqual(self.cli('list','--status','in_progress')[1]['total'],1)
        self.assertEqual(self.cli('get','--case-id','999')[0],1)
        self.assertEqual(self.cli('history','--case-id','999')[0],1)
        self.assertEqual(self.cli('note','--case-id','999','--text','note','--author','lab')[0],2)

    def test_unknown_or_malformed_schema_is_rejected(self):
        self.execute('PRAGMA user_version=99')
        with self.assertRaises(StorageError):list_cases(self.db)
        self.execute('PRAGMA user_version=3')
        with self.assertRaises(StorageError):get_case(self.db,1)
