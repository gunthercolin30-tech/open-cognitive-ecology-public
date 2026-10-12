from __future__ import annotations
import subprocess
import sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
for script in (
    "oif2d_strict_manifest_validator_functional_test.py",
    "oif2d_strict_manifest_validator_reference_test.py",
    "oif2d_strict_manifest_validator_security_test.py",
):
    result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    assert result.returncode == 0, result.stdout
print("OIF2E_NON_REGRESSION_OK")
