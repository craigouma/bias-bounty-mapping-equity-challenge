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
