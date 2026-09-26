from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from sentinellab.ingestion.reader import InputFileError
from sentinellab.storage.database import StorageError, database_summary, import_events

ROOT = Path(__file__).resolve().parents[2]


def event(**changes):
    value = {"event_id": "e-1", "source": "lab", "timestamp": "2026-09-26T10:00:00Z",
             "source_ip": "192.0.2.10", "username": "demo_user",
             "event_type": "login", "outcome": "failure"}
    value.update(changes)
    return value


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.input = self.folder / "events.jsonl"
        self.db = self.folder / "runtime" / "events.db"

    def write(self, *events):
        self.input.write_text("\n".join(json.dumps(item) for item in events) + "\n", encoding="utf-8")
        return self.input

    def query(self, sql):
        with closing(sqlite3.connect(self.db, isolation_level=None)) as connection:
            return connection.execute(sql).fetchall()

    def test_persists_normalized_and_original_evidence_after_reopen(self):
        value = event(timestamp="2026-09-26T15:00:00+05:00", source_ip="2001:0db8:0:0:0:0:0:1")
        result = import_events(self.write(value), self.db)
        self.assertEqual(result["inserted"], 1)
        self.assertEqual(database_summary(self.db)["total_events"], 1)
        row = self.query("SELECT timestamp_utc, source_ip, original_record, first_line_number FROM events")[0]
        self.assertEqual(row[:2], ("2026-09-26T10:00:00.000000+00:00", "2001:db8::1"))
        self.assertEqual(row[2], self.input.read_bytes().split(b"\n")[0].decode("utf-8"))
        self.assertEqual(row[3], 1)

    def test_reimport_is_duplicate_and_preserves_first_provenance(self):
        self.write(event())
        import_events(self.input, self.db)
        original = self.query("SELECT * FROM events")
        second = import_events(self.input, self.db)
        self.assertEqual((second["inserted"], second["duplicates"], second["total_events"]), (0, 1, 1))
        self.assertEqual(self.query("SELECT * FROM events"), original)
        self.assertEqual(database_summary(self.db)["total_imports"], 2)

    def test_same_id_different_values_is_conflict_and_original_is_kept(self):
        import_events(self.write(event()), self.db)
        report = import_events(self.write(event(outcome="success")), self.db)
        self.assertEqual((report["inserted"], report["conflicts"]), (0, 1))
        self.assertEqual(self.query("SELECT outcome FROM events"), [("failure",)])
        self.assertEqual(report["errors"][0]["line"], 1)

    def test_canonical_equivalence_ignores_offset_ip_spelling_and_key_order(self):
        first = event(source_ip="2001:0db8:0:0:0:0:0:1")
        import_events(self.write(first), self.db)
        second = event(timestamp="2026-09-26T15:00:00.000000+05:00", source_ip="2001:db8::1")
        self.input.write_text(json.dumps(dict(reversed(list(second.items()))), separators=(",", ":")), encoding="utf-8")
        report = import_events(self.input, self.db)
        self.assertEqual(report["duplicates"], 1)
        self.assertEqual(report["conflicts"], 0)

    def test_same_event_id_from_another_source_is_new(self):
        report = import_events(self.write(event(), event(source="second-lab")), self.db)
        self.assertEqual(report["inserted"], 2)

    def test_same_batch_first_valid_identity_wins(self):
        report = import_events(self.write(event(), event(), event(outcome="success")), self.db)
        self.assertEqual((report["validated"], report["inserted"], report["duplicates"], report["conflicts"]),
                         (3, 1, 1, 1))
        self.assertEqual(self.query("SELECT outcome FROM events"), [("failure",)])

    def test_case_and_spaces_are_significant(self):
        import_events(self.write(event()), self.db)
        for username in ["Demo_User", "demo_user "]:
            with self.subTest(username=username):
                self.assertEqual(import_events(self.write(event(username=username)), self.db)["conflicts"], 1)

    def test_mixed_invalid_conflict_and_new_rows_have_separate_counts(self):
        import_events(self.write(event()), self.db)
        self.input.write_text(json.dumps(event(event_id="new")) + "\n\nwrong\n" +
                              json.dumps(event(outcome="success")) + "\n", encoding="utf-8")
        report = import_events(self.input, self.db)
        self.assertEqual((report["validated"], report["inserted"], report["rejected"],
                          report["blank_lines"], report["conflicts"]), (2, 1, 1, 1, 1))
        self.assertEqual([issue["line"] for issue in report["errors"]], [3, 4])
        saved = self.query("SELECT errors_json FROM imports ORDER BY id DESC LIMIT 1")[0][0]
        self.assertEqual(json.loads(saved), report["errors"])

    def test_sql_looking_username_is_stored_as_data(self):
        username = "Robert'); DROP TABLE events;--"
        report = import_events(self.write(event(username=username)), self.db)
        self.assertEqual(report["inserted"], 1)
        self.assertEqual(self.query("SELECT username FROM events"), [(username,)])

    def test_database_failure_rolls_back_rows_and_import_summary(self):
        import_events(self.write(event()), self.db)
        with closing(sqlite3.connect(self.db, isolation_level=None)) as connection:
            connection.execute("""CREATE TRIGGER reject_demo BEFORE INSERT ON events
                WHEN NEW.event_id = 'fail-write'
                BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END""")
        before = database_summary(self.db)
        with self.assertRaises(StorageError):
            import_events(self.write(event(event_id="new-row"), event(event_id="fail-write")), self.db)
        self.assertEqual(database_summary(self.db), before)
        self.assertEqual(self.query("SELECT event_id FROM events"), [("e-1",)])

    def test_concurrent_reimports_do_not_duplicate_events(self):
        self.write(event())
        # Initialize once, then concurrent import transactions must serialize.
        import_events(self.input, self.db)
        with ThreadPoolExecutor(max_workers=2) as pool:
            reports = list(pool.map(lambda _: import_events(self.input, self.db), range(2)))
        self.assertEqual(sum(report["duplicates"] for report in reports), 2)
        self.assertEqual(database_summary(self.db), {"schema_version": 1, "total_events": 1, "total_imports": 3})

    def test_missing_input_does_not_create_database(self):
        with self.assertRaises(InputFileError):
            import_events(self.input, self.db)
        self.assertFalse(self.db.exists())

    def test_summary_does_not_create_missing_database(self):
        with self.assertRaises(StorageError):
            database_summary(self.db)
        self.assertFalse(self.db.exists())

    def test_input_cannot_be_database(self):
        self.write(event())
        original = self.input.read_bytes()
        with self.assertRaises(StorageError):
            import_events(self.input, self.input)
        self.assertEqual(self.input.read_bytes(), original)

    def test_unrelated_database_is_not_adopted_or_changed(self):
        self.db.parent.mkdir()
        with closing(sqlite3.connect(self.db, isolation_level=None)) as connection:
            connection.execute("CREATE TABLE unrelated (value TEXT)")
            connection.execute("INSERT INTO unrelated VALUES ('keep me')")
        with self.assertRaises(StorageError):
            import_events(self.write(event()), self.db)
        self.assertEqual(self.query("SELECT * FROM unrelated"), [("keep me",)])
        self.assertEqual(self.query("PRAGMA user_version"), [(0,)])

    def test_unsupported_schema_is_not_migrated(self):
        import_events(self.write(event()), self.db)
        with closing(sqlite3.connect(self.db, isolation_level=None)) as connection:
            connection.execute("PRAGMA user_version = 999")
        with self.assertRaises(StorageError):
            import_events(self.input, self.db)
        with self.assertRaises(StorageError):
            database_summary(self.db)
        self.assertEqual(self.query("PRAGMA user_version"), [(999,)])

    def test_empty_file_creates_zero_event_import(self):
        self.input.write_bytes(b"")
        report = import_events(self.input, self.db)
        self.assertEqual((report["validated"], report["inserted"], report["total_events"]), (0, 0, 0))
        self.assertEqual(database_summary(self.db)["total_imports"], 1)

    def test_cli_across_processes_persists_and_deduplicates(self):
        self.write(event())
        command = [sys.executable, str(ROOT / "scripts/database.py")]
        def run(*args):
            return subprocess.run(command + list(args) + ["--database", str(self.db), "--json"],
                                  cwd=self.folder, capture_output=True, text=True, timeout=10)
        first = run("import", str(self.input))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(json.loads(first.stdout)["inserted"], 1)
        second = run("import", str(self.input))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(json.loads(second.stdout)["duplicates"], 1)
        summary = run("summary")
        self.assertEqual(summary.returncode, 0)
        self.assertEqual(json.loads(summary.stdout)["total_events"], 1)

    def test_cli_conflict_exit_and_safe_database_error(self):
        import_events(self.write(event()), self.db)
        self.write(event(outcome="success"))
        result = subprocess.run([sys.executable, str(ROOT / "scripts/database.py"), "import",
                                 str(self.input), "--database", str(self.db), "--json"],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["conflicts"], 1)
        bad = self.folder / "not-a-database.db"
        bad.write_text("SECRET-synthetic-value", encoding="utf-8")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/database.py"), "summary",
                                 "--database", str(bad), "--json"], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("SECRET", result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
