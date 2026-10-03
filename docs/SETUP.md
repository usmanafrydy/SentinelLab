# Run SentinelLab readers and storage commands

## Current Day 15 evaluation

From the project folder run `.\.venv\bin\python.exe scripts/evaluate.py` and inspect `$LASTEXITCODE`. The existing laptop uses bin; a fresh Windows venv usually uses Scripts. No sign-in or user database is needed. Expect twelve scenarios, twelve expected-rule agreements and three of each TP/FP/TN/FN. Exit 0 means rule agreement, not perfect detection. See DAY_15_GUIDE.md for simple-English steps. Run `scripts/run_tests.py` with the same Python for all 193 tests. Continue using the Day 14 demonstration database and account; evaluation does not modify them. Later sections describe historical checkpoints.


## Current Day 14 workspace

Existing account: do not recreate it. Use the Day 14 copy for continued work; earlier databases remain separate. Start only if this server is stopped:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json
```

Open http://127.0.0.1:8776/ and sign in. Overview explains the workflow; Events contains import/search; Detection contains checks/alerts/runs; Investigations contains cases and reports. See DAY_14_GUIDE.md. In-page navigation retains drafts but does not save them. A fresh checkout has no demo database: import the sample, explicitly save detection and create a case. Historical startup examples below refer to older separate demos.

## Current Day 13 continuation and reports

Existing account: do not recreate it. Use the prepared Day 13 database for continued work. Start only if this server is not already running:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/serve.py --database data/runtime/day13_demo.db --port 8774 --credentials secrets/analyst.json
```

Open http://127.0.0.1:8774/ and sign in. Open a case, then choose Download Markdown or Download JSON. Only saved work is included; refresh if the case revision changed. Reports contain original evidence: review them before sharing.

Optional CLI: .\.venv\bin\python.exe scripts/export_report.py --database data/runtime/day13_demo.db --case-id 1 --format json. Output is restricted to ignored reports/generated and never overwrites files. Use --output reports/generated/another-name.json for another copy. See DAY_13_GUIDE.md and REPORTS.md for complete steps and limits. A fresh checkout has no runtime data; import a sample, explicitly save detection and create a case before exporting. Historical examples below use separate databases and do not automatically synchronize with Day 13.

## Day 12 account required for browser startup

Before the older browser examples below, create a private local account once. Existing users skip creation.

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/account.py --username usman
.\.venv\bin\python.exe scripts/serve.py --database data/runtime/day12_demo.db --port 8773 --credentials secrets/analyst.json
```

Enter matching 15..128 character passwords at the hidden prompts. Never put a password in chat, command arguments or tracked files. Setup refuses overwrite. Open http://127.0.0.1:8773 and sign in. Missing/invalid credentials prevent startup. A fresh database starts empty: import the synthetic sample and explicitly save detection. Prepared Day 12 data was copied consistently from Day 11, preserving the older file. CLI/database access is outside browser sign-in protection. See DAY_12_GUIDE.md for concepts and recovery.

## Requirements and current environment

Tested on September 26, 2026 with the existing MSYS2 UCRT Python 3.12.7 on Windows. Standard-library json, datetime, ipaddress, unittest, sqlite3, and venv are available. No third-party dependencies are required today. The Windows py launcher has no registered installations on this laptop; use the working python command below.

The local environment is .venv/bin/python.exe on this installation. Standard Windows CPython normally uses .venv/Scripts/python.exe. Check which exists instead of assuming the layout. Before adding web dependencies, review interpreter/package compatibility; the current setup includes a standard-library local HTTP prototype; third-party web packages are not yet verified.

## 1. Open PowerShell in the project

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
python --version
```

For another computer, use its own project location and a Python 3.12 installation.

## 2. Create an isolated environment on a fresh checkout

Already completed on this laptop. On a fresh checkout:

```powershell
python -m venv --without-pip .venv
```

There are no external packages today, so pip is not needed. Do not commit .venv. If the project moves again, recreate the environment at the new location rather than moving it. See the official Python documentation: https://docs.python.org/3.12/library/venv.html

## 3. Select the environment interpreter

```powershell
if (Test-Path '.venv/Scripts/python.exe') {
    $projectPython = '.venv/Scripts/python.exe'
} elseif (Test-Path '.venv/bin/python.exe') {
    $projectPython = '.venv/bin/python.exe'
} else {
    throw 'Create the project environment first.'
}
& $projectPython -c "import sys; print(sys.version); print('Isolated:', sys.prefix != sys.base_prefix)"
```

Expected: Python 3.12 and Isolated: True. No activation script or change to Windows execution policy is needed.

## 4. Check the good sample

```powershell
& $projectPython scripts/check_events.py data/samples/day01_login_events.jsonl
```

Expected: Accepted: 3, Rejected: 0, Blank lines skipped: 0. These are format counts, not alert counts.

## 5. Check an intentionally mixed sample

```powershell
& $projectPython scripts/check_events.py data/samples/day02_mixed_events.jsonl
```

Expected: Accepted: 2, Rejected: 1, Blank lines skipped: 1. Line 2 is rejected because banana is not an allowed outcome. This demo intentionally exits with status 1. The reader still accepts the later valid record.

## 6. Run the checks

```powershell
& $projectPython scripts/run_tests.py
```

Expected for Day 7: 103 passing tests for validation, storage, search, CLI, local HTTP, and all three detection rules. Persistent alert and full dashboard tests come later.

Add --json to check_events.py for a machine-readable summary. Exit code 0 means the file was checked without rejected records; 1 means some records were rejected; 2 means a fatal input/usage problem. An empty file is valid and produces zero counts. Summaries omit original event values.

## Troubleshooting

- Command not found: check Python installation and command path. On this laptop the base interpreter is C:\msys64\ucrt64\bin\python.exe.
- Missing .venv interpreter: recreate the environment; do not download or edit arbitrary executables.
- File cannot be read: check the file path and permissions; run from the project folder or supply an absolute sample path.
- Rejected line: read its reason, compare the fields with EVENT_FORMAT.md, and correct the input if appropriate. Do not alter original investigation evidence just to make it pass.
- Large file: current file limit is 2 MiB and 10,000 physical lines; individual lines are limited to 16 KiB.

## Day 3: save and inspect events

After choosing $projectPython above:

```powershell
& $projectPython scripts/database.py import data/samples/day01_login_events.jsonl --database data/runtime/day03_demo.db
& $projectPython scripts/database.py summary --database data/runtime/day03_demo.db
```

This laptop's demo database already contains 3 events from two imports. Another identical import reports 0 inserted and 3 duplicates. On a fresh checkout, the first import creates the database and inserts 3. Parent folders are created automatically. Relative paths are resolved from the current working directory.

Add --json for structured output. Storage exit codes: 0 = success (including duplicates alone); 1 = completed with invalid records or conflicts; 2 = fatal file/database/usage problem. Exit 1 can still save valid new records. A database write failure rolls back the whole batch.

check_events.py remains a format-only reader. database.py import explicitly saves events. Summary is read-only. See DATABASE.md for schema, evidence, and count definitions.

## Day 4: search and original evidence

Follow DAY_04_GUIDE.md for copyable commands and expected results. SEARCH.md defines filters, pagination, and exit codes. Search and get are read-only and require an existing database.

## Day 5: local browser workspace

After selecting $projectPython above:

```powershell
& $projectPython scripts/serve.py --database data/runtime/day05_demo.db
```

Open http://127.0.0.1:8765. Keep PowerShell open; Ctrl+C stops the server without deleting data. A fresh database starts with zero events/imports. This laptop's verified Day 5 demo has 3 events and 2 imports; importing the Day 1 sample again skips 3 duplicates. It is separate from the Day 3 database. If the port is busy, use the already running preview or add --port 8767 and use that port in the URL. No host override is supported. Follow DAY_05_GUIDE.md for browser practice and WEB.md for protocol and limitations. All runtime databases remain ignored by Git.

## Day 6: R1 detection preview

Follow DAY_06_GUIDE.md for R1 commands using --rule R1. Since Day 7, scripts/detect.py --database PATH [--json] defaults to all three rules. Exit 0 means success regardless of alert count; exit 2 means failure. Maximum dataset: 10,000 stored events. See DETECTION_RULES.md for exact window/grouping behavior. The existing browser does not automatically run this command.

## Day 7: combined detection

Follow DAY_07_GUIDE.md to import data/samples/day07_all_rules.jsonl into data/runtime/day07_demo.db, then run scripts/detect.py --database data/runtime/day07_demo.db --json. Expected: 16 scanned events and 3 previews. --rule accepts R1, R2, R3, or all (default). Combined output stops at 100,000 evidence references, returning an error rather than a partial preview. Alerts are not persisted. No new dependencies or schema migration required.

## Days 8-9: saved alerts and browser history

Day 10 update: scripts/cases.py adds create/list/get/note/state/history. See DAY_10_GUIDE.md for copyable commands and INVESTIGATIONS.md for constraints. Full suite is now 149 tests. Read the prepared example with:

```powershell
& ./.venv/bin/python.exe scripts/cases.py get --database data/runtime/day10_demo.db --case-id 1
& ./.venv/bin/python.exe scripts/cases.py history --database data/runtime/day10_demo.db --case-id 1
```

The separate demo case is in_progress/undecided, revision 3 after creation, one note, and a status change. Case creation explicitly migrates saved-alert databases from v2 to v3; reads never migrate. Existing event/alert commands support v3. Restart older Python servers before opening an upgraded database. The browser has no case controls yet.

CLI detection with --save explicitly saves a run and deduplicated snapshots; omission remains a read-only preview. See DAY_08_GUIDE.md. Day 9 adds Run detection and save, paged alerts/runs, and evidence navigation. Uploads alone never trigger detection. See DAY_09_GUIDE.md for fresh-database steps. Full suite: 133 passing tests.

From the project folder, start today's demo only if its server is not already running:

```powershell
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day09_demo.db --port 8769
```

Open http://127.0.0.1:8769. Verification left 16 events, 3 alerts, 2 runs, and 1 import. Further saves add runs while unchanged alerts remain deduplicated. Restart after Python changes and refresh the page for the new token. Runtime databases are not published.
