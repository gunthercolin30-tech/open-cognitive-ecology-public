from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TESTS = (
    "acee6_h_unicode_and_case_collision_test.py",
    "acee6_h_canonical_path_collision_test.py",
    "acee6_h_parent_toctou_revalidation_test.py",
    "acee6_h_path_security_non_regression_test.py",
)


def main() -> None:
    root = Path(__file__).resolve().parent
    for name in TESTS:
        completed = subprocess.run(
            [sys.executable, str(root / name)],
            cwd=str(root),
            check=False,
        )
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)
    print("ACEE6_H_PATH_SECURITY_ALL_OK")


if __name__ == "__main__":
    main()
