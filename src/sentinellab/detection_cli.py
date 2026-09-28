"""CLI for explicit, read-only detection previews."""
import argparse
import json
from pathlib import Path
import sys

from sentinellab.detection.r1 import detect_r1
from sentinellab.storage.database import StorageError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Preview R1 alerts from stored events; no writes.")
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = detect_r1(args.database)
    except StorageError as error:
        if args.json:
            print(json.dumps({"error": str(error)}))
        else:
            print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        print(f"R1 preview: {report['alert_count']} alerts from {report['events_scanned']} stored events.")
        for alert in report["alerts"]:
            print(json.dumps(alert, indent=2, ensure_ascii=True))
        print("Read-only preview: alerts were not saved. Investigate patterns; no compromise is confirmed.")
    return 0
