import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    from bbme import db
    from bbme.config import load
    from bbme.reference import tiger
    from bbme.regions import scored_tracts
    from bbme.runtime import WORKING, upstream, write_run_meta

    started = time.time()
    cfg = load("data")
    raw = upstream("audit/MANIFEST.json") / "raw"
    out = WORKING / "edges"
    out.mkdir(parents=True, exist_ok=True)
    con = db.connect(memory_limit="22GB", threads=4, temp_dir="/tmp/duckdb")
    tiger.load_roads(con, tiger.download(cfg, Path("/tmp/external")))
    scored = scored_tracts(raw, cfg["regions"])
    tolerances = {"0p1m": 1e-6, "1m": 1e-5, "5m": 5e-5, "20m": 2e-4}
    lengths = tiger.boundary_lengths(con, raw, cfg["regions"], scored, tolerances)
    lengths.to_parquet(out / "tiger_boundary_tracts.parquet", index=False)
    cols = [c for c in lengths.columns if c.startswith("tiger_")]
    summary = {
        "run_id": run["run_id"],
        "totals_by_region": lengths.groupby("region")[cols].sum().round(0).to_dict(),
    }
    (out / "EDGES_MANIFEST.json").write_text(json.dumps(summary, indent=2))
    write_run_meta(out, run, code, started)
    print(json.dumps(summary, indent=2), flush=True)
