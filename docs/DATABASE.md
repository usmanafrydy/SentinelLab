# SQLite event storage - schema versions 1 and 2

Day 3 uses Python sqlite3 without extra packages. Reference: https://docs.python.org/3.12/library/sqlite3.html

## Tables

- events: one row per (source, event_id), enforced by a UNIQUE constraint. Stores normalized UTC timestamp, IP, username, type, outcome, canonical JSON, original accepted text, first import ID, and first line number. An internal integer ID provides a future evidence reference. Timestamp text has fixed microsecond precision and a UTC offset; a time index supports later searching.
- imports: one row per completed import, with import time, validated/inserted/duplicate/conflict/rejected/blank counts, and safe line-specific errors. Invalid raw records and source file paths are not saved. Reimports add history even when zero new events are inserted.

## Identity and evidence

Compare all normalized fields using sorted-key canonical JSON. JSON whitespace, key order, equivalent time offsets, and equivalent IP text do not create different events. Username case/spaces and genuine value changes remain significant.

A new (source, event_id) is inserted. Equal identity/content is skipped as a duplicate. Equal identity with different content is a conflict: the first record is kept. Within a batch the first valid occurrence wins; an invalid record does not reserve an ID. The first accepted raw text is retained without its LF terminator; a CR can remain for CRLF files. Reimports do not replace it.

## Transactions

Validate the bounded input before opening the database. BEGIN IMMEDIATE serializes writers. Schema initialization, import-history insertion, event writes, and summary updates share one transaction. A database error rolls back the whole batch. A newly created empty file may remain, but no partial event/import rows commit.

Validation errors and identity conflicts are expected line-level results: valid new records can still commit. All event values use SQL placeholders. Unrelated databases and unsupported schema versions fail without automatic migration. Summary uses read-only mode and never creates missing files.

## Counts and exit codes

validated = inserted + duplicates + conflicts. Nonblank input records = validated + rejected. Blank lines are separate. total_events reports database size at the import checkpoint. These are not alert counts.

Exit 0: completed successfully, including duplicates-only imports. Exit 1: completed with validation rejections or conflicts. Exit 2: fatal file/database/usage problem.

## Limits

Reader limits remain 2 MiB/file, 10,000 physical lines, and 16 KiB/line. Lock timeout: five seconds. No total database retention limit yet. Read-only search and evidence lookup are documented in SEARCH.md. All rules have read-only previews (DETECTION_RULES.md). Day 8 adds explicit --save with atomic v1-to-v2 migration and alert/run tables; see ALERT_STORAGE.md. Event imports initialize v1 and accept both versions. Detection caps input at 10,000 events and output at 100,000 evidence references. No encryption at rest, tamper-evident storage, or full forensic chain of custody yet. Generated databases are excluded from Git. Use synthetic or authorized local-lab data.
