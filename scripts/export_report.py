"""Export saved investigation data to a private local file without overwriting."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from sentinellab.reports import build_report, render_report, report_filename
from sentinellab.storage.database import StorageError


def main(argv=None):
    parser = argparse.ArgumentParser(description='Export a saved case; output stays in ignored reports/generated.')
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--case-id', type=int, required=True)
    parser.add_argument('--format', choices=('json', 'markdown'), required=True)
    parser.add_argument('--expected-revision', type=int)
    parser.add_argument('--output', type=Path, help='Optional new filename within reports/generated.')
    args = parser.parse_args(argv)
    try:
        report = build_report(args.database, args.case_id, expected_revision=args.expected_revision)
        if report is None:
            raise StorageError('Case not found. Create a case from a saved alert first.')
        data = render_report(report, args.format)
        allowed = (ROOT / 'reports/generated').resolve()
        output = args.output or allowed / report_filename(args.case_id, report['case']['revision'], args.format)
        output = output.resolve()
        if not output.is_relative_to(allowed) or output == allowed:
            raise StorageError('Save private exports below reports/generated; choose a new filename there.')
        allowed.mkdir(parents=True, exist_ok=True)
        # Exclusive create: existing files (including the database) are never overwritten.
        stream = output.open('xb')
        try:
            with stream:
                stream.write(data)
        except BaseException:
            output.unlink(missing_ok=True)
            raise
        print(json.dumps({'saved': str(output), 'bytes': len(data), 'case_revision': report['case']['revision']}))
        return 0
    except (StorageError, OSError) as error:
        print(json.dumps({'error': str(error) if isinstance(error, StorageError) else
                         'Cannot create report. Choose an unused filename and check folder permissions.'}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
