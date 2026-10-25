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
