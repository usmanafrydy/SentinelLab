import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from sentinellab.evaluation import EvaluationError, confusion_class, evaluate, load_manifest, metrics

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'data/evaluation/day15/manifest.json'


class EvaluationTests(unittest.TestCase):
    def test_confusion_classes(self):
        for intent, predicted, expected in [('malicious', True, 'TP'), ('malicious', False, 'FN'),
                                             ('benign', True, 'FP'), ('benign', False, 'TN')]:
            self.assertEqual(confusion_class(intent, predicted), expected)
        with self.assertRaises(EvaluationError):
            confusion_class('unknown', False)

    def test_metrics_and_zero_denominators(self):
        result = metrics({'TP': 2, 'FP': 1, 'TN': 3, 'FN': 4})
        self.assertEqual(result['precision']['value'], 2/3)
        self.assertEqual(result['recall']['value'], 1/3)
        self.assertEqual(result['accuracy']['value'], 0.5)
        self.assertEqual(result['specificity']['value'], 0.75)
        self.assertTrue(all(v['value'] is None for v in metrics(dict.fromkeys(('TP','FP','TN','FN'),0)).values()))

    def test_bundled_corpus_repeatable_and_honest(self):
        first = evaluate(MANIFEST)
        self.assertEqual(first, evaluate(MANIFEST))
        self.assertEqual(first['scenario_count'], 12)
        self.assertEqual(first['confusion'], {'TP':3, 'FP':3, 'TN':3, 'FN':3})
        self.assertEqual(first['rule_agreement_count'], 12)
        recovery = next(x for x in first['scenarios'] if x['id']=='owner_recovery')
        self.assertEqual(recovery['observed_rules'], ['R1','R3'])
        self.assertEqual(recovery['classification'], 'FP')
        self.assertGreater(recovery['alert_count'], 1)

    def fixture(self, folder):
        data = json.loads(MANIFEST.read_text())
        data['scenarios'] = [data['scenarios'][0]]
        item = data['scenarios'][0]
        (folder/item['file']).write_bytes((MANIFEST.parent/item['file']).read_bytes())
        path = folder/'manifest.json'
        path.write_text(json.dumps(data))
        return path, data

    def test_manifest_validation(self):
        with TemporaryDirectory() as temp:
            path, original = self.fixture(Path(temp))
            for field, value in [('intent','unknown'), ('file','../other.jsonl'),
                                 ('expected_rules',['R9']), ('expected_rules',['R1','R1']),
                                 ('id','bad/id'), ('rationale','')]:
                data = json.loads(json.dumps(original))
                data['scenarios'][0][field] = value
                path.write_text(json.dumps(data))
                with self.subTest(field=field, value=value), self.assertRaises(EvaluationError):
                    load_manifest(path)
            path.write_text('{"version":1,"version":1,"scenarios":[]}')
            with self.assertRaises(EvaluationError): load_manifest(path)
            original['scenarios'] *= 2
            path.write_text(json.dumps(original))
            with self.assertRaises(EvaluationError): load_manifest(path)

    def test_rejected_or_duplicate_records_abort(self):
        with TemporaryDirectory() as temp:
            path, data = self.fixture(Path(temp))
            source = path.parent/data['scenarios'][0]['file']
            original = source.read_bytes()
            for extra in [b'not json\n', original.splitlines(keepends=True)[0], b'\n']:
                source.write_bytes(original + extra)
                with self.assertRaises(EvaluationError): evaluate(path)

    def test_oversized_input_aborts(self):
        with TemporaryDirectory() as temp:
            path, data = self.fixture(Path(temp))
            (path.parent/data['scenarios'][0]['file']).write_bytes(b' ' * (2*1024*1024+1))
            with self.assertRaises(EvaluationError): evaluate(path)

    def test_temporary_database_is_removed_on_detection_failure(self):
        paths = []
        def fail(database, rule):
            paths.append(database)
            self.assertTrue(database.exists())
            raise EvaluationError('simulated failure')
        with patch('sentinellab.evaluation.detect', side_effect=fail):
            with self.assertRaises(EvaluationError): evaluate(MANIFEST)
        self.assertTrue(paths)
        self.assertTrue(all(not p.parent.exists() for p in paths))

    def test_cli_mismatch_and_invalid_input(self):
        with TemporaryDirectory() as temp:
            path, data = self.fixture(Path(temp))
            data['scenarios'][0]['expected_rules'] = ['R1']
            path.write_text(json.dumps(data))
            run = subprocess.run([sys.executable, str(ROOT/'scripts/evaluate.py'), '--manifest', str(path)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertEqual(json.loads(run.stdout)['rule_agreement_count'], 0)
            path.write_text('{}')
            run = subprocess.run([sys.executable, str(ROOT/'scripts/evaluate.py'), '--manifest', str(path)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stdout, '')

    def test_cli_success(self):
        run = subprocess.run([sys.executable, str(ROOT/'scripts/evaluate.py')], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['scenario_count'], 12)


if __name__ == '__main__': unittest.main()
