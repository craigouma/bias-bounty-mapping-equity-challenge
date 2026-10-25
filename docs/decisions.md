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
