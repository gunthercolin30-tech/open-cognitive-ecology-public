from __future__ import annotations
import subprocess
import sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
TESTS = (
    "oif2e_secure_reference_resolver_functional_test.py",
    "oif2e_secure_reference_resolver_degradation_test.py",
    "oif2e_secure_reference_resolver_security_test.py",
    "oif2e_secure_reference_resolver_determinism_test.py",
    "oif2e_secure_reference_resolver_non_modification_test.py",
    "oif2e_secure_reference_resolver_non_regression_test.py",
)
for script in TESTS:
    result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    assert result.returncode == 0, result.stdout
print("OIF2E_FAST_ACCEPTANCE_OK")
