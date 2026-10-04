"""Real HTTP requests against an isolated loopback server and temporary SQLite DB."""
from http.client import HTTPConnection
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import socket
import tempfile
from threading import Thread
import unittest
from urllib.parse import urlencode

from sentinellab.ingestion.reader import MAX_FILE_BYTES
from sentinellab.storage.database import StorageError, database_summary, initialize_database
from sentinellab.web.server import LocalServer
from tests.integration.test_storage import event


class WebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "new" / "events.db"
        initialize_database(self.db)
        self.server = LocalServer(self.db, port=0, testing_no_auth=True)
        self.worker = Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        self.worker.start()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=5)
        self.temp.cleanup()

    def request(self, method, path, body=None, headers=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            # The client normally sends headers and body separately. Buffer this
            # finite test request so an early rejection cannot race a later body
            # send on Windows. Send once; never retry a potentially mutating POST.
            chunks = []
            send = connection.send
            connection.send = chunks.append
            connection.request(method, path, body=body, headers=headers or {})
            connection.send = send
            send(b''.join(chunks))
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def upload(self, content, **changes):
        headers = {"Origin": self.server.origin, "X-SentinelLab-Token": self.server.token,
                   "Content-Type": "application/x-ndjson"}
        headers.update(changes)
        return self.request("POST", "/api/import", content, headers)

    def data(self, *records):
        return ("\n".join(json.dumps(x) for x in records) + "\n").encode()

    def test_fresh_database_home_and_static_allowlist(self):
        self.assertEqual(database_summary(self.db)["total_imports"], 0)
        code, headers, body = self.request("GET", "/")
        self.assertEqual(code, 200)
        self.assertIn(b"Follow the evidence", body)
        self.assertIsNotNone(re.search(rb'content="[0-9a-f]{64}"', body))
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["Cache-Control"], "no-store")
        for path in ("/static/app.js", "/static/style.css", "/static/workspace.js", "/static/workspace.css"):
            self.assertEqual(self.request("GET", path)[0], 200)
        for path in ("/AGENTS.md", "/static/../../storage/database.py", "/data/runtime/events.db"):
            self.assertEqual(self.request("GET", path)[0], 404)

    def test_import_search_lookup_and_duplicate_roundtrip(self):
        content = self.data(event(), event(event_id="e-2", outcome="success"))
        code, _, body = self.upload(content)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["inserted"], 2)
        self.assertEqual(json.loads(self.upload(content)[2])["duplicates"], 2)
        query = urlencode({"username": "demo_user", "source_ip": "192.0.2.10", "outcome": "failure",
                           "start": "2026-09-26T15:00:00+05:00", "end": "2026-09-26T10:01:00Z", "limit": 1})
        code, _, body = self.request("GET", "/api/events?" + query)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["total_matches"], 1)
        evidence = json.loads(self.request("GET", "/api/events/1")[2])["event"]
        self.assertEqual(json.loads(evidence["original_record"]), event())
        self.assertEqual(self.request("GET", "/api/events/999")[0], 404)

    def test_event_browser_still_reads_and_imports_after_alert_migration(self):
        from sentinellab.storage.alerts import save_detection, alert_summary
        self.assertEqual(self.upload(self.data(event()))[0], 200)
        save_detection(self.db)
        self.assertEqual(json.loads(self.request("GET", "/api/events")[2])["total_matches"], 1)
        self.assertEqual(self.request("GET", "/api/events/1")[0], 200)
        self.assertEqual(json.loads(self.upload(self.data(event()))[2])["duplicates"], 1)
        self.assertEqual(alert_summary(self.db)["detection_runs"], 1)

    def test_browser_result_filter_contains_all_three_real_options(self):
        class Options(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_outcome = False
                self.values = []

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "select":
                    self.in_outcome = attrs.get("name") == "outcome"
                elif tag == "option" and self.in_outcome:
                    self.values.append(attrs.get("value"))

            def handle_endtag(self, tag):
                if tag == "select":
                    self.in_outcome = False

        parser = Options()
        parser.feed(self.request("GET", "/")[2].decode())
        self.assertEqual(parser.values, ["", "failure", "success"])

    def test_partial_import_and_conflict_keep_original(self):
        self.upload(self.data(event()))
        code, _, body = self.upload(self.data(event(outcome="success"), {"bad": "<secret>"}, event(event_id="new")))
        report = json.loads(body)
        self.assertEqual((code, report["inserted"], report["conflicts"], report["rejected"]), (200, 1, 1, 1))
        self.assertNotIn(b"<secret>", body)
        self.assertEqual(json.loads(self.request("GET", "/api/events/1")[2])["event"]["outcome"], "failure")

    def test_host_origin_token_and_cross_site_protections(self):
        before = self.db.read_bytes()
        for changes in ({"Origin": "https://untrusted.invalid"}, {"Origin": "null"},
                        {"X-SentinelLab-Token": "wrong"}, {"X-SentinelLab-Token": "é"},
                        {"Host": "untrusted.invalid"}, {"Sec-Fetch-Site": "cross-site"}):
            with self.subTest(changes=changes):
                self.assertEqual(self.upload(self.data(event()), **changes)[0], 403)
        self.assertEqual(self.request("POST", "/api/import", b"", {"Content-Type": "application/x-ndjson"})[0], 403)
        self.assertEqual(self.request("GET", "/api/events", headers={"Origin": "https://untrusted.invalid"})[0], 403)
        self.assertEqual(self.db.read_bytes(), before)

    def test_oversized_and_wrong_content_type_do_not_write(self):
        self.assertEqual(self.upload(b"", **{"Content-Length": str(MAX_FILE_BYTES + 1)})[0], 413)
        self.assertEqual(self.upload(b"", **{"Content-Type": "text/plain"})[0], 415)
        self.assertEqual(self.upload(b"", **{"Transfer-Encoding": "chunked"})[0], 411)
        self.assertEqual(database_summary(self.db)["total_imports"], 0)

    def test_incomplete_upload_does_not_write(self):
        with socket.create_connection(("127.0.0.1", self.server.server_port), timeout=5) as connection:
            request = (f"POST /api/import HTTP/1.0\r\nHost: 127.0.0.1:{self.server.server_port}\r\n"
                       f"Origin: {self.server.origin}\r\nX-SentinelLab-Token: {self.server.token}\r\n"
                       "Content-Type: application/x-ndjson\r\nContent-Length: 100\r\n\r\nx")
            connection.sendall(request.encode())
            connection.shutdown(socket.SHUT_WR)
            self.assertIn(b"400", connection.recv(1024).split(b"\r\n")[0])
        self.assertEqual(database_summary(self.db)["total_imports"], 0)

    def test_invalid_filters_and_empty_results(self):
        for query in ("limit=201", "offset=-1", "username=a&username=b", "extra=x", "limit=no",
                      "start=2026-09-26", "source_ip=invalid", "outcome=banana"):
            with self.subTest(query=query):
                self.assertEqual(self.request("GET", "/api/events?" + query)[0], 400)
        self.assertEqual(json.loads(self.request("GET", "/api/events?username=absent")[2])["events"], [])
        self.assertEqual(self.request("GET", "/api/events?username=" + "a" * 8192)[0], 414)

    def test_pagination_and_untrusted_text_remain_data(self):
        text = '<img src=x onerror="alert(1)">'
        self.upload(self.data(event(username=text), event(event_id="e-2")))
        first = json.loads(self.request("GET", "/api/events?limit=1")[2])
        second = json.loads(self.request("GET", "/api/events?limit=1&offset=1")[2])
        self.assertEqual(first["events"][0]["username"], text)
        self.assertEqual(first["next_offset"], 1)
        self.assertNotEqual(first["events"][0]["id"], second["events"][0]["id"])
        self.assertEqual(self.request("GET", "/api/events")[1]["Content-Type"], "application/json; charset=utf-8")

    def test_reinitialization_preserves_data_and_rejects_unrelated_file(self):
        self.upload(self.data(event()))
        initialize_database(self.db)
        self.assertEqual(database_summary(self.db)["total_events"], 1)
        bad = Path(self.temp.name) / "bad.db"
        bad.write_bytes(b"unrelated")
        with self.assertRaises(StorageError):
            initialize_database(bad)
        self.assertEqual(bad.read_bytes(), b"unrelated")
