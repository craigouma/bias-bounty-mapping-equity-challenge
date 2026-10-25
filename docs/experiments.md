# Experiments

Every Kaggle stage run is appended to the runs table by `make kaggle-run`. Wall time is
measured from push to completion on the Mac and includes queueing. Peak memory is the stage
process peak RSS read from `runtime.json`. Calibration checks, out-of-fold metrics and GPU
hours are recorded under Notes.

## Notes

## Runs

| Run ID | Stage | SHA | Overrides | Status | Wall (min) | Peak RSS (GB) |
|---|---|---|---|---|---|---|
| 20261025-1421-00_env-4ffe361 | 00_env | 4ffe361 | defaults | complete | 0.4 | 0.03 |
| 20261025-1434-01_ingest-398b1ba | 01_ingest | 398b1ba | defaults | complete | 5.4 | 1.39 |
