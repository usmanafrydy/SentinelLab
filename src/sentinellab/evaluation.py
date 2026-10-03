"""Repeatable scenario evaluation through real import and detection services."""
import hashlib
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from sentinellab.detection.engine import RULES, detect
from sentinellab.ingestion.reader import MAX_FILE_BYTES
from sentinellab.storage.database import import_events


class EvaluationError(ValueError):
    """The evaluation cannot produce a complete trustworthy report."""


def _read(path, limit):
    with Path(path).open('rb') as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise EvaluationError('evaluation input exceeds its byte limit')
    return raw


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError('duplicate JSON key in manifest')
        result[key] = value
    return result


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_manifest(path):
    path = Path(path).resolve()
    raw = _read(path, 256 * 1024)
    try:
        manifest = json.loads(raw.decode('utf-8'), object_pairs_hook=_object)
    except (UnicodeError, json.JSONDecodeError):
        raise EvaluationError('manifest must be valid UTF-8 JSON') from None
    if (not isinstance(manifest, dict) or set(manifest) != {'version', 'scenarios'}
            or type(manifest['version']) is not int or manifest['version'] != 1):
        raise EvaluationError('unsupported manifest structure or version')
    scenarios = manifest['scenarios']
    if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 100:
        raise EvaluationError('manifest requires 1 to 100 scenarios')
    seen = set()
    for item in scenarios:
        if not isinstance(item, dict) or set(item) != {
                'id', 'file', 'intent', 'expected_rules', 'rationale'}:
            raise EvaluationError('invalid scenario fields')
        ident, filename = item['id'], item['file']
        if (not isinstance(ident, str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,63}', ident)
                or ident in seen):
            raise EvaluationError('invalid or duplicate scenario ID')
        seen.add(ident)
        if not isinstance(filename, str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,63}\.jsonl', filename):
            raise EvaluationError('scenario file must be a simple JSONL filename')
        if item['intent'] not in ('benign', 'malicious'):
            raise EvaluationError('intent must be benign or malicious')
        expected = item['expected_rules']
        if (not isinstance(expected, list) or any(x not in RULES for x in expected)
                or len(set(expected)) != len(expected)):
            raise EvaluationError('expected_rules must contain unique R1 R2 or R3 IDs')
        if not isinstance(item['rationale'], str) or not 1 <= len(item['rationale']) <= 2000:
            raise EvaluationError('scenario needs a short intent rationale')
        if (path.parent / filename).resolve().parent != path.parent:
            raise EvaluationError('scenario file must remain inside the manifest directory')
    return manifest, raw


def confusion_class(intent, has_alert):
    if intent not in ('benign', 'malicious') or type(has_alert) is not bool:
        raise EvaluationError('invalid scoring input')
    return ('TP' if has_alert else 'FN') if intent == 'malicious' else ('FP' if has_alert else 'TN')


def metrics(counts):
    if (set(counts) != {'TP', 'FP', 'TN', 'FN'}
            or any(type(n) is not int or n < 0 for n in counts.values())):
        raise EvaluationError('confusion counts must be nonnegative integers')
    tp, fp, tn, fn = (counts[k] for k in ('TP', 'FP', 'TN', 'FN'))
    def ratio(n, d):
        return {'numerator': n, 'denominator': d, 'value': n / d if d else None}
    return {'precision': ratio(tp, tp + fp), 'recall': ratio(tp, tp + fn),
            'specificity': ratio(tn, tn + fp), 'accuracy': ratio(tp + tn, tp + fp + tn + fn)}


def evaluate(manifest_path):
    """Fail the whole evaluation on bad input; never accepts a user database."""
    path = Path(manifest_path).resolve()
    manifest, raw = load_manifest(path)
    rows = []
    counts = dict.fromkeys(('TP', 'FP', 'TN', 'FN'), 0)
    for item in manifest['scenarios']:
        # Import precisely the bytes hashed here, not a second read of the input.
        events = _read(path.parent / item['file'], MAX_FILE_BYTES)
        with TemporaryDirectory(prefix='sentinellab-eval-') as temporary:
            folder = Path(temporary)
            source, database = folder / 'events.jsonl', folder / 'events.db'
            source.write_bytes(events)
            imported = import_events(source, database)
            if (not imported['inserted'] or any(imported[k] for k in (
                    'rejected', 'duplicates', 'conflicts', 'blank_lines'))):
                raise EvaluationError('scenario ' + item['id'] + ' did not import cleanly')
            result = detect(database, 'all')
        actual = sorted({a['rule_id'] for a in result['alerts']})
        category = confusion_class(item['intent'], bool(result['alert_count']))
        counts[category] += 1
        rows.append({**item, 'expected_rules': sorted(item['expected_rules']),
                     'events_sha256': _sha(events), 'events_scanned': result['events_scanned'],
                     'observed_rules': actual, 'alert_count': result['alert_count'],
                     'classification': category,
                     'rule_agreement': actual == sorted(item['expected_rules'])})
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    sources = sorted(package.rglob('*.py')) + [root / 'scripts/evaluate.py']
    source_hashes = {p.relative_to(root).as_posix(): _sha(p.read_bytes()) for p in sources}
    return {'report_version': 1, 'scoring_unit': 'one scenario; any alert is positive',
            'limitations': 'Authored synthetic scenarios with known rules; not blinded or real-world accuracy.',
            'manifest_sha256': _sha(raw), 'source_sha256': source_hashes,
            'scenario_count': len(rows), 'confusion': counts, 'metrics': metrics(counts),
            'rule_agreement_count': sum(row['rule_agreement'] for row in rows), 'scenarios': rows}
