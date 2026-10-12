from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif/bin/python"

TESTS = (
    "oif2_2_read_only_shell_functional_test.py",
    "oif2_2_read_only_shell_degradation_test.py",
    "oif2_2_read_only_shell_non_regression_test.py",
)


def main() -> int:
    assert PYTHON.is_file(), PYTHON
    for name in TESTS:
        path = ROOT / name
        assert path.is_file(), path
        completed = subprocess.run(
            [str(PYTHON), str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=300,
            check=False,
        )
        print(completed.stdout, end="")
        if completed.returncode:
            print(completed.stderr, file=sys.stderr)
            return completed.returncode
    print("OIF2_2_FAST_ACCEPTANCE_ALL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
