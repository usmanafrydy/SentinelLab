# Run SentinelLab readers and storage commands

## Requirements and current environment

Tested on September 26, 2026 with the existing MSYS2 UCRT Python 3.12.7 on Windows. Standard-library json, datetime, ipaddress, unittest, sqlite3, and venv are available. No third-party dependencies are required today. The Windows py launcher has no registered installations on this laptop; use the working python command below.

The local environment is .venv/bin/python.exe on this installation. Standard Windows CPython normally uses .venv/Scripts/python.exe. Check which exists instead of assuming the layout. Before adding web dependencies, review interpreter/package compatibility; the current setup has only been verified for this standard-library checkpoint.

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

Expected for Day 4: 57 passing tests for validation, database persistence, and command-line workflows. Dashboard and detection tests come later.

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
