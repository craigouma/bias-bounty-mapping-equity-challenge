import argparse
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from bbme.config import ROOT, load
from bbme.submit import assert_valid

LOG = ROOT / "docs" / "submissions.md"
BUDGET = 35


def _run_id(sub: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    if sub.parent.parent.name == "runs":
        return sub.parent.name
    return sub.stem


def _code_sha(sub: Path) -> str:
    marker = sub.parent / "CODE_SHA"
    if marker.exists():
        return marker.read_text().strip()
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def register(args: argparse.Namespace) -> None:
    paths = load("paths")
    if not re.fullmatch(r"S\d{2}", args.id):
        raise SystemExit(f"bad submission id {args.id}")
    text = LOG.read_text()
    if f"## {args.id} " in text:
        raise SystemExit(f"{args.id} is already registered")
    assert_valid(args.sub, ROOT / paths["sample_submission"])
    run_id = _run_id(args.sub, args.run_id)
    dest = ROOT / paths["submissions"] / f"{args.id}_{run_id}.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.sub, dest)
    used = len(re.findall(r"^## S\d{2} ", text, flags=re.M)) + 1
    entry = f"""
## {args.id} ({date.today().isoformat()})

- File: `{dest.relative_to(ROOT)}`
- Run ID: `{run_id}`
- Code SHA: `{_code_sha(args.sub)}`
- Hypothesis: {args.hypothesis}
- Change against current best: {args.change}
- Expected direction: {args.expect}
- Decision informed: {args.informs}
- Public RMSE: pending
- Submissions used after this one: {used} of {BUDGET}
"""
    LOG.write_text(text.rstrip("\n") + "\n" + entry)
    print(dest)


def result(args: argparse.Namespace) -> None:
    text = LOG.read_text()
    head = f"## {args.id} "
    start = text.index(head)
    end = text.find("\n## ", start + 1)
    end = len(text) if end < 0 else end
    block = text[start:end].replace("- Public RMSE: pending", f"- Public RMSE: {args.rmse}")
    if args.note:
        block = block.rstrip("\n") + f"\n- Result note: {args.note}\n"
    LOG.write_text(text[:start] + block + text[end:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-register and log Zindi submissions.")
    sub = parser.add_subparsers(required=True)
    reg = sub.add_parser("register")
    reg.add_argument("--sub", type=Path, required=True)
    reg.add_argument("--id", required=True)
    reg.add_argument("--run-id")
    reg.add_argument("--hypothesis", required=True)
    reg.add_argument("--change", required=True)
    reg.add_argument("--expect", required=True)
    reg.add_argument("--informs", required=True)
    reg.set_defaults(func=register)
    res = sub.add_parser("result")
    res.add_argument("--id", required=True)
    res.add_argument("--rmse", required=True)
    res.add_argument("--note")
    res.set_defaults(func=result)
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
