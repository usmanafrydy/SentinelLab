# SentinelLab

An AI-assisted local security-event investigation prototype for a cybersecurity portfolio. Import synthetic login records, review explained alerts, retain original evidence, record investigations and export reports.

## Current status

Day 18 acceptance review completed on 4 October 2026: verified GitHub ZIP acquisition, a fresh environment with 194 passing tests, seven successful authenticated workflow checks and unchanged evaluation results. The owner reported successful manual account creation. See the [acceptance review and qualifications](docs/FINAL_ACCEPTANCE.md). Presentation practice, Word visual pagination and the final versioned release remain pending; target completion is October 17, 2026.

Start with [setup instructions](docs/SETUP.md), the [portfolio gallery](docs/portfolio/README.md), [five minute demo](docs/portfolio/DEMO_SCRIPT.md) and [case study](docs/portfolio/CASE_STUDY.md). Review [remaining release checks](docs/RELEASE_READINESS.md). The [Day 18 lesson](docs/DAY_18_GUIDE.md) explains this checkpoint simply.

![SentinelLab with synthetic demonstration data](docs/portfolio/screenshots/01-overview.jpg)

## Implemented workflow

- Validate bounded JSONL login events, normalize timestamps to UTC and retain accepted original record text.
- Store/search events in SQLite, deduplicate identical imports and report identity conflicts without replacing originals.
- Explicitly run R1 repeated-account failures, R2 failures across distinct accounts, and R3 success after earlier failures.
- Save versioned alert evidence and run history without duplicating unchanged findings.
- Sign in locally, create cases, append notes, record reasoned decisions and reject stale updates.
- Export complete saved investigations as bounded Markdown or JSON snapshots.
- Check rule behavior with synthetic scenarios and an isolated authenticated workflow rehearsal.

An alert is a lead for investigation, not proof of compromise. This application is not a live collector or production SIEM. It uses a single local account and loopback HTTP. Direct database access can alter records; reports are not signed or automatically redacted.

## Stack and layout

Python 3.12, SQLite, the Python standard-library HTTP server, HTML, CSS, JavaScript and unittest. No third-party application packages are required. A framework migration, public hosting and multiple roles are not implemented release features.

```text
src/sentinellab/       Ingestion, detection, storage, cases, reports and web code
scripts/              Account, server, import, detection, export and verification commands
tests/                Unit and integration checks
data/samples/         Synthetic demonstrations
data/evaluation/      Labeled synthetic evaluation corpus
docs/portfolio/       Demo, case study, CV notes, screenshots and reviewed sample reports
reports/examples/     Published synthetic rule/evaluation results
```

Runtime databases, credentials, virtual environments and normal generated/private reports are ignored. The portfolio's example reports are explicit reviewed synthetic exceptions, not permission to publish future private exports.

## Run and learn

Follow [SETUP.md](docs/SETUP.md) for a fresh copy or for continuing the owner's existing project. The owner uses .venv/bin/python.exe; other Windows Python installations commonly use .venv/Scripts/python.exe. Select the right interpreter as the guide shows, then run:

```powershell
& $projectPython scripts/run_tests.py
& $projectPython scripts/rehearse.py
& $projectPython scripts/evaluate.py
```

The [rehearsal record](docs/SETUP_REHEARSAL.md) describes the fresh venv, seven HTTP workflow checks and environment limitations. Day 18 successfully downloaded and hash-verified the published ZIP using bundled Python with TLS verification enabled, then tested a fresh venv. This does not repair the earlier runtime certificate configuration or test git clone. The owner reported the separate manual account command succeeded; keyboard visibility was not observed by the assistant. Local Git metadata in the owner's original copy remains behind under existing restrictions; connector publication is checked against every file hash.

The [evaluation lesson](docs/DAY_15_GUIDE.md) explains twelve authored scenarios: TP, FP, TN and FN are each three; all expected rule sets agree. These are synthetic results with known rules, not independent or real-world accuracy. See the [JSON results](reports/examples/day15_evaluation.json).

## Documentation

The cumulative [Markdown handbook](docs/SENTINELLAB_HANDBOOK.md) and [Word handbook](docs/SentinelLab_Project_Handbook.docx) include work through Day 18. Chapter 29 is the current completion map; chapter 34 explains the portfolio and chapter 35 explains acceptance verification. Earlier chapters retain historical lessons. Word content is checked, but visual pagination remains unverified while the supported LibreOffice renderer is unavailable.

Detailed contracts: [event format](docs/EVENT_FORMAT.md), [rules](docs/DETECTION_RULES.md), [alert storage](docs/ALERT_STORAGE.md), [investigations](docs/INVESTIGATIONS.md), [local access](docs/AUTHENTICATION.md), [reports](docs/REPORTS.md), [navigation](docs/NAVIGATION.md) and [evaluation](docs/EVALUATION.md). See [progress](docs/PROGRESS.md) and [next session](docs/NEXT_SESSION.md) for continuity.

This is a guided, AI-assisted learning project. Code, tests, documentation and debugging received substantial assistance. Portfolio claims should reflect the learner's actual understanding and involvement; no real incident-response experience or measured business impact is implied.
