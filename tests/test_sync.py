import pytest

from bbme import guard
from bbme.config import load
from bbme.ingest import sync

REGIONS = load("data")["regions"]


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("README.md", True),
        ("boundaries/all-aois.geojson", True),
        ("boundaries/eastern-ok-tract-geoids.csv", True),
        ("reference/eastern-ok/eastern-ok-overture-roads.parquet", True),
        ("reference/eastern-ok/eastern-ok-census-acs-housing.parquet", True),
        ("reference/eastern-ok/eastern-ok-census-acs-housing.csv", False),
        ("reference/eastern-ok/eastern-ok-sample-submission.csv", True),
        ("strata/eastern-wa/eastern-wa-svi-tract-table.parquet", True),
        ("strata/eastern-wa/eastern-wa-svi-tract-table.csv", False),
        ("strata/national/national-svi-tract-table.parquet", False),
        ("strata/national/national-census-tract-table.parquet", True),
        ("bulk-downloads/reference.zip", False),
        ("bulk-downloads/README.md", False),
    ],
)
def test_wanted_matches_reference_sync(key, expected):
    assert sync.wanted(key, REGIONS) is expected


def test_wanted_files_all_pass_the_guard():
    keys = [
        f"reference/{r}/{r}-overture-{layer}.parquet"
        for r in REGIONS
        for layer in load("data")["overture_layers"]
    ]
    for key in keys:
        assert sync.wanted(key, REGIONS)
        guard.raw(key)


def test_bucket_uri_split():
    bucket, prefix = sync._split(load("data")["bucket"])
    assert bucket == "us-west-2.opendata.source.coop"
    assert prefix == "humane-intelligence/bias-bounty-mapping-equity-challenge/"
