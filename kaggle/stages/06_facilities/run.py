import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    from bbme import db
    from bbme.config import load
    from bbme.reference import facilities
    from bbme.regions import scored_tracts
    from bbme.runtime import WORKING, upstream, write_run_meta

    started = time.time()
    cfg = load("data")
    fcodes = cfg["external_reference"]["facility_fcodes"]
    raw = upstream("audit/MANIFEST.json") / "raw"
    out = WORKING / "facilities"
    out.mkdir(parents=True, exist_ok=True)
    con = db.connect(memory_limit="22GB", threads=4, temp_dir="/tmp/duckdb")
    zips = facilities.download(cfg, Path("/tmp/external"))
    facilities.load_points(con, zips, fcodes)
    by_type = con.sql("SELECT kind, fcode, count(*) n FROM facility GROUP BY ALL ORDER BY ALL").df()
    scored = scored_tracts(raw, cfg["regions"])
    counts = facilities.tract_counts(con, raw, cfg["regions"], scored, list(fcodes))
    counts.to_parquet(out / "facility_reference_tracts.parquet", index=False)
    summary = {
        "run_id": run["run_id"],
        "files": {z.name: z.stat().st_size for z in zips},
        "points_by_type": by_type.to_dict(orient="records"),
        "tracts_with_type": {k: int((counts[f"ref_{k}"] > 0).sum()) for k in fcodes},
        "totals_by_region": counts.groupby("region")[[f"ref_{k}" for k in fcodes]].sum().to_dict(),
    }
    (out / "FACILITY_MANIFEST.json").write_text(json.dumps(summary, indent=2, default=int))
    write_run_meta(out, run, code, started)
    print(json.dumps(summary, indent=2, default=int), flush=True)
