import json
import traceback
from collections.abc import Callable
from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.config import load
from bbme.regions import scored_tracts

FACILITY_PATTERN = (
    "fire|ems|ambulance|paramedic|rescue|emergency|school|college|kindergarten|preschool"
    "|child_care|day_care|education|hospital|police"
)
EDGE_LAYERS = ["buildings", "roads", "pois"]
BBOX_OVERLAP = (
    "f.bbox.xmin <= t.bbox.xmax AND f.bbox.xmax >= t.bbox.xmin "
    "AND f.bbox.ymin <= t.bbox.ymax AND f.bbox.ymax >= t.bbox.ymin"
)


def md(df: pd.DataFrame, digits: int = 3) -> str:
    df = df.round(digits)
    rows = [[str(c) for c in df.columns], ["---"] * df.shape[1]]
    rows += [["" if pd.isna(v) else str(v) for v in r] for r in df.itertuples(index=False)]
    return "\n".join("| " + " | ".join(r) + " |" for r in rows)


class Audit:
    def __init__(self, raw: Path, out: Path, cfg: dict, con: duckdb.DuckDBPyConnection):
        self.raw, self.out, self.con = raw, out, con
        self.regions: list[str] = cfg["regions"]
        self.tables = out / "tables"
        self.tables.mkdir(parents=True, exist_ok=True)
        self.report: list[str] = ["# Data audit", ""]
        self.failures: list[str] = []

    def layer(self, region: str, layer: str) -> str:
        return db.scan(self.raw / "reference" / region / f"{region}-overture-{layer}.parquet")

    def strata(self, region: str, table: str) -> str:
        return db.scan(self.raw / "strata" / region / f"{region}-{table}.parquet")

    def df(self, sql: str) -> pd.DataFrame:
        return self.con.sql(sql).df()

    def save(self, name: str, df: pd.DataFrame) -> pd.DataFrame:
        df.to_csv(self.tables / f"{name}.csv", index=False)
        return df

    def per_region(self, sql_for: Callable[[str], str]) -> pd.DataFrame:
        frames = [self.df(sql_for(r)).assign(region=r) for r in self.regions]
        return pd.concat(frames, ignore_index=True)

    def section(self, title: str, fn: Callable[[], list[str]]) -> None:
        self.report += [f"## {title}", ""]
        try:
            self.report += fn()
        except Exception:
            self.failures.append(title)
            self.report += ["Section failed:", "", "```", traceback.format_exc(), "```"]
        self.report.append("")
        print(f"audit: {title} done", flush=True)

    def run(self) -> list[str]:
        self.section("Files and schemas", self.schemas)
        self.section("Geodesic length check", self.length_check)
        self.section("Overture release evidence", self.release)
        self.section("Scored tracts and tract polygons", self.tract_checks)
        self.section("Road classes", self.road_classes)
        self.section("Route networks", self.routes)
        self.section("Place categories", self.places)
        self.section("Upstream sources", self.sources)
        self.section("Buildings", self.buildings)
        self.section("Infrastructure and rail", self.infrastructure)
        self.section("ACS housing", self.acs)
        self.section("Strata columns", self.strata_columns)
        self.section("Edge-case tracts", self.edge_tracts)
        (self.out / "data_audit.md").write_text("\n".join(self.report) + "\n")
        return self.failures

    def schemas(self) -> list[str]:
        result = {}
        for path in sorted(self.raw.rglob("*.parquet")):
            src = db.scan(path)
            cols = self.con.sql(f"DESCRIBE SELECT * FROM {src}").fetchall()
            result[str(path.relative_to(self.raw))] = {
                "bytes": path.stat().st_size,
                "rows": self.con.sql(f"SELECT count(*) FROM {src}").fetchone()[0],
                "columns": [[c[0], c[1]] for c in cols],
            }
        (self.out / "schemas.json").write_text(json.dumps(result, indent=2))
        table = pd.DataFrame(
            [(k, v["rows"], len(v["columns"]), v["bytes"]) for k, v in result.items()],
            columns=["file", "rows", "columns", "bytes"],
        )
        return [md(table)]

    def length_check(self) -> list[str]:
        from pyproj import Geod

        region = self.regions[0]
        geom, got = self.con.sql(
            f"SELECT ST_AsGeoJSON(geometry), {db.length_m('geometry')} "
            f"FROM {self.layer(region, 'roads')} WHERE class = 'motorway' ORDER BY id LIMIT 1"
        ).fetchone()
        lons, lats = zip(*json.loads(geom)["coordinates"], strict=True)
        expected = Geod(ellps="WGS84").line_length(lons, lats)
        rel = abs(got - expected) / expected
        if rel > 1e-3:
            raise AssertionError(f"duckdb {got} m against pyproj {expected} m")
        return [
            f"One {region} motorway segment: DuckDB {got:.2f} m, pyproj {expected:.2f} m, "
            f"relative difference {rel:.2e}."
        ]

    def release(self) -> list[str]:
        df = self.per_region(
            lambda r: " UNION ALL ".join(
                f"SELECT '{layer}' AS layer, max(s.update_time) AS max_update_time, "
                f"count(DISTINCT s.version) AS source_versions "
                f"FROM {self.layer(r, layer)}, unnest(sources) AS t(s)"
                for layer in ["roads", "pois", "infrastructure"]
            )
        )
        pois = self.raw / "reference" / self.regions[0] / f"{self.regions[0]}-overture-pois.parquet"
        kv = self.df(
            "SELECT DISTINCT key::VARCHAR AS key FROM "
            + db.scan(pois).replace("read_parquet", "parquet_kv_metadata")
        )
        return [
            f"Parquet key-value metadata keys: {', '.join(kv['key'])}.",
            "",
            md(self.save("release_evidence", df)),
        ]

    def tract_checks(self) -> list[str]:
        scored = scored_tracts(self.raw, self.regions)
        rows = []
        for r in self.regions:
            tracts = self.df(
                f"SELECT GEOID, pop_total, frac_inside_aoi FROM {self.strata(r, 'census-tracts')}"
            )
            want = set(scored.loc[scored["region"] == r, "GEOID"])
            rows.append(
                {
                    "region": r,
                    "scored": len(want),
                    "tract_polygons": len(tracts),
                    "same_set": set(tracts["GEOID"]) == want,
                    "zero_pop": int((tracts["pop_total"] == 0).sum()),
                    "min_frac_inside": tracts["frac_inside_aoi"].min(),
                }
            )
        return [
            f"Scored tracts: {len(scored):,}.",
            "",
            md(self.save("tract_checks", pd.DataFrame(rows))),
        ]

    def road_classes(self) -> list[str]:
        frames = [
            self.per_region(
                lambda r, layer=layer: (
                    f"SELECT '{layer}' AS layer, class, subclass, count(*) AS segments, "
                    f"sum({db.length_m('geometry')}) / 1000 AS km, "
                    "count(*) FILTER (WHERE names.primary IS NULL) AS unnamed_segments "
                    f"FROM {self.layer(r, layer)} GROUP BY ALL"
                )
            )
            for layer in ["roads", "roads-unfiltered"]
        ]
        df = self.save("road_classes", pd.concat(frames, ignore_index=True))
        if df["km"].isna().any() or not df["km"].map(float).map(abs).lt(float("inf")).all():
            raise AssertionError("non-finite road lengths")
        scored = df[df["layer"] == "roads"].pivot_table(
            index="class", columns="region", values="km", aggfunc="sum"
        )
        return ["Scored roads layer, km by class:", "", md(scored.reset_index(), 1)]

    def _segments(self, r: str) -> str:
        return (
            f"SELECT id, class, {db.length_m('geometry')} AS len, routes "
            f"FROM {self.layer(r, 'roads')}"
        )

    def routes(self) -> list[str]:
        networks = self.save(
            "route_networks",
            self.per_region(
                lambda r: (
                    f"""
                WITH e AS (SELECT DISTINCT id, class, len, x.network AS network,
                                  x.between IS NOT NULL AS partial
                           FROM ({self._segments(r)}) s, unnest(routes) AS t(x))
                SELECT network, class, count(DISTINCT id) AS segments, sum(len) / 1000 AS km,
                       count(*) FILTER (WHERE partial) AS partial_entries
                FROM e GROUP BY ALL"""
                )
            ),
        )
        refs = self.save(
            "route_refs_top",
            self.per_region(
                lambda r: (
                    f"""
                WITH e AS (SELECT DISTINCT id, len, x.network AS network, x.ref AS ref
                           FROM ({self._segments(r)}) s, unnest(routes) AS t(x))
                SELECT network, ref, count(*) AS segments, sum(len) / 1000 AS km
                FROM e GROUP BY network, ref ORDER BY km DESC LIMIT 60"""
                )
            ),
        )
        coverage = self.save(
            "route_coverage_by_class",
            self.per_region(
                lambda r: (
                    f"""
                SELECT class, sum(len) / 1000 AS km,
                       coalesce(sum(len) FILTER (WHERE len(routes) > 0), 0) / 1000 AS km_on_route
                FROM ({self._segments(r)}) GROUP BY ALL"""
                )
            ),
        )
        top = networks.groupby(["region", "network"], dropna=False)["km"].sum().reset_index()
        top = top.sort_values(["region", "km"], ascending=[True, False]).groupby("region").head(12)
        return [
            "Route networks by region, top 12 by km:",
            "",
            md(top, 1),
            "",
            "Scored road length on any route, by class:",
            "",
            md(coverage, 1),
            "",
            f"Top refs in tables/route_refs_top.csv ({len(refs)} rows).",
        ]

    def places(self) -> list[str]:
        cats = self.save(
            "place_categories",
            self.per_region(
                lambda r: (
                    "SELECT categories.primary AS category, basic_category, count(*) AS n "
                    f"FROM {self.layer(r, 'pois')} GROUP BY ALL"
                )
            ),
        )
        self.save(
            "place_taxonomy",
            self.per_region(
                lambda r: (
                    "SELECT taxonomy.primary AS taxonomy_primary, "
                    "array_to_string(taxonomy.hierarchy, ' > ') AS hierarchy, count(*) AS n "
                    f"FROM {self.layer(r, 'pois')} GROUP BY ALL"
                )
            ),
        )
        totals = cats.groupby("region")["n"].sum()
        hits = cats[cats["category"].fillna("").str.contains(FACILITY_PATTERN, regex=True)]
        hits = hits.pivot_table(index="category", columns="region", values="n", aggfunc="sum")
        hits = self.save("place_facility_like", hits.fillna(0).astype(int).reset_index())
        groups = []
        for name, members in load("poi_categories")["groups"].items():
            sub = cats[cats["category"].isin(members)].groupby("region")["n"].sum()
            groups.append({"group": name, **sub.to_dict()})
        confidence = self.save(
            "place_confidence",
            self.per_region(
                lambda r: (
                    "SELECT count(*) AS n, count(confidence) AS with_confidence, "
                    "quantile_cont(confidence, 0.1) AS q10, quantile_cont(confidence, 0.5) AS q50, "
                    "quantile_cont(confidence, 0.9) AS q90, "
                    "count(*) FILTER (WHERE operating_status <> 'open') AS not_open "
                    f"FROM {self.layer(r, 'pois')}"
                )
            ),
        )
        return [
            f"Places per region: {totals.to_dict()}.",
            "",
            "Facility-like primary categories (keyword match):",
            "",
            md(hits),
            "",
            "Configured POI groups (configs/poi_categories.yaml):",
            "",
            md(pd.DataFrame(groups)),
            "",
            md(confidence),
        ]

    def sources(self) -> list[str]:
        frames = [
            self.per_region(
                lambda r, layer=layer: (
                    f"SELECT '{layer}' AS layer, sources[1].dataset AS first_dataset, "
                    "count(*) AS n, count(*) FILTER (WHERE len(sources) > 1) AS multi_source, "
                    "count(sources[1].confidence) AS with_confidence "
                    f"FROM {self.layer(r, layer)} GROUP BY ALL"
                )
            )
            for layer in ["buildings", "roads", "pois", "infrastructure"]
        ]
        df = self.save("sources_mix", pd.concat(frames, ignore_index=True))
        df["share"] = df["n"] / df.groupby(["region", "layer"])["n"].transform("sum")
        return [md(df.sort_values(["layer", "region", "n"], ascending=[True, True, False]), 4)]

    def buildings(self) -> list[str]:
        area = db.area_m2("geometry")
        summary = self.save(
            "building_summary",
            self.per_region(
                lambda r: (
                    "SELECT count(*) AS n, count(*) FILTER (WHERE has_parts) AS has_parts, "
                    "count(subtype) AS with_subtype, count(class) AS with_class, "
                    f"quantile_cont({area}, 0.1) AS area_q10, "
                    f"quantile_cont({area}, 0.5) AS area_q50, "
                    f"quantile_cont({area}, 0.9) AS area_q90, "
                    f"quantile_cont({area}, 0.99) AS area_q99 "
                    f"FROM {self.layer(r, 'buildings')}"
                )
            ),
        )
        subtypes = self.save(
            "building_subtypes",
            self.per_region(
                lambda r: (
                    "SELECT subtype, class, count(*) AS n "
                    f"FROM {self.layer(r, 'buildings')} GROUP BY ALL"
                )
            ),
        )
        top = subtypes.sort_values("n", ascending=False).groupby("region").head(8)
        return [md(summary, 1), "", md(top)]

    def infrastructure(self) -> list[str]:
        infra = self.save(
            "infrastructure_classes",
            self.per_region(
                lambda r: (
                    "SELECT subtype, class, count(*) AS n "
                    f"FROM {self.layer(r, 'infrastructure')} GROUP BY ALL"
                )
            ),
        )
        rail = self.save(
            "rail_classes",
            self.per_region(
                lambda r: (
                    f"SELECT class, count(*) AS n, sum({db.length_m('geometry')}) / 1000 AS km "
                    f"FROM {self.layer(r, 'rail')} GROUP BY ALL"
                )
            ),
        )
        wide = infra.pivot_table(
            index=["subtype", "class"], columns="region", values="n", aggfunc="sum"
        )
        return [md(wide.fillna(0).astype(int).reset_index()), "", md(rail, 1)]

    def acs(self) -> list[str]:
        scored = scored_tracts(self.raw, self.regions)
        rows = []
        for r in self.regions:
            path = self.raw / "reference" / r / f"{r}-census-acs-housing.parquet"
            df = self.df(f"SELECT GEOID, housing_units FROM {db.scan(path)}")
            want = set(scored.loc[scored["region"] == r, "GEOID"])
            rows.append(
                {
                    "region": r,
                    "rows": len(df),
                    "scored": len(want),
                    "scored_covered": len(want & set(df["GEOID"])),
                    "null_units": int(df["housing_units"].isna().sum()),
                    "zero_units": int((df["housing_units"] == 0).sum()),
                    "total_units": int(df["housing_units"].sum()),
                }
            )
        return [md(self.save("acs_checks", pd.DataFrame(rows)))]

    def strata_columns(self) -> list[str]:
        frames = []
        for r in self.regions:
            src = self.strata(r, "strata-tract-table")
            cols = self.con.sql(f"DESCRIBE SELECT * FROM {src}").fetchall()
            nulls = ", ".join(f'avg(("{c[0]}" IS NULL)::INT) AS "{c[0]}"' for c in cols)
            rates = self.df(f"SELECT {nulls} FROM {src}").T.reset_index()
            rates.columns = ["column", "null_rate"]
            rates["dtype"] = [c[1] for c in cols]
            frames.append(rates.assign(region=r))
        long = pd.concat(frames, ignore_index=True)
        order = long.drop_duplicates("column")["column"].tolist()
        wide = long.pivot_table(
            index=["column", "dtype"], columns="region", values="null_rate", aggfunc="first"
        ).reset_index()
        wide = wide.set_index("column").loc[order].reset_index()
        self.save("strata_columns", wide)
        covered = wide[wide["column"].str.endswith("_covered")]
        return [
            f"{len(order)} columns; full dictionary in tables/strata_columns.csv.",
            "",
            "Null rate of each coverage flag by region:",
            "",
            md(covered),
        ]

    def edge_tracts(self) -> list[str]:
        national = self.raw / "strata" / "national" / "national-census-tract-table.parquet"
        self.con.register("scored", scored_tracts(self.raw, self.regions))
        info = self.df(
            "SELECT s.GEOID, s.region, c.pop_total, c.ALAND, c.AWATER, "
            "c.AWATER / nullif(c.ALAND + c.AWATER, 0) AS water_share "
            f"FROM scored s JOIN {db.scan(national)} c USING (GEOID) ORDER BY GEOID"
        )
        edge = info[
            (info["water_share"] > 0.8) | (info["pop_total"] == 0) | info["GEOID"].str[5:7].eq("99")
        ].copy()
        for layer in EDGE_LAYERS:
            if layer == "roads":
                measure = f"sum({db.length_m('ST_Intersection(f.geometry, t.geometry)')}) / 1000"
            else:
                measure = "count(*)"
            values = []
            for row in edge.itertuples():
                tracts = self.strata(row.region, "census-tracts")
                tract = f"SELECT geometry, bbox FROM {tracts} WHERE GEOID = '{row.GEOID}'"
                values.append(
                    self.con.sql(
                        f"SELECT {measure} FROM {self.layer(row.region, layer)} f, ({tract}) t "
                        f"WHERE {BBOX_OVERLAP} AND ST_Intersects(f.geometry, t.geometry)"
                    ).fetchone()[0]
                    or 0
                )
            edge[f"overture_{layer}"] = values
        self.save("edge_tracts", edge)
        summary = info.groupby("region").agg(
            tracts=("GEOID", "size"),
            water_share_gt_0_8=("water_share", lambda s: int((s > 0.8).sum())),
            zero_pop=("pop_total", lambda s: int((s == 0).sum())),
        )
        return [
            f"Scored tracts joined to the national census table: {len(info):,}.",
            "",
            md(summary.reset_index()),
            "",
            md(edge),
        ]


def run(raw: Path, out: Path, cfg: dict) -> list[str]:
    con = db.connect(memory_limit="22GB", threads=4, temp_dir="/tmp/duckdb")
    return Audit(raw, out, cfg, con).run()
