from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

TRIBAL, OTHER = "#21918c", "#fde725"


def unnamed_share_by_stratum(summary: pd.DataFrame, path: Path) -> Path:
    """Unnamed share of drivable length, tribal against non-tribal, by region and RUCA class."""
    cells = summary.pivot_table(
        index=["region", "ruca_class"], columns="tribal", values="mean_unnamed_share"
    ).dropna()
    labels = [f"{r}\n{c}" for r, c in cells.index]
    x = range(len(cells))
    fig, ax = plt.subplots(figsize=(max(6, 0.9 * len(cells)), 4.2))
    ax.bar(
        [i - 0.2 for i in x], cells[False] * 100, width=0.4, color=OTHER, label="Non-tribal tracts"
    )
    ax.bar([i + 0.2 for i in x], cells[True] * 100, width=0.4, color=TRIBAL, label="Tribal tracts")
    ax.set_xticks(list(x), labels, fontsize=8)
    ax.set_ylabel("Drivable road length with no name (%)")
    ax.set_title("Unnamed road share by region and RUCA class, Overture 2026-08-19.0")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path
