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
| 20261025-1722-03_model-8d21578 | 03_model | 8d21578 | defaults | complete | 1.2 | 0.65 |
| 20261025-1726-03_model-1249b4b | 03_model | 1249b4b | defaults | complete | 1.3 | 0.66 |
| 20261025-1729-03_model-3dc08da | 03_model | 3dc08da | defaults | complete | 1.7 | 0.66 |
| 20261025-1738-03_model-cfd5aa7 | 03_model | cfd5aa7 | transport.boundary_d_m=25 | complete | 1.6 | 0.65 |
| 20261025-1750-03_model-3186428 | 03_model | 3186428 | transport.boundary_d_m=50 | complete | 1.5 | 0.66 |
| 20261025-1757-03_model-fd0d69e | 03_model | fd0d69e | poi.mode=constant | complete | 4.1 | 0.63 |
| 20261025-1806-02_features-b1a2332 | 02_features | b1a2332 | defaults | complete | 23.6 | 6.81 |
| 20261025-1848-03_model-7e4f29b | 03_model | 7e4f29b | building.reference=usfs | complete | 1.5 | 0.65 |
| 20261025-1905-03_model-ca33fb7 | 03_model | ca33fb7 | defaults | complete | 1.3 | 0.63 |
| 20261025-1907-03_model-d96dddf | 03_model | d96dddf | building.reference=usfs | complete | 1.3 | 0.65 |
| 20261026-1108-03_model-4702f1a | 03_model | 4702f1a | poi.kappa_E=0 | complete | 10.0 | 0.62 |
| 20261026-1118-03_model-f1228ef | 03_model | f1228ef | transport.sigma=0.05 | complete | 1.2 | 0.62 |
| 20261026-1130-03_model-9352aee | 03_model | 9352aee | poi.mode=model | complete | 4.3 | 0.66 |
| 20261026-1136-02_features-c1f6404 | 02_features | c1f6404 | defaults | complete | 27.9 | 6.99 |
| 20261026-1247-03_model-fa129b8 | 03_model | fa129b8 | transport.exclude_links=true | complete | 1.3 | 0.62 |
| 20261026-1249-03_model-227bfa1 | 03_model | 227bfa1 | transport.unclipped=true | complete | 1.2 | 0.62 |
| 20261026-1426-03_model-a6dc6eb | 03_model | a6dc6eb | transport.value_scale=1.5 | complete | 1.3 | 0.62 |
| 20261026-1427-03_model-92428b7 | 03_model | 92428b7 | building.baseline_gap=0.05 | complete | 1.5 | 0.62 |
| 20261027-0949-04_analysis-81b7f88 | 04_analysis | 81b7f88 | defaults | complete | 4.0 | 0.38 |
| 20261027-1001-03_model-c3c5417 | 03_model | c3c5417 | transport.value_scale=1.15 building.baseline_gap=0 poi.level=0.779 | complete | 1.2 | 0.63 |
| 20261027-1054-03_model-7c5f56c | 03_model | 7c5f56c | transport.value_scale=1.15 building.baseline_gap=0 poi.level=0.779 poi.mode=fire | complete | 1.3 | 0.71 |
| 20261027-1100-03_model-d43cff5 | 03_model | d43cff5 | transport.value_scale=1.15 building.baseline_gap=0 poi.level=0.779 poi.mode=fire | complete | 1.3 | 0.65 |
| 20261027-2109-03_model-8d5f2ee | 03_model | 8d5f2ee | transport.value_scale=1.15 building.baseline_gap=0 poi.level=0.779 poi.mode=fire poi.fire_strength=0.3 | complete | 1.4 | 0.71 |
| 20261027-2130-05_reference-26817ef | 05_reference | 26817ef | defaults | error | 1.2 | n/a |
| 20261027-2132-05_reference-5906e20 | 05_reference | 5906e20 | defaults | complete | 2.5 | 0.62 |
| 20261027-2136-03_model-5ef8bfa | 03_model | 5ef8bfa | transport.source=tiger building.baseline_gap=0 poi.level=0.779 poi.mode=fire poi.fire_strength=0.3 | error | 1.2 | n/a |
| 20261027-2139-03_model-8fffd01 | 03_model | 8fffd01 | transport.source=tiger building.baseline_gap=0 poi.level=0.779 poi.mode=fire poi.fire_strength=0.3 | complete | 1.4 | 0.66 |
| 20261027-2152-07_establishments-3e2eb58 | 07_establishments | 3e2eb58 | defaults | error | 1.2 | n/a |
| 20261027-2156-07_establishments-87a0698 | 07_establishments | 87a0698 | defaults | complete | 1.8 | 0.17 |
| 20261027-2149-06_facilities-76c1cda | 06_facilities | 76c1cda | defaults | error | 26.0 | n/a |
| 20261027-2145-05_reference-0add93b | 05_reference | 0add93b | defaults | complete | 33.9 | 3.55 |
