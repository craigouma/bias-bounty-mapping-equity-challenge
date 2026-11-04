import ast
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import kaggle_run  # noqa: E402
from bbme.config import load  # noqa: E402

STAGES = sorted(p.parent.name for p in (REPO / "kaggle" / "stages").glob("*/run.py"))


@pytest.fixture
def isolated_build(tmp_path, monkeypatch):
    real = kaggle_run.load

    def fake(name):
        cfg = real(name)
        if name == "paths":
            cfg["kernels_build"] = str(tmp_path)
        return cfg

    monkeypatch.setattr(kaggle_run, "load", fake)
    return tmp_path


@pytest.mark.parametrize("stage", STAGES)
def test_rendered_kernel_parses_and_carries_run(stage, isolated_build):
    run = {"run_id": "r1", "stage": stage, "sha": "a" * 40, "overrides": [], "install": True}
    folder = kaggle_run.render(stage, run)
    source = (folder / "run.py").read_text()
    ast.parse(source)
    assert f'EXPECTED_SHA = "{"a" * 40}"' in source
    assert source.rstrip().endswith("main(RUN, CODE)")
    meta = json.loads((folder / "kernel-metadata.json").read_text())
    scfg = load("kaggle")["stages"][stage]
    assert meta["title"] == scfg["slug"] == meta["id"].split("/")[1]
    assert meta["enable_internet"] == "true"
    assert (meta["machine_shape"] == "NvidiaTeslaT4") == scfg["gpu"]


def test_prefix_renames_kernel_and_its_sources(isolated_build):
    run = {"run_id": "r1", "stage": "03_model", "sha": "a" * 40, "overrides": [], "install": True}
    meta = json.loads(
        (kaggle_run.render("03_model", run, "repro-") / "kernel-metadata.json").read_text()
    )
    kcfg = load("kaggle")
    scfg = kcfg["stages"]["03_model"]
    assert meta["id"] == f"{kcfg['username']}/repro-{scfg['slug']}"
    assert meta["title"] == f"repro-{scfg['slug']}"
    assert meta["kernel_sources"] == [
        f"{kcfg['username']}/repro-{s}" for s in scfg["kernel_sources"]
    ]
    assert meta["dataset_sources"][0] == f"{kcfg['username']}/{kcfg['code_dataset']}"
