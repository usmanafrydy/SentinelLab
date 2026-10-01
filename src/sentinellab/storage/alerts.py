"""Atomic saved detections, immutable evidence, and read-only history."""
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3

from sentinellab.detection.common import read_snapshot
from sentinellab.detection.engine import evaluate_snapshot, validate_rule
from sentinellab.detection import r1, r2, r3
from sentinellab.storage.alert_schema import migrate
from sentinellab.storage.database import StorageError, _check_schema
from sentinellab.storage.search import _reader, _integer, MAX_LIMIT, MAX_OFFSET


def save_detection(database_path, rule="all"):
    """Explicitly upgrade an existing v1 database and save one complete run."""
    validate_rule(rule)
    try:
        uri = Path(database_path).resolve().as_uri() + "?mode=rw"
        with closing(sqlite3.connect(uri, uri=True, isolation_level=None, timeout=5)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("BEGIN IMMEDIATE")
            try:
                _check_schema(conn)
                migrate(conn)
                report = evaluate_snapshot(read_snapshot(conn), rule)
                configurations = [{"rule_id": name, "rule_version": "1.0.0",
                                   "threshold": module.THRESHOLD, "window_seconds": module.WINDOW_SECONDS}
                                  for name, module in (("R1", r1), ("R2", r2), ("R3", r3))
                                  if name in report["rules_evaluated"]]
                cursor = conn.execute(
                    "INSERT INTO detection_runs(completed_at, configurations_json, events_scanned, "
                    "max_event_id, max_import_id, matched_count, new_count, existing_count) "
                    "VALUES (?, ?, ?, (SELECT COALESCE(MAX(id),0) FROM events), "
                    "(SELECT COALESCE(MAX(id),0) FROM imports), ?, 0, 0)",
                    (datetime.now(timezone.utc).isoformat(timespec="microseconds"),
                     json.dumps(configurations), report["events_scanned"], report["alert_count"]))
                run_id, new_count = cursor.lastrowid, 0
                for alert in report["alerts"]:
                    encoded = json.dumps(alert, sort_keys=True, separators=(",", ":"))
                    existing = conn.execute("SELECT alert_json FROM saved_alerts WHERE alert_id=?",
                                            (alert["alert_id"],)).fetchone()
                    if existing is not None:
                        if existing[0] != encoded:
                            raise StorageError("Saved alert identity conflicts with its evidence; run was not saved.")
                    else:
                        conn.execute("INSERT INTO saved_alerts VALUES (?, ?, ?, ?, ?, ?)",
                                     (alert["alert_id"], alert["rule_id"], alert["rule_version"],
                                      alert["triggered_at"], run_id, encoded))
                        conn.executemany("INSERT INTO alert_evidence VALUES (?, ?, ?, ?)",
                                         [(alert["alert_id"], position, ref["internal_id"],
                                           ref.get("role", "failure"))
                                          for position, ref in enumerate(alert["evidence"])])
                        new_count += 1
                    conn.execute("INSERT INTO run_alerts VALUES (?, ?)", (run_id, alert["alert_id"]))
                existing_count = report["alert_count"] - new_count
                conn.execute("UPDATE detection_runs SET new_count=?, existing_count=?, completed_at=? WHERE id=?",
                             (new_count, existing_count,
                              datetime.now(timezone.utc).isoformat(timespec="microseconds"), run_id))
                total = conn.execute("SELECT COUNT(*) FROM saved_alerts").fetchone()[0]
                version = conn.execute("PRAGMA user_version").fetchone()[0]
                conn.commit()
            except BaseException:
                conn.rollback()
                raise
    except (sqlite3.Error, OSError):
        raise StorageError("Detection save failed; no run, alerts, or migration were saved. Check file access, locks, and schema.") from None
    return {"mode": "saved", "schema_version": version, "run_id": run_id,
            "rules_evaluated": report["rules_evaluated"], "events_scanned": report["events_scanned"],
            "alert_count": report["alert_count"], "new_alerts": new_count,
            "existing_alerts": existing_count, "total_saved_alerts": total}


def alert_summary(database_path):
    with _reader(database_path) as conn:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        return {"schema_version": version,
                "saved_alerts": conn.execute("SELECT COUNT(*) FROM saved_alerts").fetchone()[0] if version in (2, 3) else 0,
                "detection_runs": conn.execute("SELECT COUNT(*) FROM detection_runs").fetchone()[0] if version in (2, 3) else 0}


def list_history(database_path, *, runs=False, limit=50, offset=0, run_id=None):
    _integer(limit, "limit", 1, MAX_LIMIT)
    _integer(offset, "offset", 0, MAX_OFFSET)
    if run_id is not None:
        _integer(run_id, "run_id", 1, 2**63 - 1)
        if runs:
            raise StorageError("run_id filters alerts, not the run list.")
    with _reader(database_path) as conn:
        if conn.execute("PRAGMA user_version").fetchone()[0] == 1:
            return {"total": 0, "items": [], "limit": limit, "offset": offset, "next_offset": None}
        table = "detection_runs" if runs else "saved_alerts"
        columns = "*" if runs else "alert_id, rule_id, rule_version, triggered_at, first_run_id"
        order = "id DESC" if runs else "triggered_at DESC, alert_id"
        where = " WHERE alert_id IN (SELECT alert_id FROM run_alerts WHERE run_id=?)" if run_id is not None else ""
        values = [run_id] if run_id is not None else []
        total = conn.execute(f"SELECT COUNT(*) FROM {table}" + where, values).fetchone()[0]
        items = [dict(row) for row in conn.execute(
            f"SELECT {columns} FROM {table}{where} ORDER BY {order} LIMIT ? OFFSET ?", [*values, limit, offset])]
        if runs:
            for item in items:
                item["configurations"] = json.loads(item.pop("configurations_json"))
        following = offset + len(items)
        return {"total": total, "items": items, "limit": limit, "offset": offset,
                "next_offset": following if following < total and following <= MAX_OFFSET else None}


def get_alert(database_path, alert_id):
    if not isinstance(alert_id, str) or re.fullmatch(r"R[123]-[0-9a-f]{64}", alert_id) is None:
        raise StorageError("Use a full alert_id from the saved alert list.")
    with _reader(database_path) as conn:
        if conn.execute("PRAGMA user_version").fetchone()[0] == 1:
            return None
        row = conn.execute("SELECT alert_json, first_run_id FROM saved_alerts WHERE alert_id=?", (alert_id,)).fetchone()
        if row is None:
            return None
        return {"first_run_id": row[1], "alert": json.loads(row[0])}


def get_alert_page(database_path, alert_id, *, limit=25, offset=0):
    """Return a bounded evidence page from one immutable saved snapshot."""
    _integer(limit, "limit", 1, MAX_LIMIT)
    _integer(offset, "offset", 0, MAX_OFFSET)
    result = get_alert(database_path, alert_id)
    if result is None:
        return None
    alert = result["alert"]
    evidence = alert.pop("evidence")
    # R2 account names are available in paged evidence; avoid another unbounded list.
    alert.pop("usernames", None)
    items = evidence[offset:offset + limit]
    following = offset + len(items)
    result["evidence"] = {"total": len(evidence), "items": items, "limit": limit, "offset": offset,
                          "next_offset": following if following < len(evidence) and following <= MAX_OFFSET else None}
    return result
