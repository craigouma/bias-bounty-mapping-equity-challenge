"""Public RMSE of every scored submission, read from docs/submissions.md."""

import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PHASES = [(1, 1, "Constant"), (2, 16, "Estimated components"), (17, 24, "Reference rebuilt")]
# S23 was a competitor's published file uploaded as a benchmark, not a submission of this pipeline.
EXCLUDE = {23}
COLORS = ["#440154", "#21918c", "#fde725"]


def scores(log: Path) -> dict[int, float]:
    out = {}
    for section in re.split(r"^## S", log.read_text(), flags=re.M)[1:]:
        rmse = re.search(r"^- Public RMSE: ([0-9.]+)", section, flags=re.M)
        if rmse:
            out[int(section.split()[0])] = float(rmse.group(1))
    for i in EXCLUDE:
        out.pop(i, None)
    return out


def main(log: Path, out: Path) -> None:
    rmse = scores(log)
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    for (lo, hi, label), color in zip(PHASES, COLORS, strict=True):
        ids = [i for i in sorted(rmse) if lo <= i <= hi]
        ax.plot(ids, [rmse[i] for i in ids], "o", color=color, label=label, mec="0.2", mew=0.5)
    best = [min(v for k, v in rmse.items() if k <= i) for i in sorted(rmse)]
    ax.step(sorted(rmse), best, where="post", color="0.4", lw=1, label="Best so far")
    ax.set_xlabel("Submission")
    ax.set_ylabel("Public RMSE")
    ax.set_xticks(sorted(rmse), [f"S{i:02d}" for i in sorted(rmse)], rotation=90, fontsize=7)
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out, dpi=200)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
