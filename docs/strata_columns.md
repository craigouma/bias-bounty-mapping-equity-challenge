# Strata column dictionary

Source: stage 01 audit table `tables/strata_columns.csv` (run 20261025-1434-01_ingest-398b1ba). The region strata tables
carry 227 columns (the national table has 232). Null rates are per region; a null means the source does not reach
the tract and is never a zero.

| Column | Dtype | Meaning | Null eastern-ok | eastern-wa | maricopa-az | northern-ca | south-central-tx |
|---|---|---|---|---|---|---|---|
| GEOID | VARCHAR | tract id, 11-digit text | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| STATEFP | VARCHAR | state FIPS | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| COUNTYFP | VARCHAR | county FIPS | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ALAND | BIGINT | land area, m2 (TIGER) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pop_total | BIGINT | 2020 DHC population (total, urban, rural) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pop_urban | BIGINT | 2020 DHC population (total, urban, rural) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pop_rural | BIGINT | 2020 DHC population (total, urban, rural) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pct_urban | DOUBLE | urban share of population | 0.001 | 0.002 | 0.007 | 0.000 | 0.003 |
| ur_class | VARCHAR | urban or rural class | 0.001 | 0.002 | 0.007 | 0.000 | 0.003 |
| frac_inside_aoi | DOUBLE | share of tract inside the region (1.0 everywhere) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| svi_covered | BOOLEAN | CDC SVI 2022 percentile or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| svi_rank_universe | VARCHAR | CDC SVI 2022 percentile or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| svi_overall | DOUBLE | CDC SVI 2022 percentile or metadata | 0.009 | 0.007 | 0.018 | 0.000 | 0.009 |
| svi_socioeconomic | DOUBLE | CDC SVI 2022 percentile or metadata | 0.009 | 0.007 | 0.018 | 0.000 | 0.009 |
| svi_household | DOUBLE | CDC SVI 2022 percentile or metadata | 0.009 | 0.007 | 0.018 | 0.000 | 0.009 |
| svi_minority | DOUBLE | CDC SVI 2022 percentile or metadata | 0.003 | 0.005 | 0.011 | 0.000 | 0.006 |
| svi_housing_transport | DOUBLE | CDC SVI 2022 percentile or metadata | 0.009 | 0.007 | 0.018 | 0.000 | 0.009 |
| svi_pop | DOUBLE | CDC SVI 2022 percentile or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| svi_year | BIGINT | CDC SVI 2022 percentile or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cvi_covered | BOOLEAN | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cvi_xwalk_coverage | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_overall | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_baseline | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_climate | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_baseline_health | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_baseline_socioeconomic | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_baseline_infrastructure | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_baseline_environment | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_climate_health | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_climate_socioeconomic | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_climate_extreme_events | DOUBLE | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| cvi_source_vintage | BIGINT | Climate Vulnerability Index score or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ruca_covered | BOOLEAN | USDA RUCA 2020 code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ruca_primary | DOUBLE | USDA RUCA 2020 code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ruca_primary_desc | VARCHAR | USDA RUCA 2020 code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ruca_secondary | DOUBLE | USDA RUCA 2020 code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ruca_pop_density | DOUBLE | USDA RUCA 2020 code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ruca_year | BIGINT | USDA RUCA 2020 code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| rucc_covered | BOOLEAN | USDA RUCC 2023 county code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| rucc_2023 | BIGINT | USDA RUCC 2023 county code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| rucc_desc | VARCHAR | USDA RUCC 2023 county code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| rucc_metro | BOOLEAN | USDA RUCC 2023 county code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| rucc_year | BIGINT | USDA RUCC 2023 county code or metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nchs_covered | BOOLEAN | NCHS urban-rural 2013 class | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nchs_2013 | DOUBLE | NCHS urban-rural 2013 class | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nchs_2013_label | VARCHAR | NCHS urban-rural 2013 class | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nchs_year | BIGINT | NCHS urban-rural 2013 class | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| tribal_any | BOOLEAN | overlap with tribal areas | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| tribal_pct | DOUBLE | overlap with tribal areas | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| tribal_legal | BOOLEAN | overlap with tribal areas | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| tribal_legal_pct | DOUBLE | overlap with tribal areas | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| tribal_statistical | BOOLEAN | overlap with tribal areas | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| tribal_stat_pct | DOUBLE | overlap with tribal areas | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| aiannh_geoid | VARCHAR | overlapping AIANNH area id, name or kind | 0.324 | 0.928 | 0.968 | 0.922 | 1.000 |
| aiannh_name | VARCHAR | overlapping AIANNH area id, name or kind | 0.324 | 0.928 | 0.968 | 0.922 | 1.000 |
| aiannh_kind | VARCHAR | overlapping AIANNH area id, name or kind | 0.324 | 0.928 | 0.968 | 0.922 | 1.000 |
| usdm_covered | BOOLEAN | US Drought Monitor seasonal DSCI or share in drought | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usdm_summer_dsci | DOUBLE | US Drought Monitor seasonal DSCI or share in drought | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| usdm_summer_pct_d0plus | DOUBLE | US Drought Monitor seasonal DSCI or share in drought | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| usdm_summer_pct_d2plus | DOUBLE | US Drought Monitor seasonal DSCI or share in drought | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| usdm_winter_dsci | DOUBLE | US Drought Monitor seasonal DSCI or share in drought | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| usdm_winter_pct_d0plus | DOUBLE | US Drought Monitor seasonal DSCI or share in drought | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| usdm_winter_pct_d2plus | DOUBLE | US Drought Monitor seasonal DSCI or share in drought | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| usdm_year_min | BIGINT | US Drought Monitor seasonal DSCI or share in drought | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usdm_year_max | BIGINT | US Drought Monitor seasonal DSCI or share in drought | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_covered | BOOLEAN | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_BP_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_CFL_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_CRPS_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_RPS_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_WHP_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_Exposure_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_FLEP4_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_FLEP8_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_CWiRRZ_majority_label | VARCHAR | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_CWiRRZ_majority_zone4_label | VARCHAR | USFS Wildfire Risk to Communities raster summary | 0.008 | 0.123 | 0.068 | 0.096 | 0.019 |
| usfs_BuildingCount_sum | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_BuildingCover_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_BuildingDensity_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_HUCount_sum | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_HUDen_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_HUExposure_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.001 | 0.000 | 0.001 |
| usfs_HUImpact_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.001 | 0.000 | 0.001 |
| usfs_HURisk_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.001 | 0.000 | 0.001 |
| usfs_PopCount_sum | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_PopDen_mean | DOUBLE | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_edition | VARCHAR | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usfs_extent | VARCHAR | USFS Wildfire Risk to Communities raster summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| epht_covered | BOOLEAN | CDC EPHT extreme heat days or events | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| epht_heat_days_summer | DOUBLE | CDC EPHT extreme heat days or events | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| epht_heat_days_annual | DOUBLE | CDC EPHT extreme heat days or events | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| epht_heat_events_summer | DOUBLE | CDC EPHT extreme heat days or events | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| epht_threshold | VARCHAR | CDC EPHT extreme heat days or events | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| epht_metric | VARCHAR | CDC EPHT extreme heat days or events | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| epht_year_min | BIGINT | CDC EPHT extreme heat days or events | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| epht_year_max | BIGINT | CDC EPHT extreme heat days or events | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| carbonplan_covered | BOOLEAN | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| carbonplan_buildings | DOUBLE | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| carbonplan_bp_2011_mean | DOUBLE | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| carbonplan_bp_2011_median | DOUBLE | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| carbonplan_bp_2047_mean | DOUBLE | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| carbonplan_crps_mean | DOUBLE | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| carbonplan_rps_2011_mean | DOUBLE | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| carbonplan_rps_2011_median | DOUBLE | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| carbonplan_rps_2047_mean | DOUBLE | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| carbonplan_version | VARCHAR | CarbonPlan fire risk summary | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usgs_covered | BOOLEAN | USGS combined wildfire: burned share, return interval, years | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usgs_wildland_fire_burned_pct_area | DOUBLE | USGS combined wildfire: burned share, return interval, years | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usgs_wildfire_burned_pct_area | DOUBLE | USGS combined wildfire: burned share, return interval, years | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usgs_wildfire_pct_area_2plus | DOUBLE | USGS combined wildfire: burned share, return interval, years | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usgs_prescribed_burned_pct_area | DOUBLE | USGS combined wildfire: burned share, return interval, years | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usgs_wildfire_return_interval_years | DOUBLE | USGS combined wildfire: burned share, return interval, years | 0.790 | 0.569 | 0.856 | 0.580 | 0.920 |
| usgs_wildfire_fires_per_burned_pixel | DOUBLE | USGS combined wildfire: burned share, return interval, years | 0.790 | 0.569 | 0.856 | 0.580 | 0.920 |
| usgs_first_year_burned | DOUBLE | USGS combined wildfire: burned share, return interval, years | 0.790 | 0.569 | 0.856 | 0.580 | 0.920 |
| usgs_last_year_burned | DOUBLE | USGS combined wildfire: burned share, return interval, years | 0.792 | 0.569 | 0.857 | 0.580 | 0.920 |
| usgs_years_since_last_fire | DOUBLE | USGS combined wildfire: burned share, return interval, years | 0.792 | 0.569 | 0.857 | 0.580 | 0.920 |
| usgs_wildfire_ever | BOOLEAN | USGS combined wildfire: burned share, return interval, years | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usgs_record_start | BIGINT | USGS combined wildfire: burned share, return interval, years | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| usgs_record_end | BIGINT | USGS combined wildfire: burned share, return interval, years | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| mtbs_covered | BOOLEAN | MTBS burned area 1984-2023 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| mtbs_wildfire_burned_pct_land | DOUBLE | MTBS burned area 1984-2023 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| mtbs_wildfire_burned_km2 | DOUBLE | MTBS burned area 1984-2023 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| mtbs_wildfire_fires | INTEGER | MTBS burned area 1984-2023 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| mtbs_wildfire_last_year | DOUBLE | MTBS burned area 1984-2023 | 0.806 | 0.651 | 0.896 | 0.760 | 0.957 |
| mtbs_wildfire_ever | BOOLEAN | MTBS burned area 1984-2023 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| mtbs_years_since_wildfire | DOUBLE | MTBS burned area 1984-2023 | 0.806 | 0.651 | 0.896 | 0.760 | 0.957 |
| mtbs_prescribed_burned_pct_land | DOUBLE | MTBS burned area 1984-2023 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| mtbs_year_min | BIGINT | MTBS burned area 1984-2023 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| mtbs_year_max | BIGINT | MTBS burned area 1984-2023 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| mtbs_size_threshold | VARCHAR | MTBS burned area 1984-2023 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nifc_covered | BOOLEAN | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nifc_wildfire_burned_pct_land | DOUBLE | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| nifc_wildfire_burned_km2 | DOUBLE | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nifc_wildfire_fires | INTEGER | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nifc_wildfire_last_year | DOUBLE | NIFC perimeters 1984-2025 | 0.867 | 0.494 | 0.873 | 0.646 | 0.877 |
| nifc_wildfire_ever | BOOLEAN | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nifc_years_since_wildfire | DOUBLE | NIFC perimeters 1984-2025 | 0.867 | 0.494 | 0.873 | 0.646 | 0.877 |
| nifc_prescribed_burned_pct_land | DOUBLE | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| nifc_wildfire_fires_history | INTEGER | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nifc_wildfire_fires_wfigs | INTEGER | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nifc_year_min | BIGINT | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nifc_year_max | BIGINT | NIFC perimeters 1984-2025 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_covered | BOOLEAN | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_fires | INTEGER | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_acres_ignited | DOUBLE | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_ignition_density | DOUBLE | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| fod_human_fires | INTEGER | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_natural_fires | INTEGER | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_large_fires | INTEGER | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_human_share | DOUBLE | FPA FOD ignitions 1992-2020 | 0.620 | 0.405 | 0.030 | 0.102 | 0.374 |
| fod_human_share_classified | DOUBLE | FPA FOD ignitions 1992-2020 | 0.628 | 0.417 | 0.117 | 0.166 | 0.380 |
| fod_cause_unknown_share | DOUBLE | FPA FOD ignitions 1992-2020 | 0.620 | 0.405 | 0.030 | 0.102 | 0.374 |
| fod_last_fire_year | DOUBLE | FPA FOD ignitions 1992-2020 | 0.620 | 0.405 | 0.030 | 0.102 | 0.374 |
| fod_largest_fire_acres | DOUBLE | FPA FOD ignitions 1992-2020 | 0.620 | 0.405 | 0.030 | 0.102 | 0.374 |
| fod_ever | BOOLEAN | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_year_min | BIGINT | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_year_max | BIGINT | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| fod_edition | VARCHAR | FPA FOD ignitions 1992-2020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_covered | BOOLEAN | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_stations_in_tract | INTEGER | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_temp_stations_in_tract | INTEGER | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_any_nearest_km | DOUBLE | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_temp_nearest_km | DOUBLE | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_prcp_nearest_km | DOUBLE | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_any_within_25km | INTEGER | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_temp_within_25km | INTEGER | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_anchor_unreliable | BOOLEAN | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_year_min | BIGINT | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ghcn_year_max | BIGINT | NOAA GHCN station coverage | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cdcw_covered | BOOLEAN | CDC WONDER metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cdcw_grain | VARCHAR | CDC WONDER metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_maxtemp_mean | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_maxtemp_change | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_maxtemp_trend_days_per_decade | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_maxtemp_trend_p | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_maxtemp_never_defined | BOOLEAN | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_heatindex_mean | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_heatindex_change | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_heatindex_trend_days_per_decade | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_heatindex_trend_p | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_heatindex_never_defined | BOOLEAN | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_heatstress_mean | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_heatstress_change | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_heatstress_trend_days_per_decade | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| hwd_heatstress_trend_p | DOUBLE | CDC WONDER heat-wave days | 0.000 | 0.007 | 0.000 | 0.014 | 0.000 |
| hwd_heatstress_never_defined | BOOLEAN | CDC WONDER heat-wave days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cdcw_window_start | BIGINT | CDC WONDER metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cdcw_window_end | BIGINT | CDC WONDER metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_covered | BOOLEAN | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_coverage_frac | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_wbgt28_days_mean | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_wbgt28_days_change | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_wbgt28_trend_days_per_yr | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_wbgt30_days_mean | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_wbgt30_days_change | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_wbgt30_trend_days_per_yr | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_wbgt32_days_mean | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_wbgt32_days_change | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_wbgt32_trend_days_per_yr | DOUBLE | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_record_start | BIGINT | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gehe_record_end | BIGINT | NASA GEHE wet-bulb heat days | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| uhe_covered | BOOLEAN | NASA UHE-Daily urban heat | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| uhe_city_name | VARCHAR | NASA UHE-Daily urban heat | 0.580 | 0.624 | 0.308 | 0.486 | 0.356 |
| uhe_city_country | VARCHAR | NASA UHE-Daily urban heat | 0.580 | 0.624 | 0.308 | 0.486 | 0.356 |
| uhe_overlap_frac | DOUBLE | NASA UHE-Daily urban heat | 0.580 | 0.624 | 0.308 | 0.486 | 0.356 |
| uhe_wbgtmax28_days_per_yr | DOUBLE | NASA UHE-Daily urban heat | 0.580 | 0.624 | 0.308 | 0.486 | 0.356 |
| uhe_wbgtmax30_days_per_yr | DOUBLE | NASA UHE-Daily urban heat | 0.580 | 0.624 | 0.308 | 0.486 | 0.356 |
| uhe_himax461_days_per_yr | DOUBLE | NASA UHE-Daily urban heat | 0.580 | 0.624 | 0.308 | 0.486 | 0.356 |
| pmdi_covered | BOOLEAN | Palmer modified drought index | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pmdi_mean | DOUBLE | Palmer modified drought index | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pmdi_summer_mean | DOUBLE | Palmer modified drought index | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pmdi_winter_mean | DOUBLE | Palmer modified drought index | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pmdi_pct_months_severe | DOUBLE | Palmer modified drought index | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pmdi_recent_percentile | DOUBLE | Palmer modified drought index | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| pmdi_mean_1895_2025 | DOUBLE | Palmer modified drought index | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| spi_covered | BOOLEAN | Standardized Precipitation Index metadata | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| spi_calibration | DOUBLE | Standardized Precipitation Index metadata | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| spi03_mean | DOUBLE | 3-month SPI | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| spi03_summer_mean | DOUBLE | 3-month SPI | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| spi03_winter_mean | DOUBLE | 3-month SPI | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| spi03_pct_months_d2 | DOUBLE | 3-month SPI | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| spi12_mean | DOUBLE | 12-month SPI | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| spi12_summer_mean | DOUBLE | 12-month SPI | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| spi12_winter_mean | DOUBLE | 12-month SPI | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| spi12_pct_months_d2 | DOUBLE | 12-month SPI | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| drought_gov_window_start | BIGINT | drought.gov window | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| drought_gov_window_end | BIGINT | drought.gov window | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
