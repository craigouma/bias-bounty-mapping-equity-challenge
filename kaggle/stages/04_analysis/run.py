import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    import numpy as np
    import pandas as pd

    from bbme import guard
    from bbme.analysis import bias_discovery as bd
    from bbme.analysis.external.counties import county_names
    from bbme.analysis.figures import contrast_intervals, region_maps, unnamed_share_by_stratum
    from bbme.config import load
    from bbme.runtime import INPUT, WORKING, upstream, write_run_meta

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
    summary_over = {kind: bd.share_over(df, kind) for kind in ["legal", "statistical"]}
    (out / "share_over.json").write_text(json.dumps(summary_over, indent=2))
    unnamed_share_by_stratum(summary, out / "figures" / "unnamed_share_by_stratum.png")
    for measure in bd.MEASURES:
        contrast_intervals(results, measure, out / "figures" / f"contrast_{measure}.png")
    geo = bd.tract_geometry(raw, cfg["regions"])
    tribal_regions = ["eastern-ok", "maricopa-az", "eastern-wa", "northern-ca"]
    unnamed = geo[geo["region"].isin(tribal_regions)].merge(
        df[["GEOID", "local_unnamed_share", "tribal_kind"]], on="GEOID", how="left"
    )
    region_maps(
        unnamed,
        "local_unnamed_share",
        "Unnamed share of local street length",
        "Unnamed local streets by tract; reservation tracts outlined",
        out / "figures" / "map_unnamed_local.png",
        outline=unnamed["tribal_kind"].eq("legal"),
    )
    latest = sorted(INPUT.rglob("runs/*/submission.csv"), key=lambda p: p.parent.name)[-1]
    scores = pd.read_csv(guard.artifact(latest), dtype={"GEOID": str})
    scored = geo.merge(scores[["GEOID", "coverage_gap_score"]], on="GEOID", how="left")
    region_maps(
        scored,
        "coverage_gap_score",
        "Predicted coverage gap score",
        f"Coverage gap score by tract, run {latest.parent.name}",
        out / "figures" / "map_coverage_gap.png",
        vmax=0.5,
    )
    (out / "maps.json").write_text(json.dumps({"score_run": latest.parent.name}, indent=2))
    write_run_meta(out, run, code, started)
    print(json.dumps(results, indent=2), flush=True)
