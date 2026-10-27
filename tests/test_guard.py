import ast
from pathlib import Path

import pytest

from bbme import guard

REPO = Path(__file__).resolve().parents[1]
READERS = {
    "read_parquet",
    "read_csv",
    "read_table",
    "read_file",
    "read_dataframe",
    "ParquetFile",
    "dataset",
}
WRAPPERS = {REPO / "src/bbme/geoid.py", REPO / "src/bbme/guard.py"}


def _modules(*roots: str) -> list[Path]:
    return [p for r in roots for p in sorted((REPO / r).rglob("*.py"))]


def _callee(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return None


def _is_guarded(arg: ast.expr) -> bool:
    return (
        isinstance(arg, ast.Call)
        and isinstance(arg.func, ast.Attribute)
        and isinstance(arg.func.value, ast.Name)
        and arg.func.value.id == "guard"
    )


@pytest.mark.parametrize(
    "name",
    [
        "maricopa-az-overture-buildings.parquet",
        "south-central-tx-overture-roads-unfiltered.parquet",
        "eastern-wa-census-acs-housing.csv",
        "northern-ca-usgs-combined-tract-table.parquet",
        "national-strata-tract-table.parquet",
        "eastern-ok-sample-submission.csv",
        "all-aois.geojson",
        "eastern-ok-tract-geoids.csv",
        "SampleSubmission.csv",
    ],
)
def test_provided_files_open(name):
    assert guard.raw(Path("/kaggle/input/raw") / name).name == name


@pytest.mark.parametrize(
    "name",
    [
        "maricopa-az-coverage-gap.csv",
        "eastern-ok-tiger-roads.parquet",
        "tl_2025_48_roads.zip",
        "northern-ca-microsoft-buildings.parquet",
        "eastern-ok-hifld-fire-stations.parquet",
        "south-central-tx-cbp-establishments.csv",
        "maricopa-az-usgs-structures.parquet",
        "texas-overture-buildings.parquet",
    ],
)
def test_unlisted_or_denylisted_files_raise(name):
    with pytest.raises(guard.ForbiddenDataError):
        guard.raw(name)


def test_denylisted_directory_raises_even_for_provided_name():
    with pytest.raises(guard.ForbiddenDataError):
        guard.raw("old/tiger/maricopa-az-overture-roads.parquet")


def test_artifacts_reject_denylisted_names():
    assert guard.artifact("artifacts/submissions/S02_run.csv")
    with pytest.raises(guard.ForbiddenDataError):
        guard.artifact("artifacts/eastern-ok-coverage_gap.csv")


def test_listing_check_flags_only_forbidden_keys():
    keys = [
        "reference/eastern-ok/eastern-ok-overture-pois.parquet",
        "strata/national/national-usgs-combined-tract-table.parquet",
        "reference/eastern-ok/eastern-ok-coverage-gap.csv",
        "reference/eastern-ok/eastern-ok-tiger-roads.parquet",
    ]
    assert guard.denied_keys(keys) == keys[2:]


def test_every_data_reader_goes_through_the_guard():
    offenders = []
    for path in _modules("src/bbme", "kaggle/stages", "scripts"):
        if path in WRAPPERS:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            unguarded_call = (
                isinstance(node, ast.Call)
                and _callee(node) in READERS
                and not (node.args and _is_guarded(node.args[0]))
            )
            raw_sql = (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and "read_parquet(" in node.value
                and path.name != "db.py"
            )
            if unguarded_call or raw_sql:
                offenders.append(f"{path.relative_to(REPO)}:{node.lineno}")
    assert not offenders, offenders


def test_scored_pipeline_never_imports_analysis():
    scored = [
        p
        for p in _modules("src/bbme", "kaggle/stages")
        if "analysis" not in p.relative_to(REPO).parts and "04_analysis" not in p.parts
    ]
    offenders = []
    for path in scored:
        for node in ast.walk(ast.parse(path.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            if any(n == "bbme.analysis" or n.startswith("bbme.analysis.") for n in names):
                offenders.append(str(path.relative_to(REPO)))
    assert not offenders, offenders


def test_permitted_external_reference_files_open():
    assert guard.raw("external/tl_2025_48_prisecroads.zip").name == "tl_2025_48_prisecroads.zip"
    assert guard.artifact("/kaggle/input/bbme-05-reference/reference/tiger_tracts.parquet")


@pytest.mark.parametrize(
    "name",
    [
        "maricopa-az-coverage-gap.csv",
        "tl_2025_48_coverage_gap.zip",
        "coverage-gap/tl_2025_48_prisecroads.zip",
    ],
)
def test_coverage_gap_files_always_rejected(name):
    with pytest.raises(guard.ForbiddenDataError):
        guard.raw(name)
