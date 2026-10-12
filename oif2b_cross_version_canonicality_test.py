from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
OIF_PYTHON = ROOT / ".venv-oif" / "bin" / "python"
assert OIF_PYTHON.is_file(), "missing .venv-oif interpreter"

snippet = (
    "import json;"
    "from oif2b_test_support import build_spec;"
    "s=build_spec();"
    "print(json.dumps({'canonical_json':s.canonical_json(),'sha256':s.sha256()},sort_keys=True))"
)

def run(interpreter):
    completed = subprocess.run(
        [str(interpreter), "-c", snippet],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    )
    if completed.returncode:
        raise AssertionError(completed.stderr)
    return json.loads(completed.stdout.strip().splitlines()[-1])

system_result = run(Path(sys.executable))
oif_result = run(OIF_PYTHON)
assert system_result == oif_result
print("OIF2B_CROSS_VERSION_CANONICALITY_OK", system_result["sha256"])
