import pandas as pd
import pytest

from bbme.regions import assert_matches_sample, scored_tracts

ROWS = {
    "maricopa-az": ["04013010101", "35023970000"],
    "eastern-ok": ["40013795900"],
}


@pytest.fixture
def raw(tmp_path):
    for region, geoids in ROWS.items():
        folder = tmp_path / "reference" / region
        folder.mkdir(parents=True)
        lines = ["GEOID,coverage_gap_score"] + [f"{g},0.0" for g in geoids]
        (folder / f"{region}-sample-submission.csv").write_text("\n".join(lines) + "\n")
    return tmp_path


def test_region_comes_from_lists_not_fips(raw):
    scored = scored_tracts(raw, list(ROWS))
    assert scored.set_index("GEOID").loc["35023970000", "region"] == "maricopa-az"
    assert scored["GEOID"].is_monotonic_increasing


def test_mismatch_with_sample_raises(raw):
    scored = scored_tracts(raw, list(ROWS))
    sample = scored.copy()
    assert_matches_sample(scored, sample)
    sample.loc[sample["GEOID"] == "35023970000", "region"] = "eastern-ok"
    with pytest.raises(ValueError):
        assert_matches_sample(scored, sample)


def test_duplicate_membership_raises(raw):
    path = raw / "reference" / "eastern-ok" / "eastern-ok-sample-submission.csv"
    path.write_text("GEOID,coverage_gap_score\n04013010101,0.0\n")
    with pytest.raises(ValueError):
        scored_tracts(raw, list(ROWS))


def test_sample_frame_shape():
    df = pd.DataFrame({"GEOID": ["04013010101"], "region": ["maricopa-az"]})
    assert_matches_sample(df, df)
