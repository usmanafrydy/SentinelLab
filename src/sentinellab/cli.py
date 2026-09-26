"""Small command-line interface for the Day 2 reader."""

import argparse
import json
from pathlib import Path
import sys

from sentinellab.ingestion.reader import InputFileError, read_events


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check SentinelLab login records; no attack detection yet.")
    parser.add_argument("file", type=Path, help="UTF-8 JSON Lines input file")
    parser.add_argument("--json", action="store_true", help="print a machine-readable summary")
    args = parser.parse_args(argv)
    try:
        result = read_events(args.file)
    except InputFileError as error:
        if args.json:
            print(json.dumps({"error": str(error)}))
        else:
            print(f"Could not check file: {error}", file=sys.stderr)
        return 2
    summary = result.summary()
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Accepted: {summary['accepted']}")
        print(f"Rejected: {summary['rejected']}")
        print(f"Blank lines skipped: {summary['blank_lines']}")
        for issue in result.rejected:
            print(f"Line {issue.line_number}: {issue.reason}")
        print("Format check only. No database writes or security alerts were created.")
    return 1 if result.rejected else 0
