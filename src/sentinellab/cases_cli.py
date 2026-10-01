"""Explicit local case commands; author labels are not authenticated users."""
import argparse
import json
from pathlib import Path

from sentinellab.storage.database import StorageError
from sentinellab.storage.cases import (
    STATUSES, DISPOSITIONS, create_case, add_note, change_state,
    get_case, list_cases, case_history,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Keep local investigation notes and conclusions with history.')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('create', 'list', 'get', 'note', 'state', 'history'):
        command = commands.add_parser(name)
        command.add_argument('--database', required=True, type=Path)
        command.add_argument('--json', action='store_true', help='Output is always JSON; accepted for consistency.')
        if name in ('get', 'note', 'state', 'history'):
            command.add_argument('--case-id', required=True, type=int)
        if name in ('create', 'note', 'state'):
            command.add_argument('--author', required=True, help='Self-declared label, not a verified identity.')
        if name == 'create':
            command.add_argument('--alert-id', required=True)
            command.add_argument('--title', required=True)
        if name == 'note':
            command.add_argument('--text', required=True)
        if name == 'state':
            command.add_argument('--status', choices=STATUSES, required=True)
            command.add_argument('--disposition', choices=DISPOSITIONS, required=True)
            command.add_argument('--reason', required=True)
            command.add_argument('--expected-revision', type=int, required=True)
        if name == 'list':
            command.add_argument('--status', choices=STATUSES)
        if name in ('list', 'history'):
            command.add_argument('--limit', type=int, default=50)
            command.add_argument('--offset', type=int, default=0)
    args = parser.parse_args(argv)
    try:
        if args.command == 'create':
            result = create_case(args.database, args.alert_id, args.title, args.author)
        elif args.command == 'note':
            result = add_note(args.database, args.case_id, args.text, args.author)
        elif args.command == 'state':
            result = change_state(args.database, args.case_id, args.status, args.disposition,
                                  args.reason, args.author, args.expected_revision)
        elif args.command == 'get':
            result = get_case(args.database, args.case_id)
        elif args.command == 'history':
            result = case_history(args.database, args.case_id, limit=args.limit, offset=args.offset)
        else:
            result = list_cases(args.database, status=args.status, limit=args.limit, offset=args.offset)
        if result is None:
            print(json.dumps({'error': 'Case not found.'}))
            return 1
    except StorageError as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=True))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0
