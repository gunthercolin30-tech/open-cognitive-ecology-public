from __future__ import annotations
import subprocess
import sys

TESTS = [
    "acee6_g2_governed_rollback_functional_test.py",
    "acee6_g2_governed_rollback_degradation_test.py",
    "acee6_g2_governed_rollback_non_regression_test.py",
    "acee6_g2_preexisting_target_rollback_test.py",
    "acee6_g2_false_success_and_partial_failure_test.py",
    "acee6_g2_replay_and_report_integrity_test.py",
]


def main() -> None:
    for test in TESTS:
        subprocess.run([sys.executable, test], check=True)
    print("ACEE6_G2_EXTENDED_ROLLBACK_ALL_OK")


if __name__ == "__main__":
    main()
