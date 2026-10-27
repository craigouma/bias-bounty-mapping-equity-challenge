"""Forbidden-data guard.

Organiser coverage-gap files must never be opened. The removed reference layers (TIGER roads,
Microsoft footprints, HIFLD / USGS structures, CBP establishments) are admitted only under the
file names listed in `external_reference` in configs/data.yaml (permitted by Zindi staff,
27 Oct 2026). Every raw
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
    external = cfg.get("external_reference", {})
    extra = external.get("allowlist", []) if external.get("enabled") else []
    for pattern in [*cfg["allowlist"], *extra]:
        for key, value in subs.items():
            pattern = pattern.replace(key, value)
        patterns.append(f"(?:{pattern})")
    return re.compile("|".join(patterns)), tuple(cfg["denylist"]), tuple(cfg["always_denied"])


def is_allowed(name: str) -> bool:
    if any(token in name.lower() for token in _rules()[2]):
        return False
    return _rules()[0].fullmatch(name) is not None


def is_denied(path: str | Path) -> bool:
    parts = PurePosixPath(str(path)).parts
    if parts and is_allowed(parts[-1]):
        parts = parts[:-1]
    text = "/".join(parts).lower()
    return any(token in text for token in _rules()[1]) or any(
        token in str(path).lower() for token in _rules()[2]
    )


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
