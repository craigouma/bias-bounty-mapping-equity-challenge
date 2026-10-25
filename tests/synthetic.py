"""A two-tract raw tree with the real layer names and nested Overture columns.

Tract A 04013000100 spans lon -112.10 to -112.05; tract B 04013990000 (a 99xx water tract)
spans -112.05 to -112.00; both span lat 33.40 to 33.45. A motorway runs along their shared edge.
"""

from pathlib import Path

from bbme import db
from bbme.config import load

REGION = "maricopa-az"
TRACT_A = "04013000100"
TRACT_B = "04013990000"
SQUARES = {
    TRACT_A: (-112.10, 33.40, -112.05, 33.45),
    TRACT_B: (-112.05, 33.40, -112.00, 33.45),
}


def _box(x0, y0, x1, y1) -> str:
    return f"POLYGON(({x0} {y0},{x1} {y0},{x1} {y1},{x0} {y1},{x0} {y0}))"


def _sources(dataset: str, confidence: str = "NULL") -> str:
    return (
        f"[struct_pack(property := '', dataset := '{dataset}', license := NULL::VARCHAR, "
        f"record_id := 'r', update_time := '2026-08-01T00:00:00Z', "
        f'confidence := {confidence}::DOUBLE, "between" := NULL::DOUBLE[], '
        f"provider := NULL::VARCHAR, resource := NULL::VARCHAR, version := '1')]"
    )


def _names(name: str | None) -> str:
    value = f"'{name}'" if name else "NULL::VARCHAR"
    return f'struct_pack("primary" := {value}, common := NULL::MAP(VARCHAR, VARCHAR))'


def _write(con, rows: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    union = " UNION ALL ".join(rows)
    con.sql(
        f"COPY (SELECT *, struct_pack(xmin := ST_XMin(geometry), ymin := ST_YMin(geometry), "
        f"xmax := ST_XMax(geometry), ymax := ST_YMax(geometry)) AS bbox FROM ({union})) "
        f"TO '{path}' (FORMAT parquet)"
    )


def _road(i, cls, name, routes, wkt, dataset="OpenStreetMap") -> str:
    route_list = (
        "["
        + ", ".join(
            f"struct_pack(name := NULL::VARCHAR, network := '{n}', ref := '{r}', "
            f'symbol := NULL::VARCHAR, wikidata := NULL::VARCHAR, "between" := NULL::DOUBLE[])'
            for n, r in routes
        )
        + "]"
        if routes
        else "NULL"
    )
    if not routes:
        route_list = (
            "NULL::STRUCT(name VARCHAR, network VARCHAR, ref VARCHAR, symbol VARCHAR, "
            "wikidata VARCHAR, between DOUBLE[])[]"
        )
    return (
        f"SELECT 'seg{i}' AS id, {_names(name)} AS names, 'road' AS subtype, '{cls}' AS class, "
        f"NULL::VARCHAR AS subclass, {route_list} AS routes, {_sources(dataset)} AS sources, "
        f"1 AS version, ST_GeomFromText('{wkt}') AS geometry"
    )


def build_raw(root: Path) -> Path:
    con = db.connect()
    ref = root / "reference" / REGION
    strata = root / "strata" / REGION

    roads = [
        _road(1, "motorway", "I 10", [("US:I", "10")], "LINESTRING(-112.05 33.40, -112.05 33.45)"),
        _road(
            2, "primary", "Main St", [("US:AZ", "87")], "LINESTRING(-112.09 33.41, -112.06 33.44)"
        ),
        _road(3, "residential", None, [], "LINESTRING(-112.04 33.41, -112.01 33.41)"),
        _road(
            4, "tertiary", "FM 1", [("US:TX:FM", "1")], "LINESTRING(-112.09 33.42, -112.07 33.42)"
        ),
    ]
    _write(con, roads, ref / f"{REGION}-overture-roads.parquet")
    service = _road(5, "service", None, [], "LINESTRING(-112.08 33.43, -112.08 33.44)")
    _write(con, [*roads, service], ref / f"{REGION}-overture-roads-unfiltered.parquet")

    rail = [_road(9, "standard_gauge", None, [], "LINESTRING(-112.10 33.405, -112.00 33.405)")]
    _write(con, rail, ref / f"{REGION}-overture-rail.parquet")

    buildings = []
    for i, (x, dataset) in enumerate(
        [
            (-112.09, "OpenStreetMap"),
            (-112.08, "Microsoft ML Buildings"),
            (-112.07, "Microsoft ML Buildings"),
            (-112.03, "OpenStreetMap"),
        ]
    ):
        buildings.append(
            f"SELECT 'b{i}' AS id, {_names(None)} AS names, {_sources(dataset)} AS sources, "
            f"NULL::VARCHAR AS subtype, NULL::VARCHAR AS class, false AS has_parts, 1 AS version, "
            f"ST_GeomFromText('{_box(x, 33.42, x + 0.0003, 33.4203)}') AS geometry"
        )
    _write(con, buildings, ref / f"{REGION}-overture-buildings.parquet")

    places = []
    for i, (x, cat, basic) in enumerate(
        [
            (-112.09, "fire_department", "fire_station"),
            (-112.08, "elementary_school", "school"),
            (-112.07, "restaurant", "restaurant"),
            (-112.06, "hospital", "hospital"),
        ]
    ):
        places.append(
            f"SELECT 'p{i}' AS id, "
            f"struct_pack(\"primary\" := '{cat}', alternate := NULL::VARCHAR[]) "
            f"AS categories, 0.9 AS confidence, {_names('Place ' + str(i))} AS names, "
            f"{_sources('meta', '0.9')} AS sources, 'open' AS operating_status, "
            f"'{basic}' AS basic_category, struct_pack(\"primary\" := '{cat}', "
            f"hierarchy := ['x', '{cat}'], alternates := NULL::VARCHAR[]) AS taxonomy, "
            f"1 AS version, "
            f"ST_Point({x}, 33.43) AS geometry"
        )
    _write(con, places, ref / f"{REGION}-overture-pois.parquet")

    infra = [
        f"SELECT 'i1' AS id, {_sources('OpenStreetMap')} AS sources, {_names('Stop')} AS names, "
        f"'transit' AS subtype, 'bus_stop' AS class, 1 AS version, "
        f"ST_Point(-112.08, 33.41) AS geometry"
    ]
    _write(con, infra, ref / f"{REGION}-overture-infrastructure.parquet")

    tracts = [
        f"SELECT '{g}' AS GEOID, '04' AS STATEFP, '013' AS COUNTYFP, {pop} AS pop_total, "
        f"{aland} AS ALAND, 1.0 AS frac_inside_aoi, ST_GeomFromText('{_box(*box)}') AS geometry"
        for (g, box), pop, aland in zip(
            SQUARES.items(), [1200, 0], [20_000_000, 1_000_000], strict=True
        )
    ]
    _write(con, tracts, strata / f"{REGION}-census-tracts.parquet")
    acs = [
        f"SELECT '{g}' AS GEOID, {hu} AS housing_units, ST_GeomFromText('{_box(*box)}') AS geometry"
        for (g, box), hu in zip(SQUARES.items(), [500, 0], strict=True)
    ]
    _write(con, acs, ref / f"{REGION}-census-acs-housing.parquet")

    strata_table = root / "strata" / REGION / f"{REGION}-strata-tract-table.parquet"
    context = {"COUNTYFP": "'013'", "ALAND": 20_000_000, "pop_total": 1200, "ur_class": "'urban'"}
    columns = load("features")["strata_columns"]
    rows = []
    for geoid, scale in [(TRACT_A, 1), (TRACT_B, 0)]:
        values = [f"'{geoid}' AS GEOID"]
        for c in columns:
            v = context.get(c, 0.5)
            values.append(f'{v if scale or isinstance(v, str) else 0} AS "{c}"')
        values.append(f"{bool(scale)} AS svi_covered")
        rows.append("SELECT " + ", ".join(values))
    con.sql(f"COPY ({' UNION ALL '.join(rows)}) TO '{strata_table}' (FORMAT parquet)")
    for table, col in [
        ("mtbs-tract-table", "mtbs_wildfire_burned_pct_land_2015_2023"),
        ("nifc-tract-table", "nifc_wildfire_burned_pct_land_2015_2025"),
    ]:
        path = root / "strata" / REGION / f"{REGION}-{table}.parquet"
        con.sql(
            f"COPY (SELECT * FROM (VALUES ('{TRACT_A}', 0.0), ('{TRACT_B}', 12.5)) "
            f"t(GEOID, {col})) TO '{path}' (FORMAT parquet)"
        )
    national = root / "strata" / "national" / "national-census-tract-table.parquet"
    national.parent.mkdir(parents=True, exist_ok=True)
    con.sql(
        f"COPY (SELECT * FROM (VALUES ('{TRACT_A}', 1200, 20000000, 0), "
        f"('{TRACT_B}', 0, 1000000, 19000000)) t(GEOID, pop_total, ALAND, AWATER)) "
        f"TO '{national}' (FORMAT parquet)"
    )
    (ref / f"{REGION}-sample-submission.csv").write_text(
        f"GEOID,coverage_gap_score\n{TRACT_A},0.0\n{TRACT_B},0.0\n"
    )
    return root
