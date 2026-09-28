"""R1 behavior against real ingestion/storage, including limits and event-time edges."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from sentinellab.detection.r1 import detect_r1
from sentinellab.storage.database import StorageError, import_events, initialize_database
from sentinellab.storage.search import get_event
from tests.integration.test_storage import event

ROOT = Path(__file__).resolve().parents[2]
BASE = datetime(2026, 9, 28, 9, tzinfo=timezone.utc)


def failures(seconds, **changes):
    return [event(event_id=f"r1-{i}", timestamp=(BASE + timedelta(seconds=s)).isoformat(), **changes)
            for i, s in enumerate(seconds)]


class DetectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.db = self.folder / "events.db"
        self.input = self.folder / "events.jsonl"

    def save(self, records, database=None):
        self.input.write_text("\n".join(json.dumps(row) for row in records) + "\n", encoding="utf-8")
        return import_events(self.input, database or self.db)

    def test_four_failures_and_success_are_below_threshold(self):
        self.save(failures([0, 20, 40, 60]) + [event(event_id="ok", outcome="success")])
        self.assertEqual(detect_r1(self.db)["alert_count"], 0)

    def test_exact_five_minute_boundary_and_evidence(self):
        self.save(failures([0, 60, 120, 180, 300]))
        report = detect_r1(self.db)
        self.assertEqual(report["alert_count"], 1)
        alert = report["alerts"][0]
        self.assertEqual(alert["parameters"], {"threshold": 5, "window_seconds": 300})
        self.assertEqual(alert["rule_version"], "1.0.0")
        self.assertEqual(alert["failure_count"], 5)
        for ref in alert["evidence"]:
            stored = get_event(self.db, ref["internal_id"])
            self.assertEqual(stored["event_id"], ref["event_id"])
            self.assertEqual(json.loads(stored["original_record"])["outcome"], "failure")

    def test_one_microsecond_outside_boundary_does_not_trigger(self):
        self.save(failures([0, 60, 120, 180, 300.000001]))
        self.assertEqual(detect_r1(self.db)["alert_count"], 0)

    def test_ties_are_batched_and_all_contribute(self):
        self.save(failures([0] * 7))
        report = detect_r1(self.db)
        self.assertEqual(report["alert_count"], 1)
        self.assertEqual(report["alerts"][0]["failure_count"], 7)

    def test_continuous_burst_is_one_frozen_alert(self):
        self.save(failures(range(0, 601, 60)))
        alerts = detect_r1(self.db)["alerts"]
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["failure_count"], 5)
        self.assertEqual(alerts[0]["triggered_at"], "2026-09-28T09:04:00.000000+00:00")

    def test_group_rearms_after_window_drops_below_threshold(self):
        self.save(failures([0, 1, 2, 3, 4, 400, 401, 402, 403, 404]))
        alerts = detect_r1(self.db)["alerts"]
        self.assertEqual(len(alerts), 2)
        self.assertNotEqual(alerts[0]["alert_id"], alerts[1]["alert_id"])

    def test_success_does_not_reset_failures(self):
        self.save(failures([0, 60, 120, 180, 240]) + [event(
            event_id="success", outcome="success", timestamp="2026-09-28T09:02:30Z")])
        self.assertEqual(detect_r1(self.db)["alerts"][0]["failure_count"], 5)

    def test_accounts_ips_case_and_spaces_do_not_mix(self):
        rows = []
        for number, changes in enumerate(({}, {"username": "Demo_user"}, {"username": " demo_user "},
                                          {"source_ip": "192.0.2.11"})):
            for row in failures([0, 1, 2, 3], **changes):
                row["event_id"] = f"group-{number}-" + row["event_id"]
                rows.append(row)
        self.save(rows)
        self.assertEqual(detect_r1(self.db)["alert_count"], 0)

    def test_distinct_source_identities_contribute_to_same_group(self):
        self.save([event(source=f"lab-{i}", timestamp=BASE.isoformat()) for i in range(5)])
        self.assertEqual(detect_r1(self.db)["alert_count"], 1)

    def test_timezone_and_ipv6_normalization(self):
        rows = failures([0, 60, 120, 180, 240], source_ip="2001:db8::1")
        rows[0]["timestamp"] = "2026-09-28T14:00:00+05:00"
        rows[0]["source_ip"] = "2001:0db8:0:0:0:0:0:1"
        self.save(rows)
        self.assertEqual(detect_r1(self.db)["alert_count"], 1)

    def test_reimports_conflicts_and_reruns_do_not_inflate_results(self):
        rows = failures([0, 1, 2, 3, 4])
        self.save(rows)
        first = detect_r1(self.db)
        self.save(rows)
        self.assertEqual(detect_r1(self.db), first)
        conflict = dict(rows[0], outcome="success")
        self.assertEqual(self.save([conflict])["conflicts"], 1)
        self.assertEqual(detect_r1(self.db), first)

    def test_import_order_changes_row_ids_but_not_alert_identity(self):
        rows = failures([0, 60, 120, 180, 300, 300])
        self.save(rows)
        other = self.folder / "shuffled.db"
        random.Random(6).shuffle(rows)
        self.save(rows, other)
        a, b = detect_r1(self.db)["alerts"][0], detect_r1(other)["alerts"][0]
        self.assertEqual(a["alert_id"], b["alert_id"])
        self.assertEqual([(x["source"], x["event_id"]) for x in a["evidence"]],
                         [(x["source"], x["event_id"]) for x in b["evidence"]])

    def test_missing_empty_and_read_only_database_behavior(self):
        with self.assertRaises(StorageError):
            detect_r1(self.db)
        self.assertFalse(self.db.exists())
        initialize_database(self.db)
        self.assertEqual(detect_r1(self.db)["events_scanned"], 0)
        self.save(failures([0, 1, 2, 3, 4]))
        before = self.db.read_bytes()
        detect_r1(self.db)
        self.assertEqual(self.db.read_bytes(), before)

    def test_event_cap_fails_whole_run_including_successes(self):
        self.save(failures([0, 1, 2, 3, 4]))
        with patch("sentinellab.detection.r1.MAX_DETECTION_EVENTS", 5):
            self.assertEqual(detect_r1(self.db)["alert_count"], 1)
            self.save([event(event_id="extra", outcome="success")])
            with self.assertRaisesRegex(StorageError, "no partial results"):
                detect_r1(self.db)

    def test_minimum_supported_date_does_not_overflow(self):
        self.save([event(event_id=str(i), timestamp="0001-01-01T00:00:00Z") for i in range(5)])
        self.assertEqual(detect_r1(self.db)["alert_count"], 1)

    def test_cli_separate_process_json_and_exit_codes(self):
        self.save(failures([0, 1, 2, 3, 4]))
        command = [sys.executable, str(ROOT / "scripts/detect.py"), "--database", str(self.db), "--json"]
        result = subprocess.run(command, cwd=self.folder, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["alert_count"], 1)
        self.assertEqual(result.stderr, "")
        command[-2] = str(self.folder / "missing.db")
        result = subprocess.run(command, cwd=self.folder, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("error", json.loads(result.stdout))
