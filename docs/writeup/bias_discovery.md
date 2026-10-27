# Best Bias Discovery draft: unnamed roads in tribal areas

Source: stage 04 run `20261027-0949-04_analysis-81b7f88` on features run
`20261026-1136-02_features-c1f6404`. Challenge data only.

## Pattern

Overture road segments without a name (`names.primary` is null) make up a far larger share of the
drivable network in tribal tracts than in non-tribal tracts of the same region and rurality. The
Bias Scorecard measures road length and feature counts, so a tract whose roads are all present
but unnamed scores as fully covered.

## Evidence

Share of drivable road length (classes motorway to unclassified, clipped to the tract) with no
name, tribal against non-tribal tracts within region and RUCA class (figure
`figures/unnamed_share_by_stratum.png`). Tribal tracts are higher in 12 of 16 cells; the exceptions
are cells with fewer than ten tracts on one side.

Matched difference (tribal minus non-tribal mean share, cells weighted by tribal tract count),
95% intervals from 1,000 county-block bootstrap resamples:

| Region | Tribal tracts | Difference (points) | 95% interval |
|---|---|---|---|
| maricopa-az | 37 | +6.0 | +1.8 to +9.3 |
| eastern-wa | 16 | +4.6 | +0.6 to +14.1 |
| eastern-ok | 805 | +4.6 | -5.2 to +9.2 |
| northern-ca | 15 | +4.0 | -2.5 to +8.9 |

Eastern Oklahoma's interval is wide because 805 of its 1,192 scored tracts are tribal, so almost
every county is tribal and county resampling leaves little contrast.

Tribal areas with the most unnamed drivable road:

| Area | Region | Tracts | Unnamed km | Share | Population |
|---|---|---|---|---|---|
| Cheyenne and Arapaho OTSA | eastern-ok | 57 | 13,066 | 47% | 214,569 |
| Choctaw OTSA | eastern-ok | 67 | 8,831 | 34% | 223,362 |
| Cherokee OTSA | eastern-ok | 152 | 7,731 | 30% | 520,435 |
| Kiowa-Comanche-Apache-Fort Sill Apache OTSA | eastern-ok | 63 | 7,427 | 38% | 191,725 |
| Chickasaw OTSA | eastern-ok | 93 | 6,361 | 28% | 304,578 |
| Osage Reservation | eastern-ok | 13 | 2,466 | 57% | 45,818 |
| Fort Apache Reservation | maricopa-az | 5 | 825 | 29% | 18,587 |
| Tohono O'odham Nation Reservation | maricopa-az | 6 | 762 | 30% | 13,333 |
| Colville Reservation | eastern-wa | 3 | 671 | 24% | 7,804 |

Tract-level list: `analysis/tables/unnamed_worst_tribal_tracts.csv` (GEOID, tract, county).

## Consequences (to be completed)

Emergency dispatch geocodes a caller's address to a named street; turn-by-turn routing and
evacuation instructions refer to roads by name. Where a third to over half of the drivable
network has no name in the open map, an address on those roads cannot be matched, ambulance and
fire routing falls back to coordinates or local knowledge, and evacuation messaging cannot name
the egress road.

## Still to do

- Separate tribal statistical areas (OTSAs) from legal reservations.
- Check named-class roads only, so unnamed driveways or tracks do not drive the result.
- Name the worst tracts with county and community.
