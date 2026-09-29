"""Read saved alert history without installing a package."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sentinellab.alerts_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
