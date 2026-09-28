"""R1: read-only repeated-failure preview with explicit episode grouping."""
from collections import defaultdict, deque
from datetime import datetime, timedelta
import hashlib
from itertools import groupby
import json

from sentinellab.storage.database import StorageError
from sentinellab.storage.search import _reader

RULE_ID = "R1"
RULE_VERSION = "1.0.0"
THRESHOLD = 5
WINDOW_SECONDS = 300
MAX_DETECTION_EVENTS = 10_000


def _alert(window, username, source_ip):
    evidence = [{"internal_id": row["id"], "source": row["source"], "event_id": row["event_id"],
                 "timestamp_utc": row["timestamp_utc"]} for _, row in window]
    parameters = {"threshold": THRESHOLD, "window_seconds": WINDOW_SECONDS}
    identity = {
        "rule_id": RULE_ID, "rule_version": RULE_VERSION, "parameters": parameters,
        "group": {"username": username, "source_ip": source_ip},
        "evidence": [{k: v for k, v in item.items() if k != "internal_id"} for item in evidence],
    }
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "alert_id": RULE_ID + "-" + digest,
        "rule_id": RULE_ID, "rule_version": RULE_VERSION,
        "title": "Repeated failed logins", "parameters": parameters,
        "group": identity["group"], "failure_count": len(evidence),
        "first_event_at": evidence[0]["timestamp_utc"],
        "triggered_at": evidence[-1]["timestamp_utc"],
        "reason": f"{len(evidence)} failed logins for the same username and source IP within an inclusive 300-second window. Investigate; this does not confirm compromise.",
        "evidence": evidence,
    }


def detect_r1(database_path):
    """Read one bounded snapshot; return previews without saving or modifying data."""
    with _reader(database_path) as connection:
        rows = connection.execute(
            "SELECT id, source, event_id, timestamp_utc, username, source_ip, event_type, outcome "
            "FROM events ORDER BY timestamp_utc, source, event_id LIMIT ?",
            (MAX_DETECTION_EVENTS + 1,),
        ).fetchall()
    if len(rows) > MAX_DETECTION_EVENTS:
        raise StorageError(f"Detection supports at most {MAX_DETECTION_EVENTS} stored events; no partial results were produced.")
    groups = defaultdict(list)
    for row in rows:
        if row["event_type"] == "login" and row["outcome"] == "failure":
            groups[(row["username"], row["source_ip"])].append(row)
    alerts = []
    duration = timedelta(seconds=WINDOW_SECONDS)
    for (username, source_ip), records in sorted(groups.items()):
        window = deque()
        armed = True
        for timestamp, batch in groupby(records, key=lambda row: row["timestamp_utc"]):
            try:
                moment = datetime.fromisoformat(timestamp)
                if moment.utcoffset() != timedelta(0):
                    raise ValueError
            except ValueError:
                raise StorageError("Stored event time is not valid normalized UTC; detection stopped.") from None
            # Subtract two valid dates instead of t-window to support year 0001.
            while window and moment - window[0][0] > duration:
                window.popleft()
            if len(window) < THRESHOLD:
                armed = True
            window.extend((moment, row) for row in batch)
            if armed and len(window) >= THRESHOLD:
                alerts.append(_alert(window, username, source_ip))
                armed = False
    alerts.sort(key=lambda item: (item["triggered_at"], item["group"]["username"],
                                  item["group"]["source_ip"], item["alert_id"]))
    return {"mode": "read_only_preview", "rules_evaluated": [RULE_ID],
            "events_scanned": len(rows), "alert_count": len(alerts), "alerts": alerts}
