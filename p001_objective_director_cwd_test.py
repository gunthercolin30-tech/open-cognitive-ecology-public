import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
target = ROOT / "validation" / "p001_objective_director.py"

with tempfile.TemporaryDirectory() as td:
    env = dict(os.environ)
    env["OCE_ROOT"] = str(ROOT)
    proc = subprocess.run(
        [sys.executable, str(target)],
        cwd=td,
        env=env,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert '"decision": "P001_REPRESENTABLE"' in proc.stdout
print("P001_CWD_INDEPENDENCE_OK")
