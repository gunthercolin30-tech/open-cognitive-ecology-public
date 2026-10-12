from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INSTALLER = ROOT / "scripts" / "oif2_nicegui_install.sh"
STALE = "/opt/homebrew/Cellar/python@3.12/0.0.0-oif-removed/Frameworks/Python.framework/Versions/3.12/bin/python3.12"

assert INSTALLER.is_file(), INSTALLER

with tempfile.TemporaryDirectory(prefix="oif2_1_homebrew_drift_") as tmp:
    work = Path(tmp)
    env_dir = work / ".venv-oif-test"
    record = work / "oif-python-interpreter.txt"
    record.write_text(STALE + "\n", encoding="utf-8")

    env = os.environ.copy()
    env["OIF_ROOT"] = str(ROOT)
    env["OIF_ENV_DIR"] = str(env_dir)
    env["OIF_INTERPRETER_RECORD"] = str(record)
    env.pop("OIF_PYTHON", None)

    completed = subprocess.run(
        ["bash", str(INSTALLER)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=1500,
        check=False,
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 0, output
    assert "OIF2_1_NICEGUI_INSTALL_OK" in output, output
    assert env_dir.joinpath("bin", "python").is_file(), env_dir
    assert STALE not in output, output

    probe = subprocess.run(
        [
            str(env_dir / "bin" / "python"),
            "-c",
            "import sys; assert sys.version_info >= (3, 11); print(sys._base_executable)",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert probe.returncode == 0, probe.stdout + probe.stderr
    selected = probe.stdout.strip()
    assert selected
    assert selected != STALE, (selected, STALE)
    assert Path(selected).is_file(), selected

    check = subprocess.run(
        [str(env_dir / "bin" / "python"), "-m", "pip", "check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    assert check.returncode == 0, check.stdout + check.stderr

print("OIF2_1_HOMEBREW_PATH_DRIFT_TEST_OK")
