"""Loopback-only learning server; not a deployment server."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from html import escape
import re
from pathlib import Path
import secrets
import sys
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlsplit

from sentinellab.ingestion.reader import InputFileError, MAX_FILE_BYTES
from sentinellab.storage.database import StorageError, database_summary, import_events, initialize_database
from sentinellab.storage.search import get_event, search_events
from sentinellab.storage.alerts import alert_summary, list_history, get_alert_page, save_detection
from sentinellab.storage.cases import CaseConflict
from sentinellab.web.case_api import WRITE_PATH, read_case_request, write_case_request, _pairs, _invalid_constant
from sentinellab.web.auth import Auth
from sentinellab.reports import build_report, render_report, report_filename

ASSETS = Path(__file__).resolve().parent


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, database, port=8765, *, auth=None, testing_no_auth=False):
        if auth is None and not testing_no_auth:
            raise ValueError("An account is required. Use scripts/account.py first.")
        self.auth = auth
        self.database = Path(database).resolve()
        self.token = secrets.token_hex(32)
        # No configurable network host: this prototype is local-only.
        super().__init__(("127.0.0.1", port), Handler)
        self.origin = f"http://127.0.0.1:{self.server_port}"
        self.cookie_name = f"sentinellab_{self.server_port}"


class Handler(BaseHTTPRequestHandler):
    server_version = "SentinelLab"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *args):
        # Do not log search values, upload content, or the per-run request token.
        pass

    def reply(self, status, payload, content_type="application/json; charset=utf-8", *, cookie=None, filename=None):
        data = json.dumps(payload, ensure_ascii=True).encode() if not isinstance(payload, bytes) else payload
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if filename is not None:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        if cookie is not None:
            self.send_header("Set-Cookie", cookie)
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

    def session_key(self):
        values = self.headers.get_all("Cookie", [])
        if len(values) != 1:
            return None
        found = []
        for part in values[0].split(';'):
            name, sep, value = part.strip().partition('=')
            if name == self.server.cookie_name:
                found.append(value if sep else '')
        return found[0] if len(found) == 1 and re.fullmatch(r'[0-9a-f]{64}', found[0]) else None

    def session(self):
        return self.server.auth.get(self.session_key()) if self.server.auth else None

    def session_cookie(self, key, *, clear=False):
        return f"{self.server.cookie_name}={key}; Path=/; HttpOnly; SameSite=Strict" + ('; Max-Age=0' if clear else '')

    def login_page(self):
        page = (ASSETS / 'templates/login.html').read_text(encoding='utf-8')
        self.reply(200, page.replace('__REQUEST_TOKEN__', self.server.token).encode(), 'text/html; charset=utf-8')

    def do_GET(self):
        if not self.allowed():
            return
        try:
            url = urlsplit(self.path)
            if url.scheme or url.netloc:
                self.reply(400, {"error": "Use a local path."})
                return
            session = self.session()
            if url.path == '/login':
                self.login_page()
                return
            if self.server.auth and not session and not url.path.startswith('/static/'):
                if url.path == '/':
                    self.login_page()
                else:
                    self.reply(401, {'error': 'Your session ended. Sign in again; unsaved text stays in this page.', 'code': 'sign_in_required'})
                return
            if url.path == "/":
                page = (ASSETS / "templates/index.html").read_text(encoding="utf-8")
                self.reply(200, page.replace("__REQUEST_TOKEN__", session["csrf"] if session else self.server.token).replace("__ACCOUNT_NAME__", escape(session["username"] if session else "test_analyst", quote=True)).encode(), "text/html; charset=utf-8")
            elif url.path in ("/static/app.js", "/static/alerts.js", "/static/cases.js", "/static/style.css", "/static/alerts.css", "/static/cases.css", "/static/auth.js", "/static/workspace.js", "/static/workspace.css"):
                kind = "text/javascript" if url.path.endswith(".js") else "text/css"
                self.reply(200, (ASSETS / url.path.lstrip("/")).read_bytes(), kind + "; charset=utf-8")
            elif url.path == "/api/summary":
                self.reply(200, database_summary(self.server.database))
            elif match := re.fullmatch(r'/api/cases/([1-9][0-9]{0,18})/report', url.path):
                params = parse_qs(url.query, keep_blank_values=True, strict_parsing=True, max_num_fields=2)
                if (set(params) != {'format', 'revision'} or any(len(v) != 1 for v in params.values())
                        or params['format'][0] not in ('json', 'markdown')
                        or re.fullmatch(r'[1-9][0-9]{0,18}', params['revision'][0]) is None):
                    raise ValueError
                format = params['format'][0]
                report = build_report(self.server.database, int(match[1]), expected_revision=int(params['revision'][0]))
                if report is None:
                    self.reply(404, {'error': 'Case not found.'})
                else:
                    self.reply(200, render_report(report, format),
                               ('application/json' if format == 'json' else 'text/markdown') + '; charset=utf-8',
                               filename=report_filename(match[1], report['case']['revision'], format))
            elif url.path == "/api/cases" or url.path.startswith("/api/cases/"):
                code, result = read_case_request(self.server.database, url.path, url.query)
                self.reply(code, result)
            elif url.path == "/api/alerts/summary":
                self.query_options(url.query, set())
                self.reply(200, alert_summary(self.server.database))
            elif url.path in ("/api/alerts", "/api/runs"):
                runs = url.path == "/api/runs"
                options = self.query_options(url.query, {"limit", "offset"} if runs else {"limit", "offset", "run_id"})
                self.reply(200, list_history(self.server.database, runs=runs, **options))
            elif url.path.startswith("/api/alerts/"):
                options = self.query_options(url.query, {"limit", "offset"})
                result = get_alert_page(self.server.database, url.path.removeprefix("/api/alerts/"), **options)
                self.reply(200 if result else 404, result if result else {"error": "Saved alert not found."})
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
        except CaseConflict as error:
            self.reply(409, {'error': str(error), 'code': 'stale_revision'})
        except StorageError as error:
            self.reply(400, {"error": str(error)})
        except ValueError:
            self.reply(400, {"error": "Invalid query parameters or record ID."})
        except OSError:
            self.reply(500, {"error": "Cannot read the application files."})

    def query_options(self, query, permitted):
        params = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=10)
        if set(params) - permitted or any(len(values) != 1 for values in params.values()):
            raise ValueError
        return {key: int(values[0]) for key, values in params.items()}

    def do_POST(self):
        if not self.allowed():
            return
        session = self.session()
        login = self.path == '/api/login'
        logout = self.path == '/api/logout'
        if self.server.auth and not session and not login:
            self.reply(401, {'error': 'Your session ended. Sign in again; unsaved text stays in this page.', 'code': 'sign_in_required'})
            return
        if (login or logout) and not self.server.auth:
            self.reply(404, {'error': 'No account configured.'})
            return
        case_write = self.path == "/api/cases" or WRITE_PATH.fullmatch(self.path) is not None
        if self.path not in ("/api/import", "/api/detect") and not case_write and not login and not logout:
            self.reply(404, {"error": "Page not found."})
            return
        tokens = self.headers.get_all("X-SentinelLab-Token", [])
        if (self.headers.get_all("Origin", []) != [self.server.origin]
                or len(tokens) != 1 or not tokens[0].isascii()
                or not secrets.compare_digest(tokens[0], self.server.token if login or not session else session["csrf"])):
            self.reply(403, {"error": "Refresh the local page before saving changes."})
            return
        sizes = self.headers.get_all("Content-Length", [])
        if self.headers.get_all("Transfer-Encoding") or len(sizes) != 1 or not sizes[0].isascii() or not sizes[0].isdigit():
            self.reply(411, {"error": "A single Content-Length is required; streaming uploads are not supported."})
            return
        detecting = self.path == "/api/detect"
        maximum = 4096 if login or logout else 65536 if case_write else 128 if detecting else MAX_FILE_BYTES
        if len(sizes[0]) > 10 or int(sizes[0]) > maximum:
            self.reply(413, {"error": "Sign-in request exceeds 4 KiB." if login or logout else "Case request exceeds 64 KiB." if case_write else "Detection request exceeds 128 bytes." if detecting else "File exceeds the 2 MiB upload limit."})
            return
        content_type = "application/json" if case_write or login or logout else "application/x-www-form-urlencoded" if detecting else "application/x-ndjson"
        if self.headers.get_all("Content-Type", []) != [content_type]:
            self.reply(415, {"error": "Use the local page with the expected content type."})
            return
        try:
            length = int(sizes[0])
            content = self.rfile.read(length)
            if len(content) != length:
                self.reply(400, {"error": "Request was incomplete; no records saved."})
                return
            if login or logout:
                body = json.loads(content.decode('utf-8'), object_pairs_hook=_pairs, parse_constant=_invalid_constant)
                if logout:
                    if body != {} or type(body) is not dict:
                        raise ValueError
                    self.server.auth.logout(self.session_key())
                    self.reply(200, {'signed_out': True}, cookie=self.session_cookie('', clear=True))
                    return
                if type(body) is not dict or set(body) != {'username','password'} or any(type(v) is not str for v in body.values()):
                    raise ValueError
                code, key = self.server.auth.login(body['username'], body['password'], self.session_key())
                if code == 200:
                    self.reply(200, {'signed_in': True}, cookie=self.session_cookie(key))
                else:
                    self.reply(code, {'error': 'Too many attempts or sign-in is busy. Wait one minute and try again.' if code == 429 else 'Username or password is incorrect.'})
                return
            if case_write:
                self.reply(200, write_case_request(self.server.database, self.path, content, author=session["username"] if session else None))
                return
            if detecting:
                params = parse_qs(content.decode("ascii"), keep_blank_values=True, strict_parsing=True, max_num_fields=2)
                if set(params) != {"rule"} or len(params["rule"]) != 1:
                    raise ValueError
                self.reply(200, save_detection(self.server.database, params["rule"][0]))
                return
            # Never use a supplied filename or let clients choose a database path.
            with TemporaryDirectory(prefix="sentinellab-upload-") as temporary:
                source = Path(temporary) / "events.jsonl"
                source.write_bytes(content)
                report = import_events(source, self.server.database)
            self.reply(200, report)
        except InputFileError as error:
            self.reply(400, {"error": str(error)})
        except CaseConflict as error:
            self.reply(409, {"error": str(error), "code": "stale_revision"})
        except StorageError as error:
            self.reply(400, {"error": str(error)})
        except (ValueError, RecursionError):
            self.reply(400, {"error": "Invalid sign-in request." if login or logout else "Use the case form with all required text fields." if case_write else "Select exactly one rule: R1, R2, R3, or all."})
        except TimeoutError:
            self.reply(408, {"error": "Request timed out; refresh history before retrying."})
        except OSError:
            self.reply(500, {"error": "Request could not be processed; refresh history before retrying."})


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the local SentinelLab browser prototype.")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--credentials", type=Path, default=Path("secrets/analyst.json"))
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    try:
        with LocalServer(args.database, args.port, auth=Auth(args.credentials)) as server:
            initialize_database(args.database)
            print(f"SentinelLab: {server.origin} | Local learning prototype. Stop with Ctrl+C.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except (OSError, StorageError, ValueError) as error:
        print("Cannot start: check the account file, database, and port. Create an account with scripts/account.py first.", file=sys.stderr)
        return 2
    return 0
