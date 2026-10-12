from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
for script in (
    "oif2b_canonical_manifest_model_functional_test.py",
    "oif2c_json_schema_yaml_functional_test.py",
    "oif2c_json_schema_yaml_security_test.py",
):
    result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
    assert result.returncode == 0, result.stdout
print("OIF2D_NON_REGRESSION_OK")
