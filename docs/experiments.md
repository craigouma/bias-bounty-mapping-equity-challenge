# Experiments

Every Kaggle stage run is appended to the runs table by `make kaggle-run`. Wall time is
measured from push to completion on the Mac and includes queueing. Peak memory is the stage
process peak RSS read from `runtime.json`. Calibration checks, out-of-fold metrics and GPU
hours are recorded under Notes.

## Notes

### 25 Oct 2026, stage 02 road calibration (run 20261025-1447-02_features-0aa771e)

Share of scored tracts with zero proxy reference length, against the published share with an
undefined component. A = interstate, US and state routes plus motorway and trunk; B adds
secondary state, toll and business routes; C adds county routes; buf25 counts length up to 25 m
outside the tract edge.

| Region | Published | A | A buf25 | B | C | named/A | named/A buf25 | named/B |
|---|---|---|---|---|---|---|---|---|
| maricopa-az | 0.55 | 0.55 | 0.53 | 0.55 | 0.54 | 1.72 | 1.39 | 1.71 |
| northern-ca | 0.37 | 0.39 | 0.37 | 0.39 | 0.29 | 1.63 | 1.44 | 1.61 |
| eastern-ok | 0.21 | 0.23 | 0.22 | 0.22 | 0.21 | 1.11 | 0.97 | 1.10 |
| south-central-tx | 0.28 | 0.33 | 0.31 | 0.19 | 0.18 | 2.09 | 1.69 | 1.07 |
| eastern-wa | n/a | 0.23 | 0.23 | 0.23 | 0.21 | 1.43 | 1.27 | 1.40 |

Set A reproduces the published rates for three regions. Texas lies between A and B: adding the
secondary state group (FM, RM, Loop, Spur) moves the zero share from 0.33 to 0.19, while toll,
business and county routes barely move it. Set C breaks northern-ca (0.29) and pushes the
eastern-ok ratio to 0.56, below the published minimum 0.71. Transport v1 therefore uses A as the
high tier and B-only tracts as a mid tier with calibrated definedness (D019).

## Runs

| Run ID | Stage | SHA | Overrides | Status | Wall (min) | Peak RSS (GB) |
|---|---|---|---|---|---|---|
| 20261025-1421-00_env-4ffe361 | 00_env | 4ffe361 | defaults | complete | 0.4 | 0.03 |
| 20261025-1434-01_ingest-398b1ba | 01_ingest | 398b1ba | defaults | complete | 5.4 | 1.39 |
| 20261025-1447-02_features-0aa771e | 02_features | 0aa771e | defaults | complete | 23.7 | 6.72 |
