from __future__ import annotations
import subprocess
import sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
for name in ("oif2b_adversarial_validation_crown.py",):
    run = subprocess.run(
        [sys.executable, str(ROOT / name)], cwd=str(ROOT),
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1800,
    )
    if run.returncode:
        raise AssertionError("%s failed:\n%s" % (name, run.stdout))
print("OIF2C_NON_REGRESSION_OK")
