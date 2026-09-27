"""Exercise search against real temporary databases and separate CLI processes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sentinellab.storage.database import StorageError, import_events
from sentinellab.storage.search import get_event, search_events
from tests.integration.test_storage import event

ROOT = Path(__file__).resolve().parents[2]


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.db = self.folder / "events.db"
        self.source = self.folder / "input.jsonl"
        self.records = [event(event_id="late", timestamp="2026-09-26T10:05:00Z", outcome="success"),
                        event(event_id="first"), event(event_id="tie", username="Demo_user"),
                        event(event_id="v6", timestamp="2026-09-26T10:00:00.000001Z",
                              source_ip="2001:db8::1", username=" demo_user ")]
        self.source.write_bytes(("\n".join(json.dumps(x) for x in self.records) + "\n").encode())
        import_events(self.source, self.db)

    def test_default_chronological_order_and_no_original_in_list(self):
        result = search_events(self.db)
        self.assertEqual(result["total_matches"], 4)
        self.assertEqual([x["event_id"] for x in result["events"]], ["first", "tie", "v6", "late"])
        self.assertNotIn("original_record", result["events"][0])

    def test_combined_filters(self):
        result = search_events(self.db, username="demo_user", source_ip="192.0.2.10",
                               outcome="failure", start="2026-09-26T15:00:00+05:00",
                               end="2026-09-26T10:05:00Z")
        self.assertEqual([x["event_id"] for x in result["events"]], ["first"])

    def test_start_inclusive_end_exclusive_at_microseconds(self):
        result = search_events(self.db, start="2026-09-26T10:00:00Z",
                               end="2026-09-26T10:00:00.000001Z")
        self.assertEqual(result["returned"], 2)
        self.assertEqual(search_events(self.db, start="2026-09-26T10:05:00Z")["returned"], 1)

    def test_equivalent_ipv6_and_exact_username(self):
        self.assertEqual(search_events(self.db, source_ip="2001:0db8:0:0:0:0:0:1")["returned"], 1)
        self.assertEqual(search_events(self.db, username="demo_user")["returned"], 2)
        self.assertEqual(search_events(self.db, username=" demo_user ")["returned"], 1)
        self.assertEqual(search_events(self.db, username="DEMO_USER")["returned"], 0)

    def test_pages_handle_timestamp_ties_without_overlap(self):
        first = search_events(self.db, limit=2)
        second = search_events(self.db, limit=2, offset=first["next_offset"])
        self.assertEqual([x["id"] for x in first["events"] + second["events"]], [2, 3, 4, 1])
        self.assertIsNone(second["next_offset"])
        self.assertEqual(search_events(self.db, offset=10)["events"], [])

    def test_invalid_filters_are_safe(self):
        for kwargs in ({"limit": 0}, {"limit": 201}, {"limit": True}, {"offset": -1},
                       {"offset": 1_000_001}, {"offset": 1.5}, {"username": " "},
                       {"username": "x" * 129}, {"username": "bad\nname"},
                       {"source_ip": "garbage"}, {"source_ip": "fe80::1%eth0"},
                       {"outcome": "banana"}, {"start": "2026-09-26T10:00:00"},
                       {"end": "2026-02-30T00:00:00Z"},
                       {"start": "2026-09-26T10:00:00Z", "end": "2026-09-26T10:00:00Z"},
                       {"start": "2026-09-27T10:00:00Z", "end": "2026-09-26T10:00:00Z"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(StorageError):
                search_events(self.db, **kwargs)

    def test_sql_text_is_only_a_value(self):
        self.assertEqual(search_events(self.db, username="' OR 1=1 --")["returned"], 0)
        self.assertEqual(search_events(self.db)["total_matches"], 4)

    def test_lookup_retains_original_and_provenance(self):
        found = get_event(self.db, 2)
        self.assertEqual(found["event_id"], "first")
        self.assertEqual(found["original_record"], json.dumps(self.records[1]))
        self.assertEqual((found["first_import_id"], found["first_line_number"]), (1, 2))
        self.assertIsNone(get_event(self.db, 999))
        for invalid in (0, -1, True, "1", 2**63):
            with self.subTest(invalid=invalid), self.assertRaises(StorageError):
                get_event(self.db, invalid)

    def test_read_operations_leave_database_bytes_unchanged(self):
        before = self.db.read_bytes()
        search_events(self.db)
        get_event(self.db, 1)
        self.assertEqual(self.db.read_bytes(), before)

    def test_missing_or_corrupt_database_is_not_created_or_modified(self):
        missing = self.folder / "missing.db"
        for action in (lambda: search_events(missing), lambda: get_event(missing, 1)):
            with self.assertRaises(StorageError):
                action()
        self.assertFalse(missing.exists())
        missing.write_bytes(b"not sqlite")
        with self.assertRaises(StorageError):
            search_events(missing)
        self.assertEqual(missing.read_bytes(), b"not sqlite")

    def test_cli_from_another_directory_and_exit_codes(self):
        def run(*args):
            return subprocess.run([sys.executable, str(ROOT / "scripts/database.py"), *args,
                                   "--database", str(self.db), "--json"], cwd=self.folder,
                                  capture_output=True, text=True)
        result = run("search", "--outcome", "failure", "--limit", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["total_matches"], 3)
        self.assertEqual(run("search", "--username", "absent").returncode, 0)
        self.assertEqual(run("get", "999").returncode, 1)
        self.assertEqual(run("get", "0").returncode, 2)
        self.assertEqual(run("search", "--limit", "201").returncode, 2)
        self.assertEqual(json.loads(run("get", "1").stdout)["event"]["event_id"], "late")
