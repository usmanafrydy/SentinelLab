"""Version 3 case tables, created only inside an explicit case transaction."""

SCHEMA = (
    """CREATE TABLE investigations (
        id INTEGER PRIMARY KEY,
        alert_id TEXT NOT NULL UNIQUE REFERENCES saved_alerts(alert_id),
        title TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('open','in_progress','closed')),
        disposition TEXT NOT NULL CHECK(disposition IN ('undecided','benign','suspicious','confirmed_compromise')),
        revision INTEGER NOT NULL CHECK(revision > 0),
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        CHECK(status != 'closed' OR disposition != 'undecided'))""",
    """CREATE TABLE investigation_actions (
        id INTEGER PRIMARY KEY,
        case_id INTEGER NOT NULL REFERENCES investigations(id),
        revision INTEGER NOT NULL CHECK(revision > 0),
        kind TEXT NOT NULL CHECK(kind IN ('created','note','state_changed')),
        occurred_at TEXT NOT NULL, author TEXT NOT NULL, text TEXT NOT NULL,
        before_json TEXT, after_json TEXT NOT NULL,
        UNIQUE(case_id, revision))""",
)


def validate_case_schema(connection):
    connection.execute("SELECT id, alert_id, title, status, disposition, revision, created_at, updated_at "
                       "FROM investigations LIMIT 0")
    connection.execute("SELECT id, case_id, revision, kind, occurred_at, author, text, before_json, after_json "
                       "FROM investigation_actions LIMIT 0")


def migrate(connection):
    if connection.execute("PRAGMA user_version").fetchone()[0] == 2:
        for statement in SCHEMA:
            connection.execute(statement)
        connection.execute("PRAGMA user_version = 3")
    validate_case_schema(connection)
