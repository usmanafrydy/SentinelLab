"""Read-only, bounded event search and original evidence retrieval."""
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from ipaddress import ip_address
from pathlib import Path
import sqlite3

from sentinellab.ingestion.reader import TIMESTAMP_PATTERN
from sentinellab.storage.database import StorageError, _check_schema

MAX_LIMIT = 200
MAX_OFFSET = 1_000_000
COLUMNS = "id, source, event_id, timestamp_utc, source_ip, username, event_type, outcome"


@contextmanager
def _reader(path):
    try:
        uri = Path(path).resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, isolation_level=None, timeout=5)) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("BEGIN")
            _check_schema(connection)
            yield connection
    except (sqlite3.Error, OSError):
        raise StorageError("Cannot read the event database; check the file, schema, and permissions.") from None


def _integer(value, name, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise StorageError(f"{name} must be an integer from {minimum} to {maximum}.")


def _timestamp(value):
    if not isinstance(value, str) or len(value) > 32 or not TIMESTAMP_PATTERN.fullmatch(value):
        raise StorageError("Time filters need a date, time, seconds, and Z or an explicit offset.")
    try:
        return datetime.fromisoformat(value).astimezone(timezone.utc).isoformat(timespec="microseconds")
    except (ValueError, OverflowError):
        raise StorageError("Time filter contains an invalid or unsupported date/time.") from None


def search_events(database_path, *, username=None, source_ip=None, outcome=None,
                  start=None, end=None, limit=50, offset=0):
    """Exact filters combined with AND; time interval includes start, excludes end."""
    _integer(limit, "limit", 1, MAX_LIMIT)
    _integer(offset, "offset", 0, MAX_OFFSET)
    clauses, values = [], []
    if username is not None:
        if (not isinstance(username, str) or not username.strip() or len(username) > 128
                or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in username)):
            raise StorageError("username must contain 1 to 128 supported characters and not be blank.")
        clauses.append("username = ?")
        values.append(username)
    if source_ip is not None:
        try:
            if not isinstance(source_ip, str) or len(source_ip) > 45 or "%" in source_ip:
                raise ValueError
            address = str(ip_address(source_ip))
        except ValueError:
            raise StorageError("source_ip must be an IPv4 or IPv6 address without a zone ID.") from None
        clauses.append("source_ip = ?")
        values.append(address)
    if outcome is not None:
        if outcome not in ("success", "failure"):
            raise StorageError("outcome must be success or failure.")
        clauses.append("outcome = ?")
        values.append(outcome)
    start_utc = _timestamp(start) if start is not None else None
    end_utc = _timestamp(end) if end is not None else None
    if start_utc is not None and end_utc is not None and start_utc >= end_utc:
        raise StorageError("start must be earlier than end.")
    for value, clause in ((start_utc, "timestamp_utc >= ?"), (end_utc, "timestamp_utc < ?")):
        if value is not None:
            clauses.append(clause)
            values.append(value)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    # SQL fragments are constants; user values are always bound parameters.
    with _reader(database_path) as connection:
        total = connection.execute("SELECT COUNT(*) FROM events" + where, values).fetchone()[0]
        rows = connection.execute(
            "SELECT " + COLUMNS + " FROM events" + where
            + " ORDER BY timestamp_utc, id LIMIT ? OFFSET ?", [*values, limit, offset]).fetchall()
    events = [dict(row) for row in rows]
    next_offset = offset + len(events)
    return {"total_matches": total, "returned": len(events), "limit": limit, "offset": offset,
            "next_offset": next_offset if next_offset < total and next_offset <= MAX_OFFSET else None,
            "events": events}


def get_event(database_path, internal_id):
    """Return one event with first-import provenance, or None if absent."""
    _integer(internal_id, "id", 1, 2**63 - 1)
    with _reader(database_path) as connection:
        row = connection.execute(
            "SELECT " + COLUMNS + ", original_record, first_import_id, first_line_number"
            + " FROM events WHERE id = ?", (internal_id,)).fetchone()
    return dict(row) if row is not None else None
