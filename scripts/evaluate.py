"""Print a complete synthetic evaluation report; never modify a user database."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from sentinellab.evaluation import EvaluationError, evaluate
from sentinellab.ingestion.reader import InputFileError
from sentinellab.storage.database import StorageError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'data/evaluation/day15/manifest.json')
    args = parser.parse_args()
    try:
        report = evaluate(args.manifest)
    except (EvaluationError, InputFileError, StorageError, OSError) as error:
        # File-system errors can expose local paths; keep those out of output.
        message = 'evaluation file could not be read or written' if isinstance(error, OSError) else str(error)
        print('Evaluation failed: ' + message, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['rule_agreement_count'] == report['scenario_count'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
