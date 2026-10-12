from __future__ import annotations
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
TESTS = (
    "oif2_3e_fast_acceptance_suite.py",
    "oif2_3f_navigation_model_functional_test.py",
    "oif2_3f_navigation_model_degradation_test.py",
    "oif2_3f_navigation_preferences_test.py",
    "oif2_3f_renderer_boundary_test.py",
    "oif2_3f_navigation_non_regression_test.py",
    "oif2_3f_nicegui_import_smoke_test.py",
)
def main():
    for name in TESTS:
        result = subprocess.run([sys.executable, str(ROOT / name)], cwd=ROOT, check=False)
        if result.returncode: return result.returncode
    print("OIF2_3F_FAST_ACCEPTANCE_ALL_OK")
    return 0
if __name__ == "__main__": raise SystemExit(main())
