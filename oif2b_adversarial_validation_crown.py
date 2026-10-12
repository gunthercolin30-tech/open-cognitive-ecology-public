from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
TESTS = (
    "oif2b_property_campaign_test.py",
    "oif2b_cross_version_canonicality_test.py",
    "oif2b_structural_limits_test.py",
    "oif2b_reference_adversarial_test.py",
    "oif2b_security_normalization_test.py",
    "oif2b_non_modification_test.py",
    "oif2b_fast_acceptance_suite.py",
    "oif2b_canonical_manifest_model_non_regression_test.py",
)

for name in TESTS:
    completed = subprocess.run(
        [sys.executable, str(ROOT / name)],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=1800,
    )
    if completed.returncode:
        raise AssertionError("%s failed:\n%s" % (name, completed.stdout))

print("OIF2B_ADVERSARIAL_CROWN_OK")
