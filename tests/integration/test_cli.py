import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_events.py"


class CommandTests(unittest.TestCase):
    def invoke(self, path, cwd=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--json"],
            capture_output=True, text=True, cwd=cwd, timeout=10,
        )

    def test_sample_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.invoke(ROOT / "data/samples/day01_login_events.jsonl", cwd=folder)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout),
                         {"accepted": 3, "rejected": 0, "blank_lines": 0, "errors": []})

    def test_rejected_input_returns_exit_one_without_leaking_contents(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.jsonl"
            path.write_text("SECRET-EXAMPLE-invalid-json\n", encoding="utf-8")
            result = self.invoke(path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["rejected"], 1)
        self.assertNotIn("SECRET-EXAMPLE", result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_file_returns_exit_two(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.invoke(Path(folder) / "absent.jsonl")
        self.assertEqual(result.returncode, 2)
        self.assertIn("error", json.loads(result.stdout))
        self.assertNotIn("Traceback", result.stderr)
