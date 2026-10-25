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
