"""Read saved alerts and detection runs without changing the database."""
import argparse
import json
from pathlib import Path
import sys

from sentinellab.storage.alerts import alert_summary, list_history, get_alert
from sentinellab.storage.database import StorageError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read saved alert history.")
    parser.add_argument("command", choices=("summary", "list", "runs", "get"))
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--alert-id")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        if args.command == "summary":
            result = alert_summary(args.database)
        elif args.command == "get":
            result = get_alert(args.database, args.alert_id)
            if result is None:
                print(json.dumps({"error": "Saved alert not found."}))
                return 1
        else:
            result = list_history(args.database, runs=args.command == "runs", limit=args.limit, offset=args.offset)
    except StorageError as error:
        print(json.dumps({"error": str(error)}) if args.json else str(error),
              file=sys.stdout if args.json else sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0
