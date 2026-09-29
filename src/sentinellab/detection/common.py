"""Bounded snapshots and evidence identities shared by batch detectors."""
from datetime import datetime, timedelta
import hashlib
import json

from sentinellab.storage.database import StorageError
from sentinellab.storage.search import _reader

MAX_DETECTION_EVENTS = 10_000
MAX_EVIDENCE_REFERENCES = 100_000


def utc_time(value):
    try:
        moment = datetime.fromisoformat(value)
        if moment.utcoffset() != timedelta(0) or moment.isoformat(timespec="microseconds") != value:
            raise ValueError
        return moment
    except (TypeError, ValueError):
        raise StorageError("Stored event time is not valid normalized UTC; detection stopped.") from None


def load_snapshot(database_path, limit=MAX_DETECTION_EVENTS):
    with _reader(database_path) as connection:
        rows = connection.execute(
            "SELECT id, source, event_id, timestamp_utc, username, source_ip, event_type, outcome "
            "FROM events ORDER BY timestamp_utc, source, event_id LIMIT ?", (limit + 1,),
        ).fetchall()
    if len(rows) > limit:
        raise StorageError(f"Detection supports at most {limit} stored events; no partial results were produced.")
    for row in rows:
        utc_time(row["timestamp_utc"])
    return rows


class EvidenceBudget:
    def __init__(self, maximum=MAX_EVIDENCE_REFERENCES):
        self.remaining = maximum

    def consume(self, count):
        if count > self.remaining:
            raise StorageError("Detection evidence limit exceeded; no partial results were produced.")
        self.remaining -= count


def reference(row):
    return {"internal_id": row["id"], "source": row["source"], "event_id": row["event_id"],
            "timestamp_utc": row["timestamp_utc"]}


def alert_identity(rule_id, parameters, group, evidence):
    identity = {"rule_id": rule_id, "rule_version": "1.0.0", "parameters": parameters,
                "group": group,
                "evidence": [{k: v for k, v in ref.items() if k != "internal_id"} for ref in evidence]}
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return rule_id + "-" + digest
