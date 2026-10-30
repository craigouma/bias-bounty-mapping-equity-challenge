"""Publish the HUD USPS ZIP-TRACT crosswalk as a private Kaggle dataset.

Source: HUD USPS ZIP Code Crosswalk, DataLumos project 219325 V2, file
`ZIP-Tract/ZIP_TRACT_<MMYYYY>.xlsx`, placed in data/hud_crosswalk/. The xlsx is converted to
parquet with ZIP and TRACT kept as text.
"""

import json
import shutil
import sys

import pandas as pd

from bbme.config import ROOT, load
from kaggle_code_push import sh


def main() -> int:
    ext = load("data")["external_reference"]["hud_crosswalk"]
    user = load("kaggle")["username"]
    ref = f"{user}/{ext['dataset']}"
    src = ROOT / "data" / "hud_crosswalk" / f"ZIP_TRACT_{ext['quarter']}.xlsx"
    out = ROOT / load("paths")["hud_build"]
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    df = pd.read_excel(src, dtype={"ZIP": str, "TRACT": str})
    df.columns = [c.upper() for c in df.columns]
    cols = ["ZIP", "TRACT", "RES_RATIO", "BUS_RATIO", "OTH_RATIO", "TOT_RATIO"]
    df[cols].to_parquet(out / f"ZIP_TRACT_{ext['quarter']}.parquet", index=False)
    meta = {"title": ext["dataset"], "id": ref, "licenses": [{"name": "other"}]}
    (out / "dataset-metadata.json").write_text(json.dumps(meta, indent=2))
    exists = sh("kaggle", "datasets", "status", ref, check=False).returncode == 0
    if exists:
        cmd = ["kaggle", "datasets", "version", "-p", str(out), "-m", ext["quarter"]]
    else:
        cmd = ["kaggle", "datasets", "create", "-p", str(out)]
    print(sh(*cmd).stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
