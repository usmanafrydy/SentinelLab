"""Command-line import and read-only database summary."""
import argparse
import json
from pathlib import Path
import sys

from sentinellab.ingestion.reader import InputFileError
from sentinellab.storage.database import StorageError, database_summary, import_events
from sentinellab.storage.search import get_event, search_events


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Save login events or inspect database counts.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    importer = subcommands.add_parser("import", help="validate and save records")
    importer.add_argument("file", type=Path)
    summary = subcommands.add_parser("summary", help="read counts without modifying the database")
    search = subcommands.add_parser("search", help="find saved events without changing them")
    for option in ("username", "source-ip", "outcome", "start", "end"):
        search.add_argument("--" + option)
    search.add_argument("--limit", type=int, default=50)
    search.add_argument("--offset", type=int, default=0)
    get = subcommands.add_parser("get", help="open original evidence by internal event ID")
    get.add_argument("id", type=int)
    for command in (importer, summary, search, get):
        command.add_argument("--database", required=True, type=Path, help="SQLite database file")
        command.add_argument("--json", action="store_true", help="machine-readable result")
    args = parser.parse_args(argv)
    try:
        if args.command == "import":
            result = import_events(args.file, args.database)
        elif args.command == "summary":
            result = database_summary(args.database)
        elif args.command == "search":
            result = search_events(args.database, username=args.username, source_ip=args.source_ip,
                                   outcome=args.outcome, start=args.start, end=args.end,
                                   limit=args.limit, offset=args.offset)
        else:
            event = get_event(args.database, args.id)
            result = {"event": event}
    except (InputFileError, StorageError) as error:
        if args.json:
            print(json.dumps({"error": str(error)}))
        else:
            print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for name, value in result.items():
            if name != "errors":
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, indent=2, ensure_ascii=True)
                print(f"{name.replace('_', ' ').capitalize()}: {value}")
        for issue in result.get("errors", []):
            print(f"Line {issue['line']} ({issue['kind']}): {issue['reason']}")
        print("No attack detection or security alerts were performed.")
    if args.command == "get" and result["event"] is None:
        return 1
    return 1 if result.get("rejected", 0) or result.get("conflicts", 0) else 0
