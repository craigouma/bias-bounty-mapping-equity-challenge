import re
from pathlib import Path

import numpy as np
import pandas as pd

from bbme import guard
from bbme.geoid import assert_geoids

COLUMNS = [
    "GEOID",
    "coverage_gap_score",
    "region",
    "transport_gap",
    "transport_defined",
    "building_gap",
    "building_defined",
    "poi_gap",
    "poi_defined",
    "poi_gap_fire",
    "poi_defined_fire",
    "poi_gap_ems",
    "poi_defined_ems",
    "poi_gap_schools",
    "poi_defined_schools",
    "poi_gap_cbp",
    "poi_defined_cbp",
]
GAP_FLAGS = {
    "transport_gap": "transport_defined",
    "building_gap": "building_defined",
    "poi_gap": "poi_defined",
    "poi_gap_fire": "poi_defined_fire",
    "poi_gap_ems": "poi_defined_ems",
    "poi_gap_schools": "poi_defined_schools",
    "poi_gap_cbp": "poi_defined_cbp",
}
FLOATS = ["coverage_gap_score", *GAP_FLAGS]
FLAGS = list(GAP_FLAGS.values())
TOP_FLAGS = ["transport_defined", "building_defined", "poi_defined"]
INPUT_FLAGS = [f for f in FLAGS if f != "poi_defined"]
FACILITY_TYPES = ["fire", "ems", "schools"]
PLAIN_DECIMAL = re.compile(r"\d+\.\d+")
TOLERANCE = 1e-8


def read_text_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(guard.artifact(path), dtype=str, keep_default_na=False)
    assert_geoids(df["GEOID"])
    return df


def poi_rollup(gaps: pd.DataFrame, flags: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """POI point estimate from its sub-columns under the organisers' rules.

    The facilities half is the mean of the defined fire, EMS and school gaps; `poi_gap` is
    the mean of the defined halves (facilities, establishments); `poi_defined` is true when
    any sub-gap is defined. Undefined sub-gaps carry 0 and never enter a mean.
    """
    fac_gap = np.stack([gaps[f"poi_gap_{t}"] for t in FACILITY_TYPES], axis=1)
    fac_def = np.stack([flags[f"poi_defined_{t}"] for t in FACILITY_TYPES], axis=1)
    n_fac = fac_def.sum(axis=1)
    facilities = np.divide(
        (fac_gap * fac_def).sum(axis=1), n_fac, out=np.zeros(len(gaps)), where=n_fac > 0
    )
    halves_def = np.stack([n_fac > 0, flags["poi_defined_cbp"].to_numpy(bool)], axis=1)
    halves = np.stack([facilities, gaps["poi_gap_cbp"].to_numpy(float)], axis=1)
    n_halves = halves_def.sum(axis=1)
    poi = np.divide(
        (halves * halves_def).sum(axis=1), n_halves, out=np.zeros(len(gaps)), where=n_halves > 0
    )
    return pd.Series(poi, index=gaps.index), pd.Series(n_halves > 0, index=gaps.index)


def _format_float(x: float) -> str:
    return np.format_float_positional(x, precision=10, unique=False, fractional=False, trim="0")


def write(pred: pd.DataFrame, sample: pd.DataFrame, path: Path) -> Path:
    """Write a submission in the sample's exact shape.

    `pred` holds GEOID, coverage_gap_score and the transport, building and four POI
    sub-columns (gap floats, defined booleans). Region and row order come from the sample;
    `poi_gap` and `poi_defined` are derived from the sub-columns; every undefined gap is
    written as 0.0.
    """
    df = sample[["GEOID", "region"]].merge(pred, on="GEOID", how="left", validate="1:1")
    flags = df[INPUT_FLAGS].astype(bool)
    for gap, flag in GAP_FLAGS.items():
        if flag in flags:
            df[gap] = np.where(flags[flag], df[gap].astype(float), 0.0)
    df["poi_gap"], df["poi_defined"] = poi_rollup(df, flags)
    df[INPUT_FLAGS] = flags
    if df[FLOATS].isna().any().any():
        raise ValueError("missing predictions for some GEOIDs")
    lines = [",".join(COLUMNS)]
    for row in df[COLUMNS].itertuples(index=False):
        cells = []
        for col, value in zip(COLUMNS, row, strict=True):
            if col in FLOATS:
                cells.append(_format_float(float(value)))
            elif col in FLAGS:
                cells.append("True" if value else "False")
            else:
                cells.append(value)
        lines.append(",".join(cells))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("\n".join(lines) + "\n").encode("ascii"))
    return path


def validate(path: Path, sample_path: Path) -> list[str]:
    """Return every rule violation in a submission file; an empty list means valid."""
    raw = guard.artifact(path).read_bytes()
    errors = []
    if b"\r" in raw:
        errors.append("CR line endings present")
    if not raw.endswith(b"\n"):
        errors.append("file does not end with a newline")
    if not raw.isascii():
        errors.append("non-ASCII bytes present")
    header = raw.split(b"\n", 1)[0].decode("ascii", "replace").split(",")
    if header != COLUMNS:
        return [*errors, f"header differs from the sample: {header}"]

    sub = read_text_table(path)
    sample = read_text_table(sample_path)
    if len(sub) != len(sample):
        return [*errors, f"{len(sub)} rows, sample has {len(sample)}"]
    if sub["GEOID"].duplicated().any():
        errors.append("duplicate GEOIDs")
    if not sub["GEOID"].equals(sample["GEOID"]):
        errors.append("GEOID order or set differs from the sample")
    if not sub["region"].equals(sample["region"]):
        errors.append("region values differ from the sample")

    blank = sub.columns[(sub == "").any()].tolist()
    if blank:
        return [*errors, f"blank cells in {blank}"]

    for col in FLOATS:
        bad = ~sub[col].str.fullmatch(PLAIN_DECIMAL)
        if bad.any():
            example = sub[col][bad].iloc[0]
            errors.append(f"{col}: {bad.sum()} cells not plain decimal, e.g. {example}")
    for col in FLAGS:
        bad = ~sub[col].isin(["True", "False"])
        if bad.any():
            errors.append(f"{col}: {bad.sum()} cells not True/False")
    if errors:
        return errors

    gaps = sub[FLOATS].astype(float)
    flags = sub[FLAGS] == "True"
    for col in FLOATS:
        v = gaps[col]
        if not np.isfinite(v).all() or v.lt(0).any() or v.gt(1).any():
            errors.append(f"{col}: values outside [0, 1] or non-finite")
    for gap, flag in GAP_FLAGS.items():
        n = (~flags[flag] & (gaps[gap] != 0)).sum()
        if n:
            errors.append(f"{gap}: {n} undefined rows with a nonzero gap")
    poi, poi_def = poi_rollup(gaps, flags)
    if not poi_def.equals(flags["poi_defined"]):
        errors.append("poi_defined disagrees with the POI sub-flags")
    off = (poi - gaps["poi_gap"]).abs() > TOLERANCE
    if off.any():
        errors.append(f"poi_gap disagrees with its sub-columns in {off.sum()} rows")
    if not flags[TOP_FLAGS].any(axis=1).all():
        errors.append("rows with every top-level component undefined")
    return errors


def assert_valid(path: Path, sample_path: Path) -> None:
    errors = validate(path, sample_path)
    if errors:
        raise ValueError(f"{path} is invalid:\n" + "\n".join(errors))
