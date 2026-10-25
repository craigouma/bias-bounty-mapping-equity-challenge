import json
import shutil
import sys
import time
from datetime import UTC, datetime
from pathlib import Path


def main(run: dict, code: Path) -> None:
    from bbme import guard
    from bbme.config import load
    from bbme.ingest import sync
    from bbme.runtime import WORKING, write_run_meta

    started = time.time()
    cfg = load("data")
    raw = WORKING / "raw"
    audit = WORKING / "audit"
    audit.mkdir(parents=True, exist_ok=True)

    objects = sync.list_bucket(cfg)
    listed_at = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [f"{size} {key}" for key, size in sorted(objects.items())]
    (audit / "bucket_listing.txt").write_text("\n".join(lines) + "\n")
    denied = guard.denied_keys(objects)
    if denied:
        sys.exit(
            "denylisted files exist in the bucket, stopping before any download:\n"
            + "\n".join(denied)
        )

    selected = {k: v for k, v in objects.items() if sync.wanted(k, cfg["regions"])}
    local = sync.sync(cfg, selected, raw)
    files = [
        {
            "key": k,
            "bucket_bytes": selected[k],
            "local_bytes": local[k],
            "match": local[k] == selected[k],
        }
        for k in sorted(selected)
    ]
    manifest = {
        "bucket": cfg["bucket"],
        "listed_at_utc": listed_at,
        "objects_listed": len(objects),
        "files_synced": len(files),
        "bytes_synced": sum(f["local_bytes"] for f in files),
        "overture_release_expected": cfg["overture_release"],
        "denylisted_keys": denied,
        "all_match": all(f["match"] for f in files),
        "files": files,
    }
    (audit / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    if not manifest["all_match"]:
        sys.exit(
            "byte counts still differ after retries: "
            + str([f["key"] for f in files if not f["match"]])
        )
    shutil.copyfile(raw / "README.md", audit / "README.md")
    for region in cfg["regions"]:
        name = f"{region}-sample-submission.csv"
        shutil.copyfile(raw / "reference" / region / name, audit / name)
    write_run_meta(audit, run, code, started)
    print(f"synced {len(files)} files, {manifest['bytes_synced'] / 1e9:.2f} GB", flush=True)
