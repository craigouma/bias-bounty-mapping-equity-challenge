import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    import numpy as np
    import pandas as pd

    from bbme import guard
    from bbme.analysis import bias_discovery as bd
    from bbme.analysis.external.counties import county_names
    from bbme.analysis.figures import contrast_intervals, unnamed_share_by_stratum
    from bbme.config import load
    from bbme.runtime import WORKING, upstream, write_run_meta

    started = time.time()
    cfg = load("data")
    raw = upstream("audit/MANIFEST.json") / "raw"
    features = upstream("features/FEATURES_MANIFEST.json") / "features" / "features.parquet"
    out = WORKING / "analysis"
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    counties = county_names(cfg["analysis_external"]["county_names_url"], Path("/tmp/external"))
    context = bd.tract_context(raw, cfg["regions"]).merge(counties, on="county_fips", how="left")
    df = bd.unnamed_table(pd.read_parquet(guard.artifact(features)), context)
    summary = bd.stratum_summary(df)
    summary.to_csv(out / "tables" / "unnamed_by_stratum.csv", index=False)
    bd.worst_tracts(df).to_csv(out / "tables" / "unnamed_worst_tribal_tracts.csv", index=False)
    bd.worst_tracts(bd.contrast(df, "legal")).to_csv(
        out / "tables" / "unnamed_worst_reservation_tracts.csv", index=False
    )
    bd.by_tribal_area(df).to_csv(out / "tables" / "unnamed_by_tribal_area.csv", index=False)
    rng = np.random.default_rng(load("model")["seed"])
    results = {}
    for kind in ["any", "legal", "statistical"]:
        sub = bd.contrast(df, kind)
        results[kind] = {}
        for measure, value in bd.MEASURES.items():
            results[kind][measure] = {}
            for region, g in [("all", sub), *sub.groupby("region")]:
                g = g[g[value].notna()]
                if g["tribal"].sum() < 10:
                    continue
                lo, hi = bd.bootstrap_by_county(g, rng, value=value)
                results[kind][measure][region] = {
                    "tribal_tracts": int(g["tribal"].sum()),
                    "matched_difference": bd.matched_difference(g, value),
                    "ci95": [lo, hi],
                }
    (out / "findings.json").write_text(json.dumps(results, indent=2))
    unnamed_share_by_stratum(summary, out / "figures" / "unnamed_share_by_stratum.png")
    for measure in bd.MEASURES:
        contrast_intervals(results, measure, out / "figures" / f"contrast_{measure}.png")
    write_run_meta(out, run, code, started)
    print(json.dumps(results, indent=2), flush=True)
