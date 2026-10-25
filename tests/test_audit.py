import json

import pytest

from bbme import db
from bbme.ingest.audit import Audit
from synthetic import REGION, TRACT_B, build_raw


@pytest.fixture(scope="module")
def audited(tmp_path_factory):
    root = tmp_path_factory.mktemp("audit")
    raw = build_raw(root / "raw")
    out = root / "audit"
    failures = Audit(raw, out, {"regions": [REGION]}, db.connect()).run()
    return out, failures


def test_every_section_runs(audited):
    out, failures = audited
    assert failures == [], (out / "data_audit.md").read_text()


def test_schemas_cover_every_parquet(audited):
    out, _ = audited
    schemas = json.loads((out / "schemas.json").read_text())
    assert f"reference/{REGION}/{REGION}-overture-roads.parquet" in schemas
    assert schemas[f"reference/{REGION}/{REGION}-overture-pois.parquet"]["rows"] == 4


def test_edge_tracts_include_the_water_tract(audited):
    out, _ = audited
    edge = (out / "tables" / "edge_tracts.csv").read_text()
    assert TRACT_B in edge
