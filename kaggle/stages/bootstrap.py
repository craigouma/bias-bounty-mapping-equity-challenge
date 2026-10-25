import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

EXPECTED_SHA = "{sha}"
RUN = json.loads("""{run_json}""")


def _mount_code() -> Path:
    found = sorted(Path("/kaggle/input").rglob("bbme_code/CODE_SHA"))
    if found:
        return found[0].parent
    archive = next(p for p in Path("/kaggle/input").rglob("*.zip") if "bbme_code" in p.name)
    target = Path("/tmp/bbme_code_extract")
    shutil.rmtree(target, ignore_errors=True)
    zipfile.ZipFile(archive).extractall(target)
    return next(target.rglob("CODE_SHA")).parent


CODE = _mount_code()
if (CODE / "CODE_SHA").read_text().strip() != EXPECTED_SHA:
    sys.exit(f"code dataset lags: expected {EXPECTED_SHA}")
sys.path.insert(0, str(CODE / "src"))
if RUN["install"]:
    requirements = str(CODE / "requirements-kaggle.txt")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", requirements], check=True)
