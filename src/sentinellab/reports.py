"""Bounded, read-only investigation snapshots and inert export formats."""
from datetime import datetime, timezone
import json
import re

from sentinellab.storage.database import StorageError
from sentinellab.storage.cases import CaseConflict
from sentinellab.storage.search import _reader, _integer

MAX_ROWS = 1000
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_OUTPUT_BYTES = 16 * 1024 * 1024
LIMITATIONS = [
    'An alert is a lead for investigation, not proof that an account was hacked.',
    'The conclusion is an analyst judgment; export does not confirm or change it.',
    'Historical and CLI author labels may be self-declared. Stored history is not tamper-proof.',
    'This is one database snapshot. Later changes and unsaved browser drafts are not included.',
    'Times are UTC. Original records are accepted record text, not a byte copy of the source file.',
    'This report contains original evidence and notes. Review for sensitive data before sharing.',
    'No signature, encryption, redaction, or forensic chain-of-custody guarantee is provided.',
]
ID_FIELDS = {'id', 'case_id', 'internal_id', 'first_import_id', 'first_run_id',
             'max_event_id', 'max_import_id', 'revision'}


def _rows(conn, query, params, columns, budget, maximum=MAX_ROWS):
    # Only constant queries/column names from this module enter SQL fragments.
    sizes = '+'.join(f'COALESCE(length(CAST({c} AS BLOB)),0)' for c in columns.split(', '))
    count, size = conn.execute(
        f'SELECT COUNT(*), COALESCE(SUM({sizes}),0) FROM ({query} LIMIT ?)',
        (*params, maximum + 1)).fetchone()
    budget[0] += size
    if count > maximum or budget[0] > MAX_SOURCE_BYTES:
        raise StorageError('Report exceeds the 1,000-row or 8 MiB source limit; no partial export was made.')
    return [dict(row) for row in conn.execute(query + ' LIMIT ?', (*params, maximum))]


def _string_ids(value):
    if isinstance(value, dict):
        return {key: str(item) if key in ID_FIELDS and type(item) is int else _string_ids(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [_string_ids(item) for item in value]
    return value


def build_report(database, case_id, *, expected_revision=None):
    """All SELECTs share one snapshot; reads never migrate a schema."""
    _integer(case_id, 'case_id', 1, 2**63 - 1)
    if expected_revision is not None:
        _integer(expected_revision, 'revision', 1, 2**63 - 1)
    budget = [0]
    with _reader(database) as conn:
        if conn.execute('PRAGMA user_version').fetchone()[0] != 3:
            return None
        fields = 'id, alert_id, title, status, disposition, revision, created_at, updated_at'
        cases = _rows(conn, f'SELECT {fields} FROM investigations WHERE id=?', (case_id,), fields, budget, 1)
        if not cases:
            return None
        case = cases[0]
        if expected_revision is not None and case['revision'] != expected_revision:
            raise CaseConflict('Case changed. Refresh selected case, review it, and download again. Your draft is kept.')
        fields = 'alert_id, rule_id, rule_version, triggered_at, first_run_id, alert_json'
        alerts = _rows(conn, f'SELECT {fields} FROM saved_alerts WHERE alert_id=?',
                       (case['alert_id'],), fields, budget, 1)
        if not alerts:
            raise StorageError('Linked alert is missing; report was not exported.')
        saved = alerts[0]
        fields = 'id, completed_at, configurations_json, events_scanned, max_event_id, max_import_id, matched_count, new_count, existing_count'
        runs = _rows(conn, f'SELECT {fields} FROM detection_runs WHERE id=?',
                     (saved['first_run_id'],), fields, budget, 1)
        fields = 'id, case_id, revision, kind, occurred_at, author, text, before_json, after_json'
        actions = _rows(conn, f'SELECT {fields} FROM investigation_actions WHERE case_id=? ORDER BY revision',
                        (case_id,), fields, budget)
        fields = 'position, role, internal_id, source, event_id, timestamp_utc, source_ip, username, event_type, outcome, original_record, first_import_id, first_line_number, imported_at'
        evidence = _rows(conn,
            'SELECT a.position, a.role, e.id AS internal_id, e.source, e.event_id, e.timestamp_utc, '
            'e.source_ip, e.username, e.event_type, e.outcome, e.original_record, e.first_import_id, '
            'e.first_line_number, i.imported_at FROM alert_evidence a '
            'LEFT JOIN events e ON e.id=a.event_id LEFT JOIN imports i ON i.id=e.first_import_id '
            'WHERE a.alert_id=? ORDER BY a.position', (case['alert_id'],), fields, budget)
        try:
            alert = json.loads(saved['alert_json'])
            if not runs or any(alert[k] != saved[k] for k in ('alert_id', 'rule_id', 'rule_version', 'triggered_at')):
                raise ValueError
            run = runs[0]
            run['configurations'] = json.loads(run.pop('configurations_json'))
            if not actions or len(actions) != case['revision']:
                raise ValueError
            previous = None
            for revision, action in enumerate(actions, 1):
                before = action.pop('before_json')
                action['before'] = json.loads(before) if before else None
                action['after'] = json.loads(action.pop('after_json'))
                if action['revision'] != revision or action['before'] != previous or action['after']['revision'] != revision:
                    raise ValueError
                previous = action['after']
            if previous != {k: case[k] for k in ('status', 'disposition', 'revision')}:
                raise ValueError
            if not evidence or len(evidence) != len(alert['evidence']):
                raise ValueError
            for position, (row, ref) in enumerate(zip(evidence, alert['evidence'])):
                if (row['position'] != position or row['internal_id'] is None or row['imported_at'] is None
                        or row['role'] != ref.get('role', 'failure')
                        or any(row[key] != ref[key] for key in ('internal_id', 'source', 'event_id', 'timestamp_utc'))):
                    raise ValueError
        except (ValueError, KeyError, TypeError, RecursionError):
            raise StorageError('Stored report links or history are inconsistent; no partial export was made.') from None
        return _string_ids({'report_version': '1.0',
            'exported_at': datetime.now(timezone.utc).isoformat(timespec='microseconds'),
            'case': case, 'alert': alert, 'first_detection_run': run,
            'actions': actions, 'evidence': evidence, 'limitations': LIMITATIONS.copy()})


def render_report(report, format):
    if format not in ('json', 'markdown'):
        raise StorageError('Choose json or markdown for the report.')
    if format == 'json':
        chunks = json.JSONEncoder(ensure_ascii=True, indent=2, allow_nan=False).iterencode(report)
    else:
        def markdown():
            yield '# SentinelLab investigation report\n\nSaved work only. Review sensitive content before sharing.\n\n'
            for heading, value in (
                ('Report details', {k: report[k] for k in ('report_version', 'exported_at')}),
                ('Case and analyst conclusion', report['case']), ('Saved alert and rule details', report['alert']),
                ('First detection run', report['first_detection_run']), ('Complete action history', report['actions']),
                ('Linked original evidence', report['evidence']), ('Limitations', report['limitations'])):
                encoded = json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False)
                fence = '`' * max(3, 1 + max((len(m[0]) for m in re.finditer(r'`+', encoded)), default=0))
                yield f'## {heading}\n\n{fence}json\n{encoded}\n{fence}\n\n'
        chunks = markdown()
    data = bytearray()
    for chunk in chunks:
        encoded = chunk.encode('utf-8')
        if len(data) + len(encoded) + 1 > MAX_OUTPUT_BYTES:
            raise StorageError('Encoded report exceeds 16 MiB; no partial export was made.')
        data.extend(encoded)
    data.extend(b'\n')
    return bytes(data)


def report_filename(case_id, revision, format):
    return f'sentinellab-case-{int(case_id)}-rev-{int(revision)}.' + ('json' if format == 'json' else 'md')
