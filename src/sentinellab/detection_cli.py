"""Read-only detection previews with an explicit atomic --save option."""
import argparse
import json
from pathlib import Path
import sys

from sentinellab.detection.engine import detect
from sentinellab.storage.database import StorageError
from sentinellab.storage.alerts import save_detection


def main(argv=None):
    parser = argparse.ArgumentParser(description="Preview detection; --save explicitly stores results and upgrades schema v1 to v2.")
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--save", action="store_true", help="Save one atomic run with deduplicated alerts.")
    parser.add_argument("--rule", choices=("R1", "R2", "R3", "all"), default="all")
    args = parser.parse_args(argv)
    try:
        report = save_detection(args.database, args.rule) if args.save else detect(args.database, args.rule)
    except StorageError as error:
        if args.json:
            print(json.dumps({"error": str(error)}))
        else:
            print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    elif args.save:
        print(f"Saved run {report['run_id']}: {report['new_alerts']} new alerts, {report['existing_alerts']} already saved; {report['total_saved_alerts']} total saved alerts.")
        print("Alerts show suspicious patterns; investigate before concluding compromise.")
    else:
        print(f"{', '.join(report['rules_evaluated'])} preview: {report['alert_count']} alerts from {report['events_scanned']} stored events.")
        for alert in report["alerts"]:
            print(json.dumps(alert, indent=2, ensure_ascii=True))
        print("Read-only preview: alerts were not saved. Investigate patterns; no compromise is confirmed.")
    return 0
