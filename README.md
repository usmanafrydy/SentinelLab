# SentinelLab

A planned security event detection and investigation platform for a cybersecurity portfolio.

## Current status

Day 14 completed: focused Overview, Events, Detection and Investigations workspaces, responsive navigation, focused original evidence with return navigation, case shortcuts and retained drafts/filters across section changes. Existing sign-in, case history, Markdown/JSON exports and three rules remain protected; 184 tests pass. Held-out evaluation, clean setup and portfolio release remain pending. Target completion: October 17, 2026.

## Planned scope

- Import and validate one authentication-log format.
- Normalize and store events in SQLite.
- Detect repeated account failures, failures across many accounts, and success after a failure burst.
- Explain alerts using linked evidence and an event timeline.
- Record investigation notes and export reports.
- Test detection behavior using synthetic and local-lab data.

The list above describes the final target; the Current status section states what is implemented. This is a learning prototype, not a production SIEM.

## Proposed stack

Current checkpoint: Python 3.12, SQLite, a loopback-only standard-library HTTP server, HTML/CSS/JavaScript, and unittest. No third-party dependencies yet. This server is a local learning prototype; review the web stack before authenticated deployment. Planned later: FastAPI, HTML/CSS/JavaScript, and optional pytest tooling; versions will be selected when needed.

## Layout

```text
src/sentinellab/
  ingestion/       Input parsing, validation, and normalization
  detection/       Detection rules and event correlation
  storage/         Database access and schema
  web/
    templates/     Dashboard pages
    static/        Styles and browser scripts
tests/
  unit/            Isolated behavior checks
  integration/     Workflow checks
  fixtures/        Small synthetic test inputs
data/samples/      Shareable synthetic demonstration data
docs/              Plan, architecture, and progress
scripts/           Future development and lab utilities
reports/examples/  Sanitized demonstration reports
```

Empty directories contain `.gitkeep` files because Git does not track empty directories.

## Getting started

Use the [Day 14 workspace guide](docs/DAY_14_GUIDE.md) for the current interface and startup on port 8776. The [navigation contract](docs/NAVIGATION.md) explains draft preservation, keyboard focus and Back/Forward behavior. Navigation does not save drafts; full reload still loses unsaved text. The cumulative Word/Markdown handbook now includes chapter 31 for Day 14 and an updated completion map. Word page layout remains unverified because the bundled LibreOffice renderer is unavailable.

Start with the [Day 13 report guide](docs/DAY_13_GUIDE.md) for the current workspace and exports, and the [report contract](docs/REPORTS.md) for content and limits. The [Day 12 sign-in guide](docs/DAY_12_GUIDE.md) covers account setup. The [Day 11 browser guide](docs/DAY_11_GUIDE.md) covers investigations and the [Day 10 guide](docs/DAY_10_GUIDE.md) covers the equivalent CLI. See the [access contract](docs/AUTHENTICATION.md) and [investigation contract](docs/INVESTIGATIONS.md) for exact behavior and limits.

The browser includes a Start here walkthrough and expandable explanations. The cumulative [project handbook](docs/SENTINELLAB_HANDBOOK.md) and [Word edition](docs/SentinelLab_Project_Handbook.docx) include explanations through Day 14; chapters 30 and 31 teach reports and navigation, with file responsibilities, usage, tests and remaining work. Older editions remain historical references. Word content/structure checks pass; visual pagination review is pending because bundled LibreOffice is unavailable. Every future checkpoint must update both cumulative editions.

Start with the [Day 9 guide](docs/DAY_09_GUIDE.md) for browser detection and alert evidence, the [Day 8 guide](docs/DAY_08_GUIDE.md) for command-line history, or the [Day 7 guide](docs/DAY_07_GUIDE.md) for all three rules. CLI saving requires explicit --save; browser saving requires Run detection and save. Uploading alone never runs detection.

Run the reader and tests using [setup instructions](docs/SETUP.md). Read the [Day 6 detection guide](docs/DAY_06_GUIDE.md), [rule contract](docs/DETECTION_RULES.md), [Day 5 browser guide](docs/DAY_05_GUIDE.md), [web design and limits](docs/WEB.md), [Day 4 search guide](docs/DAY_04_GUIDE.md), [search contract](docs/SEARCH.md), [Day 3 guide](docs/DAY_03_GUIDE.md) and [database design](docs/DATABASE.md). The [Day 2 guide](docs/DAY_02_GUIDE.md) explains validation. Planning references: [Day 1 guide](docs/DAY_01_GUIDE.md), [project brief](docs/PROJECT_BRIEF.md), [acceptance criteria](docs/ACCEPTANCE_CRITERIA.md), and [event format](docs/EVENT_FORMAT.md). Continue using [next-session notes](docs/NEXT_SESSION.md) and the [dated roadmap](docs/ROADMAP.md).

## Development workflow

Complete one meaningful change, run applicable checks, review the staged diff, commit with a descriptive message, and push to the configured GitHub repository. Keep progress documentation accurate.

Use synthetic or explicitly authorized local-lab data. Never commit credentials, private logs, or real investigation reports.

## Open the local browser workspace

From the project folder on this laptop:

```powershell
& ./.venv/bin/python.exe scripts/account.py --username usman
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day12_demo.db --port 8773 --credentials secrets/analyst.json
```

Create the account once with hidden password entry; skip setup if it already exists. Open http://127.0.0.1:8773 and sign in. Keep the server terminal running; stop with Ctrl+C. Use synthetic samples under data/samples. See SETUP.md for other Python environment layouts. Browser login does not restrict direct CLI/filesystem access. Do not deploy or tunnel this development server.

## Preview the first detection rule

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day06_repeated_failures.jsonl --database data/runtime/day06_demo.db
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day06_demo.db --rule R1 --json
```

Expected: 6 stored events, 1 R1 preview with 5 failure references. This preview does not save alerts or run automatically in the browser. See the [synthetic example result](reports/examples/day06_r1_preview.json); its internal IDs refer to the sample database, not every installation.

## Preview all three rules

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day07_all_rules.jsonl --database data/runtime/day07_demo.db
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day07_demo.db --json
```

Expected: 16 events, 3 previews (one per rule). Use --rule R2 or --rule R3 to inspect one pattern. See the [synthetic combined result](reports/examples/day07_all_rules_preview.json). Alert counts are not confirmed incident counts. Runs stop without partial results above 10,000 input events or 100,000 evidence references.

## Save alerts and read history

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day07_all_rules.jsonl --database data/runtime/day08_demo.db --json
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day08_demo.db --save --json
& ./.venv/bin/python.exe scripts/alerts.py summary --database data/runtime/day08_demo.db --json
& ./.venv/bin/python.exe scripts/alerts.py list --database data/runtime/day08_demo.db --json
& ./.venv/bin/python.exe scripts/alerts.py runs --database data/runtime/day08_demo.db --json
```

Fresh sample: 3 new alerts. Repeat the save: 0 new alerts, 3 already saved, and a second run. Saving upgrades an existing v1 database to v2 within the same transaction; original events are preserved. See the [storage contract](docs/ALERT_STORAGE.md) for rollback, late data, evidence links, and limits.
