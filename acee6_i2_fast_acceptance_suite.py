#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
TESTS = ["acee6_i2_replay_functional_test.py", "acee6_i2_duplicate_proposal_test.py", "acee6_i2_divergence_degradation_test.py", "acee6_i2_restart_determinism_test.py", "acee6_i2_non_regression_test.py"]
for name in TESTS:
    completed = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT))
    if completed.returncode: raise SystemExit(completed.returncode)
print("ACEE6_I2_FAST_ACCEPTANCE_OK")
