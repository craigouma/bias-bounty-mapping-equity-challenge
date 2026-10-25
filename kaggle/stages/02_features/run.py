import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    from bbme import db
    from bbme.config import apply_overrides, load
    from bbme.features.build import build, calibration, column_doc, summary
    from bbme.runtime import WORKING, upstream, write_run_meta

    started = time.time()
    cfg = {
        "data": load("data"),
        "features": apply_overrides(load("features"), run["overrides"]),
        "poi": load("poi_categories"),
    }
    raw = upstream("audit/MANIFEST.json") / "raw"
    out = WORKING / "features"
    out.mkdir(parents=True, exist_ok=True)
    con = db.connect(memory_limit="22GB", threads=4, temp_dir="/tmp/duckdb")
    df = build(con, raw, cfg)
    df.to_parquet(out / "features.parquet", index=False)
    (out / "columns.md").write_text(column_doc(df))
    (out / "calibration.json").write_text(json.dumps(calibration(df, cfg["features"]), indent=2))
    manifest = {"run_id": run["run_id"], "sha": run["sha"], **summary(df)}
    (out / "FEATURES_MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    write_run_meta(out, run, code, started)
    size_mb = (out / "features.parquet").stat().st_size / 1e6
    print(f"features: {df.shape}, {size_mb:.1f} MB", flush=True)
