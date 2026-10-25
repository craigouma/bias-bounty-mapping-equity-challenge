import re
import shutil
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from bbme import guard

HEADERS = {"User-Agent": "bbme-ingest/1.0"}
CHUNK = 8 * 1024 * 1024


def _split(bucket_uri: str) -> tuple[str, str]:
    bucket, _, prefix = bucket_uri.removeprefix("s3://").partition("/")
    return bucket, prefix.rstrip("/") + "/"


def _get(url: str, timeout: int = 120):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=timeout)


def list_bucket(cfg: dict) -> dict[str, int]:
    """Every object under the challenge prefix as {relative key: bytes}."""
    bucket, prefix = _split(cfg["bucket"])
    objects: dict[str, int] = {}
    token = None
    while True:
        query = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            query["continuation-token"] = token
        url = f"{cfg['s3_endpoint']}/{bucket}?{urllib.parse.urlencode(query)}"
        with _get(url) as r:
            xml = r.read().decode()
        for key, size in re.findall(r"<Key>(.*?)</Key>.*?<Size>(\d+)</Size>", xml, re.S):
            objects[key.removeprefix(prefix)] = int(size)
        match = re.search(r"<NextContinuationToken>(.*?)</NextContinuationToken>", xml)
        if not match:
            return objects
        token = match.group(1)


def wanted(key: str, regions: list[str]) -> bool:
    """The reference `aws s3 sync` file set (the project brief 8.2) plus the national census table.

    Region strata folders carry no census tract table, and AWATER exists only in the national
    one, so that single national file is synced for the water-dominated edge case.
    """
    parts = key.split("/")
    if parts in (["README.md"], ["strata", "national", "national-census-tract-table.parquet"]):
        return True
    if len(parts) == 2 and parts[0] == "boundaries":
        return True
    if len(parts) != 3 or parts[1] not in regions:
        return False
    name = parts[2]
    if parts[0] == "reference":
        return name.endswith(".parquet") or name.endswith("-sample-submission.csv")
    return parts[0] == "strata" and not name.endswith(".csv")


def _download(cfg: dict, key: str, dest: Path) -> int:
    bucket, prefix = _split(cfg["bucket"])
    url = f"{cfg['s3_endpoint']}/{bucket}/{urllib.parse.quote(prefix + key)}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    with _get(url, timeout=600) as r, part.open("wb") as f:
        shutil.copyfileobj(r, f, CHUNK)
    part.replace(dest)
    return dest.stat().st_size


def sync(cfg: dict, objects: dict[str, int], root: Path) -> dict[str, int]:
    """Download `objects` under `root`, retrying any file whose byte count differs."""
    for key in objects:
        guard.raw(root / key)
    local: dict[str, int] = {}
    pending = list(objects)
    for attempt in range(1, cfg["sync"]["attempts"] + 1):
        if not pending:
            break
        print(f"sync attempt {attempt}: {len(pending)} files", flush=True)
        with ThreadPoolExecutor(cfg["sync"]["workers"]) as pool:
            sizes = pool.map(lambda k: _safe_download(cfg, k, root / k), pending)
            local.update(zip(pending, sizes, strict=True))
        pending = [k for k in pending if local[k] != objects[k]]
    return local


def _safe_download(cfg: dict, key: str, dest: Path) -> int:
    try:
        return _download(cfg, key, dest)
    except OSError as exc:
        print(f"download failed for {key}: {exc}", flush=True)
        return -1
