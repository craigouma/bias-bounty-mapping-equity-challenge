import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from bbme.config import ROOT, load

INCLUDE = ["src/bbme", "configs", "kaggle/stages", "requirements-kaggle.txt"]


def sh(*cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=check)


def head_sha() -> str:
    return sh("git", "rev-parse", "HEAD").stdout.strip()


def require_clean_tree() -> None:
    dirty = sh("git", "status", "--porcelain").stdout.strip()
    if dirty:
        raise SystemExit(f"git tree is dirty, commit first:\n{dirty}")


def dataset_ref() -> str:
    cfg = load("kaggle")
    return f"{cfg['username']}/{cfg['code_dataset']}"


def remote_sha() -> str | None:
    with tempfile.TemporaryDirectory() as tmp:
        got = sh(
            "kaggle",
            "datasets",
            "download",
            dataset_ref(),
            "-f",
            "CODE_SHA",
            "-p",
            tmp,
            check=False,
        )
        marker = Path(tmp) / "CODE_SHA"
        return marker.read_text().strip() if got.returncode == 0 and marker.exists() else None


def build(sha: str) -> Path:
    out = ROOT / load("paths")["code_build"]
    shutil.rmtree(out, ignore_errors=True)
    code = out / "bbme_code"
    for rel in INCLUDE:
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, code / rel, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            (code / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, code / rel)
    (code / "CODE_SHA").write_text(sha + "\n")
    (out / "CODE_SHA").write_text(sha + "\n")
    meta = {
        "title": load("kaggle")["code_dataset"],
        "id": dataset_ref(),
        "licenses": [{"name": "other"}],
    }
    (out / "dataset-metadata.json").write_text(json.dumps(meta, indent=2))
    return out


def wait_ready(timeout_s: int = 900) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        status = sh("kaggle", "datasets", "status", dataset_ref(), check=False).stdout.strip()
        if status == "ready":
            return
        time.sleep(10)
    raise SystemExit(f"{dataset_ref()} not ready after {timeout_s}s")


def wait_sha(sha: str, timeout_s: int = 900) -> None:
    deadline = time.time() + timeout_s
    while remote_sha() != sha:
        if time.time() > deadline:
            raise SystemExit(f"{dataset_ref()} still does not carry {sha[:7]}")
        time.sleep(15)


def push() -> str:
    require_clean_tree()
    sha = head_sha()
    if remote_sha() == sha:
        print(f"{dataset_ref()} already at {sha[:7]}")
        return sha
    out = build(sha)
    exists = sh("kaggle", "datasets", "status", dataset_ref(), check=False).returncode == 0
    if exists:
        cmd = ["kaggle", "datasets", "version", "-p", str(out), "-m", sha[:7], "-r", "zip"]
    else:
        cmd = ["kaggle", "datasets", "create", "-p", str(out), "-r", "zip"]
    result = sh(*cmd, check=False)
    print(result.stdout, result.stderr, sep="")
    if result.returncode != 0:
        raise SystemExit("code dataset upload failed")
    wait_ready()
    wait_sha(sha)
    print(f"{dataset_ref()} ready at {sha[:7]}")
    return sha


if __name__ == "__main__":
    push()
    sys.exit(0)
