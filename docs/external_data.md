# External data for the Best Bias Discovery analysis

Sources used only in stage 04 to describe the bias discovery. None of them enters the scored
pipeline.

| Source | URL | Retrieved | Licence | Preprocessing |
|---|---|---|---|---|
| Census Bureau 2020 county code list (`national_county2020.txt`) | https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt | at each stage 04 run (first 29 Oct 2026) | US Government work, public domain | `STATEFP` and `COUNTYFP` joined into a 5-digit FIPS, `COUNTYNAME, STATE` as the label. Used to name the county of each listed tract |
