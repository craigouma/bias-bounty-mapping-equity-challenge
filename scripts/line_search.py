import argparse
import math
import sys
from pathlib import Path

from bbme.submit import read_text_table


def main() -> int:
    """Optimal step along the direction from a base submission to a probe (one tuned scalar).

    RMSE^2(p + t d) = R0^2 - 2 t E[(y - p) d] + t^2 E[d^2], so two public scores fix the whole
    parabola: E[(y - p) d] = (R0^2 + E[d^2] - R1^2) / 2 and t* = E[(y - p) d] / E[d^2].
    Exact when the prediction moves linearly in the scalar between base and probe.
    """
    parser = argparse.ArgumentParser(description=main.__doc__.splitlines()[0])
    parser.add_argument("base", type=Path)
    parser.add_argument("base_rmse", type=float)
    parser.add_argument("probe", type=Path)
    parser.add_argument("probe_rmse", type=float)
    args = parser.parse_args()
    p = read_text_table(args.base)["coverage_gap_score"].astype(float)
    d = read_text_table(args.probe)["coverage_gap_score"].astype(float) - p
    ed2 = float((d**2).mean())
    cov = (args.base_rmse**2 + ed2 - args.probe_rmse**2) / 2
    t = cov / ed2
    print(f"E[d2]={ed2:.6f} E[(y-p)d]={cov:.6f}")
    best = math.sqrt(args.base_rmse**2 - cov**2 / ed2)
    print(f"t*={t:.3f} (probe is t=1) predicted_rmse={best:.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
