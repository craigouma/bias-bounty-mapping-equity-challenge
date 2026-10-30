import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    from bbme import db
    from bbme.config import load
    from bbme.features import load_tracts
    from bbme.reference import globalml
    from bbme.regions import scored_tracts
    from bbme.runtime import WORKING, upstream, write_run_meta

    started = time.time()
    cfg = load("data")
    ext = cfg["external_reference"]
    raw = upstream("audit/MANIFEST.json") / "raw"
    out = WORKING / "globalml"
    out.mkdir(parents=True, exist_ok=True)
    con = db.connect(memory_limit="22GB", threads=4, temp_dir="/tmp/duckdb")
    keys = set()
    for region in cfg["regions"]:
        load_tracts(con, raw, region)
        box = con.sql(
            "SELECT min(ST_XMin(geometry)), min(ST_YMin(geometry)), "
            "max(ST_XMax(geometry)), max(ST_YMax(geometry)) FROM tracts"
        ).fetchone()
        keys |= globalml.quadkeys(*box, ext["globalml_zoom"])
    files = globalml.download(
        ext["globalml_index_url"], ext["globalml_location"], keys, Path("/tmp/globalml")
    )
    print(f"globalml: {len(keys)} quadkeys, {len(files)} files", flush=True)
    counts = globalml.tract_counts(
        con, files, raw, cfg["regions"], scored_tracts(raw, cfg["regions"])
    )
    counts.to_parquet(out / "globalml_tracts.parquet", index=False)
    summary = {
        "run_id": run["run_id"],
        "quadkeys": len(keys),
        "files": len(files),
        "totals_by_region": counts.groupby("region")["ms_n_globalml"].sum().to_dict(),
        "zero_share": float((counts["ms_n_globalml"] == 0).mean()),
    }
    (out / "GLOBALML_MANIFEST.json").write_text(json.dumps(summary, indent=2))
    write_run_meta(out, run, code, started)
    print(json.dumps(summary, indent=2), flush=True)
