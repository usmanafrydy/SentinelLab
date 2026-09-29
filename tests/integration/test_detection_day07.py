"""R2/R3 boundaries, grouping, evidence, repeatability, and combined CLI coverage."""
from datetime import timedelta
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from sentinellab.detection.common import EvidenceBudget
from sentinellab.detection.engine import detect
from sentinellab.detection.r1 import detect_r1
from sentinellab.storage.database import StorageError, import_events, initialize_database
from sentinellab.storage.search import get_event
from tests.integration.test_detection import BASE, ROOT, failures
from tests.integration.test_storage import event


def spray(count=10, times=None):
    times = list(range(count)) if times is None else times
    return [event(event_id=f'spray-{i}', username=f'user-{i}',
                  timestamp=(BASE + timedelta(seconds=times[i])).isoformat()) for i in range(count)]


def success(seconds=5, **changes):
    values = {"event_id": "success", "outcome": "success",
              "timestamp": (BASE + timedelta(seconds=seconds)).isoformat()}
    values.update(changes)
    return event(**values)


class DaySevenTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.db = self.folder / "events.db"
        self.input = self.folder / "input.jsonl"

    def save(self, rows, database=None):
        self.input.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
        return import_events(self.input, database or self.db)

    def test_r2_nine_accounts_and_many_repeats_do_not_trigger(self):
        rows = spray(9)
        rows += [dict(rows[0], event_id=f"repeat-{i}") for i in range(20)]
        self.save(rows)
        self.assertEqual(detect(self.db, "R2")["alert_count"], 0)

    def test_r2_includes_exact_ten_minute_boundary(self):
        self.save(spray(times=[0, 60, 120, 180, 240, 300, 360, 420, 480, 600]))
        alert = detect(self.db, "R2")["alerts"][0]
        self.assertEqual(alert["distinct_account_count"], 10)
        self.assertEqual(len(alert["evidence"]), 10)
        self.assertEqual(alert["parameters"], {"threshold": 10, "window_seconds": 600})

    def test_r2_excludes_one_microsecond_outside_boundary(self):
        self.save(spray(times=[0, 60, 120, 180, 240, 300, 360, 420, 480, 600.000001]))
        self.assertEqual(detect(self.db, "R2")["alert_count"], 0)

    def test_r2_same_time_batch_retains_repeated_account_evidence(self):
        rows = spray(times=[0] * 10)
        rows += [dict(rows[0], event_id="same-user-extra")]
        self.save(rows)
        alert = detect(self.db, "R2")["alerts"][0]
        self.assertEqual((alert["distinct_account_count"], alert["failure_count"]), (10, 11))
        self.assertEqual(len(alert["evidence"]), 11)

    def test_r2_different_ips_and_successes_do_not_mix(self):
        rows = spray()
        rows[-1]["source_ip"] = "192.0.2.99"
        rows.append(success(username="user-10"))
        self.save(rows)
        self.assertEqual(detect(self.db, "R2")["alert_count"], 0)

    def test_r2_case_and_spaces_count_as_distinct_usernames(self):
        rows = spray()
        rows[0]["username"], rows[1]["username"], rows[2]["username"] = "demo", "Demo", " demo "
        self.save(rows)
        self.assertEqual(detect(self.db, "R2")["alert_count"], 1)

    def test_r2_ongoing_burst_suppressed_and_later_burst_rearms(self):
        rows = spray(times=[0] * 10) + [event(event_id="extra", username="extra", timestamp=(BASE + timedelta(seconds=1)).isoformat())]
        rows += [dict(row, event_id="later-" + row["event_id"], timestamp=(BASE + timedelta(seconds=700)).isoformat()) for row in spray()]
        self.save(rows)
        self.assertEqual(detect(self.db, "R2")["alert_count"], 2)

    def test_r2_expiring_one_repeat_keeps_account_active(self):
        rows = spray(9, times=[100] * 9)
        rows += [dict(rows[0], event_id="older", timestamp=BASE.isoformat()),
                 event(event_id="tenth", username="tenth", timestamp=(BASE + timedelta(seconds=601)).isoformat())]
        self.save(rows)
        self.assertEqual(detect(self.db, "R2")["alerts"][0]["distinct_account_count"], 10)

    def test_r3_five_failures_then_success_links_both_roles(self):
        self.save(failures([0, 1, 2, 3, 4]) + [success()])
        alert = detect(self.db, "R3")["alerts"][0]
        self.assertEqual(alert["failure_count"], 5)
        self.assertEqual([ref["role"] for ref in alert["evidence"]], ["preceding_failure"] * 5 + ["triggering_success"])
        for ref in alert["evidence"]:
            saved = get_event(self.db, ref["internal_id"])
            self.assertEqual(saved["event_id"], ref["event_id"])
            self.assertEqual(saved["outcome"], "success" if ref["role"] == "triggering_success" else "failure")

    def test_r3_four_failures_no_success_or_earlier_success_do_not_trigger(self):
        for index, rows in enumerate((failures([0, 1, 2, 3]) + [success()],
                                      failures([0, 1, 2, 3, 4]),
                                      failures([1, 2, 3, 4, 5]) + [success(0)])):
            database = self.folder / f"negative-{index}.db"
            self.save(rows, database)
            self.assertEqual(detect(database, "R3")["alert_count"], 0)

    def test_r3_start_inclusive_and_end_exclusive(self):
        self.save(failures([0, 60, 120, 180, 240]) + [success(300)])
        self.assertEqual(detect(self.db, "R3")["alert_count"], 1)
        outside = self.folder / "outside.db"
        self.save(failures([0, 60, 120, 180, 240]) + [success(300.000001)], outside)
        self.assertEqual(detect(outside, "R3")["alert_count"], 0)
        tied = self.folder / "tied.db"
        self.save(failures([0, 60, 120, 180, 300]) + [success(300)], tied)
        self.assertEqual(detect(tied, "R3")["alert_count"], 0)

    def test_r3_excludes_equal_time_failures_even_with_enough_earlier_ones(self):
        self.save(failures([0, 1, 2, 3, 4, 5, 5]) + [success(5)])
        self.assertEqual(detect(self.db, "R3")["alerts"][0]["failure_count"], 5)

    def test_r3_username_and_ip_must_both_match(self):
        self.save(failures([0, 1, 2, 3, 4]) + [success(username="Demo_user"),
                  success(event_id="other-ip", source_ip="192.0.2.11")])
        self.assertEqual(detect(self.db, "R3")["alert_count"], 0)

    def test_r3_each_success_has_own_identity_and_no_reset(self):
        self.save(failures([0, 1, 2, 3, 4]) + [success(), success(event_id="success-2")])
        alerts = detect(self.db, "R3")["alerts"]
        self.assertEqual(len(alerts), 2)
        self.assertEqual(len({a["alert_id"] for a in alerts}), 2)

    def test_all_rules_snapshot_stable_reruns_reimports_and_shuffled_order(self):
        rows = spray() + failures([0, 1, 2, 3, 4]) + [success()]
        self.save(rows)
        before = self.db.read_bytes()
        report = detect(self.db)
        self.assertEqual(report["rules_evaluated"], ["R1", "R2", "R3"])
        self.assertEqual({a["rule_id"] for a in report["alerts"]}, {"R1", "R2", "R3"})
        self.assertEqual(report, detect(self.db))
        self.assertEqual(self.db.read_bytes(), before)
        self.save(rows)
        self.assertEqual(report, detect(self.db))
        self.save([dict(rows[0], outcome="success")])
        self.assertEqual(report, detect(self.db))
        random.Random(7).shuffle(rows)
        other = self.folder / "shuffled.db"
        self.save(rows, other)
        self.assertEqual([a["alert_id"] for a in report["alerts"]], [a["alert_id"] for a in detect(other)["alerts"]])
        self.assertEqual([a for a in report["alerts"] if a["rule_id"] == "R1"], detect_r1(self.db)["alerts"])

    def test_r1_saved_day6_example_is_unchanged(self):
        import_events(ROOT / "data/samples/day06_repeated_failures.jsonl", self.db)
        expected = json.loads((ROOT / "reports/examples/day06_r1_preview.json").read_text())
        self.assertEqual(detect(self.db, "R1"), expected)

    def test_combined_run_reads_snapshot_once(self):
        initialize_database(self.db)
        from sentinellab.detection.common import load_snapshot
        with patch("sentinellab.detection.engine.load_snapshot", wraps=load_snapshot) as loader:
            self.assertEqual(detect(self.db)["alerts"], [])
            loader.assert_called_once_with(self.db)

    def test_evidence_budget_fails_instead_of_returning_partial_results(self):
        self.save(failures([0, 1, 2, 3, 4]) + [success(), success(6, event_id="second")])
        with patch("sentinellab.detection.engine.EvidenceBudget", return_value=EvidenceBudget(11)):
            with self.assertRaisesRegex(StorageError, "no partial results"):
                detect(self.db, "R3")

    def test_cli_default_all_and_rule_selection(self):
        self.save(spray() + failures([0, 1, 2, 3, 4]) + [success()])
        command = [sys.executable, str(ROOT / "scripts/detect.py"), "--database", str(self.db), "--json"]
        for rule in (None, "R1", "R2", "R3"):
            result = subprocess.run(command + (["--rule", rule] if rule else []), cwd=self.folder, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["rules_evaluated"], [rule] if rule else ["R1", "R2", "R3"])
        self.assertEqual(subprocess.run(command + ["--rule", "R4"], capture_output=True).returncode, 2)

    def test_missing_database_and_invalid_rule_do_not_create_files(self):
        for rule in ("all", "R2", "R3", "R4"):
            with self.assertRaises(StorageError):
                detect(self.db, rule)
        self.assertFalse(self.db.exists())
