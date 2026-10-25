import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def _cmd(*args: str) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=60).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return f"unavailable: {exc}"


def _internet(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return f"ok {r.status}"
    except OSError as exc:
        return f"failed: {exc}"


def main(run: dict, code: Path) -> None:
    from bbme.runtime import WORKING, write_run_meta

    started = time.time()
    out = WORKING / "env"
    out.mkdir(parents=True, exist_ok=True)
    mem = Path("/proc/meminfo").read_text().splitlines()[:3]
    disk = shutil.disk_usage(WORKING)
    env = {
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "sched_cpus": len(os.sched_getaffinity(0)),
        "meminfo": mem,
        "disk_working_total_gb": round(disk.total / 1e9, 1),
        "disk_working_free_gb": round(disk.free / 1e9, 1),
        "disk_tmp_free_gb": round(shutil.disk_usage("/tmp").free / 1e9, 1),
        "nvidia_smi": _cmd("nvidia-smi"),
        "internet_pypi": _internet("https://pypi.org/simple/duckdb/"),
        "internet_bucket": _internet(
            "https://data.source.coop/humane-intelligence/bias-bounty-mapping-equity-challenge/README.md"
        ),
        "aws_cli": _cmd("aws", "--version"),
        "input_listing": sorted(str(p) for p in Path("/kaggle/input").rglob("*"))[:200],
    }
    (out / "env.json").write_text(json.dumps(env, indent=2))
    write_run_meta(out, run, code, started)
    print(json.dumps({k: v for k, v in env.items() if k != "input_listing"}, indent=2))
