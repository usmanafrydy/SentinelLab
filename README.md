# SentinelLab

A planned security event detection and investigation platform for a cybersecurity portfolio.

## Current status

Day 5 learning session completed: local browser import/search/evidence workspace, SQLite persistence, duplicate/conflict handling, and 67 passing tests. Detection rules, investigations, analyst sign-in, and the full alert dashboard are not implemented yet. Target completion: October 17, 2026.

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

Run the reader and tests using [setup instructions](docs/SETUP.md). Read the [Day 5 browser guide](docs/DAY_05_GUIDE.md), [web design and limits](docs/WEB.md), [Day 4 search guide](docs/DAY_04_GUIDE.md), [search contract](docs/SEARCH.md), [Day 3 guide](docs/DAY_03_GUIDE.md) and [database design](docs/DATABASE.md). The [Day 2 guide](docs/DAY_02_GUIDE.md) explains validation. Planning references: [Day 1 guide](docs/DAY_01_GUIDE.md), [project brief](docs/PROJECT_BRIEF.md), [acceptance criteria](docs/ACCEPTANCE_CRITERIA.md), and [event format](docs/EVENT_FORMAT.md). Continue using [next-session notes](docs/NEXT_SESSION.md) and the [dated roadmap](docs/ROADMAP.md).

## Development workflow

Complete one meaningful change, run applicable checks, review the staged diff, commit with a descriptive message, and push to the configured GitHub repository. Keep progress documentation accurate.

Use synthetic or explicitly authorized local-lab data. Never commit credentials, private logs, or real investigation reports.

## Open the local browser workspace

From the project folder on this laptop:

```powershell
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day05_demo.db
```

Open http://127.0.0.1:8765 and keep the terminal running. Stop with Ctrl+C. Use synthetic sample files under data/samples. See SETUP.md for other Python environment layouts. No analyst authentication yet; the server accepts only its exact loopback address. Do not deploy or tunnel this development server.
