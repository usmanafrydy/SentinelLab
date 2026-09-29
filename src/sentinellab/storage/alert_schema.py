"""Version 2 additions. Execute only inside an explicit saving transaction."""

SCHEMA = (
    """CREATE TABLE detection_runs (
        id INTEGER PRIMARY KEY, completed_at TEXT NOT NULL,
        configurations_json TEXT NOT NULL, events_scanned INTEGER NOT NULL,
        max_event_id INTEGER NOT NULL, max_import_id INTEGER NOT NULL,
        matched_count INTEGER NOT NULL, new_count INTEGER NOT NULL,
        existing_count INTEGER NOT NULL)""",
    """CREATE TABLE saved_alerts (
        alert_id TEXT PRIMARY KEY, rule_id TEXT NOT NULL, rule_version TEXT NOT NULL,
        triggered_at TEXT NOT NULL, first_run_id INTEGER NOT NULL REFERENCES detection_runs(id),
        alert_json TEXT NOT NULL)""",
    """CREATE TABLE alert_evidence (
        alert_id TEXT NOT NULL REFERENCES saved_alerts(alert_id),
        position INTEGER NOT NULL, event_id INTEGER NOT NULL REFERENCES events(id),
        role TEXT NOT NULL, PRIMARY KEY(alert_id, position), UNIQUE(alert_id, event_id))""",
    """CREATE TABLE run_alerts (
        run_id INTEGER NOT NULL REFERENCES detection_runs(id),
        alert_id TEXT NOT NULL REFERENCES saved_alerts(alert_id), PRIMARY KEY(run_id, alert_id))""",
    "CREATE INDEX saved_alerts_time ON saved_alerts(triggered_at, alert_id)",
)


def validate_alert_schema(connection):
    for table, columns in (
        ("detection_runs", "id, completed_at, configurations_json, events_scanned, max_event_id, max_import_id, matched_count, new_count, existing_count"),
        ("saved_alerts", "alert_id, rule_id, rule_version, triggered_at, first_run_id, alert_json"),
        ("alert_evidence", "alert_id, position, event_id, role"),
        ("run_alerts", "run_id, alert_id"),
    ):
        connection.execute(f"SELECT {columns} FROM {table} LIMIT 0")


def migrate(connection):
    if connection.execute("PRAGMA user_version").fetchone()[0] == 1:
        for statement in SCHEMA:
            connection.execute(statement)
        connection.execute("PRAGMA user_version = 2")
    validate_alert_schema(connection)
