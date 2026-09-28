# Day 5 local browser prototype

Entry point: scripts/serve.py --database PATH [--port 8765]. Relative database paths use the current directory. Server assets resolve relative to server.py, so launching from another directory does not expose that directory. Startup creates/validates schema version 1 with no import-history row. It does not migrate unsupported databases.

## Architecture and implementation choice

Python 3.12.7 and its http.server module work in this laptop's MSYS2 environment. Day 5 uses the standard library, static HTML/CSS/JavaScript, and existing SQLite services, with no package downloads. Python explicitly does not recommend http.server for production: https://docs.python.org/3.12/library/http.server.html . This is a bounded local learning checkpoint. Review a maintained web framework and runtime before implementing authenticated deployment; the original FastAPI stack remains a future option.

The server binds only 127.0.0.1; there is no host argument. UI/API requests use the exact displayed numeric host and port. There is no CORS allowance. No directory listing, arbitrary file serving, or client-selected database path exists.

## HTTP contract

| Method/path | Behavior |
| --- | --- |
| GET / | Page with a random per-process request token in a meta tag |
| GET /static/app.js or /static/style.css | Exact allowlisted assets |
| GET /api/summary | Stored event/import counts |
| GET /api/events | SEARCH.md filters using source_ip, limit, offset; unknown/repeated parameters rejected |
| GET /api/events/ID | Original evidence; 404 if no such internal ID |
| POST /api/import | Raw JSONL bytes; same schema and duplicate/conflict behavior as CLI |

Import requires exact Origin and a matching X-SentinelLab-Token from the page, application/x-ndjson, one numeric Content-Length, no Transfer-Encoding, and at most 2 MiB. Input is written to a fixed name inside an isolated temporary directory and removed after processing. Upload filenames and raw rejected values are not logged or stored. Accepted original records remain in SQLite. Per-line rejection/conflict still returns HTTP 200 with explicit counts because valid records can commit. Fatal parsing/storage problems return 400; oversized input 413; unsupported content type 415; missing/ambiguous length 411; request-check failures 403. Incomplete/timed-out bodies do not import.

Query URLs are capped at 8192 characters and 10 parameters. Row bounds and UTC semantics remain those in SEARCH.md. Socket timeout is 10 seconds; SQLite lock timeout remains 5 seconds. These are not complete denial-of-service protections: thread count, total storage, query CPU, and cumulative imports are not globally capped.

## Browser protections and limits

Host and supplied Origin are checked; cross-site Fetch Metadata requests are refused. Writes additionally require the per-run request token and exact Origin. Tokens rotate on restart; refresh the page afterward. This token is a cross-site request defense, not analyst authentication. A local process/user that can read the page can obtain it and use the API. There are no accounts, TLS, roles, or audit controls for analyst actions yet. Do not expose this server through proxies, tunnels, or public hosting.

Dynamic log values use textContent/DOM nodes, never HTML insertion. CSS classes for outcomes are allowlisted. Responses use no-store, nosniff, a restrictive Content Security Policy, frame-ancestors none, and no-referrer. Only same-origin scripts/styles/connections are allowed. No external fonts, assets, or telemetry. Search and evidence remain read-only; explicit import writes records.

## Verification on September 28, 2026

67 automated tests total. Browser-tested: empty database, good import, mixed input with duplicate/rejection summary, failed-login filter, original evidence, invalid IP error, 27-record Next pagination, and literal HTML-like username with zero injected image elements. Narrow viewport had no page-level horizontal overflow; table scrolling is intentional. A malformed Failure option was found in browser testing and fixed, with a parser regression test added.

Normal demo: data/runtime/day05_demo.db has 3 events and 2 imports after verification. Browser QA used a separate ignored day05_ui_checks.db and synthetic JSONL. Generated databases, environments, and QA inputs stay out of Git. Closing/reopening the browser retains saved data. Existing storage tests verify persistence across processes.

## Day 6 scope note

R1 now runs through scripts/detect.py as a read-only preview. This browser still provides event import/search/evidence only; no detection endpoint or automatic evaluation was added. The notice now makes that distinction explicit.
