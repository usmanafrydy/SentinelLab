# SentinelLab

A planned security event detection and investigation platform for a cybersecurity portfolio.

## Current status

Initial structure only. No application features, dependencies, or executable tests have been implemented. Development is planned to begin on September 24, 2026, when the owner resumes work.

## Planned scope

- Import and validate one authentication-log format.
- Normalize and store events in SQLite.
- Detect repeated account failures, failures across many accounts, and success after a failure burst.
- Explain alerts using linked evidence and an event timeline.
- Record investigation notes and export reports.
- Test detection behavior using synthetic and local-lab data.

These are planned capabilities, not completed features. This will be a learning prototype, not a production SIEM.

## Proposed stack

Python, FastAPI, SQLite, HTML/CSS/JavaScript, and pytest. Versions and dependencies will be selected during implementation.

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

There is nothing to run yet. Begin with `docs/NEXT_SESSION.md`, then review `docs/ROADMAP.md` and `AGENTS.md`.

## Development workflow

Complete one meaningful change, run applicable checks, review the staged diff, commit with a descriptive message, and push to the configured GitHub repository. Keep progress documentation accurate.

Use synthetic or explicitly authorized local-lab data. Never commit credentials, private logs, or real investigation reports.
