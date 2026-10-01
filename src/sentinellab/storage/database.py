"""Transactional storage. Import errors never overwrite existing evidence."""
from contextlib import closing
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3

from sentinellab.ingestion.reader import Event, read_events

SCHEMA_VERSION = 1
SCHEMA = (
    """CREATE TABLE imports (
        id INTEGER PRIMARY KEY,
        imported_at TEXT NOT NULL,
        validated INTEGER NOT NULL DEFAULT 0,
        inserted INTEGER NOT NULL DEFAULT 0,
        duplicates INTEGER NOT NULL DEFAULT 0,
        conflicts INTEGER NOT NULL DEFAULT 0,
        rejected INTEGER NOT NULL DEFAULT 0,
        blank_lines INTEGER NOT NULL DEFAULT 0,
        errors_json TEXT NOT NULL DEFAULT '[]'
    )""",
    """CREATE TABLE events (
        id INTEGER PRIMARY KEY,
        source TEXT NOT NULL,
        event_id TEXT NOT NULL,
        timestamp_utc TEXT NOT NULL,
        source_ip TEXT NOT NULL,
        username TEXT NOT NULL,
        event_type TEXT NOT NULL CHECK(event_type = 'login'),
        outcome TEXT NOT NULL CHECK(outcome IN ('success', 'failure')),
        canonical_json TEXT NOT NULL,
        original_record TEXT NOT NULL,
        first_import_id INTEGER NOT NULL REFERENCES imports(id),
        first_line_number INTEGER NOT NULL CHECK(first_line_number > 0),
        UNIQUE(source, event_id)
    )""",
    "CREATE INDEX events_time ON events(timestamp_utc, id)",
)


class StorageError(ValueError):
    """A safe storage failure message, without raw input or SQL values."""


def canonical_event(event: Event) -> dict:
    """Compare normalized values, not JSON spacing, key order, or offset spelling."""
    values = asdict(event)
    values["timestamp"] = event.timestamp.astimezone(timezone.utc).isoformat(timespec="microseconds")
    return values


def _check_schema(connection: sqlite3.Connection, *, create: bool = False) -> None:
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version == 0 and create:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        if tables:
            raise StorageError("database is not an empty SentinelLab database; choose another file")
        for statement in SCHEMA:
            connection.execute(statement)
        connection.execute("PRAGMA user_version = 1")
    elif version not in (1, 2, 3):
        raise StorageError("unsupported database schema; no automatic migration was attempted")
    # Fail before writing if a version label exists but required columns are absent.
    connection.execute("SELECT id, imported_at, validated, inserted, duplicates, conflicts, "
                       "rejected, blank_lines, errors_json FROM imports LIMIT 0")
    connection.execute("SELECT id, source, event_id, timestamp_utc, source_ip, username, "
                       "event_type, outcome, canonical_json, original_record, "
                       "first_import_id, first_line_number FROM events LIMIT 0")
    if version in (2, 3):
        from sentinellab.storage.alert_schema import validate_alert_schema
        validate_alert_schema(connection)
    if version == 3:
        from sentinellab.storage.case_schema import validate_case_schema
        validate_case_schema(connection)


def initialize_database(database_path: Path | str) -> None:
    """Create an empty schema, or validate an existing one, without an import row."""
    try:
        database = Path(database_path).resolve()
        database.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(database, isolation_level=None, timeout=5)) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                _check_schema(connection, create=True)
                connection.commit()
            except BaseException:
                connection.rollback()
                raise
    except (sqlite3.Error, OSError):
        raise StorageError("Cannot initialize the database; check its location, permissions, and format.") from None


def import_events(input_path: Path | str, database_path: Path | str) -> dict:
    """Validate first, then save one atomic batch. First accepted identity wins.

    Rejected lines and identity conflicts do not stop valid rows. A database error
    rolls back this entire batch (including its import summary and new schema).
    """
    source = Path(input_path).resolve()
    database = Path(database_path).resolve()
    try:
        if source == database or (source.exists() and database.exists() and source.samefile(database)):
            raise StorageError("input file and database must be different files")
    except OSError:
        raise StorageError("could not check input and database locations") from None
    parsed = read_events(source)  # Fatal parsing/file limits cause no database write.
    report = {
        "validated": len(parsed.accepted), "inserted": 0, "duplicates": 0,
        "conflicts": 0, "rejected": len(parsed.rejected), "blank_lines": parsed.blank_lines,
        "errors": [{"line": error.line_number, "kind": "validation", "reason": error.reason}
                   for error in parsed.rejected],
    }
    try:
        database.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(database, isolation_level=None, timeout=5)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("BEGIN IMMEDIATE")
            try:
                _check_schema(connection, create=True)
                cursor = connection.execute(
                    "INSERT INTO imports(imported_at) VALUES (?)",
                    (datetime.now(timezone.utc).isoformat(timespec="microseconds"),),
                )
                import_id = cursor.lastrowid
                for record in parsed.accepted:
                    event = record.event
                    values = canonical_event(event)
                    canonical = json.dumps(values, sort_keys=True, separators=(",", ":"))
                    existing = connection.execute(
                        "SELECT canonical_json FROM events WHERE source = ? AND event_id = ?",
                        (event.source, event.event_id),
                    ).fetchone()
                    if existing:
                        if existing[0] == canonical:
                            report["duplicates"] += 1
                        else:
                            report["conflicts"] += 1
                            report["errors"].append({
                                "line": record.line_number, "kind": "conflict",
                                "reason": "event identity already exists with different values; original kept",
                            })
                        continue
                    connection.execute(
                        """INSERT INTO events(
                            source, event_id, timestamp_utc, source_ip, username,
                            event_type, outcome, canonical_json, original_record,
                            first_import_id, first_line_number
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (event.source, event.event_id, values["timestamp"], event.source_ip,
                         event.username, event.event_type, event.outcome, canonical,
                         record.original_record, import_id, record.line_number),
                    )
                    report["inserted"] += 1
                report["errors"].sort(key=lambda issue: issue["line"])
                connection.execute(
                    """UPDATE imports SET validated=?, inserted=?, duplicates=?, conflicts=?,
                       rejected=?, blank_lines=?, errors_json=? WHERE id=?""",
                    (report["validated"], report["inserted"], report["duplicates"],
                     report["conflicts"], report["rejected"], report["blank_lines"],
                     json.dumps(report["errors"]), import_id),
                )
                report["total_events"] = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
                report["import_id"] = import_id
                connection.commit()
            except BaseException:
                connection.rollback()
                raise
    except (sqlite3.Error, OSError):
        raise StorageError("database write failed; this import was not saved; check access, locks, and file format") from None
    return report


def database_summary(database_path: Path | str) -> dict:
    """Read counts in one snapshot; never create a missing database."""
    try:
        database = Path(database_path).resolve()
        with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True,
                                     isolation_level=None, timeout=5)) as connection:
            connection.execute("BEGIN")
            _check_schema(connection)
            events = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            imports = connection.execute("SELECT COUNT(*) FROM imports").fetchone()[0]
            return {"schema_version": connection.execute("PRAGMA user_version").fetchone()[0],
                    "total_events": events, "total_imports": imports}
    except (sqlite3.Error, OSError):
        raise StorageError("could not read a SentinelLab database; check its location, access, and file format") from None
