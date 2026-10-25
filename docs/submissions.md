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
- Public RMSE: pending
- Submissions used after this one: 1 of 35
