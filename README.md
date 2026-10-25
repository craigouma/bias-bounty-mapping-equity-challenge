# bias-bounty-mapping-equity-challenge

Coverage gap estimates per Census tract for the Bias Bounty Mapping Equity Challenge (Zindi,
Humane Intelligence, Reliabl, Radiant Earth). The pipeline estimates the transport, building and
POI coverage gaps of Overture Maps against the organisers' removed reference layers using only
the data in the challenge package, and combines them as the expectation of the composite score.

## Layout

| Path | Contents |
|---|---|
| `src/bbme/` | package: guard, GEOID helpers, DuckDB helpers, ingest and audit, features, components, composite, submission writer |
| `kaggle/stages/` | one script kernel per stage plus the shared bootstrap |
| `scripts/` | code dataset push, kernel runner, submission validation and logging |
| `configs/` | data, feature, POI category, model and Kaggle settings |
| `tests/` | unit tests on synthetic fixtures |
| `docs/` | data notes, decisions, experiment and submission logs, writeup |

## Setup

```bash
make setup      # uv sync, local hooks, data/ artifacts/ build/
make lint test
```

Place `SampleSubmission.csv` from the Zindi Data page in `data/`. The Kaggle CLI must be
installed and authenticated (`kaggle config view`).

## Data access

All data comes from the public Source Cooperative bucket
`s3://us-west-2.opendata.source.coop/humane-intelligence/bias-bounty-mapping-equity-challenge/`,
read without credentials. Stage 01 lists the bucket, stops if any denylisted file name exists,
downloads every reference parquet, every per-region sample submission, every region strata
parquet, the boundaries, the README and `strata/national/national-census-tract-table.parquet`
(172 files, 4,615,029,100 bytes on 25 Oct 2026), and checks every byte count against the
listing. Overture release `2026-08-19.0`. No removed reference layer (TIGER roads, Microsoft
footprints, HIFLD or USGS structures, CBP) and no coverage-gap file is read anywhere; every
reader goes through `bbme.guard`.

## Running the pipeline

Every compute stage runs on Kaggle as a private script kernel. The code reaches Kaggle as the
private dataset `carloscrou/bbme-code`, built from a clean commit.

```bash
make kaggle-code                                   # version the code dataset at HEAD
make kaggle-run STAGE=00_env                       # environment report
make kaggle-run STAGE=01_ingest                    # sync, byte check, audit
make kaggle-run STAGE=02_features                  # per-tract feature table
make kaggle-run STAGE=03_model SET="alpha=0.8"     # submission for a model config
make validate SUB=artifacts/kaggle/03_model/<run_id>/runs/<run_id>/submission.csv
```

Each run writes its resolved config, code SHA, `pip freeze`, runtime and peak memory beside
its outputs, and is logged in `docs/experiments.md`.

| Stage | Session | Measured runtime | Peak RSS |
|---|---|---|---|
| 00_env | GPU T4 x2 | 0.4 min | 0.03 GB |
| 01_ingest | CPU, 4 cores, 32 GB | 5.4 min | 1.4 GB |

## Environment

Kaggle image: Python 3.13.15, 4 CPU cores, 32 GB RAM. Installed on top of the image:
`duckdb==1.5.4` (`requirements-kaggle.txt`). Local: Python 3.13 managed by uv (`uv.lock`).

## Determinism

One seed in `configs/model.yaml` drives every random draw through a single
`numpy.random.Generator`. Rerunning stage 03 with the same config and features reproduces the
submission exactly.

## Submissions

Every submitted file, its run ID, code SHA, config and hypothesis are listed in
`docs/submissions.md`.
