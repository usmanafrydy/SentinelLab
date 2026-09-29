"""Persistent alert lifecycle, explicit migration, concurrency, and failure safety."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from sentinellab.detection.engine import detect
from sentinellab.storage.alerts import save_detection, alert_summary, list_history, get_alert
from sentinellab.storage.database import StorageError, import_events, initialize_database, database_summary
from sentinellab.storage.search import get_event, search_events
from tests.integration.test_detection import ROOT, failures


class AlertStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.db = self.folder / "events.db"
        import_events(ROOT / "data/samples/day07_all_rules.jsonl", self.db)

    def query(self, sql, values=()):
        with closing(sqlite3.connect(self.db)) as conn:
            return conn.execute(sql, values).fetchall()

    def execute(self, sql):
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute(sql)
            conn.commit()

    def original_rows(self):
        return self.query("SELECT * FROM events ORDER BY id"), self.query("SELECT * FROM imports ORDER BY id")

    def test_migration_preserves_originals_and_links_all_evidence(self):
        before = self.original_rows()
        previews = detect(self.db)["alerts"]
        result = save_detection(self.db)
        self.assertEqual((result["new_alerts"], result["existing_alerts"]), (3, 0))
        self.assertEqual(before, self.original_rows())
        self.assertEqual(database_summary(self.db)["schema_version"], 2)
        self.assertEqual(self.query("PRAGMA foreign_key_check"), [])
        for alert in previews:
            saved = get_alert(self.db, alert["alert_id"])
            self.assertEqual(saved["alert"], alert)
            links = self.query("SELECT event_id, role FROM alert_evidence WHERE alert_id=? ORDER BY position", (alert["alert_id"],))
            self.assertEqual([x[0] for x in links], [ref["internal_id"] for ref in alert["evidence"]])
            for ref in alert["evidence"]:
                self.assertEqual(get_event(self.db, ref["internal_id"])["event_id"], ref["event_id"])
            if alert["rule_id"] == "R3":
                self.assertEqual(links[-1][1], "triggering_success")
        self.assertEqual(search_events(self.db)["total_matches"], 16)

    def test_repeated_save_deduplicates_but_records_each_run(self):
        save_detection(self.db)
        original = self.query("SELECT * FROM saved_alerts ORDER BY alert_id")
        second = save_detection(self.db)
        self.assertEqual((second["new_alerts"], second["existing_alerts"], second["total_saved_alerts"]), (0, 3, 3))
        self.assertEqual(original, self.query("SELECT * FROM saved_alerts ORDER BY alert_id"))
        self.assertEqual(self.query("SELECT COUNT(*) FROM run_alerts"), [(6,)])
        self.assertEqual(alert_summary(self.db)["detection_runs"], 2)

    def test_preview_and_history_never_write_or_migrate(self):
        for version in (1, 2):
            if version == 2:
                save_detection(self.db)
            before = self.db.read_bytes()
            self.assertEqual(detect(self.db)["alert_count"], 3)
            alert_summary(self.db)
            list_history(self.db)
            list_history(self.db, runs=True)
            get_alert(self.db, "R1-" + "0" * 64)
            self.assertEqual(before, self.db.read_bytes())

    def test_selected_rules_and_zero_alert_run_record_configurations(self):
        empty = self.folder / "empty.db"
        initialize_database(empty)
        result = save_detection(empty, "R2")
        self.assertEqual(result["alert_count"], 0)
        run = list_history(empty, runs=True)["items"][0]
        self.assertEqual(run["configurations"], [{"rule_id": "R2", "rule_version": "1.0.0", "threshold": 10, "window_seconds": 600}])
        self.assertEqual((run["events_scanned"], run["max_event_id"], run["max_import_id"]), (0, 0, 0))
        save_detection(self.db, "R1")
        result = save_detection(self.db)
        self.assertEqual((result["new_alerts"], result["existing_alerts"]), (2, 1))

    def test_failed_evaluation_rolls_back_migration(self):
        before = self.original_rows()
        with patch("sentinellab.storage.alerts.evaluate_snapshot", side_effect=StorageError("evidence limit")):
            with self.assertRaises(StorageError):
                save_detection(self.db)
        self.assertEqual(self.query("PRAGMA user_version"), [(1,)])
        self.assertEqual(self.query("SELECT name FROM sqlite_master WHERE name='saved_alerts'"), [])
        self.assertEqual(self.original_rows(), before)

    def test_partial_writes_roll_back_entire_run(self):
        save_detection(self.db, "R1")
        before = alert_summary(self.db)
        self.execute("CREATE TRIGGER fail_alert BEFORE INSERT ON saved_alerts WHEN NEW.rule_id='R3' BEGIN SELECT RAISE(ABORT, 'test'); END")
        with self.assertRaises(StorageError):
            save_detection(self.db)
        self.assertEqual(alert_summary(self.db), before)
        self.assertEqual(self.query("SELECT COUNT(*) FROM run_alerts"), [(1,)])
        self.assertEqual(self.query("PRAGMA foreign_key_check"), [])

    def test_event_limit_and_invalid_stored_time_leave_v1_unchanged(self):
        from sentinellab.detection.common import read_snapshot
        before = self.original_rows()
        with patch("sentinellab.storage.alerts.read_snapshot", side_effect=lambda conn: read_snapshot(conn, limit=5)):
            with self.assertRaises(StorageError):
                save_detection(self.db)
        self.assertEqual(self.original_rows(), before)
        self.execute("UPDATE events SET timestamp_utc='invalid' WHERE id=1")
        with self.assertRaises(StorageError):
            save_detection(self.db)
        self.assertEqual(self.query("PRAGMA user_version"), [(1,)])
        self.assertEqual(self.query("SELECT name FROM sqlite_master WHERE name='detection_runs'"), [])

    def test_concurrent_import_and_save_use_one_consistent_snapshot(self):
        source = self.folder / "additional.jsonl"
        source.write_text(json.dumps(failures([0])[0]), encoding="utf-8")
        with ThreadPoolExecutor(max_workers=2) as pool:
            saving = pool.submit(save_detection, self.db)
            importing = pool.submit(import_events, source, self.db)
            saved, imported = saving.result(), importing.result()
        self.assertEqual(imported["inserted"], 1)
        run = list_history(self.db, runs=True)["items"][0]
        self.assertIn((run["events_scanned"], run["max_event_id"], run["max_import_id"]), ((16, 16, 1), (17, 17, 2)))
        self.assertEqual(run["events_scanned"], saved["events_scanned"])
        self.assertEqual(database_summary(self.db)["total_events"], 17)

    def test_migration_table_conflict_is_atomic(self):
        self.execute("CREATE TABLE saved_alerts (unrelated TEXT)")
        with self.assertRaises(StorageError):
            save_detection(self.db)
        self.assertEqual(self.query("PRAGMA user_version"), [(1,)])
        self.assertEqual(self.query("SELECT name FROM sqlite_master WHERE name='detection_runs'"), [])
        self.assertEqual(self.query("SELECT * FROM saved_alerts"), [])

    def test_unsupported_schema_and_missing_database_not_modified(self):
        self.execute("PRAGMA user_version=99")
        before = self.db.read_bytes()
        with self.assertRaises(StorageError):
            save_detection(self.db)
        self.assertEqual(before, self.db.read_bytes())
        missing = self.folder / "missing.db"
        with self.assertRaises(StorageError):
            save_detection(missing)
        self.assertFalse(missing.exists())

    def test_concurrent_saves_share_one_set_of_alerts(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: save_detection(self.db), range(2)))
        self.assertEqual(sorted(x["new_alerts"] for x in results), [0, 3])
        self.assertEqual(alert_summary(self.db), {"schema_version": 2, "saved_alerts": 3, "detection_runs": 2})
        self.assertEqual(self.query("PRAGMA foreign_key_check"), [])

    def test_import_after_upgrade_keeps_deduplication_and_provenance(self):
        save_detection(self.db)
        before = self.query("SELECT * FROM events ORDER BY id")
        report = import_events(ROOT / "data/samples/day07_all_rules.jsonl", self.db)
        self.assertEqual((report["inserted"], report["duplicates"]), (0, 16))
        self.assertEqual(self.query("SELECT * FROM events ORDER BY id"), before)
        save_detection(self.db)
        latest = list_history(self.db, runs=True)["items"][0]
        self.assertEqual((latest["max_import_id"], latest["events_scanned"]), (2, 16))

    def test_late_data_preserves_old_alert_and_records_new_membership(self):
        database = self.folder / "late.db"
        source = self.folder / "late.jsonl"
        rows = failures([10, 20, 30, 40, 50])
        source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        import_events(source, database)
        save_detection(database, "R1")
        old_id = list_history(database)["items"][0]["alert_id"]
        old_alert = get_alert(database, old_id)
        source.write_text(json.dumps(dict(rows[0], event_id="late", timestamp="2026-09-28T09:00:00Z")), encoding="utf-8")
        import_events(source, database)
        result = save_detection(database, "R1")
        self.assertEqual((result["new_alerts"], result["total_saved_alerts"]), (1, 2))
        self.assertEqual(get_alert(database, old_id), old_alert)
        with closing(sqlite3.connect(database)) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM run_alerts WHERE run_id=2 AND alert_id=?", (old_id,)).fetchone()[0], 0)

    def test_identity_conflict_does_not_overwrite(self):
        save_detection(self.db)
        self.execute("UPDATE saved_alerts SET alert_json='{}' WHERE rule_id='R1'")
        with self.assertRaises(StorageError):
            save_detection(self.db)
        self.assertEqual(alert_summary(self.db)["detection_runs"], 1)
        self.assertEqual(self.query("SELECT alert_json FROM saved_alerts WHERE rule_id='R1'"), [("{}",)])

    def test_history_paging_and_input_bounds(self):
        save_detection(self.db)
        page = list_history(self.db, limit=1)
        next_page = list_history(self.db, limit=1, offset=1)
        self.assertEqual(page["total"], 3)
        self.assertNotEqual(page["items"], next_page["items"])
        for kwargs in ({"limit": 201}, {"limit": True}, {"offset": -1}):
            with self.assertRaises(StorageError):
                list_history(self.db, **kwargs)
        with self.assertRaises(StorageError):
            get_alert(self.db, "' OR 1=1")
        with self.assertRaises(StorageError):
            save_detection(self.db, "R4")

    def test_cli_process_persistence_and_error_codes(self):
        def cli(script, *args):
            return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args,
                                   "--database", str(self.db), "--json"], capture_output=True, text=True)
        first = cli("detect.py", "--save")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(json.loads(first.stdout)["new_alerts"], 3)
        second = cli("detect.py", "--save")
        self.assertEqual(json.loads(second.stdout)["new_alerts"], 0)
        self.assertEqual(json.loads(cli("alerts.py", "summary").stdout)["saved_alerts"], 3)
        listing = json.loads(cli("alerts.py", "list").stdout)
        self.assertEqual(cli("alerts.py", "get", "--alert-id", listing["items"][0]["alert_id"]).returncode, 0)
        self.assertEqual(cli("alerts.py", "get", "--alert-id", "R1-" + "0" * 64).returncode, 1)
        self.assertEqual(cli("alerts.py", "get").returncode, 2)
        self.assertEqual(cli("alerts.py", "list", "--limit", "0").returncode, 2)
