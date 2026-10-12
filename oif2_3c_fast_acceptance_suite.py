from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif/bin/python"

TESTS = (
    "oif2_3_fast_acceptance_suite.py",
    "oif2_3c_runtime_health_adapter_functional_test.py",
    "oif2_3c_runtime_health_adapter_degradation_test.py",
    "oif2_3c_runtime_health_adapter_real_source_test.py",
    "oif2_3c_runtime_health_adapter_external_storage_test.py",
    "oif2_3c_runtime_health_adapter_long_duration_status_test.py",
    "oif2_3c_runtime_health_adapter_non_regression_test.py",
)


def main() -> int:
    for name in TESTS:
        path = ROOT / name
        assert path.is_file(), path
        completed = subprocess.run(
            [str(PYTHON), str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=1200,
            check=False,
        )
        print(completed.stdout, end="")
        if completed.returncode:
            print(completed.stderr, file=sys.stderr, end="")
            return completed.returncode
    print("OIF2_3C_FAST_ACCEPTANCE_ALL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
