from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

TRIBAL, OTHER = "#21918c", "#fde725"
KINDS = {"any": "All tribal", "legal": "Reservations", "statistical": "Statistical areas"}


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


def contrast_intervals(findings: dict, measure: str, path: Path) -> Path:
    """Matched tribal minus non-tribal difference with 95% county-bootstrap intervals."""
    rows = [
        (f"{KINDS[kind]}: {region} ({r['tribal_tracts']})", r["matched_difference"], *r["ci95"])
        for kind, by_measure in findings.items()
        for region, r in by_measure[measure].items()
    ]
    fig, ax = plt.subplots(figsize=(6.4, 0.32 * len(rows) + 1.2))
    for i, (_, mid, lo, hi) in enumerate(rows):
        ax.plot([lo * 100, hi * 100], [i, i], color=TRIBAL, lw=2)
        ax.plot(mid * 100, i, "o", color="#440154")
    ax.axvline(0, color="0.4", lw=0.8)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Tribal minus non-tribal unnamed share (percentage points)")
    ax.set_title(f"Matched difference within region and RUCA class, {measure} roads", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def region_maps(
    tracts, column: str, label: str, title: str, path: Path, outline=None, vmax: float = 1.0
) -> Path:
    """One choropleth panel per region; tracts where `outline` is true get a dark edge."""
    regions = list(dict.fromkeys(tracts["region"]))
    cols = 3 if len(regions) > 4 else 2
    rows = -(-len(regions) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 3.9 * rows))
    axes = axes.ravel()
    for ax, region in zip(axes, regions, strict=False):
        sub = tracts[tracts["region"] == region]
        sub.plot(
            column=column,
            ax=ax,
            cmap="viridis",
            vmin=0,
            vmax=vmax,
            linewidth=0.05,
            edgecolor="0.85",
            missing_kwds={"color": "0.9"},
        )
        if outline is not None:
            sub[outline.loc[sub.index]].boundary.plot(ax=ax, color="black", linewidth=0.5)
        ax.set_title(region, fontsize=10)
        ax.set_axis_off()
    for ax in axes[len(regions) :]:
        ax.set_axis_off()
    mappable = plt.cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(0, vmax))
    extend = "max" if vmax < 1 else "neither"
    fig.colorbar(mappable, ax=axes.tolist(), shrink=0.6, label=label, extend=extend)
    fig.suptitle(title, fontsize=11)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path
