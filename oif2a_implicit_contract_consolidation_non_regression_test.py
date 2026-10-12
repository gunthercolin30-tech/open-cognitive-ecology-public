from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path.home() / "open-cognitive-ecology"
OIF_PYTHON = ROOT / ".venv-oif" / "bin" / "python"

SUITES = (
    ("oif2_3_fast_acceptance_suite.py", False),
    ("oif2_3c_fast_acceptance_suite.py", False),
    ("oif2_3d_fast_acceptance_suite.py", False),
    ("oif2_3e_fast_acceptance_suite.py", True),
    ("oif2_3f_fast_acceptance_suite.py", True),
)

for name, requires_nicegui in SUITES:
    path = ROOT / name
    assert path.is_file(), name

    if requires_nicegui:
        if not OIF_PYTHON.is_file():
            raise AssertionError(
                "NiceGUI interpreter missing for %s: %s"
                % (name, OIF_PYTHON)
            )
        interpreter = OIF_PYTHON
    else:
        interpreter = Path(sys.executable)

    run = subprocess.run(
        [str(interpreter), str(path)],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=300,
    )
    if run.returncode != 0:
        raise AssertionError(
            "%s failed with interpreter %s:\n%s"
            % (name, interpreter, run.stdout)
        )

print("OIF2A_NON_REGRESSION_OK")
