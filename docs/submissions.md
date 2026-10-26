# Submissions

Budget: 35 submissions in total (the project brief section 11). Each entry is pre-registered with
`make sub-ready` before upload. Craig uploads on Zindi and reports the public RMSE, which is
logged with `uv run python scripts/log_submission.py result --id S## --rmse <value>`.
Scorecards are kept verbatim in `docs/scorecards/S##.md`.

## S01 (2026-10-25)

- File: `artifacts/submissions/S01_sample.csv`
- Run ID: `sample`
- Code SHA: `398b1ba6556639cd8b4271ad9222fccbf4ca4d76`
- Hypothesis: none (constant baseline allowed by section 4.4)
- Change against current best: first submission: the sample file as downloaded, every score 0.0
- Expected direction: RMSE equals the root mean square of the true scores; sets the scale for every later result
- Decision informed: confirms the upload format and gives the all-zero baseline
- Public RMSE: 0.107246299
- Submissions used after this one: 1 of 35
- Result note: rank 339 at upload; implies mean of y squared about 0.0115 on the public split; leaderboard top entries show exactly 0

## S02 (2026-10-25)

- File: `artifacts/submissions/S02_20261025-1729-03_model-3dc08da.csv`
- Run ID: `20261025-1729-03_model-3dc08da`
- Code SHA: `3dc08da492467a57ce35ac94279bc402293286b5`
- Hypothesis: v1 analytic method (D015, D019, D020)
- Change against current best: first model: tiered route-based transport, baseline building, Poisson facilities and kappa_E 0.01 establishments, Monte Carlo composite; predicted mean 0.058, rms 0.079
- Expected direction: below S01 (0.10725); a result above S01 means the component scale is still too high
- Decision informed: whether the v1 structure beats the constant and sets the reference for every D1 hypothesis
- Public RMSE: 0.098486812
- Submissions used after this one: 2 of 35
- Result note: rank 307; beats S01 by 0.0088
- Result note: scale 0.644, scaled rmse 0.0944 (D021)

## S03 (2026-10-25)

- File: `artifacts/submissions/S03_20261025-1738-03_model-cfd5aa7.csv`
- Run ID: `20261025-1738-03_model-cfd5aa7`
- Code SHA: `cfd5aa7b0076d0e9262dd7b012feaf3a6c955264`
- Hypothesis: H-T1 boundary double counting, d = 25 m
- Change against current best: S02 with transport reference lengths taken inside each tract grown outward by 25 m (transport.boundary_d_m=25); mean 0.073, rms 0.098
- Expected direction: scaled rmse (D021) below S02's 0.0944 if TIGER highways on tract edges count in both neighbours; raw rmse may rise because v1 already over-predicts
- Decision informed: whether transport keeps the boundary buffer and whether d is worth one more test
- Public RMSE: 0.089740618
- Submissions used after this one: 3 of 35
- Result note: rank 274; scale 0.678, scaled rmse 0.0840 against 0.0944 for S02: H-T1 confirmed

## S04 (2026-10-25)

- File: `artifacts/submissions/S04_20261025-1750-03_model-3186428.csv`
- Run ID: `20261025-1750-03_model-3186428`
- Code SHA: `3186428d2fe78734be6b140afb99e407ec6223dd`
- Hypothesis: H-T1 boundary distance, d = 50 m (second value of tuned scalar 1)
- Change against current best: S03 with transport.boundary_d_m=50 instead of 25; mean 0.077, rms 0.103
- Expected direction: scaled rmse below S03's 0.0840 if TIGER boundary highways often lie 25 to 50 m from the Overture line (divided carriageways)
- Decision informed: the boundary distance for the transport component; if 50 wins clearly, d = 100 is the last allowed test
- Public RMSE: 0.091514572
- Submissions used after this one: 4 of 35
- Result note: scale 0.646, scaled rmse 0.0839: tie with S03 (0.0840); d stays 25 m

## S05 (2026-10-25)

- File: `artifacts/submissions/S05_20261025-1757-03_model-fd0d69e.csv`
- Run ID: `20261025-1757-03_model-fd0d69e`
- Code SHA: `fd0d69ec5c19b3039a41c7e595ff64b84053ab64`
- Hypothesis: H-P0 ablation: tract-level POI variation carries signal
- Change against current best: S03 with every tract's POI value replaced by its region's mean POI estimate (poi.mode=constant); transport and building identical to S03; mean 0.072, rms 0.084
- Expected direction: scaled rmse clearly above S03's 0.0840 if POI variation carries signal; a tie means POI tract variation is noise and the over-prediction lies in its level
- Decision informed: whether day 1 effort goes into the POI estimators or into transport and the POI level
- Public RMSE: 0.077100846
- Submissions used after this one: 5 of 35
- Result note: rank 134; scale 0.891, scaled rmse 0.0766 against 0.0840 for S03: tract-level POI variation was noise; constant POI becomes the default

## S06 (2026-10-25)

- File: `artifacts/submissions/S06_20261025-1907-03_model-d96dddf.csv`
- Run ID: `20261025-1907-03_model-d96dddf`
- Code SHA: `d96dddfe52e5d8cb7fff36c6de1c2a99acf22281`
- Hypothesis: H-B3 building reference from USFS building counts (approved D017)
- Change against current best: S05 method (now with independent component streams; rms drift 0.0011 from the S05 file) with B = E[gap(N_O, k U e^z)], k and spread learned on ML-dominated tracts (building.reference=usfs); transport and POI identical; mean 0.086, rms 0.099
- Expected direction: scaled rmse below S05's 0.0766 if the Microsoft reference tracks the USFS count, so its shortfalls mark real building gaps; raw rmse may rise with the higher mean
- Decision informed: whether building gets a tract-level estimator or stays at the 0.01 baseline
- Public RMSE: 0.085445927
- Submissions used after this one: 6 of 35
- Result note: scale 0.712, scaled rmse 0.0805 against 0.0766 for S05: H-B3 rejected, building stays at the baseline

## S07 (2026-10-26)

- File: `artifacts/submissions/S07_20261026-1108-03_model-4702f1a.csv`
- Run ID: `20261026-1108-03_model-4702f1a`
- Code SHA: `4702f1a205cf7f7cc9cc5b1071bcd634a9c254fa`
- Hypothesis: H-P1 establishments half is about 0 everywhere
- Change against current best: current default (S05 method, component streams) with poi.kappa_E=0: the establishments half is defined with gap 0, so the regional POI constant falls from about 0.115 to about 0.09; transport and building identical; mean 0.062, rms 0.077
- Expected direction: scaled rmse below S05's 0.0766 if Overture places outnumber the apportioned CBP establishments in nearly every tract
- Decision informed: the POI level and whether the establishments half needs any modelling
- Public RMSE: 0.075184211
- Submissions used after this one: 7 of 35
- Result note: rank 132, best so far; scale 1.000, scaled rmse 0.0752 against 0.0766 for S05

## S08 (2026-10-26)

- File: `artifacts/submissions/S08_20261026-1118-03_model-f1228ef.csv`
- Run ID: `20261026-1118-03_model-f1228ef`
- Code SHA: `f1228efd0502c22cc22cb8e08d654d3c4ca1e2c1`
- Hypothesis: H-T2 smaller transport reference noise, sigma 0.05
- Change against current best: current default with transport.sigma=0.05 instead of 0.15; building and POI identical; mean 0.071, rms 0.084
- Expected direction: scaled rmse below S05's 0.0766 if Overture and TIGER named-highway lengths agree closely within a tract, so the noise-driven gap mass is spurious
- Decision informed: the transport noise level; a loss suggests testing a larger sigma
- Public RMSE: 0.077816544
- Submissions used after this one: 8 of 35
- Result note: scale 0.890, scaled rmse 0.0773: tie with S05; sigma stays 0.15

## S09 (2026-10-26)

- File: `artifacts/submissions/S09_20261026-1130-03_model-9352aee.csv`
- Run ID: `20261026-1130-03_model-9352aee`
- Code SHA: `9352aee6361af8708d1443bd26870dfbda2ed24b`
- Hypothesis: H-P2 tract-level facility half carries signal once the establishments half is zero
- Change against current best: S07 with poi.mode=model: POI varies by tract through the fire, EMS and school Poisson model while the establishments half stays at gap 0; mean 0.062, rms 0.082, same mean POI as S07
- Expected direction: scaled rmse below S07's 0.0752 if the S05 loss came from the establishments half; a loss means facility variation is also noise
- Decision informed: whether POI work goes into the facility model or stays constant
- Public RMSE: pending
- Submissions used after this one: 9 of 35
