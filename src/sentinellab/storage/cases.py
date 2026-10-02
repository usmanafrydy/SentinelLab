"""Local investigation state and append-only application history."""
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
import unicodedata

from sentinellab.storage.database import StorageError, _check_schema
from sentinellab.storage.case_schema import migrate
from sentinellab.storage.search import _reader, _integer, MAX_LIMIT, MAX_OFFSET

STATUSES = ('open', 'in_progress', 'closed')
DISPOSITIONS = ('undecided', 'benign', 'suspicious', 'confirmed_compromise')
MAX_ID = 2**63 - 1


class CaseConflict(StorageError):
    """A state update was based on an older case revision."""


def _text(value, name, maximum, multiline=False):
    if (not isinstance(value, str) or not 1 <= len(value) <= maximum or not value.strip()
            or any(unicodedata.category(c) in ('Cc', 'Cf', 'Cs')
                   and not (multiline and c in '\n\t') for c in value)):
        raise StorageError(f'{name} must contain 1 to {maximum} supported characters and not be blank.')
    return value.strip()


def _id(value, name='case_id'):
    _integer(value, name, 1, MAX_ID)


def _enum(value, choices, name):
    if value not in choices:
        raise StorageError(f'{name} must be one of: {", ".join(choices)}.')


def _now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')


@contextmanager
def _writer(path):
    try:
        uri = Path(path).resolve().as_uri() + '?mode=rw'
        with closing(sqlite3.connect(uri, uri=True, isolation_level=None, timeout=5)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys = ON')
            conn.execute('BEGIN IMMEDIATE')
            try:
                _check_schema(conn)
                yield conn
                conn.commit()
            except BaseException:
                conn.rollback()
                raise
    except (sqlite3.Error, OSError):
        raise StorageError('Case change failed; no changes saved. Check database access, locks, and schema.') from None


def _has_cases(conn):
    return conn.execute('PRAGMA user_version').fetchone()[0] == 3


def _case(conn, case_id):
    if not _has_cases(conn):
        return None
    row = conn.execute('SELECT * FROM investigations WHERE id=?', (case_id,)).fetchone()
    return dict(row) if row else None


def _required_case(conn, case_id):
    case = _case(conn, case_id)
    if case is None:
        raise StorageError('Case not found. Create a case from a saved alert first.')
    if case['revision'] >= MAX_ID:
        raise StorageError('Case revision limit reached; no change saved.')
    return case


def _state(case):
    return {key: case[key] for key in ('status', 'disposition', 'revision')}


def _append_action(conn, case, kind, author, text, before):
    conn.execute('INSERT INTO investigation_actions '
                 '(case_id,revision,kind,occurred_at,author,text,before_json,after_json) VALUES (?,?,?,?,?,?,?,?)',
                 (case['id'], case['revision'], kind, case['updated_at'], author, text,
                  json.dumps(before, sort_keys=True) if before is not None else None,
                  json.dumps(_state(case), sort_keys=True)))


def create_case(path, alert_id, title, author):
    title = _text(title, 'title', 120)
    author = _text(author, 'author', 80)
    if not isinstance(alert_id, str) or re.fullmatch(r'R[123]-[0-9a-f]{64}', alert_id) is None:
        raise StorageError('Use a full saved alert ID.')
    with _writer(path) as conn:
        version = conn.execute('PRAGMA user_version').fetchone()[0]
        if version == 1 or conn.execute('SELECT 1 FROM saved_alerts WHERE alert_id=?', (alert_id,)).fetchone() is None:
            raise StorageError('Saved alert not found. Save detection before creating a case.')
        migrate(conn)
        row = conn.execute('SELECT * FROM investigations WHERE alert_id=?', (alert_id,)).fetchone()
        if row:
            return {'created': False, 'case': dict(row)}
        now = _now()
        cursor = conn.execute('INSERT INTO investigations '
                              '(alert_id,title,status,disposition,revision,created_at,updated_at) '
                              "VALUES (?,?,'open','undecided',1,?,?)", (alert_id, title, now, now))
        case = _case(conn, cursor.lastrowid)
        _append_action(conn, case, 'created', author, title, None)
    return {'created': True, 'case': case}


def add_note(path, case_id, text, author):
    _id(case_id)
    text = _text(text, 'note', 4000, True)
    author = _text(author, 'author', 80)
    with _writer(path) as conn:
        case = _required_case(conn, case_id)
        before = _state(case)
        case.update(revision=case['revision'] + 1, updated_at=_now())
        conn.execute('UPDATE investigations SET revision=?,updated_at=? WHERE id=?',
                     (case['revision'], case['updated_at'], case_id))
        _append_action(conn, case, 'note', author, text, before)
    return case


def change_state(path, case_id, status, disposition, reason, author, expected_revision):
    _id(case_id)
    _id(expected_revision, 'expected_revision')
    _enum(status, STATUSES, 'status')
    _enum(disposition, DISPOSITIONS, 'disposition')
    reason = _text(reason, 'reason', 1000, True)
    author = _text(author, 'author', 80)
    if status == 'closed' and disposition == 'undecided':
        raise StorageError('Choose a conclusion before closing the case.')
    with _writer(path) as conn:
        case = _required_case(conn, case_id)
        if case['revision'] != expected_revision:
            raise CaseConflict('Case changed since you read it. Refresh the case and use its current revision.')
        if (status, disposition) == (case['status'], case['disposition']):
            raise StorageError('Status and disposition are unchanged; add a note instead.')
        if case['status'] == 'closed' and status != 'closed' and (status, disposition) != ('in_progress', 'undecided'):
            raise StorageError('Reopen a closed case as in_progress with disposition undecided.')
        before = _state(case)
        case.update(status=status, disposition=disposition, revision=case['revision'] + 1, updated_at=_now())
        conn.execute('UPDATE investigations SET status=?,disposition=?,revision=?,updated_at=? WHERE id=?',
                     (status, disposition, case['revision'], case['updated_at'], case_id))
        _append_action(conn, case, 'state_changed', author, reason, before)
    return case


def get_case(path, case_id):
    _id(case_id)
    with _reader(path) as conn:
        return _case(conn, case_id)


def _page(conn, table, where, values, order, limit, offset):
    total = conn.execute(f'SELECT COUNT(*) FROM {table}{where}', values).fetchone()[0]
    items = [dict(row) for row in conn.execute(
        f'SELECT * FROM {table}{where} ORDER BY {order} LIMIT ? OFFSET ?', (*values, limit, offset))]
    next_offset = offset + len(items)
    return {'total': total, 'items': items, 'limit': limit, 'offset': offset,
            'next_offset': next_offset if next_offset < total and next_offset <= MAX_OFFSET else None}


def list_cases(path, *, status=None, limit=50, offset=0):
    _integer(limit, 'limit', 1, MAX_LIMIT)
    _integer(offset, 'offset', 0, MAX_OFFSET)
    if status is not None:
        _enum(status, STATUSES, 'status')
    with _reader(path) as conn:
        if not _has_cases(conn):
            return {'total': 0, 'items': [], 'limit': limit, 'offset': offset, 'next_offset': None}
        return _page(conn, 'investigations', ' WHERE status=?' if status else '',
                     (status,) if status else (), 'id DESC', limit, offset)


def case_history(path, case_id, *, limit=50, offset=0):
    _id(case_id)
    _integer(limit, 'limit', 1, MAX_LIMIT)
    _integer(offset, 'offset', 0, MAX_OFFSET)
    with _reader(path) as conn:
        if _case(conn, case_id) is None:
            return None
        result = _page(conn, 'investigation_actions', ' WHERE case_id=?', (case_id,), 'revision', limit, offset)
        for item in result['items']:
            before = item.pop('before_json')
            item['before'] = json.loads(before) if before else None
            item['after'] = json.loads(item.pop('after_json'))
        return result
