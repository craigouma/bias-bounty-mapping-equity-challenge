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
- Public RMSE: 0.078050468
- Submissions used after this one: 9 of 35
- Result note: scale 0.899, scaled rmse 0.0776 against 0.0752 for S07: H-P2 rejected, POI stays constant

## S10 (2026-10-26)

- File: `artifacts/submissions/S10_20261026-1247-03_model-fa129b8.csv`
- Run ID: `20261026-1247-03_model-fa129b8`
- Code SHA: `fa129b8bc461b07ffe42ed2d2daa6b5d21d7f4d1`
- Hypothesis: H-T4 the TIGER reference excludes ramps
- Change against current best: S07 with transport.exclude_links=true: Overture ramp length (subclass link) is removed from the reference proxy, not from the Overture side; POI and building identical; mean 0.060, rms 0.074
- Expected direction: scaled rmse below S07's 0.0752 because TIGER S1100 and S1200 omit ramps (S1630) while the organisers' Overture side keeps them
- Decision informed: whether ramp exclusion becomes the transport default before the H-T5 clipping test
- Public RMSE: 0.075900456
- Submissions used after this one: 10 of 35
- Result note: scale 1.027, scaled rmse 0.0759 against 0.0752 for S07; line search t* = -0.40 along S07 to S10: H-T4 rejected

## S11 (2026-10-26)

- File: `artifacts/submissions/S11_20261026-1249-03_model-227bfa1.csv`
- Run ID: `20261026-1249-03_model-227bfa1`
- Code SHA: `227bfa187d45e0306de7d9f3f4e57e355f53d0ea`
- Hypothesis: H-T5 the organisers summed whole segments touching each tract instead of clipping
- Change against current best: S07 with transport.unclipped=true on both the Overture side and the reference proxy (the 25 m boundary increment kept); POI and building identical; mean 0.057, rms 0.067
- Expected direction: scaled rmse below S07's 0.0752 if per-tract lengths were computed with an intersects join and no clipping
- Decision informed: how per-tract road length is measured, which every transport feature depends on
- Public RMSE: 0.077658872
- Submissions used after this one: 11 of 35
- Result note: scaled 0.0773; line search t* = -0.21 along S07 to S11: H-T5 rejected, lengths stay clipped

## S12 (2026-10-26)

- File: `artifacts/submissions/S12_20261026-1426-03_model-a6dc6eb.csv`
- Run ID: `20261026-1426-03_model-a6dc6eb`
- Code SHA: `a6dc6eb67617ddb15cad8f02d8c267428067a106`
- Hypothesis: transport level probe (tuned scalar 3, transport.value_scale)
- Change against current best: S07 with every transport gap draw multiplied by 1.5 and clipped to 1; POI and building identical; mean 0.073
- Expected direction: with S07 it fixes the transport level by line search; S10's t* = -0.40 suggests the optimum lies above 1
- Decision informed: transport.value_scale for the combined candidate
- Public RMSE: 0.076317659
- Submissions used after this one: 12 of 35
- Result note: line search t* = 0.30 along S07 to S12: transport.value_scale optimum 1.15, predicted 0.0749

## S13 (2026-10-26)

- File: `artifacts/submissions/S13_20261026-1427-03_model-92428b7.csv`
- Run ID: `20261026-1427-03_model-92428b7`
- Code SHA: `92428b7edf8dd8a5366d20b7572092b4fdb9ee2a`
- Hypothesis: building level probe (tuned scalar 4, building.baseline_gap)
- Change against current best: S07 with the building baseline gap at 0.05 instead of 0.01; transport and POI identical; mean 0.078
- Expected direction: with S07 it fixes the building level by line search
- Decision informed: building.baseline_gap for the combined candidate
- Public RMSE: 0.078012379
- Submissions used after this one: 13 of 35
- Result note: line search t* = -0.39 along S07 to S13: building baseline optimum below 0, set to 0, predicted 0.0749

## S14 (2026-10-27)

- File: `artifacts/submissions/S14_20261027-1001-03_model-c3c5417.csv`
- Run ID: `20261027-1001-03_model-c3c5417`
- Code SHA: `c3c541776253aaff68a29f718cce186b17540d9b`
- Hypothesis: combined level optimum (D032)
- Change against current best: S07 with transport.value_scale=1.15, building.baseline_gap=0 and poi.level=0.779, each at its line-search optimum; mean 0.054, rms 0.074
- Expected direction: about 0.0745 from the quadratic model fitted to S05, S07, S12 and S13
- Decision informed: new base for the fire-station structure test
- Public RMSE: 0.074538803
- Submissions used after this one: 14 of 35
- Result note: best so far; predicted 0.0745 by the quadratic model

## S15 (2026-10-27)

- File: `artifacts/submissions/S15_20261027-1100-03_model-d43cff5.csv`
- Run ID: `20261027-1100-03_model-d43cff5`
- Code SHA: `d43cff5b45872ac1a93f6a0712b7ac451123ae50`
- Hypothesis: H-P3 POI is driven by fire stations (organisers: fire stations carry the facility half)
- Change against current best: S14 with poi.mode=fire: POI 0 where Overture has a fire_department place, otherwise the expected gap from uncaptured reference stations spread by population and land area over tracts without one; schools and EMS count as matched where Overture has one; regional POI means equal to S14; transport and building identical
- Expected direction: below S14 if the true POI is near 0 in tracts with a mapped station and concentrated in tracts without one
- Decision informed: whether POI keeps tract structure; the S14 to S15 line search sizes the structure
- Public RMSE: 0.077160715
- Submissions used after this one: 15 of 35
- Result note: fire-station POI structure loses against S14

## S16 (2026-10-27)

- File: `artifacts/submissions/S16_20261027-2109-03_model-8d5f2ee.csv`
- Run ID: `20261027-2109-03_model-8d5f2ee`
- Code SHA: `8d5f2eed018355d450cc89e9dc679731be3dac40`
- Hypothesis: H-P3 at its line-search strength (poi.fire_strength=0.3)
- Change against current best: S14 with 30% of the fire-station POI structure blended into the regional constant; equals S14 + 0.300 x (S15 - S14) to rms 0.0003
- Expected direction: about 0.0740 from the S14 to S15 parabola
- Decision informed: new best method and base for the final candidates
- Public RMSE: pending
- Submissions used after this one: 16 of 35

## S17 (2026-10-27)

- File: `artifacts/submissions/S17_20261027-2139-03_model-8fffd01.csv`
- Run ID: `20261027-2139-03_model-8fffd01`
- Code SHA: `8fffd016d4ccefbfac84f79fd167e9292621296c`
- Hypothesis: exact transport from TIGER S1100 + S1200 (Zindi staff permission, 27 Oct)
- Change against current best: S16 with transport.source=tiger: T = gap(Overture named length, TIGER S1100+S1200 length clipped to the tract), defined where TIGER length > 0; TIGER undefined shares match the published rates (0.212, 0.369, 0.284, 0.546 against 0.21, 0.37, 0.28, 0.55); building 0 and POI fire blend as S16
- Expected direction: a large drop from S14's 0.0745, since transport carries most of the signal and is now computed instead of estimated
- Decision informed: how much of the remaining error sits in building and POI
- Public RMSE: 0.04905907
- Submissions used after this one: 17 of 35
- Result note: rank 21 at upload; exact TIGER transport; scale 0.989

## S18 (2026-10-28)

- File: `artifacts/submissions/S18_20261028-0024-03_model-8d8b042.csv`
- Run ID: `20261028-0024-03_model-8d8b042`
- Code SHA: `8d8b04267d09ad98e52724c4e7ed5da15b669905`
- Hypothesis: exact building gap from Microsoft US Building Footprints (Zindi staff permission, 27 Oct)
- Change against current best: S17 with building.source=microsoft: B = gap(Overture footprints, Microsoft footprints) per tract by centroid, defined where Microsoft has one (99.99% of tracts); B mean 0.0026; transport TIGER and POI fire blend as S17
- Expected direction: small gain over S17, since B is close to 0 nearly everywhere
- Decision informed: building handled exactly; base for the exact POI version
- Public RMSE: 0.05461568
- Submissions used after this one: 18 of 35
- Result note: exact Microsoft buildings worse than S17: line search t* = -0.84; the organisers' footprint release differs from the public US v2 file, building stays 0

## S19 (2026-10-28)

- File: `artifacts/submissions/S19_20261028-0947-03_model-672866c.csv`
- Run ID: `20261028-0947-03_model-672866c`
- Code SHA: `672866c709f24ae75954ac55c3f66d2d1d04df9a`
- Hypothesis: exact facility gaps from USGS National Structures (fire 74026, schools 73002-73005)
- Change against current best: S17 with poi.source=reference: fire and school gaps against USGS structure counts per tract, EMS left out (the ambulance layer breaks the S01 bound) and the establishments half at gap 0; transport TIGER, building 0; mean 0.054, rms 0.101 (true rms 0.107)
- Expected direction: below S17's 0.0491 if the organisers' fire and school reference matches USGS structures
- Decision informed: whether POI is now exact; the remaining gap to the bound points at EMS or establishments
- Public RMSE: 0.029960976
- Submissions used after this one: 19 of 35
- Result note: rank 21; scale 1.016; line search t* = 0.93 along S17 to S19

## S20 (2026-10-28)

- File: `artifacts/submissions/S20_20261028-1001-03_model-4b63973.csv`
- Run ID: `20261028-1001-03_model-4b63973`
- Code SHA: `4b63973fbbe6f60909c9b7c31f60a1f4d9ddc206`
- Hypothesis: establishments half: ZIP Business Patterns apportioned by business share (Overture places as the stand-in for HUD business-address ratios)
- Change against current best: S19 with poi.establishment_weight=places: E = gap(Overture places, ZBP 2023 establishments apportioned to tracts by place share within each ZCTA); positive in 1.4% of tracts; rms 0.1031 (true 0.107, S19 0.1014)
- Expected direction: small gain over S19's 0.0300 if the organisers apportioned establishments by business addresses
- Decision informed: the establishments half; whether the remaining variance sits there
- Public RMSE: 0.031525136
- Submissions used after this one: 20 of 35
- Result note: worse than S19; line search t* = 0.24 along S19 to S20 (predicted 0.02978): establishment gaps exist but weaker or placed differently

## S21 (2026-10-28)

- File: `artifacts/submissions/S21_20261028-1009-03_model-c6d4bb5.csv`
- Run ID: `20261028-1009-03_model-c6d4bb5`
- Code SHA: `c6d4bb51b051d0c613c485d4258cfd879eb2b95a`
- Hypothesis: EMS strength probe: EMS gaps against USGS ambulance services (74034)
- Change against current best: S19 with EMS added to the facility half (reference_types fire, ems, schools; establishments at 0); rms 0.1125 against S19's 0.1014 and the true 0.107
- Expected direction: raw score may be worse than S19; the S19 to S21 line search fixes how much EMS binding the target holds
- Decision informed: EMS weight in the final candidate
- Public RMSE: 0.042893728
- Submissions used after this one: 21 of 35
- Result note: line search t* = 0.07 along S19 to S21: EMS binding is essentially absent
