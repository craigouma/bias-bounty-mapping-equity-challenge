"""Forbidden-data guard.

The removed reference layers (TIGER roads, Microsoft footprints, HIFLD / USGS structures,
CBP establishments) and any organiser coverage-gap file must never be opened. Every raw
input passes `raw()`, which admits only the provided file names; derived artifacts pass
`artifact()`, which rejects denylisted names. A provided name that happens to contain a
denylisted token (`usgs-combined-tract-table`, a permitted wildfire stratum) is admitted
because the allowlist is checked first.
"""

import re
from collections.abc import Iterable
from functools import cache
from pathlib import Path, PurePosixPath

from bbme.config import load


class ForbiddenDataError(RuntimeError):
    pass


@cache
def _rules() -> tuple[re.Pattern, tuple[str, ...]]:
    cfg = load("data")

    def alternation(items: list[str]) -> str:
        return "(" + "|".join(re.escape(i) for i in items) + ")"

    subs = {
        "{region}": alternation(cfg["regions"]),
        "{layer}": alternation(cfg["overture_layers"]),
        "{table}": alternation(cfg["strata_tables"]),
    }
    patterns = []
    for pattern in cfg["allowlist"]:
        for key, value in subs.items():
            pattern = pattern.replace(key, value)
        patterns.append(f"(?:{pattern})")
    return re.compile("|".join(patterns)), tuple(cfg["denylist"])


def is_allowed(name: str) -> bool:
    return _rules()[0].fullmatch(name) is not None


def is_denied(path: str | Path) -> bool:
    parts = PurePosixPath(str(path)).parts
    if parts and is_allowed(parts[-1]):
        parts = parts[:-1]
    text = "/".join(parts).lower()
    return any(token in text for token in _rules()[1])


def raw(path: str | Path) -> Path:
    path = Path(path)
    if not is_allowed(path.name) or is_denied(path):
        raise ForbiddenDataError(f"not a provided challenge file: {path}")
    return path


def artifact(path: str | Path) -> Path:
    path = Path(path)
    if is_denied(path):
        raise ForbiddenDataError(f"denylisted path: {path}")
    return path


def denied_keys(keys: Iterable[str]) -> list[str]:
    return [k for k in keys if is_denied(k)]
