"""Loopback-only learning server; not a deployment server."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import sys
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlsplit

from sentinellab.ingestion.reader import InputFileError, MAX_FILE_BYTES
from sentinellab.storage.database import StorageError, database_summary, import_events, initialize_database
from sentinellab.storage.search import get_event, search_events

ASSETS = Path(__file__).resolve().parent


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, database, port=8765):
        self.database = Path(database).resolve()
        self.token = secrets.token_hex(32)
        # No configurable network host: this prototype is local-only.
        super().__init__(("127.0.0.1", port), Handler)
        self.origin = f"http://127.0.0.1:{self.server_port}"


class Handler(BaseHTTPRequestHandler):
    server_version = "SentinelLab"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *args):
        # Do not log search values, upload content, or the per-run request token.
        pass

    def reply(self, status, payload, content_type="application/json; charset=utf-8"):
        data = json.dumps(payload, ensure_ascii=True).encode() if not isinstance(payload, bytes) else payload
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def allowed(self):
        hosts = self.headers.get_all("Host", [])
        origins = self.headers.get_all("Origin", [])
        if (hosts != [self.server.origin.removeprefix("http://")]
                or (origins and origins != [self.server.origin])
                or self.headers.get("Sec-Fetch-Site") == "cross-site"):
            self.reply(403, {"error": "Use the local SentinelLab page and its displayed address."})
            return False
        if len(self.path) > 8192:
            self.reply(414, {"error": "Search URL is too long."})
            return False
        return True

    def do_GET(self):
        if not self.allowed():
            return
        try:
            url = urlsplit(self.path)
            if url.scheme or url.netloc:
                self.reply(400, {"error": "Use a local path."})
                return
            if url.path == "/":
                page = (ASSETS / "templates/index.html").read_text(encoding="utf-8")
                self.reply(200, page.replace("__REQUEST_TOKEN__", self.server.token).encode(), "text/html; charset=utf-8")
            elif url.path in ("/static/app.js", "/static/style.css"):
                kind = "text/javascript" if url.path.endswith(".js") else "text/css"
                self.reply(200, (ASSETS / url.path.lstrip("/")).read_bytes(), kind + "; charset=utf-8")
            elif url.path == "/api/summary":
                self.reply(200, database_summary(self.server.database))
            elif url.path == "/api/events":
                params = parse_qs(url.query, keep_blank_values=True, max_num_fields=10)
                permitted = {"username", "source_ip", "outcome", "start", "end", "limit", "offset"}
                if set(params) - permitted or any(len(v) != 1 for v in params.values()):
                    raise ValueError
                filters = {k: v[0] for k, v in params.items()}
                for name in ("limit", "offset"):
                    if name in filters:
                        filters[name] = int(filters[name])
                self.reply(200, search_events(self.server.database, **filters))
            elif url.path.startswith("/api/events/"):
                event = get_event(self.server.database, int(url.path.removeprefix("/api/events/")))
                self.reply(200 if event else 404, {"event": event})
            else:
                self.reply(404, {"error": "Page not found."})
        except StorageError as error:
            self.reply(400, {"error": str(error)})
        except ValueError:
            self.reply(400, {"error": "Invalid search parameters or event ID."})
        except OSError:
            self.reply(500, {"error": "Cannot read the application files."})

    def do_POST(self):
        if not self.allowed():
            return
        if self.path != "/api/import":
            self.reply(404, {"error": "Page not found."})
            return
        tokens = self.headers.get_all("X-SentinelLab-Token", [])
        if (self.headers.get_all("Origin", []) != [self.server.origin]
                or len(tokens) != 1 or not tokens[0].isascii()
                or not secrets.compare_digest(tokens[0], self.server.token)):
            self.reply(403, {"error": "Refresh the local page before importing."})
            return
        sizes = self.headers.get_all("Content-Length", [])
        if self.headers.get_all("Transfer-Encoding") or len(sizes) != 1 or not sizes[0].isascii() or not sizes[0].isdigit():
            self.reply(411, {"error": "A single Content-Length is required; streaming uploads are not supported."})
            return
        if len(sizes[0]) > 10 or int(sizes[0]) > MAX_FILE_BYTES:
            self.reply(413, {"error": "File exceeds the 2 MiB upload limit."})
            return
        if self.headers.get("Content-Type") != "application/x-ndjson":
            self.reply(415, {"error": "Upload a JSON Lines file using the local page."})
            return
        try:
            length = int(sizes[0])
            content = self.rfile.read(length)
            if len(content) != length:
                self.reply(400, {"error": "Upload was incomplete; no records saved."})
                return
            # Never use a supplied filename or let clients choose a database path.
            with TemporaryDirectory(prefix="sentinellab-upload-") as temporary:
                source = Path(temporary) / "events.jsonl"
                source.write_bytes(content)
                report = import_events(source, self.server.database)
            self.reply(200, report)
        except InputFileError as error:
            self.reply(400, {"error": str(error)})
        except StorageError as error:
            self.reply(400, {"error": str(error)})
        except TimeoutError:
            self.reply(408, {"error": "Upload timed out; no records saved."})
        except OSError:
            self.reply(500, {"error": "Upload could not be processed."})


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the local SentinelLab browser prototype.")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    try:
        with LocalServer(args.database, args.port) as server:
            initialize_database(args.database)
            print(f"SentinelLab: {server.origin} | Local learning prototype. Stop with Ctrl+C.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except (OSError, StorageError) as error:
        print("Cannot start: check the database and whether the port is already in use.", file=sys.stderr)
        return 2
    return 0
