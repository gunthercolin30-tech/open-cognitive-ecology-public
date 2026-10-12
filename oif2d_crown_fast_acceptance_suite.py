from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
script = ROOT / "oif2d_adversarial_crown.py"
result = subprocess.run(
    [sys.executable, str(script)], cwd=str(ROOT), text=True,
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300,
)
if result.returncode != 0:
    raise AssertionError(result.stdout)
assert "OIF2D_ADVERSARIAL_CROWN_OK" in result.stdout, result.stdout
print("OIF2D_CROWN_FAST_ACCEPTANCE_OK")
