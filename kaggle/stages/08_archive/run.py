import json
import time
from pathlib import Path


def main(run: dict, code: Path) -> None:
    from bbme import db
    from bbme.config import load
    from bbme.reference import hifld
    from bbme.regions import scored_tracts
    from bbme.runtime import WORKING, upstream, write_run_meta

    started = time.time()
    cfg = load("data")
    raw = upstream("audit/MANIFEST.json") / "raw"
    out = WORKING / "archive"
    out.mkdir(parents=True, exist_ok=True)
    con = db.connect(memory_limit="22GB", threads=4, temp_dir="/tmp/duckdb")
    layers = hifld.download(cfg, Path("/tmp/external"))
    scored = scored_tracts(raw, cfg["regions"])
    counts = hifld.tract_counts(con, layers, raw, cfg["regions"], scored)
    counts.to_parquet(out / "hifld_reference_tracts.parquet", index=False)
    cols = [c for c in counts.columns if c.startswith("hifld_")]
    summary = {
        "run_id": run["run_id"],
        "files": {k: p.stat().st_size for k, p in layers.items()},
        "totals_by_region": counts.groupby("region")[cols].sum().to_dict(),
        "tracts_with": {c: int((counts[c] > 0).sum()) for c in cols},
    }
    (out / "ARCHIVE_MANIFEST.json").write_text(json.dumps(summary, indent=2, default=int))
    write_run_meta(out, run, code, started)
    print(json.dumps(summary, indent=2, default=int), flush=True)
