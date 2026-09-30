"""Day 9 browser API contract with real HTTP, SQLite, and bounded evidence."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import patch

from sentinellab.storage.alerts import alert_summary, get_alert
from sentinellab.storage.database import StorageError, import_events, database_summary
from tests.integration import test_web as web_fixture
from tests.integration.test_detection import failures, ROOT


class WebAlertTests(unittest.TestCase):
    setUp = web_fixture.WebTests.setUp
    cleanup = web_fixture.WebTests.cleanup
    request = web_fixture.WebTests.request
    upload = web_fixture.WebTests.upload
    data = web_fixture.WebTests.data

    def sample(self):
        import_events(ROOT / "data/samples/day07_all_rules.jsonl", self.db)

    def detect(self, body=b"rule=all", **changes):
        headers = {"Origin": self.server.origin, "X-SentinelLab-Token": self.server.token,
                   "Content-Type": "application/x-www-form-urlencoded"}
        headers.update(changes)
        return self.request("POST", "/api/detect", body, headers)

    def get_json(self, path):
        code, _, body = self.request("GET", path)
        self.assertEqual(code, 200, body)
        return json.loads(body)

    def test_empty_history_reads_do_not_migrate(self):
        before = self.db.read_bytes()
        self.assertEqual(self.get_json("/api/alerts/summary")["saved_alerts"], 0)
        for path in ("/api/alerts", "/api/runs"):
            self.assertEqual(self.get_json(path)["items"], [])
        self.assertEqual(before, self.db.read_bytes())
        self.assertEqual(database_summary(self.db)["schema_version"], 1)

    def test_save_twice_and_read_linked_originals(self):
        self.sample()
        self.assertEqual(self.detect()[0], 200)
        code, _, body = self.detect()
        self.assertEqual(code, 200)
        self.assertEqual((json.loads(body)["new_alerts"], json.loads(body)["existing_alerts"]), (0, 3))
        self.assertEqual(self.get_json("/api/alerts/summary"), {"schema_version": 2, "saved_alerts": 3, "detection_runs": 2})
        alerts = self.get_json("/api/alerts")["items"]
        for item in alerts:
            detail = self.get_json("/api/alerts/" + item["alert_id"])
            self.assertNotIn("evidence", detail["alert"])
            self.assertNotIn("usernames", detail["alert"])
            for ref in detail["evidence"]["items"]:
                original = self.get_json(f"/api/events/{ref['internal_id']}")["event"]
                self.assertEqual(original["event_id"], ref["event_id"])
                self.assertIn("original_record", original)
        latest = self.get_json("/api/runs")["items"][0]
        self.assertEqual((latest["new_count"], latest["existing_count"]), (0, 3))
        self.assertEqual([r["rule_id"] for r in latest["configurations"]], ["R1", "R2", "R3"])

    def test_selected_rules_and_run_membership(self):
        self.sample()
        self.assertEqual(self.detect(b"rule=R1")[0], 200)
        self.assertEqual(self.detect(b"rule=all")[0], 200)
        self.assertEqual(self.get_json("/api/alerts?run_id=1")["total"], 1)
        self.assertEqual(self.get_json("/api/alerts?run_id=2")["total"], 3)
        self.assertEqual(self.get_json("/api/alerts?run_id=999")["total"], 0)
        self.assertEqual(self.get_json("/api/runs")["items"][0]["existing_count"], 1)

    def test_successful_zero_match_run(self):
        code, _, body = self.detect(b"rule=R2")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["alert_count"], 0)
        run = self.get_json("/api/runs")["items"][0]
        self.assertEqual(run["events_scanned"], 0)
        self.assertEqual(run["configurations"][0]["rule_id"], "R2")

    def test_import_does_not_execute_detection(self):
        self.upload((ROOT / "data/samples/day07_all_rules.jsonl").read_bytes())
        self.assertEqual(alert_summary(self.db)["detection_runs"], 0)
        self.assertEqual(database_summary(self.db)["schema_version"], 1)

    def test_pagination_for_alerts_runs_and_evidence(self):
        self.sample()
        self.detect(); self.detect()
        for path in ("/api/alerts", "/api/runs"):
            first = self.get_json(path + "?limit=1")
            second = self.get_json(path + "?limit=1&offset=1")
            self.assertEqual(first["next_offset"], 1)
            self.assertNotEqual(first["items"], second["items"])
        alert_id = self.get_json("/api/alerts")["items"][0]["alert_id"]
        first = self.get_json(f"/api/alerts/{alert_id}?limit=1")
        second = self.get_json(f"/api/alerts/{alert_id}?limit=1&offset=1")
        self.assertEqual(first["evidence"]["next_offset"], 1)
        self.assertNotEqual(first["evidence"]["items"], second["evidence"]["items"])
        self.assertIsNone(self.get_json(f"/api/alerts/{alert_id}?offset=1000")["evidence"]["next_offset"])

    def test_history_and_detail_reads_leave_saved_snapshots_unchanged(self):
        self.sample(); self.detect()
        before = self.db.read_bytes()
        alert_id = self.get_json("/api/alerts")["items"][0]["alert_id"]
        original = get_alert(self.db, alert_id)
        self.get_json("/api/runs"); self.get_json("/api/alerts/summary")
        self.get_json(f"/api/alerts/{alert_id}?limit=1")
        self.assertEqual(get_alert(self.db, alert_id), original)
        self.assertEqual(before, self.db.read_bytes())

    def test_invalid_and_repeated_queries_and_ids(self):
        for path in ("/api/alerts?limit=201", "/api/runs?offset=-1", "/api/runs?run_id=1",
                     "/api/alerts?run_id=0", "/api/alerts?run_id=9223372036854775808",
                     "/api/alerts?limit=1&limit=2", "/api/alerts?extra=1", "/api/runs?limit=x",
                     "/api/alerts/summary?extra=1", "/api/alerts/bad", "/api/alerts?limit"):
            with self.subTest(path=path):
                self.assertEqual(self.request("GET", path)[0], 400)
        self.assertEqual(self.request("GET", "/api/alerts/R1-" + "0" * 64)[0], 404)

    def test_save_requires_all_request_protections(self):
        before = self.db.read_bytes()
        for changes in ({"Origin": "https://evil.invalid"}, {"Origin": "null"},
                        {"X-SentinelLab-Token": "bad"}, {"Host": "evil.invalid"},
                        {"Sec-Fetch-Site": "cross-site"}):
            self.assertEqual(self.detect(**changes)[0], 403)
        self.assertEqual(self.request("POST", "/api/detect", b"rule=all")[0], 403)
        self.assertEqual(self.request("GET", "/api/detect")[0], 404)
        self.assertEqual(self.db.read_bytes(), before)

    def test_bad_detection_bodies_never_write(self):
        before = self.db.read_bytes()
        for body in (b"", b"rule=R4", b"rule=R1&rule=R2", b"rule=all&extra=x", b"rule", b"rule=", b"\xff"):
            self.assertEqual(self.detect(body)[0], 400, body)
        self.assertEqual(self.detect(b"x" * 129)[0], 413)
        self.assertEqual(self.detect(**{"Content-Type": "application/json"})[0], 415)
        self.assertEqual(self.detect(**{"Transfer-Encoding": "chunked"})[0], 411)
        self.assertEqual(before, self.db.read_bytes())

    def test_failed_save_does_not_leave_partial_migration(self):
        self.sample()
        with patch("sentinellab.storage.alerts.evaluate_snapshot", side_effect=StorageError("Detection evidence limit exceeded.")):
            code, _, body = self.detect()
        self.assertEqual(code, 400)
        self.assertIn(b"evidence limit", body)
        self.assertEqual(database_summary(self.db)["schema_version"], 1)
        self.assertEqual(alert_summary(self.db)["detection_runs"], 0)

    def test_large_evidence_response_is_paged_and_text_is_data(self):
        username = '<img src=x onerror="alert(1)">'
        self.upload(self.data(*failures([0] * 55, username=username)))
        self.detect(b"rule=R1")
        alert_id = self.get_json("/api/alerts")["items"][0]["alert_id"]
        result = self.get_json("/api/alerts/" + alert_id)
        self.assertEqual(result["alert"]["group"]["username"], username)
        self.assertEqual(result["evidence"]["total"], 55)
        self.assertEqual(len(result["evidence"]["items"]), 25)
        self.assertEqual(result["evidence"]["next_offset"], 25)

    def test_new_assets_are_allowlisted_and_protected_reads_stay_protected(self):
        for asset in ("/static/alerts.js", "/static/alerts.css"):
            self.assertEqual(self.request("GET", asset)[0], 200)
        for path in ("/api/alerts", "/api/runs", "/api/alerts/summary"):
            self.assertEqual(self.request("GET", path, headers={"Origin": "https://evil.invalid"})[0], 403)
        self.assertEqual(self.request("GET", "/static/../../storage/alerts.py")[0], 404)
