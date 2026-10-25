from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs"


def load(name: str, config_dir: Path = CONFIG_DIR) -> dict[str, Any]:
    return yaml.safe_load((config_dir / f"{name}.yaml").read_text())


def apply_overrides(cfg: dict[str, Any], overrides: Iterable[str]) -> dict[str, Any]:
    """Set dotted keys from `key.path=value` strings; values are parsed as YAML scalars."""
    for item in overrides:
        key, _, raw = item.partition("=")
        *parents, leaf = key.strip().split(".")
        node = cfg
        for part in parents:
            node = node[part]
        if leaf not in node:
            raise KeyError(f"unknown config key: {key}")
        node[leaf] = yaml.safe_load(raw)
    return cfg
