# Local browser prototype through Day 12

## Current Day 12 access behavior

Startup requires a credential file (default secrets/analyst.json), created interactively by scripts/account.py. Workspace HTML and every data API require a server-side session. Login HTML and allowlisted static assets are public. POST /api/login accepts strict bounded JSON username/password with the login-page token. POST /api/logout accepts {} with the session token. Anonymous data requests return 401 with sign_in_required. Browser case authors come from the session; earlier and CLI labels remain self-declared. See AUTHENTICATION.md for precise limits and threat model.

168 tests pass, including eleven access/session tests. Browser checks covered wrong/correct login, session authors, case/note, logout, another tab's rejected save with retained draft, and desktop/390px login layouts without horizontal overflow. No console errors in the checked login flow. Protected continuation uses day12_demo.db on port 8773. Old running processes keep old behavior until restarted. Constructor testing_no_auth is restricted to explicit regression fixtures; no command-line bypass exists. Descriptions below are historical where dated.

Day 10 compatibility: after restarting with current Python code, the existing event/alert APIs accept schema v3 investigation databases and preserve case data. Case creation/notes/status/history currently use scripts/cases.py only. No case web routes or authenticated author identity have been added. Day 11 is planned to bring this workflow into the browser. The Day 9 interface guidance remains intact.

Entry point: scripts/serve.py --database PATH [--port 8765]. Relative database paths use the current directory. Server assets resolve relative to server.py, so launching from another directory does not expose that directory. Startup creates/validates schema version 1 with no import-history row. It does not migrate unsupported databases.

## Architecture and implementation choice

Python 3.12.7 and its http.server module work in this laptop's MSYS2 environment. Day 5 uses the standard library, static HTML/CSS/JavaScript, and existing SQLite services, with no package downloads. Python explicitly does not recommend http.server for production: https://docs.python.org/3.12/library/http.server.html . This is a bounded local learning checkpoint. Review a maintained web framework and runtime before implementing authenticated deployment; the original FastAPI stack remains a future option.

The server binds only 127.0.0.1; there is no host argument. UI/API requests use the exact displayed numeric host and port. There is no CORS allowance. No directory listing, arbitrary file serving, or client-selected database path exists.

## HTTP contract

| Method/path | Behavior |
| --- | --- |
| GET / | Page with a random per-process request token in a meta tag |
| GET /static/app.js, /static/alerts.js, /static/style.css, /static/alerts.css | Exact allowlisted assets |
| GET /api/summary | Stored event/import counts |
| GET /api/events | SEARCH.md filters using source_ip, limit, offset; unknown/repeated parameters rejected |
| GET /api/events/ID | Original evidence; 404 if no such internal ID |
| POST /api/import | Raw JSONL bytes; same schema and duplicate/conflict behavior as CLI |
| GET /api/alerts/summary | Saved alert/run totals; no query parameters |
| GET /api/alerts | Saved metadata list; limit, offset, optional run_id membership filter |
| GET /api/runs | Completed runs and rule configurations/counts; limit and offset |
| GET /api/alerts/ID | Saved metadata and bounded evidence page; limit and offset; missing alert 404 |
| POST /api/detect | Explicit atomic save; one form field rule=all, R1, R2, or R3 |

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

## Day 7 scope note

The command-line detector now runs R1/R2/R3 by default, with --rule for individual selection. Browser functionality remains event import/search/evidence; no detection endpoint was added. The page notice refers to detection generally. See DAY_07_GUIDE.md for the new sample and commands.

## Day 9 browser alerts and saving

Day 6/7 notes above describe historical checkpoints. The browser now provides explicit detection/save, saved-alert details with linked originals, paged alert/run lists, and per-run findings. Uploading still does not run detection. Detection checks the complete database regardless of event-table filters. CLI preview remains read-only.

POST /api/detect requires the same exact Host/Origin/token checks as import, exactly one Content-Type application/x-www-form-urlencoded, one numeric Content-Length, no Transfer-Encoding, and at most 128 body bytes. Exactly one rule field/value is required. Invalid input returns 400; over-limit 413; wrong content type 415; absent/ambiguous length 411; failed request checks 403. Success returns the existing save_detection report with run ID and scanned/matched/new/existing/total counts. Migration/evaluation/writes share one transaction; failed attempts leave no partial runs. Zero matches is successful. After a lost response, refresh history before retrying: a commit may have succeeded. There is no request-id idempotency.

New history queries reject unknown/repeated/malformed values. Lists default to 50 rows, details to 25 evidence references; limit is 1..200, offset 0..1,000,000. Pages provide total/items/limit/offset/next_offset (under evidence for details). run_id is 1..2^63-1 and selects membership, including alerts saved earlier; a valid nonexistent run yields an empty list. Alert IDs use the existing R1/R2/R3 plus SHA-256 format. HTTP detail metadata omits full evidence and R2 username arrays. Storage internally decodes the existing JSON before slicing; this is bounded output, not streaming storage. CLI full detail is unchanged. Version 1 history is empty without migration.

Browser pages show 10 alerts/runs or 25 evidence references. Concurrent saves may shift offsets across separate GETs. Refresh history restarts the lists. Detail requests guard against stale selections. Dynamic values use textContent. Busy controls prevent overlapping in-page import/detection. These controls are not authentication or complete resource-exhaustion protections.

Verified September 30: 133 tests pass, including 13 new HTTP cases for paging, repeat/selected/empty saves, protections, invalid inputs, read-only history, originals, and rollback. Browser verified 3 new then 0 new/3 existing, run-2 membership, R3's 6 references and original successful event 16, reload persistence, and desktop/narrow layouts without page-level horizontal overflow. No console errors observed. Large paging is verified by HTTP tests. Ignored day09_demo.db has 16 events, 1 import, 3 alerts, 2 runs after verification; serve on port 8769. Sign-in, investigations, and production deployment remain unfinished.

## Day 11 investigations - October 2, 2026

The browser now includes create/open-from-alert, case list/status filter, details, notes, reasoned state changes, revision-conflict recovery, bounded action history and links to original alert evidence. See INVESTIGATIONS.md for exact case API request/response contracts and DAY_11_GUIDE.md for the walkthrough. Allowlisted assets now include /static/cases.js and /static/cases.css. Shared API errors carry the conflict code to the UI. Responsive tables use internal horizontal scrolling to preserve readable columns.

157 tests pass. Browser verified case creation, note/decision persistence, duplicate case prevention, stale rejection with reason retention, refresh recovery, linked original evidence, and desktop/narrow layouts. No console errors observed in final check. Paging is covered by real HTTP tests. Separate ignored day11_demo.db contains 16 events, 1 import, 3 alerts, 1 run, 1 case and 5 actions after checks; case 1 is in_progress/suspicious at revision 5. Serve on port 8771. Sign-in, exports and final release evaluation remain pending. Older checkpoint descriptions above are historical.
