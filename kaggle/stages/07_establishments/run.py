import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    import pandas as pd

    from bbme import guard
    from bbme.config import load
    from bbme.reference import establishments as est
    from bbme.runtime import WORKING, upstream, write_run_meta

    started = time.time()
    ext = load("data")["external_reference"]
    features = upstream("features/FEATURES_MANIFEST.json") / "features" / "features.parquet"
    tracts = pd.read_parquet(
        guard.artifact(features), columns=["GEOID", "region", "pop_total", "poi_n"]
    )
    out = WORKING / "establishments"
    out.mkdir(parents=True, exist_ok=True)
    zbp = est.zip_establishments(est.download(ext["zbp_url"], Path("/tmp/external")))
    relation = est.download(ext["zcta_tract_url"], Path("/tmp/external"))
    table = est.tract_establishments(zbp, relation, tracts)
    table.to_parquet(out / "establishment_reference_tracts.parquet", index=False)
    summary = {
        "run_id": run["run_id"],
        "zip_codes": int(len(zbp)),
        "totals_by_region": table.groupby("region")[["est_area", "est_pop"]]
        .sum()
        .round(0)
        .to_dict(),
        "zero_share": {c: float((table[c] == 0).mean()) for c in ["est_area", "est_pop"]},
    }
    (out / "ESTABLISHMENT_MANIFEST.json").write_text(json.dumps(summary, indent=2))
    write_run_meta(out, run, code, started)
    print(json.dumps(summary, indent=2), flush=True)
