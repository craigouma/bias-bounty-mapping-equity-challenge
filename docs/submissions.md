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
