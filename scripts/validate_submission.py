import argparse
import sys
from pathlib import Path

from bbme.config import ROOT, load
from bbme.submit import validate


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a submission against the sample.")
    parser.add_argument("submission", type=Path)
    parser.add_argument("--sample", type=Path, default=ROOT / load("paths")["sample_submission"])
    args = parser.parse_args()
    errors = validate(args.submission, args.sample)
    for e in errors:
        print(f"INVALID: {e}")
    if not errors:
        print(f"valid: {args.submission}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
