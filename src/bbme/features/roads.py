from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.features import layer_path

CLIP = "ST_CollectionExtract(ST_Intersection(s.geometry, t.geometry), 2)"


def _group_case(groups: dict[str, str]) -> str:
    whens = " ".join(
        f"WHEN regexp_full_match(coalesce(x.network, ''), '{pattern}') THEN '{name}'"
        for name, pattern in groups.items()
    )
    return f"CASE {whens} ELSE 'other' END"


def _set_flag(members: list[str]) -> str:
    return "(" + " OR ".join(f"g_{m}" for m in members) + ")"


def load_segments(con: duckdb.DuckDBPyConnection, raw: Path, region: str, cfg: dict) -> None:
    """Create table `seg`: one row per scored-layer road segment with route-group flags.

    Each route network maps to the first group whose pattern matches it, so overlapping
    patterns never double-assign a network.
    """
    groups = [*cfg["route_groups"], "other"]
    flags = ", ".join(f"coalesce(list_contains(groups, '{g}'), false) AS g_{g}" for g in groups)
    con.sql(
        f"""
        CREATE OR REPLACE TEMP TABLE seg AS
        SELECT id, class, coalesce(subclass = 'link', false) AS is_link,
               names.primary IS NULL AS unnamed,
               geometry, {db.length_m("geometry")} AS full_len, {flags}
        FROM (SELECT *, list_transform(routes, x -> {_group_case(cfg["route_groups"])}) AS groups
              FROM {db.scan(layer_path(raw, region, "roads"))})
        """
    )


def road_features(
    con: duckdb.DuckDBPyConnection, raw: Path, region: str, cfg: dict
) -> pd.DataFrame:
    """Per-tract clipped road lengths in metres, by class, route group and reference proxy set.

    Requires table `tracts`. Lengths are geodesic metres of each segment clipped to the tract,
    the organisers' Overture side being the named classes motorway, trunk, primary, secondary.
    `_unclipped` columns sum whole segments that touch the tract (H-T5); `link` columns isolate
    ramps (Overture subclass link), which the TIGER primary and secondary classes exclude (H-T4).
    """
    load_segments(con, raw, region, cfg)
    con.sql(
        f"""
        CREATE OR REPLACE TEMP TABLE rc AS
        SELECT t.GEOID, s.* EXCLUDE (geometry), {db.length_m(CLIP)} AS len
        FROM seg s JOIN tracts t ON ST_Intersects(t.geometry, s.geometry)
        """
    )
    db.assert_finite(con, "rc", ["len"])
    named = ", ".join(f"'{c}'" for c in cfg["named_road_classes"])
    is_named = f"class IN ({named})"
    is_mt = "class IN ('motorway', 'trunk')"
    cols = [
        f"sum(len) FILTER (WHERE class = '{c}') AS road_len_{c}"
        for c in cfg["drivable_road_classes"]
    ]
    cols += [
        f"sum(len) FILTER (WHERE {is_named} AND is_link) AS road_named_link_len",
        f"sum(full_len) FILTER (WHERE {is_named}) AS road_named_unclipped_len",
        "sum(len) AS road_len_total",
        "sum(len) FILTER (WHERE unnamed) AS road_len_unnamed",
        f"sum(len) FILTER (WHERE {is_named}) AS road_named_len",
        f"sum(len) FILTER (WHERE {is_named} AND unnamed) AS road_named_unnamed_len",
        "count(DISTINCT id) AS road_segments",
    ]
    cols += [
        f"sum(len) FILTER (WHERE g_{g}) AS road_route_{g}_len"
        for g in [*cfg["route_groups"], "other"]
    ]
    for name, members in cfg["reference_sets"].items():
        ref = _set_flag(members)
        cols += [
            f"sum(len) FILTER (WHERE {ref}) AS road_ref{name}_len",
            f"sum(len) FILTER (WHERE {ref} OR {is_mt}) AS road_ref{name}mt_len",
            f"sum(len) FILTER (WHERE ({ref} OR {is_mt}) AND {is_named}) "
            f"AS road_ref{name}mt_named_len",
            f"sum(len) FILTER (WHERE ({ref} OR {is_mt}) AND NOT is_link) "
            f"AS road_ref{name}mt_nolink_len",
            f"sum(full_len) FILTER (WHERE {ref} OR {is_mt}) AS road_ref{name}mt_unclipped_len",
        ]
    df = con.sql(f"SELECT GEOID, {', '.join(cols)} FROM rc GROUP BY GEOID").df()
    return df.merge(_buffer_features(con, cfg, is_named, is_mt), on="GEOID", how="outer")


def _buffer_features(
    con: duckdb.DuckDBPyConnection, cfg: dict, is_named: str, is_mt: str
) -> pd.DataFrame:
    """Road length inside each tract grown outward by d metres (H-T1 boundary double counting).

    A highway drawn just outside a tract edge counts here but not in the tract itself; the
    difference against the unbuffered length is the boundary-hugging length a reference that
    follows tract edges would count in both neighbours.
    """
    sets = {n: _set_flag(m) for n, m in cfg["reference_sets"].items()}
    keep = " OR ".join([is_named, is_mt, *sets.values()])
    out = None
    for d in cfg["boundary_distances_m"]:
        con.sql(
            f"""
            CREATE OR REPLACE TEMP TABLE tb AS
            SELECT GEOID, ST_Transform(ST_Buffer({db.to_albers("geometry")}, {d}),
                                       'EPSG:5070', 'EPSG:4326', always_xy := true) AS geometry
            FROM tracts
            """
        )
        cols = [f"sum(len) FILTER (WHERE {is_named}) AS road_buf{d}_named_len"]
        cols += [
            f"sum(len) FILTER (WHERE {f} OR {is_mt}) AS road_buf{d}_ref{n}mt_len"
            for n, f in sets.items()
        ]
        df = con.sql(
            f"""
            WITH c AS (SELECT t.GEOID, s.* EXCLUDE (geometry), {db.length_m(CLIP)} AS len
                       FROM (SELECT * FROM seg WHERE {keep}) s
                       JOIN tb t ON ST_Intersects(t.geometry, s.geometry))
            SELECT GEOID, {", ".join(cols)} FROM c GROUP BY GEOID
            """
        ).df()
        out = df if out is None else out.merge(df, on="GEOID", how="outer")
    return out
