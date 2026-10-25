from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.features import layer_path


def _dataset_cases(datasets: dict[str, str]) -> str:
    whens = " ".join(
        f"WHEN dataset ILIKE '{pattern}' THEN '{key}'" for key, pattern in datasets.items()
    )
    return f"CASE {whens} ELSE 'other' END"


def building_features(
    con: duckdb.DuckDBPyConnection, raw: Path, region: str, cfg: dict
) -> pd.DataFrame:
    """Per-tract building counts, source mix, footprint sizes and the H-B2 suppression estimate.

    Requires table `tracts`. A footprint belongs to the tract holding its centroid; the
    intersects count is kept as a diagnostic for footprints straddling tract edges.
    """
    datasets = cfg["building_datasets"]
    con.sql(
        f"""
        CREATE OR REPLACE TEMP TABLE b AS
        SELECT id, {_dataset_cases(datasets)} AS src, sources[1].confidence AS confidence,
               {db.area_m2("geometry")} AS area, ST_Centroid(geometry) AS centroid, geometry
        FROM (SELECT *, sources[1].dataset AS dataset
              FROM {db.scan(layer_path(raw, region, "buildings"))})
        """
    )
    db.assert_finite(con, "b", ["area"])
    con.sql(
        """
        CREATE OR REPLACE TEMP TABLE bt AS
        SELECT t.GEOID, b.id, b.src, b.area, b.confidence
        FROM b JOIN tracts t ON ST_Intersects(t.geometry, b.centroid)
        """
    )
    ml = ", ".join(f"'{k}'" for k in cfg["ml_datasets"])
    per_source = ", ".join(
        f"count(*) FILTER (WHERE src = '{k}') AS bld_n_{k}" for k in [*datasets, "other"]
    )
    large = []
    for thr in cfg["osm_large_footprint_m2"]:
        osm_large = f"src = 'osm' AND area > {thr}"
        large += [
            f"count(*) FILTER (WHERE {osm_large}) AS bld_osm_large_n_{thr}",
            f"coalesce(sum(area) FILTER (WHERE {osm_large}), 0) AS bld_osm_large_area_{thr}",
            f"coalesce(sum(greatest(area / ml_median - 1, 0)) FILTER (WHERE {osm_large}), 0) "
            f"AS bld_suppressed_{thr}",
        ]
    counts = con.sql(
        f"""
        WITH region_ml AS (SELECT median(area) AS m FROM bt WHERE src IN ({ml})),
             tract_ml AS (SELECT GEOID, median(area) AS m, count(*) AS n
                          FROM bt WHERE src IN ({ml}) GROUP BY GEOID),
             x AS (SELECT bt.*,
                          CASE WHEN tract_ml.n >= {cfg["min_ml_for_tract_median"]}
                               THEN tract_ml.m ELSE region_ml.m END AS ml_median
                   FROM bt LEFT JOIN tract_ml USING (GEOID), region_ml)
        SELECT GEOID,
               count(*) AS bld_n,
               {per_source},
               count(*) FILTER (WHERE src IN ({ml})) / count(*) AS bld_ml_share,
               count(*) FILTER (WHERE src = 'osm') / count(*) AS bld_osm_share,
               median(area) AS bld_area_median,
               quantile_cont(area, 0.9) AS bld_area_p90,
               median(area) FILTER (WHERE src IN ({ml})) AS bld_area_median_ml,
               median(area) FILTER (WHERE src = 'osm') AS bld_area_median_osm,
               sum(area) AS bld_area_total,
               avg(confidence) AS bld_ml_confidence_mean,
               {", ".join(large)}
        FROM x GROUP BY GEOID
        """
    ).df()
    intersects = con.sql(
        """
        SELECT t.GEOID, count(*) AS bld_n_intersects
        FROM b JOIN tracts t ON ST_Intersects(t.geometry, b.geometry) GROUP BY t.GEOID
        """
    ).df()
    return counts.merge(intersects, on="GEOID", how="outer")
