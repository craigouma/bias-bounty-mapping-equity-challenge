import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    import pandas as pd
    import yaml

    from bbme import guard
    from bbme.config import apply_overrides, load
    from bbme.model import metrics, predict, submission_frame
    from bbme.runtime import WORKING, upstream, write_run_meta
    from bbme.submit import assert_valid, write

    started = time.time()
    cfg = apply_overrides(load("model"), run["overrides"])
    features = upstream("features/FEATURES_MANIFEST.json") / "features" / "features.parquet"
    df = pd.read_parquet(guard.artifact(features)).sort_values("GEOID", ignore_index=True)
    if cfg["transport"]["source"] == "tiger":
        ref = upstream("reference/REFERENCE_MANIFEST.json") / "reference" / "tiger_tracts.parquet"
        tiger = pd.read_parquet(guard.artifact(ref))[["GEOID", "tiger_len_m"]]
        df = df.merge(tiger, on="GEOID", how="left", validate="1:1")
    if cfg["poi"]["source"] == "reference":
        fac = upstream("facilities/FACILITY_MANIFEST.json") / "facilities"
        est = upstream("establishments/ESTABLISHMENT_MANIFEST.json") / "establishments"
        for path in [
            fac / "facility_reference_tracts.parquet",
            est / "establishment_reference_tracts.parquet",
        ]:
            table = pd.read_parquet(guard.artifact(path)).drop(columns="region")
            df = df.merge(table, on="GEOID", how="left", validate="1:1")
    if cfg["building"]["source"] == "microsoft":
        ref = upstream("reference/REFERENCE_MANIFEST.json") / "reference"
        ms = pd.read_parquet(guard.artifact(ref / "building_reference_tracts.parquet"))
        df = df.merge(ms.drop(columns="region"), on="GEOID", how="left", validate="1:1")
    out = WORKING / "runs" / run["run_id"]
    out.mkdir(parents=True, exist_ok=True)

    comp, extra = predict(df, cfg)
    sample = df[["GEOID", "region"]]
    sample_path = Path("/tmp/scored_tracts.csv")
    sample.assign(coverage_gap_score="0.0").to_csv(sample_path, index=False)
    sub = write(submission_frame(comp), sample, out / "submission.csv")
    assert_valid(sub, sample_path)

    comp.to_parquet(out / "components.parquet", index=False)
    (out / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    (out / "metrics.json").write_text(json.dumps({**metrics(comp), **extra}, indent=2, default=str))
    write_run_meta(out, run, code, started)
    print(json.dumps(metrics(comp), indent=2), flush=True)
