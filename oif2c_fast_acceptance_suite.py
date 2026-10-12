from __future__ import annotations
import subprocess
import sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
TESTS = (
    "oif2c_json_schema_yaml_functional_test.py",
    "oif2c_json_schema_yaml_degradation_test.py",
    "oif2c_json_schema_yaml_security_test.py",
    "oif2c_json_schema_yaml_determinism_test.py",
    "oif2c_json_schema_yaml_cross_version_test.py",
    "oif2c_json_schema_yaml_non_regression_test.py",
)
for name in TESTS:
    run = subprocess.run(
        [sys.executable, str(ROOT / name)], cwd=str(ROOT),
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1800,
    )
    if run.returncode:
        raise AssertionError("%s failed:\n%s" % (name, run.stdout))
print("OIF2C_FAST_ACCEPTANCE_ALL_OK")
