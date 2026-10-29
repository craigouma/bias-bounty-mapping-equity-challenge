"""Rerun the model stage for a final submission and compare the result with the uploaded file.

Upstream stage outputs (01, 02, 05, 06, 07) persist on Kaggle; rerun them first with
`make kaggle-run STAGE=<stage>` to reproduce from the raw sources.
"""

import json
import sys

from bbme.config import ROOT, load
from bbme.submit import compare
from kaggle_run import run_stage

TOLERANCE = 1e-9


def main(final: str) -> int:
    cfg = load(f"final_{final}")
    run_id, state, dest = run_stage("03_model", cfg["overrides"])
    if not state.startswith("complete"):
        return 1
    submitted = ROOT / load("paths")["submissions"] / cfg["file"]
    result = compare(dest / "runs" / run_id / "submission.csv", submitted)
    result.update(final=final, submission=cfg["submission"], run_id=run_id)
    print(json.dumps(result, indent=2))
    ok = result["max_abs_diff"] <= TOLERANCE and result["flag_mismatches"] == 0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
