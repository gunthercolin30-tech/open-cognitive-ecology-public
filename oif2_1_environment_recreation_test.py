from __future__ import annotations
import os, subprocess, tempfile
from pathlib import Path

root = Path.home() / "open-cognitive-ecology"
install = root / "scripts/oif2_nicegui_install.sh"
with tempfile.TemporaryDirectory(prefix="oif2_1_recreate_") as tmp:
    env_dir = Path(tmp) / ".venv-oif-test"
    e = os.environ.copy()
    e["OIF_ROOT"] = str(root)
    e["OIF_ENV_DIR"] = str(env_dir)
    p = subprocess.run(["bash", str(install)], cwd=root, env=e, text=True, capture_output=True, timeout=1200)
    assert p.returncode == 0, p.stdout + p.stderr
    assert env_dir.joinpath("bin/python").is_file(), env_dir
    probe = subprocess.run([str(env_dir / "bin/python"), "-c", "import sys,nicegui; assert sys.version_info >= (3,11); print(nicegui.__version__)"], text=True, capture_output=True, timeout=60)
    assert probe.returncode == 0, probe.stdout + probe.stderr
    check = subprocess.run([str(env_dir / "bin/python"), "-m", "pip", "check"], text=True, capture_output=True, timeout=120)
    assert check.returncode == 0, check.stdout + check.stderr
print("OIF2_1_ENVIRONMENT_RECREATION_TEST_OK")
