# Day 3 - Save records after the program closes

## 1. What is a database?

Day 2 kept the results in memory. Those results disappeared when the program ended. Today we save accepted events to a SQLite file on disk.

Roman Urdu: Database record book ki tarah hai. Program band hone ke baad bhi data rehta hai.

SQLite is already available in our Python environment. No extra package was installed.

## 2. What is a table?

Think of a spreadsheet. One row is a record; each column holds part of it. We made two tables: events holds login records, and imports holds a summary of each import.

Roman Urdu: events mein login records hain. imports mein har import ka result hai: kitne naye records, duplicates, aur errors thay.

## 3. Avoid duplicate events

We identify an event using source plus event_id. A new identity is saved. If the same identity arrives with the same details, it is a duplicate and is skipped.

Roman Urdu: Wahi record dobara aaye to usay dobara save nahi karein ge.

The same event ID from a different source is a different identity. Equivalent timestamps or JSON formatting changes do not make an event new.

## 4. Handle a conflict

Suppose an existing record says failure. Another record has the same source and event ID but says success. That is a conflict. We keep the first record and report the problem.

Roman Urdu: Same ID ki details badal jayein to purana record overwrite nahi hoga. Pehle conflict ko check karein ge.

Original text and normalized values are saved together. This helps review, but is not tamper-proof storage: someone with access to the database file can alter it outside our application.

## 5. What is a transaction?

A transaction groups related database changes. If a database write fails halfway through, that import's writes are rolled back.

Roman Urdu: Database failure par adhoora import save nahi hoga. Us batch ki changes wapas ho jayengi.

An invalid input line is different: we report that line and can still save valid records in the batch.

## 6. Our demonstration

First import: 3 new events.
Second import of the same file: 0 new events, 3 duplicates.
Reopen in another process: still 3 events, with 2 import-history entries.

Database location: data/runtime/day03_demo.db. It remains local and is excluded from GitHub. Another identical import adds a history entry but no new events.

## 7. Run it if you want

Follow SETUP.md to open the project and select $projectPython, then use:

```powershell
& $projectPython scripts/database.py summary --database data/runtime/day03_demo.db
& $projectPython scripts/database.py import data/samples/day01_login_events.jsonl --database data/runtime/day03_demo.db
```

The first command reads counts. The second imports our sample again. No network scans, real login attempts, or attack detection happen here. If a database cannot be read, check the path and report the error. Do not discard an existing database to fix an error.

## 8. Tests and your exercise

All 46 tests passed. They cover the reader plus database persistence, duplicates, conflicts, concurrent imports, and rollback on an intentionally forced write failure. Full application features are still in progress.

Answer in this chat:

1. We import 3 events, then import the identical file again. Should the database contain 3 or 6 events?
2. The same source/event ID arrives with changed details. Should we overwrite the original or report a conflict?
3. Will the saved records remain after closing the program?

Simple English ya Roman Urdu mein jawab dein.

Next session: event search by account, IP address, time, and outcome. Completion target remains October 17.
