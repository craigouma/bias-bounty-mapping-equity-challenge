# bias-bounty-mapping-equity-challenge

Coverage gap estimates per Census tract for the Bias Bounty Mapping Equity Challenge (Zindi,
Humane Intelligence, Reliabl, Radiant Earth). The pipeline compares Overture Maps with reference
data for roads, buildings and points of interest per tract and combines the transport, building
and POI gaps into the composite score. Submissions up to S16 estimate the reference side from the
challenge package alone. From S17 the reference side is rebuilt from public sources downloaded
from their publishers (listed under Data access). Submission S25 (`2ncgdcQQ`) scored 0.02152
public and 0.01933 private.

Code review documentation for S25: `docs/writeup/code_review.pdf` (source `code_review.tex`).

## Papers

- Methodology (Best Documentation entry):
  https://craigouma.github.io/bias-bounty-mapping-equity-challenge/methodology/
- Unnamed local roads on tribal reservations (Best Bias Discovery entry):
  https://craigouma.github.io/bias-bounty-mapping-equity-challenge/bias-discovery/

The PDFs and their LaTeX sources are in `docs/writeup/`. The pages are served by GitHub Pages
from `docs/`.

## Layout

| Path | Contents |
|---|---|
| `src/bbme/` | package: guard, GEOID helpers, DuckDB helpers, ingest and audit, features, reference builders, components, composite, submission writer |
| `kaggle/stages/` | one script kernel per stage plus the shared bootstrap |
| `scripts/` | code dataset push, kernel runner, reproduction, HUD dataset, submission validation and logging |
| `configs/` | data sources, features, POI categories, model, final configurations and Kaggle settings |
| `tests/` | unit tests on synthetic fixtures |
| `docs/` | data notes, decisions, experiment and submission logs, writeups, GitHub Pages |

## Setup

```bash
make setup      # uv sync, local hooks, data/ artifacts/ build/
make lint test
```

Place `SampleSubmission.csv` from the Zindi Data page in `data/`. The Kaggle CLI must be
installed and authenticated (`kaggle config view`), and the Kaggle account needs phone
verification for internet access in kernels. Set `username` in `configs/kaggle.yaml` to your
Kaggle user name and commit the change, because the code dataset is built only from a clean tree.

## Data access

**Challenge package.** Stage 01 lists the public Source Cooperative bucket
`s3://us-west-2.opendata.source.coop/humane-intelligence/bias-bounty-mapping-equity-challenge/`
without credentials, stops if any denylisted file name exists, downloads every reference parquet,
every per-region sample submission, every region strata parquet, the boundaries, the README and
`strata/national/national-census-tract-table.parquet` (172 files, 4,615,029,100 bytes), and checks
every byte count against the listing. Overture release `2026-08-19.0`.

**Public reference sources** (URLs in `configs/data.yaml`, downloaded inside the kernels):

| Source | Version | Stage |
|---|---|---|
| Census TIGER/Line primary and secondary roads | 2025 | 05 |
| USGS National Map structures, state GeoPackages | 2026 | 06 |
| Census ZIP Code Business Patterns, totals | 2023 | 07 |
| Census 2020 ZCTA to tract relationship file | 2020 | 07 |
| HUD USPS ZIP-TRACT crosswalk | Q4 2024 | 07 |
| Microsoft Global ML Building Footprints | 2026-02-03 | 10 |

The HUD crosswalk is the one manual download: get `ZIP-Tract/ZIP_TRACT_122024.xlsx` from
DataLumos project 219325 V2
(https://www.datalumos.org/datalumos/project/219325/version/V2/view) into
`data/hud_crosswalk/`, then run `cd scripts && uv run python hud_dataset.py` to publish it as the
private Kaggle dataset `<user>/bbme-hud-crosswalk` that stage 07 reads.

Organiser coverage-gap files are never read: every reader goes through `bbme.guard`, which
rejects any name containing `coverage-gap` or `coverage_gap`.

## Running the pipeline

Every compute stage runs on Kaggle as a private script kernel. The code reaches Kaggle as the
private dataset `<user>/bbme-code`, built from a clean commit, and each kernel stops if the commit
in the dataset differs from the one it was rendered with.

```bash
make kaggle-code                          # version the code dataset at HEAD
make kaggle-run STAGE=01_ingest           # bucket sync, byte check, audit
make kaggle-run STAGE=02_features         # Overture per tract
make kaggle-run STAGE=05_reference        # TIGER roads
make kaggle-run STAGE=06_facilities       # USGS fire stations and schools
make kaggle-run STAGE=08_archive          # archived facility layer (input of 03, unused by S25)
make kaggle-run STAGE=10_globalml         # Global ML footprints
make kaggle-run STAGE=07_establishments   # ZBP establishments by HUD business-address ratios
make reproduce FINAL=A                    # stage 03 with configs/final_A.yaml, compared with S25
```

Stages 02, 05, 06, 08 and 10 are independent of one another. `make reproduce` expects the uploaded
file at `artifacts/submissions/S25_20261030-1227-03_model-45a6fcc.csv`. `PREFIX=<text>` on
`kaggle-run` and `reproduce` runs a separate chain of kernels named `<text><slug>`.

Each run writes its resolved config, code SHA, `pip freeze`, runtime and peak memory beside its
outputs, and is logged in `docs/experiments.md`. Measured on Kaggle CPU sessions (4 cores, 32 GB)
in the from-scratch rerun of 4 Nov 2026; wall time includes queueing:

| Stage | Wall (min) | Peak RSS (GB) |
|---|---|---|
| 01_ingest | 7.8 | 1.47 |
| 02_features | 25.5 | 6.87 |
| 05_reference | 32.5 | 3.51 |
| 06_facilities | 26.8 | 0.50 |
| 07_establishments | 1.1 | 0.22 |
| 08_archive | 1.2 | 0.50 |
| 10_globalml | 16.1 | 2.22 |
| 03_model | 1.5 | 0.56 |

## Environment

Kaggle image: Python 3.13.15, 4 CPU cores, 32 GB RAM. `requirements-kaggle.txt` pins every package
the stages import (duckdb 1.5.4, geopandas 1.1.4, matplotlib 3.10.0, numpy 2.1.3, pandas 2.3.3,
pyarrow 23.0.1, pyogrio 0.13.0, pyproj 3.7.2, PyYAML 6.0.3, shapely 2.1.2). Local: Python 3.13
managed by uv (`uv.lock`).

## Determinism

One seed in `configs/model.yaml` (20261025) drives every random draw through a single
`numpy.random.Generator`; the S25 computation makes none. On 4 Nov 2026 the whole chain was rerun
from scratch, downloading the challenge package and every public source again, and stage 03
produced a file byte-identical to the uploaded S25 file (SHA-256 `03678f50...ff48d`).

## Submissions

Every submitted file, its run ID, code SHA, config and hypothesis are listed in
`docs/submissions.md`.
