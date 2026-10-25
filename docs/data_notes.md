# Data notes

Facts about the data and the compute environment, each with the file or output it came from.

## Sample submission

Source: `data/SampleSubmission.csv`, checked on 25 Oct 2026.

- 919,898 bytes, ASCII, LF line endings, a header plus 9,794 rows.
- 17 columns in the order listed in the project brief section 5.4.
- 9,794 unique GEOIDs, all 11-digit text, rows sorted ascending by GEOID.
- Rows per region: south-central-tx 6,003; maricopa-az 1,593; eastern-ok 1,192; northern-ca 591;
  eastern-wa 415.
- Rows per state FIPS: 48 6,003; 04 1,592; 40 1,192; 06 591; 53 415; 35 1 (`35023970000`,
  region `maricopa-az`).
- The Oklahoma border tracts `40013795900` and `40085094200` are `eastern-ok`. The water tracts
  `48039990000` and `48057990000` are present.
- Every float cell is `0.0` and every flag is `True`.

## Bucket

Source: S3 ListObjectsV2 on `us-west-2.opendata.source.coop`, prefix
`humane-intelligence/bias-bounty-mapping-equity-challenge/`, read 25 Oct 2026 (327 objects), and
the bucket `README.md` (34,202 bytes).

- No `coverage-gap` file and no TIGER, Microsoft, HIFLD or CBP file exists anywhere in the bucket.
- The only key that contains a denylisted token is the permitted wildfire stratum
  `usgs-combined-tract-table` (national and per region).
- `boundaries/` also holds `<region>-aoi.geojson` and `original-rings.geojson`, which the project brief
  does not list. `boundaries/south-central-tx-tract-geoids.csv` lists 6,010 tracts; 6,003 are
  scored after the 7 water tracts were dropped.
- `bulk-downloads/` holds the rebuilt zips (`reference.zip` 4,517,510,250 bytes, `strata.zip`
  1,694,666,582 bytes). The pipeline does not use them.
- Reference sizes per region (all files): south-central-tx 2.55 GB, maricopa-az 0.75 GB,
  eastern-ok 0.61 GB, northern-ca 0.35 GB, eastern-wa 0.29 GB.
- The README states the organisers' POI matching on `categories.primary`: fire stations
  `fire_department`; EMS `ambulance_and_ems_services`; schools `elementary_school`,
  `middle_school`, `high_school`, `school`, `private_school`, `public_school`. Each per-type gap is
  `1 - min(1, overture / reference)`, undefined where the tract has no reference facility of that
  type. EMS is close to 1:1 with the reference and rarely binds; fire stations carry the facility
  half.
- The README states the road comparison is TIGER S1100 plus S1200 against Overture motorway,
  trunk, primary and secondary, and that a component that is undefined is written as 0 with its
  flag false.

## Kaggle session

Source: stage 00 run `20261025-1421-00_env-4ffe361`, `env/env.json` and `env/pip_freeze.txt`.

- Python 3.13.15, Linux 6.18, glibc 2.39.
- 4 CPU cores, 32.9 GB RAM, 21 GB in `/kaggle/working`, about 1.1 TB free in `/tmp`.
- GPU session: 2 x Tesla T4 (15 GB each), driver 580, CUDA 13.0.
- Internet works (PyPI 200). The Source Cooperative HTTPS proxy returns 403 to Python's default
  urllib User-Agent; the S3 REST endpoint is used instead.
- No `aws` CLI in the image.
- Preinstalled: duckdb 1.3.2, numpy 2.1.3, pandas 2.3.3, pyarrow 23.0.1, scikit-learn 1.6.1,
  scipy 1.16.3, xgboost 3.4.1, lightgbm 4.6.0, geopandas 1.1.4, shapely 2.1.2, pyproj 3.7.2,
  boto3 1.41.5, polars 1.35.2, matplotlib 3.10.0.
- The code dataset mounts extracted at `/kaggle/input/datasets/carloscrou/bbme-code/bbme_code`.

## Stage 01 audit

Source: run `20261025-1434-01_ingest-398b1ba` (`audit/MANIFEST.json`, `audit/data_audit.md`,
`audit/schemas.json`, `audit/tables/*.csv`). Wall time 4.4 min of compute, peak RSS 1.4 GB.

### Sync

- 327 objects listed, no denylisted key. 172 files synced (4,615,029,100 bytes): every reference
  parquet and per-region sample submission, every region strata parquet, the boundaries, the
  README and `strata/national/national-census-tract-table.parquet`. Every byte count matches
  the listing on the first attempt.
- Region strata folders have no `census-tract-table`. The region `strata-tract-table` has 227
  columns. The column dictionary is in `docs/strata_columns.md`.
- `south-central-tx-census-tracts.parquet` holds 6,010 polygons: the 6,003 scored tracts plus the
  7 dropped water tracts. Every other region's polygons equal its scored list. `frac_inside_aoi`
  is 1.0 everywhere.

### Release and geometry

- The parquet key-value metadata carries only `geo` (GeoParquet 1.1.0); the Overture release is
  not stored in the files. Evidence for 2026-08-19.0: the newest `sources[].update_time` is
  2026-08-01 to 2026-08-04 for roads, 2026-08-14 for places, 2026-07-25 for infrastructure.
- Geometry columns read as `GEOMETRY('OGC:CRS84')`. One maricopa-az motorway segment measures
  826.49 m with `ST_Length_Spheroid(ST_FlipCoordinates(...))` and 826.49 m with pyproj.

### Roads

Scored `roads` layer, km by class:

| class | eastern-ok | eastern-wa | maricopa-az | northern-ca | south-central-tx |
|---|---|---|---|---|---|
| motorway | 5,915 | 1,991 | 5,542 | 2,399 | 20,266 |
| trunk | 4,270 | 1,884 | 2,985 | 1,866 | 15,922 |
| primary | 6,105 | 3,003 | 5,792 | 2,928 | 23,080 |
| secondary | 11,389 | 5,145 | 7,769 | 4,543 | 56,483 |
| tertiary | 13,829 | 12,632 | 13,090 | 10,575 | 50,806 |
| residential | 129,662 | 24,786 | 65,265 | 37,646 | 371,825 |
| unclassified | 38,924 | 29,623 | 23,034 | 16,262 | 32,438 |

- Segment schema: `names` (primary, common, rules), `class`, `subclass`, `subclass_rules`,
  `road_flags`, `road_surface`, `speed_limits`, `access_restrictions`, `destinations`, and
  `routes`, a list of structs (name, network, ref, symbol, wikidata, between).
- Route networks follow OSM route-relation naming: `US:I` (17,352 km over all regions), `US:US`
  (35,385), state networks `US:TX`, `US:OK`, `US:AZ`, `US:CA`, `US:WA`, Texas secondary state
  networks `US:TX:FM` (46,117), `US:TX:RM`, `US:TX:Loop`, `US:TX:Spur`, toll networks
  (`US:OK:Turnpike`, `US:TX:Toll`, `US:TX:NTTA`, `Texas Trunk System`), business and alternate
  routes, county networks (`US:OK:<County>`, `US:TX:<County>`, `US:CA:CR`), and non-route
  designations (`US:NHT`, `US:NHS ...`, `US:US:Historic`, scenic and forest routes). About
  9,800 km carry a route with an empty network.
- Motorway and trunk segments are almost all on a route; a large share of secondary and some
  tertiary and unclassified length is on a route (state routes classed low in OSM), and many
  primary and secondary segments are on no route (city arterials).
- Roads are 99.9% OpenStreetMap with a few TomTom segments.

### Places

- Places per region: south-central-tx 1,300,334; maricopa-az 300,046; eastern-ok 207,369;
  northern-ca 116,897; eastern-wa 76,491. Every place has `confidence` (median 0.92).
- Places carry `basic_category` and a `taxonomy` struct (primary, hierarchy, alternates) beside
  `categories`. The organisers match on `categories.primary`.
- Organiser categories, places per region (ok, wa, az, ca, tx): `fire_department` 576, 179, 462,
  289, 2,135; `ambulance_and_ems_services` 123, 44, 73, 38, 559; the six school categories
  together 3,069, 1,131, 3,501, 1,724, 15,429. Nearby categories that are not in the mapping
  include `fire_protection_service`, `emergency_room`, `emergency_medicine`, `preschool`,
  `day_care_preschool`, `charter_school`, `college_university`.
- Hospital sanity check: `hospital` has 733, 196, 758, 350, 3,524 places. Hospitals in these
  regions number in the low hundreds, which is consistent with the stated ratio of about 12.
- First source: meta 55% to 65%, Microsoft 15% to 18%, BrightQuery 11% to 17%, Foursquare 6% to 8%,
  AllThePlaces 1% to 2%.

### Buildings

- Footprints: south-central-tx 11.46 M, maricopa-az 2.91 M, eastern-ok 2.55 M, northern-ca 1.16 M,
  eastern-wa 1.08 M. Median footprint 144 to 219 m2.
- First source share: maricopa-az 80% OSM, 14% Microsoft ML, 5% Esri, 1% Google; south-central-tx
  51% OSM, 44% Microsoft, 2% Esri, 2% Google; eastern-ok 69% Microsoft, 17% OSM, 14% Esri;
  northern-ca 51% Microsoft, 47% OSM; eastern-wa 56% OSM, 38% Microsoft, 6% Esri. OSM never
  reports confidence; Microsoft reports it on a minority of footprints, Google on all.

### Infrastructure, rail, ACS

- Infrastructure is all OpenStreetMap: bus stops dominate; airports and helipads are a few
  hundred per region.
- ACS housing units cover every scored tract with no nulls; 27 (az), 10 (ok), 50 (tx, including
  unscored rows), 2 (wa) tracts have zero units.

### Edge-case tracts

- Zero population: maricopa-az 11, eastern-ok 1, south-central-tx 14, eastern-wa 1. Most of these
  still hold Overture buildings, roads and places (airports, industrial and institutional land).
- Water share above 0.8: 7 south-central-tx tracts, five of them populated coastal tracts.
- `48039990000` and `48057990000` have no land area and no Overture building, road or place.
  Any defined component there has Overture count 0 and a gap of 1, and a scored tract has at
  least one defined component, so their score is 1.

## USFS building count against Overture (H-B3 check)

Source: stage 02 run `20261025-1806-02_features-b1a2332`. `usfs_BuildingCount_sum` and
`carbonplan_buildings` have no nulls or zeros on scored tracts. In tracts at least 95% ML-derived,
the median of Overture footprints over the USFS count is 1.00 (eastern-ok, 301 tracts), 1.12
(eastern-wa, 18), 1.00 (maricopa-az, 24), 1.03 (northern-ca, 54), 1.03 (south-central-tx, 949),
with robust spread 0.03 to 0.10 on the log scale. Across all tracts the correlation of log counts
is 0.971, and fewer than 0.3% of tracts have under half the expected count. The USFS count
behaves like a building footprint count, consistent with derivation from footprint data, which
the writeup discloses (decisions D017).
