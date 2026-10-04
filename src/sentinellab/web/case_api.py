"""Bounded HTTP case contracts over the existing investigation services."""
import json
import re
from urllib.parse import parse_qs

from sentinellab.storage.cases import create_case, add_note, change_state, get_case, list_cases, case_history

WRITE_PATH = re.compile(r'/api/cases/([1-9][0-9]{0,18})/(notes|state)')
READ_PATH = re.compile(r'/api/cases/([1-9][0-9]{0,18})(/history)?')


def wire(value):
    """Avoid rounding SQLite 64-bit identifiers/revisions in JavaScript."""
    if isinstance(value, dict):
        return {key: str(item) if key in ('id', 'case_id', 'revision') else wire(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [wire(item) for item in value]
    return value


def read_case_request(database, path, query):
    match = READ_PATH.fullmatch(path)
    if path != '/api/cases' and match is None:
        return 404, {'error': 'Case page not found.'}
    permitted = {'limit', 'offset', 'status'} if path == '/api/cases' else {'limit', 'offset'} if match[2] else set()
    params = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=3)
    if set(params) - permitted or any(len(values) != 1 for values in params.values()):
        raise ValueError
    options = {key: values[0] if key == 'status' else int(values[0]) for key, values in params.items()}
    if path == '/api/cases':
        result = list_cases(database, **options)
    elif match[2]:
        result = case_history(database, int(match[1]), **options)
    else:
        result = get_case(database, int(match[1]))
    return (404, {'error': 'Case not found.'}) if result is None else (200, wire(result))


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError


def write_case_request(database, path, content, *, author=None):
    body = json.loads(content.decode('utf-8'), object_pairs_hook=_pairs, parse_constant=_invalid_constant)
    match = WRITE_PATH.fullmatch(path)
    action = 'create' if path == '/api/cases' else match[2]
    expected = {'alert_id', 'title', 'author'} if action == 'create' else (
        {'text', 'author'} if action == 'notes' else {'status', 'disposition', 'reason', 'author', 'expected_revision'})
    if type(body) is not dict or set(body) != expected or any(type(v) is not str for v in body.values()):
        raise ValueError
    if author is not None:
        body['author'] = author
    if action == 'create':
        result = create_case(database, **body)
    elif action == 'notes':
        result = add_note(database, int(match[1]), **body)
    else:
        if re.fullmatch(r'[1-9][0-9]{0,18}', body['expected_revision']) is None:
            raise ValueError
        body['expected_revision'] = int(body['expected_revision'])
        result = change_state(database, int(match[1]), **body)
    return wire(result)
