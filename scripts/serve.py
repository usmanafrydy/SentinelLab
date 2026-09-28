"""Start the local browser interface from any working directory."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sentinellab.web.server import main

if __name__ == "__main__":
    raise SystemExit(main())
