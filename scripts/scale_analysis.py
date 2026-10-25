import argparse
import math
import sys
from pathlib import Path

from bbme.submit import read_text_table

S01_RMSE = 0.107246299


def main() -> int:
    parser = argparse.ArgumentParser(description="Best global scale and scaled RMSE (D021).")
    parser.add_argument("submission", type=Path)
    parser.add_argument("rmse", type=float)
    args = parser.parse_args()
    p = read_text_table(args.submission)["coverage_gap_score"].astype(float)
    ey2, ep2 = S01_RMSE**2, float((p**2).mean())
    eyp = (ey2 + ep2 - args.rmse**2) / 2
    print(f"E[p]={p.mean():.4f} E[p2]={ep2:.6f} E[yp]={eyp:.6f}")
    print(f"scale={eyp / ep2:.3f} scaled_rmse={math.sqrt(ey2 - eyp**2 / ep2):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
