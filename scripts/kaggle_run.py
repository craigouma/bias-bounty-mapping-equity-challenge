import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from bbme.config import ROOT, load
from kaggle_code_push import head_sha, push, remote_sha, require_clean_tree, sh

STAGES_DIR = ROOT / "kaggle" / "stages"
EXPERIMENTS = ROOT / "docs" / "experiments.md"
TERMINAL = ("complete", "error", "cancel")


def render(stage: str, run: dict, prefix: str = "") -> Path:
    kcfg = load("kaggle")
    scfg = kcfg["stages"][stage]
    user = kcfg["username"]
    out = ROOT / load("paths")["kernels_build"] / stage
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    bootstrap = (STAGES_DIR / "bootstrap.py").read_text()
    bootstrap = bootstrap.replace("{sha}", run["sha"]).replace("{run_json}", json.dumps(run))
    body = (STAGES_DIR / stage / "run.py").read_text()
    (out / "run.py").write_text(f"{bootstrap}\n\n{body}\n\nmain(RUN, CODE)\n")
    meta = {
        "id": f"{user}/{prefix}{scfg['slug']}",
        "title": f"{prefix}{scfg['slug']}",
        "code_file": "run.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": "true",
        "enable_gpu": "true" if scfg["gpu"] else "false",
        "enable_internet": "true",
        "machine_shape": kcfg["accelerator"] if scfg["gpu"] else "",
        "dataset_sources": [
            f"{user}/{d}" for d in [kcfg["code_dataset"], *scfg.get("datasets", [])]
        ],
        "competition_sources": [],
        "kernel_sources": [f"{user}/{prefix}{s}" for s in scfg["kernel_sources"]],
        "model_sources": [],
    }
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
    return out


def status(ref: str) -> str:
    text = sh("kaggle", "kernels", "status", ref, check=False).stdout.lower()
    match = re.search(r'status "?(?:kernelworkerstatus\.)?([a-z_]+)', text)
    return match.group(1) if match else text.strip()


def wait(ref: str, timeout_h: float) -> str:
    deadline = time.time() + timeout_h * 3600
    while time.time() < deadline:
        state = status(ref)
        if state.startswith(TERMINAL):
            return state
        time.sleep(30)
    raise SystemExit(f"{ref} still running after {timeout_h} h")


def pull(ref: str, patterns: list[str], dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for pattern in patterns:
        subprocess.run(
            ["kaggle", "kernels", "output", ref, "-p", str(dest), "-o", "-q"]
            + ["--file-pattern", pattern, "--page-size", "200"],
            cwd=ROOT,
            check=True,
        )


def log_run(run: dict, state: str, wall_min: float, dest: Path) -> None:
    runtime = next(dest.rglob("runtime.json"), None)
    extra = json.loads(runtime.read_text()) if runtime else {}
    peak = extra.get("peak_rss_gb", "n/a")
    overrides = " ".join(run["overrides"]) or "defaults"
    row = (
        f"| {run['run_id']} | {run['stage']} | {run['sha'][:7]} | {overrides} | {state} "
        f"| {wall_min:.1f} | {peak} |\n"
    )
    with EXPERIMENTS.open("a") as f:
        f.write(row)


def run_stage(
    stage: str, overrides: list[str], timeout_h: float = 11.5, prefix: str = ""
) -> tuple[str, str, Path]:
    """Render, push, follow and pull one stage; returns run ID, final state and output folder.

    A non-empty prefix runs the stage as a separate chain of kernels (`<prefix><slug>`), whose
    kernel sources carry the same prefix, so a from-scratch rerun leaves the original outputs alone.
    """
    kcfg = load("kaggle")
    scfg = kcfg["stages"][stage]
    require_clean_tree()
    sha = head_sha()
    if remote_sha() != sha:
        push()
    run_id = f"{datetime.now():%Y%m%d-%H%M}-{stage}-{sha[:7]}"
    run = {
        "run_id": run_id,
        "stage": stage,
        "sha": sha,
        "overrides": overrides,
        "install": stage != "00_env",
    }
    folder = render(stage, run, prefix)
    ref = f"{kcfg['username']}/{prefix}{scfg['slug']}"
    cmd = ["kaggle", "kernels", "push", "-p", str(folder)]
    if scfg["gpu"]:
        cmd += ["--accelerator", kcfg["accelerator"]]
    started = time.time()
    subprocess.run(cmd, cwd=ROOT, check=True)
    print(f"run {run_id} pushed to {ref}", flush=True)
    time.sleep(20)
    subprocess.run(["kaggle", "kernels", "logs", ref, "--follow"], cwd=ROOT, check=False)
    state = wait(ref, timeout_h)
    wall_min = (time.time() - started) / 60
    dest = ROOT / load("paths")["kaggle_artifacts"] / stage / run_id
    if state.startswith("complete"):
        pull(ref, [p.replace("{run_id}", run_id) for p in scfg["pull"]], dest)
    else:
        dest.mkdir(parents=True, exist_ok=True)
        log = sh("kaggle", "kernels", "logs", ref, check=False).stdout
        (dest / "kernel.log").write_text(log)
    log_run(run, state, wall_min, dest)
    print(f"{run_id}: {state} after {wall_min:.1f} min, outputs in {dest}")
    return run_id, state, dest


def main() -> int:
    parser = argparse.ArgumentParser(description="Render, push, follow and pull a Kaggle stage.")
    parser.add_argument("stage")
    parser.add_argument("--set", default="", help="space-separated key=value overrides")
    parser.add_argument("--timeout-h", type=float, default=11.5)
    parser.add_argument("--prefix", default="", help="kernel slug prefix for a separate chain")
    args = parser.parse_args()
    _, state, _ = run_stage(args.stage, args.set.split(), args.timeout_h, args.prefix)
    return 0 if state.startswith("complete") else 1


if __name__ == "__main__":
    sys.exit(main())
