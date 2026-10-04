"""Exercise the shipped rehearsal from outside the repository directory."""
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RehearsalTests(unittest.TestCase):
    def test_complete_workflow_from_another_directory(self):
        with TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(ROOT/'scripts/rehearse.py')],
                                    cwd=folder, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['status'], 'passed')
            self.assertEqual(len(report['checks']), 7)
            self.assertNotIn('password', report)
            self.assertEqual(list(Path(folder).iterdir()), [])
