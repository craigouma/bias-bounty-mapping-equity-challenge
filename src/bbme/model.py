import numpy as np
import pandas as pd

from bbme.components.building import building_draws
from bbme.components.poi import fire_draws, poi_draws
from bbme.components.transport import calibrate, tiger_draws, transport_draws
from bbme.composite import monte_carlo, plug_in, shrink

POI_SUBS = ["fire", "ems", "schools", "cbp"]


def predict(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, dict]:
    """Component estimates and the composite expectation for every tract.

    Each component draws from its own Generator spawned from the config seed, consumed chunk by
    chunk in row order: a rerun with the same config and features reproduces every value, and
    changing one component's estimator never moves another component's draws. With
    `poi.mode: constant` (ablation H-P0) every tract's POI value is its region's mean POI
    point estimate, while POI definedness is unchanged. With `poi.mode: fire` POI follows the
    fire-station model, rescaled per region so its mean equals that same constant.
    """
    rngs = dict(
        zip(
            ["transport", "building", "poi"],
            [np.random.default_rng(c) for c in np.random.SeedSequence(cfg["seed"]).spawn(3)],
            strict=True,
        )
    )
    s = cfg["mc_draws"]
    use_tiger = cfg["transport"]["source"] == "tiger"
    cal = None if use_tiger else calibrate(df, cfg)
    constant_poi, fire_scale = None, None
    if cfg["poi"]["mode"] in ("constant", "fire"):
        pilot, _ = poi_draws(df, cfg, np.random.default_rng(cfg["seed"] + 1), 200)
        constant_poi = pd.Series(pilot.point).groupby(df["region"].to_numpy()).transform("mean")
        constant_poi = (constant_poi * cfg["poi"]["level"]).clip(0, 1)
    if cfg["poi"]["mode"] == "fire":
        fire_pilot = fire_draws(df, cfg, np.random.default_rng(cfg["seed"] + 2), 200)
        fire_mean = pd.Series(fire_pilot.point).groupby(df["region"].to_numpy()).transform("mean")
        fire_scale = (constant_poi / fire_mean.replace(0, np.nan)).to_numpy()
    frames = []
    for start in range(0, len(df), cfg["chunk_rows"]):
        chunk = df.iloc[start : start + cfg["chunk_rows"]].reset_index(drop=True)
        draws = {
            "transport": tiger_draws(chunk, s)
            if use_tiger
            else transport_draws(chunk, cfg, cal, rngs["transport"], s),
            "building": building_draws(chunk, cfg, rngs["building"], s),
        }
        draws["poi"], sub = poi_draws(chunk, cfg, rngs["poi"], s)
        if fire_scale is not None:
            fire = fire_draws(chunk, cfg, rngs["poi"], s)
            scale = fire_scale[start : start + len(chunk)]
            level = constant_poi.iloc[start : start + len(chunk)].to_numpy()
            usable = np.isfinite(scale)
            k = cfg["poi"]["fire_strength"]
            scaled = np.clip(fire.values * np.nan_to_num(scale)[:, None], 0, 1)
            fire.values = np.where(
                usable[:, None], k * scaled + (1 - k) * level[:, None], level[:, None]
            )
            fire.point = np.where(
                usable,
                k * np.clip(fire.point * np.nan_to_num(scale), 0, 1) + (1 - k) * level,
                level,
            )
            draws["poi"] = fire
        elif constant_poi is not None:
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
    extra = {} if cal is None else {"calibration": cal.reset_index().to_dict(orient="records")}
    return comp, extra


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
