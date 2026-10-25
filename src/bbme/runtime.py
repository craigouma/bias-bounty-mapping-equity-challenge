import json
import resource
import subprocess
import sys
import time
from pathlib import Path

INPUT = Path("/kaggle/input")
WORKING = Path("/kaggle/working")


def upstream(marker: str) -> Path:
    """Root of the attached kernel output that holds `marker` (e.g. `audit/MANIFEST.json`)."""
    found = sorted(INPUT.rglob(marker))
    if not found:
        raise FileNotFoundError(f"no attached input contains {marker}")
    return found[0].parents[len(Path(marker).parts) - 1]


def write_run_meta(out: Path, run: dict, code: Path, started: float) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "CODE_SHA").write_text((code / "CODE_SHA").read_text())
    freeze = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True
    )
    (out / "pip_freeze.txt").write_text(freeze.stdout)
    peak_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    runtime = {
        "run_id": run["run_id"],
        "stage": run["stage"],
        "wall_s": round(time.time() - started, 1),
        "peak_rss_gb": round(peak_kb / 1024**2, 2),
    }
    (out / "runtime.json").write_text(json.dumps(runtime, indent=2))
