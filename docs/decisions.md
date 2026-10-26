# Decisions

Dated decisions with reasons. Tunable scalars are logged with their default, values tried and the
chosen value.

## 2026-10-25

**D001. Eastern Washington is treated as scored.** The sample submission carries its 415 rows and
no answer on scoring exists yet. The pipeline applies the same method to it.

**D002. The guard checks the allowlist before the denylist.** The permitted stratum
`<region>-usgs-combined-tract-table` (USGS reburn and fire return interval) contains the denylisted
token `usgs`. A file name that matches a provided-file pattern is admitted; any other path that
contains a denylisted token in its name or a parent directory is rejected. The bucket listing check
uses the same rule.

**D003. Stage 01 downloads with Python over the S3 REST endpoint.** The Kaggle image has no `aws`
CLI, installing `awscli` risks conflicts with the image's boto3 and botocore, and the HTTPS proxy
rejects Python's default User-Agent. Stage 01 lists the bucket with ListObjectsV2, downloads the
same file set as the reference `aws s3 sync` commands in the project brief section 8.2, and keeps the byte
check and up to 3 retries.

**D004. Python 3.13.** Stage 00 reports Python 3.13.15 on the Kaggle image, so `requires-python`
is `>=3.13,<3.14` and local work uses 3.13.

**D005. One stage bootstrap.** The bootstrap from the project brief section 8.3 lives once in
`kaggle/stages/bootstrap.py`. The renderer prepends it to each stage's `run.py` (which defines
`main(run, code)`) and appends the call, so every rendered kernel still starts with the bootstrap.
Stage 00 skips the dependency install so it reports the image as shipped.

**D006. The submission writer derives `poi_gap` and `poi_defined`.** They are computed from the
four POI sub-columns under rule 4 of section 5.4, so the file is consistent by construction. The
validator checks the same rule independently on the text of the file.

**D007. Draft POI mapping copies the organisers' README.** `configs/poi_categories.yaml` uses the
category lists the bucket README gives for fire stations, EMS and schools, on
`categories.primary`. It stays marked `reviewed: false` until Craig reviews it.

**D008. ACS housing units and Overture `sources` attributes are permitted features.** Both are in
the challenge package. Their use is disclosed in the writeup and dropped if an organiser says
otherwise.

**D009. Empty root commit on `main`.** Git cannot branch from an unborn `main`, so the repository
starts with one empty commit. All later work happens on branches.

**D010. S01 sets the target scale.** S01 (all zeros) scored 0.107246299 public RMSE, so the mean
of y squared on the public split is about 0.0115. Most tracts have a composite near 0 with a sparse
tail of large values. Predictions stay low and hard 0 or 1 calls are avoided.

**D011. Scorecards of zero-RMSE entries are not used.** Several leaderboard entries score exactly
0, which is only possible by reproducing the organisers' reference scores, most likely from the
removed layers or the old coverage-gap files. Their public Bias Scorecards reveal stratum-level
ratios of the true scores. Using those ratios would be calibrating on leaked labels, so the
pipeline does not use them. Changing this needs Craig's decision.

**D012. Close date.** The Zindi leaderboard page shows Close 01 Nov 2026 and Reveal 01 Nov 2026
(read 25 Oct 2026). The exact closing hour is still to be read from the countdown. Until then the
plan keeps the final selection on Sat 31 Oct.

**D013. Building-count strata held out pending Craig.** The strata tables carry
`usfs_BuildingCount_sum`, `usfs_BuildingCover_mean`, `usfs_BuildingDensity_mean` (USFS Wildfire
Risk to Communities) and `carbonplan_buildings`. They are in the permitted package, but they may
be derived from building-footprint products close to the removed Microsoft reference. They stay
out of every feature and model until Craig decides.

**D014. Stage 03 runs on CPU for v1.** The v1 estimators are analytic and Monte Carlo only, so
the GPU quota is kept for the learned building model. `configs/kaggle.yaml` switches back when a
GPU stage is needed.

**D015. v1 estimator defaults.** S01 shows the true composite is mostly small (D010), so v1 is
conservative:

- Transport: reference proxy = interstate, US and state route networks plus motorway and trunk
  (set A in `configs/features.yaml`) in every region; tau per region at the quantile matching the
  published undefined rate less 0.01 for building or POI; p = 0.95 above tau and the p_lo that
  makes the region mean match below it; L_R noise lognormal sigma 0.15 above tau and 1.0 for the
  unseen length below it. eastern-wa borrows the median tau and p_lo.
- Building: max(0.02, gap(N_O, q10 * HU)), q10 being the 10th percentile of footprints per
  housing unit among tracts at least 95% ML-derived in the same region and RUCA class; 1 where
  Overture has no footprint. p = 0.995 with footprints or housing units, 0.2 otherwise.
- POI: facility reference ~ Poisson(0.5 * observed + 0.5 * prior), prior = the region's Overture
  total spread by population and land area (fire, EMS) or population (schools);
  establishments = 0.025 * population with lognormal sigma 0.5, undefined at zero population.
- Composite: 2,000 joint draws per tract, conditional on at least one component defined; alpha 1.

**D016. Local history rewritten once before the first push.** Before the remote existed, every
commit was rewritten so that repo content refers to "the project brief" and the local hook
source lives in the git-excluded `.hooks/`. Kaggle run IDs created before the rewrite carry the
old SHAs: `4ffe361` is now `a594b8c` (stage 00), `398b1ba` is now `0507ec9` (stage 01),
`0aa771e` is now `a6a65f0` (first stage 02 run). Pushed history is never rewritten.

**D017. Building-count strata become hypothesis H-B3 (Craig, 25 Oct 2026).** Craig approved
using `usfs_BuildingCount_sum`, `usfs_BuildingCover_mean`, `usfs_BuildingDensity_mean` and
`carbonplan_buildings` if they improve the leaderboard. They enter as a separate tested variant
of the building reference estimate, are kept only if the public score improves beyond the 0.003
tie band, and are disclosed in the writeup with their possible derivation from footprint
products. This replaces the hold in D013.

**D018. Five submissions per day.** Craig's Zindi account allows 5 uploads per day. The 35
submission budget stands; the daily plan in the project brief section 11.2 now caps each day at 5.

**D019. Tiered transport reference.** From the stage 02 calibration (docs/experiments.md, 25 Oct):
high tier = tracts with interstate, US or state route, motorway or trunk length (set A); mid tier
= tracts with only secondary state, toll or business routes (set B); low tier = neither.
Definedness is 0.98 in the high tier, 0.02 floor in the low tier, and the mid tier probability
is solved per region so the mean matches the published undefined rate less 0.01. A high-tier
tract's reference includes its secondary routes with probability p_mid / 0.98. eastern-wa
borrows the median probabilities.

**D020. v1 scale set by the S01 bound.** A calibrated expectation cannot have a larger second
moment than the target, so rms(prediction) must stay below S01's 0.107. The first v1 run had
rms 0.193. Three defaults changed, none tuned on the leaderboard: schools get a reference-to-Overture
ratio of 0.4 (Overture carries two to three school places per school); kappa_E drops to 0.01
(establishments are most likely apportioned by business addresses, so places rarely fall short);
the building per-unit deficit is switched off (it flagged metro apartment tracts where few
footprints per housing unit is real). The resulting S02 file has mean 0.058 and rms 0.079.

**D021. Scaled RMSE as the comparison metric.** With E[y^2] from S01 (0.0115019) and a
submission's E[p^2] from its own file, its public RMSE R gives E[yp] = (E[y^2] + E[p^2] - R^2) / 2.
The best global multiplicative scale for that method is s = E[yp] / E[p^2], and its RMSE at that
scale is sqrt(E[y^2] - E[yp]^2 / E[p^2]). Hypotheses are compared on this scaled RMSE, which
isolates the method's signal from its overall level. S02: s = 0.644, scaled RMSE 0.0944.
A global output scale is a tunable scalar (1 of 6, section 4.4) and is applied only to final
candidates or to a submission registered to test it. E[p^2] is computed over all tracts; the
public split is a random 30%, and excluding eastern-wa changes the S02 values by under 0.0002.

**D022. H-T1 confirmed; boundary distance is tuned scalar 1 of 6.** S03 (transport reference
counted up to 25 m outside each tract edge) improved the scaled RMSE from 0.0944 to 0.0840, well
beyond the 0.003 tie band. TIGER highways that form tract boundaries count in both neighbouring
tracts. `transport.boundary_d_m` default 0; values tried 0, 25; at most one more value (50) is
tested. The global output scale (D021) is tuned scalar 2 of 6.

**D023. Boundary distance fixed at 25 m.** S04 (d = 50 m) scored scaled RMSE 0.0839 against
0.0840 for d = 25 m, a tie inside the 0.003 band, and a worse raw score because it predicts
higher. Tuned scalar 1 is closed: tried 0, 25, 50; chosen 25 (the smaller change). d = 100 is not
tested. The Zindi submissions page shows a cap of 200 in total (read 25 Oct); the 35 budget stands.

**D024. Tract-level POI estimates dropped from the default (H-P0).** S05 replaced every tract's
POI value with its region's mean v1 POI estimate and improved the scaled RMSE from 0.0840 to
0.0766, with the best scale moving from 0.68 to 0.89. The v1 facility and establishment models
added variance unrelated to the target, and that variance was most of the over-prediction.
`poi.mode` defaults to `constant`. A tract-level POI variant returns only if it beats the
constant on scaled RMSE. Transport carries most of the signal found so far.

**D025. Independent random streams per component.** Each component now draws from its own
Generator spawned from the config seed (`numpy.random.SeedSequence(seed).spawn(3)`), so a change
to one estimator cannot move another component's Monte Carlo draws. Rerunning the S05 method
with the new streams changes scores by rms 0.0011 (max 0.015), far inside the 0.003 tie band, so
S05's result stands for the current default.

## 2026-10-26

**D026. H-B3 rejected.** S06 (building gap from the USFS building count) scored scaled RMSE
0.0805 against 0.0766 for S05. Building stays at the 0.01 baseline (`building.reference: none`).
The USFS columns remain in the feature table for the bias discovery analysis only.

**D027. H-P1 adopted, H-T2 rejected.** S07 (establishments half defined with gap 0,
`poi.kappa_E: 0`) scored 0.075184 raw, scaled RMSE 0.0752 against 0.0766, at a best scale of
exactly 1.00. The gain is inside the tie band, but the variant is simpler, physically motivated
(Overture places outnumber CBP establishments three to five times) and calibrated without any
scale, so it becomes the default. S08 (`transport.sigma: 0.05`) scored scaled 0.0773, a tie;
sigma stays 0.15 and the knob is closed after one test.
