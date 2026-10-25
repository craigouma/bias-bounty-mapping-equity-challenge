import numpy as np
import pandas as pd

from bbme.components.building import building_draws
from bbme.components.poi import poi_draws
from bbme.components.transport import calibrate, transport_draws
from bbme.composite import monte_carlo, plug_in, shrink

POI_SUBS = ["fire", "ems", "schools", "cbp"]


def predict(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, dict]:
    """Component estimates and the composite expectation for every tract.

    Each component draws from its own Generator spawned from the config seed, consumed chunk by
    chunk in row order: a rerun with the same config and features reproduces every value, and
    changing one component's estimator never moves another component's draws. With
    `poi.mode: constant` (ablation H-P0) every tract's POI value is its region's mean POI
    point estimate, while POI definedness is unchanged.
    """
    rngs = dict(
        zip(
            ["transport", "building", "poi"],
            [np.random.default_rng(c) for c in np.random.SeedSequence(cfg["seed"]).spawn(3)],
            strict=True,
        )
    )
    s = cfg["mc_draws"]
    cal = calibrate(df, cfg)
    constant_poi = None
    if cfg["poi"]["mode"] == "constant":
        pilot, _ = poi_draws(df, cfg, np.random.default_rng(cfg["seed"] + 1), 200)
        constant_poi = pd.Series(pilot.point).groupby(df["region"].to_numpy()).transform("mean")
    frames = []
    for start in range(0, len(df), cfg["chunk_rows"]):
        chunk = df.iloc[start : start + cfg["chunk_rows"]].reset_index(drop=True)
        draws = {
            "transport": transport_draws(chunk, cfg, cal, rngs["transport"], s),
            "building": building_draws(chunk, cfg, rngs["building"], s),
        }
        draws["poi"], sub = poi_draws(chunk, cfg, rngs["poi"], s)
        if constant_poi is not None:
            level = constant_poi.iloc[start : start + len(chunk)].to_numpy()
            draws["poi"].values = np.broadcast_to(level[:, None], (len(chunk), s))
            draws["poi"].point = level
        y_mc, kept = monte_carlo(draws)
        out = pd.DataFrame(
            {"GEOID": chunk["GEOID"], "y_mc": y_mc, "y_plugin": plug_in(draws), "kept": kept}
        )
        for name, d in draws.items():
            out[f"{name}_point"] = d.point
            out[f"{name}_p"] = d.p_defined
        for name in POI_SUBS:
            out[f"poi_{name}_point"], out[f"poi_{name}_p"] = sub[name]
        frames.append(out)
    comp = pd.concat(frames, ignore_index=True)
    comp["coverage_gap_score"] = shrink(comp["y_mc"].to_numpy(), cfg["alpha"])
    comp.insert(1, "region", df["region"].to_numpy())
    return comp, {"calibration": cal.reset_index().to_dict(orient="records")}


def submission_frame(comp: pd.DataFrame) -> pd.DataFrame:
    """Writer input: point gaps and flags at p >= 0.5 for every component and POI sub-gap."""
    pred = comp[["GEOID", "coverage_gap_score"]].copy()
    for name in ["transport", "building"]:
        pred[f"{name}_gap"] = comp[f"{name}_point"]
        pred[f"{name}_defined"] = comp[f"{name}_p"] >= 0.5
    for name in POI_SUBS:
        pred[f"poi_gap_{name}"] = comp[f"poi_{name}_point"]
        pred[f"poi_defined_{name}"] = comp[f"poi_{name}_p"] >= 0.5
    top = ["transport_defined", "building_defined"]
    poi_any = pred[[f"poi_defined_{n}" for n in POI_SUBS]].any(axis=1)
    none = ~(pred[top].any(axis=1) | poi_any)
    pred.loc[none, "building_defined"] = True
    return pred


def metrics(comp: pd.DataFrame) -> dict:
    cols = ["coverage_gap_score", "y_plugin", "transport_point", "transport_p", "building_point"]
    cols += ["building_p", "poi_point", "poi_p"]
    by_region = comp.groupby("region")[cols].mean().round(4).to_dict(orient="index")
    q = comp["coverage_gap_score"].quantile([0.1, 0.25, 0.5, 0.75, 0.9, 0.99]).round(4)
    return {
        "mean_score": float(comp["coverage_gap_score"].mean()),
        "rms_score": float(np.sqrt((comp["coverage_gap_score"] ** 2).mean())),
        "score_quantiles": {str(k): float(v) for k, v in q.items()},
        "min_kept_draws": int(comp["kept"].min()),
        "non_finite": int((~np.isfinite(comp.select_dtypes(include=[np.number]))).sum().sum()),
        "by_region": by_region,
    }
