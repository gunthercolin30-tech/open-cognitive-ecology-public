from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTS = [
    "acee6_g1_fault_injection_functional_test.py",
    "acee6_g1_fault_injection_degradation_test.py",
    "acee6_g1_fault_injection_non_regression_test.py",
    "acee6_g1_integrated_boundary_validation_test.py",
    "acee6_g1_journal_integrity_test.py",
    "acee6_g1_instrumentation_failure_test.py",
]


def main() -> None:
    for test in TESTS:
        completed = subprocess.run(
            [sys.executable, str(ROOT / test)],
            cwd=str(ROOT),
            check=False,
        )
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)
    print("ACEE6_G1_SECOND_CROWN_ALL_OK")


if __name__ == "__main__":
    main()
