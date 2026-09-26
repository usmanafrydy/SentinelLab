"""Command-line import and read-only database summary."""
import argparse
import json
from pathlib import Path
import sys

from sentinellab.ingestion.reader import InputFileError
from sentinellab.storage.database import StorageError, database_summary, import_events


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Save login events or inspect database counts.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    importer = subcommands.add_parser("import", help="validate and save records")
    importer.add_argument("file", type=Path)
    summary = subcommands.add_parser("summary", help="read counts without modifying the database")
    for command in (importer, summary):
        command.add_argument("--database", required=True, type=Path, help="SQLite database file")
        command.add_argument("--json", action="store_true", help="machine-readable result")
    args = parser.parse_args(argv)
    try:
        if args.command == "import":
            result = import_events(args.file, args.database)
        else:
            result = database_summary(args.database)
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
                print(f"{name.replace('_', ' ').capitalize()}: {value}")
        for issue in result.get("errors", []):
            print(f"Line {issue['line']} ({issue['kind']}): {issue['reason']}")
        print("No attack detection or security alerts were performed.")
    return 1 if result.get("rejected", 0) or result.get("conflicts", 0) else 0
