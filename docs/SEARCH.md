# Event search contract

CLI: scripts/database.py search --database PATH [--username TEXT] [--source-ip IP] [--outcome success|failure] [--start TIME] [--end TIME] [--limit N] [--offset N] [--json].

Python API: sentinellab.storage.search.search_events(database_path, *, username=None, source_ip=None, outcome=None, start=None, end=None, limit=50, offset=0).

All supplied filters combine with AND. Username matches exactly, preserving case and spaces, with the input format's supported text and 128-character limit. IP is normalized like ingestion, without zone identifiers. Times follow the event format and normalize to UTC microseconds. Start is inclusive; end is exclusive. Either bound may be omitted; when both exist start must precede end. Detection windows have separate rules.

Order: timestamp_utc ascending, then internal id ascending. Limit is an integer 1-200 (default 50). Offset is an integer 0-1,000,000 (default 0). Boolean values are rejected by the Python API. Results include total_matches, returned, limit, offset, next_offset, and events. Each event has id, source, event_id, timestamp_utc, source_ip, username, event_type, outcome. No original text appears in search lists.

Count and page share one read transaction. Separate pages do not share a snapshot: concurrent imports can shift offsets. Finish browsing before importing more data. next_offset is null at the end or when continuation exceeds the offset bound. Narrow filters for larger datasets. Limits bound returned rows, not query cost: counts and non-time filters may scan the database. Large-dataset performance and retention remain future work.

Evidence lookup: scripts/database.py get INTERNAL_ID --database PATH [--json]. Python: get_event(database_path, internal_id). Positive SQLite signed-64-bit integer IDs only. Returns normalized fields plus original_record, first_import_id, first_line_number. Python returns None for no match; CLI returns event: null and exits 1. Internal IDs belong to a particular database; they differ from source event_id strings.

Both operations open mode=ro and validate schema version 1 without creating, migrating, or modifying databases. User values are parameterized. CLI record output uses escaped JSON. Exit 0: successful search (including empty results) or found evidence. Exit 1: lookup absent. Exit 2: invalid filter, usage, file, or database error. Import exit codes are unchanged.
