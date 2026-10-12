from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif/bin/python"

TESTS = (
    "oif2_3c_fast_acceptance_suite.py",
    "oif2_3d_civilizational_state_adapter_functional_test.py",
    "oif2_3d_civilizational_state_adapter_degradation_test.py",
    "oif2_3d_civilizational_state_adapter_real_source_test.py",
    "oif2_3d_civilizational_state_adapter_external_storage_test.py",
    "oif2_3d_civilizational_state_adapter_non_regression_test.py",
)


def main() -> int:
    for name in TESTS:
        path = ROOT / name
        assert path.is_file(), path
        completed = subprocess.run(
            [str(PYTHON), str(path)], cwd=ROOT, text=True,
            capture_output=True, timeout=1200, check=False,
        )
        print(completed.stdout, end="")
        if completed.returncode:
            print(completed.stderr, file=sys.stderr, end="")
            return completed.returncode
    print("OIF2_3D_FAST_ACCEPTANCE_ALL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
