import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    import numpy as np
    import pandas as pd

    from bbme import guard
    from bbme.analysis import bias_discovery as bd
    from bbme.analysis.figures import unnamed_share_by_stratum
    from bbme.config import load
    from bbme.runtime import WORKING, upstream, write_run_meta

    started = time.time()
    cfg = load("data")
    raw = upstream("audit/MANIFEST.json") / "raw"
    features = upstream("features/FEATURES_MANIFEST.json") / "features" / "features.parquet"
    out = WORKING / "analysis"
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    df = bd.unnamed_table(
        pd.read_parquet(guard.artifact(features)), bd.tract_context(raw, cfg["regions"])
    )
    summary = bd.stratum_summary(df)
    summary.to_csv(out / "tables" / "unnamed_by_stratum.csv", index=False)
    bd.worst_tracts(df).to_csv(out / "tables" / "unnamed_worst_tribal_tracts.csv", index=False)
    bd.by_tribal_area(df).to_csv(out / "tables" / "unnamed_by_tribal_area.csv", index=False)
    rng = np.random.default_rng(load("model")["seed"])
    results = {}
    for region, g in [("all", df), *df.groupby("region")]:
        if g["tribal"].sum() < 10:
            continue
        lo, hi = bd.bootstrap_by_county(g, rng)
        results[region] = {
            "tribal_tracts": int(g["tribal"].sum()),
            "matched_difference": bd.matched_difference(g),
            "ci95": [lo, hi],
        }
    (out / "findings.json").write_text(json.dumps(results, indent=2))
    unnamed_share_by_stratum(summary, out / "figures" / "unnamed_share_by_stratum.png")
    write_run_meta(out, run, code, started)
    print(json.dumps(results, indent=2), flush=True)
