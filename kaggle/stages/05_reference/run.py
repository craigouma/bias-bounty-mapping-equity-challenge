import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    from bbme import db
    from bbme.config import load
    from bbme.reference import buildings, tiger
    from bbme.regions import scored_tracts
    from bbme.runtime import WORKING, upstream, write_run_meta

    started = time.time()
    cfg = load("data")
    raw = upstream("audit/MANIFEST.json") / "raw"
    out = WORKING / "reference"
    out.mkdir(parents=True, exist_ok=True)
    con = db.connect(memory_limit="22GB", threads=4, temp_dir="/tmp/duckdb")
    zips = tiger.download(cfg, Path("/tmp/external"))
    tiger.load_roads(con, zips)
    db.assert_finite(con, "(SELECT {} AS l FROM tiger)".format(db.length_m("geometry")), ["l"])
    scored = scored_tracts(raw, cfg["regions"])
    lengths = tiger.tract_lengths(con, raw, cfg["regions"], scored)
    lengths.to_parquet(out / "tiger_tracts.parquet", index=False)
    summary = {
        "run_id": run["run_id"],
        "files": {z.name: z.stat().st_size for z in zips},
        "segments": con.sql("SELECT count(*) FROM tiger").fetchone()[0],
        "tracts": len(lengths),
        "undefined_share_by_region": (
            (lengths["tiger_len_m"] == 0).groupby(lengths["region"]).mean().round(4).to_dict()
        ),
    }
    building_zips = buildings.download(cfg, Path("/tmp/external"))
    counts = buildings.tract_counts(con, building_zips, raw, cfg["regions"], scored)
    counts.to_parquet(out / "building_reference_tracts.parquet", index=False)
    summary["building_files"] = {z.name: z.stat().st_size for z in building_zips}
    summary["building_undefined_share_by_region"] = (
        (counts["ms_n_centroid"] == 0).groupby(counts["region"]).mean().round(4).to_dict()
    )
    (out / "REFERENCE_MANIFEST.json").write_text(json.dumps(summary, indent=2))
    write_run_meta(out, run, code, started)
    print(json.dumps(summary, indent=2), flush=True)
